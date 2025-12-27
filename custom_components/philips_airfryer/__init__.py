import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_HOST, CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_COMMAND_URL
from .airfryer_api import PhilipsAirfryerClient
from .coordinator import AirfryerCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor", "switch", "number", "button"]

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    config = {**entry.data, **entry.options}
    
    client = PhilipsAirfryerClient(
        config[CONF_HOST],
        config[CONF_CLIENT_ID],
        config[CONF_CLIENT_SECRET]
    )
    if config.get(CONF_COMMAND_URL):
        client.url = f"https://{config[CONF_HOST]}{config[CONF_COMMAND_URL]}"

    coordinator = AirfryerCoordinator(hass, client, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)