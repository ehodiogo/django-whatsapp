from __future__ import annotations

import json
import logging

from django.http import (
    HttpRequest,
    HttpResponse,
    JsonResponse,
)
from django.views import View

from ..conf import WhatsAppSettings
from ..tasks import process_webhook_payload, process_webhook_payload_task
from .security import verify_signature

logger = logging.getLogger(__name__)


class WhatsAppWebhookView(View):

    def get(
        self,
        request: HttpRequest,
    ) -> HttpResponse:
        config = WhatsAppSettings.from_django()

        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if (
            mode == "subscribe"
            and config.webhook
            and token == config.webhook.verify_token
        ):
            return HttpResponse(
                challenge or "",
                status=200,
                content_type="text/plain",
            )

        return HttpResponse(
            "Forbidden",
            status=403,
        )

    def post(
        self,
        request: HttpRequest,
    ) -> JsonResponse:
        config = WhatsAppSettings.from_django()

        if not config.webhook:
            return JsonResponse(
                {
                    "detail": "Webhook is not configured.",
                },
                status=500,
            )

        signature = request.headers.get(
            "X-Hub-Signature-256",
            "",
        )

        if not verify_signature(
            request.body,
            signature,
            config.webhook.app_secret,
        ):
            return JsonResponse(
                {
                    "detail": "Invalid signature.",
                },
                status=403,
            )

        try:
            payload = json.loads(
                request.body
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {
                    "detail": "Invalid JSON.",
                },
                status=400,
            )

        # Celery asynchronous dispatch
        if config.use_celery and process_webhook_payload_task is not None:
            process_webhook_payload_task.delay(payload)
            return JsonResponse(
                {
                    "received": True,
                    "queued": True,
                },
                status=200,
            )

        # Synchronous processing
        event_count = process_webhook_payload(payload)

        return JsonResponse(
            {
                "received": True,
                "events": event_count,
            },
            status=200,
        )