from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AirfryerPowerSwitch(coordinator)])

class AirfryerPowerSwitch(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "power"
        self._attr_unique_id = f"{DOMAIN}_power"
        self._attr_icon = "mdi:power"

    @property
    def device_info(self) -> DeviceInfo:
        data = self.coordinator.data or {}
        model_name = data.get("fw_name", "Airfryer")
        version = data.get("fw_version")

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.client.host)},
            name=self.coordinator.entry.title,
            manufacturer="Philips",
            model=model_name,
            sw_version=version
        )

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        status = self.coordinator.data.get("status")
        return status not in ["standby", "powersave", "offline", None]

    async def async_turn_on(self, **kwargs):
        await self.hass.async_add_executor_job(self.coordinator.client.send_command, {"status": "precook", "probe_required": False, "method": 0, "temp_unit": False})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.hass.async_add_executor_job(self.coordinator.client.send_command, {"status": "powersave"})
        await self.coordinator.async_request_refresh()