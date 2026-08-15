from __future__ import annotations

from typing import Any

from .events import (
    MessageReceived,
    MessageStatusUpdated,
    UnknownWebhookEvent,
)


def parse_webhook(
    payload: dict[str, Any],
):
    events = []

    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            metadata = value.get("metadata", {})

            for message in value.get("messages", []):
                events.append(
                    MessageReceived(
                        raw=payload,
                        message=message,
                        metadata=metadata,
                    )
                )

            for status in value.get("statuses", []):
                events.append(
                    MessageStatusUpdated(
                        raw=payload,
                        status=status,
                        metadata=metadata,
                    )
                )

    if not events:
        events.append(
            UnknownWebhookEvent(
                raw=payload,
            )
        )

    return events