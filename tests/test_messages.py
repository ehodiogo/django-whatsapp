import respx
from httpx import Response

from django_whatsapp import WhatsAppClient


@respx.mock
def test_messages_client_send_text():
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
                        "id": "wamid.messages-client",
                    }
                ],
            },
        ),
    )

    client = WhatsAppClient()

    response = client.messages.send_text(
        to="+55 (11) 99999-9999",
        text="Olá!",
    )

    assert route.called
    assert response.messages[0].id == "wamid.messages-client"