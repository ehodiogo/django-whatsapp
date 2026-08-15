from __future__ import annotations

from typing import Any

import httpx

from .conf import WhatsAppSettings
from .exceptions import WhatsAppAPIError


class MetaAPIClient:
    def __init__(self, config: WhatsAppSettings):
        self.config = config

        self.client = httpx.Client(
            headers=self._headers(),
            timeout=self.config.timeout,
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }

    def post(
        self,
        url: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = self.client.post(
                url,
                json=payload,
            )
        except httpx.HTTPError as exc:
            raise WhatsAppAPIError(
                f"HTTP request failed: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError:
            data = {
                "raw": response.text,
            }

        if not response.is_success:
            raise WhatsAppAPIError(
                "Meta API returned an error.",
                status_code=response.status_code,
                error=data.get("error"),
                response=data,
            )

        return data

    def close(self) -> None:
        self.client.close()

    def __enter__(self) -> "MetaAPIClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()