#!/usr/bin/env python3
"""v2 — raffinements après inspection."""
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

def circle(cx, cy, r, fill, stroke=None, sw=0):
    s = f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{sw:.2f}"'
    return s + "/>"

# ============ DIRECTION A — LA CORDE VAGALE ============
def mark_a():
    stem = [(120, 34), (98, 70), (146, 104), (100, 140), (138, 176), (116, 212)]
    parts = [f'''<defs>
<linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="{TEAL_400}"/>
<stop offset="0.55" stop-color="{TEAL_600}"/>
<stop offset="1" stop-color="{TEAL_800}"/>
</linearGradient>
</defs>''']
    parts.append(poly(taper(stem, 30, 10), "url(#ga)"))
    spts = spline(stem, n=240)
    def stem_at(f): return spts[int(f * (len(spts) - 1))]

    # branche 1 haut-gauche
    o = stem_at(0.28); b1 = [o, (o[0] - 36, o[1] - 14), (60, 60)]
    parts.append(poly(taper(b1, 11, 3), TEAL_600))
    n1 = b1[-1]; parts.append(circle(n1[0], n1[1], 7.2, TEAL_400))

    # branche 2 bas-droite
    o = stem_at(0.66); b2 = [o, (o[0] + 38, o[1] + 8), (182, 176)]
    parts.append(poly(taper(b2, 11, 3), TEAL_600))
    n2 = b2[-1]; parts.append(circle(n2[0], n2[1], 7.2, TEAL_400))

    # ganglion sur le tronc (battement médian)
    g = stem_at(0.46); parts.append(circle(g[0], g[1], 5.6, TEAL_400))

    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">'
            + "".join(parts) + "</svg>")

# ============ DIRECTION C — LE RYTHME CACHÉ ============
def mark_c():
    # trois arcs déphasés (positions / hauteurs différentes = phrase dansée)
    w_top = [(30, 142), (80, 106), (124, 142), (168, 104), (214, 140)]   # creux haut
    w_mid = [(30, 118), (82, 92), (136, 150), (178, 100), (214, 120)]    # phrase 2 pics
    w_bot = [(30, 168), (84, 140), (128, 176), (172, 142), (214, 162)]   # bas déphasé
    parts = []
    parts.append(poly(taper(w_top, 8, 3.5), TEAL_400))
    parts.append(poly(taper(w_mid, 16, 7), TEAL_800))
    parts.append(poly(taper(w_bot, 8, 3.5), TEAL_600))
    # point focal : temps fort au sommet de l'onde principale (x~82,y~92)
    fx, fy = 82, 90
    parts.append(circle(fx, fy, 10.0, STONE))          # halo de séparation (fond)
    parts.append(circle(fx, fy, 6.8, TEAL_400))        # battement accent
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">'
            + "".join(parts) + "</svg>")

# ============ LOCKUP ============
def inner(mark):
    s = mark.replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">', '')
    return s.replace('</svg>', '')

def lockup(mark_inner):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640">
<rect width="1200" height="640" fill="{STONE}"/>
<svg x="490" y="46" width="220" height="220" viewBox="0 0 240 240">{mark_inner}</svg>
<text x="600" y="398" text-anchor="middle" font-family="Cormorant Garamond" font-weight="600" font-size="86" letter-spacing="10" fill="{INK}">OPHÉLIE BLONDEL</text>
<text x="600" y="468" text-anchor="middle" font-family="DM Sans" font-weight="400" font-size="27" letter-spacing="6" fill="{TEAL_600}">Kiné · Nerf vague</text>
</svg>'''

def write(n, s): open(os.path.join(OUT, n), "w").write(s)
def render(svg, png, w, h):
    subprocess.run(["inkscape", os.path.join(OUT, svg), "-w", str(w), "-h", str(h),
                    "--export-filename=" + os.path.join(OUT, png)], capture_output=True)

a = mark_a(); c = mark_c()
write("direction-a-mark.svg", a)
write("direction-c-mark.svg", c)
write("direction-a-lockup.svg", lockup(inner(a)))
write("direction-c-lockup.svg", lockup(inner(c)))

# PNG stone
for tag, m in (("a", a), ("c", c)):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">'
           f'<rect width="240" height="240" fill="{STONE}"/>' + inner(m) + "</svg>")
    write(f"_{tag}_stone.svg", svg)
    render(f"_{tag}_stone.svg", f"direction-{tag}-mark.png", 800, 800)
    os.remove(os.path.join(OUT, f"_{tag}_stone.svg"))

render("direction-a-lockup.svg", "direction-a-lockup.png", 1600, 853)
render("direction-c-lockup.svg", "direction-c-lockup.png", 1600, 853)

# test favicon 32px (verif robustesse)
for tag, m in (("a", a), ("c", c)):
    write(f"_{tag}_fav.svg", m)
    render(f"_{tag}_fav.svg", f"_{tag}_fav32.png", 32, 32)
    os.remove(os.path.join(OUT, f"_{tag}_fav.svg"))

print("OK v2")
