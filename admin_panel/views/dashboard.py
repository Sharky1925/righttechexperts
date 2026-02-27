from datetime import timedelta

from django.db.models import Q
from django.shortcuts import render

from admin_panel.decorators import permission_required
from admin_panel.models import (
    AuthRateLimitBucket,
    ContactSubmission,
    SecurityEvent,
    SupportTicket,
    normalize_ticket_number,
)
from admin_panel.views.content import workflow_status_label
from core.constants import (
    SUPPORT_TICKET_STATUS_IN_PROGRESS,
    SUPPORT_TICKET_STATUS_OPEN,
    SUPPORT_TICKET_STATUS_RESOLVED,
    SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
    WORKFLOW_APPROVED,
    WORKFLOW_DRAFT,
    WORKFLOW_PUBLISHED,
    WORKFLOW_REVIEW,
)
from core.utils import clean_text, utc_now_naive
from public.models import CmsPage, ContentBlock, Industry, Post, Service, SiteSetting

QUOTE_INTAKE_EMAIL = 'quote-intake@rightonrepair.local'
QUOTE_SUBJECT_PREFIX = 'quote request:'
QUOTE_DETAILS_PREFIX = 'quote intake submission'


def is_quote_ticket(ticket):
    if not ticket:
        return False
    subject = (getattr(ticket, 'subject', '') or '').strip().lower()
    details = (getattr(ticket, 'details', '') or '').strip().lower()
    client = getattr(ticket, 'client', None)
    client_email = (getattr(client, 'email', '') or '').strip().lower()
    return (
        subject.startswith(QUOTE_SUBJECT_PREFIX)
        or details.startswith(QUOTE_DETAILS_PREFIX)
        or client_email == QUOTE_INTAKE_EMAIL
    )


def _empty_search_results():
    return {
        'services': [],
        'industries': [],
        'posts': [],
        'contacts': [],
        'tickets': [],
    }


@permission_required('dashboard:view')
def dashboard(request):
    now = utc_now_naive()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    stale_cutoff = now - timedelta(days=14)
    open_ticket_statuses = [
        SUPPORT_TICKET_STATUS_OPEN,
        SUPPORT_TICKET_STATUS_IN_PROGRESS,
        SUPPORT_TICKET_STATUS_WAITING_CUSTOMER,
    ]

    ticket_lookup_query_raw = clean_text(request.GET.get('ticket_number', ''), 40)
    ticket_lookup_query = normalize_ticket_number(ticket_lookup_query_raw)
    search_query = clean_text(request.GET.get('q', ''), 120).lower().strip()
    ticket_lookup_result = None

    search_results = _empty_search_results()
    search_total = 0

    stats = {
        'services': 0,
        'industries': 0,
        'posts': 0,
        'contacts': 0,
        'contacts_24h': 0,
        'support_tickets': 0,
        'support_waiting': 0,
        'tickets_24h': 0,
        'resolved_7d': 0,
        'critical_open_tickets': 0,
        'services_missing_profile': 0,
        'industries_incomplete': 0,
        'published_posts_missing_excerpt': 0,
        'security_events_24h': 0,
        'active_admin_buckets': 0,
        'missing_setting_keys': 0,
    }
    health_score = 100
    health_checks = []
    missing_setting_keys = []
    urgent_tickets = []
    unread_contacts = []
    stale_drafts = []
    recent_contacts = []
    recent_tickets = []

    stats['services'] = Service.objects.count()
    stats['industries'] = Industry.objects.count()
    stats['posts'] = Post.objects.count()
    stats['contacts'] = ContactSubmission.objects.filter(is_read=False).count()
    stats['contacts_24h'] = ContactSubmission.objects.filter(created_at__gte=last_24h).count()
    stats['support_tickets'] = SupportTicket.objects.filter(status__in=open_ticket_statuses).count()
    stats['support_waiting'] = SupportTicket.objects.filter(status=SUPPORT_TICKET_STATUS_WAITING_CUSTOMER).count()
    stats['tickets_24h'] = SupportTicket.objects.filter(created_at__gte=last_24h).count()
    stats['resolved_7d'] = SupportTicket.objects.filter(
        status=SUPPORT_TICKET_STATUS_RESOLVED,
        updated_at__gte=last_7d,
    ).count()
    stats['critical_open_tickets'] = SupportTicket.objects.filter(
        status__in=open_ticket_statuses,
        priority__in=['high', 'critical'],
    ).count()
    stats['services_missing_profile'] = Service.objects.filter(
        Q(profile_json__isnull=True) | Q(profile_json__exact='')
    ).count()
    stats['industries_incomplete'] = Industry.objects.filter(
        Q(hero_description__isnull=True)
        | Q(hero_description__exact='')
        | Q(challenges__isnull=True)
        | Q(challenges__exact='')
        | Q(solutions__isnull=True)
        | Q(solutions__exact='')
    ).count()
    stats['published_posts_missing_excerpt'] = Post.objects.filter(
        workflow_status=WORKFLOW_PUBLISHED
    ).filter(
        Q(excerpt__isnull=True) | Q(excerpt__exact='')
    ).count()
    stats['security_events_24h'] = SecurityEvent.objects.filter(
        created_at__gte=last_24h,
        event_type__in=['turnstile_failed', 'rate_limited'],
    ).count()
    stats['active_admin_buckets'] = AuthRateLimitBucket.objects.filter(
        scope='admin_login',
        count__gt=0,
        reset_at__gt=now,
    ).count()

    required_settings = {'company_name', 'email', 'meta_title', 'meta_description'}
    current_settings = {
        key: (value or '')
        for key, value in SiteSetting.objects.filter(key__in=required_settings).values_list('key', 'value')
    }
    missing_setting_keys = [
        key for key in required_settings if not current_settings.get(key, '').strip()
    ]
    stats['missing_setting_keys'] = len(missing_setting_keys)

    response_backlog = stats['contacts'] + stats['support_waiting'] + stats['critical_open_tickets']
    content_issues = stats['services_missing_profile'] + stats['industries_incomplete']
    seo_issues = stats['published_posts_missing_excerpt'] + stats['missing_setting_keys']
    security_issues = stats['security_events_24h'] + stats['active_admin_buckets']
    health_penalty = (content_issues * 4) + (seo_issues * 3) + (response_backlog * 2) + (security_issues * 2)
    health_score = max(10, min(100, 100 - health_penalty))

    health_checks = [
        {
            'label': 'Content Structure',
            'issues': content_issues,
            'href': '/admin/services',
            'description': 'Service profile coverage and industry challenge/solution completeness.',
        },
        {
            'label': 'SEO Readiness',
            'issues': seo_issues,
            'href': '/admin/posts',
            'description': 'Published excerpts plus global metadata settings coverage.',
        },
        {
            'label': 'Response Backlog',
            'issues': response_backlog,
            'href': '/admin/support-tickets',
            'description': 'Unread leads, waiting-client tickets, and urgent open support items.',
        },
        {
            'label': 'Security Watchlist',
            'issues': security_issues,
            'href': '/admin/security-events',
            'description': 'Rate-limiting and Turnstile failures in the last 24 hours.',
        },
    ]
    for check in health_checks:
        issues = check['issues']
        if issues == 0:
            check['state'] = 'good'
        elif issues <= 3:
            check['state'] = 'warn'
        else:
            check['state'] = 'critical'

    urgent_tickets = list(
        SupportTicket.objects.select_related('client')
        .filter(status__in=open_ticket_statuses, priority__in=['high', 'critical'])
        .order_by('-updated_at')[:6]
    )
    unread_contacts = list(ContactSubmission.objects.filter(is_read=False).order_by('-created_at')[:6])
    stale_drafts = list(
        Post.objects.filter(
            workflow_status__in=[WORKFLOW_DRAFT, WORKFLOW_REVIEW, WORKFLOW_APPROVED],
            updated_at__lte=stale_cutoff,
        ).order_by('updated_at')[:6]
    )
    recent_contacts = list(ContactSubmission.objects.order_by('-created_at')[:6])
    recent_tickets = list(SupportTicket.objects.select_related('client').order_by('-updated_at')[:6])

    if ticket_lookup_query:
        ticket_lookup_result = (
            SupportTicket.objects.select_related('client')
            .filter(ticket_number=ticket_lookup_query)
            .first()
        )

    if search_query:
        search_results['services'] = list(
            Service.objects.filter(
                Q(title__icontains=search_query)
                | Q(slug__icontains=search_query)
                | Q(description__icontains=search_query)
            ).order_by('sort_order', 'id')[:6]
        )
        search_results['industries'] = list(
            Industry.objects.filter(
                Q(title__icontains=search_query)
                | Q(slug__icontains=search_query)
                | Q(description__icontains=search_query)
            ).order_by('sort_order', 'id')[:6]
        )
        search_results['posts'] = list(
            Post.objects.filter(
                Q(title__icontains=search_query)
                | Q(slug__icontains=search_query)
                | Q(excerpt__icontains=search_query)
            ).order_by('-updated_at')[:6]
        )
        search_results['contacts'] = list(
            ContactSubmission.objects.filter(
                Q(name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(subject__icontains=search_query)
            ).order_by('-created_at')[:6]
        )
        search_results['tickets'] = list(
            SupportTicket.objects.select_related('client')
            .filter(
                Q(ticket_number__icontains=search_query)
                | Q(subject__icontains=search_query)
                | Q(client__full_name__icontains=search_query)
                | Q(client__email__icontains=search_query)
            )
            .order_by('-updated_at')[:6]
        )
        search_total = sum(len(items) for items in search_results.values())

    return render(
        request,
        'admin/dashboard.html',
        {
            'stats': stats,
            'health_score': health_score,
            'health_checks': health_checks,
            'missing_setting_keys': missing_setting_keys,
            'urgent_tickets': urgent_tickets,
            'unread_contacts': unread_contacts,
            'stale_drafts': stale_drafts,
            'search_query': search_query,
            'search_results': search_results,
            'search_total': search_total,
            'recent_contacts': recent_contacts,
            'recent_tickets': recent_tickets,
            'ticket_lookup_query': ticket_lookup_query,
            'ticket_lookup_result': ticket_lookup_result,
            'is_quote_ticket': is_quote_ticket,
            'workflow_status_label': workflow_status_label,
        },
    )


@permission_required('dashboard:view')
def control_center(request):
    now = utc_now_naive()
    website_modules = [
        {
            'title': 'Services',
            'description': 'Manage public service pages and workflow.',
            'icon': 'fa-solid fa-gear',
            'href': '/admin/services',
            'permission': 'content:manage',
            'metric': f'{Service.objects.count()} items',
        },
        {
            'title': 'Industries',
            'description': 'Manage industry-specific pages and content.',
            'icon': 'fa-solid fa-building',
            'href': '/admin/industries',
            'permission': 'content:manage',
            'metric': f'{Industry.objects.count()} items',
        },
        {
            'title': 'Blog Posts',
            'description': 'Draft, review, and publish blog content.',
            'icon': 'fa-solid fa-newspaper',
            'href': '/admin/posts',
            'permission': 'content:manage',
            'metric': f'{Post.objects.count()} posts',
        },
        {
            'title': 'Media Library',
            'description': 'Upload and manage media assets.',
            'icon': 'fa-solid fa-photo-film',
            'href': '/admin/media',
            'permission': 'content:manage',
            'metric': 'Asset manager',
        },
        {
            'title': 'ACP Studio',
            'description': 'Visual page and dashboard studio controls.',
            'icon': 'fa-solid fa-screwdriver-wrench',
            'href': '/admin/acp/studio',
            'permission': 'acp:studio:view',
            'metric': 'Visual builder',
        },
    ]

    operations_modules = [
        {
            'title': 'Dashboard',
            'description': 'Operational metrics and alerting overview.',
            'icon': 'fa-solid fa-gauge',
            'href': '/admin/',
            'permission': 'dashboard:view',
            'metric': 'Live status',
        },
        {
            'title': 'Contacts',
            'description': 'Lead inbox and qualification workflow.',
            'icon': 'fa-solid fa-envelope',
            'href': '/admin/contacts',
            'permission': 'support:manage',
            'metric': f'{ContactSubmission.objects.filter(is_read=False).count()} unread',
        },
        {
            'title': 'Support Tickets',
            'description': 'Track, review, and resolve client tickets.',
            'icon': 'fa-solid fa-ticket',
            'href': '/admin/support-tickets',
            'permission': 'support:manage',
            'metric': f'{SupportTicket.objects.count()} total',
        },
        {
            'title': 'Security Events',
            'description': 'Audit suspicious events and rate limits.',
            'icon': 'fa-solid fa-shield-halved',
            'href': '/admin/security-events',
            'permission': 'security:view',
            'metric': f'{SecurityEvent.objects.filter(created_at__gte=now - timedelta(hours=24)).count()} / 24h',
        },
        {
            'title': 'Settings',
            'description': 'Global site, SEO, and headless settings.',
            'icon': 'fa-solid fa-sliders',
            'href': '/admin/settings',
            'permission': 'settings:manage',
            'metric': 'Configuration',
        },
    ]

    visible_website_modules = [
        item for item in website_modules if request.user.has_permission(item['permission'])
    ]
    visible_operations_modules = [
        item for item in operations_modules if request.user.has_permission(item['permission'])
    ]

    quick_actions = []
    if request.user.has_permission('content:manage'):
        quick_actions.append(
            {'label': 'New Post', 'href': '/admin/posts/add', 'icon': 'fa-solid fa-plus'}
        )
        quick_actions.append(
            {'label': 'New Service', 'href': '/admin/services/add', 'icon': 'fa-solid fa-plus'}
        )
    if request.user.has_permission('support:manage'):
        quick_actions.append(
            {'label': 'Open Ticket Queue', 'href': '/admin/support-tickets', 'icon': 'fa-solid fa-ticket'}
        )
    if request.user.has_permission('settings:manage'):
        quick_actions.append(
            {'label': 'Headless Hub', 'href': '/admin/headless-hub', 'icon': 'fa-solid fa-cloud-arrow-down'}
        )

    published_pages = CmsPage.objects.filter(is_published=True).count()
    try:
        from acp.models import AcpDashboardDocument

        published_dashboards = AcpDashboardDocument.objects.filter(status=WORKFLOW_PUBLISHED).count()
    except Exception:
        published_dashboards = 0

    return render(
        request,
        'admin/control_center.html',
        {
            'website_modules': visible_website_modules,
            'operations_modules': visible_operations_modules,
            'quick_actions': quick_actions,
            'section_stats': {
                'website_total': len(visible_website_modules),
                'operations_total': len(visible_operations_modules),
                'published_pages': published_pages,
                'published_dashboards': published_dashboards,
                'metrics': 0,
                'mcp_servers': 0,
                'mcp_operations': 0,
                'content_blocks': ContentBlock.objects.count(),
            },
        },
    )
