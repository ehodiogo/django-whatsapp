from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING, BinaryIO

if TYPE_CHECKING:
    from ..conf import WhatsAppSettings
    from ..http import MetaAPIClient


class MediaClient:
    def __init__(
        self,
        http: MetaAPIClient,
        config: WhatsAppSettings,
    ):
        self.http = http
        self.config = config

    @property
    def media_upload_url(self) -> str:
        return f"{self.config.base_url}/{self.config.phone_number_id}/media"

    def upload(
        self,
        file: str | Path | bytes | BinaryIO,
        mime_type: str,
        filename: str | None = None,
    ) -> str:
        """
        Upload media to WhatsApp Cloud API.
        Returns the Meta media ID string.
        """
        file_content: bytes
        actual_filename = filename or "file"

        if isinstance(file, (str, Path)):
            path = Path(file)
            actual_filename = filename or path.name
            file_content = path.read_bytes()
        elif isinstance(file, bytes):
            file_content = file
        elif hasattr(file, "read"):
            file_content = file.read()
        else:
            raise TypeError("File must be a filepath string, Path, bytes, or file-like object.")

        files = {
            "file": (actual_filename, file_content, mime_type),
        }
        data = {
            "messaging_product": "whatsapp",
            "type": mime_type,
        }

        response = self.http.client.post(
            self.media_upload_url,
            data=data,
            files=files,
        )

        if response.status_code >= 400:
            from ..exceptions import WhatsAppAPIError

            try:
                error_data = response.json().get("error", {})
            except Exception:
                error_data = {}
            raise WhatsAppAPIError(
                f"Failed to upload media: {error_data.get('message', response.text)}",
                status_code=response.status_code,
                error=error_data,
            )

        return response.json().get("id")

    def get_info(self, media_id: str) -> dict:
        """
        Retrieve media metadata and download URL from Meta.
        """
        url = f"{self.config.base_url}/{media_id}"
        return self.http.get(url)

    def download(self, media_id: str) -> bytes:
        """
        Download media binary bytes given a Meta media ID.
        """
        info = self.get_info(media_id)
        download_url = info.get("url")

        if not download_url:
            from ..exceptions import WhatsAppAPIError

            raise WhatsAppAPIError(f"No download URL found for media ID {media_id}.")

        response = self.http.client.get(download_url)
        if response.status_code >= 400:
            from ..exceptions import WhatsAppAPIError

            raise WhatsAppAPIError(
                f"Failed to download media: HTTP {response.status_code}",
                status_code=response.status_code,
            )

        return response.content
