import json
import httpx
import pytest
import respx
from django_whatsapp.client import WhatsAppClient
from django_whatsapp.models import WhatsAppContact, WhatsAppMessage
from django_whatsapp.validators import InvalidMessageError

pytestmark = pytest.mark.django_db


@respx.mock
def test_send_buttons():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "messages": [{"id": "wamid.btn-123"}],
                "contacts": [{"input": "5511999999999", "wa_id": "5511999999999"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_buttons(
        to="5511999999999",
        text="Escolha uma opção:",
        buttons=[
            {"id": "btn_1", "title": "Suporte"},
            {"id": "btn_2", "title": "Vendas"},
        ],
        header="Menu",
        footer="Selecione abaixo",
    )

    assert response.messages[0].id == "wamid.btn-123"
    sent_json = route.calls.last.request.read().decode()
    assert "btn_1" in sent_json
    assert "Suporte" in sent_json
    assert "Menu" in sent_json
    assert "Selecione abaixo" in sent_json

    # Test auto-saved message in DB
    msg = WhatsAppMessage.objects.get(wamid="wamid.btn-123")
    assert msg.message_type == "interactive"
    assert "Suporte, Vendas" in msg.body


def test_send_buttons_validation():
    client = WhatsAppClient()
    with pytest.raises(InvalidMessageError):
        client.messages.send_buttons(to="5511999999999", text="Olá", buttons=[])

    with pytest.raises(InvalidMessageError):
        client.messages.send_buttons(
            to="5511999999999",
            text="Olá",
            buttons=[
                {"id": "1", "title": "1"},
                {"id": "2", "title": "2"},
                {"id": "3", "title": "3"},
                {"id": "4", "title": "4"},
            ],
        )


@respx.mock
def test_send_list():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "messages": [{"id": "wamid.list-123"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_list(
        to="5511999999999",
        text="Escolha seu produto",
        button_text="Ver Produtos",
        sections=[
            {
                "title": "Bebidas",
                "rows": [
                    {"id": "prod_1", "title": "Café", "description": "Café expresso"},
                ],
            }
        ],
    )

    assert response.messages[0].id == "wamid.list-123"
    sent_json = route.calls.last.request.read().decode()
    assert "Ver Produtos" in sent_json
    assert "Bebidas" in sent_json
    assert "prod_1" in sent_json


@respx.mock
def test_send_location():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "messages": [{"id": "wamid.loc-123"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_location(
        to="5511999999999",
        latitude=-23.550520,
        longitude=-46.633308,
        name="Praça da Sé",
        address="São Paulo - SP",
    )

    assert response.messages[0].id == "wamid.loc-123"
    sent_json = route.calls.last.request.read().decode()
    assert "-23.55052" in sent_json
    assert "Praça da Sé" in sent_json


@respx.mock
def test_send_reaction():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={
                "messaging_product": "whatsapp",
                "messages": [{"id": "wamid.react-123"}],
            },
        )
    )

    client = WhatsAppClient()
    response = client.messages.send_reaction(
        to="5511999999999",
        message_id="wamid.orig-123",
        emoji="👍",
    )

    assert response.messages[0].id == "wamid.react-123"
    sent_json = route.calls.last.request.read().decode()
    assert "wamid.orig-123" in sent_json
    assert "👍" in sent_json


@respx.mock
def test_mark_as_read():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"success": True},
        )
    )

    client = WhatsAppClient()
    data = client.messages.mark_as_read("wamid.incoming-999")
    assert data["success"] is True

    sent_data = json.loads(route.calls.last.request.read().decode())
    assert sent_data["status"] == "read"
    assert sent_data["message_id"] == "wamid.incoming-999"


@respx.mock
def test_model_mark_as_read_helper():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"success": True},
        )
    )

    contact = WhatsAppContact.objects.create(phone_number="5511999999999")
    msg = WhatsAppMessage.objects.create(
        contact=contact,
        wamid="wamid.model-read-test",
        direction="inbound",
    )

    res = msg.mark_as_read()
    assert res["success"] is True
