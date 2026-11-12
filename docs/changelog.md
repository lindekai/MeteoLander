# Changelog

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
