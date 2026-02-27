from __future__ import annotations

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import redirect, render

from admin_panel.models import ContactSubmission
from core.constants import WORKFLOW_PUBLISHED
from core.utils import clean_text, get_page_content, is_valid_email, utc_now_naive
from public.models import Service

QUOTE_BUDGET_OPTIONS = {
    'under_5k': 'Under $5,000',
    '5k_15k': '$5,000 - $15,000',
    '15k_50k': '$15,000 - $50,000',
    '50k_plus': '$50,000+',
    'not_sure': 'Not sure yet',
}
QUOTE_TIMELINE_OPTIONS = {
    'asap': 'ASAP (within 2 weeks)',
    '30_days': '30 days',
    '60_days': '60 days',
    '90_plus': '90+ days',
    'planning': 'Planning phase',
}
QUOTE_CONTACT_OPTIONS = {
    'email': 'Email',
    'phone': 'Phone',
    'either': 'Either email or phone',
}
QUOTE_COMPLIANCE_OPTIONS = {
    'none': 'No formal requirement',
    'hipaa': 'HIPAA',
    'pci': 'PCI-DSS',
    'soc2': 'SOC 2',
    'other': 'Other / mixed requirements',
}
QUOTE_URGENCY_OPTIONS = {
    'normal': 'Standard planning',
    'high': 'Priority initiative',
    'critical': 'Urgent business risk',
}


def _service_lists():
    qs = Service.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
        Q(is_trashed=False) | Q(is_trashed__isnull=True)
    )
    professional = list(qs.filter(service_type='professional').order_by('sort_order', 'id'))
    repair = list(qs.filter(service_type='repair').order_by('sort_order', 'id'))
    return professional, repair


def _ctx(page):
    professional_services, repair_services = _service_lists()
    return {
        'cb': get_page_content(page),
        'turnstile_enabled': False,
        'turnstile_site_key': '',
        'professional_services': professional_services,
        'repair_services': repair_services,
        'contact_options': QUOTE_CONTACT_OPTIONS,
    }


def _tracking_fields(request):
    return {
        'source_page': clean_text(request.path, 300),
        'utm_source': clean_text(request.GET.get('utm_source') or request.POST.get('utm_source') or '', 200),
        'utm_medium': clean_text(request.GET.get('utm_medium') or request.POST.get('utm_medium') or '', 200),
        'utm_campaign': clean_text(request.GET.get('utm_campaign') or request.POST.get('utm_campaign') or '', 200),
        'referrer_url': clean_text(request.META.get('HTTP_REFERER') or '', 500),
    }


def _create_submission(name, email, phone, subject, message_text, request):
    payload = _tracking_fields(request)
    try:
        ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message_text,
            is_read=False,
            lead_status='new',
            created_at=utc_now_naive(),
            **payload,
        )
        return True
    except Exception:
        return False


def _require(values):
    missing = [label for label, value in values if not value]
    return missing


def _build_business_quote_message(request):
    additional = [clean_text(item, 200) for item in request.POST.getlist('additional_services') if clean_text(item, 200)]
    lines = [
        f"Primary service: {clean_text(request.POST.get('primary_service_slug', ''), 200)}",
        f"Preferred contact: {clean_text(request.POST.get('preferred_contact', ''), 80)}",
        f"Budget range: {clean_text(request.POST.get('budget_range', ''), 80)}",
        f"Timeline: {clean_text(request.POST.get('timeline', ''), 80)}",
        f"Urgency: {clean_text(request.POST.get('urgency', ''), 80)}",
        f"Team size: {clean_text(request.POST.get('team_size', ''), 120)}",
        f"Locations: {clean_text(request.POST.get('location_count', ''), 120)}",
        f"Compliance: {clean_text(request.POST.get('compliance', ''), 80)}",
        f"Integrations: {clean_text(request.POST.get('integrations', ''), 400)}",
        f"Website: {clean_text(request.POST.get('website', ''), 300)}",
        f"Additional services: {', '.join(additional)}",
        '',
        'Business goals:',
        clean_text(request.POST.get('business_goals', ''), 3000),
        '',
        'Current challenges:',
        clean_text(request.POST.get('pain_points', ''), 3000),
        '',
        'Current environment:',
        clean_text(request.POST.get('current_environment', ''), 3000),
    ]
    return '\n'.join([line for line in lines if line is not None])


def _build_personal_quote_message(request):
    lines = [
        f"Service: {clean_text(request.POST.get('service_slug', ''), 200)}",
        f"Preferred contact: {clean_text(request.POST.get('preferred_contact', ''), 80)}",
        '',
        'Issue description:',
        clean_text(request.POST.get('issue_description', ''), 3000),
        '',
        'Additional notes:',
        clean_text(request.POST.get('additional_notes', ''), 3000),
    ]
    return '\n'.join([line for line in lines if line is not None])


def contact(request):
    if request.method == 'POST':
        name = clean_text(request.POST.get('name', ''), 200)
        email = clean_text(request.POST.get('email', ''), 200).lower()
        phone = clean_text(request.POST.get('phone', ''), 50)
        subject = clean_text(request.POST.get('subject', ''), 300) or 'Website Contact Form'
        message_text = clean_text(request.POST.get('message', ''), 5000)

        missing = _require(
            [
                ('full name', name),
                ('email', email),
                ('phone', phone),
                ('message', message_text),
            ]
        )
        if missing:
            messages.error(request, f"Please complete the required fields: {', '.join(missing)}.")
            return render(request, 'contact.html', _ctx('contact'))
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'contact.html', _ctx('contact'))

        if _create_submission(name, email, phone, subject, message_text, request):
            messages.success(request, 'Thank you. Your message was submitted and our team will follow up shortly.')
            return redirect('public:contact')
        messages.error(request, 'We could not submit your message right now. Please try again in a few minutes.')

    return render(request, 'contact.html', _ctx('contact'))


def request_quote(request):
    if request.method == 'POST':
        full_name = clean_text(request.POST.get('full_name', ''), 200)
        email = clean_text(request.POST.get('email', ''), 200).lower()
        phone = clean_text(request.POST.get('phone', ''), 50)
        company = clean_text(request.POST.get('company', ''), 200)
        primary_service = clean_text(request.POST.get('primary_service_slug', ''), 200)
        preferred_contact = clean_text(request.POST.get('preferred_contact', ''), 80)
        business_goals = clean_text(request.POST.get('business_goals', ''), 3000)
        pain_points = clean_text(request.POST.get('pain_points', ''), 3000)

        missing = _require(
            [
                ('full name', full_name),
                ('email', email),
                ('phone', phone),
                ('primary service', primary_service),
                ('preferred contact', preferred_contact),
                ('business goals', business_goals),
                ('current challenges', pain_points),
            ]
        )
        if missing:
            messages.error(request, f"Please complete the required fields: {', '.join(missing)}.")
            return render(request, 'request_quote.html', _ctx('request_quote'))
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'request_quote.html', _ctx('request_quote'))

        project_title = clean_text(request.POST.get('project_title', ''), 300)
        subject_parts = ['Business Quote Request']
        if project_title:
            subject_parts.append(project_title)
        if company:
            subject_parts.append(company)
        subject = ' | '.join(subject_parts)
        message_text = _build_business_quote_message(request)
        if _create_submission(full_name, email, phone, subject, message_text, request):
            messages.success(request, 'Thanks. Your business quote request has been submitted.')
            return redirect('public:request_quote')
        messages.error(request, 'We could not submit your quote request right now. Please try again in a few minutes.')

    ctx = _ctx('request_quote')
    ctx.update(
        {
            'budget_options': QUOTE_BUDGET_OPTIONS,
            'timeline_options': QUOTE_TIMELINE_OPTIONS,
            'contact_options': QUOTE_CONTACT_OPTIONS,
            'compliance_options': QUOTE_COMPLIANCE_OPTIONS,
            'urgency_options': QUOTE_URGENCY_OPTIONS,
        }
    )
    return render(request, 'request_quote.html', ctx)


def request_quote_personal(request):
    if request.method == 'POST':
        full_name = clean_text(request.POST.get('full_name', ''), 200)
        email = clean_text(request.POST.get('email', ''), 200).lower()
        phone = clean_text(request.POST.get('phone', ''), 50)
        service_slug = clean_text(request.POST.get('service_slug', ''), 200)
        preferred_contact = clean_text(request.POST.get('preferred_contact', ''), 80)
        issue_description = clean_text(request.POST.get('issue_description', ''), 3000)

        missing = _require(
            [
                ('full name', full_name),
                ('email', email),
                ('phone', phone),
                ('service needed', service_slug),
                ('preferred contact method', preferred_contact),
                ('issue description', issue_description),
            ]
        )
        if missing:
            messages.error(request, f"Please complete the required fields: {', '.join(missing)}.")
            return render(request, 'request_quote_personal.html', _ctx('request_quote_personal'))
        if not is_valid_email(email):
            messages.error(request, 'Please enter a valid email address.')
            return render(request, 'request_quote_personal.html', _ctx('request_quote_personal'))

        subject = f'Personal Quote Request | {service_slug}'
        message_text = _build_personal_quote_message(request)
        if _create_submission(full_name, email, phone, subject, message_text, request):
            messages.success(request, 'Thanks. Your personal quote request has been submitted.')
            return redirect('public:request_quote_personal')
        messages.error(request, 'We could not submit your quote request right now. Please try again in a few minutes.')

    return render(request, 'request_quote_personal.html', _ctx('request_quote_personal'))
