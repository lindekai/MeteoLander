# Software

Stand: Planung. Es gibt einen Smoke-Test-Sketch für den ersten Probelauf (M1); die eigentliche Firmware folgt.

## Smoke-Test (M1)

[`firmware/SmokeTest/SmokeTest.ino`](../firmware/SmokeTest/SmokeTest.ino) prüft die Hardware auf dem Steckbrett,
bevor die Selbsthaltung gesteckt ist. Der D1 mini hängt dafür nur an seiner USB-Buchse.

| Schritt | Prüft | Ergebnis notieren in |
|---|---|---|
| Rahmen | Initialisierung, Hochformat, Randversatz der Tab-Variante | T1.2 |
| Farbbalken | Rot, Grün, Blau, Weiß in der richtigen Reihenfolge | T1.3 |
| Schrift | Größen 1/2/4, Umlaute und Gradzeichen im CP437-Modus | T1.4 |
| I²C | Adresse und Chip-ID des Sensors (0x60 = BME280, 0x58 = BMP280), ohne Sensorbibliothek | T1.5 |
| WLAN | Netzwerksuche ohne Zugangsdaten, stärkstes Signal | T1.6 |

Zum Schluss stehen die Ergebnisse auf dem Display, ausführlich im seriellen Monitor (115200 Baud).

- **Vorbereitung:** In der Arduino IDE den ESP8266-Core installieren (Boardverwalter: „esp8266 by ESP8266
  Community“), Board „LOLIN(WEMOS) D1 R2 & mini“ wählen. Bibliotheken: Adafruit GFX Library, Adafruit ST7735 and
  ST7789 Library.
- **Tab-Variante:** voreingestellt `INITR_GREENTAB`. Fehlt der weiße Rand an einer Seite oder sind Farben
  vertauscht, `TFT_TAB` auf `INITR_BLACKTAB` oder `INITR_REDTAB` ändern.
- **Ausrichtung:** Steht „OBEN“ unten, `setRotation(2)` statt `0`.
- **Nebenbei messen:** Strom der Hintergrundbeleuchtung (Multimeter in der `LED`-Leitung) für T1.7.
- Der Sketch ist noch nicht kompiliert; Versionen von Core und Bibliotheken werden beim ersten Lauf in T1.1
  festgehalten.

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
| Sensor | BME280-Bibliothek (Auswahl nach Test, z. B. Adafruit BME280) | wird festgehalten |

## Ablauf nach Tastendruck

Das Gerät läuft nicht dauerhaft. Jeder Tastendruck ist ein vollständiger Start:

1. **Halten:** Halte-GPIO sofort setzen, damit die Selbsthalteschaltung die Versorgung übernimmt.
2. **Innen messen:** BME280 auslesen, solange die Elektronik noch kalt ist; Akkuspannung an `A0` lesen.
3. **Erste Anzeige:** Innenwerte und Akkustand sofort zeigen, Wetter als „wird geladen“.
4. **Online:** WLAN mit Zeitlimit, NTP, Open-Meteo-Abruf.
5. **Anzeigen:** Wetter, Prognose und Innenwerte für 5–10 Minuten (in `config.h` einstellbar).
6. **Abschalten:** Halte-GPIO zurücknehmen; die Versorgung wird getrennt.

Weil nach jedem Start frische Daten geholt werden, entfällt der regelmäßige Abruf alle 15 Minuten.
Bei kritischer Akkuspannung zeigt das Gerät nur einen Hinweis und schaltet sich sofort wieder ab.

## Aufbau

```text
WeatherService ──▶ WeatherModel ◀── IndoorSensor (BME280)
 (Abruf, Parsing)   (Werte, Zeitstempel,
                     Status, Fehler)  ──▶ DisplayUI
        ▲                                 (Ansichten, nur geänderte
   Zeit (NTP, Europe/Berlin)               Bereiche neu zeichnen)

Power: Halte-GPIO, Akkuspannung, Anzeigezeit, Selbstabschaltung
```

- **WeatherService:** baut die Anfrage, holt die Daten per HTTPS, wertet das JSON aus.
- **WeatherModel:** hält jeden Wert mit Zeitstempel, Aktualitätsstatus und Fehlerzustand.
- **IndoorSensor:** liest den BME280 einmal direkt nach dem Start.
- **DisplayUI:** zeichnet die Ansichten und vermeidet unnötige Vollbild-Neuzeichnungen.
- **Power:** übernimmt die Selbsthaltung, misst die Akkuspannung und schaltet nach Ablauf ab.
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
| Kein WLAN | Innenwerte bleiben sichtbar, Statuspunkt rot, Hinweis „Kein WLAN“ |
| API- oder Parsing-Fehler | Innenwerte bleiben sichtbar, Statuspunkt rot, Hinweis auf den Fehler |
| Keine Wetterdaten | `--` statt Werten, nie erfundene Werte |
| BME280 nicht gefunden | `--` für Innenwerte, Hinweis im seriellen Log |
| Akku kritisch | kurzer Hinweis, sofortige Selbstabschaltung |
| Firmware hängt | Watchdog-Neustart; spätestens die Abschaltzeit trennt die Versorgung |
