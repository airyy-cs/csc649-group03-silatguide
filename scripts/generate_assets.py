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

# ----------------------------------------------------------------- the character
def chibi(d, cx, g, s, pal, dirn=1, lean=0.0, hop=0.0, front_hand=(26, -6), back_hand=(-2, -16),
          face="smile", blink=False, keris_angle=None, legs=True, sheath=False, brow="soft"):
    """Draw one chibi Silat friend.

    cx, g   : centre x and ground y (feet) in output pixels
    s       : size multiplier (1.0 ~ 140 px tall)
    dirn    : +1 faces right, -1 faces left
    face    : 'smile' | 'grin' | 'surprise' | 'happy'
    """
    g = g - hop
    bx = cx + lean * 0.4 * s
    hx = cx + lean * s
    top = g - 52 * s
    sh_y = top + 6 * s

    # --- legs and feet
    if legs:
        for sx in (-1, 1):
            lx = cx + sx * 9 * s
            limb(d, (lx, g - 17 * s), (lx + sx * 1 * s, g - 6 * s), 12 * s, pal["pants"])
            ell(d, lx + dirn * 2.5 * s, g - 3 * s, 8.5 * s, 4.6 * s, SKIN)

    # --- back arm (behind body)
    bs = (bx - dirn * 17 * s, sh_y)
    bh = (bs[0] + dirn * back_hand[0] * s, bs[1] + back_hand[1] * s)
    limb(d, bs, bh, 10 * s, pal["baju_d"])
    ell(d, bh[0], bh[1], 5.6 * s, 5.6 * s, SKIN)

    # --- body (baju Melayu) + samping (songket sarong) + gold trim
    rrect(d, bx - 21 * s, top, bx + 21 * s, g - 17 * s, 11 * s, pal["baju"])
    rrect(d, bx - 23 * s, g - 36 * s, bx + 23 * s, g - 19 * s, 5 * s, pal["samping"])
    for i in range(-2, 3):
        x = bx + i * 9.2 * s
        poly(d, [(x, g - 34 * s), (x + 4 * s, g - 27.5 * s), (x, g - 21 * s), (x - 4 * s, g - 27.5 * s)],
             pal["samping2"], outline=None)
    line(d, [(bx - 22.5 * s, g - 36 * s), (bx + 22.5 * s, g - 36 * s)], GOLD_D, 1.4 * s)
    rrect(d, bx - 8 * s, top - 2 * s, bx + 8 * s, top + 9 * s, 3 * s, pal["baju_d"])   # cekak musang collar
    for k in range(2):
        ell(d, bx, top + 14 * s + k * 7 * s, 1.7 * s, 1.7 * s, GOLD, outline=None)

    if sheath:  # keris tucked in the samping (avatar)
        a0 = (bx + 14 * s, g - 38 * s)
        a1 = (bx - 12 * s, g - 21 * s)
        limb(d, a0, a1, 6.5 * s, (122, 70, 38), w=1.2)
        ell(d, a0[0] + 1.5 * s, a0[1] - 1.2 * s, 4.2 * s, 4.2 * s, GOLD, w=1.1)
        limb(d, (a0[0] + 2.5 * s, a0[1] - 2 * s), (a0[0] + 6.5 * s, a0[1] - 5 * s), 4.6 * s, (120, 62, 34), w=1.0)

    # --- front arm (+ keris)
    fs = (bx + dirn * 17 * s, sh_y)
    fh = (fs[0] + dirn * front_hand[0] * s, fs[1] + front_hand[1] * s)
    limb(d, fs, fh, 10 * s, pal["baju"])
    if keris_angle is not None:
        ang = keris_angle if dirn == 1 else 180 - keris_angle
        keris(d, fh, ang, s)
    ell(d, fh[0], fh[1], 6 * s, 6 * s, SKIN)

    # --- head
    hc = g - 74 * s
    ell(d, hx - 28 * s, hc + 3 * s, 6 * s, 10 * s, HAIR)
    ell(d, hx + 28 * s, hc + 3 * s, 6 * s, 10 * s, HAIR)
    ell(d, hx, hc, 30 * s, 29 * s, SKIN)

    fx = hx + dirn * 2.5 * s
    ey = hc + 4 * s
    for sx in (-1, 1):
        ex = fx + sx * 11 * s
        ell(d, ex + sx * 7.5 * s, hc + 14 * s, 6.5 * s, 3.8 * s, BLUSH, outline=None)  # blush
        if blink or face == "happy":
            d.arc([_px(ex - 5.5 * s), _px(ey - 4 * s), _px(ex + 5.5 * s), _px(ey + 6 * s)],
                  200, 340, fill=OUT, width=max(1, int(2.2 * s * SS)))
        else:
            big = face == "surprise"
            ell(d, ex, ey, (6.2 if big else 5.2) * s, (8.2 if big else 7.2) * s, (30, 22, 22), outline=None)
            ell(d, ex + dirn * 1.2 * s, ey - 2.6 * s, 2.1 * s, 2.1 * s, (255, 255, 255), outline=None)
            ell(d, ex - dirn * 1.2 * s, ey + 2.2 * s, 1.1 * s, 1.1 * s, (255, 255, 255), outline=None)
        by = hc - 7 * s
        if face == "grin":      # determined, playful brows
            line(d, [(ex - sx * 4 * s, by + 1.6 * s * (1 if sx * dirn > 0 else -1) * 0), (ex + sx * 4 * s, by - 2.2 * s)], OUT, 1.8 * s)
        elif face == "surprise":
            line(d, [(ex - 4 * s, by - 3 * s), (ex + 4 * s, by - 3 * s)], OUT, 1.6 * s)
        elif brow == "soft":
            line(d, [(ex - 4 * s, by), (ex + 4 * s, by - 0.6 * s)], (110, 78, 60), 1.4 * s)

    my = hc + 15.5 * s
    if face == "grin":
        d.pieslice([_px(fx - 7.5 * s), _px(my - 6 * s), _px(fx + 7.5 * s), _px(my + 9 * s)], 0, 180,
                   fill=MOUTH, outline=OUT, width=max(1, int(1.4 * SS)))
        ell(d, fx, my + 4.2 * s, 3.4 * s, 1.9 * s, (255, 150, 150), outline=None)
    elif face == "surprise":
        ell(d, fx, my + 2 * s, 3.3 * s, 4.2 * s, MOUTH, w=1.2)
    elif face == "happy":
        d.pieslice([_px(fx - 7.5 * s), _px(my - 6 * s), _px(fx + 7.5 * s), _px(my + 9 * s)], 0, 180,
                   fill=MOUTH, outline=OUT, width=max(1, int(1.4 * SS)))
        ell(d, fx, my + 4.2 * s, 3.8 * s, 2 * s, (255, 150, 150), outline=None)
    else:
        d.arc([_px(fx - 6 * s), _px(my - 5 * s), _px(fx + 6 * s), _px(my + 5 * s)], 25, 155,
              fill=OUT, width=max(1, int(2 * s * SS)))

    # --- tengkolok / tanjak (peak sweeps to the back)
    m = -dirn
    pts = [(-31, -3), (-30, -17), (-22, -28), (-6, -34), (2, -36), (10, -62), (18, -38), (26, -30),
           (31, -16), (31, -3), (20, -8), (0, -11), (-20, -8)]
    poly(d, [(hx + m * x * s, hc + y * s) for x, y in pts], pal["tanjak"])
    # folded-cloth creases
    line(d, [(hx + m * -20 * s, hc - 14 * s), (hx + m * -2 * s, hc - 27 * s), (hx + m * 8 * s, hc - 52 * s)], pal["tanjak_d"], 1.6 * s)
    line(d, [(hx + m * 4 * s, hc - 16 * s), (hx + m * 18 * s, hc - 29 * s)], pal["tanjak_d"], 1.4 * s)
    # gold songket band across the forehead
    band = [(hx + m * x * s, hc + y * s) for x, y in [(-31, -3), (-20, -8), (0, -11), (20, -8), (31, -3)]]
    line(d, band, OUT, 6.6 * s)
    line(d, band, pal["band"], 4.4 * s)
    # little brooch
    poly(d, [(hx, hc - 22 * s), (hx + 4.2 * s, hc - 17 * s), (hx, hc - 12 * s), (hx - 4.2 * s, hc - 17 * s)], GOLD, w=1.1)
    ell(d, hx, hc - 17 * s, 1.5 * s, 1.5 * s, (200, 40, 60), outline=None)

# --------------------------------------------------------------- backgrounds
def _radial(size, inner, outer):
    im = Image.new("RGB", (size, size), outer)
    d = ImageDraw.Draw(im)
    for i in range(size // 2, 0, -2):
        t = i / (size / 2)
        col = tuple(int(inner[k] * (1 - t) + outer[k] * t) for k in range(3))
        d.ellipse([size / 2 - i, size / 2 - i, size / 2 + i, size / 2 + i], fill=col)
    return im


# ------------------------------------------------------------------------ avatar
def make_avatar(path: Path, size: int = 512) -> None:
    big = size * SS
    bg = _radial(big, (255, 244, 214), (226, 196, 128)).convert("RGBA")
    d = ImageDraw.Draw(bg)
    # soft songket-style diamond lattice
    step = big // 8
    for gx in range(-1, 10):
        for gy in range(-1, 10):
            cx, cy = gx * step, gy * step
            r = step * 0.18
            d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=(214, 168, 70, 60))

    # character layer (drawn at final-pixel units, SS handled inside primitives)
    layer = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    s = 4.15
    chibi(ld, size / 2 + 6, 585, s, PAL_GREEN, dirn=1, face="happy", front_hand=(30, -40),
          back_hand=(-6, -8), sheath=True, legs=False)
    # waving motion arcs + sparkles
    for k, r in enumerate((26, 38)):
        cxw, cyw = size / 2 + 6 + 17 * s + 30 * s, 388 - 40 * s - 4 * s + 40 * s * 0
    star(ld, size * 0.80, size * 0.22, 14, SPARK, 10)
    star(ld, size * 0.17, size * 0.30, 9, SPARK, 0)
    star(ld, size * 0.86, size * 0.40, 7, (255, 255, 255), 0)
    bg = Image.alpha_composite(bg, layer)

    # circular crop + gold ring
    mask = Image.new("L", (big, big), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, big - 1, big - 1], fill=255)
    out = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    od = ImageDraw.Draw(out)
    ring = int(7 * SS)
    od.ellipse([ring / 2, ring / 2, big - ring / 2, big - ring / 2], outline=GOLD_D, width=ring)
    od.ellipse([ring * 1.7, ring * 1.7, big - ring * 1.7, big - ring * 1.7], outline=(255, 236, 170), width=int(2 * SS))
    out = out.resize((size, size), Image.LANCZOS)
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path, optimize=True)

