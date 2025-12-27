from homeassistant.components.number import NumberEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_AIRSPEED

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [AirfryerTempNumber(coordinator), AirfryerTimeNumber(coordinator)]
    if entry.options.get(CONF_AIRSPEED):
        entities.append(AirfryerAirspeedNumber(coordinator))
    async_add_entities(entities)

class AirfryerBaseNumber(CoordinatorEntity, NumberEntity):
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

class AirfryerTempNumber(AirfryerBaseNumber):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "target_temp"
        self._attr_unique_id = f"{DOMAIN}_target_temp"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_native_min_value = 40
        self._attr_native_max_value = 200
        self._attr_native_step = 5
        self._attr_icon = "mdi:thermometer-check" # <--- Hier geändert

    @property
    def native_value(self):
        return self.coordinator.target_temp

    async def async_set_native_value(self, value):
        self.coordinator.target_temp = int(value)
        if not self.coordinator.data: return
        status = self.coordinator.data.get("status")
        client = self.coordinator.client
        if status == "cooking":
            await self.hass.async_add_executor_job(client.send_command, {"status": "pause"})
            await self.hass.async_add_executor_job(client.send_command, {"temp": int(value)})
            await self.hass.async_add_executor_job(client.send_command, {"status": "cooking"})
        elif status in ["pause", "precook"]:
            await self.hass.async_add_executor_job(client.send_command, {"temp": int(value)})
        await self.coordinator.async_request_refresh()

class AirfryerTimeNumber(AirfryerBaseNumber):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "target_time"
        self._attr_unique_id = f"{DOMAIN}_target_time"
        self._attr_native_unit_of_measurement = "min"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 180
        self._attr_native_step = 1
        self._attr_icon = "mdi:timer-outline"

    @property
    def native_value(self):
        return self.coordinator.target_time

    async def async_set_native_value(self, value):
        self.coordinator.target_time = int(value)
        if not self.coordinator.data: return
        status = self.coordinator.data.get("status")
        client = self.coordinator.client
        sec = int(value) * 60
        if status == "cooking":
            await self.hass.async_add_executor_job(client.send_command, {"status": "pause"})
            await self.hass.async_add_executor_job(client.send_command, {"total_time": sec})
            await self.hass.async_add_executor_job(client.send_command, {"status": "cooking"})
        elif status in ["pause", "precook"]:
            await self.hass.async_add_executor_job(client.send_command, {"total_time": sec})
        await self.coordinator.async_request_refresh()

class AirfryerAirspeedNumber(AirfryerBaseNumber):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "airspeed"
        self._attr_unique_id = f"{DOMAIN}_airspeed"
        self._attr_native_min_value = 1
        self._attr_native_max_value = 2
        self._attr_native_step = 1
        self._attr_icon = "mdi:fan"

    @property
    def native_value(self):
        return self.coordinator.target_airspeed

    async def async_set_native_value(self, value):
        self.coordinator.target_airspeed = int(value)
        if not self.coordinator.data: return
        await self.hass.async_add_executor_job(self.coordinator.client.send_command, {"airspeed": int(value)})
        await self.coordinator.async_request_refresh()