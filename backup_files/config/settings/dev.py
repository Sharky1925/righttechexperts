from pathlib import Path
import os

from .base import *  # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

# Local migration preview should use the legacy Flask DB by default so existing
# content/settings render immediately in Django without reseeding.
legacy_default = '/Users/umutdemirkapu/mylauncher/app/site.db'
legacy_path = Path(os.environ.get('LEGACY_SQLITE_PATH', legacy_default)).expanduser()
if not os.environ.get('DATABASE_URL') and legacy_path.exists():
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(legacy_path),
        }
    }
