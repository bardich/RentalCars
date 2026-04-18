"""Development settings."""

from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

COMPRESS_OFFLINE = False

COMPRESS_ENABLED = True

LOGGING['loggers']['django']['level'] = 'DEBUG'
