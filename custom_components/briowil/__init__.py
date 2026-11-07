"""BrioWil setup and its optional winter-mode input boolean.

A missing input_boolean.mode_hivernage is created as a genuine Home Assistant
InputBoolean entity. It is recreated on startup, restores its previous state,
and is never written directly into Home Assistant's shared .storage files.
An existing helper is reused without modification.
"""

import logging

from homeassistant.components.input_boolean.const import DATA_INPUT_BOOLEAN
from homeassistant.components.input_boolean.entity import InputBoolean
from homeassistant.const import Platform
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, WINTER_MODE_ENTITY_ID
from .coordinator import BrioWilCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.LIGHT, Platform.NUMBER, Platform.SELECT, Platform.SENSOR]


async def _async_ensure_winter_helper(hass, coordinator):
    """Add a working input_boolean only if the requested ID is unused."""
    registry = er.async_get(hass)
    if hass.states.get(WINTER_MODE_ENTITY_ID) or registry.async_get(
        WINTER_MODE_ENTITY_ID
    ):
        _LOGGER.debug("Using existing %s", WINTER_MODE_ENTITY_ID)
        return

    config = {
        "id": "mode_hivernage",
        "name": "Mode hivernage",
        "icon": "mdi:snowflake",
    }
    # Preserve the state when this config entry reloads inside a HA session.
    cached = hass.data[DOMAIN].get("_winter_state")
    if cached is not None:
        config["initial"] = cached

    helper = InputBoolean.from_yaml(config)
    # Avoid a stale registry entry on a Home Assistant restart. The entity
    # remains a genuine input_boolean with turn_on/off and restore_state.
    helper._attr_unique_id = None
    await hass.data[DATA_INPUT_BOOLEAN].component.async_add_entities([helper])
    coordinator.created_winter_helper = True
    _LOGGER.info("Created %s for BrioWil", WINTER_MODE_ENTITY_ID)


async def async_setup_entry(hass, entry):
    """Create optional helper before starting TCP polling."""
    hass.data.setdefault(DOMAIN, {})
    coordinator = BrioWilCoordinator(hass, entry)
    await _async_ensure_winter_helper(hass, coordinator)

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def _winter_changed(event):
        """Immediately publish unavailable, or poll when winter ends."""
        new_state = event.data.get("new_state")
        _LOGGER.debug(
            "Winter mode changed: %s",
            new_state.state if new_state else "removed",
        )
        if coordinator.is_winter_mode:
            coordinator.async_set_updated_data(None)
        else:
            await coordinator.async_request_refresh()

    entry.async_on_unload(
        async_track_state_change_event(hass, [WINTER_MODE_ENTITY_ID], _winter_changed)
    )
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass, entry):
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if coordinator is not None and coordinator.created_winter_helper:
        # Cache state before unloading so an options-triggered reload keeps it.
        state = hass.states.get(WINTER_MODE_ENTITY_ID)
        if state is not None and state.state in ("on", "off"):
            hass.data[DOMAIN]["_winter_state"] = state.state == "on"

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unloaded:
        return False

    if coordinator is not None and coordinator.created_winter_helper:
        await hass.data[DATA_INPUT_BOOLEAN].component.async_remove_entity(
            WINTER_MODE_ENTITY_ID
        )
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
