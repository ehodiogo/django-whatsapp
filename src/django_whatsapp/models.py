from __future__ import annotations

from typing import TYPE_CHECKING, Any
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from .client import WhatsAppClient
    from .messages.components import TemplateHeader
    from .schemas import SendMessageResponse


class MessageDirection(models.TextChoices):
    INBOUND = "inbound", _("Inbound (Recebida)")
    OUTBOUND = "outbound", _("Outbound (Enviada)")


class MessageStatus(models.TextChoices):
    PENDING = "pending", _("Pendente")
    SENT = "sent", _("Enviada")
    DELIVERED = "delivered", _("Entregue")
    READ = "read", _("Lida")
    FAILED = "failed", _("Falhou")
    RECEIVED = "received", _("Recebida")


class MessageType(models.TextChoices):
    TEXT = "text", _("Texto")
    TEMPLATE = "template", _("Template")
    IMAGE = "image", _("Imagem")
    VIDEO = "video", _("Vídeo")
    AUDIO = "audio", _("Áudio")
    DOCUMENT = "document", _("Documento")
    STICKER = "sticker", _("Figurinha")
    LOCATION = "location", _("Localização")
    INTERACTIVE = "interactive", _("Interativo")
    BUTTON = "button", _("Botão")
    REACTION = "reaction", _("Reação")
    UNKNOWN = "unknown", _("Desconhecido")


class WhatsAppContact(models.Model):
    phone_number = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name=_("Telefone"),
        help_text=_("Número de telefone no formato internacional normalizado (ex: 5511999999999)."),
    )
    wa_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        verbose_name=_("WhatsApp ID"),
        help_text=_("ID do WhatsApp retornado pela Meta."),
    )
    name = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Nome / Perfil"),
        help_text=_("Nome do perfil do WhatsApp ou nome cadastrado."),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Metadados"),
        help_text=_("Dados adicionais do contato."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em"),
    )

    class Meta:
        db_table = "django_whatsapp_contact"
        verbose_name = _("Contato WhatsApp")
        verbose_name_plural = _("Contatos WhatsApp")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        if self.name:
            return f"{self.name} ({self.phone_number})"
        return self.phone_number

    def send_text(
        self,
        text: str,
        client: WhatsAppClient | None = None,
    ) -> SendMessageResponse:
        from .client import WhatsAppClient

        active_client = client or WhatsAppClient()
        return active_client.messages.send_text(
            to=self.phone_number,
            text=text,
        )

    def send_template(
        self,
        name: str,
        language: str = "pt_BR",
        *,
        body_parameters: list[str] | None = None,
        header: TemplateHeader | None = None,
        client: WhatsAppClient | None = None,
    ) -> SendMessageResponse:
        from .client import WhatsAppClient

        active_client = client or WhatsAppClient()
        return active_client.messages.send_template(
            to=self.phone_number,
            name=name,
            language=language,
            body_parameters=body_parameters,
            header=header,
        )


class WhatsAppMessage(models.Model):
    contact = models.ForeignKey(
        WhatsAppContact,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("Contato"),
    )
    wamid = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("WhatsApp Message ID"),
        help_text=_("ID único da mensagem na Meta (wamid)."),
    )
    direction = models.CharField(
        max_length=10,
        choices=MessageDirection.choices,
        db_index=True,
        verbose_name=_("Direção"),
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        db_index=True,
        verbose_name=_("Tipo de Mensagem"),
    )
    status = models.CharField(
        max_length=20,
        choices=MessageStatus.choices,
        default=MessageStatus.PENDING,
        db_index=True,
        verbose_name=_("Status"),
    )
    body = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Conteúdo / Texto"),
    )
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Payload Bruto"),
    )
    error_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Dados de Erro"),
    )
    timestamp = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Timestamp Meta"),
        help_text=_("Data e hora informadas pela Meta."),
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Enviado em"),
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Entregue em"),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Lido em"),
    )
    failed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Falhou em"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em"),
    )

    class Meta:
        db_table = "django_whatsapp_message"
        verbose_name = _("Mensagem WhatsApp")
        verbose_name_plural = _("Mensagens WhatsApp")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        snippet = (self.body[:30] + "...") if len(self.body) > 30 else (self.body or f"[{self.message_type}]")
        return f"{self.get_direction_display()} - {self.contact.phone_number}: {snippet}"
