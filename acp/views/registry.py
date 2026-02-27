from __future__ import annotations

from django.shortcuts import render

from acp.models import AcpComponentDefinition, AcpWidgetDefinition
from admin_panel.decorators import permission_required


@permission_required('acp:registry:manage')
def registry(request):
    try:
        components = list(AcpComponentDefinition.objects.order_by('category', 'name', 'id'))
    except Exception:
        components = []
    try:
        widgets = list(AcpWidgetDefinition.objects.order_by('category', 'name', 'id'))
    except Exception:
        widgets = []
    return render(
        request,
        'admin/acp/registry.html',
        {
            'components': components,
            'widgets': widgets,
        },
    )
