from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CONF_PROBE

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        AirfryerDrawerSensor(coordinator),
        AirfryerPreheatSensor(coordinator),
        AirfryerRestingSensor(coordinator),
        AirfryerProbeRequiredSensor(coordinator)
    ]
    
    if entry.options.get(CONF_PROBE): 
        sensors.append(AirfryerProbeConnectedSensor(coordinator))
        
    async_add_entities(sensors)

class AirfryerBaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
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

class AirfryerDrawerSensor(AirfryerBaseBinarySensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "drawer"
        self._attr_unique_id = f"{DOMAIN}_drawer"
        self._attr_device_class = BinarySensorDeviceClass.DOOR

    @property
    def is_on(self):
        if not self.coordinator.data: return None
        return self.coordinator.data.get("drawer_open")

class AirfryerProbeConnectedSensor(AirfryerBaseBinarySensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "probe_connected"
        self._attr_unique_id = f"{DOMAIN}_probe_plugged"
        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_icon = "mdi:thermometer-probe"

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        # Logik: Wenn NICHT unplugged, dann ist sie verbunden
        return not self.coordinator.data.get("probe_unplugged")

class AirfryerPreheatSensor(AirfryerBaseBinarySensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "preheat"
        self._attr_unique_id = f"{DOMAIN}_preheat"
        self._attr_device_class = BinarySensorDeviceClass.HEAT
        self._attr_icon = "mdi:fire"

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        return self.coordinator.data.get("preheat")

class AirfryerRestingSensor(AirfryerBaseBinarySensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "resting"
        self._attr_unique_id = f"{DOMAIN}_resting"
        self._attr_icon = "mdi:pot-steam" # Oder mdi:timer-sand

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        return self.coordinator.data.get("resting")

class AirfryerProbeRequiredSensor(AirfryerBaseBinarySensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "probe_required"
        self._attr_unique_id = f"{DOMAIN}_probe_required"
        self._attr_icon = "mdi:thermometer-alert"

    @property
    def is_on(self):
        if not self.coordinator.data: return False
        return self.coordinator.data.get("probe_required")