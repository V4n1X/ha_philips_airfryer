from datetime import datetime, timedelta
import logging
import async_timeout
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import (
    DOMAIN, CONF_REPLACE_TIMESTAMP, CONF_TIME_REMAINING, CONF_TIME_TOTAL, CONF_UPDATE_INTERVAL,
    DEFAULT_TIME_REMAINING, DEFAULT_TIME_TOTAL, DEFAULT_UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

class AirfryerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, client, entry):
        interval_sec = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=interval_sec))
        self.client = client
        self.entry = entry
        self.target_temp = 180
        self.target_time = 15
        self.target_airspeed = 2

    async def _async_update_data(self):
        try:
            async with async_timeout.timeout(30):
                # 1. Haupt-Status
                data = await self.hass.async_add_executor_job(self.client.get_status)
                
                if not data:
                    return self._get_offline_data()

                # 2. Firmware
                try:
                    fw_data = await self.hass.async_add_executor_job(self.client.get_firmware)
                    if fw_data:
                        data["fw_version"] = fw_data.get("version")
                        data["fw_name"] = fw_data.get("name")
                        data["fw_state"] = fw_data.get("state")
                        data["fw_response"] = fw_data 
                except Exception as e:
                    _LOGGER.debug(f"Konnte Firmware nicht laden: {e}")

                # 3. Device State
                try:
                    dev_state = await self.hass.async_add_executor_job(self.client.get_device_state)
                    if dev_state:
                        data["voltage"] = dev_state.get("voltage")
                        data["internal_temp"] = dev_state.get("current_temp")
                except Exception as e:
                    _LOGGER.debug(f"Konnte Device State nicht laden: {e}")

                # 4. Auto Cook Program
                try:
                    ac_data = await self.hass.async_add_executor_job(self.client.get_autocook_program)
                    if ac_data:
                        data["auto_cook_response"] = ac_data
                except Exception as e:
                     _LOGGER.debug(f"Konnte AutoCook Program nicht laden: {e}")

                # 5. Recipe
                try:
                    recipe_data = await self.hass.async_add_executor_job(self.client.get_recipe)
                    if recipe_data:
                        data["recipe_response"] = recipe_data
                except Exception as e:
                     _LOGGER.debug(f"Konnte Recipe nicht laden: {e}")

                # --- Datenaufbereitung ---
                options = self.entry.options
                key_rem = options.get(CONF_TIME_REMAINING, DEFAULT_TIME_REMAINING)
                key_tot = options.get(CONF_TIME_TOTAL, DEFAULT_TIME_TOTAL)
                
                data["_display_remaining"] = data.get(key_rem, 0)
                data["_display_total"] = data.get(key_tot, 0)
                
                if options.get(CONF_REPLACE_TIMESTAMP, False):
                    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if data.get("temp", 0) > 0: self.target_temp = data.get("temp")
                if data.get(key_tot, 0) > 0: self.target_time = int(data.get(key_tot) / 60)
                if data.get("airspeed"): self.target_airspeed = data.get("airspeed")
                    
                return data

        except Exception as err:
            _LOGGER.warning(f"Fehler bei Aktualisierung: {err}")
            return self._get_offline_data()

    def _get_offline_data(self):
        return {
            "status": "offline", 
            "temp": 0, 
            "disp_time": 0, 
            "total_time": 0, 
            "drawer_open": False,
            "probe_unplugged": True,
            "dialog": "none",
            "_display_remaining": 0,
            "_display_total": 0,
            "airspeed": 0,
            "error": 0,
            "method": 0,
            "prev_status": "none",
            "preheat": False,
            "resting": False,
            "probe_required": False,
            "cooking_id": "",
            "step_id": "",
            "cur_stage": 0,
            "auto_cook_response": {"UUID": "", "u1": 0, "u2": 0, "u3": 0, "doneness": 0},
            # NEU: Offline Werte für Recipe
            "recipe_response": {"recipe_id": "", "cur_stage": 0, "tu": 0, "stages": []}
        }