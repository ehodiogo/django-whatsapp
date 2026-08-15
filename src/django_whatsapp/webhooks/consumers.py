from __future__ import annotations

from .events import (
    MessageReceived,
    MessageStatusUpdated,
    UnknownWebhookEvent,
)


class WhatsAppConsumer:

    def consume(self, event):

        if isinstance(event, MessageReceived):
            return self.on_message(event)

        if isinstance(event, MessageStatusUpdated):
            return self.on_status(event)

        if isinstance(event, UnknownWebhookEvent):
            return self.on_unknown(event)

    def on_message(self, event: MessageReceived):
        pass

    def on_status(self, event: MessageStatusUpdated):
        pass

    def on_unknown(self, event: UnknownWebhookEvent):
        pass

class MessageConsumer(WhatsAppConsumer):

    def on_message(self, event):
        if event.message_type == "text":
            return self.on_text(event)

        return self.on_unsupported(event)

    def on_text(self, event):
        pass

    def on_unsupported(self, event):
        pass

class WebhookDispatcher:

    def __init__(self, consumers=None):
        self.consumers = consumers or []

    def dispatch(self, event):
        results = []

        for consumer in self.consumers:
            result = consumer.consume(event)

            if result is not None:
                results.append(result)

        return results