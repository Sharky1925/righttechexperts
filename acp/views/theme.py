from __future__ import annotations

import json

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from acp.models import AcpThemeTokenSet, AcpThemeTokenVersion
from acp.views.common import (
    maybe_mark_published,
    normalize_status,
    parse_datetime_local,
    parse_json_text,
    workflow_context,
    write_audit,
)
from admin_panel.decorators import permission_required
from core.constants import WORKFLOW_DRAFT
from core.utils import clean_text, utc_now_naive


def _theme_payload(item):
    return {
        'key': item.key,
        'name': item.name,
        'status': item.status,
        'tokens_json': item.tokens_json or '{}',
        'scheduled_publish_at': item.scheduled_publish_at.isoformat() if item.scheduled_publish_at else None,
        'published_at': item.published_at.isoformat() if item.published_at else None,
    }


def _create_theme_version(item, user, change_note=''):
    try:
        latest = AcpThemeTokenVersion.objects.filter(token_set_id=item.id).order_by('-version_number').first()
        version_number = (latest.version_number if latest else 0) + 1
        AcpThemeTokenVersion.objects.create(
            token_set_id=item.id,
            version_number=version_number,
            snapshot_json=json.dumps(_theme_payload(item), ensure_ascii=False),
            change_note=clean_text(change_note, 260),
            created_by_id=getattr(user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _save_theme_tokens(request, item=None):
    target = item if item is not None else AcpThemeTokenSet()
    name = clean_text(request.POST.get('name', ''), 180)
    key = clean_text(request.POST.get('key', 'default'), 80).lower()
    status = normalize_status(request.POST.get('workflow_status', WORKFLOW_DRAFT))
    scheduled_publish_at = parse_datetime_local(request.POST.get('scheduled_publish_at'))
    tokens_json, tokens_error = parse_json_text(request.POST.get('tokens_json', '{}'), expect='dict')
    if tokens_error:
        return None, target, f'Tokens JSON error: {tokens_error}'

    if not name or not key:
        return None, target, 'Name and key are required.'

    try:
        query = AcpThemeTokenSet.objects.filter(key=key)
        if getattr(target, 'id', None):
            query = query.exclude(id=target.id)
        if query.exists():
            return None, target, 'Key already exists.'
    except Exception:
        pass

    now = utc_now_naive()
    target.name = name
    target.key = key
    target.status = status
    target.tokens_json = tokens_json or '{}'
    target.scheduled_publish_at = scheduled_publish_at
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now

    maybe_mark_published(target, status, scheduled_publish_at)

    try:
        target.save()
        _create_theme_version(target, request.user, change_note=request.POST.get('change_note', ''))
        return target, target, ''
    except Exception:
        return None, target, 'Could not save theme token set.'


@permission_required('acp:theme:manage')
def theme_tokens(request):
    q = clean_text(request.GET.get('q', ''), 120)
    try:
        query = AcpThemeTokenSet.objects.order_by('-updated_at', '-id')
        if q:
            query = query.filter(Q(name__icontains=q) | Q(key__icontains=q))
        items = list(query[:200])
    except Exception:
        items = []
    ctx = {
        'q': q,
        'items': items,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/theme_tokens.html', ctx)


@permission_required('acp:theme:manage')
def theme_token_add(request):
    item = None
    versions = []
    if request.method == 'POST':
        saved, preview, error = _save_theme_tokens(request, item=None)
        if saved:
            write_audit(
                request,
                domain='theme',
                action='create',
                entity_type='theme_token_set',
                entity_id=saved.id,
                after_json=json.dumps(_theme_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Theme token set created.')
            return redirect('acp:theme_token_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/theme_token_form.html', ctx)


@permission_required('acp:theme:manage')
def theme_token_edit(request, id):
    item = get_object_or_404(AcpThemeTokenSet, id=id)
    if request.method == 'POST':
        before = json.dumps(_theme_payload(item), ensure_ascii=False)
        saved, preview, error = _save_theme_tokens(request, item=item)
        if saved:
            write_audit(
                request,
                domain='theme',
                action='update',
                entity_type='theme_token_set',
                entity_id=saved.id,
                before_json=before,
                after_json=json.dumps(_theme_payload(saved), ensure_ascii=False),
            )
            messages.success(request, 'Theme token set updated.')
            return redirect('acp:theme_token_edit', id=saved.id)
        item = preview
        messages.error(request, error)

    try:
        versions = list(AcpThemeTokenVersion.objects.filter(token_set_id=item.id).order_by('-version_number', '-id')[:40])
    except Exception:
        versions = []
    ctx = {
        'item': item,
        'versions': versions,
    }
    ctx.update(workflow_context())
    return render(request, 'admin/acp/theme_token_form.html', ctx)
