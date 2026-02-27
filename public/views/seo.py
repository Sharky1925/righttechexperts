from __future__ import annotations

from datetime import datetime
from xml.sax.saxutils import escape

from django.conf import settings
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from core.constants import WORKFLOW_PUBLISHED
from public.models import CmsArticle, CmsPage, Industry, Post, Service

STATIC_ROUTE_NAMES = (
    'public:index',
    'public:about',
    'public:services',
    'public:blog',
    'public:contact',
    'public:request_quote',
    'public:request_quote_personal',
    'public:remote_support',
    'public:ticket_search',
    'public:industries',
)

VIRTUAL_SERVICE_SLUGS = (
    'laptop-repair',
)


def _public_base_url(request):
    configured = (getattr(settings, 'APP_BASE_URL', '') or '').strip().rstrip('/')
    if configured:
        return configured
    return f'{request.scheme}://{request.get_host()}'


def _cache_ttl():
    return max(60, int(getattr(settings, 'SEO_CACHE_TTL', 900)))


def _cache_key(request, suffix):
    version = str(getattr(settings, 'SEO_CACHE_VERSION', 'v1'))
    return f'seo:{version}:{suffix}:{request.scheme}:{request.get_host()}'


def _join_url(base_url, path):
    normalized = path if str(path).startswith('/') else f'/{path}'
    return f'{base_url}{normalized}'


def _iso_lastmod(value):
    if not isinstance(value, datetime):
        return ''
    if timezone.is_aware(value):
        value = timezone.localtime(value, timezone.utc)
    return value.date().isoformat()


def _lastmod(updated_at, created_at):
    return _iso_lastmod(updated_at) or _iso_lastmod(created_at)


def _static_urls(base_url):
    urls = []
    for route_name in STATIC_ROUTE_NAMES:
        try:
            path = reverse(route_name)
        except Exception:
            continue
        urls.append((_join_url(base_url, path), ''))
    return urls


def _service_urls(base_url):
    rows = list(
        Service.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
        Q(is_trashed=False) | Q(is_trashed__isnull=True)
    ).only('slug', 'updated_at', 'created_at')
    )
    urls = [
        (
            _join_url(base_url, reverse('public:service_detail', kwargs={'slug': row.slug})),
            _lastmod(row.updated_at, row.created_at),
        )
        for row in rows
    ]
    existing_slugs = {row.slug for row in rows}
    for slug in VIRTUAL_SERVICE_SLUGS:
        if slug in existing_slugs:
            continue
        urls.append((_join_url(base_url, reverse('public:service_detail', kwargs={'slug': slug})), ''))
    return urls


def _industry_urls(base_url):
    rows = Industry.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
        Q(is_trashed=False) | Q(is_trashed__isnull=True)
    ).only('slug', 'updated_at', 'created_at')
    return [
        (
            _join_url(base_url, reverse('public:industry_detail', kwargs={'slug': row.slug})),
            _lastmod(row.updated_at, row.created_at),
        )
        for row in rows
    ]


def _post_urls(base_url):
    rows = Post.objects.filter(workflow_status=WORKFLOW_PUBLISHED).filter(
        Q(is_trashed=False) | Q(is_trashed__isnull=True)
    ).only('slug', 'updated_at', 'created_at')
    return [
        (
            _join_url(base_url, reverse('public:post', kwargs={'slug': row.slug})),
            _lastmod(row.updated_at, row.created_at),
        )
        for row in rows
    ]


def _cms_page_urls(base_url):
    rows = CmsPage.objects.filter(is_published=True).only('slug', 'updated_at', 'created_at')
    return [
        (
            _join_url(base_url, reverse('public:cms_page', kwargs={'slug': row.slug})),
            _lastmod(row.updated_at, row.created_at),
        )
        for row in rows
    ]


def _cms_article_urls(base_url):
    rows = CmsArticle.objects.filter(is_published=True).only('id', 'updated_at', 'created_at')
    return [
        (
            _join_url(base_url, reverse('public:cms_article', kwargs={'article_id': row.id})),
            _lastmod(row.updated_at, row.created_at),
        )
        for row in rows
    ]


def _build_sitemap_xml(urls):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for location, lastmod in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{escape(location)}</loc>')
        if lastmod:
            lines.append(f'    <lastmod>{escape(lastmod)}</lastmod>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines)


def sitemap_xml(request):
    cache_key = _cache_key(request, 'sitemap')
    cached_body = cache.get(cache_key)
    if isinstance(cached_body, str) and cached_body:
        response = HttpResponse(cached_body, content_type='application/xml; charset=utf-8')
        response['X-Content-Type-Options'] = 'nosniff'
        return response

    base_url = _public_base_url(request)
    urls = []
    urls.extend(_static_urls(base_url))
    urls.extend(_service_urls(base_url))
    urls.extend(_industry_urls(base_url))
    urls.extend(_post_urls(base_url))
    urls.extend(_cms_page_urls(base_url))
    urls.extend(_cms_article_urls(base_url))

    body = _build_sitemap_xml(urls)
    cache.set(cache_key, body, _cache_ttl())

    response = HttpResponse(body, content_type='application/xml; charset=utf-8')
    response['X-Content-Type-Options'] = 'nosniff'
    return response


def robots_txt(request):
    cache_key = _cache_key(request, 'robots')
    cached_body = cache.get(cache_key)
    if isinstance(cached_body, str) and cached_body:
        response = HttpResponse(cached_body, content_type='text/plain; charset=utf-8')
        response['X-Robots-Tag'] = 'noindex, nofollow' if getattr(settings, 'ROBOTS_DISALLOW_ALL', False) else 'all'
        return response

    disallow_all = bool(getattr(settings, 'ROBOTS_DISALLOW_ALL', False))
    base_url = _public_base_url(request)
    lines = ['User-agent: *']
    if disallow_all:
        lines.append('Disallow: /')
    else:
        lines.append('Allow: /')
        lines.append('Disallow: /admin/')
        lines.append('Disallow: /api/')
    lines.append(f'Sitemap: {base_url}/sitemap.xml')
    body = '\n'.join(lines) + '\n'

    cache.set(cache_key, body, _cache_ttl())
    response = HttpResponse(body, content_type='text/plain; charset=utf-8')
    response['X-Robots-Tag'] = 'noindex, nofollow' if disallow_all else 'all'
    return response
