import pytest
import respx
import httpx
from django_whatsapp.models import (
    MessageDirection,
    MessageStatus,
    MessageType,
    WhatsAppContact,
    WhatsAppMessage,
)
from django_whatsapp.client import WhatsAppClient

pytestmark = pytest.mark.django_db


def test_create_contact():
    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
        wa_id="5511999999999",
        name="Maria Silva",
    )

    assert str(contact) == "Maria Silva (5511999999999)"
    assert contact.phone_number == "5511999999999"
    assert contact.name == "Maria Silva"


def test_create_contact_without_name():
    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
    )

    assert str(contact) == "5511999999999"


def test_create_message():
    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
        name="Maria Silva",
    )

    message = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.test-123",
        direction=MessageDirection.INBOUND,
        message_type=MessageType.TEXT,
        status=MessageStatus.RECEIVED,
        body="Olá, tudo bem?",
    )

    assert message.contact == contact
    assert message.wamid == "wamid.test-123"
    assert message.direction == MessageDirection.INBOUND
    assert message.status == MessageStatus.RECEIVED
    assert "Inbound (Recebida) - 5511999999999: Olá, tudo bem?" in str(message)
    assert contact.messages.count() == 1


@respx.mock
def test_contact_send_text_convenience_method():
    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
        name="Maria Silva",
    )

    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "contacts": [{"input": "5511999999999", "wa_id": "5511999999999"}],
                "messages": [{"id": "wamid.contact-send-123"}],
            },
        )
    )

    client = WhatsAppClient()
    response = contact.send_text("Mensagem enviada direto pelo contato!", client=client)

    assert response.messages[0].id == "wamid.contact-send-123"
    # Verify the message was automatically saved to the DB
    saved_msg = WhatsAppMessage.objects.get(wamid="wamid.contact-send-123")
    assert saved_msg.contact == contact
    assert saved_msg.direction == MessageDirection.OUTBOUND
    assert saved_msg.body == "Mensagem enviada direto pelo contato!"
