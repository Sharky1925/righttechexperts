from __future__ import annotations

import json
from datetime import timedelta
from uuid import uuid4

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from acp.models import AcpMcpAuditEvent, AcpMcpOperation, AcpMcpServer
from acp.views.common import load_json, parse_json_text, safe_int
from admin_panel.decorators import permission_required
from core.constants import (
    MCP_APPROVAL_STATUS_APPROVED,
    MCP_APPROVAL_STATUS_NOT_REQUIRED,
    MCP_APPROVAL_STATUS_PENDING,
    MCP_APPROVAL_STATUS_REJECTED,
    MCP_OPERATION_STATUSES,
    MCP_OPERATION_STATUS_BLOCKED,
    MCP_OPERATION_STATUS_FAILED,
    MCP_OPERATION_STATUS_PENDING_APPROVAL,
    MCP_OPERATION_STATUS_QUEUED,
    MCP_OPERATION_STATUS_REJECTED,
    MCP_OPERATION_STATUS_RUNNING,
    MCP_OPERATION_STATUS_SUCCEEDED,
)
from core.utils import clean_text, utc_now_naive


def _parse_allowed_tools(raw):
    data = load_json(raw, [])
    return [str(item).strip() for item in data if str(item).strip()]


def _requires_approval(server, tool_name):
    mode = clean_text(server.require_approval, 24).lower() or 'always'
    if mode == 'never':
        return False
    if mode == 'always':
        return True
    allowed = _parse_allowed_tools(server.allowed_tools_json)
    return bool(allowed and tool_name not in allowed)


def _write_mcp_audit(
    request,
    *,
    server_id=None,
    action='',
    tool_name='',
    status='ok',
    request_json='',
    response_json='',
):
    try:
        AcpMcpAuditEvent.objects.create(
            server_id=server_id,
            action=clean_text(action, 40),
            tool_name=clean_text(tool_name, 160),
            status=clean_text(status, 30) or 'ok',
            request_json=request_json or '',
            response_json=response_json or '',
            actor_user_id=getattr(request.user, 'id', None),
            created_at=utc_now_naive(),
        )
    except Exception:
        return


def _execute_operation(request, op):
    now = utc_now_naive()
    op.attempt_count = safe_int(op.attempt_count, default=0, min_value=0) + 1
    op.last_attempt_at = now
    op.updated_at = now

    request_payload = {
        'request_id': op.request_id,
        'tool_name': op.tool_name,
        'arguments': load_json(op.arguments_json, {}),
        'attempt': op.attempt_count,
    }

    if not op.server_id:
        op.status = MCP_OPERATION_STATUS_FAILED
        op.error_message = 'MCP server not found.'
    elif not getattr(op.server, 'is_enabled', False):
        op.status = MCP_OPERATION_STATUS_BLOCKED
        op.error_message = 'MCP server is disabled.'
    elif op.attempt_count > safe_int(op.max_attempts, default=3, min_value=1):
        op.status = MCP_OPERATION_STATUS_FAILED
        op.error_message = 'Max attempts reached.'
    else:
        op.status = MCP_OPERATION_STATUS_RUNNING
        op.error_message = ''
        op.save(update_fields=['status', 'attempt_count', 'last_attempt_at', 'updated_at', 'error_message'])

        response_payload = {
            'ok': True,
            'mode': 'simulated',
            'server_id': op.server_id,
            'tool_name': op.tool_name,
            'result': {
                'message': 'Operation simulated successfully.',
                'request_id': op.request_id,
            },
        }
        op.status = MCP_OPERATION_STATUS_SUCCEEDED
        op.response_json = json.dumps(response_payload, ensure_ascii=False)
        op.error_message = ''
        op.updated_at = utc_now_naive()
        op.save(update_fields=['status', 'response_json', 'error_message', 'updated_at'])
        _write_mcp_audit(
            request,
            server_id=op.server_id,
            action='execute',
            tool_name=op.tool_name,
            status='ok',
            request_json=json.dumps(request_payload, ensure_ascii=False),
            response_json=op.response_json or '',
        )
        return True

    op.save(update_fields=['status', 'attempt_count', 'last_attempt_at', 'updated_at', 'error_message'])
    _write_mcp_audit(
        request,
        server_id=op.server_id,
        action='execute',
        tool_name=op.tool_name,
        status='error',
        request_json=json.dumps(request_payload, ensure_ascii=False),
        response_json=json.dumps({'error': op.error_message or op.status}, ensure_ascii=False),
    )
    return False


@permission_required('acp:mcp:manage')
def mcp_servers(request):
    q = clean_text(request.GET.get('q', ''), 140)
    try:
        query = AcpMcpServer.objects.order_by('-updated_at', '-id')
        if q:
            query = query.filter(
                Q(name__icontains=q) | Q(key__icontains=q) | Q(server_url__icontains=q)
            )
        items = list(query[:200])
    except Exception:
        items = []
    return render(request, 'admin/acp/mcp_servers.html', {'q': q, 'items': items})


def _save_server(request, item=None):
    target = item if item is not None else AcpMcpServer()
    name = clean_text(request.POST.get('name', ''), 180)
    key = clean_text(request.POST.get('key', ''), 120)
    server_url = clean_text(request.POST.get('server_url', ''), 500)
    transport = clean_text(request.POST.get('transport', 'http'), 40) or 'http'
    auth_mode = clean_text(request.POST.get('auth_mode', 'oauth'), 40) or 'oauth'
    environment = clean_text(request.POST.get('environment', 'production'), 40) or 'production'
    require_approval = clean_text(request.POST.get('require_approval', 'always'), 24).lower()
    require_approval = require_approval if require_approval in {'always', 'selective', 'never'} else 'always'
    is_enabled = bool(request.POST.get('is_enabled'))
    notes = clean_text(request.POST.get('notes', ''), 400)

    allowed_tools_json, allowed_error = parse_json_text(request.POST.get('allowed_tools_json', '[]'), expect='list')
    if allowed_error:
        return None, target, f'Allowed tools JSON error: {allowed_error}'
    if not name or not key or not server_url:
        return None, target, 'Name, key, and server URL are required.'
    try:
        query = AcpMcpServer.objects.filter(key=key)
        if getattr(target, 'id', None):
            query = query.exclude(id=target.id)
        if query.exists():
            return None, target, 'Server key already exists.'
    except Exception:
        pass

    now = utc_now_naive()
    target.name = name
    target.key = key
    target.server_url = server_url
    target.transport = transport
    target.auth_mode = auth_mode
    target.environment = environment
    target.require_approval = require_approval
    target.allowed_tools_json = allowed_tools_json or '[]'
    target.is_enabled = is_enabled
    target.notes = notes
    target.updated_by_id = getattr(request.user, 'id', None)
    target.updated_at = now
    if not getattr(target, 'id', None):
        target.created_by_id = getattr(request.user, 'id', None)
        target.created_at = now

    try:
        target.save()
        return target, target, ''
    except Exception:
        return None, target, 'Could not save MCP server.'


@permission_required('acp:mcp:manage')
def mcp_server_add(request):
    item = None
    if request.method == 'POST':
        saved, preview, error = _save_server(request, item=None)
        if saved:
            _write_mcp_audit(request, server_id=saved.id, action='server_create', status='ok')
            messages.success(request, 'MCP server created.')
            return redirect('acp:mcp_server_edit', id=saved.id)
        item = preview
        messages.error(request, error)
    return render(request, 'admin/acp/mcp_server_form.html', {'item': item})


@permission_required('acp:mcp:manage')
def mcp_server_edit(request, id):
    item = get_object_or_404(AcpMcpServer, id=id)
    if request.method == 'POST':
        saved, preview, error = _save_server(request, item=item)
        if saved:
            _write_mcp_audit(request, server_id=saved.id, action='server_update', status='ok')
            messages.success(request, 'MCP server updated.')
            return redirect('acp:mcp_server_edit', id=saved.id)
        item = preview
        messages.error(request, error)
    return render(request, 'admin/acp/mcp_server_form.html', {'item': item})


@permission_required('acp:mcp:manage')
def mcp_operations(request):
    selected_server_id = safe_int(request.GET.get('server_id'), default=0, min_value=0)
    status = clean_text(request.GET.get('status', ''), 32)
    tool_name = clean_text(request.GET.get('tool_name', ''), 160)
    try:
        servers = list(AcpMcpServer.objects.order_by('name', 'id'))
    except Exception:
        servers = []

    try:
        query = AcpMcpOperation.objects.select_related('server').order_by('-created_at', '-id')
        if selected_server_id > 0:
            query = query.filter(server_id=selected_server_id)
        if status:
            query = query.filter(status=status)
        if tool_name:
            query = query.filter(tool_name__icontains=tool_name)
        items = list(query[:200])
    except Exception:
        items = []

    now = utc_now_naive()
    day_ago = now - timedelta(hours=24)
    try:
        summary = {
            'pending_approval': AcpMcpOperation.objects.filter(status=MCP_OPERATION_STATUS_PENDING_APPROVAL).count(),
            'queued': AcpMcpOperation.objects.filter(status=MCP_OPERATION_STATUS_QUEUED).count(),
            'running': AcpMcpOperation.objects.filter(status=MCP_OPERATION_STATUS_RUNNING).count(),
            'failed': AcpMcpOperation.objects.filter(status=MCP_OPERATION_STATUS_FAILED).count(),
            'succeeded_24h': AcpMcpOperation.objects.filter(
                status=MCP_OPERATION_STATUS_SUCCEEDED,
            ).filter(
                Q(updated_at__gte=day_ago) | Q(created_at__gte=day_ago)
            ).count(),
        }
    except Exception:
        summary = {'pending_approval': 0, 'queued': 0, 'running': 0, 'failed': 0, 'succeeded_24h': 0}

    return render(
        request,
        'admin/acp/mcp_operations.html',
        {
            'summary': summary,
            'servers': servers,
            'selected_server_id': selected_server_id if selected_server_id > 0 else None,
            'status': status,
            'tool_name': tool_name,
            'status_options': MCP_OPERATION_STATUSES,
            'items': items,
        },
    )


@permission_required('acp:mcp:manage')
def mcp_operation_create(request):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    server_id = safe_int(request.POST.get('server_id'), default=0, min_value=0)
    tool_name = clean_text(request.POST.get('tool_name', ''), 160)
    max_attempts = safe_int(request.POST.get('max_attempts'), default=3, min_value=1, max_value=6)
    execute_now = bool(request.POST.get('execute_now'))
    args_json, args_error = parse_json_text(request.POST.get('arguments_json', '{}'), expect='dict')
    if args_error:
        messages.error(request, f'Arguments JSON error: {args_error}')
        return redirect('acp:mcp_operations')

    if server_id <= 0 or not tool_name:
        messages.error(request, 'Server and tool name are required.')
        return redirect('acp:mcp_operations')

    server = AcpMcpServer.objects.filter(id=server_id).first()
    if not server:
        messages.error(request, 'Selected MCP server does not exist.')
        return redirect('acp:mcp_operations')

    requires_approval = _requires_approval(server, tool_name)
    status = MCP_OPERATION_STATUS_PENDING_APPROVAL if requires_approval else MCP_OPERATION_STATUS_QUEUED
    approval_status = MCP_APPROVAL_STATUS_PENDING if requires_approval else MCP_APPROVAL_STATUS_NOT_REQUIRED
    now = utc_now_naive()

    try:
        op = AcpMcpOperation.objects.create(
            server_id=server_id,
            request_id=str(uuid4()),
            tool_name=tool_name,
            arguments_json=args_json or '{}',
            response_json='',
            status=status,
            approval_status=approval_status,
            requires_approval=requires_approval,
            attempt_count=0,
            max_attempts=max_attempts,
            error_message='',
            requested_by_id=getattr(request.user, 'id', None),
            created_at=now,
            updated_at=now,
        )
        _write_mcp_audit(
            request,
            server_id=server_id,
            action='operation_create',
            tool_name=tool_name,
            status='ok',
            request_json=args_json or '{}',
        )
        if execute_now and op.status == MCP_OPERATION_STATUS_QUEUED:
            _execute_operation(request, op)
        messages.success(request, 'MCP operation created.')
    except Exception:
        messages.error(request, 'Could not create MCP operation.')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:manage')
def mcp_operation_approve(request, id):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    op = get_object_or_404(AcpMcpOperation, id=id)
    if op.status != MCP_OPERATION_STATUS_PENDING_APPROVAL:
        messages.error(request, 'Only pending approval operations can be approved.')
        return redirect('acp:mcp_operations')
    now = utc_now_naive()
    op.approval_status = MCP_APPROVAL_STATUS_APPROVED
    op.approved_by_id = getattr(request.user, 'id', None)
    op.approved_at = now
    op.status = MCP_OPERATION_STATUS_QUEUED
    op.updated_at = now
    op.save(update_fields=['approval_status', 'approved_by_id', 'approved_at', 'status', 'updated_at'])
    _write_mcp_audit(request, server_id=op.server_id, action='operation_approve', tool_name=op.tool_name, status='ok')
    if request.POST.get('execute_now'):
        _execute_operation(request, op)
    messages.success(request, 'Operation approved.')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:manage')
def mcp_operation_reject(request, id):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    op = get_object_or_404(AcpMcpOperation, id=id)
    now = utc_now_naive()
    op.approval_status = MCP_APPROVAL_STATUS_REJECTED
    op.status = MCP_OPERATION_STATUS_REJECTED
    op.updated_at = now
    op.error_message = clean_text(request.POST.get('reason', 'Rejected by reviewer.'), 800) or 'Rejected by reviewer.'
    op.save(update_fields=['approval_status', 'status', 'updated_at', 'error_message'])
    _write_mcp_audit(request, server_id=op.server_id, action='operation_reject', tool_name=op.tool_name, status='blocked')
    messages.success(request, 'Operation rejected.')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:manage')
def mcp_operation_retry(request, id):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    op = get_object_or_404(AcpMcpOperation, id=id)
    now = utc_now_naive()
    if op.requires_approval and op.approval_status != MCP_APPROVAL_STATUS_APPROVED:
        op.status = MCP_OPERATION_STATUS_PENDING_APPROVAL
        op.approval_status = MCP_APPROVAL_STATUS_PENDING
    else:
        op.status = MCP_OPERATION_STATUS_QUEUED
    op.updated_at = now
    op.error_message = ''
    op.next_attempt_at = now
    op.save(update_fields=['status', 'approval_status', 'updated_at', 'error_message', 'next_attempt_at'])
    _write_mcp_audit(request, server_id=op.server_id, action='operation_retry', tool_name=op.tool_name, status='ok')
    if request.POST.get('execute_now') and op.status == MCP_OPERATION_STATUS_QUEUED:
        _execute_operation(request, op)
    messages.success(request, 'Operation moved back to queue.')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:manage')
def mcp_operation_run(request, id):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    op = get_object_or_404(AcpMcpOperation, id=id)
    if op.status not in {MCP_OPERATION_STATUS_QUEUED, MCP_OPERATION_STATUS_RUNNING}:
        messages.error(request, 'Only queued or running operations can be run now.')
        return redirect('acp:mcp_operations')
    ok = _execute_operation(request, op)
    if ok:
        messages.success(request, 'Operation executed.')
    else:
        messages.error(request, f'Operation failed: {op.error_message or op.status}')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:manage')
def mcp_process_queue(request):
    if request.method != 'POST':
        return redirect('acp:mcp_operations')
    limit = safe_int(request.POST.get('limit'), default=20, min_value=1, max_value=100)
    try:
        queue = list(
            AcpMcpOperation.objects.filter(status=MCP_OPERATION_STATUS_QUEUED)
            .select_related('server')
            .order_by('created_at', 'id')[:limit]
        )
    except Exception:
        queue = []
    processed = 0
    for op in queue:
        if _execute_operation(request, op):
            processed += 1
    messages.success(request, f'Processed {processed} queued operation(s).')
    return redirect('acp:mcp_operations')


@permission_required('acp:mcp:audit:view')
def mcp_audit(request):
    selected_server_id = safe_int(request.GET.get('server_id'), default=0, min_value=0)
    status = clean_text(request.GET.get('status', ''), 30)
    try:
        servers = list(AcpMcpServer.objects.order_by('name', 'id'))
    except Exception:
        servers = []

    try:
        query = AcpMcpAuditEvent.objects.select_related('server').order_by('-created_at', '-id')
        if selected_server_id > 0:
            query = query.filter(server_id=selected_server_id)
        if status:
            query = query.filter(status__icontains=status)
        items = list(query[:300])
    except Exception:
        items = []

    return render(
        request,
        'admin/acp/mcp_audit.html',
        {
            'servers': servers,
            'selected_server_id': selected_server_id if selected_server_id > 0 else None,
            'status': status,
            'items': items,
        },
    )
