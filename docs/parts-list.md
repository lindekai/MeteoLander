# Teileliste

Stand: 2026-11-15 · Bauteilnamen wie in [Schaltplan](../assets/schematic.svg) und
[Breadboard-Zeichnung](../assets/breadboard.svg). Dieselbe Liste als Tabelle für Tabellenkalkulationen:
[parts-list.csv](parts-list.csv).

**Status:** ✅ vorhanden und bestimmt · 🔍 vorhanden, Prüfung offen · 🛒 Typ steht, noch zu beschaffen bzw. im
Bestand zu suchen · ❓ Typ noch offen

## Elektronik

| Ref. | Anz. | Bauteil | Typ / Wert | Gehäuse | Status | Bemerkung |
|---|---:|---|---|---|:---:|---|
| U3 | 1 | ESP8266-Board | AZ-Delivery D1 mini (ESP-12F) | Modul 34 × 26 mm | ✅ | vermutlich CH340C; A0-Teiler 220 kΩ / 100 kΩ |
| U4 | 1 | TFT-Display 1,8″ | `1.8 TFT SPI 128*160 V1.2`, vermutlich ST7735S | Modul ca. 35 × 58 mm | 🔍 | Controller im Smoke-Test (M1) bestimmen |
| U5 | 1 | Klimasensor | GYBMEP-Modul (BME280 oder BMP280) | Modul ca. 10 × 13 mm | 🔍 | Chip-ID prüfen: 0x60 = BME280 |
| BT1 | 1 | LiPo-Akku | EEMB LP103454, 3,7 V, 2000 mAh, mit Schutzplatine | 10 × 34 × 57 mm | ✅ | Steckerart noch prüfen |
| U1 | 1 | Lademodul | HW-168 (TP4056), Mini-USB, ohne Schutz und Lastausgang | Modul ca. 16 × 20 mm | ✅ | Ladestrom 1 A (PROG 1,2 kΩ); laden bei ausgeschaltetem Gerät |
| U2 | 1 | LDO 3,3 V | HT7833 (500 mA); ersatzweise AP2112K-3.3 oder ME6211C33 | TO-92 | 🛒 | nötig, weil der Typ des Board-Reglers (`MK8H`) unbekannt ist; Pinfolge am Datenblatt prüfen |
| Q1 | 1 | P-MOSFET, Logikpegel | AO3401 oder gleichwertig | SOT-23 | 🛒 | Schalter der Selbsthaltung |
| Q2 | 1 | NPN-Transistor | BC547 oder gleichwertig | TO-92 | 🛒 | hält das Gate unten |
| D1, D2 | 2 | Schottky-Diode | BAT85 | DO-35 | ✅ | |
| R1 | 1 | Widerstand | 100 kΩ | THT 1/4 W | ✅ | Gate-Pull-up |
| R2 | 1 | Widerstand | 10 kΩ | THT 1/4 W | ✅ | Basiswiderstand Q2 |
| R3 | 1 | Widerstand | 100 kΩ | THT 1/4 W | ✅ | Basis nach GND |
| R4 | 1 | Widerstand | 100 kΩ | THT 1/4 W | ✅ | Akkuspannung an A0 |
| R5 | 1 | Widerstand | 10 kΩ | THT 1/4 W | ✅ | TFT-RESET nach +3V3 |
| C1, C2 | 2 | Keramikkondensator | 1 µF, ≥ 10 V | THT oder 0805 | ✅ | am Ein- und Ausgang von U2 |
| S1 | 1 | Taster | Kurzhubtaster 6 × 6 mm, ca. 5 mm hoch, zwei Beinchen, schließend | THT | ✅ | liegt auf dem Querstab im Deckrahmen, vorderes Beinchen dort angelötet (GND) |

## Testaufbau auf dem Breadboard

| Anz. | Teil | Bemerkung | Status |
|---:|---|---|:---:|
| 1 | Steckbrett, 830 Kontakte (63 Spalten) | Schienen oben und unten | ✅ |
| 1 Satz | Steckbrücken, starr | für kurze Verbindungen auf dem Brett | ✅ |
| ca. 12 | Dupont-Kabel, Buchse–Stecker | TFT und BME280 neben dem Brett | ✅ |
| 1 | Adapterplatine SOT-23 auf 2,54 mm | für Q1 | 🛒 |
| 1 | Stiftleisten 2,54 mm | für D1 mini, BME280 und Adapter | ✅ |

## Mechanik (Fähre)

Längen und Mengen stehen in der Zuschnittliste der [Bauzeichnung](../assets/build-drawing.pdf) (Blatt 1).

| Teil | Abmessung | Verwendung | Status |
|---|---|---|:---:|
| Messingdraht | Ø 1,0 mm, ca. 2,1 m | Käfig, Beine, Mast, Akku-Band; führt GND | ❓ |
| Messingblech oder -scheiben | Ø 14 mm | Landeteller | ❓ |
| Kupferlackdraht | ca. Ø 0,3 mm | sichtbare Signalleitungen | ❓ |
| Lochraster für die Akkuwanne | 36 × 14 mm | trägt den Akku, über Kupferpads an Querdraht und Rahmen gelötet | ❓ |
| Schrumpfschlauch | für 1-mm-Draht, ca. 2 × 36 mm | Akku-Band vorn und hinten | ❓ |
| Kapton-Band | – | Wannenoberseite und Akku zusätzlich isolieren | ❓ |
| Lochrasterplatine | klein | Selbsthaltung, Regler, Spannungsteiler | ❓ |
