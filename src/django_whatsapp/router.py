from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Callable, Pattern, Sequence

from .webhooks.consumers import WhatsAppConsumer
from .webhooks.events import MessageReceived, MessageStatusUpdated, WebhookEvent

if TYPE_CHECKING:
    from .client import WhatsAppClient
    from .models import WhatsAppContact, WhatsAppMessage
    from .schemas import SendMessageResponse


class WhatsAppContext:
    def __init__(
        self,
        event: MessageReceived,
        contact: WhatsAppContact | None = None,
        message: WhatsAppMessage | None = None,
        client: WhatsAppClient | None = None,
    ):
        self.event = event
        self.contact = contact
        self.message = message
        self._client = client

    @property
    def client(self) -> WhatsAppClient:
        if self._client is None:
            from .client import WhatsAppClient

            self._client = WhatsAppClient()
        return self._client

    @property
    def text(self) -> str:
        return self.event.text or ""

    @property
    def from_phone(self) -> str:
        return self.event.from_phone or ""

    @property
    def message_type(self) -> str:
        return self.event.message_type or ""

    @property
    def button_id(self) -> str | None:
        if self.event.message_type == "interactive":
            interactive = self.event.message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                return interactive.get("button_reply", {}).get("id")
        elif self.event.message_type == "button":
            return self.event.message.get("button", {}).get("payload")
        return None

    @property
    def list_id(self) -> str | None:
        if self.event.message_type == "interactive":
            interactive = self.event.message.get("interactive", {})
            if interactive.get("type") == "list_reply":
                return interactive.get("list_reply", {}).get("id")
        return None

    def reply_text(self, text: str) -> SendMessageResponse:
        return self.client.messages.send_text(to=self.from_phone, text=text)

    def reply_buttons(
        self,
        text: str,
        buttons: list[dict[str, str]],
        header: str | None = None,
        footer: str | None = None,
    ) -> SendMessageResponse:
        return self.client.messages.send_buttons(
            to=self.from_phone,
            text=text,
            buttons=buttons,
            header=header,
            footer=footer,
        )

    def reply_list(
        self,
        text: str,
        button_text: str,
        sections: list[dict[str, Any]],
        header: str | None = None,
        footer: str | None = None,
    ) -> SendMessageResponse:
        return self.client.messages.send_list(
            to=self.from_phone,
            text=text,
            button_text=button_text,
            sections=sections,
            header=header,
            footer=footer,
        )

    def reply_image(self, media: str, caption: str | None = None) -> SendMessageResponse:
        return self.client.messages.send_image(to=self.from_phone, media=media, caption=caption)

    def reply_document(self, media: str, filename: str | None = None, caption: str | None = None) -> SendMessageResponse:
        return self.client.messages.send_document(to=self.from_phone, media=media, filename=filename, caption=caption)

    def mark_as_read(self) -> dict[str, Any]:
        if self.event.message_id:
            return self.client.messages.mark_as_read(self.event.message_id)
        return {}


class WhatsAppRouter:
    def __init__(self):
        self._text_handlers: list[tuple[Pattern[str] | Sequence[str] | None, Callable]] = []
        self._button_handlers: list[tuple[str | Sequence[str] | None, Callable]] = []
        self._list_handlers: list[tuple[str | Sequence[str] | None, Callable]] = []
        self._media_handlers: list[tuple[str | Sequence[str] | None, Callable]] = []
        self._catch_all_handlers: list[Callable] = []
        self._status_handlers: list[tuple[str | None, Callable]] = []

    def on_text(self, pattern: str | Pattern[str] | Sequence[str] | None = None):
        """
        Decorator to register a handler for incoming text messages.
        `pattern` can be:
        - None: matches all text messages.
        - str: exact case-insensitive match or regex.
        - Sequence[str]: matches if text equals any of the strings.
        - Pattern: compiled regex pattern.
        """
        def decorator(func: Callable):
            compiled = pattern
            if isinstance(pattern, str):
                try:
                    compiled = re.compile(pattern, re.IGNORECASE)
                except re.error:
                    compiled = [pattern.lower()]
            self._text_handlers.append((compiled, func))
            return func

        if callable(pattern):
            func = pattern
            pattern = None
            return decorator(func)
        return decorator

    def on_button(self, button_id: str | Sequence[str] | None = None):
        """
        Decorator to register a handler for interactive button clicks.
        """
        def decorator(func: Callable):
            self._button_handlers.append((button_id, func))
            return func

        if callable(button_id):
            func = button_id
            button_id = None
            return decorator(func)
        return decorator

    def on_list(self, list_id: str | Sequence[str] | None = None):
        """
        Decorator to register a handler for interactive list selection.
        """
        def decorator(func: Callable):
            self._list_handlers.append((list_id, func))
            return func

        if callable(list_id):
            func = list_id
            list_id = None
            return decorator(func)
        return decorator

    def on_media(self, media_type: str | Sequence[str] | None = None):
        """
        Decorator to register a handler for media messages (image, video, audio, document).
        """
        def decorator(func: Callable):
            self._media_handlers.append((media_type, func))
            return func

        if callable(media_type):
            func = media_type
            media_type = None
            return decorator(func)
        return decorator

    def on_message(self, func: Callable):
        """
        Catch-all decorator for any incoming message.
        """
        self._catch_all_handlers.append(func)
        return func

    def on_status(self, status: str | None = None):
        """
        Decorator for status updates (sent, delivered, read, failed).
        """
        def decorator(func: Callable):
            self._status_handlers.append((status, func))
            return func

        if callable(status):
            func = status
            status = None
            return decorator(func)
        return decorator

    def handle_message(self, event: MessageReceived) -> list[Any]:
        # Try to resolve DB contact & message if available
        contact = None
        message = None
        try:
            from .models import WhatsAppContact, WhatsAppMessage

            if event.from_phone:
                contact = WhatsAppContact.objects.filter(phone_number=event.from_phone).first()
            if event.message_id:
                message = WhatsAppMessage.objects.filter(wamid=event.message_id).first()
        except Exception:
            pass

        ctx = WhatsAppContext(
            event=event,
            contact=contact,
            message=message,
        )

        results = []
        mtype = event.message_type

        # 1. Button handlers
        btn_id = ctx.button_id
        if btn_id:
            for registered_id, handler in self._button_handlers:
                if (
                    registered_id is None
                    or (isinstance(registered_id, str) and registered_id == btn_id)
                    or (isinstance(registered_id, (list, tuple, set)) and btn_id in registered_id)
                ):
                    res = handler(ctx)
                    if res is not None:
                        results.append(res)

        # 2. List handlers
        lst_id = ctx.list_id
        if lst_id:
            for registered_id, handler in self._list_handlers:
                if (
                    registered_id is None
                    or (isinstance(registered_id, str) and registered_id == lst_id)
                    or (isinstance(registered_id, (list, tuple, set)) and lst_id in registered_id)
                ):
                    res = handler(ctx)
                    if res is not None:
                        results.append(res)

        # 3. Media handlers
        if mtype in ("image", "video", "audio", "document", "sticker"):
            for registered_type, handler in self._media_handlers:
                if (
                    registered_type is None
                    or (isinstance(registered_type, str) and registered_type == mtype)
                    or (isinstance(registered_type, (list, tuple, set)) and mtype in registered_type)
                ):
                    res = handler(ctx)
                    if res is not None:
                        results.append(res)

        # 4. Text handlers
        if mtype == "text" or (event.text and not btn_id and not lst_id):
            text = ctx.text.strip()
            for pattern, handler in self._text_handlers:
                matched = False
                if pattern is None:
                    matched = True
                elif isinstance(pattern, re.Pattern):
                    if pattern.search(text):
                        matched = True
                elif isinstance(pattern, (list, tuple, set)):
                    if any(t.lower() == text.lower() for t in pattern):
                        matched = True

                if matched:
                    res = handler(ctx)
                    if res is not None:
                        results.append(res)

        # 5. Catch-all handlers
        for handler in self._catch_all_handlers:
            res = handler(ctx)
            if res is not None:
                results.append(res)

        return results

    def handle_status(self, event: MessageStatusUpdated) -> list[Any]:
        results = []
        status_name = event.status_name
        for registered_status, handler in self._status_handlers:
            if registered_status is None or registered_status.lower() == (status_name or "").lower():
                res = handler(event)
                if res is not None:
                    results.append(res)
        return results


class RouterConsumer(WhatsAppConsumer):
    def __init__(self, router: WhatsAppRouter):
        self.router = router

    def on_message(self, event: MessageReceived):
        return self.router.handle_message(event)

    def on_status(self, event: MessageStatusUpdated):
        return self.router.handle_status(event)


# Default global bot router instance
bot = WhatsAppRouter()
router = bot
