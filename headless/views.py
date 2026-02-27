from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from acp.models import AcpContentEntry, AcpDashboardDocument, AcpPageDocument, AcpThemeTokenSet
from headless.auth import require_delivery_token


def health(request):
    return JsonResponse({'ok': True, 'service': 'django', 'component': 'headless-api'})


@require_delivery_token
def headless_export(request):
    return JsonResponse({'ok': True, 'mode': 'scaffold', 'endpoint': 'headless_export'})


@csrf_exempt
@require_delivery_token
def headless_sync_upsert(request):
    return JsonResponse({'ok': True, 'mode': 'scaffold', 'endpoint': 'headless_sync_upsert'})


@require_delivery_token
def delivery_index(request):
    return JsonResponse({'ok': True, 'mode': 'scaffold', 'endpoint': 'delivery_index'})


def _load_json(raw, fallback):
    import json

    try:
        data = json.loads(raw or '')
    except (TypeError, ValueError):
        return fallback
    if isinstance(fallback, dict) and isinstance(data, dict):
        return data
    if isinstance(fallback, list) and isinstance(data, list):
        return data
    return fallback


def _can_view_unpublished(request):
    user = getattr(request, 'user', None)
    checker = getattr(user, 'has_permission', None)
    return bool(user and user.is_authenticated and callable(checker) and checker('acp:studio:view'))


@require_delivery_token
def acp_delivery_page(request, slug):
    allow_unpublished = _can_view_unpublished(request)
    query = AcpPageDocument.objects.filter(slug=slug)
    if not allow_unpublished:
        query = query.filter(status='published')
    item = query.first()
    if not item:
        return JsonResponse({'ok': False, 'error': 'Page not found.'}, status=404)
    return JsonResponse(
        {
            'ok': True,
            'page': {
                'id': item.id,
                'slug': item.slug,
                'title': item.title,
                'template_id': item.template_id,
                'locale': item.locale,
                'status': item.status,
                'seo': _load_json(item.seo_json, {}),
                'blocks_tree': _load_json(item.blocks_tree, {}),
                'theme_override': _load_json(item.theme_override_json, {}),
                'published_at': item.published_at.isoformat() if item.published_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            },
        }
    )


@require_delivery_token
def acp_delivery_dashboard(request, dashboard_id):
    allow_unpublished = _can_view_unpublished(request)
    query = AcpDashboardDocument.objects.filter(dashboard_id=dashboard_id)
    if not allow_unpublished:
        query = query.filter(status='published')
    item = query.first()
    if not item:
        return JsonResponse({'ok': False, 'error': 'Dashboard not found.'}, status=404)
    return JsonResponse(
        {
            'ok': True,
            'dashboard': {
                'id': item.id,
                'dashboard_id': item.dashboard_id,
                'title': item.title,
                'route': item.route,
                'layout_type': item.layout_type,
                'status': item.status,
                'layout_config': _load_json(item.layout_config_json, {}),
                'widgets': _load_json(item.widgets_json, []),
                'global_filters': _load_json(item.global_filters_json, []),
                'role_visibility': _load_json(item.role_visibility_json, {}),
                'published_at': item.published_at.isoformat() if item.published_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            },
        }
    )


@require_delivery_token
def acp_delivery_theme(request, token_set_key):
    allow_unpublished = _can_view_unpublished(request)
    query = AcpThemeTokenSet.objects.filter(key=token_set_key)
    if not allow_unpublished:
        query = query.filter(status='published')
    item = query.first()
    if not item:
        return JsonResponse({'ok': False, 'error': 'Theme token set not found.'}, status=404)
    return JsonResponse(
        {
            'ok': True,
            'theme': {
                'id': item.id,
                'key': item.key,
                'name': item.name,
                'status': item.status,
                'tokens': _load_json(item.tokens_json, {}),
                'published_at': item.published_at.isoformat() if item.published_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            },
        }
    )


@require_delivery_token
def acp_delivery_content_entry(request, content_type_key, entry_key):
    allow_unpublished = _can_view_unpublished(request)
    query = AcpContentEntry.objects.select_related('content_type').filter(
        content_type__key=content_type_key,
        entry_key=entry_key,
    )
    if not allow_unpublished:
        query = query.filter(status='published')
    item = query.order_by('-updated_at', '-id').first()
    if not item:
        return JsonResponse({'ok': False, 'error': 'Content entry not found.'}, status=404)
    return JsonResponse(
        {
            'ok': True,
            'entry': {
                'id': item.id,
                'content_type_key': item.content_type.key if item.content_type else content_type_key,
                'entry_key': item.entry_key,
                'title': item.title,
                'locale': item.locale,
                'status': item.status,
                'data': _load_json(item.data_json, {}),
                'published_at': item.published_at.isoformat() if item.published_at else None,
                'updated_at': item.updated_at.isoformat() if item.updated_at else None,
            },
        }
    )
