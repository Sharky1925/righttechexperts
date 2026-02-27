from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render

from acp.models import (
    AcpAuditEvent,
    AcpComponentDefinition,
    AcpContentEntry,
    AcpContentEntryVersion,
    AcpContentType,
    AcpContentTypeVersion,
    AcpDashboardDocument,
    AcpDashboardVersion,
    AcpEnvironment,
    AcpMcpOperation,
    AcpMcpServer,
    AcpMetricDefinition,
    AcpPageDocument,
    AcpPageRouteBinding,
    AcpPageVersion,
    AcpPromotionEvent,
    AcpThemeTokenSet,
    AcpThemeTokenVersion,
    AcpWidgetDefinition,
)
from acp.views.common import safe_int, write_audit
from admin_panel.decorators import permission_required
from core.constants import (
    MCP_OPERATION_STATUS_PENDING_APPROVAL,
    MCP_OPERATION_STATUS_QUEUED,
    WORKFLOW_PUBLISHED,
)
from core.utils import clean_text, utc_now_naive


def _safe_count(model, **filters):
    try:
        return model.objects.filter(**filters).count() if filters else model.objects.count()
    except Exception:
        return 0


@permission_required('acp:studio:view')
def studio(request):
    stats = {
        'pages': _safe_count(AcpPageDocument),
        'published_pages': _safe_count(AcpPageDocument, status=WORKFLOW_PUBLISHED),
        'dashboards': _safe_count(AcpDashboardDocument),
        'published_dashboards': _safe_count(AcpDashboardDocument, status=WORKFLOW_PUBLISHED),
        'content_types': _safe_count(AcpContentType),
        'content_entries': _safe_count(AcpContentEntry),
        'theme_tokens': _safe_count(AcpThemeTokenSet),
        'mcp_servers': _safe_count(AcpMcpServer),
        'mcp_operations': _safe_count(AcpMcpOperation),
        'mcp_queue': _safe_count(AcpMcpOperation, status=MCP_OPERATION_STATUS_QUEUED),
        'mcp_pending_approval': _safe_count(AcpMcpOperation, status=MCP_OPERATION_STATUS_PENDING_APPROVAL),
        'components': _safe_count(AcpComponentDefinition),
        'widgets': _safe_count(AcpWidgetDefinition),
        'metrics': _safe_count(AcpMetricDefinition),
        'route_bindings': _safe_count(AcpPageRouteBinding),
        'out_of_sync_routes': _safe_count(AcpPageRouteBinding) - _safe_count(AcpPageRouteBinding, sync_status='synced'),
        'audit_events': _safe_count(AcpAuditEvent),
    }
    stats['versions'] = (
        _safe_count(AcpPageVersion)
        + _safe_count(AcpDashboardVersion)
        + _safe_count(AcpContentTypeVersion)
        + _safe_count(AcpContentEntryVersion)
        + _safe_count(AcpThemeTokenVersion)
    )
    try:
        recent_audit = list(AcpAuditEvent.objects.order_by('-created_at', '-id')[:10])
    except Exception:
        recent_audit = []
    try:
        environments = list(AcpEnvironment.objects.order_by('-is_default', 'label', 'id'))
    except Exception:
        environments = []

    return render(
        request,
        'admin/acp/studio.html',
        {
            'stats': stats,
            'recent_audit': recent_audit,
            'environments': environments,
        },
    )


@permission_required('acp:metrics:manage')
def metrics(request):
    try:
        items = list(AcpMetricDefinition.objects.order_by('-is_enabled', 'dataset_key', 'key', 'id'))
    except Exception:
        items = []
    return render(request, 'admin/acp/metrics.html', {'metrics': items})


@permission_required('acp:audit:view')
def audit(request):
    domain = clean_text(request.GET.get('domain', ''), 50)
    action = clean_text(request.GET.get('action', ''), 50)
    environment = clean_text(request.GET.get('environment', ''), 40)

    try:
        query = AcpAuditEvent.objects.order_by('-created_at', '-id')
        if domain:
            query = query.filter(domain__icontains=domain)
        if action:
            query = query.filter(action__icontains=action)
        if environment:
            query = query.filter(environment__icontains=environment)
        items = list(query[:200])
    except Exception:
        items = []

    return render(
        request,
        'admin/acp/audit.html',
        {
            'items': items,
            'domain': domain,
            'action': action,
            'environment': environment,
        },
    )


@permission_required('acp:environments:manage')
def promote(request):
    if request.method != 'POST':
        return redirect('acp:studio')

    resource_type = clean_text(request.POST.get('resource_type', ''), 40).lower()
    resource_id = safe_int(request.POST.get('resource_id'), default=0, min_value=0)
    version_number = safe_int(request.POST.get('version_number'), default=1, min_value=1)
    target_environment = clean_text(request.POST.get('target_environment', ''), 40).lower()
    notes = clean_text(request.POST.get('notes', ''), 300)

    if resource_type not in {'page', 'dashboard'}:
        messages.error(request, 'Resource type must be page or dashboard.')
        return redirect('acp:studio')
    if resource_id <= 0:
        messages.error(request, 'Resource ID must be greater than zero.')
        return redirect('acp:studio')
    if not target_environment:
        messages.error(request, 'Target environment is required.')
        return redirect('acp:studio')

    source_environment = 'development'
    try:
        default_env = AcpEnvironment.objects.filter(is_default=True).only('key').first()
        if default_env and default_env.key:
            source_environment = clean_text(default_env.key, 40).lower() or source_environment
    except Exception:
        pass

    try:
        AcpPromotionEvent.objects.create(
            source_environment=source_environment,
            target_environment=target_environment,
            resource_type=resource_type,
            resource_id=resource_id,
            version_number=version_number,
            status='recorded',
            notes=notes,
            promoted_by_id=getattr(request.user, 'id', None),
            created_at=utc_now_naive(),
        )
        write_audit(
            request,
            domain='promotion',
            action='record',
            entity_type=resource_type,
            entity_id=str(resource_id),
            after_json=f'{{"target_environment":"{target_environment}","version_number":{version_number}}}',
            environment=target_environment,
        )
        messages.success(request, 'Promotion event recorded.')
    except Exception:
        messages.error(request, 'Could not record promotion event.')

    return redirect('acp:studio')
