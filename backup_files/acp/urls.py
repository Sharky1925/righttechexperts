from django.urls import path

from acp.views import content, dashboards, mcp, pages, registry, studio, theme

app_name = 'acp'

urlpatterns = [
    path('', studio.studio, name='index'),
    path('studio', studio.studio, name='studio'),
    path('audit', studio.audit, name='audit'),
    path('metrics', studio.metrics, name='metrics'),
    path('promote', studio.promote, name='promote'),

    path('pages', pages.pages, name='pages'),
    path('pages/add', pages.page_add, name='page_add'),
    path('pages/<int:id>/edit', pages.page_edit, name='page_edit'),
    path('pages/<int:id>/publish', pages.page_publish, name='page_publish'),
    path('pages/<int:id>/snapshot', pages.page_snapshot, name='page_snapshot'),
    path('sync-status', pages.sync_status, name='sync_status'),
    path('sync-status/resync', pages.sync_resync, name='sync_resync'),

    path('dashboards', dashboards.dashboards, name='dashboards'),
    path('dashboards/add', dashboards.dashboard_add, name='dashboard_add'),
    path('dashboards/<int:id>/edit', dashboards.dashboard_edit, name='dashboard_edit'),
    path('dashboards/<int:id>/preview', dashboards.dashboard_preview, name='dashboard_preview'),
    path('dashboards/<int:id>/publish', dashboards.dashboard_publish, name='dashboard_publish'),
    path('dashboards/<int:id>/snapshot', dashboards.dashboard_snapshot, name='dashboard_snapshot'),

    path('content-types', content.content_types, name='content_types'),
    path('content-types/add', content.content_type_add, name='content_type_add'),
    path('content-types/<int:id>/edit', content.content_type_edit, name='content_type_edit'),
    path('content-entries', content.content_entries, name='content_entries'),
    path('content-entries/add', content.content_entry_add, name='content_entry_add'),
    path('content-entries/<int:id>/edit', content.content_entry_edit, name='content_entry_edit'),

    path('theme', theme.theme_tokens, name='theme_tokens'),
    path('theme/add', theme.theme_token_add, name='theme_token_add'),
    path('theme/<int:id>/edit', theme.theme_token_edit, name='theme_token_edit'),

    path('mcp/servers', mcp.mcp_servers, name='mcp_servers'),
    path('mcp/servers/add', mcp.mcp_server_add, name='mcp_server_add'),
    path('mcp/servers/<int:id>/edit', mcp.mcp_server_edit, name='mcp_server_edit'),
    path('mcp/operations', mcp.mcp_operations, name='mcp_operations'),
    path('mcp/operations/create', mcp.mcp_operation_create, name='mcp_operation_create'),
    path('mcp/operations/<int:id>/approve', mcp.mcp_operation_approve, name='mcp_operation_approve'),
    path('mcp/operations/<int:id>/reject', mcp.mcp_operation_reject, name='mcp_operation_reject'),
    path('mcp/operations/<int:id>/retry', mcp.mcp_operation_retry, name='mcp_operation_retry'),
    path('mcp/operations/<int:id>/run', mcp.mcp_operation_run, name='mcp_operation_run'),
    path('mcp/operations/process-queue', mcp.mcp_process_queue, name='mcp_process_queue'),
    path('mcp/audit', mcp.mcp_audit, name='mcp_audit'),

    path('registry', registry.registry, name='registry'),
]
