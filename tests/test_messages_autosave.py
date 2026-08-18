import httpx
import pytest
import respx
from django_whatsapp.client import WhatsAppClient
from django_whatsapp.models import (
    MessageDirection,
    MessageStatus,
    MessageType,
    WhatsAppContact,
    WhatsAppMessage,
)

pytestmark = pytest.mark.django_db


@respx.mock
def test_send_text_autosaves_contact_and_message():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "contacts": [{"input": "5511999999999", "wa_id": "5511999999999"}],
                "messages": [{"id": "wamid.autosave-text-1"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_text(
        to="+55 (11) 99999-9999",
        text="Olá do sistema!",
    )

    assert response.messages[0].id == "wamid.autosave-text-1"

    # Verify contact was automatically created
    contact = WhatsAppContact.objects.get(phone_number="5511999999999")
    assert contact.wa_id == "5511999999999"

    # Verify message was automatically saved
    message = WhatsAppMessage.objects.get(wamid="wamid.autosave-text-1")
    assert message.contact == contact
    assert message.direction == MessageDirection.OUTBOUND
    assert message.message_type == MessageType.TEXT
    assert message.status == MessageStatus.SENT
    assert message.body == "Olá do sistema!"
    assert message.sent_at is not None


@respx.mock
def test_send_template_autosaves_message():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "contacts": [{"input": "5511988887777", "wa_id": "5511988887777"}],
                "messages": [{"id": "wamid.autosave-template-1"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_template(
        to="5511988887777",
        name="verification_code",
        language="pt_BR",
        body_parameters=["123456"],
    )

    assert response.messages[0].id == "wamid.autosave-template-1"

    message = WhatsAppMessage.objects.get(wamid="wamid.autosave-template-1")
    assert message.contact.phone_number == "5511988887777"
    assert message.direction == MessageDirection.OUTBOUND
    assert message.message_type == MessageType.TEMPLATE
    assert "[Template: verification_code]" in message.body
    assert "123456" in message.body


@respx.mock
def test_send_text_with_autosave_false():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "contacts": [{"input": "5511911112222", "wa_id": "5511911112222"}],
                "messages": [{"id": "wamid.no-save-1"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_text(
        to="5511911112222",
        text="Não salvar no banco",
        auto_save=False,
    )

    assert response.messages[0].id == "wamid.no-save-1"
    assert not WhatsAppMessage.objects.filter(wamid="wamid.no-save-1").exists()
    assert not WhatsAppContact.objects.filter(phone_number="5511911112222").exists()
