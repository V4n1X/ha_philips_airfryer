# 🍟 Philips Airfryer Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/github/v/release/V4n1X/ha_philips_airfryer)](https://github.com/V4n1X/ha_philips_airfryer)
[![Maintainer](https://img.shields.io/badge/maintainer-V4n1X-blue)](https://github.com/V4n1X)

A fully native Home Assistant integration for **Philips Connected Airfryers** (e.g., HD9880/90 Series 7000 XXL). 

This integration allows you to monitor and control your Airfryer locally, offering advanced diagnostics, recipe insights, and a seamless setup process using your existing configuration database.

[Deutsche Version](README_DE.md)

---

## ✨ Features

* **📱 Full Control:** Start, Pause, and Stop the Airfryer directly from HA.
* **🌡️ Adjust Settings:** Set Target Temperature, Cooking Time, and Fan Speed (for supported models).
* **👀 Live Monitoring:**
    * Current Temperature & Probe Temperature.
    * Remaining Time & Progress %.
    * Device Status (Cooking, Preheating, Sleeping, etc.).
* **🚀 Easy Setup:** Upload your `network_node.db` file directly during setup or enter credentials manually.
* **🔧 Advanced Diagnostics:**
    * Detailed Firmware Information.
    * Internal Sensor Data (Voltage, Internal Temperature).
    * **Recipe & AutoCook Insights:** See exactly which Program ID or Recipe Stage is currently running.
* **🔌 Robust Offline Handling:** Sensors report clean "offline" states instead of errors when the device is unplugged.

---

## 📸 Screenshots

| Device and Entities | Config Flow (File Upload) |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/2d095e89-3ae1-4bd3-9ac5-a5337af2b7a3" width="300" alt="Control and Sensors" /> <img src="https://github.com/user-attachments/assets/b22142e4-0995-4b83-902e-3d3282672056" width="300" alt="Diagnose" /> | <img src="https://github.com/user-attachments/assets/d38951a8-55a6-4e3c-b5f9-852cbc2228a6" width="300" alt="Setup Menu" /> <img src="https://github.com/user-attachments/assets/fc89ab56-fc8c-4200-ac34-1e017616675b" width="300" alt="File Upload" /> |

---

## 📥 Installation

### Option 1: HACS (Recommended)

1.  Open HACS in Home Assistant.
2.  Go to "Integrations" > Top right menu (⋮) > "Custom repositories".
3.  Add this repository URL: `https://github.com/V4n1X/ha_philips_airfryer`
4.  Category: **Integration**.
5.  Click **Install**.
6.  Restart Home Assistant.

### Option 2: Manual

1.  Download the latest release.
2.  Copy the `custom_components/philips_airfryer` folder into your Home Assistant's `config/custom_components/` directory.
3.  Restart Home Assistant.

---

## ⚙️ Configuration

Go to **Settings** -> **Devices & Services** -> **Add Integration** and search for **Philips Airfryer**.

You have two methods to set up the device:

### 📂 Method A: Automatic Import (Recommended)

If you have rooted your phone or extracted the data from the **Philips HomeID App** (formerly NutriU), you likely have a file named `network_node.db`.

1.  Start the setup flow in Home Assistant.
2.  Select **"Upload File (network_node.db)"**.
3.  Upload the file directly from your computer. The integration will automatically extract the IP address, Client ID, and Client Secret.
4.  Click Submit to finish.

### 📝 Method B: Manual Entry

1.  Start the setup flow in Home Assistant.
2.  Select **"Enter Manually"**.
3.  Enter the **IP Address**, **Client ID**, and **Client Secret**.
4.  (Optional) Configure advanced settings like Protocol or Update Interval.

> **💡 Important Tip:** > The default **API Endpoint** is `/di/v1/products/1/venusaf`.  
> If your device controls do not work, please change the **API Endpoint** in the configuration options to:  
> `/di/v1/products/1/airfryer`

---

## 📊 Entities & Sensors

The integration provides the following entities (prefixed with your device name, e.g., `sensor.philips_airfryer_...`):

### Controls
* `switch.power`: Turn the device On/Off (Standby).
* `button.start`, `button.pause`, `button.stop`: Control the cooking process.
* `number.target_temp`: Set cooking temperature.
* `number.target_time`: Set cooking duration.
* `number.fan_speed`: Set fan speed (HD9880 only).

### Sensors
* `sensor.status`: Current state (Cooking, Ready, Preheating, etc.).
* `sensor.current_temperature`: The live temperature inside the basket.
* `sensor.core_temperature`: Temperature of the food probe (if connected).
* `binary_sensor.drawer`: Open/Closed status.
* `binary_sensor.thermometer`: Connected/Disconnected status.

### Diagnostic Sensors
Detailed technical data found under the "Diagnostic" category:
* **Recipe & Program:** `recipe_id`, `cooking_id`, `autocook_program` (with full attribute details).
* **Firmware:** Versions, Update Status, Progress.
* **Hardware:** Voltage, Internal Temperature.
* **Process:** Current Stage, Step ID, Error Codes.

---

## ❓ FAQ

**Q: How do I get the Client ID and Secret?**
A: You need to extract them from the official **Philips HomeID App** (formerly NutriU). There are various scripts available online to extract the `network_node.db` from a rooted Android device or via backup extraction. 

With the current HomeID App (Version: 8.10.0), the path is:
`/data/data/com.philips.ka.oneka.app/databases/network_node.db`

**Q: The device shows "Offline".**
A: The Airfryer disconnects from WiFi after a period of inactivity (Deep Sleep). Wake it up by pressing the dial on the device, and Home Assistant will reconnect automatically within the next update interval.

---

## 👏 Credits

Special thanks to **[noxhirsch](https://github.com/noxhirsch)** for the original work on [Pyscript-Philips-Airfryer](https://github.com/noxhirsch/Pyscript-Philips-Airfryer), which served as the foundation for this integration.
Also, a big thank you to the community in the [Home Assistant Forum](https://community.home-assistant.io/t/philips-airfryer-nutriu-integration-alexa-only/368260) for their research and support!

## ☕ Support

If you like this integration, consider staring the repository! ⭐

## 📄 License

[MIT License](LICENSE) - based on the work of the Home Assistant Community.
