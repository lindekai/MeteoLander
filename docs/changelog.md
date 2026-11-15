# Changelog

## 2026-11-15 – Akkuhalterung

- Der Akku hing im Modell frei im Käfig. Er steht jetzt in einer Akkuwanne aus Lochraster (36 × 14 mm) auf einem
  zusätzlichen Querdraht im Bodenrahmen; ein Akku-Band (Drahtschlaufe 42 × 13 mm mit Schrumpfschlauch, 25 mm über dem
  Bodenrahmen) hält ihn oben, ohne zu klemmen
- Bauzeichnung: Querdraht und Wanne im Bodenrahmen, neue Abbildung ⑤ Akku-Band, Zuschnittliste und Nummern angepasst
- 3D-Modell: Wanne und Band ergänzt; der künstliche Tiefenversatz des Akkus entfällt

## 2026-11-15 – Bauzeichnung 1:1

- Bauzeichnung zum Ausdrucken (`assets/build-drawing.pdf`, Vorschau als SVG je Blatt), erzeugt mit
  `tools/build_drawing.py`: Käfig mit Längenlehren und Zuschnittliste, Landebeine mit Aufstellplan und
  Holm-Biegeschablone, Kontrollstrecken 100 mm und 50 mm
- 3D-Modell: Beingeometrie in `leg_points` ausgelagert und mit der Bauzeichnung geteilt; die Strebe endet jetzt auf
  dem mittleren Querstab statt frei zwischen den Holmen
- TFT-Bohrungen gemessen: Ø 3 mm, Mittenabstand 28 × 52 mm; Hinweis zur Befestigung der Halter (Öse oder Ring)

## 2026-11-15 – Teile bestimmt, Breadboard, Ansichten, Teileliste

- Teile anhand von Fotos mit Lineal bestimmt (`assets/photos/`): AZ-Delivery D1 mini (ESP-12F), TFT mit
  Pinreihenfolge `VCC GND CS RESET A0 SDA SCK LED`, GYBMEP-Modul (BME/BMP280, mit Regler und Pegelwandler),
  LiPo EEMB LP103454 mit 2000 mAh und Schutzplatine
- Breadboard-Zeichnung (`assets/breadboard.svg`, erzeugt mit `tools/breadboard.py`)
- Ansichten von vorn, rechts, hinten, links und oben (`assets/views.svg`)
- Teileliste als Markdown-Tabelle und CSV (`docs/parts-list.md`, `docs/parts-list.csv`)
- Schaltplan Rev. 0.2: Board und Akku eingetragen, Kondensatoren C1/C2 am LDO ergänzt, Hinweise zu A0-Teiler und
  Modulversorgung aktualisiert
- 3D-Modell: Maße von D1 mini und flachem Akku statt Annahmen für ein langes Board und eine 18650-Zelle

## 2026-11-12 – Bauform Landefähre

- Neue Bauform: Drahtkäfig als Landefähre mit vier Landebeinen und Messingtellern, BME280 auf einem Mast,
  Taster oben vorn, Lademodul und Lochrasterplatine an der rechten Seite
- Aufbauskizze und Titelbild werden jetzt aus einem 3D-Modell erzeugt (`tools/lander_model.py`)
- Alte Konzeptskizze des Gestells entfernt
- Hinweis auf die Inspiration: *Boron Lander* von Mohit Bhoite

## 2026-11-12 – Schaltplan und Aufbauskizze

- Schaltplanentwurf (`assets/schematic.svg`): Lademodul, Akku, Selbsthalteschaltung, LDO, ESP8266, TFT, BME280
- Pinbelegung als begründeter Vorschlag auf GPIO-Ebene; Taster an GPIO3 (RX), weil alle Bootpins ausscheiden
- Entscheidung: Ladeanzeige über die LEDs des Lademoduls, sichtbar im Gestell; Display zeigt den Akkustand
- Aufbauskizze (`assets/assembly-sketch.svg`) mit nummerierten Bauteilen und Einbauhinweisen

## 2026-11-12 – Akku, Taster und Innenklima

- Entscheidung: Akkubetrieb. Das Gerät ist aus, bis der Taster gedrückt wird; dann misst es, holt das Wetter, zeigt
  5–10 Minuten an und schaltet sich selbst ab.
- Entscheidung: **Selbsthalteschaltung** statt Deep Sleep, weil das Entwicklungsboard im Deep Sleep weiter 10–20 mA
  ziehen kann; ausgeschaltet fließt so praktisch kein Strom.
- Entscheidung: vorhandener **BME280** für Innentemperatur, -feuchte und Luftdruck, auf eigenem Messingarm mit Abstand
  zur Elektronik.
- Regelmäßiger Abruf alle 15 Minuten entfällt; jeder Start holt frische Daten.
- Offen: Akkutyp, Lademodul und Spannungsregler nach Werkstattbestand.

## 2026-11-12 – Projektstart

- Repository angelegt: README, Dokumentation, MIT-Lizenz
- Konzeptbilder: Titelbild, Layoutentwurf der Displayansichten (128 × 160 px), Konzeptskizze des Gestells
- Entscheidung: Arduino IDE als einzige Entwicklungsumgebung
- Entscheidung: Wetterdaten von Open-Meteo, Uhrzeit per NTP (Europe/Berlin)
- Entscheidung: Bauzeichnung im Maßstab 1:1 mit 100-mm-Kontrollstrecke, sobald die Platinen ausgemessen sind
