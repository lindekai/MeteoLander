# Testplan

Ein Test gilt erst als bestanden, wenn er am echten Gerät durchgeführt und hier mit Datum eingetragen ist.

| ID | Meilenstein | Test | Erwartung | Ergebnis |
|---|---|---|---|---|
| T0.1 | M0 | Platinen ausmessen | Maße und Bohrungen dokumentiert | – |
| T1.1 | M1 | Sketch kompiliert in der Arduino IDE | ohne Fehler, Versionen notiert | – |
| T1.2 | M1 | Display-Initialisierung | Bild erscheint, Hochformat, richtige Ausrichtung | – |
| T1.3 | M1 | Farbtest | Rot, Grün, Blau, Weiß korrekt, kein Randversatz | – |
| T1.4 | M1 | Schrift und Umlaute | Größen 1/2/4 lesbar, „ö“ korrekt | – |
| T2.1 | M2 | WLAN-Verbindung | Verbindung innerhalb des Zeitlimits | – |
| T2.2 | M2 | NTP | Uhrzeit korrekt, Sommer-/Winterzeit | – |
| T2.3 | M2 | Open-Meteo-Abruf | Werte plausibel im Vergleich zur Website | – |
| T2.4 | M2 | WLAN aus während des Betriebs | kein Hänger, Fehleranzeige, Wiederverbindung | – |
| T2.5 | M2 | API nicht erreichbar | letzter Stand bleibt, Status rot | – |
| T3.1 | M3 | Lesbarkeit aus 1–2 m | Temperatur und Symbol klar erkennbar | – |
| T4.1 | M4 | Kurzschlussprüfung Gestell | kein Kontakt zu fremdem Potenzial | – |
| T5.1 | M5 | Dauerlauf 72 h | keine Hänger, Speicher stabil | – |
| T5.2 | M5 | Stromausfall | startet selbstständig wieder | – |
