import re

from .exceptions import WhatsAppError


class InvalidPhoneNumberError(WhatsAppError):
    """Raised when a phone number is invalid."""


def normalize_phone_number(phone: str) -> str:
    if not isinstance(phone, str):
        raise InvalidPhoneNumberError(
            "Phone number must be a string."
        )

    value = phone.strip()

    if not value:
        raise InvalidPhoneNumberError(
            "Phone number cannot be empty."
        )

    # Remove common formatting characters.
    value = re.sub(r"[\s().-]", "", value)

    # Accept +5511999999999 and normalize to 5511999999999.
    if value.startswith("+"):
        value = value[1:]

    if not value.isdigit():
        raise InvalidPhoneNumberError(
            "Phone number must contain only digits "
            "after normalization."
        )

    # E.164 allows up to 15 digits.
    if len(value) > 15:
        raise InvalidPhoneNumberError(
            "Phone number cannot contain more than 15 digits."
        )

    if len(value) < 8:
        raise InvalidPhoneNumberError(
            "Phone number is too short."
        )

    return value