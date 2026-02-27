import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa

DEBUG = False

_secret_key = os.environ.get('SECRET_KEY', '').strip()
if not _secret_key:
    raise ImproperlyConfigured('SECRET_KEY must be set in production.')
SECRET_KEY = _secret_key

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured('ALLOWED_HOSTS must be set in production.')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.environ.get('FORCE_HTTPS', '1') == '1'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '1') == '1'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', '1') == '1'
SECURE_HSTS_SECONDS = int(os.environ.get('HSTS_MAX_AGE', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
