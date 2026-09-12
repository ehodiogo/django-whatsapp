import io
import httpx
import pytest
import respx
from django_whatsapp.client import WhatsAppClient
from django_whatsapp.exceptions import WhatsAppAPIError

pytestmark = pytest.mark.django_db


@respx.mock
def test_media_upload_bytes():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/media"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"id": "media-upload-123"},
        )
    )

    client = WhatsAppClient()
    media_id = client.media.upload(
        file=b"fake-pdf-content",
        mime_type="application/pdf",
        filename="boleto.pdf",
    )

    assert media_id == "media-upload-123"


@respx.mock
def test_media_upload_error():
    respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/media"
    ).mock(
        return_value=httpx.Response(
            400,
            json={"error": {"message": "Invalid file format"}},
        )
    )

    client = WhatsAppClient()
    with pytest.raises(WhatsAppAPIError) as exc:
        client.media.upload(
            file=b"fake-content",
            mime_type="invalid/type",
        )
    assert "Invalid file format" in str(exc.value)


@respx.mock
def test_media_download():
    respx.get("https://graph.facebook.com/v23.0/media-123").mock(
        return_value=httpx.Response(
            200,
            json={"url": "https://cdn.whatsapp.net/files/media-123", "id": "media-123"},
        )
    )
    respx.get("https://cdn.whatsapp.net/files/media-123").mock(
        return_value=httpx.Response(
            200,
            content=b"downloaded-image-bytes",
        )
    )

    client = WhatsAppClient()
    content = client.media.download("media-123")
    assert content == b"downloaded-image-bytes"


@respx.mock
def test_send_media_helpers():
    route = respx.post(
        "https://graph.facebook.com/v23.0/development-phone-number-id/messages"
    ).mock(
        return_value=httpx.Response(
            200,
            json={"messaging_product": "whatsapp", "messages": [{"id": "wamid.media-msg-1"}]},
        )
    )

    client = WhatsAppClient()

    import json

    # Image
    client.messages.send_image(to="5511999999999", media="https://site.com/img.png", caption="Foto")
    sent = json.loads(route.calls.last.request.read().decode())
    assert sent["type"] == "image"
    assert sent["image"]["link"] == "https://site.com/img.png"
    assert sent["image"]["caption"] == "Foto"

    # Document
    client.messages.send_document(to="5511999999999", media="media-id-doc", filename="doc.pdf")
    sent = json.loads(route.calls.last.request.read().decode())
    assert sent["type"] == "document"
    assert sent["document"]["id"] == "media-id-doc"
    assert sent["document"]["filename"] == "doc.pdf"

    # Audio
    client.messages.send_audio(to="5511999999999", media="media-id-audio")
    sent = json.loads(route.calls.last.request.read().decode())
    assert sent["type"] == "audio"
    assert sent["audio"]["id"] == "media-id-audio"

    # Video
    client.messages.send_video(to="5511999999999", media="https://site.com/video.mp4", caption="Vídeo")
    sent = json.loads(route.calls.last.request.read().decode())
    assert sent["type"] == "video"
    assert sent["video"]["link"] == "https://site.com/video.mp4"

    # Sticker
    client.messages.send_sticker(to="5511999999999", media="media-id-sticker")
    sent = json.loads(route.calls.last.request.read().decode())
    assert sent["type"] == "sticker"
    assert sent["sticker"]["id"] == "media-id-sticker"
