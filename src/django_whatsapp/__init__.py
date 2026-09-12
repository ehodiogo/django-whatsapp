from typing import TYPE_CHECKING
from .client import WhatsAppClient

if TYPE_CHECKING:
    from .media.client import MediaClient
    from .models import (
        MessageDirection,
        MessageStatus,
        MessageType,
        WhatsAppContact,
        WhatsAppMessage,
    )
    from .router import WhatsAppContext, WhatsAppRouter, bot, router
    from .signals import (
        contact_created,
        contact_updated,
        message_received,
        message_sent,
        message_status_updated,
    )

__all__ = [
    "WhatsAppClient",
    "MediaClient",
    "WhatsAppContact",
    "WhatsAppMessage",
    "MessageDirection",
    "MessageStatus",
    "MessageType",
    "WhatsAppRouter",
    "WhatsAppContext",
    "bot",
    "router",
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
    if name in ("WhatsAppRouter", "WhatsAppContext", "bot", "router"):
        from . import router

        return getattr(router, name)
    if name == "MediaClient":
        from .media.client import MediaClient

        return MediaClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")