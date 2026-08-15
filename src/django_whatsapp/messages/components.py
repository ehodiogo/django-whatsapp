from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..exceptions import WhatsAppError


class InvalidTemplateComponentError(WhatsAppError):
    """Raised when a template component is invalid."""


@dataclass(frozen=True)
class TemplateHeader:
    type: str
    value: str

    ALLOWED_TYPES = {
        "text",
        "image",
        "video",
        "document",
    }

    def __post_init__(self) -> None:
        if self.type not in self.ALLOWED_TYPES:
            raise InvalidTemplateComponentError(
                f"Unsupported template header type: {self.type}"
            )

        if not isinstance(self.value, str):
            raise InvalidTemplateComponentError(
                "Template header value must be a string."
            )

        if not self.value.strip():
            raise InvalidTemplateComponentError(
                "Template header value cannot be empty."
            )

    def to_payload(self) -> dict[str, Any]:
        if self.type == "text":
            parameter = {
                "type": "text",
                "text": self.value,
            }
        else:
            parameter = {
                "type": self.type,
                self.type: {
                    "link": self.value,
                },
            }

        return {
            "type": "header",
            "parameters": [parameter],
        }

    @classmethod
    def text(cls, value: str) -> "TemplateHeader":
        return cls(
            type="text",
            value=value,
        )

    @classmethod
    def image(cls, url: str) -> "TemplateHeader":
        return cls(
            type="image",
            value=url,
        )

    @classmethod
    def video(cls, url: str) -> "TemplateHeader":
        return cls(
            type="video",
            value=url,
        )

    @classmethod
    def document(cls, url: str) -> "TemplateHeader":
        return cls(
            type="document",
            value=url,
        )