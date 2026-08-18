from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from .components import TemplateHeader
from .template import build_body_component
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

if TYPE_CHECKING:
    from ..conf import WhatsAppSettings

logger = logging.getLogger(__name__)


def _save_outbound_message(
    to: str,
    message_type: str,
    body: str,
    payload: dict[str, Any],
    response: SendMessageResponse,
) -> None:
    try:
        from ..models import (
            MessageDirection,
            MessageStatus,
            MessageType,
            WhatsAppContact,
            WhatsAppMessage,
        )
        from ..signals import contact_created, message_sent

        wamid = response.messages[0].id if response.messages else None
        now = datetime.now(tz=timezone.utc)

        contact, created = WhatsAppContact.objects.get_or_create(
            phone_number=to,
            defaults={"wa_id": to},
        )
        if created:
            contact_created.send(sender=WhatsAppContact, contact=contact, created=True)

        mtype = message_type if message_type in {t.value for t in MessageType} else MessageType.UNKNOWN

        msg = WhatsAppMessage.objects.create(
            contact=contact,
            wamid=wamid,
            direction=MessageDirection.OUTBOUND,
            message_type=mtype,
            status=MessageStatus.SENT,
            body=body,
            raw_payload=payload,
            sent_at=now,
            timestamp=now,
        )

        message_sent.send(
            sender=WhatsAppMessage,
            message=msg,
            contact=contact,
        )
    except Exception as e:
        logger.warning(f"Failed to auto-save outbound WhatsApp message: {e}")


class MessagesClient:
    def __init__(
        self,
        http: MetaAPIClient,
        messages_url: str,
        config: WhatsAppSettings | None = None,
    ):
        self.http = http
        self.messages_url = messages_url
        self.config = config

    def _should_auto_save(self, auto_save_param: bool | None) -> bool:
        if auto_save_param is not None:
            return auto_save_param
        if self.config is not None:
            return self.config.auto_save
        return True

    def send_text(
        self,
        to: str,
        text: str,
        *,
        auto_save: bool | None = None,
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

        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="text",
                body=text,
                payload=payload,
                response=response,
            )

        return response

    def send_template(
        self,
        to: str,
        name: str,
        language: str = "pt_BR",
        *,
        body_parameters: list[str] | None = None,
        header: TemplateHeader | None = None,
        auto_save: bool | None = None,
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

        payload: dict[str, Any] = {
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

        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            template_desc = f"[Template: {name}]"
            if body_parameters:
                template_desc += f" params: {', '.join(body_parameters)}"
            _save_outbound_message(
                to=to,
                message_type="template",
                body=template_desc,
                payload=payload,
                response=response,
            )

        return response