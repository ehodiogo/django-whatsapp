import os
import sys
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / "src"))
sys.path.insert(0, str(BASE_DIR / "tests" / "project"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django_whatsapp import WhatsAppClient
from django_whatsapp.exceptions import (
    WhatsAppAPIError,
    WhatsAppConfigurationError,
)

def send_real_template(to_number: str, template_name: str = "hello_world", language: str = "en_US"):
    print(f"🚀 Enviando TEMPLATE '{template_name}' ({language}) para: {to_number}")
    client = WhatsAppClient()
    try:
        response = client.messages.send_template(
            to=to_number,
            name=template_name,
            language=language,
        )
        print("\n✅ Template enviado com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}): {e}")

def send_real_text(to_number: str, message_text: str = "Olá! Teste de texto."):
    print(f"🚀 Enviando TEXTO para: {to_number}")
    client = WhatsAppClient()
    try:
        response = client.messages.send_text(
            to=to_number,
            text=message_text,
        )
        print("\n✅ Texto enviado com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}): {e}")

def send_real_buttons(to_number: str):
    print(f"🚀 Enviando BOTÕES INTERATIVOS para: {to_number}")
    client = WhatsAppClient()
    try:
        response = client.messages.send_buttons(
            to=to_number,
            text="Como podemos te ajudar hoje?",
            buttons=[
                {"id": "btn_financeiro", "title": "2ª Via Boleto 💳"},
                {"id": "btn_suporte", "title": "Suporte Humano 🛠️"},
                {"id": "btn_horarios", "title": "Horários ⏰"},
            ],
            header="Atendimento Django",
            footer="Escolha uma opção acima",
        )
        print("\n✅ Botões enviados com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}): {e}")

def send_real_list(to_number: str):
    print(f"🚀 Enviando MENU DE LISTA para: {to_number}")
    client = WhatsAppClient()
    try:
        response = client.messages.send_list(
            to=to_number,
            text="Selecione o serviço desejado no catálogo:",
            button_text="Ver Catálogo",
            header="Serviços",
            footer="django-whatsapp",
            sections=[
                {
                    "title": "Produtos",
                    "rows": [
                        {"id": "prod_1", "title": "Plano Starter", "description": "Ideal para pequenos negócios"},
                        {"id": "prod_2", "title": "Plano Pro", "description": "Para grandes volumes"},
                    ],
                }
            ],
        )
        print("\n✅ Menu de Lista enviado com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}): {e}")

if __name__ == "__main__":
    target = "+55 55 99699-5573"
    mode = "template"
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
    if len(sys.argv) > 2:
        mode = sys.argv[2].lower()

    if mode == "text":
        msg = sys.argv[3] if len(sys.argv) > 3 else "Olá! Teste de mensagem de texto."
        send_real_text(target, msg)
    elif mode == "buttons":
        send_real_buttons(target)
    elif mode == "list":
        send_real_list(target)
    else:
        send_real_template(target, "hello_world", "en_US")
