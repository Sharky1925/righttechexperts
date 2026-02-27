from __future__ import annotations

import re
from types import SimpleNamespace

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe

from core.constants import ORANGE_COUNTY_CA_CITIES, USER_ROLE_LABELS, WORKFLOW_PUBLISHED
from core.utils import get_page_content
from public.models import Industry, Service, SiteSetting

ICON_CLASS_RE = re.compile(r'^fa-(solid|regular|brands)\s+fa-[a-z0-9-]+$')
ICON_CLASS_ALIASES = {
    'fa-ranking-star': 'fa-chart-line',
    'fa-filter-circle-dollar': 'fa-bullseye',
    'fa-radar': 'fa-crosshairs',
    'fa-siren-on': 'fa-bell',
    'fa-shield-check': 'fa-shield-halved',
}
VALID_ICON_STYLES = {'fa-solid', 'fa-regular', 'fa-brands'}

DEFAULT_SITE_SETTINGS = {
    'company_name': 'Right On Repair',
    'tagline': 'Orange County managed IT, cybersecurity, cloud, software, web, and technical repair services',
    'phone': '+1 (562) 542-5899',
    'email': 'info@rightonrepair.com',
    'address': '9092 Talbert Ave. Ste 4, Fountain Valley, CA 92708',
    'facebook': 'https://facebook.com',
    'twitter': 'https://twitter.com',
    'linkedin': 'https://linkedin.com',
    'meta_title': 'Right On Repair — Orange County IT Services & Computer Repair',
    'meta_description': 'Orange County IT services and technical repair: managed IT, cybersecurity, cloud migration, software and web development, surveillance setup, and same-day device repair support for local businesses.',
    'theme_mode': 'light',
}

CONTEXT_CACHE_VERSION = str(getattr(settings, 'SITE_CONTEXT_CACHE_VERSION', 'v1'))
CONTEXT_CACHE_TTL = max(30, int(getattr(settings, 'SITE_CONTEXT_CACHE_TTL', 120)))


def normalize_icon_class(icon_class, fallback='fa-solid fa-circle'):
    fallback = fallback if ICON_CLASS_RE.match(fallback) else 'fa-solid fa-circle'
    raw = str(icon_class or '').strip()
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


def _public_base_url(request):
    configured = (getattr(settings, 'APP_BASE_URL', '') or '').strip().rstrip('/')
    if configured:
        return configured
    return f'{request.scheme}://{request.get_host()}'


def _context_cache_key(key):
    return f'site-context:{CONTEXT_CACHE_VERSION}:{key}'


def _get_site_settings():
    cache_key = _context_cache_key('site_settings')
    cached = cache.get(cache_key)
    if isinstance(cached, dict) and cached:
        return dict(cached)

    settings_dict = dict(DEFAULT_SITE_SETTINGS)
    try:
        rows = SiteSetting.objects.only('key', 'value')
        for row in rows:
            settings_dict[row.key] = row.value
    except Exception:
        pass
    cache.set(cache_key, settings_dict, CONTEXT_CACHE_TTL)
    return settings_dict


def _serialize_nav_items(items):
    return [
        {
            'id': item.id,
            'slug': item.slug,
            'title': item.title,
            'description': getattr(item, 'description', ''),
            'icon_class': getattr(item, 'icon_class', ''),
        }
        for item in items
    ]


def _deserialize_nav_items(items):
    return [SimpleNamespace(**item) for item in items if isinstance(item, dict)]


def _get_navigation_items():
    cache_key = _context_cache_key('navigation')
    cached = cache.get(cache_key)
    if isinstance(cached, dict):
        return (
            _deserialize_nav_items(cached.get('nav_professional', [])),
            _deserialize_nav_items(cached.get('nav_repair', [])),
            _deserialize_nav_items(cached.get('nav_industries', [])),
        )

    service_base = (
        Service.objects.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
        .only('id', 'slug', 'title', 'description', 'icon_class', 'service_type', 'workflow_status', 'sort_order')
        .order_by('sort_order', 'id')
    )
    industry_base = (
        Industry.objects.filter(Q(is_trashed=False) | Q(is_trashed__isnull=True))
        .only('id', 'slug', 'title', 'description', 'icon_class', 'workflow_status', 'sort_order')
        .order_by('sort_order', 'id')
    )

    nav_professional = list(
        service_base.filter(
            service_type='professional',
            workflow_status=WORKFLOW_PUBLISHED,
        )
    )
    nav_repair = list(
        service_base.filter(
            service_type='repair',
            workflow_status=WORKFLOW_PUBLISHED,
        )
    )
    nav_industries = list(
        industry_base.filter(workflow_status=WORKFLOW_PUBLISHED)
    )

    # Fallback for legacy rows missing published workflow state.
    if not nav_professional:
        nav_professional = list(service_base.filter(service_type='professional'))
    if not nav_repair:
        nav_repair = list(service_base.filter(service_type='repair'))
    if not nav_industries:
        nav_industries = list(industry_base)

    nav_professional = normalize_icon_attr(nav_professional, 'fa-solid fa-gear')
    if not any((item.slug == 'laptop-repair') for item in nav_repair):
        nav_repair.append(
            SimpleNamespace(
                id=-9001,
                slug='laptop-repair',
                title='Laptop Repair',
                description='Screen, battery, charging-port, and thermal repair workflows.',
                icon_class='fa-solid fa-laptop-medical',
            )
        )
    nav_repair = normalize_icon_attr(nav_repair, 'fa-solid fa-wrench')
    nav_industries = normalize_icon_attr(nav_industries, 'fa-solid fa-building')

    cache.set(
        cache_key,
        {
            'nav_professional': _serialize_nav_items(nav_professional),
            'nav_repair': _serialize_nav_items(nav_repair),
            'nav_industries': _serialize_nav_items(nav_industries),
        },
        CONTEXT_CACHE_TTL,
    )
    return nav_professional, nav_repair, nav_industries


def _get_footer_content():
    cache_key = _context_cache_key('footer_content')
    cached = cache.get(cache_key)
    if isinstance(cached, dict):
        return cached

    try:
        footer_content = get_page_content('footer')
    except Exception:
        footer_content = {}
    if not isinstance(footer_content, dict):
        footer_content = {}
    service_area = footer_content.get('service_area', {})
    if not isinstance(service_area, dict):
        service_area = {}
    service_area['cities'] = list(ORANGE_COUNTY_CA_CITIES)
    footer_content['service_area'] = service_area
    cache.set(cache_key, footer_content, CONTEXT_CACHE_TTL)
    return footer_content


def _set_request_compat_attrs(request):
    resolver = getattr(request, 'resolver_match', None)
    endpoint = ''
    if resolver and resolver.url_name:
        namespace = resolver.namespace or 'public'
        if namespace == 'public':
            endpoint = f'main.{resolver.url_name}'
        elif namespace == 'acp':
            endpoint = f'admin.acp_{resolver.url_name}'
        else:
            endpoint = f'{namespace}.{resolver.url_name}'

    request.endpoint = endpoint
    request.base_url = request.build_absolute_uri(request.path)
    request.url = request.build_absolute_uri()


def globals_context(request):
    _set_request_compat_attrs(request)
    settings_dict = _get_site_settings()

    try:
        nav_professional, nav_repair, nav_industries = _get_navigation_items()
    except Exception:
        nav_professional, nav_repair, nav_industries = [], [], []

    footer_content = _get_footer_content()

    def csrf_input_func():
        token = get_token(request)
        return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')

    theme_mode = (settings_dict.get('theme_mode') or 'light').strip().lower()
    if theme_mode not in {'dark', 'light'}:
        theme_mode = 'light'

    return {
        'site_settings': settings_dict,
        'csp_nonce': getattr(request, 'csp_nonce', ''),
        'asset_v': settings_dict.get('asset_version', ''),
        'public_base_url': _public_base_url(request),
        'current_user': request.user,
        'csrf_input': csrf_input_func,
        'nav_professional': nav_professional,
        'nav_repair': nav_repair,
        'nav_industries': nav_industries,
        'footer_content': footer_content,
        'theme_css_vars': {},
        'theme_mode': theme_mode,
        'orange_county_cities': list(ORANGE_COUNTY_CA_CITIES),
        'google_fonts_url': (settings_dict.get('google_fonts_url') or '').strip(),
        'turnstile_enabled': bool(
            (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip()
            and (getattr(settings, 'TURNSTILE_SECRET_KEY', '') or '').strip()
        ),
        'turnstile_site_key': (getattr(settings, 'TURNSTILE_SITE_KEY', '') or '').strip(),
    }


def admin_context(request):
    return {
        'current_user': request.user,
        'role_labels': USER_ROLE_LABELS,
    }
