"""Integration entry point: create the shared TCP polling coordinator; reload when options change."""

from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import BrioWilCoordinator

PLATFORMS = [
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass,
    entry,
):

    coordinator = BrioWilCoordinator(
        hass,
        entry,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(
        DOMAIN,
        {},
    )

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(
            _async_update_listener
        )
    )

    return True


async def _async_update_listener(
    hass,
    entry,
):

    await hass.config_entries.async_reload(
        entry.entry_id
    )


async def async_unload_entry(
    hass,
    entry,
):

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(
            entry.entry_id,
            None,
        )

    return unload_ok