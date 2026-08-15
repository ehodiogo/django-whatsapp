from __future__ import annotations
from .template import build_body_component
from typing import Any

from ..http import MetaAPIClient
from ..phone import normalize_phone_number
from ..schemas import (
    SendMessageResponse,
    parse_send_message_response,
)
from ..validators import (
    InvalidMessageError,
    validate_text,
)
from .components import TemplateHeader

class MessagesClient:
    def __init__(
        self,
        http: MetaAPIClient,
        messages_url: str,
    ):
        self.http = http
        self.messages_url = messages_url

    def send_text(
        self,
        to: str,
        text: str,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        text = validate_text(text)

        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": text,
            },
        }

        data = self.http.post(
            self.messages_url,
            payload,
        )

        return parse_send_message_response(data)

    def send_template(
            self,
            to: str,
            name: str,
            language: str = "pt_BR",
            *,
            body_parameters: list[str] | None = None,
            header: TemplateHeader | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)

        if not name.strip():
            raise InvalidMessageError(
                "Template name cannot be empty."
            )

        if not language.strip():
            raise InvalidMessageError(
                "Template language cannot be empty."
            )

        components = []

        if header is not None:
            components.append(
                header.to_payload()
            )

        if body_parameters:
            components.append(
                build_body_component(body_parameters)
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": name,
                "language": {
                    "code": language,
                },
            },
        }

        if components:
            payload["template"]["components"] = components

        data = self.http.post(
            self.messages_url,
            payload,
        )

        return parse_send_message_response(data)