from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parents[3]

env = environ.Env()

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = "django-whatsapp-development"

DEBUG = True

ALLOWED_HOSTS = []

ROOT_URLCONF = "config.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django_whatsapp.apps.DjangoWhatsAppConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True

DJANGO_WHATSAPP = {
    "ACCESS_TOKEN": env("WHATSAPP_ACCESS_TOKEN"),
    "PHONE_NUMBER_ID": env("WHATSAPP_PHONE_NUMBER_ID"),
    "API_VERSION": env(
        "WHATSAPP_API_VERSION",
        default="v23.0",
    ),
    "TIMEOUT": env.float(
        "WHATSAPP_TIMEOUT",
        default=15.0,
    ),
    "WEBHOOK": {
        "VERIFY_TOKEN": env(
            "WHATSAPP_VERIFY_TOKEN",
            default="development-verify-token",
        ),
        "APP_SECRET": env(
            "WHATSAPP_APP_SECRET",
            default="development-app-secret",
        ),
        "CONSUMERS": [],
    },
}