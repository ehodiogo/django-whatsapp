import pytest

from django_whatsapp.validators import (
    InvalidMessageError,
    validate_text,
)


def test_validate_text():
    assert validate_text("Olá!") == "Olá!"


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "\n",
        "\t",
        None,
        123,
    ],
)
def test_invalid_text(text):
    with pytest.raises(InvalidMessageError):
        validate_text(text)