"""Draw a classic black/white football badge to cover the source logo (top-left)."""
from PIL import Image, ImageDraw
import math

S = 4  # supersample
CX, CY, R = 138 * S, 228 * S, 78 * S
img = Image.new("RGBA", (1080 * S, 1920 * S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

# soft shadow + white ball + outline
d.ellipse([CX - R - 10*S, CY - R - 6*S, CX + R + 10*S, CY + R + 14*S], fill=(0, 0, 0, 90))
d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=(245, 245, 245, 255))
d.ellipse([CX - R, CY - R, CX + R, CY + R], outline=(20, 20, 20, 255), width=3 * S)


def pent(cx, cy, r, rot):
    return [(cx + r * math.cos(rot + i * 2 * math.pi / 5),
             cy + r * math.sin(rot + i * 2 * math.pi / 5)) for i in range(5)]


# center pentagon + 5 edge pentagons with connecting seams
d.polygon(pent(CX, CY, 0.38 * R, -math.pi / 2), fill=(25, 25, 25, 255))
for i in range(5):
    ang = -math.pi / 2 + i * 2 * math.pi / 5
    ex, ey = CX + 0.95 * R * math.cos(ang), CY + 0.95 * R * math.sin(ang)
    # clip edge pentagons to the ball circle via mask-free trick: draw then re-outline
    d.polygon(pent(ex, ey, 0.34 * R, ang + math.pi / 5), fill=(25, 25, 25, 255))
    sx, sy = CX + 0.38 * R * math.cos(ang), CY + 0.38 * R * math.sin(ang)
    d.line([sx, sy, ex, ey], fill=(25, 25, 25, 255), width=2 * S)

# erase anything outside the ball, redraw outline
mask = Image.new("L", img.size, 0)
md = ImageDraw.Draw(mask)
md.ellipse([CX - R, CY - R, CX + R, CY + R], fill=255)
shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.ellipse([CX - R - 10*S, CY - R - 6*S, CX + R + 10*S, CY + R + 14*S], fill=(0, 0, 0, 90))
ball = Image.composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0)), mask)
out = Image.alpha_composite(shadow, ball)
od = ImageDraw.Draw(out)
od.ellipse([CX - R, CY - R, CX + R, CY + R], outline=(20, 20, 20, 255), width=3 * S)
out = out.resize((1080, 1920), Image.LANCZOS)
out.save("build/ball_logo.png")
print("ball_logo.png")
