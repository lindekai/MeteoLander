#!/usr/bin/env python3
"""MeteoLander – Bauzeichnung im Maßstab 1:1

Erzeugt aus den Maßen in tools/lander_model.py eine Bauzeichnung auf A4:
  - assets/build-drawing.pdf       zum Drucken (beide Blätter, exakt in mm)
  - assets/build-drawing-1.svg     Blatt 1: Käfig, Zuschnittliste
  - assets/build-drawing-2.svg     Blatt 2: Landebeine, Aufstellplan

Die Drähte sind in ihrer echten Stärke (0,8 mm) gezeichnet; man legt sie direkt auf den
Ausdruck. Ohne externe Bibliotheken: PDF und SVG entstehen aus denselben Zeichenbefehlen.

Aufruf:  python3 tools/build_drawing.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lander_model as M  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

PW, PH = 210.0, 297.0          # A4 hoch, mm
REV = "Rev. 0.1 · 2026-11-15"

K = (0.12, 0.16, 0.22)         # Linien und Text
GREY = (0.45, 0.48, 0.52)
LIGHT = (0.75, 0.77, 0.80)
BRASS = (0.86, 0.69, 0.25)
BRASS_DARK = (0.48, 0.36, 0.10)
RED = (0.75, 0.15, 0.18)
CU = (0.78, 0.45, 0.23)


def fmt(v):
    """Zahl mit deutschem Dezimalkomma, höchstens eine Nachkommastelle."""
    r = round(v, 1)
    return (str(int(r)) if r == int(r) else f"{r:.1f}").replace(".", ",")


# ------------------------------------------------------------------ Zeichenfläche
class Page:
    def __init__(self):
        self.ops = []

    def line(self, x1, y1, x2, y2, w=0.18, color=K, dash=None):
        self.ops.append(("poly", [(x1, y1), (x2, y2)], w, color, dash, False, None))

    def poly(self, pts, w=0.18, color=K, dash=None, closed=False, fill=None):
        self.ops.append(("poly", list(pts), w, color, dash, closed, fill))

    def rect(self, x, y, rw, rh, **kw):
        self.poly([(x, y), (x + rw, y), (x + rw, y + rh), (x, y + rh)], closed=True, **kw)

    def circle(self, cx, cy, r, w=0.18, color=K, fill=None, dash=None):
        self.ops.append(("circle", cx, cy, r, w, color, fill, dash))

    def text(self, x, y, s, size=2.6, bold=False, anchor="start", color=K):
        self.ops.append(("text", x, y, s, size, bold, anchor, color))

    def rod(self, pts, closed=False):
        """Messingdraht in echter Stärke mit dünner Mittellinie."""
        self.poly(pts, w=M.ROD, color=BRASS, closed=closed)
        self.poly(pts, w=0.08, color=BRASS_DARK, closed=closed)

    def joint(self, x, y):
        self.circle(x, y, 0.75, w=0.12, color=GREY, fill=(1, 1, 1))

    def arrow(self, tip, frm, size=1.3):
        ux, uy = tip[0] - frm[0], tip[1] - frm[1]
        l = math.hypot(ux, uy) or 1
        ux, uy = ux / l, uy / l
        bx, by = tip[0] - ux * size, tip[1] - uy * size
        self.poly([tip, (bx - uy * size * 0.33, by + ux * size * 0.33), (bx + uy * size * 0.33, by - ux * size * 0.33)],
                  w=0.05, color=K, closed=True, fill=K)

    def dim(self, p, q, off, label=None, size=2.3):
        """Bemaßung von p nach q, um off (mm) seitlich versetzt; positiv = links der Richtung p→q."""
        dx, dy = q[0] - p[0], q[1] - p[1]
        l = math.hypot(dx, dy)
        nx, ny = dy / l, -dx / l
        a = (p[0] + nx * off, p[1] + ny * off)
        b = (q[0] + nx * off, q[1] + ny * off)
        ext = 1.2 if off > 0 else -1.2
        self.line(p[0] + nx * 0.6 * (1 if off > 0 else -1), p[1] + ny * 0.6 * (1 if off > 0 else -1),
                  a[0] + nx * ext, a[1] + ny * ext, w=0.12, color=GREY)
        self.line(q[0] + nx * 0.6 * (1 if off > 0 else -1), q[1] + ny * 0.6 * (1 if off > 0 else -1),
                  b[0] + nx * ext, b[1] + ny * ext, w=0.12, color=GREY)
        self.line(a[0], a[1], b[0], b[1], w=0.15)
        self.arrow(a, b)
        self.arrow(b, a)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        s = label if label is not None else fmt(l)
        if abs(dx) >= abs(dy):                      # waagerecht: Text über bzw. unter der Linie
            ty = my - 0.9 if ny <= 0 else my + size + 0.6
            self.text(mx, ty, s, size, anchor="middle")
        else:                                       # senkrecht: Text neben der Linie
            if nx >= 0:
                self.text(mx + 1.2, my + size * 0.35, s, size)
            else:
                self.text(mx - 1.2, my + size * 0.35, s, size, anchor="end")

    def heading(self, x, y, num, title, sub=None):
        self.circle(x + 2.2, y - 1.0, 2.4, w=0.25, color=K)
        self.text(x + 2.2, y, str(num), 2.8, True, "middle")
        self.text(x + 6.2, y, title, 3.4, True)
        if sub:
            self.text(x + 6.2, y + 4.2, sub, 2.4, color=GREY)


# ------------------------------------------------------------------ Ausgabe SVG
def svg_page(page, title):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW}mm" height="{PH}mm" viewBox="0 0 {PW} {PH}" '
           f'role="img" aria-label="{title}">',
           f'<rect width="{PW}" height="{PH}" fill="#ffffff"/>']
    col = lambda c: "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in c)
    for op in page.ops:
        if op[0] == "poly":
            _, pts, w, c, dash, closed, fill = op
            d = "M" + " L".join(f"{x:.3f} {y:.3f}" for x, y in pts) + (" Z" if closed else "")
            da = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
            out.append(f'<path d="{d}" fill="{col(fill) if fill else "none"}" stroke="{col(c)}" stroke-width="{w}" '
                       f'stroke-linecap="round" stroke-linejoin="round"{da}/>')
        elif op[0] == "circle":
            _, x, y, r, w, c, fill, dash = op
            da = f' stroke-dasharray="{dash[0]} {dash[1]}"' if dash else ""
            out.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" fill="{col(fill) if fill else "none"}" '
                       f'stroke="{col(c)}" stroke-width="{w}"{da}/>')
        else:
            _, x, y, s, size, bold, anchor, c = op
            s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            out.append(f'<text x="{x:.3f}" y="{y:.3f}" font-family="Helvetica, Arial, sans-serif" font-size="{size}" '
                       f'font-weight="{"700" if bold else "400"}" text-anchor="{anchor}" fill="{col(c)}">{s}</text>')
    out.append("</svg>\n")
    return "\n".join(out)


# ------------------------------------------------------------------ Ausgabe PDF
# Zeichenbreiten von Helvetica (1/1000 em) für die Textausrichtung
_W = dict(zip(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
              [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
              [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833,
               722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556, 333, 556,
               556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333, 500, 278, 556,
               500, 722, 500, 500, 500, 334, 260, 334, 584]))
_W.update({"ä": 556, "ö": 556, "ü": 556, "Ä": 667, "Ö": 778, "Ü": 722, "ß": 611, "–": 556, "·": 278, "„": 333,
           "“": 333, "×": 584, "Ø": 778, "°": 400, "µ": 556, "²": 333})


def text_width(s, size, bold):
    return sum(_W.get(ch, 556) for ch in s) / 1000 * size * (1.06 if bold else 1.0)


def pdf_stream(page):
    k = 72 / 25.4
    o = [f"{k:.6f} 0 0 {-k:.6f} 0 {PH * k:.4f} cm", "1 J 1 j"]
    rgb = lambda c: "%.3f %.3f %.3f" % c
    for op in page.ops:
        if op[0] == "poly":
            _, pts, w, c, dash, closed, fill = op
            o.append(f"{w:.3f} w {rgb(c)} RG" + (f" [{dash[0]} {dash[1]}] 0 d" if dash else " [] 0 d"))
            path = f"{pts[0][0]:.3f} {pts[0][1]:.3f} m " + " ".join(f"{x:.3f} {y:.3f} l" for x, y in pts[1:])
            if fill:
                o.append(f"{rgb(fill)} rg {path} h B")
            else:
                o.append(path + (" h S" if closed else " S"))
        elif op[0] == "circle":
            _, x, y, r, w, c, fill, dash = op
            m = 0.5523 * r
            path = (f"{x + r:.3f} {y:.3f} m {x + r:.3f} {y + m:.3f} {x + m:.3f} {y + r:.3f} {x:.3f} {y + r:.3f} c "
                    f"{x - m:.3f} {y + r:.3f} {x - r:.3f} {y + m:.3f} {x - r:.3f} {y:.3f} c "
                    f"{x - r:.3f} {y - m:.3f} {x - m:.3f} {y - r:.3f} {x:.3f} {y - r:.3f} c "
                    f"{x + m:.3f} {y - r:.3f} {x + r:.3f} {y - m:.3f} {x + r:.3f} {y:.3f} c h")
            o.append(f"{w:.3f} w {rgb(c)} RG" + (f" [{dash[0]} {dash[1]}] 0 d" if dash else " [] 0 d"))
            o.append(f"{rgb(fill)} rg {path} B" if fill else f"{path} S")
        else:
            _, x, y, s, size, bold, anchor, c = op
            wdt = text_width(s, size, bold)
            x0 = x - (wdt / 2 if anchor == "middle" else wdt if anchor == "end" else 0)
            raw = s.encode("cp1252")
            esc = raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            o.append(f"BT /{'F2' if bold else 'F1'} {size:.3f} Tf {rgb(c)} rg 1 0 0 -1 {x0:.3f} {y:.3f} Tm (".encode()
                     .decode("latin-1") + esc.decode("latin-1") + ") Tj ET")
    return "\n".join(o).encode("latin-1")


def write_pdf(pages, path):
    objs = []

    def add(b):
        objs.append(b)
        return len(objs)

    f1 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    f2 = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    pages_id = len(objs) + 1 + 2 * len(pages) + 1
    kids = []
    for pg in pages:
        data = pdf_stream(pg)
        cid = add(b"<< /Length %d >>\nstream\n" % len(data) + data + b"\nendstream")
        kids.append(add(("<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %.4f %.4f] /Contents %d 0 R "
                         "/Resources << /Font << /F1 %d 0 R /F2 %d 0 R >> >> >>"
                         % (pages_id, PW * 72 / 25.4, PH * 72 / 25.4, cid, f1, f2)).encode()))
    info = add(b"<< /Title (MeteoLander - Bauzeichnung 1:1) /Producer (tools/build_drawing.py) >>")
    assert add(("<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join(f"{k} 0 R" for k in kids), len(kids))).encode()) == pages_id
    cat = add(b"<< /Type /Catalog /Pages %d 0 R /ViewerPreferences << /PrintScaling /None >> >>" % pages_id)
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offs = []
    for i, b in enumerate(objs, 1):
        offs.append(len(out))
        out += b"%d 0 obj\n" % i + b + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offs)
    out += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, cat, info, xref)
    with open(path, "wb") as f:
        f.write(out)


# ------------------------------------------------------------------ Geometrie aus dem Modell
CW, CD = M.CAGE_W, M.CAGE_D
CH = M.CAGE_Z1 - M.CAGE_Z0
TFT_BOTTOM = M.TFT_Z0 - M.CAGE_Z0                 # Unterkante TFT über der unteren Käfigkante
HOLE_Z = (TFT_BOTTOM + M.TFT_H / 2 - M.TFT_HOLE_DZ / 2, TFT_BOTTOM + M.TFT_H / 2 + M.TFT_HOLE_DZ / 2)
HOLDER = CW / 2 - M.TFT_HOLE_DX / 2               # Draht vom TFT-Loch zur Käfigsenkrechten
STUB = M.LEG_FOOT_Z - 0.5                         # Stummel vom Fußpunkt zum Teller

LEG = M.leg_points(CW / 2, 0.0)                   # vorn rechts; alle vier Beine sind gleich (gespiegelt)


def radial(p):
    """(r, z): Abstand von der Käfigkante entlang der Beinrichtung und Höhe über dem Boden."""
    c = LEG["lo"]
    return ((p[0] - c[0]) * LEG["d"][0] + (p[1] - c[1]) * LEG["d"][1], p[2])


def lateral(p):
    """(s, z): seitlicher Versatz quer zur Beinrichtung und Höhe – Blick von außen auf das Bein."""
    c = LEG["lo"]
    return ((p[0] - c[0]) * LEG["perp"][0] + (p[1] - c[1]) * LEG["perp"][1], p[2])


HOLM_A = math.dist(LEG["hi"], LEG["k1"])          # oberer Schenkel eines Holms
HOLM_B = math.dist(LEG["k1"], LEG["foot"])        # unterer Schenkel
HOLM_C = math.dist(LEG["hi"], LEG["foot"])        # Sehne
KNEE_INNER = math.degrees(math.acos((HOLM_A ** 2 + HOLM_B ** 2 - HOLM_C ** 2) / (2 * HOLM_A * HOLM_B)))
STRUT = math.dist(LEG["lo"], LEG["strut"])
BAR_K = math.dist(LEG["k1"], LEG["k2"])
BAR_M = math.dist(LEG["m1"], LEG["m2"])
FOOT_DX = 2 * LEG["foot"][0]                      # Abstand der Fußpunkte quer
FOOT_DY = M.leg_points(CW / 2, CD)["foot"][1] - LEG["foot"][1]

CUT_LIST = [
    ("1", "Bodenrahmen", 1, 2 * (CW + CD), "ein Stück, 3 × 90° gebogen, Stoß an einer Ecke"),
    ("2", "Deckrahmen", 1, 2 * (CW + CD), "wie Bodenrahmen"),
    ("2, 4", "Querstäbe Deckrahmen", 2, CW, "Taster vorn, Mast in der Mitte"),
    ("3, 4", "Senkrechte", 4, CH, ""),
    ("3, 4", "Display-Halter", 4, HOLDER, "vom TFT-Loch zur Senkrechten"),
    ("4", "Mast", 1, M.MAST_H, "BME280 oben"),
    ("8", "Holme", 8, HOLM_A + HOLM_B, f"am Knie um {fmt(180 - KNEE_INNER)}° gebogen"),
    ("7, 10", "Streben", 4, STRUT, "untere Käfigecke bis Mittel-Querstab"),
    ("9, 10", "Querstab Knie", 4, BAR_K, ""),
    ("9, 10", "Querstab Mitte", 4, BAR_M, ""),
    ("7, 10", "Stummel zum Teller", 4, STUB, ""),
]


# ------------------------------------------------------------------ Rahmen der Blätter
def frame(pg, sheet, title):
    pg.rect(8, 8, PW - 16, PH - 16, w=0.35)
    pg.text(12, 16.5, "MeteoLander – Bauzeichnung 1:1", 5.2, True)
    pg.text(12, 22, f"Blatt {sheet}/2 · {title} · Messingdraht Ø {fmt(M.ROD)} mm · Maße in mm · {REV}", 2.6, color=GREY)
    pg.rect(127, 11, 71, 13, w=0.3, color=RED)
    pg.text(162.5, 15.6, "Drucken mit „Tatsächliche Größe“ / 100 %", 2.6, True, "middle", RED)
    pg.text(162.5, 19.4, "nicht „An Seite anpassen“ – danach die", 2.4, False, "middle", RED)
    pg.text(162.5, 22.6, "Kontrollstrecken nachmessen!", 2.4, False, "middle", RED)
    pg.line(8, 26, PW - 8, 26, w=0.25)
    # Kontrollstrecken: 100 mm waagerecht, 50 mm senkrecht
    x0, y0 = 14, 282
    pg.line(x0, y0, x0 + 100, y0, w=0.3)
    for i in range(0, 101):
        h = 2.6 if i % 10 == 0 else (1.8 if i % 5 == 0 else 1.0)
        pg.line(x0 + i, y0, x0 + i, y0 - h, w=0.12 if i % 10 else 0.2)
    for v in (0, 50, 100):
        pg.text(x0 + v, y0 + 3.4, str(v), 2.3, anchor="middle")
    pg.text(x0 + 104, y0 + 0.8, "Kontrollstrecke 100 mm", 2.6, True)
    pg.text(x0 + 104, y0 + 4.4, "muss genau 100 mm messen", 2.3, color=GREY)
    xv, yv = 196, 282
    pg.line(xv, yv, xv, yv - 50, w=0.3)
    for i in range(0, 51):
        h = 2.6 if i % 10 == 0 else (1.8 if i % 5 == 0 else 1.0)
        pg.line(xv, yv - i, xv - h, yv - i, w=0.12 if i % 10 else 0.2)
    pg.text(xv - 1, yv - 52, "50 mm", 2.3, anchor="end")


def gauge(pg, x, y, length, label, count):
    """Längenlehre: Draht in echter Länge mit Anschlagstrichen."""
    pg.rod([(x, y), (x + length, y)])
    for xx in (x, x + length):
        pg.line(xx, y - 2.2, xx, y + 2.2, w=0.2)
    pg.text(x + length + 3, y + 0.9, f"{label} · {count} × {fmt(length)} mm", 2.6)


# ------------------------------------------------------------------ Blatt 1: Käfig
def sheet1():
    pg = Page()
    frame(pg, 1, "Käfig")

    # ① Bodenrahmen, Draufsicht (vorn unten)
    ox, oy = 16, 42
    pg.heading(ox - 2, 34, 1, "Bodenrahmen", "Draufsicht, vorn ist unten")
    pts = [(ox, oy), (ox + CW, oy), (ox + CW, oy + CD), (ox, oy + CD)]
    pg.rod(pts, closed=True)
    for x, y in pts:
        pg.joint(x, y)
    pg.text(ox + CW / 2, oy + CD + 4, "vorn", 2.4, anchor="middle", color=GREY)
    pg.text(ox + CW / 2, oy + CD / 2 - 1, "an jeder Ecke:", 2.2, anchor="middle", color=GREY)
    pg.text(ox + CW / 2, oy + CD / 2 + 2.2, "Senkrechte + Strebe", 2.2, anchor="middle", color=GREY)
    pg.dim((ox, oy + CD), (ox + CW, oy + CD), -9)
    pg.dim((ox + CW, oy + CD), (ox + CW, oy), -6)

    # ② Deckrahmen mit Querstäben
    ox = 78
    pg.heading(ox - 2, 34, 2, "Deckrahmen", "Draufsicht, vorn ist unten")
    pts = [(ox, oy), (ox + CW, oy), (ox + CW, oy + CD), (ox, oy + CD)]
    pg.rod(pts, closed=True)
    yb = oy + CD - M.BTN_BAR_Y
    ym = oy + CD / 2
    pg.rod([(ox, yb), (ox + CW, yb)])
    pg.rod([(ox, ym), (ox + CW, ym)])
    for x, y in pts + [(ox, yb), (ox + CW, yb), (ox, ym), (ox + CW, ym)]:
        pg.joint(x, y)
    pg.circle(ox + CW / 2, ym, 1.4, w=0.25, color=CU)
    pg.text(ox + CW / 2, ym - 2.6, "Mast", 2.3, anchor="middle", color=CU)
    pg.rect(ox + CW / 2 - 3, yb - 3, 6, 6, w=0.2, color=GREY, dash=(0.8, 0.6))
    pg.text(ox + CW / 2, yb - 4, "Taster", 2.3, anchor="middle", color=GREY)
    pg.text(ox + CW / 2, oy + CD + 4, "vorn", 2.4, anchor="middle", color=GREY)
    pg.dim((ox + CW, oy + CD), (ox + CW, yb), -5)
    pg.dim((ox + CW, oy + CD), (ox + CW, ym), -12)
    pg.dim((ox, oy + CD), (ox + CW, oy + CD), -9)

    # ③ Vorderansicht mit Display und Haltern
    ox, oy = 146, 42
    pg.heading(ox - 2, 34, 3, "Vorderansicht", "Display an vier Haltern")
    bot = oy + CH
    pg.rod([(ox, bot), (ox + CW, bot), (ox + CW, oy), (ox, oy)], closed=True)
    tx0 = ox + CW / 2 - M.TFT_W / 2
    pg.rect(tx0, bot - TFT_BOTTOM - M.TFT_H, M.TFT_W, M.TFT_H, w=0.3, color=RED, dash=(1.2, 0.8))
    pg.text(ox + CW / 2, bot - TFT_BOTTOM - M.TFT_H / 2 - 1, "TFT", 3, True, "middle", RED)
    pg.text(ox + CW / 2, bot - TFT_BOTTOM - M.TFT_H / 2 + 2.6, "Umriss", 2.2, False, "middle", RED)
    for hx in (ox + CW / 2 - M.TFT_HOLE_DX / 2, ox + CW / 2 + M.TFT_HOLE_DX / 2):
        for hz in HOLE_Z:
            edge = ox if hx < ox + CW / 2 else ox + CW
            pg.rod([(hx, bot - hz), (edge, bot - hz)])
            pg.circle(hx, bot - hz, 1.5, w=0.2, color=RED)
            pg.joint(edge, bot - hz)
    for x, y in ((ox, bot), (ox + CW, bot), (ox, oy), (ox + CW, oy)):
        pg.joint(x, y)
    pg.dim((ox, bot), (ox + CW, bot), -9)
    pg.dim((ox + CW, bot), (ox + CW, oy), -6)
    hl = ox + CW / 2 - M.TFT_HOLE_DX / 2
    pg.dim((hl, bot - HOLE_Z[1]), (hl + M.TFT_HOLE_DX, bot - HOLE_Z[1]), 4)
    pg.dim((ox, bot), (ox, bot - HOLE_Z[0]), 4)
    pg.dim((ox, bot - HOLE_Z[0]), (ox, bot - HOLE_Z[1]), 4)
    pg.text(ox + CW / 2, bot + 13.5, "Bohrungsabstand am TFT vor dem Bau messen", 2.1, anchor="middle", color=RED)

    # ④–⑤ Längenlehren
    y = 138
    pg.heading(14, y, 4, "Längenlehren", "Draht auf die Linie legen, an den Strichen abkneifen")
    gauge(pg, 16, y + 11, CH, "Senkrechte", 4)
    gauge(pg, 16, y + 19, CW, "Querstab Deckrahmen", 2)
    gauge(pg, 16, y + 27, M.MAST_H, "Mast", 1)
    gauge(pg, 16, y + 35, HOLDER, "Display-Halter", 4)

    # Zuschnittliste
    y = 190
    pg.heading(14, y, 5, "Zuschnittliste", "Nettolängen ohne Zugabe; je Lötstelle 1–2 mm zugeben")
    cols = (16, 26, 74, 88, 108)
    yy = y + 10
    for x, h in zip(cols, ("Abb.", "Teil", "Anz.", "je mm", "Bemerkung")):
        pg.text(x, yy, h, 2.4, True)
    pg.line(14, yy + 1.2, 186, yy + 1.2, w=0.2)
    total = 0.0
    for i, (pos, name, n, l, note) in enumerate(CUT_LIST):
        yy = y + 14.6 + i * 4.3
        for x, s in zip(cols, (pos, name, str(n), fmt(l), note)):
            pg.text(x, yy, s, 2.4)
        total += n * l
    yy += 2
    pg.line(14, yy, 186, yy, w=0.2)
    pg.text(26, yy + 4, f"Summe Messingdraht Ø {fmt(M.ROD)} mm: ca. {fmt(total / 10)} cm netto – mit Zugabe "
                        f"und Verschnitt etwa {fmt(math.ceil(total * 1.3 / 100) / 10)} m bereitlegen", 2.4, True)
    pg.text(26, yy + 8.4, "Dazu: 4 Landeteller Ø 14 mm aus Messingblech (Vorlage auf Blatt 2)", 2.4)
    return pg


# ------------------------------------------------------------------ Blatt 2: Landebeine
def sheet2():
    pg = Page()
    frame(pg, 2, "Landebeine (4 ×)")

    # ⑥ Aufstellplan, Draufsicht
    corners = [(-CW / 2, 0.0), (CW / 2, 0.0), (CW / 2, CD), (-CW / 2, CD)]
    legs = [M.leg_points(cx, cy) for cx, cy in corners]
    ymax = max(L["foot"][1] for L in legs) + M.PAD_R
    cx0, oy = 105, 40
    P = lambda p: (cx0 + p[0], oy + (ymax - p[1]))
    pg.heading(14, 34, 6, "Aufstellplan", "Draufsicht · Ausdruck unter die Fähre legen")
    pg.poly([P((x, y, 0)) for x, y in corners], w=0.25, color=GREY, dash=(1.2, 0.8), closed=True)
    pg.text(*P((0, CD / 2, 0)), "Käfig", 2.6, anchor="middle", color=GREY)
    for L in legs:
        f = P(L["foot"])
        pg.circle(f[0], f[1], M.PAD_R, w=0.35, color=BRASS_DARK)
        pg.line(f[0] - 2, f[1], f[0] + 2, f[1], w=0.15)
        pg.line(f[0], f[1] - 2, f[0], f[1] + 2, w=0.15)
        for k in ("k1", "k2"):
            pg.rod([P(L["hi"]), P(L[k]), P(L["foot"])])
        pg.rod([P(L["k1"]), P(L["k2"])])
        pg.rod([P(L["lo"]), P(L["strut"])])
    pg.text(cx0, P((0, 0, 0))[1] - 2, "vorn", 2.6, anchor="middle", color=GREY)
    fl, fr = P(legs[0]["foot"]), P(legs[1]["foot"])
    pg.dim(fl, fr, -9.5, f"{fmt(FOOT_DX)} (Tellermitte)")
    br = P(legs[2]["foot"])
    pg.dim(fr, br, -12, fmt(FOOT_DY))
    pg.text(fr[0] + 9, fr[1] + 3.5, f"Teller Ø {fmt(2 * M.PAD_R)} –", 2.3, color=BRASS_DARK)
    pg.text(fr[0] + 9, fr[1] + 6.5, "Kreise als Schneidvorlage", 2.3, color=BRASS_DARK)

    base = 234                                   # Bodenlinie der Detailansichten

    # ⑦ Seitenansicht eines Beins
    ox = 32
    R = lambda p: (ox + radial(p)[0], base - radial(p)[1])
    pg.heading(14, 162, 7, "Bein von der Seite", "in Beinrichtung, Käfig links")
    pg.line(ox - 6, base, ox + 42, base, w=0.25, color=GREY)
    pg.line(ox, base - M.CAGE_Z0, ox, base - M.CAGE_Z0 - 26, w=M.ROD, color=LIGHT)
    pg.line(ox, base - M.CAGE_Z0, ox - 5, base - M.CAGE_Z0, w=M.ROD, color=LIGHT)
    pg.text(ox, base - M.CAGE_Z0 - 27.5, "Käfigkante", 2.1, anchor="middle", color=GREY)
    pg.rod([R(LEG["hi"]), R(LEG["k1"]), R(LEG["foot"])])
    pg.rod([R(LEG["lo"]), R(LEG["strut"])])
    fx, fy = R(LEG["foot"])
    pg.rod([(fx, fy), (fx, base - 0.5)])
    pg.rect(fx - M.PAD_R, base - 0.6, 2 * M.PAD_R, 0.6, w=0.15, color=BRASS_DARK, fill=BRASS)
    for k in ("hi", "lo", "k1", "strut", "foot"):
        pg.joint(*R(LEG[k]))
    pg.dim((ox, base), (ox, R(LEG["hi"])[1]), 13)
    pg.dim((ox, base), (ox, base - M.CAGE_Z0), 6.5)
    pg.dim((ox, base), (fx, base), -7, fmt(radial(LEG["foot"])[0]))
    pg.dim((fx, base), (fx, fy), 9)
    pg.text(R(LEG["k1"])[0] + 1.5, R(LEG["k1"])[1] - 1.5, "Knie", 2.2, color=GREY)
    pg.text(R(LEG["strut"])[0] + 1.8, R(LEG["strut"])[1] + 0.8, "Strebe", 2.2, color=GREY)

    # ⑧ Holm, Biegeschablone in wahrer Größe
    hx, hy = 102, base - 48
    u = (radial(LEG["foot"])[0] - radial(LEG["hi"])[0], -(radial(LEG["foot"])[1] - radial(LEG["hi"])[1]))
    ul = math.hypot(*u)
    u = (u[0] / ul, u[1] / ul)
    n = (u[1], -u[0])
    xa = (HOLM_A ** 2 + HOLM_C ** 2 - HOLM_B ** 2) / (2 * HOLM_C)
    ha = math.sqrt(HOLM_A ** 2 - xa ** 2)
    hi = (hx, hy)
    knee = (hx + u[0] * xa + n[0] * ha, hy + u[1] * xa + n[1] * ha)
    foot = (hx + u[0] * HOLM_C, hy + u[1] * HOLM_C)
    pg.heading(80, 162, 8, "Holm – Biegeschablone", "wahre Größe · 8 Stück, je Bein 2")
    pg.line(hi[0], hi[1], foot[0], foot[1], w=0.15, color=LIGHT, dash=(1, 0.8))
    pg.rod([hi, knee, foot])
    pg.joint(*hi)
    pg.joint(*foot)
    pg.circle(knee[0], knee[1], 1.6, w=0.25, color=RED)
    pg.text(knee[0] + 2.5, knee[1] - 0.6, f"hier um {fmt(180 - KNEE_INNER)}° biegen", 2.4, True, color=RED)
    pg.dim(hi, knee, 3.5)
    pg.dim(knee, foot, -3.5)
    pg.text(hi[0] - 1.5, hi[1] - 1.5, "oben (Käfig)", 2.2, anchor="end", color=GREY)
    pg.text(foot[0] + 2, foot[1] + 1, "Fuß", 2.2, color=GREY)

    # ⑨ Bein von außen
    ox = 170
    S = lambda p: (ox + lateral(p)[0] * 1.0, base - lateral(p)[1])
    pg.heading(146, 162, 9, "Bein von außen", "Blick auf die Käfigecke")
    pg.line(ox - 12, base, ox + 12, base, w=0.25, color=GREY)
    for k in ("k1", "k2"):
        pg.rod([S(LEG["hi"]), S(LEG[k]), S(LEG["foot"])])
    pg.rod([S(LEG["k1"]), S(LEG["k2"])])
    pg.rod([S(LEG["m1"]), S(LEG["m2"])])
    fx, fy = S(LEG["foot"])
    pg.rod([(fx, fy), (fx, base - 0.5)])
    pg.rect(fx - M.PAD_R, base - 0.6, 2 * M.PAD_R, 0.6, w=0.15, color=BRASS_DARK, fill=BRASS)
    for k in ("hi", "k1", "k2", "m1", "m2", "foot"):
        pg.joint(*S(LEG[k]))
    for key, lines in (("k1", (f"Querstab Knie {fmt(BAR_K)}",)),
                       ("m1", (f"Querstab Mitte {fmt(BAR_M)}", "Strebe endet hier mittig"))):
        x, y = S(LEG[key])
        pg.line(x + 1, y, ox + 7, y, w=0.12, color=GREY)
        for j, ln in enumerate(lines):
            pg.text(ox + 8, y + 0.8 + j * 2.9, ln, 2.1, color=GREY)

    # ⑩ Längenlehren und Ablauf
    y = 246
    pg.heading(14, y, 10, "Längenlehren Bein", None)
    gauge(pg, 16, y + 6, STRUT, "Strebe", 4)
    gauge(pg, 16, y + 12, BAR_K, "Querstab Knie", 4)
    gauge(pg, 16, y + 18, BAR_M, "Querstab Mitte", 4)
    gauge(pg, 16, y + 24, STUB, "Stummel", 4)
    steps = ["Ablauf je Bein:",
             "1  Zwei Holme nach ⑧ biegen, auf ⑦ legen.",
             "2  Holme oben und unten verlöten,",
             "    Querstäbe Knie und Mitte einsetzen (⑨).",
             "3  Bein an der Käfigkante anlöten,",
             "    Strebe von der unteren Ecke ergänzen.",
             "4  Alle vier Beine, dann Fähre auf ⑥ stellen",
             "    und erst zuletzt Stummel und Teller löten."]
    for i, s in enumerate(steps):
        pg.text(100, y - 2 + i * 3.7, s.replace("⑥", "6").replace("⑦", "7").replace("⑧", "8").replace("⑨", "9"),
                2.4, i == 0)
    return pg


def main():
    pages = [sheet1(), sheet2()]
    titles = ["Bauzeichnung MeteoLander, Blatt 1: Käfig 1:1", "Bauzeichnung MeteoLander, Blatt 2: Landebeine 1:1"]
    for i, (pg, title) in enumerate(zip(pages, titles), 1):
        with open(os.path.join(ASSETS, f"build-drawing-{i}.svg"), "w", encoding="utf-8") as f:
            f.write(svg_page(pg, title))
    write_pdf(pages, os.path.join(ASSETS, "build-drawing.pdf"))
    print("assets/build-drawing.pdf, assets/build-drawing-1.svg und assets/build-drawing-2.svg geschrieben")


if __name__ == "__main__":
    main()
