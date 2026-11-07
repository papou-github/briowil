"""Protocol diagnostic sensors: initially disabled in the HA entity registry."""

from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.helpers.entity import (
    EntityCategory,
)

from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
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
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Program Number",
                "program_number",
                "color",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Program Name",
                "program_name",
                "color_name",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Program Hex",
                "program_hex",
                "color_hex",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Brightness Mode",
                "brightness_mode",
                "brightness_mode",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Brightness Character",
                "brightness_character",
                "brightness_char",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Home Assistant Brightness",
                "ha_brightness",
                "ha_brightness",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Effect Speed",
                "effect_speed",
                "effect_speed",
            ),
            BrioWilDiagnosticSensor(
                coordinator,
                "Current Speed Character",
                "speed_character",
                "speed_char",
            ),
        ]
    )


class BrioWilDiagnosticSensor(
    CoordinatorEntity,
    SensorEntity,
):

    def __init__(
        self,
        coordinator,
        name,
        unique_suffix,
        data_key,
    ):

        super().__init__(
            coordinator
        )

        self._attr_name = name

        self._attr_unique_id = (
            f"briowil_{unique_suffix}_{coordinator.server_ip}"
        )

        self._attr_entity_category = (
            EntityCategory.DIAGNOSTIC
        )

        self._attr_entity_registry_enabled_default = (
            False
        )

        self.data_key = data_key

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

        if not self.coordinator.data:
            return None

        return self.coordinator.data.get(
            self.data_key
        )