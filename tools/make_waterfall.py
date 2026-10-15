"""Generate the header graphic: a 3D waterfall of power spectra.

    python tools/make_waterfall.py            -> writes assets/svg/waterfall.svg
    python tools/make_waterfall.py --seed 4   -> a different (random) recording

Each slice is one moment of a recording: a power spectrum from 2 to 40 Hz with the
1/f background removed, so what is left is a theta peak that waxes and wanes over
time and a small, intermittent beta bump. Slices are filled with horizontal bands
colored by height and drawn back to front in an orthographic view.

Style after N. P. Rougier's "waterfall-3d" showcase in Scientific Visualization:
Python & Matplotlib (BSD license). Writes the drawing to assets/svg/waterfall.svg and a one-line wrapper to
_includes/waterfall.svg. Colors come from CSS variables (--w0 ... --w7) in
assets/css/style.css, so the graphic follows light and dark mode.
Synthetic data, for illustration only. Needs numpy.
"""
import argparse, math, os
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--slices", type=int, default=48)
ap.add_argument("--elev", type=float, default=36)
ap.add_argument("--azim", type=float, default=-38)
args = ap.parse_args()
rng = np.random.default_rng(args.seed)

LEVELS = 8           # number of color bands
N_FREQ = 160         # points along each spectrum
TIME_LEN, FREQ_LEN, HEIGHT = 1.5, 1.0, 0.42   # world-space extents


def smooth(x, sigma):
    k = np.arange(-4 * sigma, 4 * sigma + 1)
    g = np.exp(-k ** 2 / (2 * sigma ** 2)); g /= g.sum()
    return np.convolve(np.pad(x, len(k), mode="edge"), g, mode="same")[len(k):-len(k)]


# --- Synthetic, physiologically flavoured spectra -------------------------------
freqs = np.geomspace(2, 40, N_FREQ)              # log-frequency axis
u = np.linspace(-1, 1, N_FREQ)
taper = np.exp(-2.2 * u ** 2)                    # Rougier's edge taper
S = args.slices
t = np.linspace(0, 1, S)
def slow(sigma):                                                 # slowly drifting process, unit variance
    z = smooth(rng.normal(0, 1, S), sigma)
    return (z - z.mean()) / z.std()
bursty = lambda sigma, thr: np.clip(slow(sigma) - thr, 0, None) / 2  # on/off bursts

# Theta: waxes and wanes, drifts in frequency, and jitters window to window
theta_amp = 0.45 + 0.35 * np.sin(2 * np.pi * (1.7 * t + 0.1)) + 0.15 * slow(3)
theta_amp *= np.exp(rng.normal(0, 0.22, S))
theta_amp = np.clip(theta_amp, 0.04, None)
theta_f = 6.3 + 0.5 * slow(4) + rng.normal(0, 0.25, S)
theta_w = 0.14 + 0.02 * np.abs(slow(2))
# Alpha, beta and low-gamma: intermittent bursts that come and go
alpha_amp = bursty(2.5, 0.6) * 1.3
beta_amp = bursty(1.8, 0.5) * 1.6
beta_f = 19 + 2.5 * slow(3)
gamma_amp = bursty(1.2, 0.9) * 1.4
gamma_f = 33 + 2 * slow(2)

lf = np.log(freqs)
bump = lambda f0, w: np.exp(-(lf - np.log(f0)) ** 2 / (2 * w ** 2))
spectra = []
for i in range(S):
    s = theta_amp[i] * bump(theta_f[i], theta_w[i])
    s += 0.3 * theta_amp[i] * np.exp(rng.normal(0, 0.3)) * bump(2 * theta_f[i], 0.11)   # harmonic
    s += 0.8 * alpha_amp[i] * bump(10 + rng.normal(0, 0.4), 0.09)
    s += 0.75 * beta_amp[i] * bump(beta_f[i], 0.13)
    s += 0.6 * gamma_amp[i] * bump(gamma_f[i], 0.09)
    # short-window estimates are noisy: structured ripples across frequency
    s += 0.03 + 0.06 * np.abs(smooth(rng.normal(0, 1, N_FREQ), 3.5))
    spectra.append(smooth(s, 1.6) * taper)
spectra = np.array(spectra)
# occasional broadband transient (a sharp event lifts the whole spectrum for a moment)
for i in rng.choice(S, size=2, replace=False):
    spectra[i] += 0.12 * taper * np.exp(-0.6 * (lf - lf[0]))
# a touch of temporal smoothing, like overlapping analysis windows
spectra = np.array([smooth(spectra[:, j], 0.8) for j in range(N_FREQ)]).T
spectra = spectra / spectra.max() * HEIGHT


# --- Orthographic projection (same convention as matplotlib's 3D axes) ------------
az, el = math.radians(args.azim), math.radians(args.elev)
right = np.array([-math.sin(az), math.cos(az), 0.0])
up = np.array([-math.sin(el) * math.cos(az), -math.sin(el) * math.sin(az), math.cos(el)])
toward = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)])


def project(P):
    P = np.atleast_2d(P)
    return np.c_[P @ right, -(P @ up)]           # SVG y grows downwards


ys = np.linspace(0, FREQ_LEN, N_FREQ)
xs = np.linspace(0, TIME_LEN, args.slices)
order = np.argsort([np.array([x, 0, 0]) @ toward for x in xs])   # far to near

def band_polygons(f, z0, z1):
    """Exact region of one slice that lies between heights z0 and z1 (no clipping needed)."""
    polys, n = [], len(f)
    above = f > z0
    k = 0
    while k < n:
        if not above[k]:
            k += 1; continue
        a = k
        while k < n and above[k]:
            k += 1
        b = k - 1
        def cross(i, j):   # where the curve crosses z0 between samples i and j
            t = (z0 - f[i]) / (f[j] - f[i]); return ys[i] + t * (ys[j] - ys[i])
        y_start = cross(a - 1, a) if a > 0 else ys[0]
        y_end = cross(b, b + 1) if b < n - 1 else ys[-1]
        top = [(ys[j], min(f[j], z1)) for j in range(a, b + 1)]
        polys.append([(y_start, z0)] + top + [(y_end, z0)])
    return polys


slices, all_pts = [], []
for i in order:
    x = xs[i]
    bands = []
    for k in range(LEVELS):
        z0, z1 = HEIGHT * k / LEVELS, HEIGHT * (k + 1) / LEVELS
        if spectra[i].max() <= z0:
            break
        for poly in band_polygons(spectra[i], z0, z1):
            P = project(np.array([[x, y, z] for y, z in poly]))
            bands.append((k, P)); all_pts.append(P)
    slices.append(bands)

pts = np.vstack(all_pts)
x_min, y_min = pts.min(0)
w, h = pts.max(0) - pts.min(0)
W = 600                                          # viewBox width
scale = W / w
H = round(h * scale)


def simplify(P, tol=0.12):
    """Drop points that change the outline by less than tol pixels (Ramer-Douglas-Peucker)."""
    if len(P) < 3:
        return P
    a, b = P[0], P[-1]
    d = b - a
    nrm = np.hypot(*d) or 1.0
    dist = np.abs(d[0] * (P[:, 1] - a[1]) - d[1] * (P[:, 0] - a[0])) / nrm
    i = int(np.argmax(dist))
    if dist[i] > tol:
        return np.vstack([simplify(P[:i + 1], tol)[:-1], simplify(P[i:], tol)])
    return np.vstack([a, b])


fmt = lambda P: " ".join(f"{px:.1f},{py:.1f}" for px, py in simplify((np.asarray(P) - [x_min, y_min]) * scale))

# The drawing lives in its own file; pages only reference it. Colors are CSS variables,
# which pass through <use>, so light/dark mode and the toggle still apply.
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(os.path.join(root, "assets", "svg"), exist_ok=True)
art = [f'<svg xmlns="http://www.w3.org/2000/svg"><symbol id="img" viewBox="0 0 {W} {H}">']
for bands in slices:
    for k, P in bands:
        art.append(f'<polygon style="fill:var(--w{k})" points="{fmt(P)}"/>')
art.append("</symbol></svg>")
dest = os.path.join(root, "assets", "svg", "waterfall.svg")
open(dest, "w", encoding="utf-8").write("\n".join(art) + "\n")
wrapper = (f'<svg class="waterfall" viewBox="0 0 {W} {H}" role="img" aria-label="A waterfall of brain-signal '
           f'spectra over time, with a theta peak rising and falling"><use href="{{{{ \'/assets/svg/waterfall.svg\' | relative_url }}}}#img"/></svg>\n')
open(os.path.join(root, "_includes", "waterfall.svg"), "w", encoding="utf-8").write(wrapper)
print(f"wrote {dest} ({os.path.getsize(dest) / 1024:.0f} KB) and the _includes/waterfall.svg wrapper")
