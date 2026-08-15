from __future__ import annotations

from typing import Any


def build_text_parameters(
    values: list[str],
) -> list[dict[str, Any]]:
    return [
        {
            "type": "text",
            "text": str(value),
        }
        for value in values
    ]


def build_body_component(
    parameters: list[str],
) -> dict[str, Any]:
    return {
        "type": "body",
        "parameters": build_text_parameters(parameters),
    }