"""Downloadable diagnostics: redact IP addresses and the raw TCP response."""

from homeassistant.components.diagnostics import (
    async_redact_data,
)

from .const import (
    DOMAIN,
    CONF_SERVER_IP,
)

TO_REDACT = {
    CONF_SERVER_IP,
    "raw_response",
}


async def async_get_config_entry_diagnostics(
    hass,
    config_entry,
):

    coordinator = hass.data[
        DOMAIN
    ].get(
        config_entry.entry_id
    )

    coordinator_data = None

    if coordinator is not None:
        coordinator_data = coordinator.data

    return {
        "entry": async_redact_data(
            {
                "title": config_entry.title,
                "data": dict(
                    config_entry.data
                ),
                "options": dict(
                    config_entry.options
                ),
            },
            TO_REDACT,
        ),
        "coordinator": async_redact_data(
            {
                "last_update_success":
                    coordinator.last_update_success
                    if coordinator is not None
                    else None,
                "server_ip":
                    coordinator.server_ip
                    if coordinator is not None
                    else None,
                "data":
                    coordinator_data,
            },
            TO_REDACT,
        ),
    }