import json

import pytest
import respx

from httpx import Response

from django_whatsapp import WhatsAppClient
from django_whatsapp.validators import InvalidMessageError
from django_whatsapp.messages.components import TemplateHeader

@respx.mock
def test_send_template():
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
                        "id": "wamid.template-123",
                    }
                ],
            },
        )
    )

    client = WhatsAppClient()

    result = client.messages.send_template(
        to="5511999999999",
        name="hello_world",
        language="en_US",
    )

    assert route.called
    assert result.messages[0].id == "wamid.template-123"

    payload = json.loads(
        route.calls.last.request.content
    )

    assert payload == {
        "messaging_product": "whatsapp",
        "to": "5511999999999",
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {
                "code": "en_US",
            },
        },
    }


@respx.mock
def test_send_template_with_body_parameters():
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
                        "id": "wamid.template-456",
                    }
                ],
            },
        )
    )

    client = WhatsAppClient()

    result = client.messages.send_template(
        to="+55 (11) 99999-9999",
        name="pedido_confirmado",
        language="pt_BR",
        body_parameters=[
            "12345",
            "R$ 149,90",
        ],
    )

    assert result.messages[0].id == "wamid.template-456"

    payload = json.loads(
        route.calls.last.request.content
    )

    assert payload == {
        "messaging_product": "whatsapp",
        "to": "5511999999999",
        "type": "template",
        "template": {
            "name": "pedido_confirmado",
            "language": {
                "code": "pt_BR",
            },
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": "12345",
                        },
                        {
                            "type": "text",
                            "text": "R$ 149,90",
                        },
                    ],
                },
            ],
        },
    }


def test_template_name_cannot_be_empty():
    client = WhatsAppClient()

    with pytest.raises(InvalidMessageError):
        client.messages.send_template(
            to="5511999999999",
            name="",
            language="pt_BR",
        )


def test_template_language_cannot_be_empty():
    client = WhatsAppClient()

    with pytest.raises(InvalidMessageError):
        client.messages.send_template(
            to="5511999999999",
            name="hello_world",
            language="",
        )

@respx.mock
def test_send_template_with_image_header():
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
                        "id": "wamid.template-image",
                    }
                ],
            },
        )
    )

    client = WhatsAppClient()

    result = client.messages.send_template(
        to="5511999999999",
        name="pedido",
        language="pt_BR",
        header=TemplateHeader.image(
            "https://example.com/pedido.jpg"
        ),
    )

    assert result.messages[0].id == "wamid.template-image"

    payload = json.loads(
        route.calls.last.request.content
    )

    assert payload["template"]["components"] == [
        {
            "type": "header",
            "parameters": [
                {
                    "type": "image",
                    "image": {
                        "link": "https://example.com/pedido.jpg",
                    },
                }
            ],
        }
    ]

@respx.mock
def test_send_template_with_text_header():
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
                        "id": "wamid.template-text-header",
                    }
                ],
            },
        )
    )

    client = WhatsAppClient()

    result = client.messages.send_template(
        to="5511999999999",
        name="pedido",
        language="pt_BR",
        header=TemplateHeader.text(
            "Pedido #12345"
        ),
    )

    assert result.messages[0].id == (
        "wamid.template-text-header"
    )

    payload = json.loads(
        route.calls.last.request.content
    )

    assert payload["template"]["components"] == [
        {
            "type": "header",
            "parameters": [
                {
                    "type": "text",
                    "text": "Pedido #12345",
                }
            ],
        }
    ]