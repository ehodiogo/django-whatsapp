from django_whatsapp.messages.components import TemplateHeader


def test_image_header_payload():
    header = TemplateHeader.image(
        "https://example.com/image.jpg"
    )

    assert header.to_payload() == {
        "type": "header",
        "parameters": [
            {
                "type": "image",
                "image": {
                    "link": "https://example.com/image.jpg",
                },
            }
        ],
    }