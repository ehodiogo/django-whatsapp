import httpx
import pytest
import respx
from django_whatsapp.router import WhatsAppRouter, WhatsAppContext
from django_whatsapp.webhooks.events import MessageReceived, MessageStatusUpdated
from django_whatsapp.models import WhatsAppContact

pytestmark = pytest.mark.django_db


def test_router_text_exact_and_pattern():
    router = WhatsAppRouter()
    handled = []

    @router.on_text(["oi", "olá", "menu"])
    def handle_greeting(ctx: WhatsAppContext):
        handled.append(("greeting", ctx.text, ctx.from_phone))

    @router.on_text(r"^pedido\s+(\d+)$")
    def handle_order(ctx: WhatsAppContext):
        handled.append(("order", ctx.text))

    # Trigger greeting
    event_hi = MessageReceived(
        raw={},
        message={"id": "m1", "from": "5511999999999", "type": "text", "text": {"body": "Olá"}},
        metadata={},
    )
    router.handle_message(event_hi)
    assert len(handled) == 1
    assert handled[0] == ("greeting", "Olá", "5511999999999")

    # Trigger order pattern
    event_order = MessageReceived(
        raw={},
        message={"id": "m2", "from": "5511999999999", "type": "text", "text": {"body": "pedido 12345"}},
        metadata={},
    )
    router.handle_message(event_order)
    assert len(handled) == 2
    assert handled[1] == ("order", "pedido 12345")


def test_router_button_and_list_handlers():
    router = WhatsAppRouter()
    handled = []

    @router.on_button("btn_suporte")
    def on_suporte(ctx: WhatsAppContext):
        handled.append(("button", ctx.button_id))

    @router.on_list("prod_1")
    def on_prod(ctx: WhatsAppContext):
        handled.append(("list", ctx.list_id))

    # Button event
    btn_event = MessageReceived(
        raw={},
        message={
            "id": "m3",
            "from": "5511999999999",
            "type": "interactive",
            "interactive": {
                "type": "button_reply",
                "button_reply": {"id": "btn_suporte", "title": "Suporte"},
            },
        },
        metadata={},
    )
    router.handle_message(btn_event)
    assert len(handled) == 1
    assert handled[0] == ("button", "btn_suporte")

    # List event
    list_event = MessageReceived(
        raw={},
        message={
            "id": "m4",
            "from": "5511999999999",
            "type": "interactive",
            "interactive": {
                "type": "list_reply",
                "list_reply": {"id": "prod_1", "title": "Café"},
            },
        },
        metadata={},
    )
    router.handle_message(list_event)
    assert len(handled) == 2
    assert handled[1] == ("list", "prod_1")


@respx.mock
def test_context_reply_helpers():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"messaging_product": "whatsapp", "messages": [{"id": "wamid.reply-1"}]},
        )
    )

    router = WhatsAppRouter()

    @router.on_text
    def auto_reply(ctx: WhatsAppContext):
        ctx.mark_as_read()
        ctx.reply_text("Resposta automática")
        ctx.reply_buttons("Escolha:", buttons=[{"id": "b1", "title": "Opção 1"}])

    event = MessageReceived(
        raw={},
        message={"id": "m5", "from": "5511999999999", "type": "text", "text": {"body": "qualquer coisa"}},
        metadata={},
    )
    router.handle_message(event)

    assert route.call_count == 3  # mark_as_read, reply_text, reply_buttons
