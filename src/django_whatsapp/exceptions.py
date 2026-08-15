class WhatsAppError(Exception):
    """Base exception for django-whatsapp."""


class WhatsAppConfigurationError(WhatsAppError):
    """Raised when the WhatsApp configuration is invalid."""


class WhatsAppAPIError(WhatsAppError):
    """Raised when Meta's API returns an error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        error: dict | None = None,
        response: dict | None = None,
    ):
        super().__init__(message)

        self.status_code = status_code
        self.error = error
        self.response = response


class WhatsAppWebhookError(WhatsAppError):
    """Raised when a webhook payload is invalid."""