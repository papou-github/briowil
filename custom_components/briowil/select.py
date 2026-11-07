"""Effect-speed control: pspd=0 Slow, 1 Medium, 2 Fast."""

import asyncio
import logging
import socket

from homeassistant.components.select import (
    SelectEntity,
)

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    EFFECT_SPEED_MAP,
    EFFECT_SPEED_NUMBER_TO_NAME,
)

_LOGGER = logging.getLogger(__name__)


def send_effect_speed(
    ip,
    speed_number,
):

    payload = (
        f'{{"pspd":{speed_number}}}'
    )

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.settimeout(5)

    try:

        sock.connect(
            (
                ip,
                DEFAULT_PORT,
            )
        )

        _LOGGER.debug(
            "Sending effect speed command: %s",
            payload,
        )

        sock.sendall(
            payload.encode()
        )

    finally:

        sock.close()


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
            BrioWilEffectSpeed(
                coordinator
            )
        ]
    )


class BrioWilEffectSpeed(
    CoordinatorEntity,
    SelectEntity,
):

    def __init__(
        self,
        coordinator,
    ):

        super().__init__(
            coordinator
        )

        self._attr_name = (
            "Effect Speed"
        )

        self._attr_unique_id = (
            f"briowil_effect_speed_{coordinator.server_ip}"
        )

        self._attr_options = list(
            EFFECT_SPEED_MAP.keys()
        )

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
    def available(self):
        return (
            not self.coordinator.is_winter_mode
            and self.coordinator.last_update_success
            and self.coordinator.data is not None
        )

    @property
    def current_option(
        self,
    ):

        if not self.coordinator.data:
            return None

        effect_speed = self.coordinator.data.get(
            "effect_speed"
        )

        return EFFECT_SPEED_NUMBER_TO_NAME.get(
            effect_speed
        )

    async def async_select_option(
        self,
        option,
    ):
        if self.coordinator.is_winter_mode:
            raise HomeAssistantError("BrioWil is unavailable during winter mode")

        speed_number = EFFECT_SPEED_MAP[
            option
        ]

        _LOGGER.debug(
            "Setting effect speed: %s (%s)",
            option,
            speed_number,
        )

        await self.hass.async_add_executor_job(
            send_effect_speed,
            self.coordinator.server_ip,
            speed_number,
        )

        await asyncio.sleep(
            1
        )

        await self.coordinator.async_request_refresh()