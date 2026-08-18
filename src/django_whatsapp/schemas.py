from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContactResponse:
    input: str
    wa_id: str


@dataclass(frozen=True)
class MessageResponse:
    id: str


@dataclass(frozen=True)
class SendMessageResponse:
    messaging_product: str
    messages: tuple[MessageResponse, ...]
    contacts: tuple[ContactResponse, ...] = ()


def parse_send_message_response(
    data: dict,
) -> SendMessageResponse:
    messages = tuple(
        MessageResponse(
            id=item["id"],
        )
        for item in data.get("messages", [])
    )

    contacts = tuple(
        ContactResponse(
            input=item.get("input", ""),
            wa_id=item.get("wa_id", ""),
        )
        for item in data.get("contacts", [])
    )

    return SendMessageResponse(
        messaging_product=data.get(
            "messaging_product",
            "whatsapp",
        ),
        messages=messages,
        contacts=contacts,
    )