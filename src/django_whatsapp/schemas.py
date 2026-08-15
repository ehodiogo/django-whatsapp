from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MessageResponse:
    id: str


@dataclass(frozen=True)
class SendMessageResponse:
    messaging_product: str
    messages: tuple[MessageResponse, ...]

def parse_send_message_response(
    data: dict,
) -> SendMessageResponse:
    messages = tuple(
        MessageResponse(
            id=item["id"],
        )
        for item in data.get("messages", [])
    )

    return SendMessageResponse(
        messaging_product=data.get(
            "messaging_product",
            "whatsapp",
        ),
        messages=messages,
    )