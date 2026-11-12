# Verdrahtung

> [!IMPORTANT]
> Noch **kein** gültiger Anschlussplan. Die Zuordnung zu ESP8266-Pins wird erst festgelegt, wenn Boardvariante,
> Pinreihenfolge am TFT und Versorgung geprüft sind (Meilenstein M0).

## Anschlüsse des TFT

| TFT-Pin | Funktion | ESP8266-Pin |
|---|---|---|
| `VCC` | Versorgung | offen – abhängig vom Regler auf dem Modul |
| `GND` | Masse | GND |
| `CS` | Chip Select | offen |
| `RESET` | Reset | offen |
| `A0` | Daten/Befehl (DC) | offen |
| `SDA` | SPI MOSI | voraussichtlich Hardware-SPI MOSI, prüfen |
| `SCK` | SPI-Takt | voraussichtlich Hardware-SPI SCK, prüfen |
| `LED` | Hintergrundbeleuchtung | offen – Strombedarf prüfen |

Die microSD-Anschlüsse bleiben unbeschaltet.

## Regeln für die Pinwahl

- Hardware-SPI des ESP8266 verwenden, wenn die Boardvariante es erlaubt.
- Bootstrapping-Pins (beim ESP8266 GPIO0, GPIO2 und GPIO15) nur nutzen, wenn ihr Pegel beim Start nicht gestört wird.
- Jede Zuordnung wird hier mit Begründung eingetragen und im Smoke-Test bestätigt.

## Sicherheit am offenen Aufbau

- Das Messinggestell liegt kontrolliert auf GND oder ist vollständig isoliert – nie auf einem anderen Potenzial.
- Keine unterschiedlichen Versorgungspotenziale unisoliert nebeneinander.
- Das USB-Kabel wird am Gestell zugentlastet.
