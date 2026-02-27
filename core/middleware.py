import secrets
import time
import uuid

from django.conf import settings as django_settings


class PathInfoNormalizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path != '/' and request.path.endswith('//'):
            request.path_info = request.path.rstrip('/')

        # Flask compatibility aliases used by Jinja templates.
        request.args = request.GET
        request.form = request.POST

        response = self.get_response(request)
        return response


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = str(uuid.uuid4())
        request._start_ts = time.perf_counter()
        response = self.get_response(request)
        response['X-Request-ID'] = request.request_id
        # Only expose timing information in development
        if getattr(django_settings, 'DEBUG', False):
            duration_ms = int((time.perf_counter() - request._start_ts) * 1000)
            response['Server-Timing'] = f'app;dur={duration_ms}'
        return response


class CSPNonceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = secrets.token_urlsafe(16)
        response = self.get_response(request)
        nonce = getattr(request, 'csp_nonce', '')
        if nonce:
            csp = (
                "default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tiny.cloud https://challenges.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.tiny.cloud; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
                "connect-src 'self' https://cdn.tiny.cloud https://challenges.cloudflare.com; "
                "frame-src 'self' https://challenges.cloudflare.com; "
                "frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
            )
            if not getattr(django_settings, 'DEBUG', False):
                csp += " upgrade-insecure-requests;"
            response['Content-Security-Policy'] = csp
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault('Cross-Origin-Resource-Policy', 'same-origin')
        response.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        response.setdefault('X-Permitted-Cross-Domain-Policies', 'none')
        response.setdefault('Origin-Agent-Cluster', '?1')
        response.setdefault(
            'Permissions-Policy',
            'camera=(), microphone=(), geolocation=(), payment=(), usb=(), '
            'magnetometer=(), gyroscope=(), accelerometer=()'
        )
        return response

