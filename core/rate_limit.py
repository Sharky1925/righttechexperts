"""
Rate-limiting helpers using Django's cache framework.

Usage:
    from core.rate_limit import check_rate_limit, clear_rate_limit

    # In a login view:
    ip = get_client_ip(request)
    if check_rate_limit(f'login:{ip}', max_attempts=5, window_seconds=300):
        messages.error(request, 'Too many attempts. Please wait a few minutes.')
        return render(...)

    # On successful login, clear the limiter:
    clear_rate_limit(f'login:{ip}')
"""
from __future__ import annotations

from django.core.cache import cache


def _cache_key(namespace: str) -> str:
    return f'ratelimit:{namespace}'


def check_rate_limit(namespace: str, *, max_attempts: int = 5, window_seconds: int = 300) -> bool:
    """
    Increment the attempt counter for *namespace* and return True if
    the caller has EXCEEDED the allowed number of attempts within the
    sliding window.  Returns False when the request is still allowed.
    """
    key = _cache_key(namespace)
    current = cache.get(key, 0)
    current += 1
    cache.set(key, current, window_seconds)
    return current > max_attempts


def clear_rate_limit(namespace: str) -> None:
    """Reset the counter after a successful action (e.g. login)."""
    cache.delete(_cache_key(namespace))


def get_client_ip(request) -> str:
    """
    Return the client IP, preferring X-Forwarded-For when behind a
    reverse proxy.  Falls back to REMOTE_ADDR.
    """
    xff = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
