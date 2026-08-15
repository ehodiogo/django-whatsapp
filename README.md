# django-whatsapp

> Biblioteca Django para integração com a WhatsApp Cloud API oficial da Meta.

**Status:** pre-alpha / em desenvolvimento.

A API pública ainda pode sofrer alterações antes da primeira versão estável.

## Objetivos

O `django-whatsapp` pretende fornecer uma interface Python/Django simples,
tipada e testável para integração com a WhatsApp Cloud API oficial da Meta.

Exemplo:

```python
from django_whatsapp import WhatsAppClient

client = WhatsAppClient()

client.messages.send_text(
    to="+55 (11) 99999-9999",
    text="Olá!",
)
```

## Status

### Implementado

- [x] Estrutura inicial do pacote
- [x] Integração com Django
- [x] Sistema de configuração
- [x] Configuração via `settings.py`
- [x] Cliente HTTP separado
- [x] `httpx.Client`
- [x] Tratamento inicial de erros da API
- [x] Normalização de números de telefone
- [x] Validação de mensagens
- [x] API `client.messages`
- [x] Envio de mensagens de texto
- [x] Parsing de respostas
- [x] Templates básicos
- [x] Headers de template
- [x] Testes automatizados

### Em desenvolvimento

- [ ] Templates completos
- [ ] Mídia
- [ ] Webhooks
- [ ] Validação de assinatura de webhook
- [ ] Upload e download de mídia
- [ ] Status de mensagens
- [ ] Retry/backoff
- [ ] Cliente assíncrono
- [ ] CI/CD
- [ ] Publicação no PyPI
- [ ] Documentação completa da API

## Requisitos

Desenvolvimento atual:

- Python 3.13
- Django 5.2
- HTTPX
- pytest
- pytest-django
- respx

## Instalação

Durante o desenvolvimento:

```bash
git clone <URL_DO_REPOSITORIO>
cd django-whatsapp

python -m venv venv
source venv/bin/activate

pip install -e .
```

Para desenvolvimento:

```bash
pip install -e ".[dev]"
```

## Configuração

No projeto Django consumidor:

```python
DJANGO_WHATSAPP = {
    "ACCESS_TOKEN": "...",
    "PHONE_NUMBER_ID": "...",
    "API_VERSION": "v23.0",
    "TIMEOUT": 15.0,
}
```

Recomenda-se usar variáveis de ambiente:

```env
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_API_VERSION=v23.0
WHATSAPP_TIMEOUT=15
```

Nunca versione tokens reais.

Exemplo usando `django-environ`:

```python
DJANGO_WHATSAPP = {
    "ACCESS_TOKEN": env("WHATSAPP_ACCESS_TOKEN"),
    "PHONE_NUMBER_ID": env("WHATSAPP_PHONE_NUMBER_ID"),
    "API_VERSION": env(
        "WHATSAPP_API_VERSION",
        default="v23.0",
    ),
    "TIMEOUT": env.float(
        "WHATSAPP_TIMEOUT",
        default=15.0,
    ),
}
```

## Uso

```python
from django_whatsapp import WhatsAppClient

client = WhatsAppClient()
```

### Envio de texto

```python
response = client.messages.send_text(
    to="+55 (11) 99999-9999",
    text="Olá! Esta é uma mensagem enviada pelo django-whatsapp.",
)

message_id = response.messages[0].id
```

### Templates

```python
client.messages.send_template(
    to="5511999999999",
    name="hello_world",
    language="en_US",
)
```

Templates com parâmetros e componentes continuam em evolução.

## Arquitetura

```text
Django
  |
  v
WhatsAppSettings
  |
  v
WhatsAppClient
  |
  +-- messages
  |     +-- send_text()
  |     +-- send_template()
  |
  v
MetaAPIClient
  |
  v
httpx.Client
  |
  v
WhatsApp Cloud API
```

### Principais módulos

- `conf.py` — configuração.
- `client.py` — facade principal.
- `messages/` — operações de mensagens.
- `http.py` — transporte HTTP.
- `schemas.py` — parsing de respostas.
- `validators.py` — validações locais.
- `phone.py` — normalização de telefone.
- `exceptions.py` — exceções públicas.

## Testes

Execute:

```bash
python -m pytest
```

A suíte usa `respx` para mockar chamadas HTTP. Portanto, os testes não
precisam de token real, número real ou conexão com a API da Meta.

## Segurança

Nunca coloque tokens reais no Git.

Mantenha `.env` fora do controle de versão e use `.env.example` para
documentar as variáveis necessárias.

Se uma credencial for exposta, ela deve ser revogada/rotacionada
imediatamente no ambiente da Meta.

## Roadmap

### Core

- [x] Configuração
- [x] Cliente HTTP
- [x] Exceções
- [x] Validação
- [x] Mensagens de texto
- [x] Templates básicos

### Templates

- [x] Header básico
- [ ] Body parameters tipados
- [ ] Buttons
- [ ] Templates multimídia
- [ ] Componentes tipados completos

### Media

- [ ] Upload
- [ ] Download
- [ ] Image
- [ ] Video
- [ ] Audio
- [ ] Document
- [ ] Sticker

### Webhooks

- [ ] Endpoint Django
- [ ] Verificação do webhook
- [ ] Parsing de eventos
- [ ] Mensagens recebidas
- [ ] Status
- [ ] Eventos de mídia

### Produção

- [ ] Retry
- [ ] Backoff
- [ ] Rate limiting
- [ ] Logging
- [ ] Observabilidade
- [ ] Async client
- [ ] CI
- [ ] Publicação no PyPI
- [ ] Documentação

## Contribuição

Antes de abrir um Pull Request:

```bash
python -m pytest
```

Novas funcionalidades devem incluir testes automatizados.

## Licença

Este projeto é distribuído sob a Apache License 2.0.
Consulte o arquivo `LICENSE` para o texto completo.

## Aviso sobre Meta e WhatsApp

`django-whatsapp` é um projeto independente e não é afiliado, patrocinado,
endossado ou administrado pela Meta Platforms, Inc.

WhatsApp e suas respectivas marcas, nomes e logotipos pertencem aos seus
respectivos titulares.

Este projeto pretende fornecer uma interface Python/Django para integração
com APIs oficiais disponibilizadas pela Meta.
