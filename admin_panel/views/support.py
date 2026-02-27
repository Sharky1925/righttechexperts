from __future__ import annotations

import csv
import json
from datetime import timedelta
from io import StringIO

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from admin_panel.decorators import permission_required
from admin_panel.models import ContactSubmission, SecurityEvent, SupportTicket, SupportTicketEvent
from core.constants import (
    SUPPORT_TICKET_EVENT_ADMIN_UPDATE,
    SUPPORT_TICKET_EVENT_CREATED,
    SUPPORT_TICKET_EVENT_REVIEW_ACTION,
    SUPPORT_TICKET_STAGE_LABELS,
    SUPPORT_TICKET_STAGE_PENDING,
    SUPPORT_TICKET_STAGE_TO_STATUS,
    SUPPORT_TICKET_STATUS_LABELS,
    normalize_support_ticket_stage,
    normalize_support_ticket_status,
    support_ticket_stage_for_status,
)
from core.utils import clean_text, utc_now_naive

LEAD_STATUS_LABELS = {
    'new': 'New',
    'qualified': 'Qualified',
    'in_progress': 'In Progress',
    'won': 'Won',
    'lost': 'Lost',
}
VALID_PRIORITIES = {'low', 'normal', 'high', 'critical'}
QUOTE_INTAKE_EMAIL = 'quote-intake@rightonrepair.local'
QUOTE_SUBJECT_PREFIX = 'quote request:'
QUOTE_DETAILS_PREFIX = 'quote intake submission'


class PaginationAdapter:
    def __init__(self, page_obj):
        self._page = page_obj
        self.page = page_obj.number
        self.pages = page_obj.paginator.num_pages
        self.total = page_obj.paginator.count

    @property
    def items(self):
        return list(self._page.object_list)

    @property
    def has_prev(self):
        return self._page.has_previous()

    @property
    def has_next(self):
        return self._page.has_next()

    @property
    def prev_num(self):
        return self._page.previous_page_number() if self.has_prev else None

    @property
    def next_num(self):
        return self._page.next_page_number() if self.has_next else None


def _coerce_ids(values):
    if not values:
        return []
    result = []
    seen = set()
    for value in values:
        for part in str(value or '').split(','):
            token = part.strip()
            if not token.isdigit():
                continue
            parsed = int(token)
            if parsed in seen:
                continue
            seen.add(parsed)
            result.append(parsed)
    return result


def _quote_ticket_filter():
    return (
        Q(subject__istartswith=QUOTE_SUBJECT_PREFIX)
        | Q(details__istartswith=QUOTE_DETAILS_PREFIX)
        | Q(client__email__iexact=QUOTE_INTAKE_EMAIL)
    )


def is_quote_ticket(ticket):
    if not ticket:
        return False
    subject = (getattr(ticket, 'subject', '') or '').strip().lower()
    details = (getattr(ticket, 'details', '') or '').strip().lower()
    client_email = (getattr(getattr(ticket, 'client', None), 'email', '') or '').strip().lower()
    return (
        subject.startswith(QUOTE_SUBJECT_PREFIX)
        or details.startswith(QUOTE_DETAILS_PREFIX)
        or client_email == QUOTE_INTAKE_EMAIL
    )


def support_ticket_status_label(status):
    normalized = normalize_support_ticket_status(status)
    return SUPPORT_TICKET_STATUS_LABELS.get(normalized, normalized.replace('_', ' ').title())


def support_ticket_stage_label(stage):
    normalized = normalize_support_ticket_stage(stage, default=SUPPORT_TICKET_STAGE_PENDING)
    return SUPPORT_TICKET_STAGE_LABELS.get(normalized, normalized.replace('_', ' ').title())


def support_ticket_stage_badge(stage):
    normalized = normalize_support_ticket_stage(stage, default=SUPPORT_TICKET_STAGE_PENDING)
    if normalized == 'done':
        return 'bg-success'
    if normalized == 'closed':
        return 'bg-secondary'
    return 'bg-warning text-dark'


def support_ticket_event_label(event_type):
    mapping = {
        SUPPORT_TICKET_EVENT_CREATED: 'Created',
        SUPPORT_TICKET_EVENT_REVIEW_ACTION: 'Review Update',
        SUPPORT_TICKET_EVENT_ADMIN_UPDATE: 'Admin Update',
    }
    return mapping.get((event_type or '').strip(), (event_type or 'update').replace('_', ' ').title())


def support_ticket_event_badge(event_type):
    et = (event_type or '').strip()
    if et == SUPPORT_TICKET_EVENT_CREATED:
        return 'bg-primary'
    if et == SUPPORT_TICKET_EVENT_REVIEW_ACTION:
        return 'bg-warning text-dark'
    if et == SUPPORT_TICKET_EVENT_ADMIN_UPDATE:
        return 'bg-info text-dark'
    return 'bg-secondary'


def format_datetime_local(value):
    if not value:
        return '—'
    return value.strftime('%Y-%m-%d %H:%M')


@permission_required('support:manage')
def contacts(request):
    status_filter = clean_text(request.GET.get('status', ''), 30)
    query = ContactSubmission.objects.order_by('-created_at', '-id')
    if status_filter in LEAD_STATUS_LABELS:
        query = query.filter(lead_status=status_filter)
    items = list(query[:500])
    return render(
        request,
        'admin/contacts.html',
        {
            'items': items,
            'lead_statuses': LEAD_STATUS_LABELS,
            'lead_status_labels': LEAD_STATUS_LABELS,
            'bulk_url': '/admin/contacts/bulk',
        },
    )


@permission_required('support:manage')
def contact_view(request, id):
    item = get_object_or_404(ContactSubmission, id=id)
    return render(
        request,
        'admin/contact_view.html',
        {
            'item': item,
            'lead_status_labels': LEAD_STATUS_LABELS,
        },
    )


@permission_required('support:manage')
def contact_status_update(request, id):
    if request.method != 'POST':
        return redirect('admin:contact_view', id=id)
    item = get_object_or_404(ContactSubmission, id=id)
    lead_status = clean_text(request.POST.get('lead_status', ''), 30)
    if lead_status not in LEAD_STATUS_LABELS:
        lead_status = 'new'
    item.lead_status = lead_status
    item.lead_notes = request.POST.get('lead_notes', '')
    item.is_read = True
    item.save(update_fields=['lead_status', 'lead_notes', 'is_read'])
    messages.success(request, 'Lead status updated.')
    return redirect('admin:contact_view', id=item.id)


@permission_required('support:manage')
def contact_delete(request, id):
    if request.method != 'POST':
        return redirect('admin:contacts')
    item = get_object_or_404(ContactSubmission, id=id)
    item.delete()
    messages.success(request, 'Contact submission deleted.')
    return redirect('admin:contacts')


@permission_required('support:manage')
def contacts_bulk(request):
    if request.method != 'POST':
        return redirect('admin:contacts')
    action = clean_text(request.POST.get('action', ''), 20).lower()
    ids = _coerce_ids(request.POST.getlist('ids'))
    if not ids:
        messages.error(request, 'No contacts selected.')
        return redirect('admin:contacts')

    query = ContactSubmission.objects.filter(id__in=ids)
    if action == 'publish':
        query.update(is_read=True, lead_status='qualified')
        messages.success(request, f'Updated {len(ids)} contacts to qualified.')
    elif action == 'draft':
        query.update(is_read=False, lead_status='new')
        messages.success(request, f'Updated {len(ids)} contacts to new.')
    elif action == 'trash':
        query.update(is_read=True, lead_status='lost')
        messages.success(request, f'Updated {len(ids)} contacts to lost.')
    elif action == 'delete':
        deleted, _ = query.delete()
        messages.success(request, f'Deleted {deleted} contact records.')
    else:
        messages.error(request, 'Unsupported bulk action.')
    return redirect('admin:contacts')


@permission_required('support:manage')
def contacts_export(request):
    rows = ContactSubmission.objects.order_by('-created_at', '-id')[:5000]
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(
        [
            'id',
            'created_at',
            'name',
            'email',
            'phone',
            'subject',
            'message',
            'is_read',
            'lead_status',
            'lead_notes',
            'source_page',
            'utm_source',
            'utm_medium',
            'utm_campaign',
            'referrer_url',
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row.id,
                row.created_at.isoformat() if row.created_at else '',
                row.name,
                row.email,
                row.phone or '',
                row.subject or '',
                row.message or '',
                int(bool(row.is_read)),
                row.lead_status or '',
                row.lead_notes or '',
                row.source_page or '',
                row.utm_source or '',
                row.utm_medium or '',
                row.utm_campaign or '',
                row.referrer_url or '',
            ]
        )
    payload = stream.getvalue()
    response = HttpResponse(payload, content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="contact_submissions.csv"'
    return response


@permission_required('support:manage')
def support_tickets(request):
    stage_filter = clean_text(request.GET.get('stage', ''), 20).lower()
    status_filter = clean_text(request.GET.get('status', ''), 30).lower()
    type_filter = clean_text(request.GET.get('type', 'all'), 20).lower() or 'all'
    search_query = clean_text(request.GET.get('q', ''), 120)

    query = SupportTicket.objects.select_related('client').order_by('-updated_at', '-id')

    if status_filter:
        query = query.filter(status=normalize_support_ticket_status(status_filter))
    elif stage_filter:
        normalized_stage = normalize_support_ticket_stage(stage_filter)
        if normalized_stage == 'pending':
            query = query.filter(status__in=['open', 'in_progress', 'waiting_customer'])
        elif normalized_stage == 'done':
            query = query.filter(status='resolved')
        elif normalized_stage == 'closed':
            query = query.filter(status='closed')

    if type_filter == 'quote':
        query = query.filter(_quote_ticket_filter())
    elif type_filter == 'support':
        query = query.exclude(_quote_ticket_filter())
    else:
        type_filter = 'all'

    if search_query:
        query = query.filter(
            Q(ticket_number__icontains=search_query)
            | Q(subject__icontains=search_query)
            | Q(client__full_name__icontains=search_query)
            | Q(client__email__icontains=search_query)
        )

    page_num = request.GET.get('page', '1')
    try:
        page_num = max(1, min(int(page_num), 1000))
    except (TypeError, ValueError):
        page_num = 1
    paginator = Paginator(query, 50)
    items = PaginationAdapter(paginator.get_page(page_num))

    return render(
        request,
        'admin/support_tickets.html',
        {
            'items': items.items,
            'stage_filter': stage_filter,
            'status_filter': status_filter,
            'type_filter': type_filter,
            'search_query': search_query,
            'support_ticket_stage_for_status': support_ticket_stage_for_status,
            'support_ticket_stage_label': support_ticket_stage_label,
            'support_ticket_status_label': support_ticket_status_label,
            'support_ticket_stage_badge': support_ticket_stage_badge,
            'is_quote_ticket': is_quote_ticket,
        },
    )


def _create_ticket_event(ticket, request, *, event_type, message='', status_from=None, status_to=None):
    now = utc_now_naive()
    stage_from = support_ticket_stage_for_status(status_from) if status_from else None
    stage_to = support_ticket_stage_for_status(status_to) if status_to else None
    SupportTicketEvent.objects.create(
        ticket_id=ticket.id,
        event_type=event_type,
        message=message or None,
        actor_type='admin',
        actor_name=getattr(request.user, 'username', 'admin'),
        actor_user_id=getattr(request.user, 'id', None),
        status_from=status_from,
        status_to=status_to,
        stage_from=stage_from,
        stage_to=stage_to,
        metadata_json=json.dumps({'path': request.path}, ensure_ascii=False),
        created_at=now,
    )


@permission_required('support:manage')
def support_ticket_review(request, id):
    if request.method != 'POST':
        return redirect('admin:support_tickets')
    item = get_object_or_404(SupportTicket, id=id)
    review_action = clean_text(request.POST.get('review_action', ''), 20).lower()
    stage = normalize_support_ticket_stage(review_action)
    if stage not in SUPPORT_TICKET_STAGE_TO_STATUS:
        messages.error(request, 'Unknown review action.')
        return redirect('admin:support_tickets')

    previous_status = item.status
    item.status = SUPPORT_TICKET_STAGE_TO_STATUS[stage]
    item.updated_at = utc_now_naive()
    item.save(update_fields=['status', 'updated_at'])
    _create_ticket_event(
        item,
        request,
        event_type=SUPPORT_TICKET_EVENT_REVIEW_ACTION,
        message=f'Ticket stage updated to {support_ticket_stage_label(stage)}.',
        status_from=previous_status,
        status_to=item.status,
    )
    messages.success(request, f'Ticket moved to {support_ticket_stage_label(stage)}.')
    return redirect('admin:support_tickets')


@permission_required('support:manage')
def support_ticket_view(request, id):
    item = get_object_or_404(SupportTicket.objects.select_related('client'), id=id)

    if request.method == 'POST':
        previous_status = item.status
        status_raw = clean_text(request.POST.get('status', ''), 40)
        item.status = normalize_support_ticket_status(status_raw, default=item.status)
        priority = clean_text(request.POST.get('priority', ''), 20).lower()
        if priority in VALID_PRIORITIES:
            item.priority = priority
        item.internal_notes = request.POST.get('internal_notes', '')
        item.updated_at = utc_now_naive()
        item.save(update_fields=['status', 'priority', 'internal_notes', 'updated_at'])
        review_note = clean_text(request.POST.get('review_note', ''), 500)
        message = review_note or f'Ticket updated by admin. Status: {support_ticket_status_label(item.status)}.'
        _create_ticket_event(
            item,
            request,
            event_type=SUPPORT_TICKET_EVENT_ADMIN_UPDATE,
            message=message,
            status_from=previous_status,
            status_to=item.status,
        )
        messages.success(request, 'Ticket updated.')
        return redirect('admin:support_ticket_view', id=item.id)

    ticket_events = list(
        SupportTicketEvent.objects.filter(ticket_id=item.id).order_by('-created_at', '-id')[:100]
    )
    current_ticket_stage = support_ticket_stage_for_status(item.status)
    return render(
        request,
        'admin/support_ticket_view.html',
        {
            'item': item,
            'is_quote_ticket': is_quote_ticket(item),
            'current_ticket_stage': current_ticket_stage,
            'ticket_events': ticket_events,
            'support_ticket_stage_label': support_ticket_stage_label,
            'support_ticket_status_label': support_ticket_status_label,
            'support_ticket_stage_badge': support_ticket_stage_badge,
            'support_ticket_event_label': support_ticket_event_label,
            'support_ticket_event_badge': support_ticket_event_badge,
            'format_datetime_local': format_datetime_local,
        },
    )


@permission_required('security:view')
def security_events(request):
    event_type_filter = clean_text(request.GET.get('event_type', 'all'), 40) or 'all'
    scope_filter = clean_text(request.GET.get('scope', 'all'), 80) or 'all'
    search = clean_text(request.GET.get('q', ''), 120)
    page_num = request.GET.get('page', '1')
    try:
        page_num = max(1, min(int(page_num), 1000))
    except (TypeError, ValueError):
        page_num = 1

    query = SecurityEvent.objects.order_by('-created_at', '-id')
    if event_type_filter != 'all':
        query = query.filter(event_type=event_type_filter)
    if scope_filter != 'all':
        query = query.filter(scope=scope_filter)
    if search:
        query = query.filter(
            Q(ip__icontains=search)
            | Q(path__icontains=search)
            | Q(details__icontains=search)
            | Q(user_agent__icontains=search)
        )

    paginator = Paginator(query, 25)
    items = PaginationAdapter(paginator.get_page(page_num))

    now = utc_now_naive()
    since = now - timedelta(hours=24)
    recent = SecurityEvent.objects.filter(created_at__gte=since)
    stats = {
        'last_24h': recent.count(),
        'turnstile_failed_24h': recent.filter(event_type='turnstile_failed').count(),
        'rate_limited_24h': recent.filter(event_type='rate_limited').count(),
    }

    return render(
        request,
        'admin/security_events.html',
        {
            'items': items,
            'stats': stats,
            'event_type_filter': event_type_filter,
            'scope_filter': scope_filter,
            'search': search,
        },
    )
