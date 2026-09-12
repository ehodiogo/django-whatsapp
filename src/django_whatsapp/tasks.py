from __future__ import annotations

import logging
from typing import Any

from .conf import WhatsAppSettings
from .webhooks.consumers import WebhookDispatcher
from .webhooks.parser import parse_webhook
from .webhooks.persistence import DatabasePersistenceConsumer
from .webhooks.registry import load_consumers

logger = logging.getLogger(__name__)


def process_webhook_payload(payload: dict[str, Any]) -> int:
    """
    Synchronously process a parsed webhook payload.
    """
    config = WhatsAppSettings.from_django()
    events = parse_webhook(payload)

    consumers = list(
        load_consumers(
            config.webhook.consumers if config.webhook else ()
        )
    )

    if config.auto_save:
        if not any(isinstance(c, DatabasePersistenceConsumer) for c in consumers):
            consumers.insert(0, DatabasePersistenceConsumer())

    # Include default bot router if it has any registered handlers
    from .router import RouterConsumer, bot

    if (
        bot._text_handlers
        or bot._button_handlers
        or bot._list_handlers
        or bot._media_handlers
        or bot._catch_all_handlers
        or bot._status_handlers
    ):
        if not any(isinstance(c, RouterConsumer) for c in consumers):
            consumers.append(RouterConsumer(bot))

    dispatcher = WebhookDispatcher(
        consumers=consumers,
    )

    for event in events:
        dispatcher.dispatch(event)

    return len(events)


try:
    from celery import shared_task

    @shared_task(name="django_whatsapp.process_webhook_payload")
    def process_webhook_payload_task(payload: dict[str, Any]) -> int:
        return process_webhook_payload(payload)

except ImportError:
    shared_task = None  # type: ignore
    process_webhook_payload_task = None  # type: ignore
