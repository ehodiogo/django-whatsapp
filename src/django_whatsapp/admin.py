from __future__ import annotations

import json
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import (
    MessageDirection,
    MessageStatus,
    WhatsAppContact,
    WhatsAppMessage,
)


class WhatsAppMessageInline(admin.TabularInline):
    model = WhatsAppMessage
    extra = 0
    can_delete = False
    show_change_link = True
    fields = (
        "direction",
        "message_type",
        "status",
        "body_preview",
        "wamid",
        "created_at",
    )
    readonly_fields = fields

    @admin.display(description=_("Conteúdo"))
    def body_preview(self, obj: WhatsAppMessage) -> str:
        if not obj.body:
            return f"[{obj.message_type}]"
        return (obj.body[:50] + "...") if len(obj.body) > 50 else obj.body

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(WhatsAppContact)
class WhatsAppContactAdmin(admin.ModelAdmin):
    list_display = (
        "phone_number",
        "name",
        "wa_id",
        "messages_count",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "phone_number",
        "name",
        "wa_id",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "messages_count",
    )
    inlines = [WhatsAppMessageInline]

    @admin.display(description=_("Total de Mensagens"))
    def messages_count(self, obj: WhatsAppContact) -> int:
        return obj.messages.count()


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contact_link",
        "direction_badge",
        "message_type",
        "status_badge",
        "body_snippet",
        "wamid",
        "created_at",
    )
    list_filter = (
        "direction",
        "status",
        "message_type",
        "created_at",
    )
    search_fields = (
        "contact__phone_number",
        "contact__name",
        "wamid",
        "body",
    )
    readonly_fields = (
        "contact",
        "wamid",
        "direction",
        "message_type",
        "status",
        "body",
        "raw_payload_formatted",
        "error_data_formatted",
        "timestamp",
        "sent_at",
        "delivered_at",
        "read_at",
        "failed_at",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            _("Informações Básicas"),
            {
                "fields": (
                    "contact",
                    "direction",
                    "message_type",
                    "status",
                    "wamid",
                    "body",
                )
            },
        ),
        (
            _("Timestamps"),
            {
                "fields": (
                    "timestamp",
                    "sent_at",
                    "delivered_at",
                    "read_at",
                    "failed_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
        (
            _("Payloads e Dados Técnicos"),
            {
                "classes": ("collapse",),
                "fields": (
                    "raw_payload_formatted",
                    "error_data_formatted",
                ),
            },
        ),
    )

    @admin.display(description=_("Contato"))
    def contact_link(self, obj: WhatsAppMessage) -> str:
        return str(obj.contact)

    @admin.display(description=_("Conteúdo"))
    def body_snippet(self, obj: WhatsAppMessage) -> str:
        if not obj.body:
            return f"[{obj.message_type}]"
        return (obj.body[:60] + "...") if len(obj.body) > 60 else obj.body

    @admin.display(description=_("Direção"))
    def direction_badge(self, obj: WhatsAppMessage) -> str:
        if obj.direction == MessageDirection.INBOUND:
            color = "#0284c7"  # sky-600
            label = "Recebida (In)"
        else:
            color = "#16a34a"  # green-600
            label = "Enviada (Out)"
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            label,
        )

    @admin.display(description=_("Status"))
    def status_badge(self, obj: WhatsAppMessage) -> str:
        colors = {
            MessageStatus.PENDING: "#eab308",    # yellow-500
            MessageStatus.SENT: "#64748b",       # slate-500
            MessageStatus.DELIVERED: "#0284c7",  # sky-600
            MessageStatus.READ: "#22c55e",       # green-500
            MessageStatus.FAILED: "#ef4444",     # red-500
            MessageStatus.RECEIVED: "#3b82f6",   # blue-500
        }
        color = colors.get(obj.status, "#64748b")
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.display(description=_("Payload Bruto (JSON)"))
    def raw_payload_formatted(self, obj: WhatsAppMessage) -> str:
        if not obj.raw_payload:
            return "-"
        formatted = json.dumps(obj.raw_payload, indent=2, ensure_ascii=False)
        return format_html("<pre style='max-height: 300px; overflow: auto;'>{}</pre>", formatted)

    @admin.display(description=_("Dados de Erro (JSON)"))
    def error_data_formatted(self, obj: WhatsAppMessage) -> str:
        if not obj.error_data:
            return "-"
        formatted = json.dumps(obj.error_data, indent=2, ensure_ascii=False)
        return format_html("<pre style='max-height: 300px; overflow: auto; color: red;'>{}</pre>", formatted)
