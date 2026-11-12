# Software

Stand: Planung. Es gibt noch keine Firmware.

## Rahmen

- **Entwicklungsumgebung:** ausschließlich Arduino IDE 2.x mit dem ESP8266-Arduino-Core
- **Sketch:** `firmware/MeteoLander/MeteoLander.ino` – direkt in der Arduino IDE zu öffnen
- **Konfiguration:** `config.example.h` wird versioniert; die eigene `config.h` mit WLAN-Daten ist per `.gitignore` ausgeschlossen

## Geplante Bibliotheken

| Zweck | Bibliothek | Version |
|---|---|---|
| Grafik | Adafruit GFX | wird bei M1 festgehalten |
| Displaytreiber | Adafruit ST7735 and ST7789 (nach Prüfung des Controllers) | wird bei M1 festgehalten |
| WLAN / HTTPS | `ESP8266WiFi`, `WiFiClientSecure` (im Core enthalten) | Core-Version wird festgehalten |
| JSON | ArduinoJson | wird bei M2 festgehalten |

## Aufbau

```text
WeatherService ──▶ WeatherModel ──▶ DisplayUI
 (Abruf, Parsing)   (Werte, Zeitstempel,   (Ansichten, nur geänderte
                     Status, Fehler)         Bereiche neu zeichnen)
        ▲
   Zeit (NTP, Europe/Berlin)
```

- **WeatherService:** baut die Anfrage, holt die Daten per HTTPS, wertet das JSON aus.
- **WeatherModel:** hält jeden Wert mit Zeitstempel, Aktualitätsstatus und Fehlerzustand.
- **DisplayUI:** zeichnet die Ansichten und vermeidet unnötige Vollbild-Neuzeichnungen.
- Steuerung über `millis()`-Intervalle, keine blockierenden `delay()`-Aufrufe im Betrieb.

## Datenquelle

Open-Meteo Forecast API, ohne API-Schlüssel. Geplante Felder:

- **aktuell:** `temperature_2m`, `relative_humidity_2m`, `weather_code`, `wind_speed_10m`
- **täglich:** `temperature_2m_max`, `temperature_2m_min`, `precipitation_probability_max`, `weather_code`
- **Parameter:** `timezone=Europe/Berlin`, `forecast_days=2`, Koordinaten aus `config.h`

Die Koordinaten für Saarmund werden vor der ersten Nutzung verifiziert und erst dann in `config.example.h` eingetragen.

## Verhalten bei Fehlern

| Situation | Anzeige |
|---|---|
| Daten älter als zwei Abrufintervalle | Werte bleiben stehen, Statuspunkt gelb, Uhrzeit des Datenstands |
| Kein WLAN | Statuspunkt rot, Hinweis „Kein WLAN“, Wiederverbindung mit festem Zeitlimit |
| API- oder Parsing-Fehler | Statuspunkt rot, letzter gültiger Stand bleibt sichtbar |
| Noch nie Daten erhalten | `--` statt Werten |
