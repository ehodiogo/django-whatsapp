from django_whatsapp.webhooks.consumers import (
    WebhookDispatcher,
    WhatsAppConsumer,
)
from django_whatsapp.webhooks.events import (
    MessageReceived,
    MessageStatusUpdated,
)


class ConsumerSpy(WhatsAppConsumer):
    def __init__(self):
        self.messages = []
        self.statuses = []

    def on_message(self, event):
        self.messages.append(event)

    def on_status(self, event):
        self.statuses.append(event)


def test_dispatch_message():
    consumer = ConsumerSpy()

    dispatcher = WebhookDispatcher(
        consumers=[consumer]
    )

    event = MessageReceived(
        raw={},
        message={
            "id": "wamid.123",
            "from": "5511999999999",
            "type": "text",
            "text": {
                "body": "Olá!"
            },
        },
        metadata={},
    )

    dispatcher.dispatch(event)

    assert len(consumer.messages) == 1
    assert consumer.messages[0] is event


def test_dispatch_status():
    consumer = ConsumerSpy()

    dispatcher = WebhookDispatcher(
        consumers=[consumer]
    )

    event = MessageStatusUpdated(
        raw={},
        status={
            "id": "wamid.123",
            "status": "read",
        },
        metadata={},
    )

    dispatcher.dispatch(event)

    assert len(consumer.statuses) == 1
    assert consumer.statuses[0] is event

def test_dispatch_to_multiple_consumers():
    consumer_a = ConsumerSpy()
    consumer_b = ConsumerSpy()

    dispatcher = WebhookDispatcher(
        consumers=[
            consumer_a,
            consumer_b,
        ]
    )

    event = MessageReceived(
        raw={},
        message={
            "id": "wamid.123",
            "from": "5511999999999",
            "type": "text",
        },
        metadata={},
    )

    dispatcher.dispatch(event)

    assert len(consumer_a.messages) == 1
    assert len(consumer_b.messages) == 1