# 🍟 Philips Airfryer Integration für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![version](https://img.shields.io/github/v/release/V4n1X/ha_philips_airfryer)](https://github.com/V4n1X/ha_philips_airfryer)
[![Maintainer](https://img.shields.io/badge/maintainer-V4n1X-blue)](https://github.com/V4n1X)

Eine vollständig native Home Assistant Integration für **Philips Connected Airfryer** (z. B. HD9880/90 Serie 7000 XXL).

Diese Integration ermöglicht die lokale Überwachung und Steuerung deines Airfryers und bietet erweiterte Diagnosen, Einblicke in laufende Rezepte und eine kinderleichte Einrichtung durch den Upload deiner vorhandenen Konfigurationsdatenbank.

---

## ✨ Funktionen

* **📱 Volle Kontrolle:** Starte, Pausiere und Stoppe den Airfryer direkt aus HA.
* **🌡️ Einstellungen anpassen:** Setze Zieltemperatur, Kochzeit und Lüftergeschwindigkeit (für unterstützte Modelle).
* **👀 Live-Überwachung:**
    * Aktuelle Temperatur & Kerntemperatur (Thermometer).
    * Restzeit & Fortschritt in %.
    * Gerätestatus (Kochen, Vorheizen, Schlafen, etc.).
* **🚀 Einfache Einrichtung:** Lade deine `network_node.db` Datei direkt im Browser hoch oder gib die Daten manuell ein.
* **🔧 Erweiterte Diagnose:**
    * Detaillierte Firmware-Informationen.
    * Interne Sensordaten (Spannung, Interne Temperatur).
    * **Rezept & AutoCook Einblicke:** Sieh genau, welche Programm-ID oder welcher Rezeptschritt gerade läuft.
* **🔌 Robustes Offline-Handling:** Sensoren melden einen sauberen "Offline"-Status anstatt Fehler zu werfen, wenn der Stecker gezogen ist.

---

## 📸 Screenshots

| Gerät und Entitäten | Config Flow (Datei-Upload) |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/2d095e89-3ae1-4bd3-9ac5-a5337af2b7a3" width="300" alt="Steuerung und Sensoren" /> <img src="https://github.com/user-attachments/assets/b22142e4-0995-4b83-902e-3d3282672056" width="300" alt="Diagnose" /> | <img src="https://github.com/user-attachments/assets/d38951a8-55a6-4e3c-b5f9-852cbc2228a6" width="300" alt="Einrichtungsmenü" /> <img src="https://github.com/user-attachments/assets/fc89ab56-fc8c-4200-ac34-1e017616675b" width="300" alt="Datei Upload" /> |

---

## 📥 Installation

### Option 1: HACS (Empfohlen)

1.  Öffne HACS in Home Assistant.
2.  Gehe zu "Integrationen" > Menü oben rechts (⋮) > "Benutzerdefinierte Repositories".
3.  Füge diese URL hinzu: `https://github.com/V4n1X/ha_philips_airfryer`
4.  Kategorie: **Integration**.
5.  Klicke auf **Installieren**.
6.  Starte Home Assistant neu.

### Option 2: Manuell

1.  Lade das neueste Release herunter.
2.  Kopiere den Ordner `custom_components/philips_airfryer` in dein Home Assistant `config/custom_components/` Verzeichnis.
3.  Starte Home Assistant neu.

---

## ⚙️ Konfiguration

Gehe zu **Einstellungen** -> **Geräte & Dienste** -> **Integration hinzufügen** und suche nach **Philips Airfryer**.

Du hast zwei Möglichkeiten, das Gerät einzurichten:

### 📂 Methode A: Automatischer Import (Empfohlen)

Wenn du ein gerootetes Android-Handy hast oder die Daten aus der **Philips HomeID App** (ehemals NutriU) extrahiert hast, besitzt du wahrscheinlich eine Datei namens `network_node.db`.

1.  Starte den Config Flow in Home Assistant.
2.  Wähle **"Aus Datei hochladen (network_node.db)"**.
3.  Lade die Datei direkt von deinem Computer hoch. Die Integration extrahiert automatisch IP-Adresse, Client-ID und Client-Secret.
4.  Klicke auf Absenden, um abzuschließen.

### 📝 Methode B: Manuelle Eingabe

1.  Starte den Config Flow in Home Assistant.
2.  Wähle **"Manuell eingeben"**.
3.  Gib die **IP-Adresse**, **Client-ID** und das **Client-Secret** ein.
4.  (Optional) Konfiguriere erweiterte Einstellungen wie Protokoll oder Update-Intervall.

> **💡 Wichtiger Tipp:** > Der Standard **API Endpunkt** ist `/di/v1/products/1/venusaf`.  
> Sollte die Steuerung deines Geräts nicht funktionieren, ändere bitte den **API Endpunkt** in den Konfigurations-Optionen auf:  
> `/di/v1/products/1/airfryer`

---

## 📊 Entitäten & Sensoren

Die Integration stellt folgende Entitäten bereit (mit dem Präfix deines Gerätenamens, z. B. `sensor.philips_airfryer_...`):

### Steuerung
* `switch.power`: Gerät Ein/Aus (Standby).
* `button.start`, `button.pause`, `button.stop`: Steuerung des Kochvorgangs.
* `number.target_temp`: Zieltemperatur einstellen.
* `number.target_time`: Kochzeit einstellen.
* `number.fan_speed`: Lüftergeschwindigkeit einstellen (nur HD9880).

### Sensoren
* `sensor.status`: Aktueller Status (Kochen, Bereit, Vorheizen, etc.).
* `sensor.current_temperature`: Die Live-Temperatur im Korb.
* `sensor.core_temperature`: Temperatur des Fleischthermometers (falls verbunden).
* `binary_sensor.drawer`: Status Schublade (Offen/Geschlossen).
* `binary_sensor.thermometer`: Status Thermometer (Verbunden/Getrennt).

### Diagnose-Sensoren
Detaillierte technische Daten unter der Kategorie "Diagnose":
* **Rezept & Programm:** `recipe_id`, `cooking_id`, `autocook_program` (mit allen Attributen).
* **Firmware:** Versionen, Update-Status, Fortschritt.
* **Hardware:** Spannung, Interne Temperatur.
* **Prozess:** Aktuelle Stufe, Schritt-ID, Fehlercodes.

---

## ❓ FAQ

**F: Woher bekomme ich Client-ID und Secret?**
A: Diese müssen aus der offiziellen **Philips HomeID App** (ehemals NutriU) extrahiert werden. Es gibt online verschiedene Skripte, um die `network_node.db` von einem gerooteten Android-Gerät oder über eine Backup-Extraktion zu erhalten.

Mit der aktuellen HomeID App (Version: 8.10.0) lautet der Pfad:
`/data/data/com.philips.ka.oneka.app/databases/network_node.db`

**F: Das Gerät zeigt "Nicht erreichbar" (Offline) an.**
A: Der Airfryer trennt nach einer gewissen Zeit der Inaktivität die WLAN-Verbindung (Deep Sleep), um Strom zu sparen. Wecke ihn auf, indem du das Drehrad am Gerät drückst. Home Assistant verbindet sich beim nächsten Update-Intervall automatisch wieder.

---

## 👏 Danksagung

Ein besonderer Dank geht an **[noxhirsch](https://github.com/noxhirsch)** für die Vorarbeit am [Pyscript-Philips-Airfryer](https://github.com/noxhirsch/Pyscript-Philips-Airfryer), welches als Basis für diese Integration diente.
Ebenfalls vielen Dank an die Community im [Home Assistant Forum](https://community.home-assistant.io/t/philips-airfryer-nutriu-integration-alexa-only/368260) für die Recherche und Unterstützung!

## ☕ Support

Wenn dir diese Integration gefällt, lass gerne einen Stern auf GitHub da! ⭐

## 📄 Lizenz

[MIT License](LICENSE) - basierend auf der Arbeit der Home Assistant Community.
