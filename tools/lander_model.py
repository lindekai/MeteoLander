#!/usr/bin/env python3
"""MeteoLander – 3D-Drahtmodell und SVG-Renderer.

Erzeugt aus einem einfachen Modell (Maße in mm) die Grafiken in assets/:
  - assembly-sketch.svg  Aufbauskizze mit nummerierten Bauteilen
  - views.svg            Ansichten von vorn, rechts, hinten, links und oben
  - hero.svg             Titelbild für das README

Die Maße sind Annahmen, bis die Platinen ausgemessen sind (M0). Sie stehen
gesammelt im Abschnitt MASSE und werden dann dort korrigiert.

Aufruf:  python3 tools/lander_model.py
"""

import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")

# ---------------------------------------------------------------- MASSE (mm)
CAGE_W, CAGE_D = 42.0, 48.0          # Käfig: Breite (x), Tiefe (y)
CAGE_Z0, CAGE_Z1 = 30.0, 100.0       # Käfig: Unter-/Oberkante
TFT_W, TFT_H = 35.0, 58.0            # rotes TFT-Modul, Platine (Foto, ca.)
TFT_Z0 = 36.0
TFT_HOLE_DX, TFT_HOLE_DZ = 28.0, 52.0  # Bohrungsabstand TFT, Mitte zu Mitte (gemessen)
SCREEN_W, SCREEN_H = 28.0, 35.0      # aktive Fläche 1,8"
ESP_W, ESP_H = 25.6, 34.2            # AZ-Delivery D1 mini
BAT_W, BAT_T, BAT_H = 34.0, 10.0, 57.0  # LiPo LP103454 inkl. Schutzplatine
LEG_SPREAD = 30.0                    # Abstand Fuß zu Käfigecke (horizontal)
PAD_R = 7.0                          # Landeteller
ROD = 1.0                            # Messingdraht 1,0 mm
BTN_BAR_Y = 6.0                      # Querstab für den Taster, Abstand zur Vorderkante
MAST_H = 26.0                        # Mast über dem Deckrahmen
TRAY_W, TRAY_D, TRAY_T = 36.0, 14.0, 1.6  # Akkuwanne aus Lochraster
TRAY_ROD_Y = CAGE_D - 13.0           # Querdraht im Bodenrahmen, trägt die Wanne vorn
BAND_DZ = 25.0                       # Akku-Band über dem Bodenrahmen (zwischen Lademodul und Lochraster)

# ---------------------------------------------------------------- Farben
BRASS = (201, 160, 51)
BRASS_LIGHT = (243, 214, 122)
BRASS_DARK = (122, 92, 26)


def rgb(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in c)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ---------------------------------------------------------------- Vektoren
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def lerp(a, b, t): return add(a, mul(sub(b, a), t))
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    l = math.sqrt(dot(a, a)) or 1.0
    return mul(a, 1.0 / l)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


# ---------------------------------------------------------------- Kamera
class Camera:
    """Orthografische Kamera: Blick von vorn (-y) und schräg oben."""

    def __init__(self, az_deg, el_deg, scale, ox, oy):
        self.az = math.radians(az_deg)
        self.el = math.radians(el_deg)
        self.s, self.ox, self.oy = scale, ox, oy
        ca, sa = math.cos(self.az), math.sin(self.az)
        ce, se = math.cos(self.el), math.sin(self.el)
        self.view = (0.0, ce, -se)
        self._m = (ca, sa, ce, se)

    def rot(self, p):
        ca, sa, ce, se = self._m
        x1 = p[0] * ca - p[1] * sa
        y1 = p[0] * sa + p[1] * ca
        return (x1, y1, p[2])

    def proj(self, p):
        ca, sa, ce, se = self._m
        x1, y1, z1 = self.rot(p)
        sx = self.ox + x1 * self.s
        sy = self.oy - (y1 * se + z1 * ce) * self.s
        depth = y1 * ce - z1 * se
        return sx, sy, depth

    def ybias(self, mm):
        """Tiefenversatz, als läge ein Teil mm weiter hinten (+y) – passt für jede Blickrichtung."""
        return mm * self.rot((0.0, 1.0, 0.0))[1] * math.cos(self.el)

    def facing(self, n):
        return dot(self.rot(n), self.view) < 0

    def affine(self, origin, ux, uy):
        """SVG-Matrix, die lokale Koordinaten (u, v) auf die Fläche origin + u*ux + v*uy abbildet."""
        o = self.proj(origin)
        a = self.proj(add(origin, ux))
        b = self.proj(add(origin, uy))
        return "matrix(%.5f %.5f %.5f %.5f %.3f %.3f)" % (
            a[0] - o[0], a[1] - o[1], b[0] - o[0], b[1] - o[1], o[0], o[1])


LIGHT = norm((-0.5, -0.8, 0.9))


# ---------------------------------------------------------------- Szene
class Scene:
    def __init__(self, cam):
        self.cam = cam
        self.items = []          # (depth, svg)
        self.depth_range = [1e9, -1e9]
        self.anchors = {}

    def _track(self, d):
        self.depth_range[0] = min(self.depth_range[0], d)
        self.depth_range[1] = max(self.depth_range[1], d)

    # Draht in kurzen Stücken, damit die Tiefensortierung stimmt
    def rod(self, a, b, width=ROD, color=None, step=2.0):
        n = max(1, int(math.dist(a, b) / step))
        for i in range(n):
            p, q = lerp(a, b, i / n), lerp(a, b, (i + 1) / n)
            pa, pb = self.cam.proj(p), self.cam.proj(q)
            d = (pa[2] + pb[2]) / 2
            self._track(d)
            self.items.append((d, ("rod", pa, pb, width, color)))

    def polyline(self, pts, **kw):
        for a, b in zip(pts, pts[1:]):
            self.rod(a, b, **kw)

    def joint(self, p, r=0.75):
        sp = self.cam.proj(p)
        self.items.append((sp[2] - 0.6, ("joint", sp, r)))

    def face(self, pts, fill, normal, extra="", stroke=None, bias=0.0):
        if not self.cam.facing(normal):
            return
        sp = [self.cam.proj(p) for p in pts]
        d = sum(p[2] for p in sp) / len(sp) + bias
        shade = 0.62 + 0.38 * max(0.0, dot(norm(normal), LIGHT))
        col = rgb(mul(hexrgb(fill), shade))
        st = stroke or rgb(mul(hexrgb(fill), shade * 0.7))
        path = "M" + " L".join("%.2f %.2f" % (p[0], p[1]) for p in sp) + " Z"
        self.items.append((d, ("svg", '<path d="%s" fill="%s" stroke="%s" stroke-width="0.6" stroke-linejoin="round"/>%s'
                                % (path, col, st, extra))))

    def box(self, lo, hi, fill, faces_extra=None, bias=0.0):
        x0, y0, z0 = lo
        x1, y1, z1 = hi
        F = {
            "front": ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0)),
            "back": ([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], (0, 1, 0)),
            "left": ([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], (-1, 0, 0)),
            "right": ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0)),
            "top": ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)),
            "bottom": ([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], (0, 0, -1)),
        }
        for name, (pts, n) in F.items():
            ex = (faces_extra or {}).get(name, "")
            self.face(pts, fill, n, extra=ex, bias=bias)

    def cylinder(self, c, r, h, fill, top_fill, seg=36):
        x, y, z = c
        ring0 = [(x + r * math.cos(2 * math.pi * i / seg), y + r * math.sin(2 * math.pi * i / seg), z) for i in range(seg)]
        ring1 = [(p[0], p[1], z + h) for p in ring0]
        for i in range(seg):
            j = (i + 1) % seg
            a = 2 * math.pi * (i + 0.5) / seg
            n = (math.cos(a), math.sin(a), 0)
            self.face([ring0[i], ring0[j], ring1[j], ring1[i]], fill, n, stroke="none")
        self.face(ring1, top_fill, (0, 0, 1))

    def disc(self, c, r, fill, thick=0.5, seg=48):
        x, y, z = c
        ring = [(x + r * math.cos(2 * math.pi * i / seg), y + r * math.sin(2 * math.pi * i / seg), z + thick) for i in range(seg)]
        sp = [self.cam.proj(p) for p in ring]
        d = self.cam.proj(c)[2] + 4  # Teller liegen unter allem anderen am Fuß
        path = "M" + " L".join("%.2f %.2f" % (p[0], p[1]) for p in sp) + " Z"
        self.items.append((d, ("svg",
            '<path d="%s" fill="url(#padGrad)" stroke="%s" stroke-width="1"/>' % (path, rgb(BRASS_DARK)))))

    def overlay(self, origin, ux, uy, svg, depth_of, bias=-0.05):
        """Flacher Inhalt (Bildschirm, Aufdruck) auf einer Fläche; von hinten unsichtbar."""
        if not self.cam.facing(mul(cross(ux, uy), -1.0)):
            return
        d = self.cam.proj(depth_of)[2] + bias
        self.items.append((d, ("svg", '<g transform="%s">%s</g>' % (self.cam.affine(origin, ux, uy), svg))))

    def anchor(self, key, p):
        self.anchors[key] = self.cam.proj(p)

    def render(self):
        lo, hi = self.depth_range
        span = (hi - lo) or 1
        out = []
        for d, it in sorted(self.items, key=lambda t: -t[0]):
            kind = it[0]
            if kind == "rod":
                _, pa, pb, w, color = it
                t = (d - lo) / span                      # 0 = vorn, 1 = hinten
                base = hexrgb(color) if color else mix(BRASS, BRASS_DARK, t * 0.75)
                light = mix(base, BRASS_LIGHT if not color else (255, 220, 190), 0.55)
                px = w * self.cam.s
                out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f" stroke-linecap="round"/>'
                           % (pa[0], pa[1], pb[0], pb[1], rgb(base), px))
                if not color:
                    out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-opacity="0.8"/>'
                               % (pa[0] - px * 0.18, pa[1] - px * 0.18, pb[0] - px * 0.18, pb[1] - px * 0.18, rgb(light), px * 0.32))
            elif kind == "joint":
                _, sp, r = it
                out.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="url(#solder)"/>' % (sp[0], sp[1], r * self.cam.s))
            else:
                out.append(it[1])
        return "\n".join(out)


# ---------------------------------------------------------------- Inhalte
def screen_svg():
    """Bildschirminhalt in Displaypixeln (128 × 160), wie im Layoutentwurf."""
    mono = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
    return f'''
<rect width="128" height="160" fill="#05070c"/>
<g font-family="{mono}">
<text x="4" y="10" fill="#c9d1d9" font-size="10" textLength="48" lengthAdjust="spacingAndGlyphs">Saarmund</text>
<text x="94" y="10" fill="#c9d1d9" font-size="10" textLength="30" lengthAdjust="spacingAndGlyphs">14:30</text>
<rect x="4" y="14" width="120" height="1" fill="#2a3340"/>
<circle cx="30" cy="36" r="9" fill="#ffd23f"/>
<path d="M18 54h26a7 7 0 0 0 0-14a9 9 0 0 0-17-2a7 7 0 0 0-9 16z" fill="#dfe6ee"/>
<text x="62" y="58" fill="#ffffff" font-size="40" font-weight="700" textLength="48" lengthAdjust="spacingAndGlyphs">7°</text>
<text x="22" y="76" fill="#5ce1ff" font-size="10" textLength="84" lengthAdjust="spacingAndGlyphs">Leicht bewölkt</text>
<rect x="4" y="84" width="120" height="1" fill="#2a3340"/>
<text x="4" y="102" fill="#8b949e" font-size="10" textLength="30" lengthAdjust="spacingAndGlyphs">Innen</text>
<text x="70" y="104" fill="#ffffff" font-size="20" textLength="48" lengthAdjust="spacingAndGlyphs">21,4</text>
<text x="4" y="126" fill="#8b949e" font-size="10" textLength="42" lengthAdjust="spacingAndGlyphs">Feuchte</text>
<text x="76" y="128" fill="#ffffff" font-size="20" textLength="24" lengthAdjust="spacingAndGlyphs">81</text>
<text x="104" y="128" fill="#8b949e" font-size="10" textLength="6" lengthAdjust="spacingAndGlyphs">%</text>
<rect x="4" y="142" width="120" height="1" fill="#2a3340"/>
<circle cx="8" cy="152" r="2.5" fill="#3fb950"/>
<text x="14" y="155" fill="#6e7681" font-size="10" textLength="66" lengthAdjust="spacingAndGlyphs">Stand 14:15</text>
<rect x="104" y="148" width="18" height="8" rx="1" fill="none" stroke="#8b949e" stroke-width="1"/>
<rect x="106" y="150" width="10" height="4" fill="#3fb950"/>
</g>
<rect width="128" height="160" fill="url(#glare)"/>'''


def tft_print_svg():
    """Aufdruck auf der roten Platine (lokale Einheiten = mm)."""
    sans = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
    pins = ["VCC", "GND", "CS", "RESET", "A0", "SDA", "SCK", "LED"]
    s = [f'<text x="{TFT_W / 2}" y="3.6" font-family="{sans}" font-size="2.2" fill="#ffe7e7" text-anchor="middle" opacity="0.9">1.8 TFT SPI 128*160 V1.2</text>']
    pitch = 2.54
    x0 = TFT_W / 2 - pitch * 3.5
    for i, name in enumerate(pins):
        x = x0 + i * pitch
        s.append(f'<rect x="{x - 0.75:.2f}" y="{TFT_H - 3.1:.2f}" width="1.5" height="1.5" fill="#e6c25a"/>')
        s.append(f'<text x="{x:.2f}" y="{TFT_H - 4.0:.2f}" font-family="{sans}" font-size="1.05" fill="#ffe7e7" text-anchor="middle" opacity="0.85">{name}</text>')
    return "".join(s)


DEFS = '''
<defs>
  <radialGradient id="padGrad" cx="0.4" cy="0.35" r="0.8">
    <stop offset="0" stop-color="#f6dc8c"/><stop offset="0.6" stop-color="#c9a033"/><stop offset="1" stop-color="#8a6a1f"/>
  </radialGradient>
  <radialGradient id="solder" cx="0.35" cy="0.35" r="0.7">
    <stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#cfd3d8"/><stop offset="1" stop-color="#7d838b"/>
  </radialGradient>
  <linearGradient id="glare" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0.10"/><stop offset="0.45" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
  <filter id="softer" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
    <stop offset="0" stop-color="#d4a73a" stop-opacity="0.20"/><stop offset="1" stop-color="#d4a73a" stop-opacity="0"/>
  </radialGradient>
</defs>'''


# ---------------------------------------------------------------- Modell
LEG_HI = 18.0          # Bein setzt so weit über der Käfigunterkante an
LEG_KNEE_R = 0.72      # Knie bei diesem Anteil der Spreizung …
LEG_KNEE_Z = 9.0       # … und so hoch über der Käfigunterkante
LEG_FOOT_Z = 4.0       # Fußpunkt über dem Boden (darunter der Stummel zum Teller)
LEG_HALF_W = 2.6       # halber Abstand der beiden Holme am Knie


def leg_points(cx, cy):
    """Punkte eines Landebeins an der Käfigecke (cx, cy); gemeinsam für Modell und Bauzeichnung."""
    z0 = CAGE_Z0
    d = norm((cx, cy - CAGE_D / 2, 0))
    perp = (-d[1], d[0], 0)
    knee = add((cx, cy, z0 + LEG_KNEE_Z), mul(d, LEG_SPREAD * LEG_KNEE_R))
    foot = add((cx, cy, LEG_FOOT_Z), mul(d, LEG_SPREAD))
    k1, k2 = add(knee, mul(perp, LEG_HALF_W)), add(knee, mul(perp, -LEG_HALF_W))
    m1, m2 = lerp(k1, foot, 0.5), lerp(k2, foot, 0.5)
    return {"d": d, "perp": perp, "hi": (cx, cy, z0 + LEG_HI), "lo": (cx, cy, z0), "knee": knee,
            "foot": foot, "k1": k1, "k2": k2, "m1": m1, "m2": m2, "strut": lerp(m1, m2, 0.5)}


def build(scene):
    S = scene
    x0, x1 = -CAGE_W / 2, CAGE_W / 2
    y0, y1 = 0.0, CAGE_D
    z0, z1 = CAGE_Z0, CAGE_Z1
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

    # Schatten am Boden
    for cx, cy in corners:
        pass

    # --- Käfig: 12 Kanten
    for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
        S.rod((ax, ay, z0), (bx, by, z0))
        S.rod((ax, ay, z1), (bx, by, z1))
    for cx, cy in corners:
        S.rod((cx, cy, z0), (cx, cy, z1))
        S.joint((cx, cy, z0)); S.joint((cx, cy, z1))
    # Querdraht im Bodenrahmen für die Akkuwanne
    S.rod((x0, TRAY_ROD_Y, z0), (x1, TRAY_ROD_Y, z0))
    S.joint((x0, TRAY_ROD_Y, z0)); S.joint((x1, TRAY_ROD_Y, z0))
    # Querstab oben für den Taster, Mittelring
    S.rod((x0, BTN_BAR_Y, z1), (x1, BTN_BAR_Y, z1))
    S.joint((x0, BTN_BAR_Y, z1)); S.joint((x1, BTN_BAR_Y, z1))

    # --- Beine (Fähre): Oberarm, Knie, Unterschenkel, Strebe, Teller
    for cx, cy in corners:
        L = leg_points(cx, cy)
        hi, lo, knee, foot, k1, k2, m1, m2 = (L[k] for k in ("hi", "lo", "knee", "foot", "k1", "k2", "m1", "m2"))
        S.disc((foot[0], foot[1], 0.0), PAD_R, "#c9a033")
        S.rod(hi, k1); S.rod(hi, k2)
        S.rod(k1, foot); S.rod(k2, foot)
        S.rod(k1, k2)
        S.rod(m1, m2)
        S.rod(lo, L["strut"])
        S.rod(foot, (foot[0], foot[1], 0.5))
        for p in (hi, k1, k2, foot, (foot[0], foot[1], 0.5)):
            S.joint(p, 0.65)
        if (cx, cy) == (x1, y0):
            S.anchor("leg", lerp(knee, foot, 0.3))
            S.anchor("pad", (foot[0] + PAD_R * 0.7, foot[1], 0.3))

    # --- TFT-Modul an der Vorderseite
    tx0, tx1 = -TFT_W / 2, TFT_W / 2
    tz0, tz1 = TFT_Z0, TFT_Z0 + TFT_H
    S.box((tx0, 1.2, tz0), (tx1, 2.8, tz1), "#c0262d")
    # Display-Glas mit Rahmen
    gx, gz0, gz1 = 15.5, tz0 + 8.0, tz0 + 8.0 + 42.0
    S.box((-gx, -0.6, gz0), (gx, 1.2, gz1), "#111318", bias=-0.2)
    sx0 = -SCREEN_W / 2
    sz_top = gz1 - 3.5
    S.overlay((sx0, -0.61, sz_top), (SCREEN_W / 128, 0, 0), (0, 0, -SCREEN_H / 160), screen_svg(), (0, -0.6, (gz0 + gz1) / 2), bias=-1.0)
    S.overlay((tx0, 1.19, tz1), (1, 0, 0), (0, 0, -1), tft_print_svg(), (0, 1.2, tz1 - 2), bias=-0.3)
    # Befestigung an den vier Bohrungen
    for hx in (-TFT_HOLE_DX / 2, TFT_HOLE_DX / 2):
        for hz in (tz0 + TFT_H / 2 - TFT_HOLE_DZ / 2, tz0 + TFT_H / 2 + TFT_HOLE_DZ / 2):
            S.joint((hx, 1.0, hz), 0.9)
            cxs = x0 if hx < 0 else x1
            S.rod((hx, 1.0, hz), (cxs, 0.0, hz), width=0.7)
    S.anchor("tft", (tx0 + 4, 0, tz1 - 4))

    # --- ESP8266 hinter dem Display (Platine senkrecht)
    ex0, ex1 = -ESP_W / 2, ESP_W / 2
    ez0, ez1 = 48.0, 48.0 + ESP_H                                           # USB unten, Antenne oben
    S.box((ex0, 14.0, ez0), (ex1, 15.6, ez1), "#1d4a92")
    S.box((-7.5, 15.6, ez1 - 22), (7.5, 18.0, ez1 - 7), "#b7bec8")           # ESP-12F-Abschirmung
    for i in range(8):
        z = ez0 + 9.1 + i * 2.54
        for ex in (ex0 + 1.3, ex1 - 1.3):
            S.box((ex - 1.1, 11.0, z - 1.1), (ex + 1.1, 14.0, z + 1.1), "#1b1f24")
    S.anchor("esp", (ex1, 15.6, ez0 + 24))

    # --- Akku: steht auf der Lochraster-Wanne, ein Drahtband hält ihn
    tz = z0 + ROD / 2
    S.box((-TRAY_W / 2, CAGE_D - TRAY_D, tz), (TRAY_W / 2, CAGE_D, tz + TRAY_T), "#3f8f4f")
    bz = tz + TRAY_T                                                        # Unterkante Akku
    by0 = CAGE_D - TRAY_D / 2 - BAT_T / 2                                   # mittig auf der Wanne
    S.box((-BAT_W / 2, by0, bz), (BAT_W / 2, by0 + BAT_T, bz + BAT_H - 4), "#c7cdd4")
    S.box((-BAT_W / 2, by0, bz + BAT_H - 4), (BAT_W / 2, by0 + BAT_T, bz + BAT_H), "#d9a62e")  # Schutzplatine
    S.anchor("bat", (BAT_W / 2 - 6, by0, bz + BAT_H - 10))
    zb = z0 + BAND_DZ
    band = [(x0, TRAY_ROD_Y, zb), (x1, TRAY_ROD_Y, zb), (x1, CAGE_D, zb), (x0, CAGE_D, zb)]
    for a, b in zip(band, band[1:] + band[:1]):
        S.rod(a, b)
    for y in (TRAY_ROD_Y, CAGE_D):                                         # Schrumpfschlauch am Akku
        S.rod((-BAT_W / 2 - 1, y, zb), (BAT_W / 2 + 1, y, zb), width=1.5, color="#30363d")
    S.joint((x0, CAGE_D, zb)); S.joint((x1, CAGE_D, zb))

    # --- Lademodul an der rechten Seite unten, LEDs außen
    S.box((x1 - 2.2, 25.0, 36.0), (x1 - 0.6, 45.0, 52.0), "#1d4a92")           # HW-168, 20 x 16 mm
    S.box((x1 - 4.4, 42.0, 40.0), (x1 - 2.2, 48.2, 48.0), "#b7bec8")           # Mini-USB nach hinten
    S.box((x1 - 0.6, 27.0, 46.0), (x1 + 0.6, 29.0, 47.6), "#ff4d4f")
    S.box((x1 - 0.6, 31.0, 46.0), (x1 + 0.6, 33.0, 47.6), "#3fb950")
    S.box((x1 - 0.6, 33.0, 38.0), (x1 + 1.0, 38.0, 43.0), "#1b1f24")
    S.anchor("chg", (x1 + 0.6, 30.0, 47.6))

    # --- Lochrasterplatine rechts oben: Selbsthaltung, LDO, Teiler
    S.box((x1 - 2.2, 16.0, 58.0), (x1 - 0.6, 44.0, 90.0), "#1a7f37")
    S.box((x1 - 0.6, 20.0, 80.0), (x1 + 3.0, 24.6, 84.0), "#1b1f24")          # Q2 TO-92
    S.box((x1 - 0.6, 30.0, 80.0), (x1 + 2.0, 36.0, 86.0), "#1b1f24")          # LDO
    S.box((x1 - 0.6, 37.0, 70.0), (x1 + 1.2, 40.0, 73.0), "#1b1f24")          # Q1
    for i, z in enumerate((64.0, 68.0, 72.0)):
        S.box((x1 - 0.6, 20.0, z), (x1 + 1.6, 28.0, z + 1.8), "#d9c39a")      # Widerstände
    S.box((x1 - 0.6, 30.0, 62.0), (x1 + 1.4, 36.0, 64.0), "#c84b31")          # Diode
    S.anchor("perf", (x1 + 2.0, 20.0, 88.0))

    # --- Kupferlackdraht: Verbindungen
    cu = "#c8743a"
    S.polyline([(x1 - 0.6, 30, 52), (x1 - 0.2, 30, 55), (x1 - 0.6, 30, 58)], width=0.35, color=cu)
    S.polyline([(x1 - 0.6, 26, 90), (x1 - 2, 26, 94), (ex1 - 1.3, 15, 94), (ex1 - 1.3, 13, ez1)], width=0.35, color=cu)
    S.polyline([(x1 - 0.6, 40, 90), (x1 - 3, 40, 96), (ex1 - 1.3, 16, 96), (ex1 - 1.3, 12.5, ez1 - 2)], width=0.35, color=cu)

    # --- Taster oben vorn
    S.box((-3.0, 3.0, z1 + 0.4), (3.0, 9.0, z1 + 3.8), "#2d333b")
    S.cylinder((0.0, 6.0, z1 + 3.8), 1.8, 1.6, "#e6c25a", "#f3d67a", seg=20)
    S.anchor("btn", (0.0, 6.0, z1 + 5.4))

    # --- BME280 auf dem Mast
    mast_top = z1 + MAST_H
    S.rod((0, CAGE_D / 2, z1), (0, CAGE_D / 2, mast_top))
    S.rod((x0, CAGE_D / 2, z1), (x1, CAGE_D / 2, z1))
    S.joint((0, CAGE_D / 2, z1)); S.joint((x0, CAGE_D / 2, z1)); S.joint((x1, CAGE_D / 2, z1))
    S.box((-6.5, CAGE_D / 2 - 0.8, mast_top - 2), (6.5, CAGE_D / 2 + 0.8, mast_top + 8.5), "#7b3fb5")
    S.box((-1.4, CAGE_D / 2 - 1.6, mast_top + 2.6), (1.4, CAGE_D / 2 - 0.8, mast_top + 5.4), "#c7cdd4")
    S.polyline([(0.9, CAGE_D / 2 - 0.9, mast_top - 2), (0.9, CAGE_D / 2 - 0.9, z1 + 4), (6, 18, z1 - 4)], width=0.35, color=cu)
    S.anchor("bme", (6.5, CAGE_D / 2, mast_top + 6))
    S.anchor("cage", (x0, 0, z1 - 20))

    return S


def floor_shadow(cam):
    pts = []
    r = LEG_SPREAD + CAGE_W * 0.55
    for i in range(48):
        a = 2 * math.pi * i / 48
        pts.append(cam.proj((r * math.cos(a), CAGE_D / 2 + r * math.sin(a) * 1.05, 0)))
    path = "M" + " L".join("%.1f %.1f" % (p[0], p[1]) for p in pts) + " Z"
    return '<path d="%s" fill="#000000" fill-opacity="0.38" filter="url(#soft)"/>' % path


# ---------------------------------------------------------------- Ausgaben
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

LEGEND = [
    ("tft", "TFT-Modul 1,8″ (rot)", ["Vorderseite der Fähre, an den vier", "Bohrungen am Käfig verlötet."]),
    ("cage", "Käfig aus Messingdraht", ["Tragende Struktur und zugleich GND."]),
    ("leg", "Vier Landebeine", ["Oberarm, Knie, Unterschenkel und Strebe;", "Teller zuletzt anlöten, sonst wackelt es."]),
    ("pad", "Landeteller", ["Messingscheiben Ø 14 mm."]),
    ("esp", "D1 mini (ESP8266)", ["Senkrecht hinter dem Display;", "WLAN-Antenne oben frei lassen."]),
    ("bat", "LiPo-Akku 2000 mAh", ["Steht in einer Lochraster-Wanne;", "ein Drahtband mit Schrumpfschlauch hält ihn."]),
    ("chg", "Lademodul", ["HW-168, rechte Seite, LEDs nach außen,", "Mini-USB-Buchse nach hinten."]),
    ("perf", "Lochrasterplatine", ["Selbsthaltung, LDO und Spannungsteiler."]),
    ("btn", "Taster", ["Oben vorn – Druck von oben", "belastet die Beine, nichts kippt."]),
    ("bme", "BME280 auf dem Mast", ["Misst direkt nach dem Einschalten,", "bevor sich die Elektronik erwärmt."]),
]

CALLOUT_OFFSET = {
    "tft": (-80, -30), "cage": (-70, 0), "leg": (70, 10), "pad": (70, -20), "esp": (150, 20),
    "bat": (-120, -50), "chg": (110, 20), "perf": (110, -30), "btn": (-90, -30), "bme": (80, -10),
}


def assembly():
    W, H = 1280, 940
    cam = Camera(-34, 24, 5.0, 330, 800)
    sc = build(Scene(cam))
    body = sc.render()

    calls = []
    for i, (key, title, lines) in enumerate(LEGEND, 1):
        ax, ay, _ = sc.anchors[key]
        dx, dy = CALLOUT_OFFSET[key]
        nx, ny = ax + dx, ay + dy
        calls.append(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#e6c25a" stroke-width="1" stroke-opacity="0.7"/>')
        calls.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="2.4" fill="#e6c25a"/>')
        calls.append(f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="12" fill="#0b1530" stroke="#e6c25a" stroke-width="1.6"/>')
        calls.append(f'<text x="{nx:.1f}" y="{ny + 4:.1f}" font-family="{SANS}" font-size="12" font-weight="700" fill="#e6c25a" text-anchor="middle">{i}</text>')

    leg = []
    y = 150
    for i, (key, title, lines) in enumerate(LEGEND, 1):
        leg.append(f'<circle cx="890" cy="{y - 5}" r="11" fill="#0b1530" stroke="#e6c25a" stroke-width="1.6"/>')
        leg.append(f'<text x="890" y="{y - 1}" font-family="{SANS}" font-size="11.5" font-weight="700" fill="#e6c25a" text-anchor="middle">{i}</text>')
        leg.append(f'<text x="912" y="{y}" font-family="{SANS}" font-size="14.5" font-weight="700" fill="#ffffff">{title}</text>')
        for j, ln in enumerate(lines):
            leg.append(f'<text x="912" y="{y + 18 + j * 16}" font-family="{SANS}" font-size="12.5" fill="#8b949e">{ln}</text>')
        y += 30 + 16 * len(lines) + 12

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Aufbauskizze MeteoLander: Drahtkäfig als Landefähre mit vier Beinen, rotem TFT, ESP8266, Akku, Lademodul, Taster und BME280">
{DEFS}
<rect width="{W}" height="{H}" rx="18" fill="#0b1530"/>
<ellipse cx="400" cy="470" rx="380" ry="360" fill="url(#glow)"/>
<text x="44" y="56" font-family="{SANS}" font-size="24" font-weight="700" fill="#ffffff">Aufbauskizze</text>
<text x="44" y="82" font-family="{SANS}" font-size="14" fill="#8b949e">Landefähre aus 1-mm-Messingdraht · Maße sind Annahmen, bis die Platinen ausgemessen sind</text>
{floor_shadow(cam)}
{body}
{"".join(calls)}
<line x1="860" y1="112" x2="860" y2="{y - 20}" stroke="#2a3340"/>
{"".join(leg)}
<text x="44" y="{H - 28}" font-family="{SANS}" font-size="12" fill="#59636e">Gerendert aus tools/lander_model.py · Kupferlackdraht = Signalleitungen · Messing = GND</text>
</svg>
'''
    with open(os.path.join(ASSETS, "assembly-sketch.svg"), "w") as f:
        f.write(svg)


def hero():
    W, H = 1280, 480
    cam = Camera(-34, 20, 2.75, 900, 400)
    sc = build(Scene(cam))
    body = sc.render()
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="MeteoLander – Wetteranzeige als Landefähre aus Messingdraht mit rotem 1,8-Zoll-TFT (Konzeptillustration)">
{DEFS}
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1530"/><stop offset="1" stop-color="#070b16"/></linearGradient>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<g fill="#ffffff">
  <circle cx="620" cy="70" r="1.2" opacity="0.5"/><circle cx="700" cy="140" r="0.9" opacity="0.4"/><circle cx="1180" cy="90" r="1.1" opacity="0.5"/>
  <circle cx="1230" cy="260" r="0.8" opacity="0.35"/><circle cx="760" cy="300" r="1" opacity="0.3"/><circle cx="1110" cy="40" r="0.8" opacity="0.4"/>
  <circle cx="660" cy="220" r="0.7" opacity="0.35"/><circle cx="1250" cy="170" r="1.2" opacity="0.45"/>
</g>
<ellipse cx="960" cy="250" rx="280" ry="230" fill="url(#glow)"/>
<g font-family="{SANS}">
  <text x="80" y="128" fill="#d4a73a" font-size="17" font-weight="600" letter-spacing="3">ESP8266 · 1,8″ TFT · BME280 · OPEN-METEO</text>
  <text x="76" y="212" fill="#ffffff" font-size="80" font-weight="700" letter-spacing="-1">MeteoLander</text>
  <text x="80" y="264" fill="#c9d1d9" font-size="28">Das Wetter, gelandet auf deinem Schreibtisch</text>
  <text x="80" y="304" fill="#8b949e" font-size="20">Circuit Sculpture aus Messing · auf Knopfdruck · akkubetrieben</text>
  <g transform="translate(80 344)">
    <rect width="150" height="34" rx="17" fill="none" stroke="#d4a73a" stroke-opacity="0.7"/>
    <circle cx="20" cy="17" r="5" fill="#d4a73a"/>
    <text x="34" y="23" fill="#e6c25a" font-size="15" font-weight="600">Konzeptphase</text>
  </g>
</g>
{floor_shadow(cam)}
{body}
<text x="{W - 24}" y="{H - 16}" text-anchor="end" fill="#59636e" font-family="{SANS}" font-size="12">Konzeptillustration – Maße folgen nach dem Ausmessen der Teile</text>
</svg>
'''
    with open(os.path.join(ASSETS, "hero.svg"), "w") as f:
        f.write(svg)


VIEWS = [
    ("Vorn", 0, 12, "Display mit vier Bohrungen am Käfig, Taster oben vorn"),
    ("Rechts", -90, 12, "Lademodul unten mit Lade-LEDs, Lochrasterplatine darüber"),
    ("Hinten", 180, 12, "Akku in der Wanne, Drahtband, USB-Buchse des Lademoduls"),
    ("Links", 90, 12, "D1 mini hinter dem Display, Antenne oben frei"),
]


def centered(cam, p, at):
    """Verschiebt die Kamera so, dass der Modellpunkt p auf der Bildposition at landet."""
    sx, sy, _ = cam.proj(p)
    cam.ox, cam.oy = at[0] - sx, at[1] - sy
    return cam


def views():
    """Ansichtsblatt: vier Seitenansichten und Draufsicht aus demselben Modell."""
    W, H = 1640, 1060
    s = 2.6
    pw = W / 4
    panels = []
    for i, (title, az, el, note) in enumerate(VIEWS):
        cam = centered(Camera(az, el, s, 0, 0), (0, CAGE_D / 2, 0), (pw * i + pw / 2, 580))
        body = build(Scene(cam)).render()
        panels.append(f'''<g>
<rect x="{pw * i + 12}" y="104" width="{pw - 24}" height="520" rx="12" fill="#0f1b3a" stroke="#1f2b4a"/>
<text x="{pw * i + 32}" y="138" font-family="{SANS}" font-size="18" font-weight="700" fill="#ffffff">{title}</text>
<text x="{pw * i + 32}" y="160" font-family="{SANS}" font-size="12" fill="#8b949e">{note}</text>
{floor_shadow(cam)}
{body}
</g>''')
    # Draufsicht
    cam = centered(Camera(0, 90, 2.3, 0, 0), (0, CAGE_D / 2, 0), (pw, 835))
    body = build(Scene(cam)).render()
    panels.append(f'''<g>
<rect x="12" y="640" width="{pw * 2 - 24}" height="{H - 640 - 50}" rx="12" fill="#0f1b3a" stroke="#1f2b4a"/>
<text x="32" y="674" font-family="{SANS}" font-size="18" font-weight="700" fill="#ffffff">Oben</text>
<text x="32" y="696" font-family="{SANS}" font-size="12" fill="#8b949e">Vorn ist unten</text>
{body}
</g>''')
    notes = [
        ("Reihenfolge", "Käfig mit Wannen-Querdraht → Display → D1 mini → Wanne, Akku, Band → Lademodul und Lochraster → Beine → Teller"),
        ("Antenne", "Die WLAN-Antenne des D1 mini zeigt nach oben; kein Messing direkt davor oder darüber."),
        ("Akku", "Die Pouchzelle steht in einer Lochraster-Wanne; das Band hält sie mit Schrumpfschlauch, ohne zu klemmen."),
        ("Masse", "Das Messinggestell ist GND. Signale laufen als sichtbarer Kupferlackdraht."),
        ("Maße", "TFT, D1 mini und Akku nach Fotos mit Lineal; Käfig und Beine bleiben bis M4 Annahmen."),
    ]
    nt = [f'<text x="{pw * 2 + 32}" y="674" font-family="{SANS}" font-size="18" font-weight="700" fill="#ffffff">Worauf es beim Aufbau ankommt</text>']
    for j, (k, v) in enumerate(notes):
        y = 712 + j * 52
        nt.append(f'<text x="{pw * 2 + 32}" y="{y}" font-family="{SANS}" font-size="13.5" font-weight="700" fill="#e6c25a">{k}</text>')
        nt.append(f'<text x="{pw * 2 + 32}" y="{y + 20}" font-family="{SANS}" font-size="13" fill="#c9d1d9">{v}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Ansichten MeteoLander: Landefähre von vorn, rechts, hinten, links und oben">
{DEFS}
<rect width="{W}" height="{H}" rx="18" fill="#0b1530"/>
<text x="32" y="56" font-family="{SANS}" font-size="24" font-weight="700" fill="#ffffff">Ansichten von allen Seiten</text>
<text x="32" y="82" font-family="{SANS}" font-size="14" fill="#8b949e">Orthografische Ansichten aus demselben Modell wie die Aufbauskizze · Maßstab in allen Ansichten gleich</text>
{"".join(panels)}
<rect x="{pw * 2 + 12}" y="640" width="{pw * 2 - 24}" height="{H - 640 - 50}" rx="12" fill="#0f1b3a" stroke="#1f2b4a"/>
{"".join(nt)}
<text x="32" y="{H - 18}" font-family="{SANS}" font-size="12" fill="#59636e">Gerendert aus tools/lander_model.py · Kupferlackdraht = Signalleitungen · Messing = GND</text>
</svg>
'''
    with open(os.path.join(ASSETS, "views.svg"), "w") as f:
        f.write(svg)


if __name__ == "__main__":
    assembly()
    hero()
    views()
    print("assets/assembly-sketch.svg, assets/hero.svg und assets/views.svg geschrieben")
