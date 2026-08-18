import hashlib
import hmac
import json
import pytest
from django_whatsapp.webhooks.consumers import (
    WhatsAppConsumer,
)

pytestmark = pytest.mark.django_db

class RecordingConsumer(WhatsAppConsumer):

    def __init__(self):
        self.received = []

    def on_message(self, event):
        self.received.append(event)

def test_webhook_verification(client):
    response = client.get(
        "/whatsapp/webhook/",
        {
            "hub.mode": "subscribe",
            "hub.verify_token": (
                "development-verify-token"
            ),
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 200
    assert response.content == b"challenge-123"
    assert response["Content-Type"].startswith(
        "text/plain"
    )

def test_webhook_verification_invalid_token(client):
    response = client.get(
        "/whatsapp/webhook/",
        {
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 403

def test_webhook_verification_invalid_mode(client):
    response = client.get(
        "/whatsapp/webhook/",
        {
            "hub.mode": "invalid",
            "hub.verify_token": (
                "development-verify-token"
            ),
            "hub.challenge": "challenge-123",
        },
    )

    assert response.status_code == 403

def sign_payload(payload: bytes) -> str:
    digest = hmac.new(
        b"development-app-secret",
        payload,
        hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}"

def test_webhook_post(client):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [],
    }

    body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )

    assert response.status_code == 200

    assert response.json() == {
        "received": True,
        "events": 1,
    }

def test_webhook_post_invalid_signature(client):
    body = b'{"object":"whatsapp_business_account"}'

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=(
            "sha256=invalid"
        ),
    )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Invalid signature.",
    }

def test_webhook_post_missing_signature(client):
    body = b'{"object":"whatsapp_business_account"}'

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
    )

    assert response.status_code == 403

def test_webhook_post_invalid_json(client):
    body = b'{"invalid-json"'

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )

    assert response.status_code == 400

    assert response.json() == {
        "detail": "Invalid JSON.",
    }


def test_webhook_post_message(client):
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba-123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "metadata": {
                                "phone_number_id": "phone-123",
                            },
                            "messages": [
                                {
                                    "from": "5511999999999",
                                    "id": "wamid.received-123",
                                    "type": "text",
                                    "text": {
                                        "body": "Olá!"
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )

    assert response.status_code == 200

    assert response.json() == {
        "received": True,
        "events": 1,
    }

def test_webhook_dispatches_to_consumer(
    client,
    settings,
):
    settings.DJANGO_WHATSAPP = {
        **settings.DJANGO_WHATSAPP,
        "WEBHOOK": {
            **settings.DJANGO_WHATSAPP.get("WEBHOOK", {}),
            "CONSUMERS": [
                "tests.test_webhook_views.RecordingConsumer",
            ],
        },
    }

    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {
                                "phone_number_id": "phone-123",
                            },
                            "messages": [
                                {
                                    "id": "wamid.consumer-123",
                                    "from": "5511999999999",
                                    "type": "text",
                                    "text": {
                                        "body": "Olá!"
                                    },
                                }
                            ],
                        }
                    }
                ]
            }
        ],
    }

    body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )

    assert response.status_code == 200

    assert response.json() == {
        "received": True,
        "events": 1,
    }