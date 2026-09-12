# django-whatsapp

> Biblioteca Django completa, robusta e **plug-and-play** para integração com a WhatsApp Cloud API oficial da Meta.

**Status:** beta / em desenvolvimento ativo.

---

## Recursos Principais (Plug-and-Play)

- 🚀 **Plug & Play**: Apenas adicione aos `INSTALLED_APPS` e execute `python manage.py migrate`.
- 🗄️ **Modelos ORM Integrados**:
  - `WhatsAppContact`: Gestão automática de contatos, nomes de perfil e metadados.
  - `WhatsAppMessage`: Histórico completo de mensagens enviadas e recebidas com status e payloads.
- 💾 **Persistência Automática**:
  - Envio de mensagens (`send_text`, `send_template`, `send_buttons`, etc.) salva automaticamente no banco.
  - Webhooks criam contatos e mensagens recebidas, e atualizam status (`sent`, `delivered`, `read`, `failed`) em tempo real.
- 🔘 **Mensagens Interativas**:
  - Botões de resposta rápida (Quick Reply, até 3 botões).
  - Menus de Lista (Dropdown de catálogo com seções e itens).
  - Localização geográfica e reações com emoji.
  - Marcar como lido (`mark_as_read`) para confirmação de leitura visual (dois tracinhos azuis).
- 📸 **Upload & Envio de Mídias**:
  - Envio de imagens, PDFs/documentos, áudios, vídeos e stickers (por URL ou ID de mídia).
  - Upload e download direto de arquivos autenticados via `client.media`.
- 🤖 **Mini Chatbot Engine & Router**:
  - Decorators declarativos `@bot.on_text`, `@bot.on_button`, `@bot.on_list`, `@bot.on_media`.
  - Contexto rico com helpers `ctx.reply_text()`, `ctx.reply_buttons()`, `ctx.reply_image()`, `ctx.mark_as_read()`.
- ⚡ **Processamento em Background (Celery)**:
  - Suporte opcional a Celery com `USE_CELERY = True` para responder webhooks em < 10ms.
- 🔔 **Django Signals**: Dispare regras de negócio quando mensagens forem recebidas, enviadas ou status atualizados.
- 🖥️ **Django Admin**: Interface administrativa com badges de status, inline de mensagens, visualizador de JSON e filtros.
- 🔒 **Segurança**: Validação de assinatura HMAC-SHA256 do webhook Meta Cloud API.

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
    "AUTO_SAVE": True,    # Salva contatos e mensagens no banco automaticamente (padrão: True)
    "USE_CELERY": False,  # Despacha processamento de webhooks para o Celery (opcional)
    "WEBHOOK": {
        "VERIFY_TOKEN": "seu-verify-token-do-webhook",
        "APP_SECRET": "seu-app-secret-meta",
        "CONSUMERS": [],
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

### 1. Envio de Mensagens

```python
from django_whatsapp import WhatsAppClient

client = WhatsAppClient()

# Texto
client.messages.send_text(
    to="+55 (11) 99999-9999",
    text="Olá! Esta é uma mensagem do django-whatsapp.",
)

# Template Oficial
client.messages.send_template(
    to="5511999999999",
    name="hello_world",
    language="en_US",
)

# Botões Interativos (Quick Reply)
client.messages.send_buttons(
    to="5511999999999",
    text="Como podemos te ajudar hoje?",
    buttons=[
        {"id": "btn_financeiro", "title": "Financeiro 💳"},
        {"id": "btn_suporte", "title": "Suporte Técnico 🛠️"},
    ],
    header="Menu Principal",
    footer="Escolha uma opção",
)

# Menu de Lista (Dropdown)
client.messages.send_list(
    to="5511999999999",
    text="Selecione um plano:",
    button_text="Ver Planos",
    sections=[
        {
            "title": "Planos Mensais",
            "rows": [
                {"id": "p1", "title": "Starter", "description": "R$ 49/mês"},
                {"id": "p2", "title": "Pro", "description": "R$ 99/mês"},
            ],
        }
    ],
)

# Envio de Imagens e Documentos (PDF)
client.messages.send_image(to="5511999999999", media="https://exemplo.com/foto.jpg", caption="Foto do produto")
client.messages.send_document(to="5511999999999", media="https://exemplo.com/boleto.pdf", filename="Boleto.pdf")

# Reações e Marcar como Lido
client.messages.send_reaction(to="5511999999999", message_id="wamid.HBg...", emoji="👍")
client.messages.mark_as_read(message_id="wamid.HBg...")
```

### 2. Mini Chatbot Router

Crie bots e fluxos conversacionais completos em poucas linhas:

```python
from django_whatsapp import bot

@bot.on_text(["oi", "olá", "menu"])
def menu_handler(ctx):
    ctx.mark_as_read()
    ctx.reply_buttons(
        text="Olá! Escolha como podemos te ajudar:",
        buttons=[
            {"id": "btn_suporte", "title": "Suporte 🛠️"},
            {"id": "btn_compras", "title": "Ver Catálogo 🛍️"},
        ],
    )

@bot.on_button("btn_suporte")
def suporte_handler(ctx):
    ctx.reply_text("Um de nossos atendentes já vai falar com você!")

@bot.on_media("image")
def image_handler(ctx):
    ctx.reply_text("Recebemos sua imagem com sucesso!")
```

### 3. Envio Direto via Objeto de Contato (`WhatsAppContact`)

```python
from django_whatsapp import WhatsAppContact

contact = WhatsAppContact.objects.get(phone_number="5511999999999")

# Envia mensagem e vincula o histórico
contact.send_text("Olá, seu pedido está a caminho!")
contact.send_buttons("Você confirma o recebimento?", buttons=[{"id": "sim", "title": "Sim ✅"}])
```

### 4. Utilizando Signals Django

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

@receiver(message_status_updated)
def handle_status_change(sender, message, status, previous_status, raw_event, **kwargs):
    print(f"Mensagem {message.wamid} mudou para {status}")
```

### 5. Django Admin

O `django-whatsapp` inclui painéis prontos no Django Admin:
- **Contatos**: Visualização de contatos com lista de mensagens relacionadas em inline e contagem de interações.
- **Mensagens**: Histórico com badges coloridos de status (`Pendente`, `Enviada`, `Entregue`, `Lida`, `Falhou`), direção (`Inbound` / `Outbound`), filtros por data e tipo, e visualizador formatado dos payloads da Meta.

---

## Testes

Para executar toda a suíte de testes:

```bash
python -m pytest
```

Todos os 92 testes automatizados utilizam mocks HTTP (`respx`) e banco de dados SQLite isolado.

---

## Licença

Este projeto é distribuído sob a licença Apache 2.0. Consulte o arquivo `LICENSE` para mais detalhes.
