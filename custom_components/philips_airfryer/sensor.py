from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from .const import DOMAIN, CONF_PROBE

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        # --- Normale Sensoren ---
        AirfryerSensor(coordinator, "status", "status", None, "mdi:state-machine"),
        AirfryerSensor(coordinator, "temp", "current_temp", "°C", "mdi:thermometer"),
        AirfryerSensor(coordinator, "method", "cooking_method", None, "mdi:chef-hat"),
        
        AirfryerProgressSensor(coordinator),
        AirfryerDialogSensor(coordinator),
        
        # --- Diagnose Sensoren ---
        AirfryerTokenSensor(coordinator),
        AirfryerDiagnosticSensor(coordinator, "_display_remaining", "diag_disp_time", "s"),
        AirfryerDiagnosticSensor(coordinator, "_display_total", "diag_total_time", "s"),
        AirfryerDiagnosticSensor(coordinator, "timestamp", "diag_timestamp", None),
        AirfryerDiagnosticSensor(coordinator, "voltage", "voltage", "V", "mdi:current-ac"),
        AirfryerDiagnosticSensor(coordinator, "internal_temp", "internal_temp", "°C", "mdi:thermometer"),
        AirfryerDiagnosticSensor(coordinator, "error", "error_code", None, "mdi:alert-circle-outline"),
        AirfryerDiagnosticSensor(coordinator, "prev_status", "prev_status", None, "mdi:history"),
        AirfryerDiagnosticSensor(coordinator, "cooking_id", "cooking_id", None, "mdi:identifier"),
        AirfryerDiagnosticSensor(coordinator, "step_id", "step_id", None, "mdi:format-list-numbered"),
        AirfryerDiagnosticSensor(coordinator, "cur_stage", "cur_stage", None, "mdi:stairs"),
        
        # Firmware & AutoCook & Recipe
        AirfryerFirmwareSensor(coordinator),
        AirfryerAutoCookSensor(coordinator),
        AirfryerRecipeSensor(coordinator),
    ]
    
    if entry.options.get(CONF_PROBE):
        sensors.append(AirfryerSensor(coordinator, "temp_probe", "probe_temp", "°C", "mdi:thermometer"))
        
    async_add_entities(sensors)

class AirfryerBaseSensor(CoordinatorEntity):
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

class AirfryerSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator, key, trans_key, unit, icon=None):
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = trans_key
        self._unit = unit
        self._attr_unique_id = f"{DOMAIN}_{key}"
        if icon:
            self._attr_icon = icon

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        return self.coordinator.data.get(self._key)

    @property
    def native_unit_of_measurement(self):
        return self._unit

class AirfryerProgressSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "progress"
        self._attr_unique_id = f"{DOMAIN}_progress"
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:progress-clock"
    
    @property
    def native_value(self):
        data = self.coordinator.data
        if not data: return 0
        total = data.get("_display_total", 0) or 0
        rem = data.get("_display_remaining", 0) or 0
        if total > 0: return round(((total - rem) / total) * 100, 1)
        return 0

class AirfryerDialogSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "dialog"
        self._attr_unique_id = f"{DOMAIN}_dialog"
        self._attr_icon = "mdi:message-alert-outline"
    
    @property
    def native_value(self):
        if not self.coordinator.data: return "offline"
        val = self.coordinator.data.get("dialog")
        return val if val != "none" else "OK"

class AirfryerTokenSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "token"
        self._attr_unique_id = f"{DOMAIN}_token"
        self._attr_icon = "mdi:key-variant"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.client.token

class AirfryerDiagnosticSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator, key, trans_key, unit, icon="mdi:information-outline"):
        super().__init__(coordinator)
        self._key = key
        self._attr_translation_key = trans_key
        self._unit = unit
        self._attr_unique_id = f"{DOMAIN}_{key}"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = icon

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        return self.coordinator.data.get(self._key)

    @property
    def native_unit_of_measurement(self):
        return self._unit

class AirfryerFirmwareSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "fw_state"
        self._attr_unique_id = f"{DOMAIN}_fw_state"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:update"

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        return self.coordinator.data.get("fw_state")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data: return {}
        fw_data = self.coordinator.data.get("fw_response", {})
        return {
            "upgrade_available": fw_data.get("upgrade"),
            "versions": fw_data.get("versions"),
            "progress": fw_data.get("progress"),
            "mandatory": fw_data.get("mandatory"),
            "can_upgrade": fw_data.get("canupgrade"),
            "can_download": fw_data.get("candownload"),
            "status_msg": fw_data.get("statusmsg"),
            "size": fw_data.get("size")
        }

class AirfryerAutoCookSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "autocook_program"
        self._attr_unique_id = f"{DOMAIN}_autocook_program"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:script-text-outline"

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        data = self.coordinator.data.get("auto_cook_response", {})
        return data.get("UUID")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data: return {}
        data = self.coordinator.data.get("auto_cook_response", {})
        return {
            "u1": data.get("u1"),
            "u2": data.get("u2"),
            "u3": data.get("u3"),
            "doneness": data.get("doneness")
        }

class AirfryerRecipeSensor(AirfryerBaseSensor, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_translation_key = "recipe_id"
        self._attr_unique_id = f"{DOMAIN}_recipe_id"
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        self._attr_icon = "mdi:book-open-variant"

    @property
    def native_value(self):
        if not self.coordinator.data: return None
        data = self.coordinator.data.get("recipe_response", {})
        return data.get("recipe_id")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data: return {}
        data = self.coordinator.data.get("recipe_response", {})
        return {
            "cur_stage": data.get("cur_stage"),
            "tu": data.get("tu"),
            "stages": data.get("stages")
        }