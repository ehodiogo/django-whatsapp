from django_whatsapp.webhooks.events import MessageReceived


def test_message_received_properties():
    event = MessageReceived(
        raw={},
        message={
            "id": "wamid.123",
            "from": "5511999999999",
            "type": "text",
            "text": {
                "body": "Olá Django!"
            },
        },
        metadata={
            "phone_number_id": "123456",
        },
    )

    assert event.message_id == "wamid.123"
    assert event.from_phone == "5511999999999"
    assert event.message_type == "text"
    assert event.text == "Olá Django!"


def test_non_text_message_has_no_text():
    event = MessageReceived(
        raw={},
        message={
            "id": "wamid.image",
            "from": "5511999999999",
            "type": "image",
            "image": {
                "id": "media-123",
            },
        },
        metadata={},
    )

    assert event.message_type == "image"
    assert event.text is None