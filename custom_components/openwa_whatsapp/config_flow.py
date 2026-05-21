"""Config flow for OpenWA WhatsApp."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_HEALTH_PATH,
    API_SESSIONS_PATH,
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_SESSION_ID,
    DEFAULT_NAME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OpenWAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an OpenWA WhatsApp config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.FlowResult:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            base_url = user_input[CONF_BASE_URL].rstrip("/")
            api_key = user_input[CONF_API_KEY]
            session_id = user_input[CONF_SESSION_ID]

            result = await self._validate_input(base_url, api_key)

            if result == "ok":
                await self.async_set_unique_id(f"{base_url}_{session_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=DEFAULT_NAME,
                    data={
                        CONF_BASE_URL: base_url,
                        CONF_API_KEY: api_key,
                        CONF_SESSION_ID: session_id,
                    },
                )

            errors["base"] = result

        schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default="http://OPENWA_HOST:2785"): str,
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_SESSION_ID): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _validate_input(self, base_url: str, api_key: str) -> str:
        """Validate OpenWA connection and API key."""
        session = async_get_clientsession(self.hass)

        health_url = f"{base_url}{API_HEALTH_PATH}"
        sessions_url = f"{base_url}{API_SESSIONS_PATH}"

        try:
            async with session.get(health_url, timeout=10) as response:
                if response.status != 200:
                    _LOGGER.error(
                        "OpenWA health check failed with status %s",
                        response.status,
                    )
                    return "cannot_connect"

            async with session.get(
                sessions_url,
                headers={"X-API-Key": api_key},
                timeout=10,
            ) as response:
                if response.status in (401, 403):
                    return "invalid_auth"

                if response.status < 200 or response.status >= 300:
                    _LOGGER.error(
                        "OpenWA sessions check failed with status %s",
                        response.status,
                    )
                    return "cannot_connect"

        except TimeoutError:
            return "timeout"
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("OpenWA validation failed: %s", err)
            return "cannot_connect"

        return "ok"