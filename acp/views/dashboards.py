from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from acp.models import AcpDashboardDocument, AcpDashboardVersion, AcpWidgetDefinition
from acp.views.common import (
    load_json,
    maybe_mark_published,
    normalize_status,
    parse_datetime_local,
    parse_json_text,
    role_context,
    workflow_context,
    write_audit,
)
from admin_panel.decorators import permission_required
from core.constants import WORKFLOW_DRAFT
from core.utils import clean_text, utc_now_naive


def _dashboard_payload(item):
    return {
        'dashboard_id': item.dashboard_id,
        'title': item.title,
        'route': item.route,
        'layout_type': item.layout_type,
        'status': item.status,
        'layout_config_json': item.layout_config_json or '{}',
        'widgets_json': item.widgets_json or '[]',
        'global_filters_json': item.global_filters_json or '[]',
        'role_visibility_json': item.role_visibility_json or '{}',
        'scheduled_publish_at': item.scheduled_publish_at.isoformat() if item.scheduled_publish_at else None,
        'published_at': item.published_at.isoformat() if item.published_at else None,
    }


def _create_dashboard_version(item, user, change_note=''):
    try:
        latest = AcpDashboardVersion.objects.filter(dashboard_document_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        AcpDashboardVersion.objects.create(
            dashboard_document_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_dashboard_payload(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _save_dashboard(request, item=None):
    target = item if item is not None else AcpDashboardDocument()
    title = clean_text(request.POST.get('title', ''), 220)
    dashboard_id = clean_text(request.POST.get('dashboard_id', ''), 120)
    route = clean_text(request.POST.get('route', ''), 220)
    layout_type = clean_text(request.POST.get('layout_type', 'grid'), 24).lower()
    layout_type = layout_type if layout_type in {'grid', 'tree'} else 'grid'
    status = normalize_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))

    layout_config_json, layout_error = parse_json_text(request.POST.get('layout_config_json', '{}'), expect='dict')
    if layout_error:
        return None, target, f'Layout config error: {layout_error}'
    widgets_json, widgets_error = parse_json_text(request.POST.get('widgets_json', '[]'), expect='list')
    if widgets_error:
        return None, target, f'Widgets JSON error: {widgets_error}'
    filters_json, filters_error = parse_json_text(request.POST.get('global_filters_json', '[]'), expect='list')
    if filters_error:
        return None, target, f'Global filters JSON error: {filters_error}'
    role_visibility_json, role_error = parse_json_text(request.POST.get('role_visibility_json', '{}'), expect='dict')
    if role_error:
        return None, target, f'Role visibility JSON error: {role_error}'

    if not title or not dashboard_id or not route:
        return None, target, 'Title, dashboard ID, and route are required.'

    try:
        id_query = AcpDashboardDocument.objects.filter(dashboard_id=dashboard_id)
        route_query = AcpDashboardDocument.objects.filter(route=route)
        if getattr(target, 'id', None):
            id_query = id_query.exclude(id=target.id)
            route_query = route_query.exclude(id=target.id)
        if id_query.exists():
            return None, target, 'Dashboard ID already exists.'
        if route_query.exists():
            return None, target, 'Route already exists.'
    except Exception:
        pass

    now = utc_now_naive()
    target.title = title
    target.dashboard_id = dashboard_id
    target.route = route
    target.layout_type = layout_type
    target.status = status
    target.layout_config_json = layout_config_json or '{}'
    target.widgets_json = widgets_json or '[]'
    target.global_filters_json = filters_json or '[]'
    target.role_visibility_json = role_visibility_json or '{}'
    target.scheduled_publish_at = scheduled_publish_at
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now

    maybe_mark_published(target, status, scheduled_publish_at)

    try:
        target.save()
        _create_dashboard_version(target, request.user, change_note=request.POST.get('change_note', ''))
        return target, target, ''
    except Exception:
        return None, target, 'Could not save dashboard document.'


def _visible_widgets_for_role(item, role):
    widgets = load_json(item.widgets_json, [])
    role_visibility = load_json(item.role_visibility_json, {})
    role_rule = role_visibility.get(role, {})
    hidden_ids = set()
    allowed_ids = set()

    if isinstance(role_rule, dict):
        hidden_ids = {str(x).strip() for x in role_rule.get('hiddenWidgets', []) if str(x).strip()}
        allowed_ids = {str(x).strip() for x in role_rule.get('allowedWidgets', []) if str(x).strip()}
        show_all = bool(role_rule.get('showAll'))
    else:
        show_all = False

    visible = []
    for widget in widgets:
        widget_id = str(widget.get('id', '')).strip()
        if widget_id in hidden_ids:
            continue
        if allowed_ids and widget_id and widget_id not in allowed_ids and not show_all:
            continue
        visible.append(widget)
    return visible, max(0, len(widgets) - len(visible)), role_rule


def _widget_registry():
    try:
        rows = list(AcpWidgetDefinition.objects.filter(is_enabled=True).order_by('category', 'name', 'id'))
    except Exception:
        return []

    registry = []
    for row in rows:
        try:
            config_schema = json.loads(row.config_schema_json or '{}')
        except (TypeError, ValueError):
            config_schema = {}
        registry.append(
            {
                'key': row.key,
                'name': row.name,
                'category': row.category,
                'config_schema': config_schema if isinstance(config_schema, dict) else {},
            }
        )
    return registry


@permission_required('acp:dashboards:manage')
def dashboards(request):
    q = clean_text(request.GET.get('q', ''), 120)
    try:
        query = AcpDashboardDocument.objects.order_by('-updated_at', '-id')
        if q:
            query = query.filter(
                Q(title__icontains=q) | Q(dashboard_id__icontains=q) | Q(route__icontains=q)
            )
        items = list(query[:200])
    except Exception:
        items = []

    ctx = {
        'q': q,
        'items': items,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/dashboards.html', ctx)


@permission_required('acp:dashboards:manage')
def dashboard_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_dashboard(request, item=None)
        if saved:
            write_audit(
                request,
                domain='dashboards',
                action='create',
                entity_type='dashboard',
                entity_id=saved.id,
                after_json=json.dumps(_dashboard_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Dashboard created.')
            return redirect('acp:dashboard_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    widget_registry = _widget_registry()

    ctx = {
        'item': item,
        'versions': versions,
        'widget_registry': widget_registry,
    }
    ctx.update(workflow_context())
    ctx.update(role_context())
    return render(request, 'admin/acp/dashboard_form.html', ctx)


@permission_required('acp:dashboards:manage')
def dashboard_edit(request, id):
    item = get_object_or_404(AcpDashboardDocument, id=id)
    if request.method == 'POST':
        before = json.dumps(_dashboard_payload(item), ensure_ascii=False)
        saved, preview, error = _save_dashboard(request, item=item)
        if saved:
            write_audit(
                request,
                domain='dashboards',
                action='update',
                entity_type='dashboard',
                entity_id=saved.id,
                before_json=before,
                after_json=json.dumps(_dashboard_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Dashboard updated.')
            return redirect('acp:dashboard_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    try:
        versions = list(AcpDashboardVersion.objects.filter(dashboard_document_id=item.id).order_by('-version_number', '-id')[:40])
    except Exception:
        versions = []
    widget_registry = _widget_registry()

    ctx = {
        'item': item,
        'versions': versions,
        'widget_registry': widget_registry,
    }
    ctx.update(workflow_context())
    ctx.update(role_context())
    return render(request, 'admin/acp/dashboard_form.html', ctx)


@permission_required('acp:dashboards:manage')
def dashboard_preview(request, id):
    item = get_object_or_404(AcpDashboardDocument, id=id)
    role = clean_text(request.GET.get('role', ''), 30).lower() or clean_text(getattr(request.user, 'role_key', 'admin'), 30)
    if role not in role_context()['role_options']:
        role = clean_text(getattr(request.user, 'role_key', 'admin'), 30)
    visible_widgets, hidden_count, role_rule = _visible_widgets_for_role(item, role)
    ctx = {
        'item': item,
        'role': role,
        'visible_widgets': visible_widgets,
        'hidden_count': hidden_count,
        'role_rule': role_rule if isinstance(role_rule, dict) else {},
        'global_filters': load_json(item.global_filters_json, []),
        'layout_config': load_json(item.layout_config_json, {}),
    }
    ctx.update(role_context())
    return render(request, 'admin/acp/dashboard_preview.html', ctx)


@permission_required('acp:publish')
def dashboard_publish(request, id):
    if request.method != 'POST':
        return redirect('acp:dashboard_edit', id=id)
    item = get_object_or_404(AcpDashboardDocument, id=id)
    before = json.dumps(_dashboard_payload(item), ensure_ascii=False)

    status = normalize_status(request.POST.get('workflow_status', item.status))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))
    item.status = status
    item.scheduled_publish_at = scheduled_publish_at
    item.updated_by_id = getattr(request.user, 'id', None)
    item.updated_at = utc_now_naive()
    maybe_mark_published(item, status, scheduled_publish_at)
    try:
        item.save(update_fields=['status', 'scheduled_publish_at', 'published_at', 'updated_by_id', 'updated_at'])
        _create_dashboard_version(item, request.user, change_note=request.POST.get('change_note', 'workflow update'))
        write_audit(
            request,
            domain='dashboards',
            action='workflow',
            entity_type='dashboard',
            entity_id=item.id,
            before_json=before,
            after_json=json.dumps(_dashboard_payload(item), ensure_ascii=False),
        )
        messages.success(request, 'Dashboard workflow updated.')
    except Exception:
        messages.error(request, 'Could not update dashboard workflow.')
    return redirect('acp:dashboard_edit', id=id)


@permission_required('acp:dashboards:manage')
def dashboard_snapshot(request, id):
    if request.method != 'POST':
        return redirect('acp:dashboard_edit', id=id)
    item = get_object_or_404(AcpDashboardDocument, id=id)
    _create_dashboard_version(item, request.user, change_note=request.POST.get('change_note', 'manual snapshot'))
    write_audit(
        request,
        domain='dashboards',
        action='snapshot',
        entity_type='dashboard',
        entity_id=item.id,
        after_json=json.dumps(_dashboard_payload(item), ensure_ascii=False),
    )
    messages.success(request, 'Snapshot created.')
    return redirect('acp:dashboard_edit', id=id)
