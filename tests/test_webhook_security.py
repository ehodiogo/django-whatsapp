import hashlib
import hmac

from django_whatsapp.webhooks.security import (
    verify_signature,
)


def test_valid_signature():
    payload = b'{"hello":"world"}'
    secret = "test-secret"

    digest = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    signature = f"sha256={digest}"

    assert verify_signature(
        payload,
        signature,
        secret,
    )


def test_invalid_signature():
    payload = b'{"hello":"world"}'

    assert not verify_signature(
        payload,
        "sha256=invalid",
        "test-secret",
    )


def test_missing_signature():
    payload = b'{"hello":"world"}'

    assert not verify_signature(
        payload,
        "",
        "test-secret",
    )


def test_invalid_signature_prefix():
    payload = b'{"hello":"world"}'

    assert not verify_signature(
        payload,
        "md5=abc",
        "test-secret",
    )