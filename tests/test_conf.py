import pytest

from django_whatsapp.conf import WhatsAppSettings


def test_settings_from_django():
    config = WhatsAppSettings.from_django()

    assert config.access_token == "development-token"
    assert config.phone_number_id == "development-phone-number-id"
    assert config.api_version == "v23.0"
    assert config.timeout == 15.0