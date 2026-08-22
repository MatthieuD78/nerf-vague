#!/usr/bin/env python3
"""Direction C × tatouage — v2 (correctif visibilité de la « fumé »).

Retour utilisateur : la courbe « fumé » du tatouage était INVISIBLE
(filet teal-100 trop pâle, fondant dans le fond clair).

CORRECTION :
- La « fumé » devient un nerf FONCÉ (teal-800) nettement plus épais,
  qui se détache au premier coup d'œil sur le fond clair.
- Effet « doublé » : un second filet lumineux (teal-400) légèrement
  décalé court en parallèle, lisant le geste du tatouage (double trait),
  reste lisible.
- On GARDE la Direction C intacte : 3 ondes + point focal.
- Le filet s'estompe toujours en pointe (le geste « fumé »), mais il reste visible.

Livrables (ne pas écraser les existants) :
  logo-c-tatouage-v2-mark.svg/.png + logo-c-tatouage-v2-lockup.svg/.png
"""
import math, os, subprocess, shutil

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
    s = spline(pts, n=n)
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

# ---------- Direction C intacte (ondes + point focal, inchangés) ----------
W_TOP = [(30, 142), (80, 106), (124, 142), (168, 104), (214, 140)]
W_MID = [(30, 118), (82, 92), (136, 150), (178, 100), (214, 120)]
W_BOT = [(30, 168), (84, 140), (128, 176), (172, 142), (214, 162)]
FOCUS = (82, 90)

def focus_parts():
    fx, fy = FOCUS
    return circle(fx, fy, 10.0, STONE) + circle(fx, fy, 6.8, TEAL_400)

# ---------- la « fumé » du tatouage : filet ascendant (désormais visible) ----------
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

# --- profil « doublé » : un nerf foncé + un filet lumineux parallèle ---
MAIN_W0 = 4.6     # racine épaisse (bien visible)
MAIN_W1 = 1.0     # pointe fine mais encore lisible
MAIN_COL = TEAL_800

ECHO_DX = 3.0     # décalage parallèle du filet lumineux
ECHO_DY = -3.2
ECHO_W0 = 1.9
ECHO_W1 = 0.35
ECHO_COL = TEAL_400

def _smoke_ribbon(spine, w0, w1):
    """Renvoie {b, fa, fc, jA, jB, wA, wB} : segments du filet tressé
    dessous/dessus la vague médiane."""
    S = spline(spine, n=240)
    def idx_by_x(s, xthr):
        for i, (x, y) in enumerate(s):
            if x >= xthr:
                return i
        return len(s) - 1
    iA = idx_by_x(S, 143)
    iB = idx_by_x(S, 177)
    N = len(S)
    ws = [w0 + (w1 - w0) * (i / max(1, N - 1)) for i in range(N)]
    return {
        "fa": taper_w(S[0:iA + 1], ws[0:iA + 1], n=80),
        "b":  taper_w(S[iA:iB + 1], ws[iA:iB + 1], n=80),
        "fc": taper_w(S[iB:N], ws[iB:N], n=80),
        "jA": S[iA], "jB": S[iB], "wA": ws[iA], "wB": ws[iB],
    }

def mark_parts():
    echo_spine = [(x + ECHO_DX, y + ECHO_DY) for x, y in SMOKE]
    main = _smoke_ribbon(SMOKE, MAIN_W0, MAIN_W1)
    echo = _smoke_ribbon(echo_spine, ECHO_W0, ECHO_W1)

    parts = []
    # 1. vague supérieure (la plus en arrière)
    parts.append(poly(taper(W_TOP, 8, 3.5), TEAL_400))
    # 2. filet : segments sous la médiane (derrière la vague médiane)
    parts.append(poly(echo["b"], ECHO_COL))
    parts.append(poly(main["b"], MAIN_COL))
    # 3. vague médiane (dominante) — recouvre le filet => filet « dessous »
    parts.append(poly(taper(W_MID, 16, 7), TEAL_800))
    # 4. vague inférieure
    parts.append(poly(taper(W_BOT, 8, 3.5), TEAL_600))
    # 5. filets : segments devant (racine + libération)
    parts.append(poly(echo["fa"], ECHO_COL))
    parts.append(poly(echo["fc"], ECHO_COL))
    parts.append(poly(main["fa"], MAIN_COL))
    parts.append(poly(main["fc"], MAIN_COL))
    # joints lissés (cachent la couture aux points de tressage)
    parts.append(circle(echo["jA"][0], echo["jA"][1], echo["wA"] / 2, ECHO_COL))
    parts.append(circle(echo["jB"][0], echo["jB"][1], echo["wB"] / 2, ECHO_COL))
    parts.append(circle(main["jA"][0], main["jA"][1], main["wA"] / 2, MAIN_COL))
    parts.append(circle(main["jB"][0], main["jB"][1], main["wB"] / 2, MAIN_COL))
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

write("logo-c-tatouage-v2-mark.svg", mark_svg())
write("logo-c-tatouage-v2-lockup.svg", lockup_svg())
render("logo-c-tatouage-v2-mark.svg", "logo-c-tatouage-v2-mark.png", 800, 800)
render("logo-c-tatouage-v2-lockup.svg", "logo-c-tatouage-v2-lockup.png", 1600, 853)

print("OK c-tatouage v2")