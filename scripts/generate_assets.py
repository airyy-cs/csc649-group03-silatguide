"""Generate SilatGuide's artwork with Pillow (no external images, fully original).

    python scripts/generate_assets.py

Outputs (overwritten each run)
    app/assets/chatbot_avatar.png   - friendly chibi guide in tengkolok + baju Melayu
    app/assets/loading_silat.gif    - two tiny chibi Silat friends in playful, harmless sparring

Both pieces share one `chibi()` drawing routine so the characters look like one cast.
To use your own artwork instead, just replace the two files (same names) - the app loads
whatever is in app/assets/.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

SS = 3  # supersampling factor (draw big, shrink = smooth edges)
OUT_DIR = Path(__file__).resolve().parent.parent / "app" / "assets"

# ------------------------------------------------------------------------ colours
OUT = (62, 40, 30)            # soft brown outline
SKIN = (251, 208, 166)
BLUSH = (255, 140, 135)
HAIR = (44, 30, 26)
GOLD = (226, 180, 72)
GOLD_D = (170, 124, 38)
CREAM = (255, 252, 244)
STEEL = (222, 228, 235)
MOUTH = (160, 45, 55)
SPARK = (255, 214, 102)

PAL_GREEN = dict(baju=(27, 112, 82), baju_d=(17, 78, 57), pants=(34, 44, 40),
                 samping=(224, 178, 70), samping2=(150, 30, 42),
                 tanjak=(142, 30, 44), tanjak_d=(98, 18, 30), band=GOLD)
PAL_BLACK = dict(baju=(38, 42, 46), baju_d=(24, 27, 30), pants=(30, 34, 36),
                 samping=(20, 96, 72), samping2=(226, 180, 72),
                 tanjak=(224, 178, 70), tanjak_d=(176, 130, 40), band=(142, 30, 44))


# ------------------------------------------------------------------- primitives
def _px(v: float) -> float:
    return v * SS


def ell(d, cx, cy, rx, ry, fill, outline=OUT, w=1.6):
    d.ellipse([_px(cx - rx), _px(cy - ry), _px(cx + rx), _px(cy + ry)], fill=fill,
              outline=outline, width=max(1, int(w * SS)) if outline else 0)


def poly(d, pts, fill, outline=OUT, w=1.6):
    P = [(_px(x), _px(y)) for x, y in pts]
    d.polygon(P, fill=fill)
    if outline:
        d.line(P + [P[0]], fill=outline, width=max(1, int(w * SS)), joint="curve")


def rrect(d, x0, y0, x1, y1, r, fill, outline=OUT, w=1.6):
    d.rounded_rectangle([_px(x0), _px(y0), _px(x1), _px(y1)], radius=_px(r), fill=fill,
                        outline=outline, width=max(1, int(w * SS)) if outline else 0)


def limb(d, p0, p1, width, fill, outline=OUT, w=1.6):
    def seg(wd, col):
        d.line([(_px(p0[0]), _px(p0[1])), (_px(p1[0]), _px(p1[1]))], fill=col, width=max(1, int(_px(wd))))
        for p in (p0, p1):
            r = wd / 2
            d.ellipse([_px(p[0] - r), _px(p[1] - r), _px(p[0] + r), _px(p[1] + r)], fill=col)
    seg(width + 2 * w, outline)
    seg(width, fill)


def line(d, pts, fill, width):
    d.line([(_px(x), _px(y)) for x, y in pts], fill=fill, width=max(1, int(_px(width))), joint="curve")


def star(d, cx, cy, r, fill=SPARK, rot=0):
    pts = []
    for i in range(8):
        a = math.radians(rot + i * 45)
        rr = r if i % 2 == 0 else r * 0.36
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    poly(d, pts, fill, outline=None)


def keris(d, base, angle_deg, s, length=27):
    """Tiny wavy-bladed keris (decorative, drawn small and cute). `base` = bottom of the handle."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    h1 = (base[0] + ux * 8 * s, base[1] + uy * 8 * s)
    limb(d, base, h1, 5 * s, (120, 62, 34), w=1.1)               # carved handle (hulu)
    ell(d, h1[0], h1[1], 3.3 * s, 3.3 * s, GOLD, w=1.0)          # gold ring
    left, right = [], []
    n = 16
    for i in range(n + 1):
        t = i / n
        wave = math.sin(t * math.pi * 2.7) * 1.9 * s * (1 - 0.35 * t)   # the keris "luk" (waves)
        width = (4.6 * (1 - t) + 0.6) * s
        cx = h1[0] + ux * length * s * t + nx * wave
        cy = h1[1] + uy * length * s * t + ny * wave
        left.append((cx + nx * width / 2, cy + ny * width / 2))
        right.append((cx - nx * width / 2, cy - ny * width / 2))
    poly(d, left + right[::-1], STEEL, w=1.1)

