import pytest

from django_whatsapp.webhooks.consumers import (
    WhatsAppConsumer,
)
from django_whatsapp.webhooks.registry import (
    import_consumer,
    load_consumers,
)


class ExampleConsumer(WhatsAppConsumer):
    pass


def test_import_consumer():
    path = (
        "tests.test_webhook_registry."
        "ExampleConsumer"
    )

    consumer_class = import_consumer(path)

    assert consumer_class is ExampleConsumer


def test_load_consumers():
    paths = (
        "tests.test_webhook_registry."
        "ExampleConsumer",
    )

    consumers = load_consumers(paths)

    assert len(consumers) == 1
    assert isinstance(
        consumers[0],
        ExampleConsumer,
    )

class InvalidConsumer:
    pass

def test_import_consumer_requires_base_class():
    path = (
        "tests.test_webhook_registry."
        "InvalidConsumer"
    )

    with pytest.raises(TypeError):
        import_consumer(path)

def test_import_consumer_invalid_path():
    with pytest.raises(
        (ImportError, AttributeError)
    ):
        import_consumer(
            "does.not.exist.Consumer"
        )