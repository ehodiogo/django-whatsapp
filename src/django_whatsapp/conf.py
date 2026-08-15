from dataclasses import dataclass

from django.conf import settings


@dataclass(frozen=True)
class WhatsAppSettings:
    access_token: str
    phone_number_id: str
    api_version: str = "v23.0"
    timeout: float = 15.0

    @classmethod
    def from_django(cls) -> "WhatsAppSettings":
        config = getattr(settings, "DJANGO_WHATSAPP", {})

        return cls(
            access_token=config.get("ACCESS_TOKEN", ""),
            phone_number_id=config.get("PHONE_NUMBER_ID", ""),
            api_version=config.get("API_VERSION", "v23.0"),
            timeout=float(config.get("TIMEOUT", 15.0)),
        )

    @property
    def base_url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}"