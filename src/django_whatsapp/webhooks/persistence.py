from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from django.db import transaction

from ..models import (
    MessageDirection,
    MessageStatus,
    MessageType,
    WhatsAppContact,
    WhatsAppMessage,
)
from ..phone import normalize_phone_number
from ..signals import (
    contact_created,
    contact_updated,
    message_received,
    message_status_updated,
)
from .consumers import WhatsAppConsumer
from .events import MessageReceived, MessageStatusUpdated, UnknownWebhookEvent

logger = logging.getLogger(__name__)


def _parse_timestamp(ts: Any) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    except (ValueError, TypeError, OverflowError):
        return None


def _map_message_type(raw_type: str | None) -> str:
    if not raw_type:
        return MessageType.UNKNOWN
    valid_types = {t.value for t in MessageType}
    if raw_type in valid_types:
        return raw_type
    return MessageType.UNKNOWN


def _map_status(raw_status: str | None) -> str:
    if not raw_status:
        return MessageStatus.PENDING
    status_map = {
        "sent": MessageStatus.SENT,
        "delivered": MessageStatus.DELIVERED,
        "read": MessageStatus.READ,
        "failed": MessageStatus.FAILED,
    }
    return status_map.get(raw_status.lower(), MessageStatus.PENDING)


class DatabasePersistenceConsumer(WhatsAppConsumer):
    """
    Built-in consumer that automatically persists WhatsApp contacts and messages
    to the Django database, and fires Django signals.
    """

    def on_message(self, event: MessageReceived) -> WhatsAppMessage | None:
        from_phone = event.from_phone
        if not from_phone:
            logger.warning("MessageReceived event has no from_phone. Skipping persistence.")
            return None

        try:
            normalized_phone = normalize_phone_number(from_phone)
        except Exception:
            normalized_phone = from_phone

        contact_name = event.contact_name or ""
        contact_wa_id = event.contact_wa_id or from_phone

        with transaction.atomic():
            contact, created = WhatsAppContact.objects.get_or_create(
                phone_number=normalized_phone,
                defaults={
                    "wa_id": contact_wa_id,
                    "name": contact_name,
                },
            )

            updated = False
            if not created:
                if contact_name and not contact.name:
                    contact.name = contact_name
                    updated = True
                if contact_wa_id and not contact.wa_id:
                    contact.wa_id = contact_wa_id
                    updated = True
                if updated:
                    contact.save(update_fields=["name", "wa_id", "updated_at"])

            if created:
                contact_created.send(sender=WhatsAppContact, contact=contact, created=True)
            elif updated:
                contact_updated.send(sender=WhatsAppContact, contact=contact)

            wamid = event.message_id
            mtype = _map_message_type(event.message_type)
            body = event.text or (f"[{mtype}]" if mtype != MessageType.TEXT else "")
            ts = _parse_timestamp(event.timestamp)

            message, _ = WhatsAppMessage.objects.update_or_create(
                wamid=wamid,
                defaults={
                    "contact": contact,
                    "direction": MessageDirection.INBOUND,
                    "message_type": mtype,
                    "status": MessageStatus.RECEIVED,
                    "body": body,
                    "raw_payload": event.message,
                    "timestamp": ts,
                },
            )

            message_received.send(
                sender=WhatsAppMessage,
                message=message,
                contact=contact,
                raw_event=event,
            )

            return message

    def on_status(self, event: MessageStatusUpdated) -> WhatsAppMessage | None:
        wamid = event.message_id
        if not wamid:
            return None

        raw_status = event.status_name
        new_status = _map_status(raw_status)
        ts = _parse_timestamp(event.timestamp) or datetime.now(tz=timezone.utc)

        try:
            message = WhatsAppMessage.objects.select_related("contact").get(wamid=wamid)
        except WhatsAppMessage.DoesNotExist:
            logger.debug(f"WhatsAppMessage with wamid={wamid} not found for status update.")
            return None

        old_status = message.status
        message.status = new_status

        update_fields = ["status", "updated_at"]

        if new_status == MessageStatus.SENT and not message.sent_at:
            message.sent_at = ts
            update_fields.append("sent_at")
        elif new_status == MessageStatus.DELIVERED and not message.delivered_at:
            message.delivered_at = ts
            update_fields.append("delivered_at")
        elif new_status == MessageStatus.READ and not message.read_at:
            message.read_at = ts
            update_fields.append("read_at")
        elif new_status == MessageStatus.FAILED:
            message.failed_at = ts
            message.error_data = {"errors": event.errors}
            update_fields.extend(["failed_at", "error_data"])

        message.save(update_fields=update_fields)

        message_status_updated.send(
            sender=WhatsAppMessage,
            message=message,
            status=new_status,
            previous_status=old_status,
            raw_event=event,
        )

        return message
