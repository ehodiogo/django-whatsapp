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
    "django.contrib.contenttypes",
    "django_whatsapp.apps.DjangoWhatsAppConfig",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True

DJANGO_WHATSAPP = {
    "ACCESS_TOKEN": env("WHATSAPP_ACCESS_TOKEN"),
    "PHONE_NUMBER_ID": env("WHATSAPP_PHONE_NUMBER_ID"),
    "API_VERSION": env("WHATSAPP_API_VERSION", default="v23.0"),
    "TIMEOUT": env.float("WHATSAPP_TIMEOUT", default=15.0),
}