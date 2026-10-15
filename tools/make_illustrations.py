"""Generate the small project illustrations in _includes/illustrations/.

    python tools/make_illustrations.py

Each picture explains one idea from a project page. The signals are synthetic
(made up for illustration), not data. Drawings go to assets/svg/<name>.svg and a
one-line wrapper to _includes/illustrations/<name>.svg. Colors are CSS variables
from assets/css/style.css, so the drawings follow light and dark mode. Needs numpy.
"""
import os
import re
import numpy as np

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_includes", "illustrations")
os.makedirs(OUT, exist_ok=True)


def smooth(x, sigma):
    k = np.arange(-int(4 * sigma), int(4 * sigma) + 1)
    g = np.exp(-k ** 2 / (2 * sigma ** 2)); g /= g.sum()
    return np.convolve(np.pad(x, len(k), mode="edge"), g, mode="same")[len(k):-len(k)]


def path(xs, ys):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))


# Inline styles (not classes) because the drawings are referenced with <use>, where
# page stylesheets don't reach but CSS variables do; light/dark mode keeps working.
STYLE = {
    "tr": "fill:none;stroke:var(--ink);stroke-width:1;stroke-linejoin:round;opacity:.85",
    "acc": "fill:none;stroke:var(--accent);stroke-width:1.8;stroke-linecap:round",
    "thin": "fill:none;stroke:var(--slate);stroke-width:.8",
    "dash": "stroke-dasharray:3 4",
    "band": "fill:var(--w0);opacity:.75;stroke:none",
    "band-acc": "fill:var(--w2);opacity:.45;stroke:none",
    "target": "fill:var(--w1);stroke:var(--accent);stroke-width:1.2",
    "spk": "fill:none;stroke:var(--ink);stroke-width:1;opacity:.7",
    "spk-acc": "fill:none;stroke:var(--accent);stroke-width:1.1",
    "lbl": "font:italic 12.5px var(--font);fill:var(--slate)",
    "strong": "font-style:normal;font-weight:600;fill:var(--ink)",
    "acc-text": "fill:var(--accent)",
}


def styled(cls):
    names = cls.split()
    if "acc" in names and "thin" in names:     # thin accent rule
        return STYLE["acc"] + ";stroke-width:1.2"
    return ";".join(STYLE[c] for c in names)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets", "svg")
os.makedirs(ART, exist_ok=True)


def svg(name, w, h, label, body):
    body = [re.sub(r'class="([^"]+)"', lambda m: f'style="{styled(m.group(1))}"', b) for b in body]
    art = (f'<svg xmlns="http://www.w3.org/2000/svg"><symbol id="img" viewBox="0 0 {w} {h}" overflow="visible">\n'
           + "\n".join(body) + "\n</symbol></svg>\n")
    open(os.path.join(ART, name), "w", encoding="utf-8").write(art)
    wrapper = (f'<svg class="illus-svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
               f'<use href="{{{{ \'/assets/svg/{name}\' | relative_url }}}}#img"/></svg>\n')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(wrapper)
    print("wrote", name)


def text(x, y, s, cls="lbl", anchor="start"):
    return f'<text class="{cls}" x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}">{s}</text>'


# 1. OCD decoding: channels across neutral/trigger periods, and the decoder's running guess
rng = np.random.default_rng(3)
W, H = 640, 270
x0, x1 = 20, 620
n = 1200
t = np.linspace(0, 60, n)
xs = x0 + (x1 - x0) * t / 60
trig = [(13, 26), (38, 51)]
in_trig = np.zeros(n)
for a, b in trig:
    in_trig += 1 / (1 + np.exp(-(t - a) * 3)) * (1 - 1 / (1 + np.exp(-(t - b) * 3)))
body = []
for a, b in trig:
    xa, xb = x0 + (x1 - x0) * a / 60, x0 + (x1 - x0) * b / 60
    body.append(f'<rect class="band" x="{xa:.1f}" y="18" width="{xb - xa:.1f}" height="236"/>')
    body.append(text((xa + xb) / 2, 14, "trigger", anchor="middle"))
body.append(text((x0 + 120) / 2 + 40, 14, "neutral", anchor="middle"))
for c in range(4):
    base = 46 + c * 34
    slow = smooth(rng.normal(0, 1, n), 14) * 2.2
    fast = rng.normal(0, 1, n) * (0.7 + 1.9 * in_trig * (0.6 + 0.4 * rng.random()))
    y = base + (slow + smooth(fast, 1.2) * 3.2)
    body.append(f'<path class="tr" d="{path(xs, y)}"/>')
p = np.clip(0.18 + 0.65 * in_trig + smooth(rng.normal(0, 1, n), 10) * 0.35, 0.02, 0.98)
ytop, ybot = 196, 248
body.append(f'<line class="thin dash" x1="{x0}" y1="{(ytop + ybot) / 2}" x2="{x1}" y2="{(ytop + ybot) / 2}"/>')
body.append(f'<path class="acc" d="{path(xs, ybot - p * (ybot - ytop))}"/>')
body.append(text(x0 + 2, ytop - 6, "decoder's guess: trigger or not?"))
svg("ocd-decoding.svg", W, H, "Illustration: four brain signals become busier during two trigger periods, and a decoder's running guess rises during those periods.", body)

# 2. Frontal biomarkers: three clocks out of step, then aligned by shared skin pulses
rng = np.random.default_rng(5)
W, H = 640, 200
rows = ["implant A", "implant B", "scalp EEG"]
offsets = [0.0, 1.6, -1.1]
pulses = [3.0, 8.5, 14.0]
body = []
for panel, (px0, title, aligned) in enumerate([(20, "as recorded", False), (340, "lined up", True)]):
    pw = 280
    body.append(text(px0, 16, title, cls="lbl strong"))
    for r, name in enumerate(rows):
        base = 58 + r * 54
        tt = np.linspace(0, 18, 600)
        y = smooth(rng.normal(0, 1, 600), 3) * 4
        sh = 0 if aligned else offsets[r]
        for pt in pulses:
            y -= 22 * np.exp(-((tt - (pt + sh)) ** 2) / (2 * 0.06 ** 2))
        xs = px0 + pw * tt / 18
        body.append(f'<path class="tr" d="{path(xs, base + y)}"/>')
        if not aligned:
            body.append(text(px0, base + 20, name))
    if aligned:
        for pt in pulses:
            xp = px0 + pw * pt / 18
            body.append(f'<line class="acc dash" x1="{xp:.1f}" y1="26" x2="{xp:.1f}" y2="186"/>')
svg("ocd-sync.svg", W, H, "Illustration: three recordings whose sync pulses do not line up, and the same recordings lined up using those pulses.", body)

# 3. Loss-of-control eating: spikes and response, milkshake vs water, around the moment of tasting
rng = np.random.default_rng(8)
W, H = 640, 340
t = np.linspace(-1, 4, 500)
x0, x1 = 60, 600
X = lambda v: x0 + (x1 - x0) * (v + 1) / 5
shape = (t > 0) * (1 - np.exp(-np.clip(t, 0, None) / 0.35)) * np.exp(-np.clip(t, 0, None) / 1.8)
body = []
# raster: one row per sip; spikes become denser after a milkshake, barely change after water
rt, rows, rh = 34, 10, 6.5
dt = t[1] - t[0]
for g, (gain, cls, name) in enumerate([(9.0, "spk-acc", "milkshake"), (1.4, "spk", "water")]):
    gy = rt + g * (rows * rh + 12)
    body.append(text(x0 - 8, gy + rows * rh / 2 + 4, name, cls="lbl acc-text" if g == 0 else "lbl", anchor="end"))
    for r in range(rows):
        rate = 6 * (1 + gain * shape * (0.8 + 0.4 * rng.random()))
        spikes = t[rng.random(len(t)) < rate * dt]
        y = gy + r * rh
        d = " ".join(f"M{X(sp):.1f},{y:.1f} v{rh - 1.5:.1f}" for sp in spikes)
        body.append(f'<path class="{cls}" d="{d}"/>')
# averaged response below
y0, y1 = 300, 190
shake = 0.15 + shape * 1.0 + smooth(rng.normal(0, 1, 500), 6) * 0.025
water = 0.15 + shape * 0.22 + smooth(rng.normal(0, 1, 500), 6) * 0.025
Y = lambda v: y0 - (y0 - y1) * v
body += [f'<line class="thin" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}"/>',
         f'<line class="thin dash" x1="{X(0):.1f}" y1="{rt - 12}" x2="{X(0):.1f}" y2="{y0}"/>',
         text(X(0) + 6, rt - 16, "sip delivered"),
         text(x0, y0 + 20, "1 s before"), text(x1, y0 + 20, "4 s after", anchor="end"),
         text(x0 - 8, (y0 + y1) / 2 + 4, "response", anchor="end")]
for v, cls in [(shake, "acc"), (water, "tr")]:
    band = np.r_[Y(v + 0.05), Y(v - 0.05)[::-1]]
    bx = np.r_[X(t), X(t)[::-1]]
    body.append(f'<path class="{"band-acc" if cls == "acc" else "band"}" d="{path(bx, band)} Z"/>')
    body.append(f'<path class="{cls}" d="{path(X(t), Y(v))}"/>')
body.append(text(X(1.0) + 14, Y(shake[np.argmin(abs(t - 1.0))]) - 6, "milkshake", cls="lbl acc-text"))
body.append(text(X(2.2), Y(water[np.argmin(abs(t - 2.2))]) + 15, "water"))
svg("loc-taste.svg", W, H, "Illustration: spikes from one neuron become denser after a sip of milkshake but not after water, and the averaged response rises only for the milkshake.", body)

# 4. Primate implants: a small tilt at the skull grows into millimetres of error at depth
W, H = 640, 260
body = []
cx, top = 250, 40
xs = np.linspace(60, 440, 200)
skull = top + 0.0016 * (xs - cx) ** 2
body.append(f'<path class="tr" d="{path(xs, skull)}"/>')
body.append(text(445, skull[-1] + 4, "skull"))
deep = 230
ang = np.deg2rad(9)
body.append(f'<line class="thin dash" x1="{cx}" y1="{top}" x2="{cx}" y2="{deep}"/>')
body.append(f'<line class="acc" x1="{cx}" y1="{top}" x2="{cx + (deep - top) * np.tan(ang):.1f}" y2="{deep}"/>')
body.append(f'<circle class="target" cx="{cx}" cy="{deep}" r="7"/>')
body.append(text(cx - 14, deep + 4, "deep target", anchor="end"))
for d, lab in [(104, "near the surface: a small miss"), (deep - 6, "at depth: millimetres off")]:
    off = (d - top) * np.tan(ang)
    body.append(f'<line class="acc thin" x1="{cx}" y1="{d}" x2="{cx + off:.1f}" y2="{d}"/>')
    for xe in (cx, cx + off):
        body.append(f'<line class="acc thin" x1="{xe:.1f}" y1="{d - 4}" x2="{xe:.1f}" y2="{d + 4}"/>')
    body.append(text(cx + off + 12, d + 4, lab))
body.append(text(cx + 16, top + 22, "small tilt", cls="lbl acc-text"))
body.append(text(cx - 10, 130, "planned path", anchor="end"))
svg("nhp-depth.svg", W, H, "Illustration: a path tilted slightly at the skull drifts further from the planned path the deeper it goes.", body)
