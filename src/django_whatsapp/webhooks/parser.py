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
            contacts_list = value.get("contacts", [])
            contacts_by_wa_id = {
                c.get("wa_id"): c for c in contacts_list if isinstance(c, dict) and c.get("wa_id")
            }

            for message in value.get("messages", []):
                from_phone = message.get("from")
                contact_info = contacts_by_wa_id.get(from_phone) or (contacts_list[0] if contacts_list else None)
                events.append(
                    MessageReceived(
                        raw=payload,
                        message=message,
                        metadata=metadata,
                        contact=contact_info,
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