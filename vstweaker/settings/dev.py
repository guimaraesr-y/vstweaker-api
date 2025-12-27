import os
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
}

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "media"

# melhor DX
INSTALLED_APPS += ["django_extensions"]

# celery local
CELERY_TASK_ALWAYS_EAGER = False

CORS_ALLOW_ALL_ORIGINS = True
