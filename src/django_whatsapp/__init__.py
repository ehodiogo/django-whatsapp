from typing import TYPE_CHECKING
from .client import WhatsAppClient

if TYPE_CHECKING:
    from .models import (
        MessageDirection,
        MessageStatus,
        MessageType,
        WhatsAppContact,
        WhatsAppMessage,
    )
    from .signals import (
        contact_created,
        contact_updated,
        message_received,
        message_sent,
        message_status_updated,
    )

__all__ = [
    "WhatsAppClient",
    "WhatsAppContact",
    "WhatsAppMessage",
    "MessageDirection",
    "MessageStatus",
    "MessageType",
    "contact_created",
    "contact_updated",
    "message_received",
    "message_sent",
    "message_status_updated",
]

__version__ = "0.1.0"


def __getattr__(name: str):
    if name in (
        "WhatsAppContact",
        "WhatsAppMessage",
        "MessageDirection",
        "MessageStatus",
        "MessageType",
    ):
        from . import models

        return getattr(models, name)
    if name in (
        "contact_created",
        "contact_updated",
        "message_received",
        "message_sent",
        "message_status_updated",
    ):
        from . import signals

        return getattr(signals, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")