"""Read controller status using TCP and decode fixed-width response indexes (zero-based)."""

import logging
import socket

from datetime import timedelta

from homeassistant.core import HomeAssistant

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    DEFAULT_PORT,
    CONF_REFRESH_INTERVAL,
    DEFAULT_REFRESH_INTERVAL,
    COLOR_NUMBER_TO_NAME,
    WINTER_MODE_ENTITY_ID,
)

_LOGGER = logging.getLogger(__name__)


def get_pool_light_status(
    ip,
):

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    sock.settimeout(
        5
    )

    try:

        _LOGGER.debug(
            "Connecting to BrioWil server %s:%s",
            ip,
            DEFAULT_PORT,
        )

        sock.connect(
            (
                ip,
                DEFAULT_PORT,
            )
        )

        sock.shutdown(
            socket.SHUT_WR
        )

        chunks = []

        while True:

            try:

                data = sock.recv(
                    1024
                )

                if not data:
                    break

                chunks.append(
                    data
                )

            except socket.timeout:
                break

        response = b"".join(
            chunks
        ).decode(
            "utf-8",
            errors="ignore",
        )

        _LOGGER.debug(
            "Raw status response: %s",
            response,
        )

        if len(response) >= 72:

            #
            # Power
            # Character 34
            #
            power_char = response[
                33
            ]

            if power_char == "2":

                power = True

            elif power_char == "0":

                power = False

            else:

                power = None

            #
            # Color
            # Characters 65-66
            #
            color_hex = response[
                64:66
            ]

            try:

                color = int(
                    color_hex,
                    16,
                )

            except ValueError:

                _LOGGER.warning(
                    "Invalid color hex value from BrioWil: %s",
                    color_hex,
                )

                color = None

            color_name = (
                COLOR_NUMBER_TO_NAME.get(
                    color
                )
            )

            #
            # Effect Speed
            #
            speed_char = response[
                70
            ]

            try:

                effect_speed = (
                    int(
                        speed_char,
                        16,
                    ) - 4
                )

            except ValueError:

                effect_speed = None

            #
            # Brightness
            #
            brightness_char = response[
                71
            ]

            try:

                brightness_mode = (
                    int(
                        brightness_char,
                        16,
                    ) // 4
                )

            except ValueError:

                brightness_mode = None

            ha_brightness = {
                0: 64,
                1: 128,
                2: 191,
                3: 255,
            }.get(
                brightness_mode
            )

            _LOGGER.debug(
                "Decoded status: power=%s color=%s color_name=%s color_hex=%s effect_speed=%s speed_char=%s brightness_mode=%s brightness_char=%s ha_brightness=%s",
                power,
                color,
                color_name,
                color_hex,
                effect_speed,
                speed_char,
                brightness_mode,
                brightness_char,
                ha_brightness,
            )

            return {
                "power": power,
                "color": color,
                "color_name": color_name,
                "color_hex": color_hex,
                "effect_speed": effect_speed,
                "speed_char": speed_char,
                "brightness_mode": brightness_mode,
                "brightness_char": brightness_char,
                "ha_brightness": ha_brightness,
                "raw_response": response,
            }

        _LOGGER.warning(
            "BrioWil response too short: %s characters",
            len(response),
        )

        return {
            "power": None,
            "color": None,
            "color_name": None,
            "color_hex": None,
            "effect_speed": None,
            "speed_char": None,
            "brightness_mode": None,
            "brightness_char": None,
            "ha_brightness": None,
            "raw_response": response,
        }

    except Exception as err:

        _LOGGER.error(
            "Status request failed: %s",
            err,
        )

        return None

    finally:

        sock.close()


class BrioWilCoordinator(
    DataUpdateCoordinator
):

    def __init__(
        self,
        hass: HomeAssistant,
        entry,
    ):

        self.entry = entry
        self.created_winter_helper = False

        self.server_ip = entry.data[
            "server_ip"
        ]

        refresh_interval = (
            entry.options.get(
                CONF_REFRESH_INTERVAL,
                DEFAULT_REFRESH_INTERVAL,
            )
        )

        _LOGGER.debug(
            "Creating BrioWil coordinator with refresh interval %s seconds",
            refresh_interval,
        )

        super().__init__(
            hass,
            _LOGGER,
            name="BrioWil Pool Light",
            update_interval=timedelta(
                seconds=refresh_interval
            ),
        )

    @property
    def is_winter_mode(self):
        """True when the Home Assistant winter-mode helper is on."""
        return self.hass.states.is_state(WINTER_MODE_ENTITY_ID, "on")

    async def _async_update_data(self):
        """Skip all socket activity during winter mode."""
        if self.is_winter_mode:
            _LOGGER.debug("Winter mode enabled: skipping BrioWil TCP poll")
            return None

        _LOGGER.debug("Polling BrioWil status")
        result = await self.hass.async_add_executor_job(
            get_pool_light_status, self.server_ip
        )
        # A toggle can occur while a network request is already in flight.
        return None if self.is_winter_mode else result