import pytest


@pytest.fixture(autouse=True)
def default_whatsapp_settings(settings):
    """
    Ensure unit tests always run with predictable mock settings,
    regardless of what real credentials are in .env.
    """
    settings.DJANGO_WHATSAPP = {
        "ACCESS_TOKEN": "development-token",
        "PHONE_NUMBER_ID": "development-phone-number-id",
        "API_VERSION": "v23.0",
        "TIMEOUT": 15.0,
        "AUTO_SAVE": True,
        "WEBHOOK": {
            "VERIFY_TOKEN": "development-verify-token",
            "APP_SECRET": "development-app-secret",
            "CONSUMERS": [],
        },
    }
