from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.urls import NoReverseMatch, reverse
from django.utils.safestring import mark_safe
from jinja2 import Environment, pass_context

_ENDPOINT_MAP = {
    'main.index': 'public:index',
    'main.about': 'public:about',
    'main.services': 'public:services',
    'main.blog': 'public:blog',
    'main.contact': 'public:contact',
    'main.request_quote': 'public:request_quote',
    'main.request_quote_personal': 'public:request_quote_personal',
    'main.remote_support': 'public:remote_support',
    'main.industries': 'public:industries',
    'main.sitemap_xml': 'public:sitemap_xml',
    'main.robots_txt': 'public:robots_txt',
    'main.headless_export': 'headless:headless_export',
    'main.headless_sync_upsert': 'headless:headless_sync_upsert',
    'main.acp_delivery_page': 'headless:acp_delivery_page',
    'main.acp_delivery_dashboard': 'headless:acp_delivery_dashboard',
    'main.acp_delivery_theme': 'headless:acp_delivery_theme',
    'main.acp_delivery_content_entry': 'headless:acp_delivery_content_entry',
    'admin.dashboard': 'admin:dashboard',
    'admin.login': 'admin:login',
    'admin.logout': 'admin:logout',
    'admin.control_center': 'admin:control_center',
    'admin.uploaded_file': 'admin:uploaded_file',
}

_FALLBACK_ROUTE_MAP = {
    # ACP aliases while advanced ACP routes are progressively ported.
    'acp:content_entries': 'acp:content_types',
    'acp:content_entry_add': 'acp:content_types',
    'acp:content_entry_edit': 'acp:content_types',
    'acp:content_type_add': 'acp:content_types',
    'acp:content_type_edit': 'acp:content_types',
    'acp:dashboard_add': 'acp:dashboards',
    'acp:dashboard_edit': 'acp:dashboards',
    'acp:dashboard_preview': 'acp:dashboards',
    'acp:dashboard_publish': 'acp:dashboards',
    'acp:dashboard_snapshot': 'acp:dashboards',
    'acp:page_add': 'acp:pages',
    'acp:page_edit': 'acp:pages',
    'acp:page_publish': 'acp:pages',
    'acp:page_snapshot': 'acp:pages',
    'acp:sync_status': 'acp:pages',
    'acp:sync_resync': 'acp:pages',
    'acp:theme_token_add': 'acp:theme_tokens',
    'acp:theme_token_edit': 'acp:theme_tokens',
    'acp:mcp_operations': 'acp:mcp_servers',
    'acp:mcp_operation_create': 'acp:mcp_servers',
    'acp:mcp_operation_approve': 'acp:mcp_servers',
    'acp:mcp_operation_reject': 'acp:mcp_servers',
    'acp:mcp_operation_retry': 'acp:mcp_servers',
    'acp:mcp_operation_run': 'acp:mcp_servers',
    'acp:mcp_process_queue': 'acp:mcp_servers',
    'acp:mcp_server_add': 'acp:mcp_servers',
    'acp:mcp_server_edit': 'acp:mcp_servers',
    'acp:mcp_audit': 'acp:mcp_servers',
    'acp:metrics': 'acp:studio',
    'acp:audit': 'acp:studio',
    'acp:promote': 'acp:studio',
}


def _map_endpoint(endpoint: str) -> str:
    if endpoint in _ENDPOINT_MAP:
        return _ENDPOINT_MAP[endpoint]
    if endpoint.startswith('main.'):
        return endpoint.replace('main.', 'public:', 1)
    if endpoint.startswith('admin.acp_'):
        return endpoint.replace('admin.acp_', 'acp:', 1)
    if endpoint.startswith('admin.'):
        return endpoint.replace('admin.', 'admin:', 1)
    return endpoint.replace('.', ':', 1)


def url_for_adapter(endpoint: str, **kwargs: Any) -> str:
    if endpoint == 'static':
        return static(kwargs.get('filename', ''))

    django_name = _map_endpoint(endpoint)
    try:
        if kwargs:
            return reverse(django_name, kwargs=kwargs)
        return reverse(django_name)
    except NoReverseMatch:
        fallback_name = _FALLBACK_ROUTE_MAP.get(django_name)
        if fallback_name:
            try:
                return reverse(fallback_name)
            except NoReverseMatch:
                pass
        # Flask's url_for accepts extra kwargs as query params.
        try:
            base = reverse(django_name)
        except NoReverseMatch:
            return '#'

        if not kwargs:
            return base

        query = urlencode({k: v for k, v in kwargs.items() if v is not None}, doseq=True)
        if query:
            return f'{base}?{query}'
        return base


def _public_base_url(request) -> str:
    configured = (getattr(settings, 'APP_BASE_URL', '') or '').strip().rstrip('/')
    if configured:
        return configured
    return f'{request.scheme}://{request.get_host()}'


@pass_context
def public_url_func(context, path='') -> str:
    request = context.get('request')
    if request is None:
        return str(path or '')

    raw = str(path or '')
    if raw.startswith('http://') or raw.startswith('https://'):
        return raw

    base = _public_base_url(request)
    if not raw:
        return base
    if raw.startswith('/'):
        return f'{base}{raw}'
    return f'{base}/{raw}'


@pass_context
def csrf_input_func(context) -> str:
    request = context.get('request')
    if request is None:
        return ''
    token = get_token(request)
    return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')


@pass_context
def flash_adapter(context, with_categories: bool = False):
    request = context.get('request')
    if request is None:
        return []
    queued = [(m.tags or 'info', str(m)) for m in messages.get_messages(request)]
    if with_categories:
        return queued
    return [msg for _, msg in queued]


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            'url_for': url_for_adapter,
            'csrf_input': csrf_input_func,
            'get_flashed_messages': flash_adapter,
            'public_url': public_url_func,
        }
    )
    return env
