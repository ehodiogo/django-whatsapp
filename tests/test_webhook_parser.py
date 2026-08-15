from django_whatsapp.webhooks.events import (
    MessageReceived,
    MessageStatusUpdated,
    UnknownWebhookEvent,
)
from django_whatsapp.webhooks.parser import parse_webhook


def test_parse_text_message():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "waba-123",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "metadata": {
                                "display_phone_number": "15550000000",
                                "phone_number_id": "phone-123",
                            },
                            "messages": [
                                {
                                    "from": "5511999999999",
                                    "id": "wamid.received-123",
                                    "timestamp": "1750000000",
                                    "type": "text",
                                    "text": {
                                        "body": "Olá!"
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    events = parse_webhook(payload)

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, MessageReceived)
    assert event.message_id == "wamid.received-123"
    assert event.from_phone == "5511999999999"
    assert event.message_type == "text"
    assert event.text == "Olá!"
    assert event.metadata["phone_number_id"] == "phone-123"


def test_parse_status_update():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "metadata": {
                                "phone_number_id": "phone-123",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.sent-123",
                                    "status": "delivered",
                                    "timestamp": "1750000000",
                                    "recipient_id": "5511999999999",
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    events = parse_webhook(payload)

    assert len(events) == 1

    event = events[0]

    assert isinstance(event, MessageStatusUpdated)
    assert event.message_id == "wamid.sent-123"
    assert event.status_name == "delivered"


def test_unknown_webhook():
    payload = {
        "object": "whatsapp_business_account",
        "entry": [],
    }

    events = parse_webhook(payload)

    assert len(events) == 1
    assert isinstance(events[0], UnknownWebhookEvent)

def test_parse_multiple_messages():
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "metadata": {
                                "phone_number_id": "phone-123",
                            },
                            "messages": [
                                {
                                    "id": "wamid.1",
                                    "from": "5511111111111",
                                    "type": "text",
                                    "text": {
                                        "body": "Primeira"
                                    },
                                },
                                {
                                    "id": "wamid.2",
                                    "from": "5522222222222",
                                    "type": "text",
                                    "text": {
                                        "body": "Segunda"
                                    },
                                },
                            ],
                        }
                    }
                ]
            }
        ]
    }

    events = parse_webhook(payload)

    assert len(events) == 2

    assert events[0].message_id == "wamid.1"
    assert events[0].text == "Primeira"

    assert events[1].message_id == "wamid.2"
    assert events[1].text == "Segunda"