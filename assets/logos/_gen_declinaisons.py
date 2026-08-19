#!/usr/bin/env python3
"""Déclinaisons Direction C — « Le Rythme Caché ».
Réutilise la géométrie exacte du mark original (direction-c-mark.svg).
Produit : favicon, lockup horizontal, app icon, logo sombre.
"""
import math, subprocess, os

OUT = os.path.dirname(os.path.abspath(__file__))

TEAL_50  = "#E1F5EE"
TEAL_100 = "#9FE1CB"
TEAL_400 = "#1D9E75"
TEAL_600 = "#0F6E56"
TEAL_800 = "#085041"
TEAL_900 = "#04342C"
STONE    = "#FAFAF7"
INK      = "#1a1a18"
WHITE    = "#FFFFFF"

# ---- helpers géométrie (identiques à _gen.py, mark original) ----
def _m(a, s): return (a[0] * s, a[1] * s)
def _va(a, b): return (a[0] + b[0], a[1] + b[1])
def _vs(a, b): return (a[0] - b[0], a[1] - b[1])

def _cr(a, b, c, d, t):
    t2, t3 = t * t, t * t * t
    return _m(_va(_m(b, 2), _va(_m(_vs(c, a), t), _va(
        _m(_va(_va(_m(a, 2), _m(b, -5)), _va(_m(c, 4), _m(d, -1))), t2),
        _m(_va(_va(_m(a, -1), _m(b, 3)), _va(_m(c, -3), _m(d, 1))), t3)))), 0.5)

def spline(pts, n=80):
    if len(pts) == 2:
        return [(pts[0][0] + (pts[1][0] - pts[0][0]) * i / n,
                 pts[0][1] + (pts[1][1] - pts[0][1]) * i / n) for i in range(n + 1)]
    first = pts[0]; out = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        c = pts[i + 2] if i + 2 < len(pts) else (2 * pts[i + 1][0] - pts[i][0],
                                                 2 * pts[i + 1][1] - pts[i][1])
        pm = pts[i - 1] if i >= 1 else (2 * pts[i][0] - first[0],
                                        2 * pts[i][1] - first[1])
        steps = n // (len(pts) - 1)
        for j in range(steps):
            out.append(_cr(pm, a, b, c, j / steps))
    out.append(pts[-1])
    return out

def taper(pts, w0, w1, n=80):
    s = spline(pts, n=n); L, R = [], []
    for i, (x, y) in enumerate(s):
        t = i / max(1, len(s) - 1); w = (w0 + (w1 - w0) * t) / 2.0
        if i + 1 < len(s):
            dx, dy = s[i + 1][0] - x, s[i + 1][1] - y
        else:
            dx, dy = x - s[i - 1][0], y - s[i - 1][1]
        ln = math.hypot(dx, dy) or 1; px, py = -dy / ln, dx / ln
        L.append((x + px * w, y + py * w)); R.append((x - px * w, y - py * w))
    R.reverse()
    return L + R + [s[0]]

def poly(s, fill):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in s)
    return f'<polygon points="{pts}" fill="{fill}"/>'

def circle(cx, cy, r, fill):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"/>'

# ---- géométrie des ondes (identique au mark original) ----
W_TOP = [(30, 142), (80, 106), (124, 142), (168, 104), (214, 140)]
W_MID = [(30, 118), (82, 92), (136, 150), (178, 100), (214, 120)]
W_BOT = [(30, 168), (84, 140), (128, 176), (172, 142), (214, 162)]
FOCUS = (82, 90)

def mark_inner(c_top=TEAL_400, c_mid=TEAL_800, c_bot=TEAL_600,
               halo=STONE, dot=TEAL_400):
    """Le mark complet (3 ondes + battement), couleurs paramétrables."""
    parts = []
    parts.append(poly(taper(W_TOP, 8, 3.5), c_top))
    parts.append(poly(taper(W_MID, 16, 7), c_mid))
    parts.append(poly(taper(W_BOT, 8, 3.5), c_bot))
    fx, fy = FOCUS
    parts.append(circle(fx, fy, 10.0, halo))
    parts.append(circle(fx, fy, 6.8, dot))
    return "".join(parts)

def wrap(mark_inner, vb="0 0 240 240", bg=None):
    rect = f'<rect width="240" height="240" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{rect}{mark_inner}</svg>'

# ============================================================
# 1. FAVICON — un seul geste épaissi + battement (robuste à 32px)
# ============================================================
def favicon_inner():
    parts = []
    # un seul geste : l'onde principale, épaissie et recentrée
    parts.append(poly(taper(W_MID, 28, 16), TEAL_800))
    # battement accent au sommet (creux haut -> point focal)
    fx, fy = FOCUS
    parts.append(circle(fx, fy, 16.0, STONE))
    parts.append(circle(fx, fy, 11.0, TEAL_400))
    return "".join(parts)

# ============================================================
# 2. LOCKUP HORIZONTAL — mark à gauche, texte à droite
# ============================================================
def lockup_horizontal(mark, name_fill, sub_fill, bg):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400">
<rect width="1200" height="400" fill="{bg}"/>
<svg x="40" y="90" width="220" height="220" viewBox="0 0 240 240">{mark}</svg>
<text x="310" y="200" font-family="Cormorant Garamond" font-weight="600" font-size="70" letter-spacing="8" fill="{name_fill}">OPHÉLIE BLONDEL</text>
<text x="312" y="256" font-family="DM Sans" font-weight="400" font-size="28" letter-spacing="5" fill="{sub_fill}">Kiné · Nerf vague</text>
</svg>'''

# ============================================================
# 3. APP ICON — fond teal-800 plein, mark clair
# ============================================================
def app_icon_svg():
    mark = mark_inner(c_top=TEAL_100, c_mid=TEAL_50, c_bot=TEAL_400,
                      halo=TEAL_800, dot=WHITE)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600">
<rect width="600" height="600" fill="{TEAL_800}"/>
<svg x="60" y="60" width="480" height="480" viewBox="0 0 240 240">{mark}</svg>
</svg>'''

# ============================================================
# 4. LOGO SOMBRE — lockup clair sur fond sombre
# ============================================================
def dark_mark_inner():
    return mark_inner(c_top=TEAL_100, c_mid=TEAL_50, c_bot=TEAL_400,
                      halo=TEAL_900, dot=TEAL_100)

def lockup_dark(mark):
    return lockup_horizontal(mark, TEAL_50, TEAL_100, TEAL_900)

# ============================================================
# écriture + rendu
# ============================================================
def write(n, s): open(os.path.join(OUT, n), "w").write(s)

def render(svg_path, png_path, w, h):
    subprocess.run(["inkscape", os.path.join(OUT, svg_path), "-w", str(w), "-h", str(h),
                    "--export-filename=" + os.path.join(OUT, png_path)],
                   capture_output=True)

# --- favicon ---
fav_svg = wrap(favicon_inner(), bg=STONE)
write("direction-c-favicon.svg", fav_svg)
render("direction-c-favicon.svg", "direction-c-favicon.png", 64, 64)

# --- lockup horizontal (clair) ---
mark_full = mark_inner()
write("direction-c-lockup-horizontal.svg",
      lockup_horizontal(mark_full, INK, TEAL_600, STONE))
render("direction-c-lockup-horizontal.svg", "direction-c-lockup-horizontal.png", 1600, 533)

# --- app icon ---
write("direction-c-app.svg", app_icon_svg())
render("direction-c-app.svg", "direction-c-app.png", 600, 600)

# --- logo sombre ---
write("direction-c-logo-sombre.svg", lockup_dark(dark_mark_inner()))
render("direction-c-logo-sombre.svg", "direction-c-logo-sombre.png", 1600, 533)

# --- vérif favicon 32px ---
write("_fav32.svg", fav_svg)
render("_fav32.svg", "_fav32.png", 32, 32)
os.remove(os.path.join(OUT, "_fav32.svg"))

# nettoyage des svg intermédiaires (app garde le svg ? on garde app.svg pour édition)
print("OK declinaisons")
