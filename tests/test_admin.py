import pytest
from django.contrib.admin.sites import AdminSite
from django_whatsapp.admin import (
    WhatsAppContactAdmin,
    WhatsAppMessageAdmin,
    WhatsAppMessageInline,
)
from django_whatsapp.models import (
    MessageDirection,
    MessageStatus,
    MessageType,
    WhatsAppContact,
    WhatsAppMessage,
)

pytestmark = pytest.mark.django_db


class DummyAdminSite(AdminSite):
    pass


def test_contact_admin_helpers():
    site = DummyAdminSite()
    admin = WhatsAppContactAdmin(WhatsAppContact, site)

    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
        name="Teste Admin",
    )
    WhatsAppMessage.objects.create(
        contact=contact,
        direction=MessageDirection.INBOUND,
        status=MessageStatus.RECEIVED,
        body="Msg 1",
    )
    WhatsAppMessage.objects.create(
        contact=contact,
        direction=MessageDirection.OUTBOUND,
        status=MessageStatus.SENT,
        body="Msg 2",
    )

    assert admin.messages_count(contact) == 2


def test_message_admin_helpers_and_badges():
    site = DummyAdminSite()
    admin = WhatsAppMessageAdmin(WhatsAppMessage, site)

    contact = WhatsAppContact.objects.create(
        phone_number="5511999999999",
        name="Contato Teste",
    )
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.admin-1",
        direction=MessageDirection.INBOUND,
        message_type=MessageType.TEXT,
        status=MessageStatus.READ,
        body="Texto da mensagem para teste no admin",
        raw_payload={"test": 123},
        error_data={"error": "none"},
    )

    assert "Contato Teste" in admin.contact_link(msg)
    assert "Texto da mensagem" in admin.body_snippet(msg)

    direction_badge = admin.direction_badge(msg)
    assert "Recebida (In)" in str(direction_badge)

    status_badge = admin.status_badge(msg)
    assert "Lida" in str(status_badge)

    raw_payload_html = admin.raw_payload_formatted(msg)
    assert "123" in str(raw_payload_html)

    error_data_html = admin.error_data_formatted(msg)
    assert "none" in str(error_data_html)


def test_message_inline_body_preview():
    contact = WhatsAppContact.objects.create(phone_number="5511999999999")
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        direction=MessageDirection.INBOUND,
        body="Mensagem curta",
    )

    inline = WhatsAppMessageInline(WhatsAppContact, DummyAdminSite())
    preview = inline.body_preview(msg)
    assert preview == "Mensagem curta"
