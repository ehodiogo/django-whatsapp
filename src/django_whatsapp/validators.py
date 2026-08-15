from .exceptions import WhatsAppError


class InvalidMessageError(WhatsAppError):
    """Raised when a WhatsApp message is invalid."""


def validate_text(text: str) -> str:
    if not isinstance(text, str):
        raise InvalidMessageError(
            "Message text must be a string."
        )

    if not text.strip():
        raise InvalidMessageError(
            "Message text cannot be empty."
        )

    return text