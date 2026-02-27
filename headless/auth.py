import secrets

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from public.models import SiteSetting


def _site_setting(key):
    cache_key = f'headless:site_setting:{key}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        row = SiteSetting.objects.filter(key=key).only('value').first()
        value = (row.value if row else '') or ''
    except Exception:
        value = ''
    cache.set(cache_key, value, 30)
    return value


def _bool_like(value):
    return str(value or '').strip().lower() in {'1', 'true', 'yes', 'on'}


def require_delivery_token(view_func):
    def wrapped(request, *args, **kwargs):
        site_expected = _site_setting('headless_delivery_token').strip()
        env_expected = (getattr(settings, 'HEADLESS_DELIVERY_TOKEN', '') or '').strip()
        expected = site_expected or env_expected

        require_site = _bool_like(_site_setting('headless_delivery_require_token'))
        require_env = _bool_like(getattr(settings, 'HEADLESS_DELIVERY_REQUIRE_TOKEN', False))
        require_token = require_site or require_env
        if not require_token:
            return view_func(request, *args, **kwargs)

        if not expected:
            return JsonResponse({'ok': False, 'error': 'Delivery token is required but not configured.'}, status=503)

        provided = (request.headers.get('X-Delivery-Token') or '').strip()
        if not provided:
            auth = (request.headers.get('Authorization') or '').strip()
            if auth.lower().startswith('bearer '):
                provided = auth[7:].strip()
        if not provided or not secrets.compare_digest(expected, provided):
            return JsonResponse({'ok': False, 'error': 'Unauthorized.'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapped
