from __future__ import annotations

from importlib import import_module
from typing import Type

from .consumers import WhatsAppConsumer


def import_consumer(path: str) -> Type[WhatsAppConsumer]:
    module_path, class_name = path.rsplit(".", 1)

    module = import_module(module_path)

    consumer_class = getattr(
        module,
        class_name,
    )

    if not issubclass(
        consumer_class,
        WhatsAppConsumer,
    ):
        raise TypeError(
            f"{path} must inherit from "
            "WhatsAppConsumer."
        )

    return consumer_class


def load_consumers(
    paths: tuple[str, ...],
) -> list[WhatsAppConsumer]:
    return [
        import_consumer(path)()
        for path in paths
    ]