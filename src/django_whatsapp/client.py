from __future__ import annotations

from .conf import WhatsAppSettings
from .exceptions import WhatsAppConfigurationError
from .http import MetaAPIClient
from .messages.client import MessagesClient


class WhatsAppClient:
    def __init__(
        self,
        config: WhatsAppSettings | None = None,
    ):
        self.config = config or WhatsAppSettings.from_django()

        self._validate_config()

        self.http = MetaAPIClient(self.config)

        self.messages = MessagesClient(
            http=self.http,
            messages_url=self.messages_url,
        )

    def _validate_config(self) -> None:
        if not self.config.access_token:
            raise WhatsAppConfigurationError(
                "DJANGO_WHATSAPP['ACCESS_TOKEN'] is required."
            )

        if not self.config.phone_number_id:
            raise WhatsAppConfigurationError(
                "DJANGO_WHATSAPP['PHONE_NUMBER_ID'] is required."
            )

    @property
    def messages_url(self) -> str:
        return (
            f"{self.config.base_url}/"
            f"{self.config.phone_number_id}/messages"
        )

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> "WhatsAppClient":
        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:
        self.close()