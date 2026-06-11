"""Compose freeze-frame stills with highlight circles + arrows at 2160x3840."""
from PIL import Image, ImageDraw
import math

YELLOW = (255, 212, 0, 255)
BLACK = (0, 0, 0, 200)

# coords given in 1080x1920 output space; scaled 2x onto 2160x3840
SPECS = {
    "5.5":  {"circle": (115, 885, 95),  "arrow": ((260, 870), (640, 830))},
    "15.4": {"circle": (912, 955, 100), "arrow": ((780, 930), (330, 865))},
    "27.2": {"circle": (630, 780, 95),  "arrow": ((530, 730), (330, 615))},
    "42.0": {"circle": (790, 1060, 105),"arrow": ((665, 1005), (340, 800))},
    "55.4": {"circle": (640, 900, 110), "arrow": None},
}


def draw_circle(d, cx, cy, r):
    # soft black halo then double yellow ring
    d.ellipse([cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8], outline=BLACK, width=26)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=YELLOW, width=12)
    d.ellipse([cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22], outline=YELLOW, width=5)


def draw_arrow(d, a, b):
    ax, ay = a
    bx, by = b
    ang = math.atan2(by - ay, bx - ax)
    head = 56
    # shaft stops short of the head tip
    sx, sy = bx - head * 0.8 * math.cos(ang), by - head * 0.8 * math.sin(ang)
    d.line([ax, ay, sx, sy], fill=BLACK, width=30)
    d.line([ax, ay, sx, sy], fill=YELLOW, width=16)
    pts = []
    for off in (math.radians(150), math.radians(-150)):
        pts.append((bx + head * math.cos(ang + off), by + head * math.sin(ang + off)))
    d.polygon([(bx, by)] + pts, fill=YELLOW, outline=(0, 0, 0, 200))


for key, spec in SPECS.items():
    img = Image.open(f"build/comps/raw_{key}.png").convert("RGBA")
    img = img.resize((2160, 3840), Image.LANCZOS)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cx, cy, r = [v * 2 for v in spec["circle"]]
    draw_circle(d, cx, cy, r)
    if spec["arrow"]:
        a = tuple(v * 2 for v in spec["arrow"][0])
        b = tuple(v * 2 for v in spec["arrow"][1])
        draw_arrow(d, a, b)
    out = Image.alpha_composite(img, ov).convert("RGB")
    out.save(f"build/comps/comp_{key}.png")
    print("comp_" + key)

# CTA background: plain 2x upscale, darkening handled in ffmpeg
img = Image.open("build/comps/raw_58.5.png").convert("RGB").resize((2160, 3840), Image.LANCZOS)
img.save("build/comps/comp_cta.png")
print("comp_cta")
