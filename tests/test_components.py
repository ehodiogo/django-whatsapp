import pytest
from django_whatsapp.messages.components import (
    InvalidTemplateComponentError,
    TemplateHeader,
)

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

def test_text_header_payload():
    header = TemplateHeader.text(
        "Pedido #12345"
    )

    assert header.to_payload() == {
        "type": "header",
        "parameters": [
            {
                "type": "text",
                "text": "Pedido #12345",
            }
        ],
    }

def test_invalid_header_type():
    with pytest.raises(InvalidTemplateComponentError):
        TemplateHeader(
            type="banana",
            value="abc",
        )

def test_empty_header_value():
    with pytest.raises(InvalidTemplateComponentError):
        TemplateHeader.text("")

def test_whitespace_header_value():
    with pytest.raises(InvalidTemplateComponentError):
        TemplateHeader.text("   ")