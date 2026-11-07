"""Polling-frequency control: __init__.py handles the update-triggered reload."""

import logging

from homeassistant.components.number import (
    NumberEntity,
)

from .const import (
    DOMAIN,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    MIN_REFRESH_INTERVAL,
    MAX_REFRESH_INTERVAL,
)

_LOGGER = logging.getLogger(
    __name__
)


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    coordinator = hass.data[
        DOMAIN
    ][entry.entry_id]

    async_add_entities(
        [
            BrioWilRefreshFrequency(
                hass,
                entry,
                coordinator,
            )
        ]
    )


class BrioWilRefreshFrequency(
    NumberEntity,
):

    def __init__(
        self,
        hass,
        entry,
        coordinator,
    ):

        self.hass = hass
        self.entry = entry
        self.coordinator = coordinator

        self._attr_name = (
            "Refresh Frequency"
        )

        self._attr_unique_id = (
            f"briowil_refresh_frequency_{coordinator.server_ip}"
        )

        self._attr_native_min_value = (
            MIN_REFRESH_INTERVAL
        )

        self._attr_native_max_value = (
            MAX_REFRESH_INTERVAL
        )

        self._attr_native_step = 1

        self._attr_native_unit_of_measurement = "s"

    @property
    def device_info(
        self,
    ):

        return {
            "identifiers": {
                (
                    DOMAIN,
                    self.coordinator.server_ip,
                )
            },
            "name": "BrioWil Server",
            "manufacturer": "BrioWil",
            "model": "TCP Pool Controller",
        }

    @property
    def native_value(
        self,
    ):

        return self.entry.options.get(
            CONF_REFRESH_INTERVAL,
            DEFAULT_REFRESH_INTERVAL,
        )

    async def async_set_native_value(
        self,
        value,
    ):

        value = int(
            value
        )

        _LOGGER.debug(
            "Setting BrioWil refresh frequency to %s seconds",
            value,
        )

        self.hass.config_entries.async_update_entry(
            self.entry,
            options={
                **self.entry.options,
                CONF_REFRESH_INTERVAL: value,
            },
        )
        # The config-entry options listener will automatically reload.
