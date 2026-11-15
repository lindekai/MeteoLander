# Testplan

Ein Test gilt erst als bestanden, wenn er am echten Gerät durchgeführt und hier mit Datum eingetragen ist.

| ID | Meilenstein | Test | Erwartung | Ergebnis |
|---|---|---|---|---|
| T0.1 | M0 | Platinen ausmessen | Maße und Bohrungen dokumentiert | ✅ 2026-11-15: TFT 34 × 58 (Bohrungen Ø 3, 28 × 52), D1 mini 34 × 26, BME280 11 × 14 mm |
| T1.1 | M1 | `SmokeTest.ino` kompiliert in der Arduino IDE | ohne Fehler, Versionen von Core und Bibliotheken notiert | – |
| T1.2 | M1 | Display-Initialisierung | Bild erscheint, Hochformat, weißer Rand ringsum; Tab-Variante notiert | – |
| T1.3 | M1 | Farbtest | Rot, Grün, Blau, Weiß korrekt, kein Randversatz | – |
| T1.4 | M1 | Schrift und Umlaute | Größen 1/2/4 lesbar, „ä ö ü Ä Ö Ü ß“ und „°“ korrekt | – |
| T1.5 | M1 | I²C und Chip-ID | Sensor an 0x76 oder 0x77; Chip-ID 0x60 (BME280) oder 0x58 (BMP280) notiert | – |
| T1.6 | M1 | WLAN-Funk | Netzwerksuche findet Netze, Signalstärke notiert | – |
| T1.7 | M1 | Strom der Hintergrundbeleuchtung | Strom an 3,3 V gemessen; über 30 mA → Zusatzwiderstand 10–22 Ω | – |
| T2.1 | M2 | WLAN-Verbindung | Verbindung innerhalb des Zeitlimits | – |
| T2.2 | M2 | NTP | Uhrzeit korrekt, Sommer-/Winterzeit | – |
| T2.3 | M2 | Open-Meteo-Abruf | Werte plausibel im Vergleich zur Website | – |
| T2.4 | M2 | WLAN aus während des Betriebs | kein Hänger, Fehleranzeige, Wiederverbindung | – |
| T2.5 | M2 | API nicht erreichbar | letzter Stand bleibt, Status rot | – |
| T2.6 | M2 | BME280 auslesen | Werte plausibel gegenüber Referenzthermometer | – |
| T2.7 | M2 | Selbsthalteschaltung | kurzer Tastendruck schaltet ein, Gerät hält sich selbst, schaltet nach Ablauf ab | – |
| T2.8 | M2 | Ruhestrom | im ausgeschalteten Zustand < 10 µA aus dem Akku (gemessen) | – |
| T2.9 | M2 | Akkuspannung | Anzeige weicht < 0,05 V vom Multimeter ab | – |
| T2.10 | M2 | Schaltregler TPS62827 | 3,3 V am Ausgang bei WLAN-Last, auch bei 3,4 V Akkuspannung; Verhalten von `EN` notiert | – |
| T3.1 | M3 | Lesbarkeit aus 1–2 m | Temperatur und Symbol klar erkennbar | – |
| T4.1 | M4 | Kurzschlussprüfung Gestell | kein Kontakt zu fremdem Potenzial | – |
| T5.1 | M5 | 200 Einschaltzyklen | jeder Start zeigt Daten und schaltet sauber ab | – |
| T5.2 | M5 | Akkulaufzeit | Verbrauch pro Einschaltung gemessen, Laufzeit hochgerechnet | – |
| T5.3 | M5 | Laden | im ausgeschalteten Zustand lädt der Akku, die LEDs zeigen Laden und Ende; kurzes Einschalten beim Laden ohne Fehlverhalten | – |
| T5.4 | M5 | Akku leer | kein Fehlverhalten, sauberer Start nach dem Laden | – |
