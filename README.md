# django-whatsapp

> Biblioteca Django completa e **plug-and-play** para integração com a WhatsApp Cloud API oficial da Meta.

**Status:** beta / em desenvolvimento ativo.

---

## Recursos Principais (Plug-and-Play)

- 🚀 **Plug & Play**: Apenas adicione aos `INSTALLED_APPS` e execute `python manage.py migrate`.
- 🗄️ **Modelos ORM Integrados**:
  - `WhatsAppContact`: Gestão automática de contatos, nomes de perfil e metadados.
  - `WhatsAppMessage`: Histórico completo de mensagens enviadas e recebidas com status e payloads.
- 💾 **Persistência Automática**:
  - Envio de mensagens (`send_text`, `send_template`) salva automaticamente no banco.
  - Webhooks criam contatos e mensagens recebidas, e atualizam status (`sent`, `delivered`, `read`, `failed`) em tempo real.
- 🔔 **Django Signals**: Dispare regras de negócio quando mensagens forem recebidas, enviadas ou status atualizados.
- 🖥️ **Django Admin**: Interface administrativa com badges de status, inline de mensagens, visualizador de JSON e filtros.
- 🔒 **Segurança**: Validação de assinatura HMAC-SHA256 do webhook Meta Cloud API.
- 📱 **Normalização e Validação**: Suporte automático a normalização de números telefônicos no padrão E.164.

---

## Instalação

```bash
pip install django-whatsapp
```

Adicione `django_whatsapp` ao seu `INSTALLED_APPS` em `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django.contrib.admin",
    "django.contrib.auth",
    "django_whatsapp.apps.DjangoWhatsAppConfig",
]
```

Execute as migrações:

```bash
python manage.py migrate
```

---

## Configuração

No seu arquivo `settings.py`:

```python
DJANGO_WHATSAPP = {
    "ACCESS_TOKEN": "seu-access-token-meta",
    "PHONE_NUMBER_ID": "seu-phone-number-id",
    "API_VERSION": "v23.0",
    "TIMEOUT": 15.0,
    "AUTO_SAVE": True,  # Salva contatos e mensagens no banco automaticamente (padrão: True)
    "WEBHOOK": {
        "VERIFY_TOKEN": "seu-verify-token-do-webhook",
        "APP_SECRET": "seu-app-secret-meta",
        "CONSUMERS": [
            # Seus consumers adicionais customizados (opcional)
        ],
    },
}
```

Inclua as rotas do webhook no `urls.py` do seu projeto:

```python
from django.urls import path, include

urlpatterns = [
    path("whatsapp/", include("django_whatsapp.webhooks.urls")),
]
```

---

## Como Usar

### 1. Envio Direto via Cliente

```python
from django_whatsapp import WhatsAppClient

client = WhatsAppClient()

# Envio de texto (salva automaticamente o contato e a mensagem no banco)
response = client.messages.send_text(
    to="+55 (11) 99999-9999",
    text="Olá! Esta é uma mensagem do django-whatsapp.",
)

# Envio de template
response = client.messages.send_template(
    to="5511999999999",
    name="hello_world",
    language="en_US",
)
```

### 2. Envio Direto via Objeto de Contato (`WhatsAppContact`)

```python
from django_whatsapp import WhatsAppContact

contact = WhatsAppContact.objects.get(phone_number="5511999999999")

# Envia a mensagem e registra o histórico
contact.send_text("Olá, seu pedido está pronto!")
```

### 3. Utilizando Signals Django

Conecte aos signals para executar automações em tempo real:

```python
from django.dispatch import receiver
from django_whatsapp.signals import (
    message_received,
    message_sent,
    message_status_updated,
    contact_created,
)

@receiver(message_received)
def handle_incoming_message(sender, message, contact, raw_event, **kwargs):
    print(f"Nova mensagem de {contact.name or contact.phone_number}: {message.body}")
    
    # Exemplo: Responder automaticamente
    if "ajuda" in message.body.lower():
        contact.send_text("Como posso te ajudar hoje?")

@receiver(message_status_updated)
def handle_status_change(sender, message, status, previous_status, raw_event, **kwargs):
    print(f"Mensagem {message.wamid} mudou de {previous_status} para {status}")
```

### 4. Django Admin

O `django-whatsapp` inclui painéis prontos no Django Admin:
- **Contatos**: Visualização de contatos com lista de mensagens relacionadas em inline e contagem de interações.
- **Mensagens**: Histórico com badges coloridos de status (`Pendente`, `Enviada`, `Entregue`, `Lida`, `Falhou`), direção (`Inbound` / `Outbound`), filtros por data e tipo, e visualizador formatado dos payloads da Meta.

---

## Testes

Para executar toda a suíte de testes:

```bash
python -m pytest
```

Todos os testes utilizam mocks HTTP (`respx`) e banco SQLite em memória.

---

## Licença

Este projeto é distribuído sob a licença Apache 2.0. Consulte o arquivo `LICENSE` para mais detalhes.
