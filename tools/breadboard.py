#!/usr/bin/env python3
"""MeteoLander – Breadboard-Zeichnung

Erzeugt assets/breadboard.svg: Testaufbau der Schaltung aus assets/schematic.svg auf einem
Steckbrett mit 63 Spalten. Bauteilnamen (R1, Q1, D1 …) entsprechen dem Schaltplan.

Aufruf:  python3 tools/breadboard.py

Belegung des Steckbretts:
  obere Schienen   außen +3V3, innen GND
  untere Schienen  innen VBAT, außen GND (rechts mit der oberen GND-Schiene verbunden)
  Spalten 4–24     Bereich A: Selbsthaltung und 3,3-V-Regler
  Spalten 31–45    D1 mini, um 180° gedreht (USB links, Antenne rechts frei)
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "breadboard.svg")

W, H = 1640, 1030
P = 17.0                       # Rastermaß 2,54 mm in px
MM = P / 2.54                  # px pro mm
BX, BY = 300.0, 560.0          # linke obere Ecke des Steckbretts
COLS = 63
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

ROW_Y = {r: BY + 4 * P + i * P for i, r in enumerate("abcde")}
ROW_Y.update({r: BY + 4 * P + (i + 7) * P for i, r in enumerate("fghij")})
RAIL_Y = {"T+": BY + 1.2 * P, "T-": BY + 2.2 * P, "B+": ROW_Y["j"] + 1.9 * P, "B-": ROW_Y["j"] + 2.9 * P}
BOARD_H = ROW_Y["j"] + 4.1 * P - BY

# Netzfarben
C = {
    "3V3": "#d73a49", "GND": "#24292f", "VBAT": "#e36209", "VSW": "#bf8700",
    "G": "#8250df", "HOLD": "#bf3989", "BTN": "#8c959f", "SENSE": "#8a5a2b",
    "SCK": "#d4a72c", "MOSI": "#1a7f37", "CS": "#0969da", "DC": "#1b9aaa",
    "RST": "#6e7781", "SCL": "#54aeff", "SDA": "#4ac26b",
}


def cx(col):
    return BX + 24 + (col - 1) * P


def hole(col, row):
    return (cx(col), RAIL_Y[row] if row in RAIL_Y else ROW_Y[row])


HALO = ' paint-order="stroke" stroke="#f3f1ea" stroke-width="3.5" stroke-linejoin="round"'


def t(x, y, s, size=11, anchor="start", fill="#1f2937", weight="400", font=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{fill}" font-weight="{weight}"{extra}>{s}</text>')


# ------------------------------------------------------------------ Steckbrett
def breadboard():
    s = [f'<rect x="{BX}" y="{BY}" width="{cx(COLS) - BX + 24}" height="{BOARD_H}" rx="6" fill="#f3f1ea" stroke="#c9c4b5"/>']
    x1 = cx(COLS) + 24
    # Mittelrinne
    gy = (ROW_Y["e"] + ROW_Y["f"]) / 2
    s.append(f'<rect x="{BX + 6}" y="{gy - 5}" width="{x1 - BX - 12}" height="10" fill="#e2ddd0"/>')
    # Schienen mit Farbstreifen
    for key, col, dy in (("T+", C["3V3"], -0.55 * P), ("T-", "#0969da", 0.55 * P), ("B+", C["VBAT"], -0.55 * P), ("B-", "#0969da", 0.55 * P)):
        y = RAIL_Y[key] + dy
        s.append(f'<line x1="{BX + 20}" y1="{y}" x2="{x1 - 20}" y2="{y}" stroke="{col}" stroke-width="1.6"/>')
    labels = {"T+": "+3V3", "T-": "GND", "B+": "VBAT", "B-": "GND"}
    for key, y in RAIL_Y.items():
        s.append(t(BX + 6, y + 3.5, "+" if "+" in key else "−", 11, fill="#57606a", weight="700"))
        s.append(t(x1 + 6, y + 3.5, labels[key], 10, fill=C["VBAT"] if key == "B+" else ("#d73a49" if key == "T+" else "#0969da"),
                   weight="700", font=MONO))
    # Löcher
    for col in range(1, COLS + 1):
        for row in list(ROW_Y) + list(RAIL_Y):
            x, y = hole(col, row)
            s.append(f'<rect x="{x - 2.6:.1f}" y="{y - 2.6:.1f}" width="5.2" height="5.2" rx="0.8" fill="#3d3a33" opacity="0.8"/>')
    # Beschriftung
    for col in (1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60):
        s.append(t(cx(col), ROW_Y["a"] - 10, str(col), 8, "middle", "#8c959f", font=MONO))
        s.append(t(cx(col), ROW_Y["j"] + 15, str(col), 8, "middle", "#8c959f", font=MONO))
    for r, y in ROW_Y.items():
        s.append(t(BX + 10, y + 3, r, 8, "middle", "#8c959f", font=MONO))
        s.append(t(x1 - 10, y + 3, r, 8, "middle", "#8c959f", font=MONO))
    return s


# ------------------------------------------------------------------ Bauteile
def resistor(a, b, bands, ref, val, lab_dx=0, lab_dy=0, lab=None):
    (x0, y0), (x1, y1) = a, b
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    horiz = abs(x1 - x0) > abs(y1 - y0)
    L = min(26, (abs(x1 - x0) if horiz else abs(y1 - y0)) - 6)
    s = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#9aa0a6" stroke-width="1.6"/>']
    if horiz:
        s.append(f'<rect x="{mx - L / 2}" y="{my - 4.5}" width="{L}" height="9" rx="4" fill="#e3c9a0" stroke="#a88b5c" stroke-width="0.8"/>')
        for i, c in enumerate(bands):
            bx = mx - L / 2 + 5 + i * (L - 10) / 3
            s.append(f'<rect x="{bx:.1f}" y="{my - 4.5}" width="2.2" height="9" fill="{c}"/>')
        lx, ly = mx + lab_dx, my - 9 + lab_dy
    else:
        s.append(f'<rect x="{mx - 4.5}" y="{my - L / 2}" width="9" height="{L}" rx="4" fill="#e3c9a0" stroke="#a88b5c" stroke-width="0.8"/>')
        for i, c in enumerate(bands):
            by = my - L / 2 + 4 + i * (L - 8) / 3
            s.append(f'<rect x="{mx - 4.5}" y="{by:.1f}" width="9" height="2" fill="{c}"/>')
        lx, ly = mx + 8 + lab_dx, my + 3 + lab_dy
    anchor = "middle" if horiz else "start"
    if lab:
        lx, ly, anchor = lab
    s.append(t(lx, ly, f'{ref} <tspan fill="#57606a" font-weight="400">{val}</tspan>', 9.5, anchor, weight="700", extra=HALO))
    return s


BR, BK, YE, OR = "#7a4a1d", "#1f1f1f", "#e3b505", "#e07b1a"
K100 = (BR, BK, YE)            # 100 kΩ: braun-schwarz-gelb
K10 = (BR, BK, OR)             # 10 kΩ: braun-schwarz-orange


def diode(a, b, ref, val, lab_dy=-8, lab=None):
    """a = Anode, b = Kathode (Ring)."""
    (x0, y0), (x1, y1) = a, b
    mx = (x0 + x1) / 2
    s = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#9aa0a6" stroke-width="1.6"/>',
         f'<rect x="{mx - 11}" y="{y0 - 4}" width="22" height="8" rx="2" fill="#2d333b"/>']
    ring = mx + 7 if x1 > x0 else mx - 9
    s.append(f'<rect x="{ring}" y="{y0 - 4}" width="2.4" height="8" fill="#d0d7de"/>')
    lx, ly, anchor = lab or (mx, y0 + lab_dy, "middle")
    s.append(t(lx, ly, f'{ref} <tspan fill="#57606a" font-weight="400">{val}</tspan>', 9.5, anchor, weight="700", extra=HALO))
    return s


def ceramic(a, b, ref, val):
    (x0, y0), (x1, y1) = a, b
    my = (y0 + y1) / 2
    return [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#9aa0a6" stroke-width="1.6"/>',
            f'<ellipse cx="{x0}" cy="{my}" rx="5.5" ry="4.5" fill="#d9a53f" stroke="#9a6a14" stroke-width="0.8"/>',
            t(x0, RAIL_Y["B-"] + 15, f'{ref} <tspan fill="#57606a" font-weight="400">{val}</tspan>', 9, "middle", weight="700", extra=HALO)]


def sot_adapter(cols, row, pins, ref, val, lab=None):
    """SOT-23 auf Adapterplatine, Stifte in einer Reihe; lab = (x, y, anchor) der Beschriftung."""
    x0, x1 = cx(cols[0]) - 6, cx(cols[-1]) + 6
    y = ROW_Y[row]
    s = [f'<rect x="{x0}" y="{y - 7}" width="{x1 - x0}" height="14" rx="1.5" fill="#1a7f37" stroke="#0f5323" stroke-width="0.8" opacity="0.92"/>',
         f'<rect x="{(x0 + x1) / 2 - 5}" y="{y - 4}" width="10" height="8" rx="1" fill="#2d333b"/>']
    for c, name in zip(cols, pins):
        s.append(f'<circle cx="{cx(c)}" cy="{y}" r="2" fill="#e6c25a"/>')
        s.append(t(cx(c), y - P / 2 + 1, name, 7, "middle", "#1a7f37", "700", MONO))
    lx, ly, anchor = lab or ((x0 + x1) / 2, y - 11, "middle")
    s.append(t(lx, ly, f'{ref} <tspan fill="#57606a" font-weight="400">{val}</tspan>', 9.5, anchor, weight="700", extra=HALO))
    return s


def to92(cols, row, pins, ref, val, lab=None):
    y = ROW_Y[row]
    x0, x1 = cx(cols[0]) - 6, cx(cols[-1]) + 6
    s = [f'<path d="M{x0} {y + 3} H{x1} A{(x1 - x0) / 2} {(x1 - x0) / 2.6} 0 0 0 {x0} {y + 3} Z" fill="#2d333b"/>']
    for c, name in zip(cols, pins):
        s.append(f'<circle cx="{cx(c)}" cy="{y}" r="1.8" fill="#c7cdd4"/>')
        s.append(t(cx(c), y + P / 2 + 3, name, 7, "middle", "#57606a", "700", MONO))
    lx, ly, anchor = lab or ((x0 + x1) / 2, y - 12, "middle")
    s.append(t(lx, ly, f'{ref} <tspan fill="#57606a" font-weight="400">{val}</tspan>', 9.5, "middle", weight="700", extra=HALO))
    return s


def button(c0, c1):
    x0, x1 = cx(c0), cx(c1)
    y0, y1 = ROW_Y["e"], ROW_Y["f"]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    sz = 6 * MM
    return [f'<rect x="{mx - sz / 2}" y="{my - sz / 2}" width="{sz}" height="{sz}" rx="2" fill="#30363d"/>',
            f'<circle cx="{mx}" cy="{my}" r="{sz * 0.3}" fill="#e6c25a" stroke="#9a6700" stroke-width="0.8"/>',
            t(mx + sz / 2 + 3, my - sz / 2 + 2, 'S1 <tspan fill="#57606a" font-weight="400">Taster</tspan>', 9.5, weight="700", extra=HALO)]


def d1mini():
    """D1 mini von oben, um 180° gedreht: USB links, Antenne rechts.
    Obere Stiftreihe (Reihe b): 3V3 D8 D7 D6 D5 D0 A0 RST, untere (Reihe i): 5V G D4 D3 D2 D1 RX TX."""
    c0, c7 = 34, 41
    x0 = cx(c0) - 9.1 * MM
    x1 = cx(c7) + 7.7 * MM
    yb, yi = ROW_Y["b"], ROW_Y["i"]
    ym = (yb + yi) / 2
    h = 25.6 * MM
    y0 = ym - h / 2
    s = [f'<path d="M{x0} {y0} H{x1 - 6} L{x1} {y0 + 6} V{y0 + h - 6} L{x1 - 6} {y0 + h} H{x0} Z" fill="#1f5fae" stroke="#123a6b" stroke-width="1" opacity="0.96"/>']
    # Micro-USB links, Reset-Taster
    s.append(f'<rect x="{x0 - 5}" y="{ym - 13}" width="22" height="26" rx="2" fill="#b7bec8" stroke="#6e7781" stroke-width="0.8"/>')
    s.append(f'<rect x="{x0 + 3}" y="{y0 + h - 16}" width="9" height="12" rx="1.5" fill="#c7cdd4"/>')
    # ESP-12F-Abschirmung und Antenne
    sx0 = cx(c0) + 1.5 * P
    s.append(f'<rect x="{sx0}" y="{ym - 6.2 * MM}" width="{15.5 * MM}" height="{12.4 * MM}" rx="2" fill="#c7cdd4" stroke="#8c959f" stroke-width="0.8"/>')
    s.append(t(sx0 + 7.75 * MM, ym - 4, "ESP8266MOD 12-F", 7.5, "middle", "#57606a", "700"))
    s.append(t(sx0 + 7.75 * MM, ym + 9, "U3 · D1 mini", 10, "middle", "#1f2937", "700"))
    s.append(t(sx0 + 7.75 * MM, ym + 21, "AZ-Delivery", 7.5, "middle", "#57606a"))
    ax = x1 - 6.5 * MM
    zig = " ".join(f"L{ax + (i % 2) * 4.2 * MM:.1f} {ym - 8 * MM + i * 2.3 * MM:.1f} L{ax + (i % 2) * 4.2 * MM:.1f} {ym - 8 * MM + (i + 1) * 2.3 * MM:.1f}" for i in range(7))
    s.append(f'<path d="M{ax:.1f} {ym - 8 * MM:.1f} {zig}" fill="none" stroke="#e6c25a" stroke-width="1.6" opacity="0.9"/>')
    top = ["3V3", "D8", "D7", "D6", "D5", "D0", "A0", "RST"]
    bot = ["5V", "G", "D4", "D3", "D2", "D1", "RX", "TX"]
    for i, (a, b) in enumerate(zip(top, bot)):
        x = cx(c0 + i)
        for y, name, dy in ((yb, a, 14), (yi, b, -8)):
            s.append(f'<circle cx="{x}" cy="{y}" r="3.4" fill="#e6c25a" stroke="#9a6700" stroke-width="0.8"/>')
            s.append(f'<circle cx="{x}" cy="{y}" r="1.4" fill="#3d3a33"/>')
            s.append(t(x, y + dy, name, 7.5, "middle", "#ffffff", "700", MONO))
    return s


def tft(x0, y0):
    """Rotes 1,8″-Modul von vorn, Stiftleiste unten. Gibt (svg, Pinpositionen) zurück."""
    w, h = 35 * MM, 58 * MM
    s = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="#c0262d" stroke="#7d1418" stroke-width="1"/>']
    for hx in (x0 + 3.5 * MM, x0 + w - 3.5 * MM):
        for hy in (y0 + 3.5 * MM, y0 + h - 3.5 * MM):
            s.append(f'<circle cx="{hx}" cy="{hy}" r="{1.6 * MM}" fill="#fbfaf6" stroke="#e6c25a" stroke-width="1.2"/>')
    gx, gy, gw, gh = x0 + 2.2 * MM, y0 + 8.5 * MM, w - 4.4 * MM, 41 * MM
    s.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" fill="#e9e6df"/>')
    s.append(f'<rect x="{gx + 1.2 * MM}" y="{gy + 1.2 * MM}" width="{gw - 2.4 * MM}" height="{gh - 5 * MM}" fill="#111318"/>')
    s.append(t(x0 + w / 2, gy + gh / 2 - 6, "128 × 160", 11, "middle", "#8b949e", "700", MONO))
    s.append(t(x0 + w / 2, gy + gh / 2 + 10, "ST7735?", 10, "middle", "#5ce1ff", "400", MONO))
    names = ["VCC", "GND", "CS", "RESET", "A0", "SDA", "SCK", "LED"]
    py = y0 + h - 3.2 * MM
    pins = {}
    for i, n in enumerate(names):
        px = x0 + w / 2 + (i - 3.5) * P
        shape = (f'<rect x="{px - 3.2}" y="{py - 3.2}" width="6.4" height="6.4" fill="#e6c25a"/>' if i == 0 else
                 f'<circle cx="{px}" cy="{py}" r="3.3" fill="#e6c25a"/>')
        s.append(shape)
        s.append(f'<circle cx="{px}" cy="{py}" r="1.3" fill="#3d3a33"/>')
        s.append(t(px, py - 8, n, 6.5, "end", "#ffe7e7", "700", MONO, extra=f' transform="rotate(90 {px} {py - 8})"'))
        pins[n] = (px, py)
    s.append(t(x0, y0 - 8, 'U4 <tspan fill="#57606a" font-weight="400">TFT 1,8″ · Stiftleiste von vorn, Pin 1 = VCC (eckig)</tspan>', 10, weight="700"))
    return s, pins


def bme(x0, y0):
    """BME280-Modul, Anschlüsse links (von oben: VIN GND SCL SDA)."""
    w, h = 13 * MM, 10.5 * MM
    s = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="2" fill="#7b3fb5" stroke="#4c2373" stroke-width="1"/>',
         f'<rect x="{x0 + w - 5.5 * MM}" y="{y0 + 1.5 * MM}" width="{2.5 * MM}" height="{2.5 * MM}" fill="#c7cdd4"/>',
         f'<circle cx="{x0 + w - 3 * MM}" cy="{y0 + h - 3 * MM}" r="{1.4 * MM}" fill="#fbfaf6" stroke="#e6c25a" stroke-width="1"/>']
    pins = {}
    for i, n in enumerate(["VIN", "GND", "SCL", "SDA"]):
        px, py = x0 + 2.2 * MM, y0 + h / 2 + (i - 1.5) * P
        s.append(f'<circle cx="{px}" cy="{py}" r="3.2" fill="#e6c25a"/>')
        s.append(f'<circle cx="{px}" cy="{py}" r="1.2" fill="#3d3a33"/>')
        s.append(t(px + 6, py + 3, n, 7, "start", "#ffffff", "700", MONO))
        pins[n] = (px, py)
    s.append(t(x0, y0 - 8, 'U5 <tspan fill="#57606a" font-weight="400">BME280 (GYBMEP)</tspan>', 10, weight="700"))
    return s, pins


def charger_and_cell():
    """Lademodul HW-168 und Akku links neben dem Steckbrett. Gibt (svg, BAT+, BAT−) zurück.

    Das Modul hat keinen Lastausgang; Akku und Steckbrett hängen beide an BAT+/BAT−.
    """
    x0, y0, w, h = 30, BY + 6, 220, 100
    s = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="#1f5fae" stroke="#123a6b"/>',
         f'<rect x="{x0 - 6}" y="{y0 + h / 2 - 14}" width="24" height="28" rx="2" fill="#b7bec8" stroke="#6e7781"/>',
         t(x0 + 30, y0 + 22, "U1 Lademodul", 10.5, fill="#ffffff", weight="700"),
         t(x0 + 30, y0 + 37, "HW-168 (TP4056)", 9, fill="#c9d7ea"),
         t(x0 + 30, y0 + 50, "Last an BAT+/BAT−", 9, fill="#c9d7ea"),
         f'<circle cx="{x0 + 40}" cy="{y0 + 68}" r="3.5" fill="#ff4d4f"/>',
         f'<circle cx="{x0 + 54}" cy="{y0 + 68}" r="3.5" fill="#3fb950"/>',
         t(x0 + 64, y0 + 71, "Lade-LEDs", 8, fill="#c9d7ea")]
    pads = {}
    for n, yy in (("BAT+", y0 + 30), ("BAT−", y0 + 82)):
        px = x0 + w - 8
        s.append(f'<rect x="{px - 4}" y="{yy - 4}" width="8" height="8" fill="#e6c25a"/>')
        s.append(t(px + 4, yy - 7, n, 7.5, "end", "#ffffff", "700", MONO))
        pads[n] = (px, yy)
    # Akku
    ax, ay, aw, ah = 30, BY + 150, 170, 84
    s.append(f'<rect x="{ax}" y="{ay}" width="{aw * 1.0}" height="{ah}" rx="4" fill="#c7cdd4" stroke="#8c959f"/>')
    s.append(f'<rect x="{ax + aw - 4}" y="{ay}" width="10" height="{ah}" rx="2" fill="#d9a62e"/>')
    s.append(t(ax + 8, ay + 22, "BT1 LiPo LP103454", 10, fill="#1f2937", weight="700"))
    s.append(t(ax + 8, ay + 37, "3,7 V · 2000 mAh · geschützt", 9, fill="#57606a"))
    s.append(t(ax + 8, ay + 51, "nicht maßstäblich", 8, fill="#8c959f"))
    for n, x, color in (("BAT+", ax + aw - 30, "#d73a49"), ("BAT−", ax + aw - 16, "#24292f")):
        s += wire([(x, ay), (x, pads[n][1]), pads[n]], color)
    return s, pads["BAT+"], pads["BAT−"]


# ------------------------------------------------------------------ Drähte
def wire(pts, color, end_dots=True):
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    s = [f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="4.6" stroke-linejoin="round" stroke-linecap="round"/>',
         f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round"/>']
    if end_dots:
        for x, y in (pts[0], pts[-1]):
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{color}" stroke="#000" stroke-opacity="0.4" stroke-width="0.8"/>')
    return s


def jumper(a, b, color, lift=0):
    """Gerade Brücke zwischen zwei Löchern; lift > 0 hebt die Mitte als Bogen an."""
    (x0, y0), (x1, y1) = a, b
    if not lift:
        return wire([a, b], color)
    mx = (x0 + x1) / 2
    d = f"M{x0:.1f} {y0:.1f} Q{mx:.1f} {min(y0, y1) - lift:.1f} {x1:.1f} {y1:.1f}"
    return [f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.25" stroke-width="4.6" stroke-linecap="round"/>',
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.2" stroke-linecap="round"/>',
            f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="2.6" fill="{color}"/>', f'<circle cx="{x1:.1f}" cy="{y1:.1f}" r="2.6" fill="{color}"/>']


def h(col, row):
    return hole(col, row)


# ------------------------------------------------------------------ Gesamtbild
def build():
    out = []
    out += breadboard()

    out.append(f'<rect x="{cx(4) - 8}" y="{BY - 34}" width="{cx(24) - cx(4) + 16}" height="22" rx="4" fill="#fff8c5" stroke="#d4a72c"/>')
    out.append(t(cx(4), BY - 19, "Bereich A · Selbsthaltung und 3,3-V-Regler (Spalten 4–24)", 10, weight="700", fill="#7d4e00"))

    # --- Bereich A: Bauteile (Drähte liegen obenauf)
    out += sot_adapter([4, 5, 6], "g", ["G", "S", "D"], "Q1", "", lab=(cx(4) - 9, ROW_Y["g"] + 3, "end"))
    out += to92([13, 14, 15], "g", ["C", "B", "E"], "Q2", "BC547", lab=(cx(15) + 9, ROW_Y["g"] + 3, "start"))
    out += to92([22, 23, 24], "g", ["GND", "IN", "OUT"], "U2", "HT7833", lab=(cx(23), ROW_Y["e"] + 3, "middle"))
    out += resistor(h(4, "j"), h(4, "B+"), K100, "R1", "100k", lab_dx=-62)
    out += resistor(h(14, "e"), h(14, "f"), K10, "R2", "10k")
    out += resistor(h(14, "i"), h(18, "i"), K100, "R3", "100k", lab=(cx(14) - 8, ROW_Y["i"] + 3.5, "end"))
    out += resistor(h(6, "e"), h(6, "f"), K100, "R4", "100k", lab_dx=-62)
    out += resistor(h(50, "c"), h(54, "c"), K10, "R5", "10k")
    out += diode(h(4, "i"), h(8, "i"), "D1", "BAT85", lab=(cx(4) - 9, ROW_Y["i"] + 3.5, "end"))
    out += diode(h(12, "c"), h(8, "c"), "D2", "BAT85")
    out += button(8, 10)
    out += ceramic(h(20, "j"), h(20, "B-"), "C1", "1µ")
    out += ceramic(h(24, "j"), h(24, "B-"), "C2", "1µ")

    # --- Drähte Bereich A
    out += jumper(h(5, "j"), h(5, "B+"), C["VBAT"])
    out += jumper(h(13, "h"), h(4, "h"), C["G"], lift=8)
    out += jumper(h(6, "h"), h(20, "h"), C["VSW"], lift=14)
    out += jumper(h(20, "i"), h(23, "i"), C["VSW"], lift=6)
    for col in (10, 15, 18, 22):
        out += wire([h(col, "j"), (cx(col), RAIL_Y["B-"])], C["GND"])
    out += wire([h(24, "h"), (cx(24) + 8, ROW_Y["h"] - 6), (cx(24) + 8, RAIL_Y["T+"] + 5), (cx(25), RAIL_Y["T+"])], C["3V3"])

    # --- D1 mini und Anschlüsse
    out += d1mini()
    out += wire([h(34, "a"), h(34, "T+")], C["3V3"])
    out += wire([h(35, "j"), (cx(35), RAIL_Y["B-"])], C["GND"])
    lane = ROW_Y["a"] - 0.8 * P
    out += wire([h(6, "a"), (cx(6), lane + 3), (cx(40) - 4, lane + 3), (cx(40), ROW_Y["a"])], C["SENSE"])
    out += wire([h(14, "a"), (cx(14), lane - 3), (cx(39) - 4, lane - 3), (cx(39), ROW_Y["a"])], C["HOLD"])
    low = ROW_Y["j"] + 0.6 * P
    out += wire([h(12, "a"), (cx(12) + 5, ROW_Y["a"] - 0.45 * P), (cx(28), ROW_Y["a"] - 0.45 * P), (cx(28), low), (cx(40), low), h(40, "j")], C["BTN"])

    # --- TFT oben rechts
    tsvg, tp = tft(cx(47) - 10, 96)
    out += tsvg
    base = tp["VCC"][1]
    lv = lambda i: base + 18 + i * 6.5
    out += wire([tp["VCC"], (tp["VCC"][0], lv(7)), (cx(47), lv(7)), h(47, "T+")], C["3V3"])
    out += wire([tp["GND"], (tp["GND"][0], lv(6)), (cx(48), lv(6)), h(48, "T-")], C["GND"])
    out += wire([tp["CS"], (tp["CS"][0], lv(0)), (cx(35), lv(0)), h(35, "a")], C["CS"])
    out += wire([tp["RESET"], (tp["RESET"][0], lv(5)), (cx(50), lv(5)), h(50, "a")], C["RST"])
    out += wire([tp["A0"], (tp["A0"][0], lv(3)), (cx(44) + 6, lv(3)), (cx(44) + 6, ROW_Y["j"] + 1.2 * P), (cx(37), ROW_Y["j"] + 1.2 * P), h(37, "j")], C["DC"])
    out += wire([tp["SDA"], (tp["SDA"][0], lv(1)), (cx(36), lv(1)), h(36, "a")], C["MOSI"])
    out += wire([tp["SCK"], (tp["SCK"][0], lv(2)), (cx(38), lv(2)), h(38, "a")], C["SCK"])
    out += wire([tp["LED"], (tp["LED"][0], lv(4)), (cx(55), lv(4)), h(55, "T+")], C["3V3"])
    out += wire([h(54, "a"), h(54, "T+")], C["3V3"])

    # --- BME280 rechts unterhalb
    bsvg, bp = bme(cx(COLS) + 104, BY + BOARD_H + 40)
    out += bsvg
    r = cx(COLS) + 80
    out += wire([bp["VIN"], (r + 8, bp["VIN"][1]), (r + 8, BY - 8), (cx(62), BY - 8), h(62, "T+")], C["3V3"])
    out += wire([bp["GND"], (r, bp["GND"][1]), (r, BY + BOARD_H + 8), (cx(62), BY + BOARD_H + 8), h(62, "B-")], C["GND"])
    y_scl, y_sda = BY + BOARD_H + 16, BY + BOARD_H + 25
    out += wire([bp["SCL"], (r - 10, bp["SCL"][1]), (r - 10, y_scl), (cx(39), y_scl), h(39, "j")], C["SCL"])
    out += wire([bp["SDA"], (r - 18, bp["SDA"][1]), (r - 18, y_sda), (cx(38) + 5, y_sda), (cx(38) + 5, ROW_Y["j"] + 5), h(38, "j")], C["SDA"])
    out += wire([h(63, "T-"), (cx(63) + 12, RAIL_Y["T-"]), (cx(63) + 12, RAIL_Y["B-"]), h(63, "B-")], C["GND"])

    # --- Lademodul und Akku
    csvg, op, om = charger_and_cell()
    out += csvg
    out += wire([op, (BX - 22, op[1]), (BX - 22, RAIL_Y["B+"]), h(1, "B+")], C["VBAT"])
    out += wire([om, (BX - 32, om[1]), (BX - 32, RAIL_Y["B-"]), h(1, "B-")], C["GND"])
    return out


def legend():
    items = [("+3V3", "3V3"), ("GND", "GND"), ("VBAT", "VBAT"), ("VSW geschaltet", "VSW"), ("Gate G", "G"),
             ("HOLD", "HOLD"), ("BTN", "BTN"), ("VBAT_SENSE", "SENSE"), ("SCK", "SCK"), ("MOSI/SDA", "MOSI"),
             ("CS", "CS"), ("DC/A0", "DC"), ("RESET", "RST"), ("I²C SCL", "SCL"), ("I²C SDA", "SDA")]
    s = []
    x, y = 30, 110
    s.append(t(x, y, "Drahtfarben", 12, weight="700"))
    for i, (name, key) in enumerate(items):
        cx_, cy_ = x + (i % 5) * 120, y + 22 + (i // 5) * 20
        s.append(f'<line x1="{cx_}" y1="{cy_ - 4}" x2="{cx_ + 18}" y2="{cy_ - 4}" stroke="{C[key]}" stroke-width="3.2" stroke-linecap="round"/>')
        s.append(t(cx_ + 24, cy_, name, 10, font=MONO))
    notes = [
        "<tspan font-weight=\"700\">Entwurf.</tspan> Nicht aufgebaut. Bauteilnamen wie im Schaltplan (assets/schematic.svg).",
        "M1 (TFT-Smoke-Test): nur Bereich B, TFT und BME280 stecken; der D1 mini läuft über USB und speist mit 3V3 die +3V3-Schiene.",
        "Bereich A erst in M2 stecken. Dann den D1 mini nicht mehr über seine USB-Buchse versorgen (Rückspeisung in U2).",
        "Q1 (SOT-23) sitzt auf einer Adapterplatine. U2 HT7833 (TO-92): Pinfolge GND–IN–OUT vor dem Stecken am Datenblatt prüfen.",
        "Der D1 mini belegt die Reihen b und i: frei bleibt je Pin nur ein Loch (Reihe a bzw. j).",
        "S1 steckt über der Mittelrinne; die Kontakte oben und unten in derselben Spalte sind im Taster verbunden.",
    ]
    ny = y + 92
    s.append(t(x, ny, "Hinweise", 12, weight="700"))
    for i, n in enumerate(notes):
        s.append(t(x, ny + 22 + i * 19, "• " + n, 11))
    return s


def main():
    body = build() + legend()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Breadboard-Aufbau MeteoLander: D1 mini, TFT, BME280, Selbsthalteschaltung, Lademodul und Akku auf einem Steckbrett">
  <rect width="{W}" height="{H}" fill="#fbfaf6"/>
  <rect x="0" y="0" width="{W}" height="64" fill="#0b1530"/>
  {t(30, 40, "MeteoLander – Breadboard", 22, fill="#ffffff", weight="700")}
  {t(W - 30, 30, "ENTWURF · NICHT AUFGEBAUT · NICHT GEPRÜFT", 13, "end", "#e6c25a", "600")}
  {t(W - 30, 48, "Rev. 0.1 · 2026-11-15 · erzeugt mit tools/breadboard.py", 12, "end", "#8b949e")}
  {chr(10).join("  " + x for x in body)}
</svg>
'''
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print("assets/breadboard.svg geschrieben")


if __name__ == "__main__":
    main()
