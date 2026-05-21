# OpenWA WhatsApp for Home Assistant

A Home Assistant custom integration for sending WhatsApp messages through a self-hosted OpenWA API instance.

This integration lets you send WhatsApp messages from Home Assistant automations, scripts, scenes, and Developer Tools using your own OpenWA server.

## Features

- Send WhatsApp text messages from Home Assistant.
- Uses a local or self-hosted OpenWA API server.
- Supports individual WhatsApp chats.
- Supports WhatsApp groups if you know the group chat ID.
- Configurable through the Home Assistant UI.
- Works with automations, scripts, scenes, and blueprints.

## Requirements

You need a working OpenWA API server.

Example OpenWA base URL:

```text
http://OPENWA_HOST:2785
```

Do not include `/api` at the end of the base URL.

You also need:

- An OpenWA API key.
- An OpenWA session ID.
- A ready/authenticated WhatsApp session in OpenWA.

## OpenWA API endpoint used

This integration sends messages using:

```text
POST /api/sessions/{session_id}/messages/send-text
```

Request body:

```json
{
  "chatId": "15551234567@c.us",
  "text": "Message text"
}
```

Header:

```text
X-API-Key: OPENWA_API_KEY
```

## Installation with HACS

1. Open Home Assistant.
2. Go to **HACS**.
3. Go to **Integrations**.
4. Open the three-dot menu.
5. Choose **Custom repositories**.
6. Add this repository URL.
7. Set category to **Integration**.
8. Install **OpenWA WhatsApp**.
9. Restart Home Assistant.
10. Go to **Settings → Devices & services → Add integration**.
11. Search for **OpenWA WhatsApp**.

## Manual installation

Copy this folder:

```text
custom_components/openwa_whatsapp
```

to your Home Assistant config folder:

```text
/config/custom_components/openwa_whatsapp
```

Then restart Home Assistant.

## Configuration

After installation, add the integration from:

```text
Settings → Devices & services → Add integration → OpenWA WhatsApp
```

The setup flow asks for:

| Field | Example |
|---|---|
| OpenWA Base URL | `http://OPENWA_HOST:2785` |
| OpenWA API Key | `owa_k1_REPLACE_WITH_YOUR_API_KEY` |
| OpenWA Session ID | `REPLACE_WITH_SESSION_ID` |

## Finding your OpenWA API key

On the machine running OpenWA, check the container logs:

```bash
docker logs openwa 2>&1 | grep -i -A4 -B4 "api key"
```

You should see a key similar to:

```text
owa_k1_REPLACE_WITH_YOUR_API_KEY
```

Use the full `owa_k1_...` value as the API key.

## Finding your OpenWA session ID

Use the OpenWA sessions endpoint:

```bash
curl -H "X-API-Key: OPENWA_API_KEY" \
  http://OPENWA_HOST:2785/api/sessions
```

Example response:

```json
[
  {
    "id": "REPLACE_WITH_SESSION_ID",
    "name": "main",
    "status": "ready"
  }
]
```

Use the `id` value as the session ID.

## Confirm OpenWA is working

Health check:

```bash
curl http://OPENWA_HOST:2785/api/health
```

Check sessions:

```bash
curl -H "X-API-Key: OPENWA_API_KEY" \
  http://OPENWA_HOST:2785/api/sessions
```

Send a direct OpenWA test message:

```bash
curl -X POST \
  -H "X-API-Key: OPENWA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "15551234567@c.us",
    "text": "Test from OpenWA"
  }' \
  "http://OPENWA_HOST:2785/api/sessions/OPENWA_SESSION_ID/messages/send-text"
```

## Service

This integration provides one service:

```yaml
openwa_whatsapp.send_message
```

### Service data

| Field | Required | Description |
|---|---:|---|
| `chat_id` | Yes | WhatsApp chat ID, such as `15551234567@c.us` |
| `message` | Yes | Message text to send |
| `entry_id` | No | Optional config entry ID when using multiple OpenWA instances |

## Send a message

```yaml
action: openwa_whatsapp.send_message
data:
  chat_id: "15551234567@c.us"
  message: "Hello from Home Assistant"
```

## Chat ID format

Individual recipients use the full international phone number without `+`, followed by `@c.us`.

```text
15551234567@c.us
```

Groups usually end with `@g.us`.

```text
123456789012345@g.us
```

## Example automation

```yaml
alias: WhatsApp light notification
mode: single

triggers:
  - trigger: state
    entity_id: light.example_light
    to: "on"

actions:
  - action: openwa_whatsapp.send_message
    data:
      chat_id: "15551234567@c.us"
      message: "Example light turned on"
```

## Example with a templated message

```yaml
alias: WhatsApp entity state notification
mode: single

triggers:
  - trigger: state
    entity_id: binary_sensor.example_door
    to: "on"

actions:
  - action: openwa_whatsapp.send_message
    data:
      chat_id: "15551234567@c.us"
      message: >
        {{ trigger.to_state.name }} changed to {{ trigger.to_state.state }}
```

## Using Home Assistant secrets

In `secrets.yaml`:

```yaml
openwa_primary_recipient: "15551234567@c.us"
openwa_secondary_recipient: "15557654321@c.us"
```

In automation YAML:

```yaml
actions:
  - action: openwa_whatsapp.send_message
    data:
      chat_id: !secret openwa_primary_recipient
      message: "Motion detected"
```

Some Home Assistant UI editors may not preserve `!secret` values cleanly inside automation action data. If that happens, use YAML mode or create wrapper scripts.

## Recommended wrapper scripts

```yaml
whatsapp_primary:
  alias: WhatsApp Primary
  mode: single
  fields:
    message:
      description: Message to send
      example: "Garage door opened"
  sequence:
    - action: openwa_whatsapp.send_message
      data:
        chat_id: !secret openwa_primary_recipient
        message: "{{ message }}"
```

Then automations can use:

```yaml
actions:
  - action: script.whatsapp_primary
    data:
      message: "Garage door opened"
```

## Troubleshooting

### Cannot connect

Check:

```bash
curl http://OPENWA_HOST:2785/api/health
```

### Invalid API key

Verify the key:

```bash
docker logs openwa 2>&1 | grep -i -A4 -B4 "api key"
```

Then test it:

```bash
curl -H "X-API-Key: OPENWA_API_KEY" \
  http://OPENWA_HOST:2785/api/sessions
```

### Session is not ready

Check sessions:

```bash
curl -H "X-API-Key: OPENWA_API_KEY" \
  http://OPENWA_HOST:2785/api/sessions
```

The session should show a ready or connected state.

### Message returns an error

Test OpenWA directly:

```bash
curl -X POST \
  -H "X-API-Key: OPENWA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "15551234567@c.us",
    "text": "Direct OpenWA test"
  }' \
  "http://OPENWA_HOST:2785/api/sessions/OPENWA_SESSION_ID/messages/send-text"
```

## Privacy and security

Do not commit real values to a public repository.

Never publish:

- Real OpenWA API keys
- Real OpenWA session IDs
- Real IP addresses or hostnames
- Real WhatsApp phone numbers
- Real recipient names

Use placeholders in examples:

```text
OPENWA_HOST
OPENWA_API_KEY
OPENWA_SESSION_ID
PRIMARY_RECIPIENT
SECONDARY_RECIPIENT
15551234567@c.us
```

Recommended:

- Store API keys securely.
- Keep OpenWA on a private LAN or behind proper authentication.
- Do not expose OpenWA directly to the public internet.
- Use Home Assistant `secrets.yaml` for recipient chat IDs where practical.
- Rotate any key that was shared in logs, screenshots, commits, or chat.

## Development

Repository layout:

```text
homeassistant-openwa-whatsapp/
├── README.md
├── hacs.json
└── custom_components/
    └── openwa_whatsapp/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── manifest.json
        ├── services.yaml
        └── translations/
            └── en.json
```

Check Python syntax:

```bash
python3 -m py_compile custom_components/openwa_whatsapp/*.py
```

## Disclaimer

This integration is not affiliated with WhatsApp, Meta, or OpenWA.

Use responsibly and follow the terms and policies of the services you connect to.