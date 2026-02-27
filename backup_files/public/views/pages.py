from __future__ import annotations

import json
import re
from types import SimpleNamespace

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render

from core.constants import ORANGE_COUNTY_CA_CITIES, WORKFLOW_PUBLISHED
from core.service_seo_overrides import SERVICE_RESEARCH_OVERRIDES
from core.utils import clean_text, get_page_content
from public.models import Category, CmsArticle, CmsPage, Industry, Post, Service, TeamMember, Testimonial

SERVICE_SLUG_ALIASES = {
    'computer-laptop-repair': 'laptop-repair',
    'server-network-repair': 'mobile-phone-repair',
    'printer-peripheral-repair': 'game-console-repair',
    'virus-malware-removal': 'device-diagnostics',
    'hardware-installation-upgrades': 'surveillance-camera-installation',
    'data-analytics-bi': 'web-development',
    'it-consulting-strategy': 'managed-it-services',
}

VIRTUAL_SERVICE_DEFINITIONS = (
    {
        'id': -9001,
        'slug': 'laptop-repair',
        'title': 'Laptop Repair',
        'description': (
            'Fast laptop diagnostics and repair in Orange County: screen replacement, battery swap, '
            'charging-port repair, keyboard and hinge fixes, thermal cleanup, and SSD performance recovery.'
        ),
        'icon_class': 'fa-solid fa-laptop-medical',
        'service_type': 'repair',
        'sort_order': 12,
        'is_featured': True,
    },
)

INDUSTRY_SLUG_ALIASES = {
    'healthcare': 'healthcare-clinics',
    'finance-banking': 'law-firms',
    'education': 'construction-field-services',
    'retail-e-commerce': 'retail-ecommerce',
    'real-estate': 'real-estate-property-management',
    'legal': 'professional-services',
    'hospitality': 'nonprofits',
}

ICON_CLASS_RE = re.compile(r'^fa-(solid|regular|brands)\s+fa-[a-z0-9-]+$')
ICON_CLASS_ALIASES = {
    'fa-ranking-star': 'fa-chart-line',
    'fa-filter-circle-dollar': 'fa-bullseye',
    'fa-radar': 'fa-crosshairs',
    'fa-siren-on': 'fa-bell',
    'fa-shield-check': 'fa-shield-halved',
}
VALID_ICON_STYLES = {'fa-solid', 'fa-regular', 'fa-brands'}


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

    def iter_pages(self, left_edge=1, right_edge=1, left_current=1, right_current=2):
        last = 0
        for num in self._page.paginator.page_range:
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


def normalize_icon_class(icon_class, fallback='fa-solid fa-circle'):
    fallback = fallback if ICON_CLASS_RE.match(fallback) else 'fa-solid fa-circle'
    raw = clean_text(str(icon_class or ''), 120)
    if not raw:
        return fallback

    parts = raw.split()
    if len(parts) == 1 and parts[0].startswith('fa-'):
        style, glyph = 'fa-solid', parts[0]
    else:
        style = parts[0] if parts else 'fa-solid'
        glyph = parts[1] if len(parts) > 1 else ''

    if style not in VALID_ICON_STYLES:
        style = 'fa-solid'

    glyph = ICON_CLASS_ALIASES.get(glyph, glyph)
    normalized = f'{style} {glyph}'.strip()
    if not ICON_CLASS_RE.match(normalized):
        return fallback
    return normalized


def normalize_icon_attr(items, fallback):
    for item in items:
        item.icon_class = normalize_icon_class(getattr(item, 'icon_class', ''), fallback)
    return items


def _active_queryset(model):
    if hasattr(model, 'is_trashed'):
        return model.objects.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
    return model.objects.all()


def _published_queryset(model):
    if hasattr(model, 'workflow_status'):
        return _active_queryset(model).filter(workflow_status=WORKFLOW_PUBLISHED)
    return _active_queryset(model)


def _service_base_queryset():
    return _active_queryset(Service).order_by('sort_order', 'id')


def _service_queryset(only_published=True):
    if only_published:
        return _published_queryset(Service).order_by('sort_order', 'id')
    return _service_base_queryset()


def _virtual_services():
    items = []
    for definition in VIRTUAL_SERVICE_DEFINITIONS:
        items.append(
            SimpleNamespace(
                id=definition.get('id', 0),
                slug=definition.get('slug', ''),
                title=definition.get('title', ''),
                description=definition.get('description', ''),
                icon_class=definition.get('icon_class', 'fa-solid fa-circle'),
                service_type=definition.get('service_type', 'repair'),
                sort_order=definition.get('sort_order', 0),
                is_featured=bool(definition.get('is_featured', False)),
                profile_json='',
                seo_title='',
                seo_description='',
                og_image='',
                workflow_status=WORKFLOW_PUBLISHED,
                image='',
                scheduled_publish_at=None,
                published_at=None,
                created_at=None,
                updated_at=None,
            )
        )
    return items


def _virtual_service_by_slug(slug):
    normalized = clean_text(slug, 180)
    for item in _virtual_services():
        if item.slug == normalized:
            return item
    return None


def _inject_virtual_services(items, *, service_type=None, is_featured=None, exclude_id=None):
    merged = list(items)
    existing_slugs = {clean_text(getattr(item, 'slug', ''), 200) for item in merged}
    for candidate in _virtual_services():
        if candidate.slug in existing_slugs:
            continue
        if service_type and candidate.service_type != service_type:
            continue
        if is_featured is not None and bool(candidate.is_featured) != bool(is_featured):
            continue
        if exclude_id is not None and candidate.id == exclude_id:
            continue
        merged.append(candidate)
        existing_slugs.add(candidate.slug)
    return sorted(
        merged,
        key=lambda item: (
            int(getattr(item, 'sort_order', 0) or 0),
            int(getattr(item, 'id', 0) or 0),
        ),
    )


def _industry_base_queryset():
    return _active_queryset(Industry).order_by('sort_order', 'id')


def _industry_queryset(only_published=True):
    if only_published:
        return _published_queryset(Industry).order_by('sort_order', 'id')
    return _industry_base_queryset()


def _service_list(service_type=None, is_featured=None, exclude_id=None, limit=None, allow_fallback=True):
    def _apply(base):
        q = base
        if service_type:
            q = q.filter(service_type=service_type)
        if is_featured is not None:
            q = q.filter(is_featured=bool(is_featured))
        if exclude_id is not None:
            q = q.exclude(id=exclude_id)
        return list(q)

    items = _inject_virtual_services(
        _apply(_service_queryset(only_published=True)),
        service_type=service_type,
        is_featured=is_featured,
        exclude_id=exclude_id,
    )
    if not items and allow_fallback:
        items = _inject_virtual_services(
            _apply(_service_queryset(only_published=False)),
            service_type=service_type,
            is_featured=is_featured,
            exclude_id=exclude_id,
        )
    if limit:
        return items[:limit]
    return items


def _industry_list(limit=None, allow_fallback=True):
    def _apply(base):
        q = base
        if limit:
            q = q[:limit]
        return list(q)

    items = _apply(_industry_queryset(only_published=True))
    if items or not allow_fallback:
        return items
    return _apply(_industry_queryset(only_published=False))


def _base_context():
    return {
        'cb': {},
        'hero_cards': [],
        'pro_services': [],
        'repair_services': [],
        'nav_industries': [],
        'team': [],
        'testimonials': [],
        'recent_posts': [],
        'service': None,
        'industry': None,
        'post': None,
    }


def _compact_excerpt(value, limit=260):
    text = re.sub(r'\s+', ' ', str(value or '')).strip()
    if len(text) <= limit:
        return text
    safe_limit = max(1, limit - 3)
    return f'{text[:safe_limit].rstrip()}...'


def _safe_json_dict(raw):
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        loaded = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _safe_str_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [chunk.strip() for chunk in value.split(',') if chunk.strip()]
    return []


def _safe_dict_list(value):
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _default_service_profile(service):
    is_professional = (service.service_type or '').strip().lower() == 'professional'
    description = _compact_excerpt(getattr(service, 'description', ''), 220)
    if not description:
        description = f'{service.title} service support for Orange County businesses.'

    if is_professional:
        process = [
            {'title': 'Discovery', 'detail': 'Map requirements, risks, and success criteria.', 'icon': 'fa-solid fa-clipboard-check'},
            {'title': 'Architecture', 'detail': 'Design secure workflows, integrations, and standards.', 'icon': 'fa-solid fa-diagram-project'},
            {'title': 'Implementation', 'detail': 'Deliver in milestones with validation at each stage.', 'icon': 'fa-solid fa-gears'},
            {'title': 'Optimization', 'detail': 'Refine performance and outcomes with measurable reporting.', 'icon': 'fa-solid fa-chart-line'},
        ]
        tools = [
            {'name': 'Microsoft 365', 'icon': 'fa-brands fa-microsoft', 'desc': 'Identity, productivity, and endpoint workflows'},
            {'name': 'Cloudflare', 'icon': 'fa-solid fa-cloud', 'desc': 'Edge networking, security, and performance controls'},
            {'name': 'Endpoint Monitoring', 'icon': 'fa-solid fa-desktop', 'desc': 'Visibility into uptime, incidents, and drift'},
            {'name': 'Secure Access', 'icon': 'fa-solid fa-shield-halved', 'desc': 'Policy-based authentication and access control'},
        ]
        deliverables = [
            {'label': 'Coverage', 'value': 'Strategic delivery aligned to business goals', 'icon': 'fa-solid fa-layer-group'},
            {'label': 'Security', 'value': 'Risk-aware controls and compliance alignment', 'icon': 'fa-solid fa-shield-halved'},
            {'label': 'Performance', 'value': 'Stable operations with optimization visibility', 'icon': 'fa-solid fa-gauge-high'},
            {'label': 'Support', 'value': 'Structured escalation and accountable communication', 'icon': 'fa-solid fa-headset'},
        ]
        hero_badges = [
            {'icon': 'fa-solid fa-layer-group', 'label': 'Strategic Discovery and Planning'},
            {'icon': 'fa-solid fa-gears', 'label': 'Milestone-Based Implementation'},
            {'icon': 'fa-solid fa-chart-line', 'label': 'Continuous Performance Optimization'},
        ]
    else:
        process = [
            {'title': 'Intake & Diagnostics', 'detail': 'Capture symptoms and run root-cause tests.', 'icon': 'fa-solid fa-stethoscope'},
            {'title': 'Repair Plan', 'detail': 'Confirm scope, parts, and expected turnaround.', 'icon': 'fa-solid fa-screwdriver-wrench'},
            {'title': 'Repair Execution', 'detail': 'Apply component-level fixes with QA checkpoints.', 'icon': 'fa-solid fa-microchip'},
            {'title': 'Validation', 'detail': 'Stress test and verify full functional readiness.', 'icon': 'fa-solid fa-circle-check'},
        ]
        tools = [
            {'name': 'Bench Diagnostics', 'icon': 'fa-solid fa-laptop-medical', 'desc': 'Hardware and subsystem verification workflows'},
            {'name': 'Data-Safe Handling', 'icon': 'fa-solid fa-user-lock', 'desc': 'Minimized risk during repair and recovery handling'},
            {'name': 'Thermal + Power Tests', 'icon': 'fa-solid fa-temperature-half', 'desc': 'Performance and stability validation under load'},
            {'name': 'Post-Repair QA', 'icon': 'fa-solid fa-list-check', 'desc': 'Final checklist before customer handoff'},
        ]
        deliverables = [
            {'label': 'Diagnostics', 'value': 'Root-cause confirmation before repairs', 'icon': 'fa-solid fa-stethoscope'},
            {'label': 'Turnaround', 'value': 'Clear checkpoints and status visibility', 'icon': 'fa-solid fa-stopwatch'},
            {'label': 'Parts Quality', 'value': 'Verified components and repair standards', 'icon': 'fa-solid fa-microchip'},
            {'label': 'Validation', 'value': 'Functional and stress testing complete', 'icon': 'fa-solid fa-circle-check'},
        ]
        hero_badges = [
            {'icon': 'fa-solid fa-stethoscope', 'label': 'Diagnostics-First Workflow'},
            {'icon': 'fa-solid fa-screwdriver-wrench', 'label': 'Component-Level Repair Paths'},
            {'icon': 'fa-solid fa-circle-check', 'label': 'Validation Before Handoff'},
        ]

    return {
        'meta_description': description,
        'meta_title': f'{service.title} in Orange County | Right On Repair',
        'keywords': [
            f'{service.title} Orange County',
            f'{service.title} services',
            'business IT support',
            'Right On Repair',
        ],
        'intro_kicker': 'Solutions',
        'positioning_badge': 'Service Delivery Program',
        'board_title': 'Service Workflow',
        'modules_title': 'Specialized Service Programs',
        'narrative_title': 'Service Scope and Delivery Standards',
        'process': process,
        'tools': tools,
        'deliverables': deliverables,
        'hero_badges': hero_badges,
        'service_modules': [
            {'title': item['title'], 'detail': item['detail'], 'icon': item['icon']} for item in process[:4]
        ],
        'issue_solution_map': [
            {
                'issue': f'{item["title"]} gaps creating inconsistent outcomes',
                'solution': item['detail'],
                'icon': item['icon'],
            }
            for item in process[:4]
        ],
        'lead_time_diagram': [
            {
                'phase': item['title'],
                'eta': '1-3 business days',
                'detail': item['detail'],
                'icon': item['icon'],
            }
            for item in process[:4]
        ],
        'faqs': [
            {
                'q': f'What is included in {service.title.lower()}?',
                'a': 'We scope your requirements, deliver with clear milestones, and provide post-delivery support and optimization guidance.',
            },
            {
                'q': 'Can this be tailored to our environment?',
                'a': 'Yes. Every engagement is adapted to your business workflows, constraints, and growth goals.',
            },
            {
                'q': 'Do you provide post-delivery support?',
                'a': 'Yes. We offer ongoing support, reporting, and improvement cycles after implementation.',
            },
        ],
        'seo_content_blocks': [],
        'service_area_cities': list(ORANGE_COUNTY_CA_CITIES),
        'compliance_frameworks': ['NIST-aligned controls', 'Least-privilege access principles', 'Routine security review cadences'],
        'proof_points': [
            {'label': 'Scope', 'value': 'Clear objectives and accountable ownership'},
            {'label': 'Reliability', 'value': 'Stability-first implementation and testing'},
            {'label': 'Visibility', 'value': 'Actionable reporting and communication cadence'},
        ],
        'related_technologies': [item['name'] for item in tools],
        'supported_brands': [],
        'brand_services': [],
    }


def _normalize_service_profile(service):
    profile = _default_service_profile(service)
    incoming = _safe_json_dict(getattr(service, 'profile_json', None))
    if not incoming:
        research_defaults = SERVICE_RESEARCH_OVERRIDES.get(service.slug, {})
        if isinstance(research_defaults, dict):
            incoming = research_defaults

    # Scalar overrides.
    for key in (
        'meta_description',
        'meta_title',
        'intro_kicker',
        'positioning_badge',
        'board_title',
        'modules_title',
        'narrative_title',
    ):
        value = clean_text(incoming.get(key, ''), 500)
        if value:
            profile[key] = value

    # Keywords and string-list overrides.
    keywords = _safe_str_list(incoming.get('keywords'))
    if keywords:
        profile['keywords'] = keywords

    related_tech = _safe_str_list(incoming.get('related_technologies'))
    if related_tech:
        profile['related_technologies'] = related_tech

    service_area_cities = _safe_str_list(incoming.get('service_area_cities'))
    if service_area_cities:
        profile['service_area_cities'] = service_area_cities
    # Keep every Cities We Serve component aligned to complete Orange County city coverage.
    profile['service_area_cities'] = list(ORANGE_COUNTY_CA_CITIES)

    compliance_frameworks = _safe_str_list(incoming.get('compliance_frameworks'))
    if compliance_frameworks:
        profile['compliance_frameworks'] = compliance_frameworks

    # List-of-string content blocks.
    seo_blocks = incoming.get('seo_content_blocks')
    if isinstance(seo_blocks, list):
        cleaned_blocks = [clean_text(str(item), 1000) for item in seo_blocks if clean_text(str(item), 1000)]
        if cleaned_blocks:
            profile['seo_content_blocks'] = cleaned_blocks

    # Dict list with icon normalization.
    def _normalize_icon_list(source_key, target_key, icon_fallback, fields):
        raw = _safe_dict_list(incoming.get(source_key))
        if not raw:
            raw = _safe_dict_list(profile.get(target_key))
        normalized = []
        for item in raw:
            candidate = {}
            for field in fields:
                val = clean_text(str(item.get(field, '')), 1000)
                if val:
                    candidate[field] = val
            candidate['icon'] = normalize_icon_class(item.get('icon', ''), icon_fallback)
            if any(candidate.get(field) for field in fields):
                normalized.append(candidate)
        if normalized:
            profile[target_key] = normalized

    _normalize_icon_list('process', 'process', 'fa-solid fa-diagram-project', ('title', 'detail'))
    _normalize_icon_list('tools', 'tools', 'fa-solid fa-wrench', ('name', 'desc'))
    _normalize_icon_list('deliverables', 'deliverables', 'fa-solid fa-bullseye', ('label', 'value'))
    _normalize_icon_list('hero_badges', 'hero_badges', 'fa-solid fa-circle-check', ('label',))
    _normalize_icon_list('service_modules', 'service_modules', 'fa-solid fa-cubes', ('title', 'detail'))
    _normalize_icon_list('issue_solution_map', 'issue_solution_map', 'fa-solid fa-circle-info', ('issue', 'solution'))
    _normalize_icon_list('lead_time_diagram', 'lead_time_diagram', 'fa-solid fa-hourglass-half', ('phase', 'eta', 'detail'))

    # Dict list without icons.
    proof_points = _safe_dict_list(incoming.get('proof_points'))
    if proof_points:
        normalized_points = []
        for item in proof_points:
            label = clean_text(str(item.get('label', '')), 140)
            value = clean_text(str(item.get('value', '')), 500)
            if label and value:
                normalized_points.append({'label': label, 'value': value})
        if normalized_points:
            profile['proof_points'] = normalized_points

    brand_services = _safe_dict_list(incoming.get('brand_services'))
    if brand_services:
        normalized_brand_services = []
        for item in brand_services:
            brand = clean_text(str(item.get('brand', '')), 200)
            services = clean_text(str(item.get('services', '')), 500)
            if brand and services:
                normalized_brand_services.append({'brand': brand, 'services': services})
        if normalized_brand_services:
            profile['brand_services'] = normalized_brand_services

    supported_brands = _safe_str_list(incoming.get('supported_brands'))
    if supported_brands:
        profile['supported_brands'] = supported_brands

    faqs = _safe_dict_list(incoming.get('faqs'))
    if faqs:
        normalized_faqs = []
        for item in faqs:
            question = clean_text(str(item.get('q', '')), 260)
            answer = clean_text(str(item.get('a', '')), 1000)
            if question and answer:
                normalized_faqs.append({'q': question, 'a': answer})
        if normalized_faqs:
            profile['faqs'] = normalized_faqs

    # Ensure keywords include local intent variants.
    keyword_set = {k.lower() for k in profile['keywords']}
    for variant in (f'{service.title} Irvine', f'{service.title} Santa Ana', f'{service.title} Anaheim'):
        if variant.lower() not in keyword_set:
            profile['keywords'].append(variant)
            keyword_set.add(variant.lower())

    description = _compact_excerpt(getattr(service, 'description', ''), 220)
    if not description:
        description = f'{service.title} service support for Orange County businesses.'
    if not clean_text(profile.get('meta_description', ''), 500):
        profile['meta_description'] = description
    if not clean_text(profile.get('meta_title', ''), 180):
        profile['meta_title'] = f'{service.title} in Orange County | Right On Repair'

    if not profile.get('related_technologies'):
        profile['related_technologies'] = [item.get('name', '') for item in profile.get('tools', []) if item.get('name')]

    return profile


# ── Rich content details per industry ────────────────────────────────
INDUSTRY_CONTENT_DETAILS = {
    'healthcare-clinics': {
        'challenge_descriptions': {
            'Downtime during intake and charting': 'System failures during patient check-in slow workflows and frustrate staff, causing delays in care delivery.',
            'Shared workstations with weak controls': 'Multiple users sharing a single login create audit gaps and increase the risk of unauthorized access to PHI.',
            'Aging clinical endpoints': 'Outdated desktops and peripherals lead to slow performance, security vulnerabilities, and incompatibility with modern EHR platforms.',
            'EHR vendor complexity': 'Coordinating updates, integrations, and troubleshooting across EHR vendors requires specialized IT knowledge.',
            'HIPAA security pressure': 'Clinics must meet strict compliance standards for data encryption, access logs, and breach notification protocols.',
        },
        'solution_descriptions': {
            'Role-based access and MFA': 'Enforce least-privilege access with multi-factor authentication to protect patient data at every login.',
            'Endpoint hardening and patching': 'Automated patching and security baselines keep clinical devices compliant and protected against known threats.',
            'EHR workflow support': 'Dedicated support for EHR systems including vendor coordination, update management, and performance optimization.',
            'Backup and recovery planning': 'HIPAA-compliant backup strategies with regular recovery testing ensure business continuity after any incident.',
            'Documented escalation playbooks': 'Pre-built response procedures so staff know exactly what to do during critical IT issues.',
        },
        'seo_keywords': 'healthcare IT support, HIPAA compliant IT, medical office technology, EHR support, clinic IT services, healthcare cybersecurity, patient data protection, Orange County healthcare IT',
        'seo_description': 'HIPAA-compliant managed IT services for healthcare clinics in Orange County. Secure EHR support, endpoint protection, and 24/7 monitoring for medical practices.',
    },
    'law-firms': {
        'challenge_descriptions': {
            'Case document bottlenecks': 'Slow document retrieval and version conflicts waste billable hours and increase risk of filing errors.',
            'Risky file sharing practices': 'Attorneys sharing sensitive case files via personal email or unencrypted drives create confidentiality breaches.',
            'Unmanaged remote access': 'Lawyers working remotely without secured VPN or endpoint controls expose client data to interception.',
            'Weak backup visibility': 'Without verified backups, a ransomware attack or hardware failure could mean permanent loss of case files.',
            'Phishing exposure': 'Legal staff are prime phishing targets due to time pressure and high-value client information they handle.',
        },
        'solution_descriptions': {
            'Access-controlled document workflows': 'Secure document management with role-based permissions and audit trails for every file interaction.',
            'Endpoint and identity hardening': 'Advanced endpoint protection and identity verification to prevent unauthorized access to client data.',
            'Secure remote collaboration': 'Encrypted VPN, secure file sharing, and compliant video conferencing for remote legal work.',
            'Backup validation and continuity': 'Regular backup testing and disaster recovery drills to ensure case files are always recoverable.',
            'Priority deadline support': 'Expedited IT support aligned with court deadlines and filing schedules to prevent costly delays.',
        },
        'seo_keywords': 'law firm IT support, legal technology services, legal document management, law firm cybersecurity, attorney IT services, legal compliance IT, Orange County law firm IT',
        'seo_description': 'Secure IT solutions for law firms in Orange County. Confidential document management, endpoint protection, and priority support aligned with court deadlines.',
    },
    'construction-field-services': {
        'challenge_descriptions': {
            'Field device failures': 'Tablets, phones, and ruggedized devices break down in harsh jobsite conditions, halting daily reports and communication.',
            'Unstable office-jobsite connectivity': 'Poor network links between the main office and remote jobsites create delays in project management and file access.',
            'Inconsistent mobile security': 'Field workers using personal devices without security policies expose project data to theft and malware.',
            'Shared credentials': 'Teams sharing one login across multiple devices eliminates accountability and makes breach investigation impossible.',
            'Slow incident response': 'When a device or system fails on a jobsite, delayed IT response causes idle crews and missed milestones.',
        },
        'solution_descriptions': {
            'Mobile device standardization': 'Uniform device configurations with remote management ensure every field worker has secure, reliable tools.',
            'Cloud collaboration hardening': 'Secure cloud-based project management, file sharing, and communication tools accessible from any jobsite.',
            'Secure onboarding and offboarding': 'Automated provisioning and de-provisioning of field worker accounts to prevent unauthorized access after turnover.',
            'Priority field support': 'Rapid remote and onsite IT support prioritized for time-sensitive construction operations.',
            'Diagnostics and lifecycle planning': 'Proactive device health monitoring and replacement scheduling to prevent unexpected equipment failures.',
        },
        'seo_keywords': 'construction IT support, field services technology, jobsite IT solutions, mobile device management construction, construction cybersecurity, Orange County construction IT',
        'seo_description': 'Reliable IT support for construction and field service companies in Orange County. Mobile device management, secure cloud access, and rapid onsite support.',
    },
    'manufacturing': {
        'challenge_descriptions': {
            'Production-impacting outages': 'Unplanned IT downtime stops production lines, causing costly delays and missed delivery commitments.',
            'Aging infrastructure': 'Legacy systems and outdated network equipment create bottlenecks and increase vulnerability to cyberattacks.',
            'Mixed legacy and modern systems': 'Integrating older industrial control systems with modern cloud platforms introduces compatibility and security risks.',
            'Patch risk on live operations': 'Applying security patches during production hours risks system crashes and unexpected behavior on critical equipment.',
            'Weak recovery testing': 'Without regular disaster recovery drills, manufacturers cannot guarantee they can restore operations after a breach.',
        },
        'solution_descriptions': {
            'Proactive monitoring with safe maintenance windows': 'Continuous monitoring with scheduled maintenance during planned downtime to minimize production disruption.',
            'Endpoint and identity hardening': 'Secure authentication and endpoint controls to protect both office workstations and production floor systems.',
            'Backup and recovery validation': 'Regular backup testing with documented recovery procedures to verify data can be restored under real conditions.',
            'Vendor coordination for ERP and tooling': 'Managing vendor relationships and updates for ERP systems, SCADA, and specialized manufacturing software.',
            'Monthly health reporting': 'Detailed monthly reports on system health, security posture, and recommended actions for continuous improvement.',
        },
        'seo_keywords': 'manufacturing IT support, production IT services, industrial cybersecurity, ERP support manufacturing, SCADA security, Orange County manufacturing IT',
        'seo_description': 'Managed IT services for manufacturers in Orange County. Minimize downtime, secure industrial systems, and maintain production continuity with proactive support.',
    },
    'retail-ecommerce': {
        'challenge_descriptions': {
            'POS outages during peak periods': 'Point-of-sale failures during high-traffic periods directly impact revenue and customer satisfaction.',
            'Store connectivity inconsistencies': 'Unreliable Wi-Fi and network connections across store locations create checkout delays and inventory sync issues.',
            'Payment endpoint risk': 'Payment terminals and card readers that lack security updates are prime targets for data theft and skimming attacks.',
            'Checkout device failures': 'Broken scanners, receipt printers, and card readers disrupt checkout flow and increase customer wait times.',
            'Multi-location visibility gaps': 'Without centralized monitoring, issues at one store location may go undetected for hours or days.',
        },
        'solution_descriptions': {
            'POS and network stabilization': 'Redundant network configurations and proactive POS monitoring to ensure uninterrupted checkout operations.',
            'Endpoint security controls': 'Hardened payment terminals and workstations with encryption, patching, and real-time threat detection.',
            'Store operations cloud workflows': 'Cloud-based inventory, scheduling, and reporting tools accessible from any store location securely.',
            'Vendor escalation management': 'Single point of contact for all technology vendor issues, from POS providers to payment processors.',
            'Backup and incident planning': 'Retail-specific disaster recovery and incident response plans to minimize downtime and data loss.',
        },
        'seo_keywords': 'retail IT support, eCommerce IT services, POS system support, retail cybersecurity, payment security, Orange County retail IT, store technology management',
        'seo_description': 'IT support for retail and eCommerce businesses in Orange County. POS system management, payment security, and multi-location technology support.',
    },
    'professional-services': {
        'challenge_descriptions': {
            'Tool sprawl and workflow friction': 'Too many disconnected tools slow productivity and create data silos that make collaboration difficult.',
            'Manual onboarding and permissions': 'Setting up new employees manually wastes IT hours and introduces security gaps from inconsistent permissions.',
            'Weak client-data safeguards': 'Client-facing firms handling sensitive financial or business data need stronger encryption and access controls.',
            'Slow systems reducing billable output': 'Laggy workstations and unreliable software directly reduce the hours professionals can bill to clients.',
            'Reactive support cycles': 'Waiting until something breaks to call IT creates unpredictable costs and extended downtime.',
        },
        'solution_descriptions': {
            'Cloud collaboration standardization': 'Unified cloud platforms for document sharing, communication, and project management to eliminate tool sprawl.',
            'Automated user lifecycle controls': 'Automated onboarding and offboarding with predefined role-based permissions for security and efficiency.',
            'Endpoint and account hardening': 'Advanced endpoint security and account protection including MFA, conditional access, and encryption.',
            'Proactive device support': 'Continuous monitoring and maintenance of workstations to prevent performance issues before they impact productivity.',
            'Workflow automation opportunities': 'Identify and implement automations for repetitive tasks like reporting, invoicing, and data entry.',
        },
        'seo_keywords': 'professional services IT, accounting firm IT support, consulting firm technology, agency IT services, business services IT, Orange County professional IT',
        'seo_description': 'Scalable IT support for professional services firms in Orange County. Cloud collaboration, automated onboarding, and proactive device management.',
    },
    'nonprofits': {
        'challenge_descriptions': {
            'Limited internal IT capacity': 'Most nonprofits lack dedicated IT staff, leaving technology decisions to people already stretched thin.',
            'Aging mixed devices': 'Donated and outdated devices running different operating systems create support headaches and security risks.',
            'Donor-data security risk': 'Donor information, payment details, and personal records require protection that many nonprofits are not equipped to provide.',
            'Volunteer access complexity': 'Granting temporary access to volunteers while maintaining security boundaries is operationally challenging.',
            'Backup uncertainty': 'Without verified backup processes, a hardware failure could mean losing years of organizational data.',
        },
        'solution_descriptions': {
            'Right-sized managed coverage': 'Managed IT services scaled to nonprofit budgets — no unnecessary features, just what your team actually needs.',
            'Secure cloud identity and collaboration': 'Cloud-based identity management and collaboration tools with nonprofit licensing discounts where available.',
            'Device standardization': 'Consistent device configurations and software deployments to reduce support complexity and improve security.',
            'Recovery readiness testing': 'Regular backup verification and recovery drills to ensure your data is always recoverable.',
            'Strategic IT planning': 'Technology roadmaps aligned with your mission and grant cycles to maximize impact per dollar spent.',
        },
        'seo_keywords': 'nonprofit IT support, NGO technology services, nonprofit cybersecurity, donor data protection, nonprofit cloud services, Orange County nonprofit IT',
        'seo_description': 'Mission-focused IT support for nonprofits in Orange County. Budget-conscious managed services, donor data protection, and strategic technology planning.',
    },
    'real-estate-property-management': {
        'challenge_descriptions': {
            'Mobile device issues for agents': 'Real estate agents depend on smartphones and tablets for showings, closings, and client communication — downtime costs deals.',
            'Fragmented file sharing': 'Contracts, disclosures, and inspection reports scattered across personal drives and email threads create version confusion.',
            'Transaction-time support delays': 'IT issues during a closing or contract signing can delay transactions and damage client relationships.',
            'Weak account security': 'Email account compromises in real estate are increasingly common, leading to wire fraud and data exposure.',
            'Onboarding/offboarding gaps': 'High agent turnover means credentials are frequently left active, creating unauthorized access risks.',
        },
        'solution_descriptions': {
            'Secure cloud document workflows': 'Centralized document management with version control, e-signatures, and secure sharing for transaction files.',
            'Mobile and office device management': 'Unified management of agent smartphones, tablets, and office workstations for consistent security and performance.',
            'Identity protection and phishing controls': 'Email security with advanced phishing protection to prevent wire fraud and business email compromise.',
            'Repeatable user lifecycle management': 'Standardized onboarding and offboarding checklists with automated account provisioning and deactivation.',
            'Priority troubleshooting support': 'Fast-track IT support prioritized for time-sensitive real estate transactions and deadlines.',
        },
        'seo_keywords': 'real estate IT support, property management technology, real estate cybersecurity, wire fraud prevention, property management IT, Orange County real estate IT',
        'seo_description': 'IT support for real estate and property management firms in Orange County. Mobile device management, wire fraud prevention, and transaction-ready technology.',
    },
}

def _normalize_industry_content(industry):
    hero_description = clean_text(getattr(industry, 'hero_description', '') or '', 1000)
    if not hero_description:
        hero_description = clean_text(getattr(industry, 'description', '') or '', 1000)

    challenges = clean_text(getattr(industry, 'challenges', '') or '', 2000)
    if not challenges:
        challenges = 'Downtime pressure|Security and compliance requirements|Scalability constraints'

    solutions = clean_text(getattr(industry, 'solutions', '') or '', 2000)
    if not solutions:
        solutions = 'Proactive monitoring and escalation|Security-first architecture and controls|Roadmap-based technology modernization'

    stats = clean_text(getattr(industry, 'stats', '') or '', 1000)
    if not stats:
        stats = 'Response SLA:24/7|Coverage:Orange County|Support Model:Onsite + Remote|Focus:Security + Uptime'

    return {
        'hero_description': hero_description,
        'challenges': challenges,
        'solutions': solutions,
        'stats': stats,
    }


def _build_home_hero_cards(cb, all_services):
    all_slugs = {service.slug for service in all_services}

    def detail_or_services(slug):
        if slug in all_slugs:
            return f'/services/{slug}'
        return '/services'

    allowed_colors = {'blue', 'purple', 'green', 'amber', 'cyan', 'rose'}

    raw_hero_cards = []
    if isinstance(cb.get('hero_cards'), dict):
        raw_hero_cards = cb.get('hero_cards', {}).get('items', []) or []

    hero_cards = []
    for card in raw_hero_cards:
        if not isinstance(card, dict):
            continue
        slug = clean_text(card.get('service_slug', ''), 120)
        if slug:
            href = detail_or_services(slug)
        else:
            href = '/services#repair'

        title = clean_text(card.get('title', ''), 120) or 'Service'
        subtitle = clean_text(card.get('subtitle', ''), 180) or 'Explore service details'
        color = clean_text(card.get('color', ''), 30)
        if color not in allowed_colors:
            color = 'blue'

        hero_cards.append(
            {
                'title': title,
                'subtitle': subtitle,
                'icon': normalize_icon_class(card.get('icon', ''), 'fa-solid fa-circle'),
                'color': color,
                'href': href,
                'aria_label': f'Open {title} service page',
            }
        )

    if hero_cards:
        return hero_cards

    return [
        {
            'title': 'Cloud',
            'subtitle': 'AWS, Azure, and GCP',
            'icon': 'fa-solid fa-cloud',
            'color': 'blue',
            'href': detail_or_services('cloud-solutions'),
            'aria_label': 'Open Cloud Solutions service page',
        },
        {
            'title': 'Cybersecurity',
            'subtitle': 'Threat Defense',
            'icon': 'fa-solid fa-lock',
            'color': 'purple',
            'href': detail_or_services('cybersecurity'),
            'aria_label': 'Open Cybersecurity service page',
        },
        {
            'title': 'Software & Web Development',
            'subtitle': 'Full-Stack Solutions',
            'icon': 'fa-solid fa-code',
            'color': 'green',
            'href': detail_or_services('software-development'),
            'aria_label': 'Open Software & Web Development service page',
        },
        {
            'title': 'Technical Repair',
            'subtitle': 'Certified Technicians',
            'icon': 'fa-solid fa-laptop-medical',
            'color': 'amber',
            'href': '/services#repair',
            'aria_label': 'Open Technical Repair services',
        },
        {
            'title': 'Managed IT Solutions',
            'subtitle': 'Proactive Support',
            'icon': 'fa-solid fa-network-wired',
            'color': 'cyan',
            'href': detail_or_services('managed-it-services'),
            'aria_label': 'Open Managed IT Solutions service page',
        },
        {
            'title': 'Enterprise Consultancy',
            'subtitle': 'Strategic Advisory',
            'icon': 'fa-solid fa-handshake',
            'color': 'rose',
            'href': detail_or_services('enterprise-consultancy'),
            'aria_label': 'Open Enterprise Consultancy service page',
        },
    ]


def index(request):
    ctx = _base_context()
    pro_services = normalize_icon_attr(
        _service_list(service_type='professional', is_featured=True),
        'fa-solid fa-gear',
    )
    if not pro_services:
        pro_services = normalize_icon_attr(
            _service_list(service_type='professional'),
            'fa-solid fa-gear',
        )

    repair_services = normalize_icon_attr(
        _service_list(service_type='repair', is_featured=True),
        'fa-solid fa-wrench',
    )
    if not repair_services:
        repair_services = normalize_icon_attr(
            _service_list(service_type='repair'),
            'fa-solid fa-wrench',
        )

    all_services = _service_list()

    testimonials = list(_active_queryset(Testimonial).filter(is_featured=True).order_by('id'))
    cb = get_page_content('home')

    # Normalize icon payloads coming from content blocks.
    trust = cb.get('trust_signals') if isinstance(cb.get('trust_signals'), dict) else {}
    trust_items = trust.get('items', []) if isinstance(trust, dict) else []
    if isinstance(trust_items, list):
        normalized_trust_items = []
        for item in trust_items:
            if isinstance(item, dict):
                label = clean_text(item.get('label', ''), 90)
                if not label:
                    continue
                item['icon'] = normalize_icon_class(item.get('icon', ''), 'fa-solid fa-circle-check')
                item['label'] = label
                normalized_trust_items.append(item)
        if normalized_trust_items:
            trust['items'] = normalized_trust_items[:10]
            cb['trust_signals'] = trust

    service_area = cb.get('service_area', {})
    if not isinstance(service_area, dict):
        service_area = {}
    service_area['cities'] = list(ORANGE_COUNTY_CA_CITIES)
    cb['service_area'] = service_area

    ctx.update(
        {
            'pro_services': pro_services,
            'repair_services': repair_services,
            'testimonials': testimonials,
            'hero_cards': _build_home_hero_cards(cb, all_services),
            'cb': cb,
        }
    )
    return render(request, 'index.html', ctx)


def about(request):
    ctx = _base_context()
    team = list(_active_queryset(TeamMember).order_by('sort_order', 'id'))
    ctx.update({'team': team, 'cb': get_page_content('about')})
    return render(request, 'about.html', ctx)


def services(request):
    ctx = _base_context()
    service_type = request.GET.get('type', '')
    pro_services = normalize_icon_attr(
        _service_list(service_type='professional'),
        'fa-solid fa-gear',
    )
    repair_services = normalize_icon_attr(
        _service_list(service_type='repair'),
        'fa-solid fa-wrench',
    )
    cb = get_page_content('services')
    if not isinstance(cb, dict):
        cb = {}
    ctx.update(
        {
            'pro_services': pro_services,
            'repair_services': repair_services,
            'active_type': service_type,
            'cb': cb,
        }
    )
    return render(request, 'services.html', ctx)


def services_it_track(request):
    return redirect('/services?type=professional', permanent=True)


def services_repair_track(request):
    return redirect('/services#repair', permanent=True)


def blog(request):
    ctx = _base_context()
    try:
        page = int(request.GET.get('page', 1) or 1)
    except (TypeError, ValueError):
        page = 1
    page = max(1, min(page, 1000))
    category_slug = clean_text(request.GET.get('category', ''), 120)
    search = clean_text(request.GET.get('q', ''), 120)

    query = _published_queryset(Post).select_related('category')

    if category_slug:
        cat = Category.objects.filter(slug=category_slug).first()
        if cat:
            query = query.filter(category_id=cat.id)

    if search:
        query = query.filter(title__icontains=search)

    paginator = Paginator(query.order_by('-created_at', '-id'), 6)
    page_obj = paginator.get_page(page)
    posts = PaginationAdapter(page_obj)
    categories = list(Category.objects.only('id', 'name', 'slug').order_by('name', 'id'))

    ctx.update({'posts': posts, 'categories': categories, 'current_category': category_slug, 'search': search})
    return render(request, 'blog.html', ctx)


def post(request, slug):
    post_obj = _published_queryset(Post).select_related('category').filter(slug=slug).first()
    if not post_obj:
        raise Http404

    recent_posts = list(
        _published_queryset(Post)
        .select_related('category')
        .exclude(id=post_obj.id)
        .order_by('-created_at', '-id')[:3]
    )

    ctx = _base_context()
    ctx.update({'post': post_obj, 'recent_posts': recent_posts})
    return render(request, 'post.html', ctx)


def industries(request):
    ctx = _base_context()
    all_industries = normalize_icon_attr(
        _industry_list(),
        'fa-solid fa-building',
    )
    cb = get_page_content('industries')
    if not isinstance(cb, dict):
        cb = {}
    expertise = cb.get('expertise', {})
    if isinstance(expertise, dict) and isinstance(expertise.get('items'), list):
        normalized_items = []
        for item in expertise.get('items', []):
            if not isinstance(item, dict):
                continue
            title = clean_text(item.get('title', ''), 90)
            desc = clean_text(item.get('description', ''), 220)
            if not title and not desc:
                continue
            normalized_items.append(
                {
                    'title': title or 'Industry expertise',
                    'description': desc or 'Operationally aligned delivery for your sector.',
                    'icon': normalize_icon_class(item.get('icon', ''), 'fa-solid fa-shield-halved'),
                }
            )
        if normalized_items:
            expertise['items'] = normalized_items[:8]
            cb['expertise'] = expertise
    ctx.update({'industries': all_industries, 'cb': cb})
    return render(request, 'industries.html', ctx)


def industry_detail(request, slug):
    industry = _industry_queryset(only_published=True).filter(slug=slug).first()
    if not industry:
        industry = _industry_queryset(only_published=False).filter(slug=slug).first()
    if industry is None and slug in INDUSTRY_SLUG_ALIASES:
        aliased = _industry_queryset(only_published=True).filter(slug=INDUSTRY_SLUG_ALIASES[slug]).first()
        if not aliased:
            aliased = _industry_queryset(only_published=False).filter(slug=INDUSTRY_SLUG_ALIASES[slug]).first()
        if aliased:
            return redirect('public:industry_detail', slug=INDUSTRY_SLUG_ALIASES[slug], permanent=True)
    if industry is None:
        raise Http404

    industry.icon_class = normalize_icon_class(industry.icon_class, 'fa-solid fa-building')
    normalized_industry = _normalize_industry_content(industry)
    industry.hero_description = normalized_industry['hero_description']
    industry.challenges = normalized_industry['challenges']
    industry.solutions = normalized_industry['solutions']
    industry.stats = normalized_industry['stats']

    services = normalize_icon_attr(
        _service_list(is_featured=True, limit=6),
        'fa-solid fa-gear',
    )
    if not services:
        services = normalize_icon_attr(
            _service_list(limit=6),
            'fa-solid fa-gear',
        )

    other_industries = normalize_icon_attr(
        [ind for ind in _industry_list() if ind.slug != slug],
        'fa-solid fa-building',
    )

    content_details = INDUSTRY_CONTENT_DETAILS.get(slug, {})

    ctx = _base_context()
    ctx.update({
        'slug': slug,
        'industry': industry,
        'services': services,
        'other_industries': other_industries,
        'challenge_descriptions': content_details.get('challenge_descriptions', {}),
        'solution_descriptions': content_details.get('solution_descriptions', {}),
        'seo_keywords': content_details.get('seo_keywords', ''),
        'seo_description': content_details.get('seo_description', ''),
    })
    return render(request, 'industry_detail.html', ctx)


def service_detail(request, slug):
    service = _service_queryset(only_published=True).filter(slug=slug).first()
    if not service:
        service = _service_queryset(only_published=False).filter(slug=slug).first()
    if service is None:
        service = _virtual_service_by_slug(slug)
    if service is None and slug in SERVICE_SLUG_ALIASES:
        aliased = _service_queryset(only_published=True).filter(slug=SERVICE_SLUG_ALIASES[slug]).first()
        if not aliased:
            aliased = _service_queryset(only_published=False).filter(slug=SERVICE_SLUG_ALIASES[slug]).first()
        if not aliased:
            aliased = _virtual_service_by_slug(SERVICE_SLUG_ALIASES[slug])
        if aliased:
            return redirect('public:service_detail', slug=SERVICE_SLUG_ALIASES[slug], permanent=True)
    if service is None:
        raise Http404

    service.icon_class = normalize_icon_class(service.icon_class, 'fa-solid fa-gear')
    service_profile = _normalize_service_profile(service)

    related_services_same_type = normalize_icon_attr(
        _service_list(service_type=service.service_type, exclude_id=service.id, limit=4),
        'fa-solid fa-gear',
    )
    related_services_other_type = normalize_icon_attr(
        _service_list(exclude_id=service.id, limit=8),
        'fa-solid fa-wrench',
    )
    related_ids = {item.id for item in related_services_same_type}
    related_services = list(related_services_same_type)
    for item in related_services_other_type:
        if item.id in related_ids or item.service_type == service.service_type:
            continue
        related_services.append(item)
        related_ids.add(item.id)
        if len(related_services) >= 6:
            break

    featured_industries = normalize_icon_attr(
        _industry_list(limit=6),
        'fa-solid fa-building',
    )

    related_posts = list(
        _published_queryset(Post)
        .select_related('category')
        .filter(title__icontains=service.title)
        .order_by('-created_at', '-id')[:3]
    )
    if len(related_posts) < 3:
        existing_ids = {p.id for p in related_posts}
        fallback_posts = list(_published_queryset(Post).select_related('category').order_by('-created_at', '-id')[:6])
        for item in fallback_posts:
            if item.id in existing_ids:
                continue
            related_posts.append(item)
            existing_ids.add(item.id)
            if len(related_posts) >= 3:
                break

    ctx = _base_context()
    ctx.update(
        {
            'slug': slug,
            'service': service,
            'service_profile': service_profile,
            'related_services': related_services,
            'featured_industries': featured_industries,
            'related_posts': related_posts,
        }
    )
    return render(request, 'service_detail.html', ctx)


def cms_page(request, slug):
    normalized_slug = re.sub(r'[^a-z0-9-]+', '-', str(slug or '').strip().lower()).strip('-')
    page = CmsPage.objects.filter(slug=normalized_slug, is_published=True).first()
    if not page:
        raise Http404
    return render(request, 'cms/page.html', {'slug': normalized_slug, 'page': page})


def cms_article(request, article_id):
    article = CmsArticle.objects.select_related('author').filter(id=article_id, is_published=True).first()
    if not article:
        raise Http404
    return render(request, 'cms/article.html', {'article_id': article_id, 'article': article})
