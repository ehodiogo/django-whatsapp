from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TemplateHeader:
    type: str
    value: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "type": "header",
            "parameters": [
                {
                    "type": self.type,
                    self.type: {
                        "link": self.value,
                    },
                }
            ],
        }

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