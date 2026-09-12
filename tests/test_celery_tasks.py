import json
import pytest
from unittest.mock import MagicMock, patch
from django_whatsapp.tasks import process_webhook_payload
from django_whatsapp.models import WhatsAppContact, WhatsAppMessage

pytestmark = pytest.mark.django_db


def test_process_webhook_payload_synchronously():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "metadata": {"phone_number_id": "phone-123"},
                            "contacts": [{"profile": {"name": "Celery User"}, "wa_id": "5511944445555"}],
                            "messages": [
                                {
                                    "from": "5511944445555",
                                    "id": "wamid.celery-test-1",
                                    "type": "text",
                                    "text": {"body": "Testando task síncrona"},
                                }
                            ],
                        },
                    }
                ]
            }
        ],
    }

    count = process_webhook_payload(payload)
    assert count == 1

    contact = WhatsAppContact.objects.get(phone_number="5511944445555")
    assert contact.name == "Celery User"
    msg = WhatsAppMessage.objects.get(wamid="wamid.celery-test-1")
    assert msg.body == "Testando task síncrona"


def test_webhook_view_with_celery_setting(client, settings):
    settings.DJANGO_WHATSAPP = {
        **settings.DJANGO_WHATSAPP,
        "USE_CELERY": True,
    }

    payload = {
        "object": "whatsapp_business_account",
        "entry": [],
    }
    body = json.dumps(payload).encode()

    with patch("django_whatsapp.webhooks.views.process_webhook_payload_task") as mock_task:
        mock_task.delay = MagicMock()
        
        import hmac, hashlib
        digest = hmac.new(b"development-app-secret", body, hashlib.sha256).hexdigest()

        response = client.post(
            "/whatsapp/webhook/",
            data=body,
            content_type="application/json",
            HTTP_X_HUB_SIGNATURE_256=f"sha256={digest}",
        )

        assert response.status_code == 200
        assert response.json().get("queued") is True
        mock_task.delay.assert_called_once_with(payload)
