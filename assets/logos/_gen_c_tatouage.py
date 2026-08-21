#!/usr/bin/env python3
"""Direction C × tatouage — enrichissement (PAS refonte).

Garde la Direction C intacte (3 ondes déphasées + point focal = la structure
dominante) et y ajoute la « fumé » fine du tatouage d'Ophélie : une courbe
ascendante subtile qui transit les ondes (entrelacée dessus/dessous) et se
libère au sommet en un filet qui s'estompe.

Livrables : logo-c-tatouage-mark.svg/.png + lockup, fond transparent.
"""
import math, os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))

TEAL_50  = "#E1F5EE"
TEAL_100 = "#9FE1CB"
TEAL_400 = "#1D9E75"
TEAL_600 = "#0F6E56"
TEAL_800 = "#085041"
TEAL_900 = "#04342C"
STONE    = "#FAFAF7"
INK      = "#1a1a18"

# ---------- helpers géométrie (identiques à Direction C d'origine) ----------
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

def taper_w(pts, ws, n=80):
    """Ribbon à profil de largeur explicite ws[i] (continuité aux joints)."""
    s = spline(pts, n=n)
    # ws is indexed like spline output? map by resampling: we sample widths by
    # param across full spine. ws has length len(pts); interpolate per point.
    m = len(pts) - 1
    L, R = [], []
    for i, (x, y) in enumerate(s):
        ti = i / max(1, len(s) - 1)
        seg = min(int(ti * m), m - 1)
        frac = ti * m - seg
        width = ws[seg] * (1 - frac) + ws[seg + 1] * frac
        w = width / 2.0
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

# ---------- Direction C intacte (ondes + point focal) ----------
W_TOP = [(30, 142), (80, 106), (124, 142), (168, 104), (214, 140)]
W_MID = [(30, 118), (82, 92), (136, 150), (178, 100), (214, 120)]
W_BOT = [(30, 168), (84, 140), (128, 176), (172, 142), (214, 162)]
FOCUS = (82, 90)

def waves_parts():
    p = []
    p.append(poly(taper(W_TOP, 8, 3.5), TEAL_400))
    p.append(poly(taper(W_MID, 16, 7), TEAL_800))
    p.append(poly(taper(W_BOT, 8, 3.5), TEAL_600))
    return p

def focus_parts():
    fx, fy = FOCUS
    return circle(fx, fy, 10.0, STONE) + circle(fx, fy, 6.8, TEAL_400)

# ---------- la « fumé » du tatouage : filet ascendant qui transit ----------
# Courbe qui part en bas-gauche, traverse les 3 ondes (dessous la vague
# médiane dominante, dessus les deux autres), puis se libère en haut-droite
# et s'estompe (la pointe « fumé »).
SMOKE = [
    (46, 214),
    (66, 190),
    (92, 168),
    (112, 152),
    (128, 140),
    (144, 130),   # entrée sous la vague médiane
    (156, 118),
    (170, 104),   # sortie (sommet médian)
    (188, 86),
    (202, 66),
    (214, 50),    # pointe qui se dissout
]
SMOKE_W0 = 2.6   # largeur à la racine (subtil)
SMOKE_W1 = 0.45  # largeur en pointe (s'estompe en fumé)
SMOKE_COL = TEAL_100  # filet clair « fumé », distinct des 3 ondes

def smoke_segments():
    """Renvoie (back_seg, front_seg_a, front_seg_c, joints) pour tresser
    le filet dessous/dessus les ondes."""
    n = 240
    S = spline(SMOKE, n=n)
    # points de coupe par seuil x (x strictement croissant ici)
    def idx_by_x(s, xthr):
        for i, (x, y) in enumerate(s):
            if x >= xthr:
                return i
        return len(s) - 1
    iA = idx_by_x(S, 143)   # avant de plonger sous la médiane
    iB = idx_by_x(S, 177)   # après être ressortie au sommet médian
    N = len(S)
    # profil de largeur global (linéaire racine -> pointe)
    ws = [SMOKE_W0 + (SMOKE_W1 - SMOKE_W0) * (i / max(1, N - 1)) for i in range(N)]
    seg_fa = taper_w(S[0:iA + 1], ws[0:iA + 1], n=80)   # dessous -> médiane (devant)
    seg_b  = taper_w(S[iA:iB + 1], ws[iA:iB + 1], n=80) # sous la médiane (derrière)
    seg_fc = taper_w(S[iB:N], ws[iB:N], n=80)           # au-dessus (devant)
    return seg_b, seg_fa, seg_fc, (S[iA], S[iB], ws[iA], ws[iB])

# ---------- composition (ordre de dessin = profondeur) ----------
def mark_parts():
    seg_b, seg_fa, seg_fc, (jA, jB, wA, wB) = smoke_segments()
    parts = []
    # 1. vague supérieure (la plus en arrière)
    parts.append(poly(taper(W_TOP, 8, 3.5), TEAL_400))
    # 2. filet : segment sous la médiane (devant la sup', derrière la médiane)
    parts.append(poly(seg_b, SMOKE_COL))
    # 3. vague médiane (dominante) — recouvre le filet => filet « dessous »
    parts.append(poly(taper(W_MID, 16, 7), TEAL_800))
    # 4. vague inférieure
    parts.append(poly(taper(W_BOT, 8, 3.5), TEAL_600))
    # 5. filet : segments devant (racine + libération)
    parts.append(poly(seg_fa, SMOKE_COL))
    parts.append(poly(seg_fc, SMOKE_COL))
    # joints lissés (cachent la couture aux points de tressage)
    parts.append(circle(jA[0], jA[1], wA / 2, SMOKE_COL))
    parts.append(circle(jB[0], jB[1], wB / 2, SMOKE_COL))
    # 6. point focal (le battement)
    parts.append(focus_parts())
    return "".join(parts)

def mark_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">'
            + mark_parts() + "</svg>")

def lockup_svg():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640">
<svg x="490" y="46" width="220" height="220" viewBox="0 0 240 240">{mark_parts()}</svg>
<text x="600" y="398" text-anchor="middle" font-family="Cormorant Garamond" font-weight="600" font-size="86" letter-spacing="10" fill="{INK}">OPHÉLIE BLONDEL</text>
<text x="600" y="468" text-anchor="middle" font-family="DM Sans" font-weight="400" font-size="27" letter-spacing="6" fill="{TEAL_600}">Kiné · Nerf vague</text>
</svg>'''

def write(n, s):
    open(os.path.join(OUT, n), "w").write(s)

def render(svg_name, png_name, w, h):
    src = os.path.join(OUT, svg_name); dst = os.path.join(OUT, png_name)
    for cmd in (["inkscape", src, "-w", str(w), "-h", str(h), "--export-filename=" + dst],
                ["rsvg-convert", "-w", str(w), "-h", str(h), "-o", dst, src]):
        try:
            r = subprocess.run(cmd, capture_output=True)
            if r.returncode == 0 and os.path.exists(dst):
                return True
        except FileNotFoundError:
            continue
    print(f"WARN: pas de rendu PNG pour {png_name}")
    return False

write("logo-c-tatouage-mark.svg", mark_svg())
write("logo-c-tatouage-lockup.svg", lockup_svg())
render("logo-c-tatouage-mark.svg", "logo-c-tatouage-mark.png", 800, 800)
render("logo-c-tatouage-lockup.svg", "logo-c-tatouage-lockup.png", 1600, 853)

# alias explicite demandé dans le brief (« direction-c-tatouage-* »)
for src, dst in (("logo-c-tatouage-mark.svg", "direction-c-tatouage-mark.svg"),
                 ("logo-c-tatouage-lockup.svg", "direction-c-tatouage-lockup.svg")):
    import shutil
    shutil.copy(os.path.join(OUT, src), os.path.join(OUT, dst))
render("direction-c-tatouage-mark.svg", "direction-c-tatouage-mark.png", 800, 800)
render("direction-c-tatouage-lockup.svg", "direction-c-tatouage-lockup.png", 1600, 853)

print("OK c-tatouage v2")