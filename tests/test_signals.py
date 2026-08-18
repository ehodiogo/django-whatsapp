import hashlib
import hmac
import json
import httpx
import pytest
import respx
from django_whatsapp.client import WhatsAppClient
from django_whatsapp.models import (
    MessageDirection,
    MessageStatus,
    WhatsAppContact,
    WhatsAppMessage,
)
from django_whatsapp.signals import (
    contact_created,
    contact_updated,
    message_received,
    message_sent,
    message_status_updated,
)

pytestmark = pytest.mark.django_db


def sign_payload(payload: bytes) -> str:
    digest = hmac.new(
        b"development-app-secret",
        payload,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def test_signals_on_webhook_message_received(client):
    received_events = []
    contact_events = []

    def on_msg_received(sender, message, contact, raw_event, **kwargs):
        received_events.append((message, contact, raw_event))

    def on_contact_created(sender, contact, created, **kwargs):
        contact_events.append((contact, created))

    message_received.connect(on_msg_received)
    contact_created.connect(on_contact_created)

    try:
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "metadata": {"phone_number_id": "phone-123"},
                                "contacts": [{"profile": {"name": "Ana"}, "wa_id": "5511955554444"}],
                                "messages": [
                                    {
                                        "from": "5511955554444",
                                        "id": "wamid.signal-test-1",
                                        "type": "text",
                                        "text": {"body": "Oi, tudo bem?"},
                                    }
                                ],
                            },
                        }
                    ]
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

        assert len(contact_events) == 1
        assert contact_events[0][0].phone_number == "5511955554444"
        assert contact_events[0][1] is True

        assert len(received_events) == 1
        assert received_events[0][0].wamid == "wamid.signal-test-1"
        assert received_events[0][1].phone_number == "5511955554444"
    finally:
        message_received.disconnect(on_msg_received)
        contact_created.disconnect(on_contact_created)


def test_signals_on_status_updated(client):
    contact = WhatsAppContact.objects.create(phone_number="5511944443333")
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.status-signal-test",
        direction=MessageDirection.OUTBOUND,
        status=MessageStatus.SENT,
    )

    status_events = []

    def on_status_change(sender, message, status, previous_status, raw_event, **kwargs):
        status_events.append((message, status, previous_status))

    message_status_updated.connect(on_status_change)

    try:
        payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "changes": [
                        {
                            "field": "messages",
                            "value": {
                                "statuses": [
                                    {
                                        "id": "wamid.status-signal-test",
                                        "status": "delivered",
                                        "timestamp": "1700000500",
                                        "recipient_id": "5511944443333",
                                    }
                                ]
                            },
                        }
                    ]
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

        assert len(status_events) == 1
        assert status_events[0][0].wamid == "wamid.status-signal-test"
        assert status_events[0][1] == MessageStatus.DELIVERED
        assert status_events[0][2] == MessageStatus.SENT
    finally:
        message_status_updated.disconnect(on_status_change)


@respx.mock
def test_signals_on_outbound_send():
    sent_events = []

    def on_sent(sender, message, contact, **kwargs):
        sent_events.append((message, contact))

    message_sent.connect(on_sent)

    try:
        respx.post(
            "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "messaging_product": "whatsapp",
                    "contacts": [{"input": "5511933332222", "wa_id": "5511933332222"}],
                    "messages": [{"id": "wamid.signal-outbound-1"}],
                },
            )
        )

        client = WhatsAppClient()
        client.messages.send_text(
            to="5511933332222",
            text="Testando signal de envio",
        )

        assert len(sent_events) == 1
        assert sent_events[0][0].wamid == "wamid.signal-outbound-1"
        assert sent_events[0][1].phone_number == "5511933332222"
    finally:
        message_sent.disconnect(on_sent)
