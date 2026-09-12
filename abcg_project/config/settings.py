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
    'https://singer-evacuee-sediment.ngrok-free.dev',
]

# 3. Installed Apps Registry
# This tells Django to activate its internal modules AND our custom code app
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "questions",  # This links our custom workspace folder!
    "eptb"
]

# 4. Middleware Security & Sessions Layer
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
# We are starting with standard SQLite3 locally for fast agile progress
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

# 9. Static Assets (CSS / JS) Routing
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 10. Central Sync Backend Integration
CENTRAL_BACKEND_URL = "http://127.0.0.1:8001"  # Default on-premise backend URL
CENTRAL_BACKEND_USER = "admin"
CENTRAL_BACKEND_PASSWORD = "adminpassword"