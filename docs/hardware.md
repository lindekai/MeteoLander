# Hardware

Stand: Konzeptphase. Alle Angaben unten stammen aus Fotos der vorhandenen Teile und sind **noch nicht am Bauteil
verifiziert**. Es wird nur die bereits vorhandene Hardware verwendet; nichts wird ersetzt oder umgebaut.

## Bauteile

### ESP8266-Entwicklungsboard

| Merkmal | Wert | Status |
|---|---|---|
| Farbe | blau | Foto |
| Variante (NodeMCU, LoLin, Amica …) | unbekannt | **offen** |
| Abmessungen, Befestigungsbohrungen | unbekannt | **offen** |
| USB-Buchse / USB-Seriell-Chip | unbekannt | **offen** |

Das Board wird ausdrücklich **nicht** als Wemos D1 mini behandelt, solange die Variante nicht feststeht.

### TFT-Display

| Merkmal | Wert | Status |
|---|---|---|
| Platine | rot, Aufdruck `1.8 TFT SPI 128*160 V1.2` | Foto |
| Auflösung | 128 × 160 Pixel, Betrieb im Hochformat | Aufdruck |
| Controller | vermutlich ST7735 (Tab-Variante unbekannt) | **offen** |
| Displayanschlüsse | `VCC`, `GND`, `CS`, `RESET`, `A0` (DC), `SDA` (MOSI), `SCK`, `LED` | Foto, Reihenfolge prüfen |
| microSD-Anschlüsse | `SD_CS`, `SD_MOSI`, `SD_MISO`, `SD_SCK` | Foto, wird nicht genutzt |
| Befestigung | vier Bohrungen | Abstände **offen** |
| Spannungsregler / Pegel an `VCC` und `LED` | unbekannt | **offen** |

## Offene Prüfungen (M0)

- [ ] Beide Platinen von beiden Seiten mit Lineal fotografieren und in `assets/photos/` ablegen
- [ ] ESP8266-Variante anhand von Aufdruck und Bauteilen bestimmen
- [ ] Platinenmaße, Bohrungsabstände und Bohrungsdurchmesser messen (Messschieber)
- [ ] Pinreihenfolge am TFT physisch ablesen
- [ ] Prüfen, ob das TFT-Modul einen eigenen Spannungsregler hat (3,3 V oder 5 V an `VCC`)
- [ ] Vorwiderstand bzw. Transistor am `LED`-Pin prüfen
- [ ] Displaycontroller und Tab-Variante im Smoke-Test bestimmen (M1)
