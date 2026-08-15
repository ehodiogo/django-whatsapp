from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class WhatsAppWebhookSettings:
    verify_token: str = ""
    app_secret: str = ""
    consumers: tuple[str, ...] = ()


@dataclass(frozen=True)
class WhatsAppSettings:
    access_token: str
    phone_number_id: str
    api_version: str = "v23.0"
    timeout: float = 15.0
    webhook: WhatsAppWebhookSettings | None = None

    @classmethod
    def from_django(cls) -> "WhatsAppSettings":
        config = getattr(
            settings,
            "DJANGO_WHATSAPP",
            {},
        )

        webhook_config = config.get(
            "WEBHOOK",
            {},
        )

        webhook = WhatsAppWebhookSettings(
            verify_token=webhook_config.get(
                "VERIFY_TOKEN",
                "",
            ),
            app_secret=webhook_config.get(
                "APP_SECRET",
                "",
            ),
            consumers=tuple(
                webhook_config.get(
                    "CONSUMERS",
                    [],
                )
            ),
        )

        return cls(
            access_token=config.get(
                "ACCESS_TOKEN",
                "",
            ),
            phone_number_id=config.get(
                "PHONE_NUMBER_ID",
                "",
            ),
            api_version=config.get(
                "API_VERSION",
                "v23.0",
            ),
            timeout=float(
                config.get(
                    "TIMEOUT",
                    15.0,
                )
            ),
            webhook=webhook,
        )

    @property
    def base_url(self) -> str:
        return (
            f"https://graph.facebook.com/"
            f"{self.api_version}"
        )