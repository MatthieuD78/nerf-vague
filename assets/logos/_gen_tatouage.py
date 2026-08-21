#!/usr/bin/env python3
"""Fusion logo v4 — « Le Dixième Nerf », tatouage d'Ophélie x Direction C.

Un nerf unique et continu : base dense en bas, qui s'élève en respirant
(trois ondulations = le rythme des ondes), se déploie en deux pointes fines
divergentes (signature du tatouage), et porte un battement (point focal)
au cœur du geste. Composition centrée, équilibrée, fond transparent.
"""
import math, os, subprocess

OUT = os.path.dirname(os.path.abspath(__file__))

TEAL_50  = "#E1F5EE"
TEAL_100 = "#9FE1CB"
TEAL_400 = "#1D9E75"
TEAL_600 = "#0F6E56"
TEAL_800 = "#085041"
INK      = "#1a1a18"

def _m(a, s): return (a[0]*s, a[1]*s)
def _va(a, b): return (a[0]+b[0], a[1]+b[1])
def _vs(a, b): return (a[0]-b[0], a[1]-b[1])

def _cr(a, b, c, d, t):
    t2, t3 = t*t, t*t*t
    return _m(_va(_m(b,2), _va(_m(_vs(c,a),t), _va(
        _m(_va(_va(_m(a,2),_m(b,-5)), _va(_m(c,4),_m(d,-1))), t2),
        _m(_va(_va(_m(a,-1),_m(b,3)), _va(_m(c,-3),_m(d,1))), t3)))), 0.5)

def spline(pts, n=100):
    if len(pts) == 2:
        return [(pts[0][0]+(pts[1][0]-pts[0][0])*i/n,
                 pts[0][1]+(pts[1][1]-pts[0][1])*i/n) for i in range(n+1)]
    first = pts[0]; out = []
    for i in range(len(pts)-1):
        a, b = pts[i], pts[i+1]
        c = pts[i+2] if i+2 < len(pts) else (2*pts[i+1][0]-pts[i][0], 2*pts[i+1][1]-pts[i][1])
        pm = pts[i-1] if i >= 1 else (2*pts[i][0]-first[0], 2*pts[i][1]-first[1])
        steps = n // (len(pts)-1)
        for j in range(steps):
            out.append(_cr(pm, a, b, c, j/steps))
    out.append(pts[-1])
    return out

def taper(pts, w0, w1, n=100):
    s = spline(pts, n=n); L, R = [], []
    for i,(x,y) in enumerate(s):
        t = i/max(1,len(s)-1); w = (w0+(w1-w0)*t)/2.0
        if i+1 < len(s):
            dx,dy = s[i+1][0]-x, s[i+1][1]-y
        else:
            dx,dy = x-s[i-1][0], y-s[i-1][1]
        ln = math.hypot(dx,dy) or 1; px,py = -dy/ln, dx/ln
        L.append((x+px*w, y+py*w)); R.append((x-px*w, y-py*w))
    R.reverse()
    return L + R + [s[0]]

def poly(s, fill):
    pts = " ".join(f"{x:.2f},{y:.2f}" for x,y in s)
    return f'<polygon points="{pts}" fill="{fill}"/>'

def circle(cx, cy, r, fill):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{fill}"/>'

# ---- GEOMETRIE (centré, nerf unique + deux pointes + battement) ----
TRUNK = [(120,209),(98,190),(122,170),(140,150),(120,132),(118,104),(120,74)]
TIP_A = [(120,74),(104,52),(86,32)]
TIP_B = [(120,74),(136,52),(154,32)]
FOCUS = (120, 56)

def mark_parts():
    parts = []
    parts.append(poly(taper(TRUNK, 18.0, 4.0), TEAL_800))
    parts.append(poly(taper(TIP_A, 4.2, 1.4), TEAL_800))
    parts.append(poly(taper(TIP_B, 4.2, 1.4), TEAL_800))
    fx, fy = FOCUS
    parts.append(circle(fx, fy, 10.5, TEAL_50))
    parts.append(circle(fx, fy, 6.8, TEAL_400))
    return "".join(parts)

def mark_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240">'
            + mark_parts() + '</svg>')

def lockup_svg():
    m = mark_parts()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 640">
<svg x="490" y="46" width="220" height="220" viewBox="0 0 240 240">{m}</svg>
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
                return
        except FileNotFoundError:
            continue
    print(f"WARN: pas de rendu PNG pour {png_name}")

mark = mark_svg()
write("logo-tatouage-mark.svg", mark)
write("logo-tatouage-lockup.svg", lockup_svg())
render("logo-tatouage-mark.svg", "logo-tatouage-mark.png", 600, 600)
render("logo-tatouage-lockup.svg", "logo-tatouage-lockup.png", 1200, 640)
print("OK fusion v4")