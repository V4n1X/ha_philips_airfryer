import voluptuous as vol
import os
import sqlite3
import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.helpers.selector import FileSelector, FileSelectorConfig
from homeassistant.const import CONF_HOST, CONF_CLIENT_ID, CONF_CLIENT_SECRET
from .const import (
    DOMAIN, CONF_COMMAND_URL, CONF_AIRSPEED, CONF_PROBE, 
    CONF_REPLACE_TIMESTAMP, CONF_TIME_REMAINING, CONF_TIME_TOTAL, CONF_UPDATE_INTERVAL,
    DEFAULT_COMMAND_URL, DEFAULT_AIRSPEED, DEFAULT_PROBE,
    DEFAULT_REPLACE_TIMESTAMP, DEFAULT_TIME_REMAINING, DEFAULT_TIME_TOTAL, DEFAULT_UPDATE_INTERVAL
)
from .airfryer_api import PhilipsAirfryerClient

_LOGGER = logging.getLogger(__name__)

class PhilipsAirfryerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PhilipsAirfryerOptionsFlowHandler(config_entry)

    def _get_schema(self, defaults=None):
        if defaults is None:
            defaults = {}
        
        def get_def(key, fallback):
            return defaults.get(key, fallback)

        return vol.Schema({
            # Verbindungsdaten
            vol.Required(CONF_HOST, default=get_def(CONF_HOST, "")): str,
            vol.Required(CONF_CLIENT_ID, default=get_def(CONF_CLIENT_ID, "")): str,
            vol.Required(CONF_CLIENT_SECRET, default=get_def(CONF_CLIENT_SECRET, "")): str,
            
            # Einstellungen
            vol.Optional(CONF_COMMAND_URL, default=get_def(CONF_COMMAND_URL, DEFAULT_COMMAND_URL)): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=get_def(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=600)),
            vol.Optional(CONF_AIRSPEED, default=get_def(CONF_AIRSPEED, DEFAULT_AIRSPEED)): bool,
            vol.Optional(CONF_PROBE, default=get_def(CONF_PROBE, DEFAULT_PROBE)): bool,
            vol.Optional(CONF_REPLACE_TIMESTAMP, default=get_def(CONF_REPLACE_TIMESTAMP, DEFAULT_REPLACE_TIMESTAMP)): bool,
            vol.Optional(CONF_TIME_REMAINING, default=get_def(CONF_TIME_REMAINING, DEFAULT_TIME_REMAINING)): str,
            vol.Optional(CONF_TIME_TOTAL, default=get_def(CONF_TIME_TOTAL, DEFAULT_TIME_TOTAL)): str,
        })

    async def async_step_user(self, user_input=None):
        """Erster Schritt: Auswahl zwischen Manuell oder Datei-Upload."""
        return self.async_show_menu(
            step_id="user",
            menu_options=["manual", "upload_file"]
        )

    async def async_step_manual(self, user_input=None):
        """Manueller Modus."""
        errors = {}
        if user_input is not None:
            return await self._validate_and_create(user_input, errors, step_id="manual")

        return self.async_show_form(step_id="manual", data_schema=self._get_schema(), errors=errors)

    async def async_step_upload_file(self, user_input=None):
        """Schritt für Datei-Upload."""
        errors = {}
        
        if user_input is not None:
            uploaded_file_id = user_input.get("file_id")
            if uploaded_file_id:
                try:
                    # Verarbeitung im Executor, da sqlite3 blockierend ist
                    extracted_data = await self.hass.async_add_executor_job(
                        self._process_uploaded_db, uploaded_file_id
                    )
                    
                    if extracted_data:
                        # Daten erfolgreich extrahiert -> Vorausfüllen
                        defaults = {
                            CONF_HOST: extracted_data.get("ip_address", ""),
                            CONF_CLIENT_ID: extracted_data.get("client_id", ""),
                            CONF_CLIENT_SECRET: extracted_data.get("client_secret", ""),
                            CONF_COMMAND_URL: DEFAULT_COMMAND_URL,
                            CONF_UPDATE_INTERVAL: DEFAULT_UPDATE_INTERVAL
                        }
                        
                        return self.async_show_form(
                            step_id="manual", 
                            data_schema=self._get_schema(defaults=defaults), 
                            errors={}
                        )
                    else:
                        errors["base"] = "db_empty_or_invalid"
                except Exception as e:
                    _LOGGER.error(f"Fehler beim Verarbeiten der Datei: {e}")
                    errors["base"] = "db_read_error"
            else:
                errors["base"] = "no_file_selected"

        return self.async_show_form(
            step_id="upload_file",
            data_schema=vol.Schema({
                vol.Required("file_id"): FileSelector(
                    config=FileSelectorConfig(accept=".db")
                )
            }),
            errors=errors
        )

    def _process_uploaded_db(self, file_id):
        """Hilfsfunktion: Verarbeitet den Upload Context und liest die DB."""
        # process_uploaded_file liefert einen Context Manager mit dem Pfad zur temp. Datei
        with process_uploaded_file(self.hass, file_id) as file_path:
            return self._read_db_file(file_path)

    def _read_db_file(self, path):
        """Liest die SQLite Datei."""
        data = {}
        try:
            # Wir verbinden uns zur temporären Datei
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT ip_address, client_id, client_secret FROM network_node LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                data["ip_address"] = row["ip_address"]
                data["client_id"] = row["client_id"]
                data["client_secret"] = row["client_secret"]
            
            conn.close()
            return data
        except sqlite3.Error as e:
            _LOGGER.error(f"SQLite Fehler: {e}")
            raise e

    async def _validate_and_create(self, user_input, errors, step_id):
        """Validierungslogik."""
        host_clean = user_input[CONF_HOST].replace("http://", "").replace("https://", "").replace("/", "").strip()
        user_input[CONF_HOST] = host_clean
        user_input[CONF_CLIENT_ID] = user_input[CONF_CLIENT_ID].strip()
        user_input[CONF_CLIENT_SECRET] = user_input[CONF_CLIENT_SECRET].strip()

        client = PhilipsAirfryerClient(user_input[CONF_HOST], user_input[CONF_CLIENT_ID], user_input[CONF_CLIENT_SECRET])
        if user_input.get(CONF_COMMAND_URL):
            client.url = f"https://{user_input[CONF_HOST]}{user_input[CONF_COMMAND_URL]}"

        try:
            await self.hass.async_add_executor_job(client.get_status)
            
            data = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
            }
            options = {k: v for k, v in user_input.items() if k not in data}

            return self.async_create_entry(title="Philips Airfryer", data=data, options=options)
        except Exception:
            errors["base"] = "cannot_connect"
        
        return self.async_show_form(step_id=step_id, data_schema=self._get_schema(defaults=user_input), errors=errors)

class PhilipsAirfryerOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _get_schema(self, defaults=None):
        if defaults is None: defaults = {}
        def get_def(key, fallback): return defaults.get(key, fallback)

        return vol.Schema({
            vol.Required(CONF_HOST, default=get_def(CONF_HOST, "")): str,
            vol.Required(CONF_CLIENT_ID, default=get_def(CONF_CLIENT_ID, "")): str,
            vol.Required(CONF_CLIENT_SECRET, default=get_def(CONF_CLIENT_SECRET, "")): str,
            
            vol.Optional(CONF_COMMAND_URL, default=get_def(CONF_COMMAND_URL, DEFAULT_COMMAND_URL)): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=get_def(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)): vol.All(vol.Coerce(int), vol.Range(min=5, max=600)),
            vol.Optional(CONF_AIRSPEED, default=get_def(CONF_AIRSPEED, DEFAULT_AIRSPEED)): bool,
            vol.Optional(CONF_PROBE, default=get_def(CONF_PROBE, DEFAULT_PROBE)): bool,
            vol.Optional(CONF_REPLACE_TIMESTAMP, default=get_def(CONF_REPLACE_TIMESTAMP, DEFAULT_REPLACE_TIMESTAMP)): bool,
            vol.Optional(CONF_TIME_REMAINING, default=get_def(CONF_TIME_REMAINING, DEFAULT_TIME_REMAINING)): str,
            vol.Optional(CONF_TIME_TOTAL, default=get_def(CONF_TIME_TOTAL, DEFAULT_TIME_TOTAL)): str,
        })

    async def async_step_init(self, user_input=None):
        errors = {}
        current_config = {**self._config_entry.data, **self._config_entry.options}

        if user_input is not None:
            host_clean = user_input[CONF_HOST].replace("http://", "").replace("https://", "").replace("/", "").strip()
            user_input[CONF_HOST] = host_clean
            user_input[CONF_CLIENT_ID] = user_input[CONF_CLIENT_ID].strip()
            user_input[CONF_CLIENT_SECRET] = user_input[CONF_CLIENT_SECRET].strip()

            client = PhilipsAirfryerClient(user_input[CONF_HOST], user_input[CONF_CLIENT_ID], user_input[CONF_CLIENT_SECRET])
            if user_input.get(CONF_COMMAND_URL):
                client.url = f"https://{user_input[CONF_HOST]}{user_input[CONF_COMMAND_URL]}"

            try:
                await self.hass.async_add_executor_job(client.get_status)
                
                new_data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_CLIENT_ID: user_input[CONF_CLIENT_ID],
                    CONF_CLIENT_SECRET: user_input[CONF_CLIENT_SECRET],
                }
                new_options = {k: v for k, v in user_input.items() if k not in new_data}

                self.hass.config_entries.async_update_entry(self._config_entry, data=new_data)
                return self.async_create_entry(title="", data=new_options)
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(step_id="init", data_schema=self._get_schema(defaults=current_config), errors=errors)