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
    def text(self) -> str | None:
        text = self.message.get("text")

        if not text:
            return None

        return text.get("body")


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


@dataclass(frozen=True)
class UnknownWebhookEvent(WebhookEvent):
    pass