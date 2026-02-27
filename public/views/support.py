from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render

from admin_panel.models import SupportClient, SupportTicket, SupportTicketEvent
from core.constants import (
    SUPPORT_TICKET_EVENT_CREATED,
    SUPPORT_TICKET_STAGE_LABELS,
    SUPPORT_TICKET_STATUS_OPEN,
    SUPPORT_TICKET_STATUS_LABELS,
    support_ticket_stage_for_status,
    WORKFLOW_PUBLISHED,
)
from core.rate_limit import check_rate_limit, clear_rate_limit, get_client_ip
from core.utils import clean_text, is_valid_email, utc_now_naive
from public.models import Service

_PORTAL_LOGIN_MAX = 10
_PORTAL_LOGIN_WINDOW = 300  # 5 minutes

TICKET_PRIORITY_LABELS = {
    'low': 'Low',
    'normal': 'Normal',
    'high': 'High',
    'critical': 'Critical',
}
PORTAL_SESSION_KEY = 'remote_support_client_id'
VALID_PRIORITIES = {'low', 'normal', 'high', 'critical'}


def _generate_ticket_number():
    today_prefix = f"RT-{utc_now_naive().strftime('%y%m%d')}-"
    latest = (
        SupportTicket.objects.filter(ticket_number__startswith=today_prefix)
        .order_by('-id')
        .values_list('ticket_number', flat=True)
        .first()
    )
    seq = 1
    if latest and latest.startswith(today_prefix):
        raw = latest[len(today_prefix):].strip()
        if raw.isdigit():
            seq = int(raw) + 1

    while True:
        ticket_number = f'{today_prefix}{seq:04d}'
        if not SupportTicket.objects.filter(ticket_number=ticket_number).exists():
            return ticket_number
        seq += 1


def _get_portal_client(request):
    client_id = request.session.get(PORTAL_SESSION_KEY)
    if not client_id:
        return None
    client = SupportClient.objects.filter(id=client_id).first()
    if client is None:
        request.session.pop(PORTAL_SESSION_KEY, None)
    return client


def remote_support(request):
    portal_client = _get_portal_client(request)
    services = list(
        Service.objects.filter(workflow_status=WORKFLOW_PUBLISHED)
        .filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
        .order_by('title', 'id')
    )
    tickets = []
    stage_counts = {'pending': 0, 'done': 0, 'closed': 0}
    if portal_client:
        tickets = list(
            SupportTicket.objects.filter(client_id=portal_client.id)
            .order_by('-updated_at', '-id')[:120]
        )
        for ticket in tickets:
            stage = support_ticket_stage_for_status(ticket.status)
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

    return render(
        request,
        'remote_support.html',
        {
            'portal_client': portal_client,
            'ticket_stage_counts': stage_counts,
            'ticket_stage_labels': SUPPORT_TICKET_STAGE_LABELS,
            'tickets': tickets,
            'services': services,
            'ticket_status_labels': SUPPORT_TICKET_STATUS_LABELS,
            'ticket_stage_for_status': support_ticket_stage_for_status,
            'ticket_status_badges': {},
            'ticket_stage_badges': {},
            'ticket_priority_labels': TICKET_PRIORITY_LABELS,
        },
    )


def remote_support_register(request):
    if request.method != 'POST':
        return redirect('public:remote_support')

    full_name = clean_text(request.POST.get('full_name', ''), 200)
    email = clean_text(request.POST.get('email', ''), 200).lower()
    phone = clean_text(request.POST.get('phone', ''), 50)
    company = clean_text(request.POST.get('company', ''), 200)
    password = request.POST.get('password') or ''
    confirm_password = request.POST.get('confirm_password') or ''

    if not full_name or not email or not phone or not password:
        messages.error(request, 'Please complete all required fields to register.')
        return redirect('public:remote_support')
    if not is_valid_email(email):
        messages.error(request, 'Please provide a valid email address.')
        return redirect('public:remote_support')
    if len(password) < 8:
        messages.error(request, 'Password must be at least 8 characters.')
        return redirect('public:remote_support')
    if password != confirm_password:
        messages.error(request, 'Password confirmation does not match.')
        return redirect('public:remote_support')
    if SupportClient.objects.filter(email__iexact=email).exists():
        messages.error(request, 'An account with this email already exists. Please sign in.')
        return redirect('public:remote_support')

    now = utc_now_naive()
    client = SupportClient(
        full_name=full_name,
        email=email,
        company=company or None,
        phone=phone,
        created_at=now,
        last_login_at=now,
    )
    client.set_password(password)
    client.save()
    request.session.cycle_key()  # Prevent session fixation
    request.session[PORTAL_SESSION_KEY] = client.id
    messages.success(request, 'Account created. You are now signed in.')
    return redirect('public:remote_support')


def remote_support_login(request):
    if request.method != 'POST':
        return redirect('public:remote_support')

    ip = get_client_ip(request)
    rate_key = f'portal_login:{ip}'
    if check_rate_limit(rate_key, max_attempts=_PORTAL_LOGIN_MAX, window_seconds=_PORTAL_LOGIN_WINDOW):
        messages.error(request, 'Too many login attempts. Please wait a few minutes before trying again.')
        return redirect('public:remote_support')

    email = clean_text(request.POST.get('email', ''), 200).lower()
    password = request.POST.get('password') or ''
    client = SupportClient.objects.filter(email__iexact=email).first()
    if not client or not client.check_password(password):
        messages.error(request, 'Invalid email or password.')
        return redirect('public:remote_support')

    clear_rate_limit(rate_key)
    client.last_login_at = utc_now_naive()
    client.save(update_fields=['last_login_at'])
    request.session.cycle_key()  # Prevent session fixation
    request.session[PORTAL_SESSION_KEY] = client.id
    messages.success(request, 'Signed in successfully.')
    return redirect('public:remote_support')


def remote_support_logout(request):
    if request.method == 'POST':
        request.session.pop(PORTAL_SESSION_KEY, None)
        messages.success(request, 'Signed out.')
    return redirect('public:remote_support')


def remote_support_create_ticket(request):
    if request.method != 'POST':
        return redirect('public:remote_support')

    client = _get_portal_client(request)
    if client is None:
        messages.error(request, 'Please sign in to create a ticket.')
        return redirect('public:remote_support')

    subject = clean_text(request.POST.get('subject', ''), 300)
    service_slug = clean_text(request.POST.get('service_slug', ''), 200)
    priority = clean_text(request.POST.get('priority', ''), 20).lower()
    details = clean_text(request.POST.get('details', ''), 8000)
    if priority not in VALID_PRIORITIES:
        priority = 'normal'

    if not subject or not details:
        messages.error(request, 'Subject and issue details are required.')
        return redirect('public:remote_support')

    now = utc_now_naive()
    try:
        ticket = SupportTicket.objects.create(
            ticket_number=_generate_ticket_number(),
            client_id=client.id,
            subject=subject,
            service_slug=service_slug or None,
            priority=priority,
            status=SUPPORT_TICKET_STATUS_OPEN,
            details=details,
            internal_notes='',
            created_at=now,
            updated_at=now,
        )
        SupportTicketEvent.objects.create(
            ticket_id=ticket.id,
            event_type=SUPPORT_TICKET_EVENT_CREATED,
            message='Ticket submitted via remote support portal.',
            actor_type='client',
            actor_name=client.full_name,
            actor_client_id=client.id,
            status_from='',
            status_to=SUPPORT_TICKET_STATUS_OPEN,
            stage_from='',
            stage_to=support_ticket_stage_for_status(SUPPORT_TICKET_STATUS_OPEN),
            metadata_json=json.dumps({'source': 'remote_support_portal'}),
            created_at=now,
        )
    except Exception:
        messages.error(request, 'We could not create your ticket right now. Please try again shortly.')
        return redirect('public:remote_support')

    messages.success(request, f'Ticket {ticket.ticket_number} created successfully.')
    return redirect('public:remote_support')


def ticket_search(request):
    return render(request, 'ticket_search.html', {'ticket': None, 'verification': None, 'verification_email': ''})
