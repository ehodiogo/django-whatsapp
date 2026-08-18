from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WebhookEvent:
    raw: dict[str, Any]


@dataclass(frozen=True)
class MessageReceived(WebhookEvent):
    message: dict[str, Any]
    metadata: dict[str, Any]
    contact: dict[str, Any] | None = None

    @property
    def message_id(self) -> str | None:
        return self.message.get("id")

    @property
    def message_type(self) -> str | None:
        return self.message.get("type")

    @property
    def from_phone(self) -> str | None:
        return self.message.get("from")

    @property
    def contact_name(self) -> str | None:
        if self.contact and isinstance(self.contact.get("profile"), dict):
            return self.contact["profile"].get("name")
        return None

    @property
    def contact_wa_id(self) -> str | None:
        if self.contact:
            return self.contact.get("wa_id")
        return None

    @property
    def timestamp(self) -> str | None:
        return self.message.get("timestamp")

    @property
    def text(self) -> str | None:
        mtype = self.message_type
        if mtype == "text":
            text_data = self.message.get("text")
            if isinstance(text_data, dict):
                return text_data.get("body")
        elif mtype == "interactive":
            interactive = self.message.get("interactive", {})
            itype = interactive.get("type")
            if itype == "button_reply":
                return interactive.get("button_reply", {}).get("title")
            elif itype == "list_reply":
                return interactive.get("list_reply", {}).get("title")
        elif mtype == "button":
            btn = self.message.get("button", {})
            return btn.get("text")
        elif mtype == "reaction":
            reaction = self.message.get("reaction", {})
            return reaction.get("emoji")
        elif mtype in ("image", "video", "audio", "document", "sticker"):
            media_data = self.message.get(mtype, {})
            if isinstance(media_data, dict):
                return media_data.get("caption")
        return None


@dataclass(frozen=True)
class MessageStatusUpdated(WebhookEvent):
    status: dict[str, Any]
    metadata: dict[str, Any]

    @property
    def message_id(self) -> str | None:
        return self.status.get("id")

    @property
    def status_name(self) -> str | None:
        return self.status.get("status")

    @property
    def recipient_id(self) -> str | None:
        return self.status.get("recipient_id")

    @property
    def timestamp(self) -> str | None:
        return self.status.get("timestamp")

    @property
    def errors(self) -> list[dict[str, Any]]:
        return self.status.get("errors", [])


@dataclass(frozen=True)
class UnknownWebhookEvent(WebhookEvent):
    pass