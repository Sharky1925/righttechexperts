import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parents[2]

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-key-change-me')
DEBUG = False
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'public',
    'headless',
    'admin_panel',
    'acp',
]

MIDDLEWARE = [
    'core.middleware.PathInfoNormalizerMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RequestIDMiddleware',
    'core.middleware.CSPNonceMiddleware',
    'core.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [BASE_DIR / 'app' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'environment': 'config.jinja2_env.environment',
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.globals_context',
                'core.context_processors.admin_context',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


def _postgres_db_from_url(raw_url: str):
    parsed = urlparse(raw_url.replace('postgres://', 'postgresql://', 1))
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': (parsed.path or '').lstrip('/'),
        'USER': parsed.username or '',
        'PASSWORD': parsed.password or '',
        'HOST': parsed.hostname or '',
        'PORT': str(parsed.port or '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '60')),
    }


DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
SQLITE_PATH = (
    os.environ.get('SQLITE_PATH', '').strip()
    or os.environ.get('LEGACY_SQLITE_PATH', '').strip()
)
if DATABASE_URL:
    DATABASES = {'default': _postgres_db_from_url(DATABASE_URL)}
elif SQLITE_PATH:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(Path(SQLITE_PATH).expanduser()),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_USER_MODEL = 'admin_panel.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.ScryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'core.hashers.WerkzeugPBKDF2SHA256PasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = False

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'app' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/admin/uploads/'
MEDIA_ROOT = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))

APP_BASE_URL = os.environ.get('APP_BASE_URL', '').strip().rstrip('/')
ROBOTS_DISALLOW_ALL = os.environ.get('ROBOTS_DISALLOW_ALL', '0').strip().lower() in {'1', 'true', 'yes'}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'mylauncher-main-cache',
    }
}
SITE_CONTEXT_CACHE_VERSION = os.environ.get('SITE_CONTEXT_CACHE_VERSION', 'v1').strip() or 'v1'
SITE_CONTEXT_CACHE_TTL = int(os.environ.get('SITE_CONTEXT_CACHE_TTL', '120'))
SEO_CACHE_VERSION = os.environ.get('SEO_CACHE_VERSION', 'v1').strip() or 'v1'
SEO_CACHE_TTL = int(os.environ.get('SEO_CACHE_TTL', '900'))

CSRF_COOKIE_HTTPONLY = True
SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 28800  # 8 hours

LOGIN_URL = '/admin/login'
LOGIN_REDIRECT_URL = '/admin/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SECURE_CONTENT_TYPE_NOSNIFF = True
