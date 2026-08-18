import hashlib
import hmac
import json
import pytest
from django_whatsapp.models import (
    MessageDirection,
    MessageStatus,
    MessageType,
    WhatsAppContact,
    WhatsAppMessage,
)

pytestmark = pytest.mark.django_db


def sign_payload(payload: bytes) -> str:
    digest = hmac.new(
        b"development-app-secret",
        payload,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def test_webhook_persists_inbound_message_and_contact(client):
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
                            "contacts": [
                                {
                                    "profile": {
                                        "name": "João da Silva"
                                    },
                                    "wa_id": "5511988887777",
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5511988887777",
                                    "id": "wamid.inbound-999",
                                    "timestamp": "1700000000",
                                    "type": "text",
                                    "text": {
                                        "body": "Boa tarde, preciso de ajuda."
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    body = json.dumps(payload, separators=(",", ":")).encode()

    response = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )

    assert response.status_code == 200

    # Contact should be created automatically
    contact = WhatsAppContact.objects.get(phone_number="5511988887777")
    assert contact.name == "João da Silva"
    assert contact.wa_id == "5511988887777"

    # Message should be created automatically
    msg = WhatsAppMessage.objects.get(wamid="wamid.inbound-999")
    assert msg.contact == contact
    assert msg.direction == MessageDirection.INBOUND
    assert msg.message_type == MessageType.TEXT
    assert msg.status == MessageStatus.RECEIVED
    assert msg.body == "Boa tarde, preciso de ajuda."
    assert msg.timestamp is not None


def test_webhook_updates_message_status_flow(client):
    # Setup contact and initial outbound message
    contact = WhatsAppContact.objects.create(
        phone_number="5511977776666",
        name="Carlos",
    )
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.outbound-status-test",
        direction=MessageDirection.OUTBOUND,
        message_type=MessageType.TEXT,
        status=MessageStatus.SENT,
        body="Seu pedido foi confirmado!",
    )

    # 1. Simulate "delivered" status update from webhook
    delivered_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.outbound-status-test",
                                    "status": "delivered",
                                    "timestamp": "1700000100",
                                    "recipient_id": "5511977776666",
                                }
                            ]
                        },
                    }
                ]
            }
        ],
    }
    body = json.dumps(delivered_payload, separators=(",", ":")).encode()
    res = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )
    assert res.status_code == 200

    msg.refresh_from_db()
    assert msg.status == MessageStatus.DELIVERED
    assert msg.delivered_at is not None

    # 2. Simulate "read" status update from webhook
    read_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.outbound-status-test",
                                    "status": "read",
                                    "timestamp": "1700000200",
                                    "recipient_id": "5511977776666",
                                }
                            ]
                        },
                    }
                ]
            }
        ],
    }
    body = json.dumps(read_payload, separators=(",", ":")).encode()
    res = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )
    assert res.status_code == 200

    msg.refresh_from_db()
    assert msg.status == MessageStatus.READ
    assert msg.read_at is not None


def test_webhook_failed_status(client):
    contact = WhatsAppContact.objects.create(
        phone_number="5511966665555",
    )
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.outbound-failed-test",
        direction=MessageDirection.OUTBOUND,
        status=MessageStatus.SENT,
    )

    failed_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "statuses": [
                                {
                                    "id": "wamid.outbound-failed-test",
                                    "status": "failed",
                                    "timestamp": "1700000300",
                                    "recipient_id": "5511966665555",
                                    "errors": [
                                        {
                                            "code": 131026,
                                            "title": "Message Undeliverable",
                                        }
                                    ],
                                }
                            ]
                        },
                    }
                ]
            }
        ],
    }
    body = json.dumps(failed_payload, separators=(",", ":")).encode()
    res = client.post(
        "/whatsapp/webhook/",
        data=body,
        content_type="application/json",
        HTTP_X_HUB_SIGNATURE_256=sign_payload(body),
    )
    assert res.status_code == 200

    msg.refresh_from_db()
    assert msg.status == MessageStatus.FAILED
    assert msg.failed_at is not None
    assert msg.error_data == {"errors": [{"code": 131026, "title": "Message Undeliverable"}]}
