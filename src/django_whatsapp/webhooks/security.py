from __future__ import annotations

import hashlib
import hmac


def verify_signature(
    payload: bytes,
    signature: str,
    app_secret: str,
) -> bool:
    if not signature:
        return False

    if not signature.startswith("sha256="):
        return False

    expected = hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    received = signature.removeprefix("sha256=")

    return hmac.compare_digest(
        expected,
        received,
    )