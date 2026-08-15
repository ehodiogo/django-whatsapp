from django_whatsapp.schemas import (
    MessageResponse,
    SendMessageResponse,
    parse_send_message_response,
)


def test_parse_send_message_response():
    data = {
        "messaging_product": "whatsapp",
        "messages": [
            {
                "id": "wamid.123",
            }
        ],
    }

    result = parse_send_message_response(data)

    assert isinstance(result, SendMessageResponse)
    assert result.messaging_product == "whatsapp"
    assert result.messages == (
        MessageResponse(id="wamid.123"),
    )