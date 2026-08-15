import pytest

from django_whatsapp.phone import (
    InvalidPhoneNumberError,
    normalize_phone_number,
)


def test_normalize_brazilian_phone():
    assert normalize_phone_number(
        "+55 (11) 99999-9999"
    ) == "5511999999999"


def test_normalize_phone_without_plus():
    assert normalize_phone_number(
        "5511999999999"
    ) == "5511999999999"


@pytest.mark.parametrize(
    "phone",
    [
        "",
        "abc",
        "1234567",
        "1234567890123456",
    ],
)
def test_invalid_phone_numbers(phone):
    with pytest.raises(InvalidPhoneNumberError):
        normalize_phone_number(phone)

def test_eleven_digit_phone_can_be_valid():
    assert normalize_phone_number(
        "11999999999"
    ) == "11999999999"