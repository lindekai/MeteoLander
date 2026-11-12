# Gestaltung

## Leitidee

MeteoLander ist ein kleines, freistehendes Objekt: das rote Displaymodul, gehalten von einem offenen Messingrahmen, der
gleichzeitig die Standbeine bildet. Die Elektronik ist Teil der Form und wird nicht versteckt. Weniger ist mehr – keine
Zierantennen, keine großen Rahmen, kein Steampunk.

## Gestell

![Konzeptskizze](../assets/sculpture-concept.svg)

- Das TFT-Modul wird an seinen **vier Befestigungsbohrungen** gehalten. Die Platine wird nicht verändert.
- Zwei seitliche Drahtbügel führen von den Bohrungen nach unten und laufen als Standbeine aus.
- Eine hintere Strebe stützt das leicht nach hinten geneigte Display.
- Das ESP8266-Board sitzt dahinter auf eigenen Drahtstützen, gut sichtbar.
- Das USB-Kabel wird hinten am Gestell zugentlastet.

Drahtstärken, Neigungswinkel und Gesamthöhe werden in M4 festgelegt. Sicherheitsregeln siehe [wiring.md](wiring.md).

## 1:1-Bauzeichnung (geplant für M4)

Die Bauzeichnung entsteht aus den gemessenen Maßen beider Platinen. Sie ist zugleich Biegeschablone: Drähte werden direkt
auf den Ausdruck gelegt.

- **Format:** SVG als Quelle, PDF auf A4 zum Drucken
- **Inhalt:** Draufsicht als Biegeschablone, Seitenansicht mit Neigung, Bohrungspositionen, Lötpunkte, Drahtlängen
- **Kontrollstrecke 100 mm:** nach dem Drucken nachmessen. Im Druckdialog „Tatsächliche Größe“ bzw. 100 % wählen,
  nicht „An Seite anpassen“.
- **Materialliste:** Drahtstärken, Längen, Isolierung, Befestigung

## Display

![Layoutentwurf](../assets/display-layout.svg)

- Harte Grenze: 128 × 160 Pixel im Hochformat
- Dunkler Hintergrund; Weiß für Werte, dezentes Cyan für Zustand und Tiefstwerte, Gelb für die Sonne
- Temperatur groß (GFX-Schriftgröße 4), höchstens zwei bis drei weitere Werte
- Kopfzeile mit Ort bzw. Ansicht und Uhrzeit; Fußzeile mit Datenstand und Statuspunkt
  (grün = aktuell, gelb = veraltet, rot = Fehler)
- Deutsche Beschriftung, metrische Einheiten
- Offener Punkt: Darstellung von Umlauten im GFX-Standardfont (CP437-Modus) im Smoke-Test prüfen
