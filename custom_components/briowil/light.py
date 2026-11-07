"""Light control: brightness writes reset the hardware to White, so reapply the previous program."""

import asyncio
import logging
import socket

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_HS_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)

from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_PORT,
    EFFECT_MAP,
    HS_COLOR_MAP,
    COLOR_NUMBER_TO_NAME,
    BRIGHTNESS_MAP,
)

_LOGGER = logging.getLogger(__name__)


def send_tcp(ip, payload):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((ip, DEFAULT_PORT))

        _LOGGER.debug(
            "Sending command: %s",
            payload,
        )

        sock.sendall(payload.encode())

    finally:
        sock.close()


def send_color_program(ip, color_number):
    payload = f'{{"prcn":{color_number}}}'
    send_tcp(ip, payload)


def send_brightness(ip, brightness_mode):
    payload = f'{{"plum":{brightness_mode}}}'
    send_tcp(ip, payload)


def nearest_color_number_from_hs(hs_color):
    requested_hue = float(hs_color[0])
    requested_saturation = float(hs_color[1])

    best_number = None
    best_distance = None

    for color_number, known_hs in HS_COLOR_MAP.items():
        known_hue = float(known_hs[0])
        known_saturation = float(known_hs[1])

        hue_distance = abs(requested_hue - known_hue)
        hue_distance = min(
            hue_distance,
            360 - hue_distance,
        )

        saturation_distance = abs(
            requested_saturation - known_saturation
        )

        distance = (
            hue_distance * 2
            + saturation_distance
        )

        if (
            best_distance is None
            or distance < best_distance
        ):
            best_distance = distance
            best_number = color_number

    return best_number


def brightness_to_mode(brightness):
    if brightness <= 64:
        return 0

    if brightness <= 128:
        return 1

    if brightness <= 191:
        return 2

    return 3


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
            BrioWilPoolLight(
                coordinator
            )
        ]
    )


class BrioWilPoolLight(
    CoordinatorEntity,
    RestoreEntity,
    LightEntity,
):

    def __init__(
        self,
        coordinator,
    ):
        super().__init__(
            coordinator
        )

        self._attr_name = "Pool Light"

        self._attr_unique_id = (
            f"briowil_pool_light_{coordinator.server_ip}"
        )

        self._attr_supported_color_modes = {
            ColorMode.HS
        }

        self._attr_color_mode = ColorMode.HS

        self._attr_effect_list = list(
            EFFECT_MAP.keys()
        )

        self._attr_supported_features = (
            LightEntityFeature.EFFECT
        )

    @property
    def device_info(self):
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
    def is_on(self):
        if not self.coordinator.data:
            return False

        return self.coordinator.data.get(
            "power",
            False,
        )

    @property
    def brightness(self):
        if not self.coordinator.data:
            return None

        brightness_mode = self.coordinator.data.get(
            "brightness_mode"
        )

        return BRIGHTNESS_MAP.get(
            brightness_mode
        )

    @property
    def hs_color(self):
        if not self.coordinator.data:
            return None

        color_number = self.coordinator.data.get(
            "color"
        )

        return HS_COLOR_MAP.get(
            color_number
        )

    @property
    def effect(self):
        if not self.coordinator.data:
            return None

        color_number = self.coordinator.data.get(
            "color"
        )

        color_name = COLOR_NUMBER_TO_NAME.get(
            color_number
        )

        if color_name in EFFECT_MAP:
            return color_name

        return None

    async def async_turn_on(
        self,
        **kwargs,
    ):
        if self.coordinator.is_winter_mode:
            raise HomeAssistantError("BrioWil is unavailable during winter mode")

        #
        # Brightness changes are handled separately.
        # Some Home Assistant cards may send brightness
        # together with hs_color. For BrioWil, that can
        # accidentally switch the program to White.
        #
        # So:
        # 1. remember the current BrioWil program
        # 2. send brightness
        # 3. re-apply the previous program
        # 4. refresh
        # 5. return
        #
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[
                ATTR_BRIGHTNESS
            ]

            brightness_mode = brightness_to_mode(
                brightness
            )

            current_color_number = None

            if self.coordinator.data:
                current_color_number = self.coordinator.data.get(
                    "color"
                )

            _LOGGER.debug(
                "Setting brightness: HA=%s mode=%s preserving_program=%s",
                brightness,
                brightness_mode,
                current_color_number,
            )

            await self.hass.async_add_executor_job(
                send_brightness,
                self.coordinator.server_ip,
                brightness_mode,
            )

            if current_color_number is not None:
                await asyncio.sleep(1)

                _LOGGER.debug(
                    "Re-applying program after brightness change: %s",
                    current_color_number,
                )

                await self.hass.async_add_executor_job(
                    send_color_program,
                    self.coordinator.server_ip,
                    current_color_number,
                )

            await asyncio.sleep(1)

            await self.coordinator.async_request_refresh()

            return

        if ATTR_EFFECT in kwargs:
            effect = kwargs[
                ATTR_EFFECT
            ]

            color_number = EFFECT_MAP.get(
                effect
            )

            if color_number is not None:
                _LOGGER.debug(
                    "Setting effect: %s (%s)",
                    effect,
                    color_number,
                )

                await self.hass.async_add_executor_job(
                    send_color_program,
                    self.coordinator.server_ip,
                    color_number,
                )

                await asyncio.sleep(1)

                await self.coordinator.async_request_refresh()

                return

        if ATTR_HS_COLOR in kwargs:
            hs_color = kwargs[
                ATTR_HS_COLOR
            ]

            color_number = nearest_color_number_from_hs(
                hs_color
            )

            color_name = COLOR_NUMBER_TO_NAME.get(
                color_number
            )

            _LOGGER.debug(
                "Setting color from HS %s -> %s (%s)",
                hs_color,
                color_name,
                color_number,
            )

            await self.hass.async_add_executor_job(
                send_color_program,
                self.coordinator.server_ip,
                color_number,
            )

            await asyncio.sleep(1)

            await self.coordinator.async_request_refresh()

            return

        _LOGGER.debug(
            "Turning light on"
        )

        await self.hass.async_add_executor_job(
            send_tcp,
            self.coordinator.server_ip,
            '{"sprj":1}',
        )

        await asyncio.sleep(1)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(
        self,
        **kwargs,
    ):
        if self.coordinator.is_winter_mode:
            raise HomeAssistantError("BrioWil is unavailable during winter mode")
        _LOGGER.debug(
            "Turning light off"
        )

        await self.hass.async_add_executor_job(
            send_tcp,
            self.coordinator.server_ip,
            '{"sprj":0}',
        )

        await asyncio.sleep(1)

        await self.coordinator.async_request_refresh()