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


def _build_media_object(media: str, caption: str | None = None, filename: str | None = None) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    if media.startswith("http://") or media.startswith("https://"):
        obj["link"] = media
    else:
        obj["id"] = media

    if caption:
        obj["caption"] = caption
    if filename:
        obj["filename"] = filename
    return obj


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

    def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """
        Mark an incoming message as read (blue double checkmarks in WhatsApp).
        """
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        return self.http.post(self.messages_url, payload)

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
            raise InvalidMessageError("Template name cannot be empty.")
        if not language.strip():
            raise InvalidMessageError("Template language cannot be empty.")

        components = []
        if header is not None:
            components.append(header.to_payload())
        if body_parameters:
            components.append(build_body_component(body_parameters))

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

    def send_reaction(
        self,
        to: str,
        message_id: str,
        emoji: str,
        *,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "reaction",
            "reaction": {
                "message_id": message_id,
                "emoji": emoji,
            },
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="reaction",
                body=emoji,
                payload=payload,
                response=response,
            )
        return response

    def send_buttons(
        self,
        to: str,
        text: str,
        buttons: list[dict[str, str]],
        *,
        header: str | None = None,
        footer: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        """
        Send interactive reply buttons (up to 3 buttons).
        Each button dict should have 'id' and 'title'.
        """
        to = normalize_phone_number(to)
        if not buttons or len(buttons) > 3:
            raise InvalidMessageError("Buttons message must have between 1 and 3 buttons.")

        formatted_buttons = []
        for btn in buttons:
            btn_id = btn.get("id", "").strip()
            btn_title = btn.get("title", "").strip()
            if not btn_id or not btn_title:
                raise InvalidMessageError("Each button must have non-empty 'id' and 'title'.")
            formatted_buttons.append({
                "type": "reply",
                "reply": {
                    "id": btn_id,
                    "title": btn_title[:20],
                },
            })

        interactive: dict[str, Any] = {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": formatted_buttons},
        }

        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": interactive,
        }

        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            btn_titles = [b.get("title", "") for b in buttons]
            summary = f"{text} [Buttons: {', '.join(btn_titles)}]"
            _save_outbound_message(
                to=to,
                message_type="interactive",
                body=summary,
                payload=payload,
                response=response,
            )
        return response

    def send_list(
        self,
        to: str,
        text: str,
        button_text: str,
        sections: list[dict[str, Any]],
        *,
        header: str | None = None,
        footer: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        """
        Send interactive list message (dropdown menu).
        """
        to = normalize_phone_number(to)
        if not sections:
            raise InvalidMessageError("List message must have at least one section.")

        interactive: dict[str, Any] = {
            "type": "list",
            "body": {"text": text},
            "action": {
                "button": button_text[:20],
                "sections": sections,
            },
        }

        if header:
            interactive["header"] = {"type": "text", "text": header}
        if footer:
            interactive["footer"] = {"text": footer}

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": interactive,
        }

        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="interactive",
                body=f"[List: {button_text}] {text}",
                payload=payload,
                response=response,
            )
        return response

    def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        *,
        name: str | None = None,
        address: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        loc_data: dict[str, Any] = {
            "latitude": str(latitude),
            "longitude": str(longitude),
        }
        if name:
            loc_data["name"] = name
        if address:
            loc_data["address"] = address

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "location",
            "location": loc_data,
        }

        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            desc = f"[Location] {name or f'{latitude}, {longitude}'}"
            _save_outbound_message(
                to=to,
                message_type="location",
                body=desc,
                payload=payload,
                response=response,
            )
        return response

    def send_image(
        self,
        to: str,
        media: str,
        *,
        caption: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "image",
            "image": _build_media_object(media, caption=caption),
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="image",
                body=caption or "[Image]",
                payload=payload,
                response=response,
            )
        return response

    def send_document(
        self,
        to: str,
        media: str,
        *,
        filename: str | None = None,
        caption: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "document",
            "document": _build_media_object(media, caption=caption, filename=filename),
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="document",
                body=caption or (f"[Document: {filename}]" if filename else "[Document]"),
                payload=payload,
                response=response,
            )
        return response

    def send_audio(
        self,
        to: str,
        media: str,
        *,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "audio",
            "audio": _build_media_object(media),
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="audio",
                body="[Audio]",
                payload=payload,
                response=response,
            )
        return response

    def send_video(
        self,
        to: str,
        media: str,
        *,
        caption: str | None = None,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "video",
            "video": _build_media_object(media, caption=caption),
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="video",
                body=caption or "[Video]",
                payload=payload,
                response=response,
            )
        return response

    def send_sticker(
        self,
        to: str,
        media: str,
        *,
        auto_save: bool | None = None,
    ) -> SendMessageResponse:
        to = normalize_phone_number(to)
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "sticker",
            "sticker": _build_media_object(media),
        }
        data = self.http.post(self.messages_url, payload)
        response = parse_send_message_response(data)

        if self._should_auto_save(auto_save):
            _save_outbound_message(
                to=to,
                message_type="sticker",
                body="[Sticker]",
                payload=payload,
                response=response,
            )
        return response