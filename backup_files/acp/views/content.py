from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from acp.models import (
    AcpContentEntry,
    AcpContentEntryVersion,
    AcpContentType,
    AcpContentTypeVersion,
)
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


def _content_type_payload(item):
    return {
        'key': item.key,
        'name': item.name,
        'description': item.description or '',
        'schema_json': item.schema_json or '{}',
        'is_enabled': bool(item.is_enabled),
    }


def _content_entry_payload(item):
    return {
        'content_type_id': item.content_type_id,
        'entry_key': item.entry_key,
        'title': item.title,
        'locale': item.locale,
        'status': item.status,
        'data_json': item.data_json or '{}',
        'scheduled_publish_at': item.scheduled_publish_at.isoformat() if item.scheduled_publish_at else None,
        'published_at': item.published_at.isoformat() if item.published_at else None,
    }


def _create_content_type_version(item, user, change_note=''):
    try:
        latest = AcpContentTypeVersion.objects.filter(content_type_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        AcpContentTypeVersion.objects.create(
            content_type_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_content_type_payload(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _create_content_entry_version(item, user, change_note=''):
    try:
        latest = AcpContentEntryVersion.objects.filter(content_entry_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        AcpContentEntryVersion.objects.create(
            content_entry_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_content_entry_payload(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _save_content_type(request, item=None):
    target = item if item is not None else AcpContentType()
    name = clean_text(request.POST.get('name', ''), 180)
    key = clean_text(request.POST.get('key', ''), 120).lower().replace(' ', '_')
    description = request.POST.get('description', '')
    schema_json, schema_error = parse_json_text(request.POST.get('schema_json', '{}'), expect='dict')
    if schema_error:
        return None, target, f'Schema JSON error: {schema_error}'
    is_enabled = bool(request.POST.get('is_enabled'))
    if not name or not key:
        return None, target, 'Name and key are required.'

    try:
        query = AcpContentType.objects.filter(key=key)
        if getattr(target, 'id', None):
            query = query.exclude(id=target.id)
        if query.exists():
            return None, target, 'Key already exists.'
    except Exception:
        pass

    now = utc_now_naive()
    target.name = name
    target.key = key
    target.description = description
    target.schema_json = schema_json or '{}'
    target.is_enabled = is_enabled
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now

    try:
        target.save()
        _create_content_type_version(target, request.user, change_note=request.POST.get('change_note', ''))
        return target, target, ''
    except Exception:
        return None, target, 'Could not save content type.'


def _save_content_entry(request, item=None):
    target = item if item is not None else AcpContentEntry()
    content_type_id = safe_int(request.POST.get('content_type_id'), default=0, min_value=0)
    title = clean_text(request.POST.get('title', ''), 220)
    entry_key = clean_text(request.POST.get('entry_key', ''), 140)
    locale = clean_text(request.POST.get('locale', 'en-US'), 20) or 'en-US'
    status = normalize_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))
    data_json, data_error = parse_json_text(request.POST.get('data_json', '{}'), expect='dict')
    if data_error:
        return None, target, f'Data JSON error: {data_error}'

    if content_type_id <= 0 or not title or not entry_key:
        return None, target, 'Content type, title, and entry key are required.'

    try:
        content_type = AcpContentType.objects.filter(id=content_type_id).first()
    except Exception:
        content_type = None
    if not content_type:
        return None, target, 'Selected content type does not exist.'

    now = utc_now_naive()
    target.content_type_id = content_type_id
    target.title = title
    target.entry_key = entry_key
    target.locale = locale
    target.status = status
    target.data_json = data_json or '{}'
    target.scheduled_publish_at = scheduled_publish_at
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now
    maybe_mark_published(target, status, scheduled_publish_at)

    try:
        target.save()
        _create_content_entry_version(target, request.user, change_note=request.POST.get('change_note', ''))
        return target, target, ''
    except Exception:
        return None, target, 'Could not save content entry.'


@permission_required('acp:content:manage')
def content_types(request):
    q = clean_text(request.GET.get('q', ''), 120)
    try:
        query = AcpContentType.objects.order_by('-updated_at', '-id')
        if q:
            query = query.filter(Q(name__icontains=q) | Q(key__icontains=q))
        items = list(query[:200])
    except Exception:
        items = []
    return render(request, 'admin/acp/content_types.html', {'q': q, 'items': items})


@permission_required('acp:content:manage')
def content_type_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_content_type(request, item=None)
        if saved:
            write_audit(
                request,
                domain='content',
                action='create_type',
                entity_type='content_type',
                entity_id=saved.id,
                after_json=json.dumps(_content_type_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Content type created.')
            return redirect('acp:content_type_edit', id=saved.id)
        item = preview
        messages.error(request, error)
    return render(
        request,
        'admin/acp/content_type_form.html',
        {
            'item': item,
            'versions': versions,
        },
    )


@permission_required('acp:content:manage')
def content_type_edit(request, id):
    item = get_object_or_404(AcpContentType, id=id)
    if request.method == 'POST':
        before = json.dumps(_content_type_payload(item), ensure_ascii=False)
        saved, preview, error = _save_content_type(request, item=item)
        if saved:
            write_audit(
                request,
                domain='content',
                action='update_type',
                entity_type='content_type',
                entity_id=saved.id,
                before_json=before,
                after_json=json.dumps(_content_type_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Content type updated.')
            return redirect('acp:content_type_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    try:
        versions = list(AcpContentTypeVersion.objects.filter(content_type_id=item.id).order_by('-version_number', '-id')[:40])
    except Exception:
        versions = []
    return render(
        request,
        'admin/acp/content_type_form.html',
        {
            'item': item,
            'versions': versions,
        },
    )


@permission_required('acp:content:manage')
def content_entries(request):
    q = clean_text(request.GET.get('q', ''), 120)
    selected_content_type_id = safe_int(request.GET.get('content_type_id'), default=0, min_value=0)
    try:
        query = AcpContentEntry.objects.select_related('content_type').order_by('-updated_at', '-id')
        if q:
            query = query.filter(
                Q(title__icontains=q)
                | Q(entry_key__icontains=q)
                | Q(content_type__name__icontains=q)
                | Q(content_type__key__icontains=q)
            )
        if selected_content_type_id > 0:
            query = query.filter(content_type_id=selected_content_type_id)
        items = list(query[:300])
    except Exception:
        items = []
    try:
        content_types = list(AcpContentType.objects.order_by('name', 'id'))
    except Exception:
        content_types = []

    ctx = {
        'q': q,
        'items': items,
        'content_types': content_types,
        'selected_content_type_id': selected_content_type_id if selected_content_type_id > 0 else None,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/content_entries.html', ctx)


@permission_required('acp:content:manage')
def content_entry_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_content_entry(request, item=None)
        if saved:
            write_audit(
                request,
                domain='content',
                action='create_entry',
                entity_type='content_entry',
                entity_id=saved.id,
                after_json=json.dumps(_content_entry_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Content entry created.')
            return redirect('acp:content_entry_edit', id=saved.id)
        item = preview
        messages.error(request, error)
    else:
        preselected = safe_int(request.GET.get('content_type_id'), default=0, min_value=0)
        if preselected > 0:
            preview = AcpContentEntry()
            preview.content_type_id = preselected
            preview.locale = 'en-US'
            preview.status = WORKFLOW_DRAFT
            item = preview

    try:
        content_types = list(AcpContentType.objects.order_by('name', 'id'))
    except Exception:
        content_types = []
    ctx = {
        'item': item,
        'versions': versions,
        'content_types': content_types,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/content_entry_form.html', ctx)


@permission_required('acp:content:manage')
def content_entry_edit(request, id):
    item = get_object_or_404(AcpContentEntry, id=id)
    if request.method == 'POST':
        before = json.dumps(_content_entry_payload(item), ensure_ascii=False)
        saved, preview, error = _save_content_entry(request, item=item)
        if saved:
            write_audit(
                request,
                domain='content',
                action='update_entry',
                entity_type='content_entry',
                entity_id=saved.id,
                before_json=before,
                after_json=json.dumps(_content_entry_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Content entry updated.')
            return redirect('acp:content_entry_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    try:
        versions = list(AcpContentEntryVersion.objects.filter(content_entry_id=item.id).order_by('-version_number', '-id')[:40])
    except Exception:
        versions = []
    try:
        content_types = list(AcpContentType.objects.order_by('name', 'id'))
    except Exception:
        content_types = []
    ctx = {
        'item': item,
        'versions': versions,
        'content_types': content_types,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/content_entry_form.html', ctx)
