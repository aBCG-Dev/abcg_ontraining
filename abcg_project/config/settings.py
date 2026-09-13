import os
from pathlib import Path

# 1. Base Directory Location
# This calculates the absolute path to your root folder dynamically
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Security Configurations
SECRET_KEY = "django-insecure-scratch-development-key-rules"
DEBUG = True
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://*.vercel.app',
    'https://*.netlify.app',
    'https://*.ngrok-free.dev',
    'https://*.ngrok.io',
    'https://*.render.com',
    'https://*.onrender.com',
]

# 3. Installed Apps Registry
# This tells Django to activate its internal modules AND our custom code app
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "questions",  # This links our custom workspace folder!
    "eptb"
]

# 4. Middleware Security & Sessions Layer
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 5. Routing Entry Point
ROOT_URLCONF = "config.urls"

# 6. HTML Template Configurations
# This tells Django to look inside our templates folder to find the visual components
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "questions" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "questions.context_processors.navbar_choices",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# 7. Database Configuration
# Supports DATABASE_URL (e.g. Neon, Supabase PostgreSQL), Vercel /tmp writable fallback, and local SQLite
if os.environ.get("DATABASE_URL"):
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.environ.get("VERCEL"):
    import shutil
    tmp_db = Path("/tmp/db.sqlite3")
    bundled_db = BASE_DIR / "db.sqlite3"
    if not tmp_db.exists() and bundled_db.exists():
        try:
            shutil.copy2(bundled_db, tmp_db)
        except Exception:
            pass
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(tmp_db) if tmp_db.exists() else bundled_db,
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# 8. Localization Setup
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# 9. Static & Media Assets Routing
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB limit per photo
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 10. Central Sync Backend Integration
CENTRAL_BACKEND_URL = "http://127.0.0.1:8001"  # Default on-premise backend URL
CENTRAL_BACKEND_USER = "admin"
CENTRAL_BACKEND_PASSWORD = "adminpassword"