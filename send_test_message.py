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
    
    try:
        client = WhatsAppClient()
    except WhatsAppConfigurationError as e:
        print(f"\n❌ Erro de Configuração: {e}")
        return

    try:
        response = client.messages.send_template(
            to=to_number,
            name=template_name,
            language=language,
        )
        print("\n✅ Template enviado com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
        if response.contacts:
            print(f"👤 Contato Meta: {response.contacts[0].wa_id}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}):")
        print(f"   Mensagem: {e}")
        if e.error:
            print(f"   Código Meta: {e.error.get('code')}")
            print(f"   Detalhes: {e.error}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")

def send_real_text(to_number: str, message_text: str = "Olá! Este é um teste real enviado pelo django-whatsapp 🚀"):
    print(f"🚀 Enviando TEXTO para: {to_number}")
    
    try:
        client = WhatsAppClient()
    except WhatsAppConfigurationError as e:
        print(f"\n❌ Erro de Configuração: {e}")
        return

    try:
        response = client.messages.send_text(
            to=to_number,
            text=message_text,
        )
        print("\n✅ Texto enviado com SUCESSO!")
        print(f"🆔 Message ID (wamid): {response.messages[0].id if response.messages else 'N/A'}")
        if response.contacts:
            print(f"👤 Contato Meta: {response.contacts[0].wa_id}")
    except WhatsAppAPIError as e:
        print(f"\n❌ Erro retornado pela API da Meta (HTTP {e.status_code}):")
        print(f"   Mensagem: {e}")
        if e.error:
            print(f"   Código Meta: {e.error.get('code')}")
            print(f"   Detalhes: {e.error}")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")

if __name__ == "__main__":
    target = "+55 55 99699-5573"
    mode = "template"  # default to template because of Meta 24-hour window policy
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
    if len(sys.argv) > 2:
        mode = sys.argv[2]

    if mode == "text":
        msg = sys.argv[3] if len(sys.argv) > 3 else "Olá! Teste de mensagem de texto."
        send_real_text(target, msg)
    else:
        send_real_template(target, "hello_world", "en_US")
