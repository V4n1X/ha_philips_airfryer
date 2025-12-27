import logging
import requests
import json
import base64
import hashlib
import threading
import time

_LOGGER = logging.getLogger(__name__)

class PhilipsAirfryerClient:
    def __init__(self, host, client_id, client_secret):
        self.host = host
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = ""
        self.session = requests.Session()
        requests.packages.urllib3.disable_warnings()
        self.base_url = f"https://{self.host}"
        # Standard URL für Status
        self.url = f"{self.base_url}/di/v1/products/1/venusaf"
        
        self._lock = threading.Lock()

    def _decode(self, txt):
        return base64.standard_b64decode(txt)

    def _get_auth(self, challenge):
        vvv = self._decode(challenge) + self._decode(self.client_id) + self._decode(self.client_secret)
        myhash = hashlib.sha256(vvv).hexdigest()
        myhashhex = bytes.fromhex(myhash)
        res = self._decode(self.client_id) + myhashhex
        encoded = base64.b64encode(res)
        return encoded.decode("ascii")

    def _request(self, method, endpoint, data=None):
        if endpoint.startswith("http"):
            url = endpoint
        else:
            url = f"{self.base_url}{endpoint}"
        
        with self._lock:
            headers = {"User-Agent": "cml", "Content-Type": "application/json"}
            if self.token:
                headers["Authorization"] = f"PHILIPS-Condor {self.token}"

            try:
                if method == "GET":
                    response = self.session.get(url, headers=headers, verify=False, timeout=10)
                else:
                    response = self.session.put(url, headers=headers, data=json.dumps(data), verify=False, timeout=10)
                    time.sleep(0.1)

                if response.status_code == 401:
                    _LOGGER.info(f"Token abgelaufen bei {endpoint}, erneuere...")
                    challenge = response.headers.get('WWW-Authenticate')
                    if challenge:
                        challenge = challenge.replace('PHILIPS-Condor ', '')
                        self.token = self._get_auth(challenge)
                        headers["Authorization"] = f"PHILIPS-Condor {self.token}"
                        if method == "GET":
                            response = self.session.get(url, headers=headers, verify=False, timeout=10)
                        else:
                            response = self.session.put(url, headers=headers, data=json.dumps(data), verify=False, timeout=10)

                if response.status_code == 200:
                    return response.json()
                else:
                    _LOGGER.debug(f"API Fehler {url}: Status {response.status_code}")
                    return None
            except Exception as e:
                _LOGGER.error(f"Verbindungsfehler bei {url}: {e}")
                return None

    def get_status(self):
        return self._request("GET", self.url)

    def send_command(self, command):
        return self._request("PUT", self.url, command)

    def get_firmware(self):
        return self._request("GET", "/di/v1/products/0/firmware")

    def get_device_state(self):
        return self._request("GET", "/di/v1/products/1/devcurrstate")

    def get_autocook_program(self):
        return self._request("GET", "/di/v1/products/1/autocookprogram")

    def get_recipe(self):
        # Neuer Endpunkt für Rezepte
        return self._request("GET", "/di/v1/products/1/recipe")