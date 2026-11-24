#!/usr/bin/env python3
"""compose24.py — THE WORLD IN ONE DAY, Tuesday 24 November 2026.

Draws a dense newspaper front page (1024x1024) with PIL, flat editorial art,
one consistent palette, no photos, no network. Deterministic: same bytes
every run. Entry: entry.png beside this file.
"""
import hashlib
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (253, 251, 245)
INK = (18, 18, 18)
GREY = (90, 90, 86)
RED = (178, 34, 28)
NAVY = (16, 34, 64)
GREEN = (22, 110, 58)
GOLD = (196, 148, 28)
MX = 16

FDIR = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(f"{FDIR}/{name}.ttf", size)


SERIF_B = lambda s: F("DejaVuSerif-Bold", s)
SERIF = lambda s: F("DejaVuSerif", s)
SANS = lambda s: F("DejaVuSans", s)
SANS_B = lambda s: F("DejaVuSans-Bold", s)
MONO_B = lambda s: F("DejaVuSansMono-Bold", s)


def wrap(d, text, font, maxw):
    """Greedy word wrap to maxw pixels; returns list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, text, font, maxw, max_lines):
    """Wrap and trim to max_lines, adding an ellipsis if trimmed."""
    lines = wrap(d, text, font, maxw)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + " ...", font=font) > maxw:
            lines[-1] = lines[-1][:-1].rstrip()
        lines[-1] = (lines[-1] + " ...").strip()
    return lines


def chip(d, x, y, text, fill):
    """CONFIRMED/REPORTED tag chip; returns width used."""
    font = SANS_B(8)
    tw = d.textlength(text, font=font)
    w = int(tw) + 10
    d.rounded_rectangle([x, y, x + w, y + 12], radius=3, fill=fill)
    d.text((x + 5, y + 2), text, font=font, fill=(255, 255, 255))
    return w


def star_points(cx, cy, r_out, r_in, rot=-90):
    import math
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 36)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


class _ScaledDraw:
    """Wraps ImageDraw, scaling 322x84 design coordinates into (w, h).

    Picture functions are authored once in a 322x84 design space (the lead
    size) and reused for the smaller card boxes; the wrapper scales every
    coordinate, line width and font size so the composition stays intact.
    """
    def __init__(self, draw, sx, sy):
        self._d = draw
        self.sx = sx
        self.sy = sy

    def _xy(self, pt):
        return (pt[0] * self.sx, pt[1] * self.sy)

    def _pts(self, pts):
        return [self._xy(p) for p in pts]

    def _box(self, box):
        return [box[0] * self.sx, box[1] * self.sy,
                box[2] * self.sx, box[3] * self.sy]

    def _kw(self, kw):
        kw = dict(kw)
        if "width" in kw:
            kw["width"] = max(1, int(round(kw["width"] * min(self.sx, self.sy))))
        return kw

    def rectangle(self, box, **kw):
        return self._d.rectangle(self._box(box), **self._kw(kw))

    def ellipse(self, box, **kw):
        return self._d.ellipse(self._box(box), **self._kw(kw))

    def polygon(self, pts, **kw):
        return self._d.polygon(self._pts(pts), **kw)

    def line(self, pts, **kw):
        return self._d.line(self._pts(pts), **self._kw(kw))

    def text(self, xy, text, font=None, **kw):
        if font is not None:
            fsize = max(6, int(round(font.size * self.sx)))
            try:
                font = ImageFont.truetype(font.path, fsize)
            except Exception:
                pass
        return self._d.text(self._xy(xy), text, font=font, **kw)



# ---------------------------------------------------------------- pictures
# Every picture is drawn on its own (w, h) layer and pasted in, so no shape
# can ever poke outside its box into the text around it.

def pic_hormuz(w, h):
    im = Image.new("RGB", (w, h), (14, 42, 84))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    d.rectangle([0, 0, w, int(h * 0.30)], fill=(196, 214, 232))  # hazy sky
    d.rectangle([0, int(h * 0.30), w, h], fill=(14, 42, 84))     # sea
    for i in range(5):  # wave lines
        yy = int(h * 0.38) + i * 9
        d.line([(8, yy), (w - 8, yy)], fill=(38, 84, 138), width=2)
    # tanker 1 (left, burning)
    d.rectangle([14, 52, 96, 64], fill=(150, 155, 160))
    d.rectangle([14, 52, 96, 56], fill=(178, 34, 28))
    d.rectangle([66, 38, 92, 52], fill=(235, 235, 230))
    d.rectangle([80, 30, 88, 38], fill=(178, 34, 28))
    # flames on tanker 1
    d.polygon([(30, 52), (40, 26), (48, 52)], fill=(240, 120, 20))
    d.polygon([(44, 52), (54, 20), (64, 52)], fill=(250, 180, 30))
    d.polygon([(58, 52), (68, 32), (76, 52)], fill=(240, 120, 20))
    # smoke column
    for r, yy in ((7, 18), (9, 10), (11, 2)):
        d.ellipse([52 - r, yy, 52 + r, yy + 2 * r], fill=(40, 40, 40))
    # tanker 2 (centre)
    d.rectangle([118, 56, 200, 68], fill=(150, 155, 160))
    d.rectangle([118, 56, 200, 60], fill=(178, 34, 28))
    d.rectangle([170, 42, 196, 56], fill=(235, 235, 230))
    d.rectangle([184, 34, 192, 42], fill=(178, 34, 28))
    # tanker 3 (right)
    d.rectangle([222, 56, 304, 68], fill=(150, 155, 160))
    d.rectangle([222, 56, 304, 60], fill=(178, 34, 28))
    d.rectangle([274, 42, 300, 56], fill=(235, 235, 230))
    # naval mines
    for cx, cy in ((112, 74), (262, 76)):
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(20, 20, 20))
        for ang in range(0, 360, 45):
            import math
            a = math.radians(ang)
            d.line([(cx + 5 * math.cos(a), cy + 5 * math.sin(a)),
                    (cx + 10 * math.cos(a), cy + 10 * math.sin(a))],
                   fill=(20, 20, 20), width=2)
    return im


def pic_gaza(w, h):
    im = Image.new("RGB", (w, h), (18, 18, 46))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    for sx, sy in ((20, 8), (60, 16), (120, 6), (200, 12), (280, 8), (300, 20), (160, 14)):
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 200))
    # apartment block
    d.rectangle([30, 24, 250, h], fill=(96, 94, 88))
    d.rectangle([30, 24, 250, 30], fill=(70, 68, 64))
    for r in range(3):
        for c in range(8):
            x0, y0 = 42 + c * 26, 36 + r * 16
            lit = (r + c) % 3 == 0
            d.rectangle([x0, y0, x0 + 14, y0 + 9],
                        fill=(250, 210, 90) if lit else (40, 40, 44))
    # blast bursting from the side
    d.polygon([(250, 40), (292, 30), (312, 48), (296, 58), (308, 66),
               (282, 72), (292, 80), (250, 74)], fill=(250, 140, 20))
    d.polygon([(250, 48), (282, 42), (296, 54), (282, 62), (250, 62)],
              fill=(255, 210, 60))
    # debris + smoke
    for dx, dy in ((262, 76), (276, 70), (290, 78), (300, 68)):
        d.rectangle([dx, dy, dx + 4, dy + 3], fill=(60, 58, 54))
    d.ellipse([256, 8, 288, 30], fill=(90, 88, 84))
    d.ellipse([272, 2, 300, 20], fill=(110, 108, 104))
    return im


def pic_asia(w, h):
    im = Image.new("RGB", (w, h), (10, 58, 32))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    for gy in (16, 32, 48, 64):
        d.line([(8, gy), (w - 8, gy)], fill=(30, 96, 58), width=1)
    pts = [(12, 68), (50, 62), (90, 66), (130, 48), (170, 52),
           (210, 30), (250, 34), (292, 12)]
    d.line(pts, fill=(255, 210, 60), width=4)
    d.polygon([(292, 12), (278, 14), (290, 24)], fill=(255, 210, 60))
    d.ellipse([284, 4, 300, 20], fill=(255, 210, 60))
    # chip labelled NV
    d.rectangle([w - 74, h - 34, w - 12, h - 8], fill=(20, 20, 24))
    d.rectangle([w - 74, h - 34, w - 12, h - 8], outline=(255, 210, 60), width=2)
    for px in range(w - 70, w - 16, 8):
        d.line([(px, h - 34), (px, h - 38)], fill=(255, 210, 60), width=1)
        d.line([(px, h - 8), (px, h - 4)], fill=(255, 210, 60), width=1)
    d.text((w - 58, h - 30), "NV", font=SANS_B(13), fill=(255, 255, 255))
    d.text((14, 4), "KOSPI +6.0%", font=SANS_B(15), fill=(255, 255, 255))
    return im


def pic_zaporizhzhia(w, h):
    im = Image.new("RGB", (w, h), (64, 48, 78))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    d.rectangle([0, 0, w, int(h * 0.45)], fill=(214, 140, 90))   # dusk sky
    d.rectangle([0, int(h * 0.45), w, h], fill=(52, 44, 52))
    # five-storey block, right section collapsed
    d.rectangle([24, 26, 220, h], fill=(120, 114, 106))
    for r in range(4):
        for c in range(6):
            x0, y0 = 34 + c * 26, 32 + r * 13
            d.rectangle([x0, y0, x0 + 14, y0 + 8],
                        fill=(250, 210, 90) if (r + c) % 4 == 0 else (52, 50, 48))
    # collapsed section: rubble
    d.polygon([(220, h), (220, 52), (252, 62), (282, h)], fill=(88, 82, 76))
    d.polygon([(228, h), (240, 66), (258, h)], fill=(70, 66, 62))
    d.polygon([(258, h), (272, 70), (292, h)], fill=(60, 56, 52))
    for dx, dy in ((232, 74), (252, 78), (272, 74)):
        d.rectangle([dx, dy, dx + 5, dy + 4], fill=(40, 38, 36))
    # smoke rising
    d.ellipse([236, 34, 258, 52], fill=(150, 146, 142))
    d.ellipse([248, 20, 272, 40], fill=(170, 166, 162))
    d.ellipse([258, 8, 278, 24], fill=(186, 182, 178))
    return im


def pic_moscow(w, h):
    im = Image.new("RGB", (w, h), (14, 14, 38))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    for sx, sy in ((24, 10), (80, 6), (150, 12), (220, 8), (290, 14), (180, 5)):
        d.ellipse([sx, sy, sx + 2, sy + 2], fill=(255, 255, 220))
    # skyline with Kremlin-style towers
    d.rectangle([0, 52, w, h], fill=(30, 28, 44))
    for tx, th in ((30, 34), (70, 44), (150, 30), (210, 40), (260, 32)):
        d.rectangle([tx, 52 - th, tx + 16, 52], fill=(44, 40, 60))
        d.ellipse([tx + 2, 52 - th - 12, tx + 14, 52 - th], fill=(196, 148, 28))
        d.line([(tx + 8, 52 - th - 12), (tx + 8, 52 - th - 20)], fill=(196, 148, 28), width=2)
    d.rectangle([110, 40, 140, 52], fill=(44, 40, 60))
    # drone swarm with red lights
    for dx, dy in ((60, 14), (110, 8), (160, 18), (210, 10), (260, 16), (90, 24), (190, 26)):
        d.line([(dx - 6, dy), (dx + 6, dy)], fill=(160, 160, 160), width=2)
        d.line([(dx, dy - 6), (dx, dy + 6)], fill=(160, 160, 160), width=2)
        d.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(255, 60, 40))
    # explosion flash on the horizon
    d.polygon([(286, 52), (296, 38), (304, 52), (312, 40), (318, 52)],
              fill=(250, 160, 30))
    d.ellipse([292, 44, 312, 56], fill=(255, 210, 80))
    return im


def pic_colombia(w, h):
    im = Image.new("RGB", (w, h), (150, 158, 168))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    # columned government building
    d.rectangle([0, 8, w, 52], fill=(232, 226, 210))
    d.rectangle([0, 8, w, 14], fill=(196, 188, 168))
    for cx in range(20, w, 36):
        d.rectangle([cx, 16, cx + 10, 52], fill=(210, 204, 186))
        d.rectangle([cx - 2, 14, cx + 12, 17], fill=(196, 188, 168))
    d.rectangle([0, 52, w, h], fill=(110, 110, 112))  # street
    d.line([(0, 52), (w, 52)], fill=(70, 70, 72), width=2)
    # car engulfed in flames (light body so it reads against the street)
    d.rectangle([96, 58, 216, 70], fill=(120, 122, 130))
    d.rectangle([116, 50, 196, 58], fill=(120, 122, 130))
    d.rectangle([124, 52, 188, 58], fill=(90, 120, 150))
    d.ellipse([112, 68, 128, 80], fill=(12, 12, 12))
    d.ellipse([188, 68, 204, 80], fill=(12, 12, 12))
    d.polygon([(106, 50), (124, 22), (140, 50)], fill=(240, 120, 20))
    d.polygon([(136, 50), (156, 14), (176, 50)], fill=(250, 180, 30))
    d.polygon([(172, 50), (190, 26), (206, 50)], fill=(240, 120, 20))
    # smoke + broken glass
    d.ellipse([140, 4, 164, 22], fill=(60, 60, 60))
    d.ellipse([158, 0, 180, 14], fill=(80, 80, 80))
    for gx, gy in ((70, 74), (240, 76), (90, 78), (230, 70)):
        d.polygon([(gx, gy), (gx + 6, gy + 2), (gx + 2, gy + 6)], fill=(180, 210, 225))
    return im


def pic_hanoi(w, h):
    im = Image.new("RGB", (w, h), (22, 20, 40))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    # restaurant frontage at night
    d.rectangle([0, 20, w, 70], fill=(120, 70, 40))
    d.rectangle([0, 20, w, 30], fill=(178, 34, 28))
    d.text((12, 22), "RESTAURANT", font=SANS_B(9), fill=(255, 230, 160))
    for wx in range(16, w - 20, 34):
        d.rectangle([wx, 36, wx + 22, 56], fill=(250, 200, 110))
        d.line([(wx + 11, 36), (wx + 11, 56)], fill=(120, 70, 40), width=2)
    # doorway burst of flame
    d.rectangle([w - 74, 36, w - 30, 70], fill=(40, 24, 16))
    d.polygon([(w - 74, 70), (w - 62, 34), (w - 52, 70)], fill=(240, 120, 20))
    d.polygon([(w - 58, 70), (w - 48, 26), (w - 36, 70)], fill=(250, 180, 30))
    d.polygon([(w - 44, 70), (w - 34, 40), (w - 26, 70)], fill=(240, 120, 20))
    # rubble + smoke
    for rx, ry in ((w - 70, 72), (w - 50, 74), (w - 30, 72)):
        d.rectangle([rx, ry, rx + 8, ry + 5], fill=(70, 66, 62))
    d.ellipse([w - 66, 8, w - 44, 26], fill=(90, 88, 84))
    d.ellipse([w - 52, 0, w - 32, 16], fill=(110, 108, 104))
    d.rectangle([0, 70, w, h], fill=(60, 58, 56))
    return im


def pic_yemen(w, h):
    im = Image.new("RGB", (w, h), (214, 178, 120))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    d.rectangle([0, 0, w, 30], fill=(232, 214, 170))  # pale sky
    d.polygon([(0, 34), (60, 10), (120, 34)], fill=(150, 110, 70))   # mountains
    d.polygon([(90, 34), (170, 6), (250, 34)], fill=(130, 94, 58))
    d.polygon([(210, 34), (280, 12), (w, 34)], fill=(150, 110, 70))
    d.rectangle([0, 34, w, h], fill=(196, 158, 100))  # desert
    d.rectangle([0, 56, w, 74], fill=(90, 88, 86))    # road
    d.line([(0, 65), (w, 65)], fill=(240, 230, 200), width=2)
    # bus struck and burning
    d.rectangle([30, 40, 120, 58], fill=(240, 200, 60))
    d.rectangle([30, 40, 120, 46], fill=(250, 240, 200))
    for wx in range(38, 116, 14):
        d.rectangle([wx, 42, wx + 9, 52], fill=(40, 60, 90))
    d.ellipse([44, 56, 58, 66], fill=(16, 16, 16))
    d.ellipse([100, 56, 114, 66], fill=(16, 16, 16))
    d.polygon([(60, 40), (72, 18), (84, 40)], fill=(240, 120, 20))
    d.polygon([(78, 40), (92, 12), (104, 40)], fill=(250, 180, 30))
    d.ellipse([72, 2, 92, 18], fill=(40, 40, 40))
    # truck struck and burning
    d.rectangle([180, 42, 250, 58], fill=(150, 90, 50))
    d.rectangle([250, 44, 272, 58], fill=(180, 120, 60))
    d.rectangle([256, 46, 268, 52], fill=(180, 220, 240))
    d.ellipse([196, 56, 210, 66], fill=(16, 16, 16))
    d.ellipse([252, 56, 266, 66], fill=(16, 16, 16))
    d.polygon([(200, 42), (212, 22), (224, 42)], fill=(240, 120, 20))
    d.ellipse([206, 8, 226, 24], fill=(40, 40, 40))
    return im


def pic_uk(w, h):
    im = Image.new("RGB", (w, h), NAVY)
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    # Union Jack (simplified) on the left
    jx, jy, jw, jh = 12, 12, 96, 52
    d.rectangle([jx, jy, jx + jw, jy + jh], fill=(0, 36, 125))
    d.polygon([(jx, jy), (jx + 14, jy), (jx + jw, jy + jh), (jx + jw - 14, jy + jh)], fill=(255, 255, 255))
    d.polygon([(jx + jw, jy), (jx + jw - 14, jy), (jx, jy + jh), (jx + 14, jy + jh)], fill=(255, 255, 255))
    d.rectangle([jx + jw // 2 - 8, jy, jx + jw // 2 + 8, jy + jh], fill=(255, 255, 255))
    d.rectangle([jx, jy + jh // 2 - 8, jx + jw, jy + jh // 2 + 8], fill=(255, 255, 255))
    d.rectangle([jx + jw // 2 - 5, jy, jx + jw // 2 + 5, jy + jh], fill=(200, 16, 46))
    d.rectangle([jx, jy + jh // 2 - 5, jx + jw, jy + jh // 2 + 5], fill=(200, 16, 46))
    # document with seal
    d.rectangle([130, 14, 300, 66], fill=(245, 243, 236))
    d.rectangle([130, 14, 300, 66], outline=(120, 118, 110), width=1)
    for ly in (24, 34, 44):
        d.line([(140, ly), (280, ly)], fill=(120, 118, 110), width=2)
    d.ellipse([268, 48, 292, 68], fill=(196, 148, 28))
    d.ellipse([274, 54, 286, 62], fill=(178, 34, 28))
    # red SANCTIONED stamp, rotated
    stamp = Image.new("RGBA", (150, 26), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stamp)
    sd.rectangle([1, 1, 148, 24], outline=(220, 40, 30, 255), width=3)
    sd.text((10, 5), "SANCTIONED", font=SANS_B(14), fill=(220, 40, 30, 255))
    stamp = stamp.rotate(14, expand=True, resample=Image.BICUBIC)
    stamp = stamp.resize((max(1, int(stamp.width * sx)),
                          max(1, int(stamp.height * sy))), Image.LANCZOS)
    im.paste(stamp, (int(140 * sx), int(10 * sy)), stamp)
    return im


def pic_ankara(w, h):
    im = Image.new("RGB", (w, h), (168, 196, 224))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    # skyline behind
    d.rectangle([0, 54, w, h], fill=(120, 128, 140))
    for bx, bh in ((10, 22), (50, 30), (100, 18), (160, 28), (230, 20), (280, 26)):
        d.rectangle([bx, 54 - bh + 22, bx + 34, 76], fill=(96, 102, 116))
    # Turkish flag (left, tilted) and Libyan flag (right, tilted)
    d.polygon([(60, 8), (150, 8), (150, 46), (60, 46)], fill=(227, 10, 23))
    d.ellipse([86, 16, 114, 38], fill=(255, 255, 255))
    d.ellipse([92, 19, 114, 35], fill=(227, 10, 23))
    d.polygon(star_points(128, 27, 7, 3), fill=(255, 255, 255))
    d.polygon([(170, 8), (262, 8), (262, 46), (170, 46)], fill=(0, 0, 0))
    d.rectangle([170, 8, 262, 21], fill=(227, 10, 23))
    d.rectangle([170, 33, 262, 46], fill=(0, 128, 0))
    d.ellipse([200, 23, 216, 31], fill=(255, 255, 255))
    d.ellipse([204, 24, 216, 30], fill=(0, 0, 0))
    d.polygon(star_points(224, 27, 4, 2), fill=(255, 255, 255))
    # handshake: two sleeves meeting at centre
    d.polygon([(40, h), (120, 62), (150, 74), (90, h)], fill=(40, 40, 56))
    d.polygon([(w - 40, h), (w - 120, 62), (w - 150, 74), (w - 90, h)], fill=(60, 60, 74))
    d.ellipse([128, 56, 192, 78], fill=(214, 164, 120))
    d.ellipse([140, 52, 180, 66], fill=(226, 178, 134))
    return im


def pic_iraq(w, h):
    im = Image.new("RGB", (w, h), (232, 206, 150))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    d.rectangle([0, 0, w, 30], fill=(240, 226, 190))
    d.ellipse([w - 52, 6, w - 20, 34], fill=(250, 210, 90))  # sun
    d.rectangle([0, 30, w, h], fill=(216, 178, 110))  # desert
    # derrick (lattice tower)
    bx = 230
    d.polygon([(bx, 26), (bx + 26, 26), (bx + 20, 70), (bx + 6, 70)], fill=(60, 54, 48))
    for yy in range(30, 68, 8):
        d.line([(bx + 2, yy), (bx + 24, yy + 6)], fill=(232, 206, 150), width=1)
    # pumpjack
    d.polygon([(40, 70), (52, 34), (64, 70)], fill=(52, 48, 44))
    d.line([(52, 34), (110, 44)], fill=(52, 48, 44), width=4)
    d.line([(110, 44), (110, 62)], fill=(52, 48, 44), width=3)
    d.ellipse([104, 38, 118, 50], fill=(52, 48, 44))
    d.line([(52, 34), (30, 30)], fill=(52, 48, 44), width=3)
    # pipeline + black oil drop
    d.rectangle([0, 66, w, 72], fill=(40, 38, 34))
    for px in range(20, w, 40):
        d.line([(px, 66), (px, 72)], fill=(120, 116, 110), width=2)
    d.ellipse([150, 40, 172, 58], fill=(16, 16, 16))
    d.polygon([(150, 52), (161, 34), (172, 52)], fill=(16, 16, 16))
    return im


def pic_mexico(w, h):
    im = Image.new("RGB", (w, h), (72, 44, 84))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    d.rectangle([0, 0, w, 34], fill=(214, 130, 80))  # dusk sky
    d.rectangle([0, 34, w, h], fill=(96, 78, 66))
    d.polygon([(0, 40), (80, 16), (160, 40)], fill=(70, 54, 72))
    d.polygon([(120, 40), (210, 12), (300, 40)], fill=(62, 48, 66))
    d.rectangle([0, 56, w, 72], fill=(70, 68, 66))  # road
    d.line([(0, 64), (w, 64)], fill=(240, 220, 120), width=2)
    # police car with flashing lights
    d.rectangle([120, 58, 210, 70], fill=(20, 20, 26))
    d.rectangle([140, 50, 190, 58], fill=(20, 20, 26))
    d.ellipse([150, 50, 162, 56], fill=(255, 50, 40))
    d.ellipse([168, 50, 180, 56], fill=(60, 120, 255))
    d.ellipse([136, 68, 148, 76], fill=(12, 12, 12))
    d.ellipse([182, 68, 194, 76], fill=(12, 12, 12))
    # surveillance drone low over the road
    cx, cy = 256, 26
    d.ellipse([cx - 18, cy - 6, cx + 18, cy + 6], fill=(90, 92, 96))
    d.ellipse([cx - 6, cy + 4, cx + 6, cy + 12], fill=(60, 62, 66))
    d.ellipse([cx - 3, cy + 6, cx + 3, cy + 10], fill=(40, 120, 200))
    for sx in (cx - 26, cx + 14):
        d.line([(sx, cy - 8), (sx + 12, cy - 8)], fill=(160, 160, 160), width=2)
        d.ellipse([sx + 2, cy - 12, sx + 10, cy - 4], fill=(200, 200, 200))
    d.line([(cx, cy + 12), (cx, cy + 22)], fill=(120, 120, 120), width=1)
    return im


def pic_nepal(w, h):
    im = Image.new("RGB", (w, h), (170, 200, 228))
    _W, _H = w, h
    w, h = 322, 84
    sx, sy = _W / 322.0, _H / 84.0
    d = _ScaledDraw(ImageDraw.Draw(im), sx, sy)
    # snow-peaked mountains
    d.polygon([(0, h), (70, 26), (140, h)], fill=(120, 140, 170))
    d.polygon([(70, 26), (52, 44), (70, 40), (88, 46), (70, 26)], fill=(255, 255, 255))
    d.polygon([(90, h), (180, 14), (270, h)], fill=(96, 118, 152))
    d.polygon([(180, 14), (158, 36), (180, 32), (202, 40), (180, 14)], fill=(255, 255, 255))
    d.polygon([(200, h), (280, 30), (w, h)], fill=(120, 140, 170))
    d.polygon([(280, 30), (262, 48), (280, 44), (296, 50), (280, 30)], fill=(255, 255, 255))
    # leaning cracked building (a block drawn tilted, with cracks)
    d.polygon([(42, 80), (98, 68), (110, 80), (54, 84)], fill=(196, 176, 140))
    d.polygon([(42, 80), (98, 68), (100, 74), (44, 84)], fill=(150, 128, 96))
    d.line([(60, 78), (66, 74), (62, 70)], fill=(60, 50, 40), width=2)
    d.line([(84, 74), (90, 70), (86, 66)], fill=(60, 50, 40), width=2)
    # red seismograph zigzag across the sky
    d.line([(0, 10), (30, 10), (38, 2), (46, 18), (54, 4), (62, 14),
            (90, 10), (120, 10), (128, 2), (136, 18), (144, 4), (152, 14),
            (180, 10), (220, 10), (228, 2), (236, 18), (244, 4), (252, 14),
            (280, 10), (w, 10)], fill=(178, 34, 28), width=2)
    d.text((w - 52, 14), "5.4", font=SANS_B(16), fill=(178, 34, 28))
    return im


# ---------------------------------------------------------------- layout

LAND = [
    (0, 8, 14), (0, 19, 21), (0, 40, 58),
    (1, 4, 7), (1, 8, 16), (1, 18, 21), (1, 30, 32), (1, 34, 58),
    (2, 5, 8), (2, 8, 16), (2, 18, 20), (2, 29, 31), (2, 33, 58),
    (3, 7, 16), (3, 28, 28), (3, 29, 31), (3, 33, 57),
    (4, 8, 15), (4, 28, 28), (4, 30, 35), (4, 36, 56), (4, 56, 57),
    (5, 7, 15), (5, 30, 36), (5, 38, 54),
    (6, 8, 15), (6, 30, 35), (6, 38, 52),
    (7, 8, 15), (7, 30, 34), (7, 35, 38), (7, 39, 51),
    (8, 8, 14), (8, 30, 33), (8, 36, 40), (8, 44, 50),
    (9, 9, 14), (9, 29, 35), (9, 36, 39), (9, 41, 50),
    (10, 9, 12), (10, 29, 36), (10, 37, 39), (10, 41, 43), (10, 46, 49),
    (11, 10, 13), (11, 30, 37), (11, 42, 44), (11, 46, 50),
    (12, 12, 13), (12, 30, 37), (12, 47, 50),
    (13, 14, 17), (13, 30, 37), (13, 47, 49), (13, 48, 52),
    (14, 14, 18), (14, 31, 36), (14, 48, 53),
    (15, 14, 18), (15, 31, 35), (15, 49, 53),
    (16, 14, 18), (16, 31, 35), (16, 50, 54),
    (17, 14, 17), (17, 31, 34), (17, 51, 56),
    (18, 15, 17), (18, 32, 34), (18, 50, 57),
    (19, 15, 17), (19, 32, 33), (19, 37, 37), (19, 50, 57),
    (20, 15, 17), (20, 32, 33), (20, 51, 56),
    (21, 15, 16), (21, 32, 33), (21, 52, 56), (21, 58, 59),
    (22, 15, 16), (22, 32, 32), (22, 53, 55), (22, 59, 59),
    (23, 15, 16), (23, 59, 59),
    (24, 15, 15),
    (25, 15, 15),
]

PINS = [  # (number, lon, lat, dx, dy)
    (1, 56.5, 26.5, 10, 12),
    (2, 34.5, 31.5, -14, 10),
    (3, 127, 37.5, 0, 0),
    (4, 35.2, 47.8, 12, -12),
    (5, 37.6, 55.8, -14, -6),
    (6, -73.6, 4.15, 0, 0),
    (7, 105.8, 21, 0, 0),
    (8, 44.9, 13, 0, 0),
    (9, -0.1, 51.5, 0, 0),
    (10, 32.9, 39.9, -16, 2),
    (11, 44.4, 33.3, 14, -4),
    (12, -107.4, 24.8, 0, 0),
    (13, 87, 27, 0, 0),
]

LEADS = [
    dict(kicker="HORMUZ \u2022 LEAD STORY",
         headline="Four tankers hit mines in the Strait of Hormuz",
         body="Iran's Revolutionary Guard says three oil tankers hit naval mines and caught fire, then a fourth was hit. Tehran's army commander ordered the strait closed further until Washington meets its conditions.",
         tag="REPORTED", tagfill=GOLD,
         source="IRGC / JMIC via Daily Summary",
         pic=pic_hormuz),
    dict(kicker="GAZA \u2022 ISRAEL\u2013HAMAS WAR",
         headline="Israeli strike kills Hamas internal security chief",
         body="An Israeli air strike killed Brig. Gen. Naeem Abu Nahel, who headed Hamas's internal security service, Gaza officials say. Six others were killed in separate strikes on Tuesday despite the ceasefire.",
         tag="CONFIRMED", tagfill=GREEN,
         source="Reuters / Hamas sources",
         pic=pic_gaza),
    dict(kicker="MARKETS \u2022 ASIA",
         headline="Asian markets surge as Nvidia's return lifts chip stocks",
         body="Taiwan, South Korea and Japan rebounded after Jensen Huang's reinstatement: Seoul's Kospi rose nearly 6% and the TAIEX climbed, with traders cheering the chip rally while doubting it lasts.",
         tag="CONFIRMED", tagfill=GREEN,
         source="ABC News / Reuters",
         pic=pic_asia),
]

CARDS = [
    ("UKRAINE \u2022 ZAPORIZHZHIA", "Russian strike kills 2, wounds 40 in Zaporizhzhia",
     "CONFIRMED", GREEN, "Reuters / Gov. Semikin", pic_zaporizhzhia),
    ("UKRAINE \u2022 MOSCOW", "Ukraine sends 350+ drones at Moscow in nine hours",
     "REPORTED", GOLD, "Rosbalt / Lenta", pic_moscow),
    ("COLOMBIA", "Car bomb outside regional offices injures 23",
     "CONFIRMED", GREEN, "Reuters", pic_colombia),
    ("VIETNAM", "Hanoi restaurant blast kills at least six",
     "CONFIRMED", GREEN, "AP", pic_hanoi),
    ("YEMEN", "Saudi strikes on buses, trucks leave 25 dead or missing",
     "REPORTED", GOLD, "Saba", pic_yemen),
    ("UK \u2022 SANCTIONS", "Britain sanctions Yemen's Houthis and four officials",
     "CONFIRMED", GREEN, "Reuters", pic_uk),
    ("TURKEY \u2022 LIBYA", "Libya's Haftar visits Ankara for the first time",
     "CONFIRMED", GREEN, "Reuters", pic_ankara),
    ("IRAQ", "Baghdad orders federal control of Kurdish oilfields",
     "CONFIRMED", GREEN, "Reuters", pic_iraq),
    ("MEXICO", "US drone helps capture 'El Chapo Isidro'",
     "CONFIRMED", GREEN, "Mexican officials", pic_mexico),
    ("NEPAL", "Magnitude 5.4 quake strikes Nepal's Koshi Province",
     "CONFIRMED", GREEN, "The Statesman", pic_nepal),
]

NUMBERS = [
    ("KOSPI", "+6.0%"), ("TAIEX", "UP"), ("NIKKEI", "REBOUND"),
    ("BRENT", "$85"), ("GOLD", "$3,637"), ("DRONES AT MOSCOW", "350+"),
    ("TANKERS HIT", "4"), ("MENINGITIS CASES", "272"),
    ("MIGRANTS TO RETURN", "5,303"), ("CANADA FLEET FIT", "41.9%"),
]

TIMELINE = [
    ("00:00", "Iran: four tankers hit mines in Hormuz"),
    ("00:52", "US blacklists Megaspeed + 6 firms"),
    ("01:04", "Russian aircraft enter S. Korea ADIZ"),
    ("02:09", "US drone helps capture El Chapo Isidro"),
    ("05:54", "Malaysia to return migrants to Myanmar"),
    ("08:16", "Hanoi restaurant blast kills six"),
    ("10:42", "Saudi strikes kill 25 in Yemen"),
    ("11:40", "Israel kills Hamas security chief"),
    ("13:45", "Haftar visits Ankara"),
]

ALSO_ON = [
    ("EUROPE", "Germany first to use Ukraine's Delta battle system"),
    ("EUROPE", "Norway, Ukraine expand anti-drone cooperation"),
    ("EUROPE", "Kyiv: Libya ship strikes were self-defence"),
    ("EUROPE", "Germans narrowly oppose Ukraine military aid \u2014 survey"),
    ("EUROPE", "Latvia sees war 'tipping point' next year"),
    ("EUROPE", "Magyar to meet Zelenskyy in W. Ukraine (SCHEDULED)"),
    ("EUROPE", "Russian drone briefly violates Polish airspace"),
    ("EUROPE", "Russia rebuilding base 60 km from Finland \u2014 report"),
    ("N. AMER", "US blacklists Alibaba-linked firm in Megaspeed sweep"),
    ("N. AMER", "Trump: Nvidia return poses no security risk"),
    ("N. AMER", "N. Korea may shut Swiss office in Pyongyang"),
    ("M. EAST", "Libya mission urges probe into Benghazi port attacks"),
    ("M. EAST", "Tripoli demands Kyiv explain ship strikes"),
    ("AFRICA", "DRC fighting traps Ebola responders in Ituri"),
    ("ASIA", "Indonesia names two candidates for VP"),
    ("ASIA", "China sentences official Ma to death for spying"),
    ("ASIA", "S. Korea offers $375k to catch AI exam cheats"),
    ("ASIA", "Bukele names 3 Salvadoran soldiers killed in Haiti"),
    ("LATAM", "Colombia blast on eve of FARC deal's 10th anniversary"),
    ("MARKETS", "Brent ~$85; gold $3,637 as tech rally lifts Asia"),
    ("MARKETS", "US PCE report due Wed 25 Nov (SCHEDULED)"),
]


def draw_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.line([(MX, 10), (W - MX, 10)], fill=INK, width=1)
    d.text((MX, 15), "EST. 2026 \u2022 ONE DAY, ONE PAGE", font=SANS_B(10), fill=GREY)
    right = "PRICE: FREE \u2022 1024 x 1024"
    d.text((W - MX - d.textlength(right, font=SANS_B(10)), 15), right,
           font=SANS_B(10), fill=GREY)
    title = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(title, font=SERIF_B(46))) / 2, 30), title,
           font=SERIF_B(46), fill=INK)
    date = "TUESDAY 24 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=SANS_B(21))) / 2, 82), date,
           font=SANS_B(21), fill=RED)
    d.line([(MX, 108), (W - MX, 108)], fill=INK, width=3)
    d.line([(MX, 112), (W - MX, 112)], fill=INK, width=1)

    # ---- numbers strip
    d.rectangle([MX, 118, W - MX, 146], fill=INK)
    slot = (W - 2 * MX) / len(NUMBERS)
    for i, (label, value) in enumerate(NUMBERS):
        cx = MX + slot * i + slot / 2
        lw = d.textlength(label, font=SANS_B(8))
        d.text((cx - lw / 2, 121), label, font=SANS_B(8), fill=(170, 170, 165))
        vw = d.textlength(value, font=SANS_B(12))
        d.text((cx - vw / 2, 132), value, font=SANS_B(12), fill=(255, 255, 255))

    # ---- three leads
    COLW = (W - 2 * MX - 2 * 12) // 3
    for i, lead in enumerate(LEADS):
        x = MX + i * (COLW + 12)
        d.text((x, 154), lead["kicker"], font=SANS_B(10), fill=RED)
        hl = fit_lines(d, lead["headline"], SERIF_B(17), COLW, 2)
        yy = 168
        for line in hl:
            d.text((x, yy), line, font=SERIF_B(17), fill=INK)
            yy += 21
        img.paste(lead["pic"](COLW, 84), (x, 212))
        body = fit_lines(d, lead["body"], SANS(10), COLW, 4)
        yy = 300
        for line in body:
            d.text((x, yy), line, font=SANS(10), fill=INK)
            yy += 13
        cw = chip(d, x, 350, lead["tag"], lead["tagfill"])
        d.text((x + cw + 6, 351), "Source: " + lead["source"],
               font=SANS(9), fill=GREY)
    d.line([(MX, 364), (W - MX, 364)], fill=INK, width=1)

    # ---- the day in pictures
    d.text((MX, 370), "THE DAY IN PICTURES", font=SERIF_B(16), fill=INK)
    note = "Every picture shows its own story"
    d.text((W - MX - d.textlength(note, font=SANS(9)), 374), note,
           font=SANS(9), fill=GREY)
    CW = (W - 2 * MX - 4 * 10) // 5
    CH = 148
    for i, (kicker, headline, tag, tagfill, source, picfn) in enumerate(CARDS):
        col, row = i % 5, i // 5
        x = MX + col * (CW + 10)
        y = 390 + row * (CH + 8)
        img.paste(picfn(CW - 2, 74), (x + 1, y + 1))
        d.text((x, y + 78), kicker, font=SANS_B(8), fill=RED)
        hl = fit_lines(d, headline, SANS_B(10), CW, 3)
        yy = y + 89
        for line in hl:
            d.text((x, yy), line, font=SANS_B(10), fill=INK)
            yy += 12
        cw = chip(d, x, y + 130, tag, tagfill)
        d.text((x + cw + 5, y + 131), source, font=SANS(8), fill=GREY)

    # ---- the day in UTC
    d.line([(MX, 700), (W - MX, 700)], fill=INK, width=1)
    d.text((MX, 706), "THE DAY IN UTC", font=SERIF_B(14), fill=INK)
    for i, (t, text) in enumerate(TIMELINE):
        col, row = i % 3, i // 3
        x = MX + col * 336
        y = 724 + row * 12
        d.text((x, y), t, font=MONO_B(10), fill=RED)
        d.text((x + 38, y), text, font=SANS(9), fill=INK)

    # ---- map (21 Nov style: tall dense dotted land grid, numbered pins)
    d.line([(MX, 764), (W - MX, 764)], fill=INK, width=1)
    d.text((MX, 770), "WHERE THE NEWS HAPPENED", font=SERIF_B(14), fill=INK)
    d.text((MX, 786), "Pins mark the pictured stories", font=SANS(9), fill=GREY)
    MAPX, MAPY, MAPW, MAPH = 24, 800, 360, 168

    def lonlat_to_xy(lon, lat):
        return (MAPX + (lon + 180) / 360 * MAPW,
                MAPY + (80 - lat) / 135 * MAPH)

    for r, c0, c1 in LAND:
        for c in range(c0, c1 + 1):
            cx = MAPX + c * (MAPW / 64) + 2
            cy = MAPY + r * (MAPH / 26) + 3
            d.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=NAVY)
    for num, lon, lat, dx, dy in PINS:
        px, py = lonlat_to_xy(lon, lat)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=INK)
        qx, qy = px + dx, py + dy
        if dx or dy:
            d.line([(px, py), (qx, qy)], fill=GREY, width=1)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=RED, outline=(255, 255, 255), width=1)
        num_s = str(num)
        nw = d.textlength(num_s, font=SANS_B(9))
        d.text((qx - nw / 2, qy - 6), num_s, font=SANS_B(9), fill=(255, 255, 255))

    # ---- also on
    d.text((408, 770), "ALSO ON", font=SERIF_B(14), fill=INK)
    cols = [ALSO_ON[:11], ALSO_ON[11:]]
    for ci, col_items in enumerate(cols):
        x = 408 + ci * (292 + 16)
        y = 788
        for region, text in col_items:
            lab = region + "  "
            lw = d.textlength(lab, font=SANS_B(8))
            lines = wrap(d, text, SANS(9), 292 - lw)
            lines = lines[:2]
            d.text((x, y), lab, font=SANS_B(8), fill=RED)
            yy = y
            for ln in lines:
                d.text((x + lw, yy), ln, font=SANS(9), fill=INK)
                yy += 11
            y = yy + 4

    # ---- date check box (exactly two lines inside)
    d.rectangle([16, 972, 1008, 1006], outline=RED, width=2)
    head = "DATE CHECK \u2014 NOT TODAY'S NEWS:  "
    hw = d.textlength(head, font=SANS_B(9))
    d.text((22, 975), head, font=SANS_B(9), fill=RED)
    l1 = "Nvidia reinstates Huang (Mon 23 Nov) \u2022 Sea drones sink Russian corvette off Libya (Sun 23 Nov) \u2022 Poland summons Russia envoy (Mon 23 Nov)"
    l2 = "COP31 collapsed with no deal (Sun 22 Nov) \u2022 ICJ found Myanmar guilty of genocide (Thu 19 Nov) \u2022 Murmansk governor detained (Mon 23 Nov) \u2022 BYD Dutch sales ban (Mon 23 Nov)"
    d.text((22 + hw, 975), l1, font=SANS(8), fill=INK)
    d.text((22, 989), l2, font=SANS(8), fill=INK)

    # ---- footer
    d.text((MX, 1012),
           "SOURCES: Reuters, AP, Just Security, Daily Summary of World, Kyiv Independent, Al Jazeera, The Statesman, ABC News, Yeni Safak, Daily Investor",
           font=SANS(8), fill=GREY)
    return img


def main():
    img = draw_page()
    img.save("entry.png", format="PNG", optimize=False)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
