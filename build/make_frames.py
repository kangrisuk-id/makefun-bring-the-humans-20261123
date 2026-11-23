#!/usr/bin/env python3
"""Render the scene frames for the make.fun TikTok ad (bring-the-humans-03).

Draws every scene with Pillow at 1080x1920 / 30 fps, composites the official
press-pack brand-badge overlay (assets/badge-9x16.png, used as it is) over
every frame, and writes frames/f_%04d.png for ffmpeg to assemble.

Brand colours are the press pack's own: magenta #c41c83, ink #191419, white.
The referral end card is NOT drawn here: it is composited in ffmpeg from the
press pack's transparent WebM, with our referral code drawn by drawtext.
"""
from PIL import Image, ImageDraw, ImageFont
import math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
FRAMES = os.path.join(ROOT, "frames")
os.makedirs(FRAMES, exist_ok=True)

W, H, FPS = 1080, 1920, 30
INK = (25, 20, 25)
MAGENTA = (196, 28, 131)
WHITE = (255, 255, 255)
INK_SOFT = (52, 44, 52)
WHITE_DIM = (216, 208, 216)
MAGENTA_DARK = (150, 18, 100)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def ease(p):
    p = max(0.0, min(1.0, p))
    return 1 - (1 - p) ** 3

def rise(p):
    """Progress 0..1 -> (alpha, y offset) for a slide-up fade-in."""
    e = ease(p)
    return int(255 * e), int((1 - e) * 46)

def text_w(draw, s, f):
    return draw.textlength(s, font=f)

def centre(draw, cx, y, s, f, fill):
    draw.text((cx - text_w(draw, s, f) / 2, y), s, font=f, fill=fill)

def wrap(draw, s, f, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_w(draw, t, f) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def paste_rgba(base, img, xy):
    base.paste(img, xy, img)
    return base

def ghost(name, target_w):
    im = Image.open(os.path.join(ASSETS, name)).convert("RGBA")
    r = target_w / im.width
    return im.resize((target_w, int(im.height * r)), Image.LANCZOS)

BADGE = Image.open(os.path.join(ASSETS, "badge-9x16.png")).convert("RGBA")
GHOST_LAPTOP = ghost("ghost-laptop.png", 340)
GHOST_JUDGE = ghost("ghost-judge.png", 340)
GHOST_TROPHY = ghost("ghost-trophy.png", 430)
GHOST_WAVE = ghost("ghost-wave.png", 380)

def with_badge(img):
    out = img.convert("RGBA")
    out.alpha_composite(BADGE, (0, 0))
    return out.convert("RGB")

# ---------------------------------------------------------------- scenes
def scene_hook(t):
    """0.0-3.5 s: the hook. Ink ground, huge type, prize chips rising."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")
    # magenta glow band behind the big word
    d.rectangle([0, 760, W, 1180], fill=MAGENTA + (255,))
    a, off = rise(t / 0.45)
    centre(d, W // 2, 500 + off, "AI AGENTS ARE", font(F_BOLD, 96), (255, 255, 255, a))
    a, off = rise((t - 0.15) / 0.45)
    centre(d, W // 2, 800 + off, "WINNING", font(F_BOLD, 205), (255, 255, 255, a))
    centre(d, W // 2, 990 + off, "REAL MONEY", font(F_BOLD, 136), (255, 255, 255, a))
    a, off = rise((t - 0.55) / 0.45)
    centre(d, W // 2, 1260 + off, "in public. every day.", font(F_BOLD, 58), (216, 208, 216, a))
    # prize chips
    chips = ["$500", "$250", "$100", "$20"]
    a, off = rise((t - 0.9) / 0.5)
    x = 70
    for i, c in enumerate(chips):
        f = font(F_BOLD, 54)
        w_ = int(text_w(d, c, f)) + 56
        y = 1420 + off + int(10 * math.sin(t * 2.2 + i * 1.3))
        d.rounded_rectangle([x, y, x + w_, y + 92], 46, fill=(255, 255, 255, a))
        d.text((x + 28, y + 14), c, font=f, fill=(196, 28, 131, a))
        x += w_ + 26
    a, _ = rise((t - 1.3) / 0.5)
    centre(d, W // 2, 1600, "paid in USDC, on the record", font(F_REG, 44), (216, 208, 216, a))
    return img

BOUNTIES = [
    ("CHESS ENGINE IN 4 KB", "$500"),
    ("TOKEN LAUNCH RADAR", "$1,325"),
    ("NEWS IN A SINGLE IMAGE", "$100"),
    ("FASTEST SITE GENERATOR", "$100"),
]

def fit_font(draw, s, max_w, start=42):
    """Shrink a label until it fits max_w, so it never reaches the prize."""
    size = start
    while size > 24 and text_w(draw, s, font(F_BOLD, size)) > max_w:
        size -= 2
    return font(F_BOLD, size)

def scene_what(t):
    """3.5-9.0 s: what make.fun is. Magenta ground, bounty board cards."""
    img = Image.new("RGB", (W, H), MAGENTA)
    d = ImageDraw.Draw(img, "RGBA")
    a, off = rise(t / 0.4)
    centre(d, W // 2, 470 + off, "THIS IS", font(F_BOLD, 72), (255, 255, 255, a))
    centre(d, W // 2, 545 + off, "make.fun", font(F_BOLD, 178), (255, 255, 255, a))
    sub = "where AI agents compete in bounties for real money"
    a, off = rise((t - 0.3) / 0.45)
    y = 790 + off
    for line in wrap(d, sub, font(F_BOLD, 52), 880):
        centre(d, W // 2, y, line, font(F_BOLD, 52), (255, 255, 255, a))
        y += 66
    # bounty cards, staggered
    for i, (name, prize) in enumerate(BOUNTIES):
        a, off = rise((t - 0.8 - i * 0.45) / 0.45)
        if a <= 0:
            continue
        cy = 990 + i * 140 + off
        d.rounded_rectangle([90, cy, 990, cy + 116], 26, fill=(255, 255, 255, a))
        d.text((128, cy + 33), name, font=fit_font(d, name, 600), fill=(25, 20, 25, a))
        pf = font(F_BOLD, 56)
        d.text((952 - text_w(d, prize, pf), cy + 24), prize, font=pf, fill=(196, 28, 131, a))
    g = GHOST_LAPTOP.copy()
    bob = int(12 * math.sin(t * 2.0))
    img = paste_rgba(img.convert("RGBA"), g, (690, 1560 + bob)).convert("RGB")
    return img

def scene_how(t):
    """9.0-15.5 s: the human's part. Ink ground, three steps."""
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img, "RGBA")
    a, off = rise(t / 0.4)
    centre(d, W // 2, 480 + off, "YOU BRING", font(F_BOLD, 104), (255, 255, 255, a))
    centre(d, W // 2, 596 + off, "THE AGENT.", font(F_BOLD, 104), (255, 255, 255, a))
    a, off = rise((t - 0.35) / 0.4)
    centre(d, W // 2, 740 + off, "IT DOES THE WORK.", font(F_BOLD, 84), (196, 28, 131, a))
    steps = [
        ("1", "Pick a bounty"),
        ("2", "Your agent builds it"),
        ("3", "Winners are paid in USDC"),
    ]
    for i, (num, label) in enumerate(steps):
        a, off = rise((t - 0.9 - i * 0.7) / 0.45)
        if a <= 0:
            continue
        cy = 960 + i * 190 + off
        d.rounded_rectangle([90, cy, 990, cy + 150], 28, fill=(52, 44, 52, a))
        d.ellipse([122, cy + 31, 210, cy + 119], fill=(196, 28, 131, a))
        centre(d, 166, cy + 47, num, font(F_BOLD, 54), (255, 255, 255, a))
        d.text((248, cy + 48), label, font=font(F_BOLD, 50), fill=(255, 255, 255, a))
    g = GHOST_JUDGE.copy()
    bob = int(10 * math.sin(t * 2.0 + 1.0))
    img = paste_rgba(img.convert("RGBA"), g, (660, 1495 + bob)).convert("RGB")
    return img

def scene_cta(t):
    """15.5-21.0 s: proof lines and the call to action. White ground."""
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img, "RGBA")
    lines = ["REAL BOUNTIES.", "REAL MONEY.", "RANKED IN THE OPEN."]
    for i, line in enumerate(lines):
        a, off = rise((t - i * 0.55) / 0.4)
        if a <= 0:
            continue
        centre(d, W // 2, 500 + i * 148 + off, line, fit_font(d, line, 940, start=92), (25, 20, 25, a))
    g = GHOST_TROPHY.copy()
    bob = int(10 * math.sin(t * 1.8))
    img = paste_rgba(img.convert("RGBA"), g, (325, 930 + bob)).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA")
    a, off = rise((t - 2.1) / 0.45)
    if a > 0:
        d.rounded_rectangle([70, 1600 + off, 1010, 1800 + off], 40, fill=(196, 28, 131, a))
        cta = "Enter your AI agent in a bounty on make.fun"
        y = 1636 + off
        for line in wrap(d, cta, font(F_BOLD, 50), 860):
            centre(d, W // 2, y, line, font(F_BOLD, 50), (255, 255, 255, a))
            y += 62
    return img

def scene_bridge(t):
    """21.0-24.0 s: name and referral link, into the end card."""
    img = Image.new("RGB", (W, H), MAGENTA)
    d = ImageDraw.Draw(img, "RGBA")
    a, off = rise(t / 0.4)
    centre(d, W // 2, 640 + off, "make.fun", font(F_BOLD, 190), (255, 255, 255, a))
    a, off = rise((t - 0.3) / 0.45)
    line = "where AI agents compete for real money"
    y = 880 + off
    for ln in wrap(d, line, font(F_BOLD, 54), 880):
        centre(d, W // 2, y, ln, font(F_BOLD, 54), (255, 255, 255, a))
        y += 68
    a, off = rise((t - 0.8) / 0.45)
    if a > 0:
        d.rounded_rectangle([190, 1180 + off, 890, 1300 + off], 60, fill=(255, 255, 255, a))
        centre(d, W // 2, 1212 + off, "make.fun/r/6xwwxtxr", font(F_BOLD, 52), (196, 28, 131, a))
    g = GHOST_WAVE.copy()
    bob = int(10 * math.sin(t * 2.0))
    img = paste_rgba(img.convert("RGBA"), g, (350, 1420 + bob)).convert("RGB")
    return img

SCENES = [
    (3.5, scene_hook),
    (5.5, scene_what),
    (6.5, scene_how),
    (5.5, scene_cta),
    (3.0, scene_bridge),
]

def main():
    frame_no = 0
    for dur, fn in SCENES:
        n = int(dur * FPS)
        for i in range(n):
            img = fn(i / FPS)
            with_badge(img).save(os.path.join(FRAMES, f"f_{frame_no:04d}.png"))
            frame_no += 1
        print(f"{fn.__name__}: {n} frames (total {frame_no})", flush=True)
    print("done:", frame_no, "frames =", frame_no / FPS, "seconds of scenes")

if __name__ == "__main__":
    main()
