from __future__ import annotations

import json
from urllib.parse import unquote

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import URLPattern, URLResolver, get_resolver
from django.utils.text import slugify

from acp.models import AcpComponentDefinition, AcpPageDocument, AcpPageRouteBinding, AcpPageVersion
from acp.views.common import (
    maybe_mark_published,
    normalize_status,
    parse_datetime_local,
    parse_json_text,
    safe_int,
    workflow_context,
    write_audit,
)
from admin_panel.decorators import permission_required
from core.constants import WORKFLOW_DRAFT
from core.utils import clean_text, utc_now_naive


def _page_payload(item):
    return {
        'slug': item.slug,
        'title': item.title,
        'template_id': item.template_id,
        'locale': item.locale,
        'status': item.status,
        'seo_json': item.seo_json or '{}',
        'blocks_tree': item.blocks_tree or '{}',
        'theme_override_json': item.theme_override_json or '{}',
        'scheduled_publish_at': item.scheduled_publish_at.isoformat() if item.scheduled_publish_at else None,
        'published_at': item.published_at.isoformat() if item.published_at else None,
    }


def _create_page_version(item, user, change_note=''):
    try:
        latest = AcpPageVersion.objects.filter(page_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        AcpPageVersion.objects.create(
            page_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_page_payload(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _coerce_slug(value):
    raw = clean_text(value, 200).strip('/')
    if not raw:
        return ''
    if raw != slugify(raw):
        return slugify(raw)[:200]
    return raw[:200]


def _component_registry():
    try:
        rows = list(AcpComponentDefinition.objects.filter(is_enabled=True).order_by('category', 'name', 'id'))
    except Exception:
        return []

    registry = []
    for row in rows:
        try:
            prop_schema = json.loads(row.prop_schema_json or '{}')
        except (TypeError, ValueError):
            prop_schema = {}
        try:
            default_props = json.loads(row.default_props_json or '{}')
        except (TypeError, ValueError):
            default_props = {}
        registry.append(
            {
                'key': row.key,
                'name': row.name,
                'category': row.category,
                'prop_schema': prop_schema if isinstance(prop_schema, dict) else {},
                'default_props': default_props if isinstance(default_props, dict) else {},
            }
        )
    return registry


def _save_page(request, item=None):
    target = item if item is not None else AcpPageDocument()

    title = clean_text(request.POST.get('title', ''), 220)
    slug = _coerce_slug(request.POST.get('slug', ''))
    template_id = clean_text(request.POST.get('template_id', 'default-page'), 120) or 'default-page'
    locale = clean_text(request.POST.get('locale', 'en-US'), 20) or 'en-US'
    status = normalize_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))

    seo_json, seo_error = parse_json_text(request.POST.get('seo_json', '{}'), expect='dict')
    if seo_error:
        return None, target, f'SEO JSON error: {seo_error}'
    blocks_tree, blocks_error = parse_json_text(request.POST.get('blocks_tree', '{}'), expect='dict')
    if blocks_error:
        return None, target, f'Blocks Tree JSON error: {blocks_error}'
    theme_override_json, theme_error = parse_json_text(request.POST.get('theme_override_json', '{}'), expect='dict')
    if theme_error:
        return None, target, f'Theme Override JSON error: {theme_error}'

    if not title or not slug:
        return None, target, 'Title and slug are required.'

    try:
        query = AcpPageDocument.objects.filter(slug=slug)
        if getattr(target, 'id', None):
            query = query.exclude(id=target.id)
        if query.exists():
            return None, target, 'Slug already exists.'
    except Exception:
        pass

    now = utc_now_naive()
    target.title = title
    target.slug = slug
    target.template_id = template_id
    target.locale = locale
    target.status = status
    target.seo_json = seo_json or '{}'
    target.blocks_tree = blocks_tree or '{}'
    target.theme_override_json = theme_override_json or '{}'
    target.scheduled_publish_at = scheduled_publish_at
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now

    maybe_mark_published(target, status, scheduled_publish_at)

    try:
        target.save()
        _create_page_version(target, request.user, change_note=request.POST.get('change_note', ''))
        return target, target, ''
    except Exception:
        return None, target, 'Could not save page document.'


@permission_required('acp:pages:manage')
def pages(request):
    q = clean_text(request.GET.get('q', ''), 120)
    try:
        query = AcpPageDocument.objects.order_by('-updated_at', '-id')
        if q:
            query = query.filter(
                Q(title__icontains=q) | Q(slug__icontains=q) | Q(template_id__icontains=q)
            )
        items = list(query[:200])
    except Exception:
        items = []
    ctx = {
        'q': q,
        'items': items,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/pages.html', ctx)


@permission_required('acp:pages:manage')
def page_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_page(request, item=None)
        if saved:
            write_audit(
                request,
                domain='pages',
                action='create',
                entity_type='page',
                entity_id=saved.id,
                after_json=json.dumps(_page_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Page created.')
            return redirect('acp:page_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    component_registry = _component_registry()
    ctx = {
        'item': item,
        'versions': versions,
        'component_registry': component_registry,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/page_form.html', ctx)


@permission_required('acp:pages:manage')
def page_edit(request, id):
    item = get_object_or_404(AcpPageDocument, id=id)
    if request.method == 'POST':
        before = json.dumps(_page_payload(item), ensure_ascii=False)
        saved, preview, error = _save_page(request, item=item)
        if saved:
            write_audit(
                request,
                domain='pages',
                action='update',
                entity_type='page',
                entity_id=saved.id,
                before_json=before,
                after_json=json.dumps(_page_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Page updated.')
            return redirect('acp:page_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    try:
        versions = list(AcpPageVersion.objects.filter(page_id=item.id).order_by('-version_number', '-id')[:40])
    except Exception:
        versions = []
    component_registry = _component_registry()
    ctx = {
        'item': item,
        'versions': versions,
        'component_registry': component_registry,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/page_form.html', ctx)


@permission_required('acp:publish')
def page_publish(request, id):
    if request.method != 'POST':
        return redirect('acp:page_edit', id=id)
    item = get_object_or_404(AcpPageDocument, id=id)
    before = json.dumps(_page_payload(item), ensure_ascii=False)

    status = normalize_status(request.POST.get('workflow_status'))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))
    item.status = status
    item.scheduled_publish_at = scheduled_publish_at
    item.updated_by_id = getattr(request.user, 'id', None)
    item.updated_at = utc_now_naive()
    maybe_mark_published(item, status, scheduled_publish_at)
    try:
        item.save(update_fields=['status', 'scheduled_publish_at', 'published_at', 'updated_by_id', 'updated_at'])
        _create_page_version(item, request.user, change_note=request.POST.get('change_note', 'workflow update'))
        write_audit(
            request,
            domain='pages',
            action='workflow',
            entity_type='page',
            entity_id=item.id,
            before_json=before,
            after_json=json.dumps(_page_payload(item), ensure_ascii=False),
        )
        messages.success(request, 'Page workflow updated.')
    except Exception:
        messages.error(request, 'Could not update page workflow.')
    return redirect('acp:page_edit', id=id)


@permission_required('acp:pages:manage')
def page_snapshot(request, id):
    if request.method != 'POST':
        return redirect('acp:page_edit', id=id)
    item = get_object_or_404(AcpPageDocument, id=id)
    _create_page_version(item, request.user, change_note=request.POST.get('change_note', 'manual snapshot'))
    write_audit(
        request,
        domain='pages',
        action='snapshot',
        entity_type='page',
        entity_id=item.id,
        after_json=json.dumps(_page_payload(item), ensure_ascii=False),
    )
    messages.success(request, 'Snapshot created.')
    return redirect('acp:page_edit', id=id)


def _iter_patterns(patterns, prefix='', namespace=''):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            sub_prefix = f'{prefix}{pattern.pattern}'
            sub_namespace = namespace
            if pattern.namespace:
                sub_namespace = f'{namespace}:{pattern.namespace}' if namespace else pattern.namespace
            yield from _iter_patterns(pattern.url_patterns, prefix=sub_prefix, namespace=sub_namespace)
            continue
        if not isinstance(pattern, URLPattern):
            continue
        rule = f'/{prefix}{pattern.pattern}'.replace('//', '/')
        endpoint = pattern.name or ''
        if pattern.lookup_str:
            endpoint = endpoint or pattern.lookup_str
        yield {
            'rule': unquote(rule.rstrip('/') or '/'),
            'endpoint': endpoint[:180],
            'namespace': namespace,
        }


def _expected_slug_for_rule(rule):
    if '<' in rule and '>' in rule:
        return ''
    normalized = (rule or '/').strip('/')
    if not normalized:
        return 'home'
    if normalized in {'sitemap.xml', 'robots.txt'}:
        return ''
    if normalized.startswith('admin') or normalized.startswith('api'):
        return ''
    if '/' in normalized:
        return normalized.replace('/', '-')
    return normalized


def _sync_scan():
    try:
        routes = [
            row
            for row in _iter_patterns(get_resolver().url_patterns)
            if (row['namespace'] or '').split(':')[0] == 'public'
        ]
    except Exception:
        routes = []

    page_by_slug = {}
    try:
        page_by_slug = {item.slug: item for item in AcpPageDocument.objects.all()}
    except Exception:
        page_by_slug = {}

    rows = []
    for route in routes:
        rule = route['rule']
        expected_slug = _expected_slug_for_rule(rule)
        is_dynamic = '<' in rule and '>' in rule
        page = page_by_slug.get(expected_slug) if expected_slug else None

        sync_status = 'unmapped_route'
        issue = ''
        if expected_slug:
            if not page:
                sync_status = 'missing_page_document'
                issue = 'No page document found for route-derived slug.'
            elif page.status != 'published':
                sync_status = 'unpublished_page_document'
                issue = 'Page exists but is not published.'
            else:
                sync_status = 'synced'
        rows.append(
            {
                'rule': rule[:240],
                'endpoint': route['endpoint'],
                'expected_slug': expected_slug,
                'sync_status': sync_status,
                'issue': issue,
                'is_dynamic': is_dynamic,
                'page_id': getattr(page, 'id', None),
                'title': getattr(page, 'title', ''),
                'status': getattr(page, 'status', ''),
            }
        )

    orphan_pages = []
    seen_slugs = {row['expected_slug'] for row in rows if row['expected_slug']}
    for slug, page in page_by_slug.items():
        if slug not in seen_slugs:
            orphan_pages.append(
                {
                    'id': page.id,
                    'slug': page.slug,
                    'title': page.title,
                    'status': page.status,
                }
            )

    totals = {
        'routes_scanned': len(rows),
        'synced': len([r for r in rows if r['sync_status'] == 'synced']),
        'missing_page_document': len([r for r in rows if r['sync_status'] == 'missing_page_document']),
        'unpublished_page_document': len([r for r in rows if r['sync_status'] == 'unpublished_page_document']),
        'unmapped_route': len([r for r in rows if r['sync_status'] == 'unmapped_route']),
        'orphan_pages': len(orphan_pages),
        'orphan_bindings': 0,
        'auto_registered_pages': 0,
    }
    return {
        'generated_at': utc_now_naive(),
        'routes': rows,
        'orphan_pages': orphan_pages,
        'totals': totals,
    }


def _persist_sync(rows, *, auto_register=False, user=None):
    now = utc_now_naive()
    auto_registered = 0
    try:
        page_by_slug = {item.slug: item for item in AcpPageDocument.objects.all()}
    except Exception:
        page_by_slug = {}

    for row in rows:
        expected_slug = row.get('expected_slug') or ''
        page = page_by_slug.get(expected_slug)
        if auto_register and expected_slug and row.get('sync_status') == 'missing_page_document' and not page:
            try:
                page = AcpPageDocument.objects.create(
                    slug=expected_slug,
                    title=expected_slug.replace('-', ' ').title(),
                    template_id='default-page',
                    locale='en-US',
                    status='draft',
                    seo_json='{}',
                    blocks_tree='{"type":"layout.container","props":{},"children":[]}',
                    theme_override_json='{}',
                    created_by_id=getattr(user, 'id', None),
                    updated_by_id=getattr(user, 'id', None),
                    created_at=now,
                    updated_at=now,
                )
                _create_page_version(page, user, change_note='auto-register from route sync')
                page_by_slug[expected_slug] = page
                row['sync_status'] = 'unpublished_page_document'
                row['page_id'] = page.id
                auto_registered += 1
            except Exception:
                page = None

        try:
            binding = AcpPageRouteBinding.objects.filter(route_rule=row['rule']).first()
            if not binding:
                binding = AcpPageRouteBinding(route_rule=row['rule'])
                binding.created_at = now
            binding.endpoint = clean_text(row.get('endpoint', ''), 180)
            binding.methods_json = '["GET"]'
            binding.page_slug = expected_slug or ''
            binding.page_id = getattr(page, 'id', None)
            binding.sync_status = clean_text(row.get('sync_status', ''), 40) or 'unmapped_route'
            binding.issue_detail = clean_text(row.get('issue', ''), 320)
            binding.is_dynamic = bool(row.get('is_dynamic'))
            binding.is_active = True
            binding.last_seen_at = now
            binding.updated_at = now
            binding.save()
        except Exception:
            continue
    return auto_registered


@permission_required('acp:pages:manage')
def sync_status(request):
    report = _sync_scan()
    try:
        stored_bindings = list(AcpPageRouteBinding.objects.order_by('-updated_at', '-id')[:300])
        report['totals']['orphan_bindings'] = len(
            [b for b in stored_bindings if (b.sync_status or '').strip() == 'orphan_route_binding']
        )
    except Exception:
        stored_bindings = []
        report['totals']['orphan_bindings'] = 0
    ctx = {
        'report': report,
        'stored_bindings': stored_bindings,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/sync_status.html', ctx)


@permission_required('acp:pages:manage')
def sync_resync(request):
    if request.method != 'POST':
        return redirect('acp:sync_status')

    action = clean_text(request.POST.get('action', ''), 20).lower()
    report = _sync_scan()
    rows = report.get('routes', [])
    auto_register = action == 'autoregister'

    try:
        auto_registered = _persist_sync(rows, auto_register=auto_register, user=request.user)
        report['totals']['auto_registered_pages'] = safe_int(auto_registered, default=0, min_value=0)
        if action == 'scan':
            messages.success(request, f'Sync scan completed: {report["totals"]["routes_scanned"]} routes checked.')
        elif action == 'autoregister':
            messages.success(request, f'Auto-register completed. Added {auto_registered} page document(s).')
        else:
            messages.info(request, 'Sync request completed.')
    except Exception:
        messages.error(request, 'Could not run sync operation.')
    return redirect('acp:sync_status')
