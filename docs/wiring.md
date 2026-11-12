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

## BME280

| BME280-Pin | Funktion | ESP8266-Pin |
|---|---|---|
| `VIN`/`VCC` | Versorgung | offen – abhängig von der Modulversion |
| `GND` | Masse | GND |
| `SDA` | I²C-Daten | offen |
| `SCL` | I²C-Takt | offen |

## Stromversorgung mit Selbsthalteschaltung

```text
USB ──▶ Lademodul ──▶ Akku (mit Schutz)
                         │
                         ▼
                    P-MOSFET (Schalter) ──▶ 3,3-V-Regler ──▶ ESP8266, TFT, BME280
                         ▲      ▲
       Taster nach GND ──┘      └── Transistor ◀── GPIO „Halten“ des ESP8266
```

1. **Aus:** Ein Pull-up hält das Gate des P-MOSFET hoch, der Schalter sperrt, es fließt kein Strom.
2. **Einschalten:** Der Taster zieht das Gate auf GND, die Elektronik bekommt Strom und startet.
3. **Halten:** Die Firmware setzt sofort beim Start den Halte-GPIO, der Transistor hält das Gate unten.
   Der Taster darf losgelassen werden.
4. **Ausschalten:** Nach der Anzeigezeit nimmt die Firmware den Halte-GPIO zurück und schaltet sich damit selbst ab.

Offene Punkte: Bauteiltypen, Wahl des Halte-GPIO (muss beim Booten ruhig bleiben), ob der Taster zusätzlich über eine
Diode an einem GPIO gelesen wird (für einen zweiten Tastendruck im Betrieb) und wie lange der Taster beim Einschalten
gedrückt werden muss.

## Akkuspannung

Über einen Spannungsteiler an `A0`. Der Teiler sitzt hinter dem MOSFET und verbraucht deshalb im ausgeschalteten
Zustand nichts. Das Teilerverhältnis hängt davon ab, ob das Board an `A0` bereits einen eigenen Teiler hat.

## Regeln für die Pinwahl

- Hardware-SPI des ESP8266 verwenden, wenn die Boardvariante es erlaubt.
- Bootstrapping-Pins (beim ESP8266 GPIO0, GPIO2 und GPIO15) nur nutzen, wenn ihr Pegel beim Start nicht gestört wird.
- Jede Zuordnung wird hier mit Begründung eingetragen und im Smoke-Test bestätigt.

## Sicherheit am offenen Aufbau

- Das Messinggestell liegt kontrolliert auf GND oder ist vollständig isoliert – nie auf einem anderen Potenzial.
- Keine unterschiedlichen Versorgungspotenziale unisoliert nebeneinander.
- Das USB-Kabel wird am Gestell zugentlastet.
- Der Akku hat eine Schutzschaltung, ist rundum isoliert und mechanisch fest gehalten; er berührt das Gestell nirgends blank.
