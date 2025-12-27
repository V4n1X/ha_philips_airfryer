from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([AirfryerStartButton(coordinator), AirfryerPauseButton(coordinator), AirfryerStopButton(coordinator)])

class AirfryerBaseButton(CoordinatorEntity, ButtonEntity):
    _attr_has_entity_name = True

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

class AirfryerStartButton(AirfryerBaseButton):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "start"
        self._attr_unique_id = f"{DOMAIN}_start"
        self._attr_icon = "mdi:play"

    async def async_press(self):
        client = self.coordinator.client
        settings = {"temp": self.coordinator.target_temp, "total_time": self.coordinator.target_time * 60, "method": 0, "probe_required": False, "temp_unit": False}
        if self.coordinator.data and self.coordinator.data.get("airspeed") is not None: 
            settings["airspeed"] = self.coordinator.target_airspeed
        
        await self.hass.async_add_executor_job(client.send_command, {"status": "precook", "probe_required": False, "method": 0, "temp_unit": False})
        await self.hass.async_add_executor_job(client.send_command, settings)
        await self.hass.async_add_executor_job(client.send_command, {"status": "cooking"})
        await self.coordinator.async_request_refresh()

class AirfryerPauseButton(AirfryerBaseButton):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "pause"
        self._attr_unique_id = f"{DOMAIN}_pause"
        self._attr_icon = "mdi:pause"

    async def async_press(self):
        await self.hass.async_add_executor_job(self.coordinator.client.send_command, {"status": "pause"})
        await self.coordinator.async_request_refresh()

class AirfryerStopButton(AirfryerBaseButton):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "stop"
        self._attr_unique_id = f"{DOMAIN}_stop"
        self._attr_icon = "mdi:stop"

    async def async_press(self):
        client = self.coordinator.client
        await self.hass.async_add_executor_job(client.send_command, {"status": "pause"})
        await self.hass.async_add_executor_job(client.send_command, {"status": "mainmenu"})
        await self.coordinator.async_request_refresh()