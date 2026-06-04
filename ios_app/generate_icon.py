"""
generate_icon.py
Generates the $250 Scalper app icon — 1024×1024 PNG.
Run once, then drag the output into Xcode.

Usage:
    pip install pillow
    python ios_app/generate_icon.py
Output:
    ios_app/AppIcon-1024.png
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math, sys

SIZE   = 1024
OUT    = Path(__file__).parent / "AppIcon-1024.png"

# ── Colours ───────────────────────────────────────────────────────────────────
BG         = (14,  17,  23)       # #0e1117  Streamlit dark
GREEN      = (46,  204, 113)      # #2ecc71  signal green
GREEN_DIM  = (30,  130, 72)       # darker green for area fill
WHITE      = (255, 255, 255)
GREY       = (139, 146, 168)      # #8b92a8

# ── Canvas ────────────────────────────────────────────────────────────────────
img  = Image.new("RGB", (SIZE, SIZE), BG)
draw = ImageDraw.Draw(img, "RGBA")

# ── Background gradient (dark → slightly lighter at top) ──────────────────────
for y in range(SIZE):
    t   = y / SIZE
    r   = int(BG[0] + (30  - BG[0]) * (1 - t))
    g   = int(BG[1] + (35  - BG[1]) * (1 - t))
    b   = int(BG[2] + (50  - BG[2]) * (1 - t))
    draw.line([(0, y), (SIZE, y)], fill=(r, g, b))

# ── Rising chart line ─────────────────────────────────────────────────────────
# 8 control points — left-low to right-high with one dip for realism
chart_pts = [
    (90,  820),
    (200, 760),
    (290, 700),
    (370, 730),   # small pullback
    (470, 580),
    (580, 460),
    (700, 340),
    (880, 230),
]

# Area fill under the line (semi-transparent green)
fill_pts = chart_pts + [(880, 900), (90, 900)]
draw.polygon(fill_pts, fill=(46, 204, 113, 35))

# Glow layers (wide → narrow)
for width, alpha in [(28, 15), (18, 35), (10, 80), (5, 200), (3, 255)]:
    draw.line(chart_pts, fill=(46, 204, 113, alpha), width=width, joint="curve")

# Dots at each control point
for i, (x, y) in enumerate(chart_pts):
    r = 18 if i == len(chart_pts) - 1 else 11
    # glow
    draw.ellipse([x-r*2, y-r*2, x+r*2, y+r*2],
                 fill=(46, 204, 113, 40))
    draw.ellipse([x-r, y-r, x+r, y+r],
                 fill=GREEN)

# ── "$250" text ───────────────────────────────────────────────────────────────
# Try to use a bold system font, fall back to default
def _load_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/SFNSDisplay-Bold.otf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()

font_big  = _load_font(190)
font_sub  = _load_font(68)

# Main dollar amount — bottom centre
label     = "$250"
bbox      = draw.textbbox((0, 0), label, font=font_big)
tw, th    = bbox[2] - bbox[0], bbox[3] - bbox[1]
tx        = (SIZE - tw) // 2
ty        = SIZE - th - 72

# Shadow
draw.text((tx + 6, ty + 6), label, font=font_big, fill=(0, 0, 0, 160))
# White text
draw.text((tx, ty), label, font=font_big, fill=WHITE)

# Sub-label
sub       = "Options Scalper"
sbbox     = draw.textbbox((0, 0), sub, font=font_sub)
sw        = sbbox[2] - sbbox[0]
sx        = (SIZE - sw) // 2
sy        = ty + th + 8
draw.text((sx, sy), sub, font=font_sub, fill=(139, 146, 168, 210))

# ── Moon badge — top-right corner ─────────────────────────────────────────────
moon_cx, moon_cy, moon_r = 870, 155, 90
# Outer glow
draw.ellipse(
    [moon_cx - moon_r - 20, moon_cy - moon_r - 20,
     moon_cx + moon_r + 20, moon_cy + moon_r + 20],
    fill=(46, 204, 113, 25)
)
# Circle
draw.ellipse(
    [moon_cx - moon_r, moon_cy - moon_r,
     moon_cx + moon_r, moon_cy + moon_r],
    fill=(46, 204, 113, 200)
)
# Crescent cut-out
draw.ellipse(
    [moon_cx - moon_r + 22, moon_cy - moon_r - 18,
     moon_cx + moon_r + 22, moon_cy + moon_r - 18],
    fill=(*BG, 255)
)

# ── iOS rounded-corner mask ───────────────────────────────────────────────────
mask = Image.new("L", (SIZE, SIZE), 0)
mdraw = ImageDraw.Draw(mask)
mdraw.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=220, fill=255)

result = Image.new("RGB", (SIZE, SIZE), BG)
result.paste(img, mask=mask)

result.save(OUT, "PNG")
print(f"✅  Icon saved → {OUT}")
print(f"    Drag  AppIcon-1024.png  into Xcode → Assets.xcassets → AppIcon")
