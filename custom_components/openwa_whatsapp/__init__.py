"""OpenWA WhatsApp integration for Home Assistant."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_SEND_TEXT_PATH,
    ATTR_CHAT_ID,
    ATTR_ENTRY_ID,
    ATTR_MESSAGE,
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_SESSION_ID,
    DOMAIN,
    SERVICE_SEND_MESSAGE,
    SERVICE_START_SESSION,
    API_START_SESSION_PATH,
)

_LOGGER = logging.getLogger(__name__)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_CHAT_ID): str,
        vol.Required(ATTR_MESSAGE): str,
        vol.Optional(ATTR_ENTRY_ID): str,
    }
)

START_SESSION_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): str,
    }
)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the OpenWA WhatsApp integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OpenWA WhatsApp from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_BASE_URL: entry.data[CONF_BASE_URL].rstrip("/"),
        CONF_API_KEY: entry.data[CONF_API_KEY],
        CONF_SESSION_ID: entry.data[CONF_SESSION_ID],
    }

    if not hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_MESSAGE,
            _build_send_message_handler(hass),
            schema=SERVICE_SCHEMA,
        )

    if not hass.services.has_service(DOMAIN, SERVICE_START_SESSION):
        hass.services.async_register(
            DOMAIN,
            SERVICE_START_SESSION,
            _build_start_session_handler(hass),
            schema=START_SESSION_SCHEMA,
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an OpenWA WhatsApp config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.data[DOMAIN] and hass.services.has_service(DOMAIN, SERVICE_SEND_MESSAGE):
        hass.services.async_remove(DOMAIN, SERVICE_SEND_MESSAGE)

    if not hass.data[DOMAIN] and hass.services.has_service(DOMAIN, SERVICE_START_SESSION):
        hass.services.async_remove(DOMAIN, SERVICE_START_SESSION)

    return True


def _build_send_message_handler(hass: HomeAssistant):
    """Create the OpenWA send message service handler."""

    async def async_send_message(call: ServiceCall) -> None:
        """Send a WhatsApp message through OpenWA."""
        entry_id = call.data.get(ATTR_ENTRY_ID)

        if entry_id:
            config = hass.data[DOMAIN].get(entry_id)
            if config is None:
                raise HomeAssistantError(f"OpenWA entry_id not found: {entry_id}")
        else:
            if not hass.data[DOMAIN]:
                raise HomeAssistantError("No OpenWA WhatsApp configuration found")
            config = next(iter(hass.data[DOMAIN].values()))

        chat_id = call.data[ATTR_CHAT_ID]
        message = call.data[ATTR_MESSAGE]

        base_url = config[CONF_BASE_URL]
        api_key = config[CONF_API_KEY]
        session_id = config[CONF_SESSION_ID]

        url = f"{base_url}{API_SEND_TEXT_PATH.format(session_id=session_id)}"

        session = async_get_clientsession(hass)

        try:
            async with session.post(
                url,
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "chatId": chat_id,
                    "text": message,
                },
                timeout=30,
            ) as response:
                response_text = await response.text()

                if response.status < 200 or response.status >= 300:
                    _LOGGER.error(
                        "OpenWA send_message failed. Status: %s. Response: %s",
                        response.status,
                        response_text,
                    )
                    raise HomeAssistantError(
                        f"OpenWA send_message failed with status {response.status}: {response_text}"
                    )

                _LOGGER.debug(
                    "OpenWA message sent successfully. Status: %s. Response: %s",
                    response.status,
                    response_text,
                )

        except TimeoutError as err:
            raise HomeAssistantError("OpenWA request timed out") from err
        except HomeAssistantError:
            raise
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"OpenWA request failed: {err}") from err

    return async_send_message

def _build_start_session_handler(hass: HomeAssistant):
    """Create the OpenWA start session service handler."""

    async def async_start_session(call: ServiceCall) -> None:
        """Start an OpenWA session."""
        entry_id = call.data.get(ATTR_ENTRY_ID)

        if entry_id:
            config = hass.data[DOMAIN].get(entry_id)
            if config is None:
                raise HomeAssistantError(f"OpenWA entry_id not found: {entry_id}")
        else:
            if not hass.data[DOMAIN]:
                raise HomeAssistantError("No OpenWA WhatsApp configuration found")
            config = next(iter(hass.data[DOMAIN].values()))

        base_url = config[CONF_BASE_URL]
        api_key = config[CONF_API_KEY]
        session_id = config[CONF_SESSION_ID]

        url = f"{base_url}{API_START_SESSION_PATH.format(session_id=session_id)}"

        session = async_get_clientsession(hass)

        try:
            async with session.post(
                url,
                headers={
                    "X-API-Key": api_key,
                    "Content-Type": "application/json",
                },
                timeout=30,
            ) as response:
                response_text = await response.text()

                if response.status < 200 or response.status >= 300:
                    _LOGGER.error(
                        "OpenWA start_session failed. Status: %s. Response: %s",
                        response.status,
                        response_text,
                    )
                    raise HomeAssistantError(
                        f"OpenWA start_session failed with status {response.status}: {response_text}"
                    )

                _LOGGER.debug(
                    "OpenWA session started successfully. Status: %s. Response: %s",
                    response.status,
                    response_text,
                )

        except TimeoutError as err:
            raise HomeAssistantError("OpenWA request timed out") from err
        except HomeAssistantError:
            raise
        except Exception as err:  # noqa: BLE001
            raise HomeAssistantError(f"OpenWA request failed: {err}") from err

    return async_start_session

