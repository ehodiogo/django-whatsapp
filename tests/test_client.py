import pytest
import respx

from httpx import Response

from django_whatsapp import WhatsAppClient
from django_whatsapp.conf import WhatsAppSettings
from django_whatsapp.exceptions import WhatsAppAPIError
from django_whatsapp.http import MetaAPIClient
from django_whatsapp.validators import InvalidMessageError


@respx.mock
def test_send_text():
    route = respx.post(
        "https://graph.facebook.com/v23.0/"
        "development-phone-number-id/messages"
    ).mock(
        return_value=Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "messages": [
                    {
                        "id": "wamid.test-123",
                    }
                ],
            },
        )
    )

    client = WhatsAppClient()

    result = client.messages.send_text(
        to="5511999999999",
        text="Olá!",
    )

    assert route.called
    assert result.messages[0].id == "wamid.test-123"


@respx.mock
def test_meta_api_error():
    respx.post(
        "https://graph.facebook.com/v23.0/"
        "development-phone-number-id/messages"
    ).mock(
        return_value=Response(
            400,
            json={
                "error": {
                    "message": "Invalid OAuth access token",
                    "type": "OAuthException",
                    "code": 190,
                }
            },
        )
    )

    client = WhatsAppClient()

    with pytest.raises(WhatsAppAPIError) as exc_info:
        client.messages.send_text(
            to="+55 (11) 99999-9999",
            text="Olá!",
        )

    error = exc_info.value

    assert error.status_code == 400
    assert error.error["code"] == 190


def test_http_client_lifecycle():
    config = WhatsAppSettings.from_django()

    client = MetaAPIClient(config)

    assert not client.client.is_closed

    client.close()

    assert client.client.is_closed


@respx.mock
def test_send_text_does_not_call_api_with_empty_text():
    route = respx.post(
        "https://graph.facebook.com/v23.0/"
        "development-phone-number-id/messages"
    ).mock()

    client = WhatsAppClient()

    with pytest.raises(InvalidMessageError):
        client.messages.send_text(
            to="5511999999999",
            text="",
        )

    assert not route.called


def test_client_exposes_messages():
    client = WhatsAppClient()

    assert client.messages is not None