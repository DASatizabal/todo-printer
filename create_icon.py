"""
Generate a Todo Printer app icon (.ico).
Run once: python create_icon.py
Requires: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

SIZES = [16, 32, 48, 64, 128, 256]
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_printer.ico")


def draw_icon(size):
    """Draw a bold thermal printer icon - dark printer body with receipt coming out."""
    # Use supersampling for smooth edges
    ss = 4
    s = size * ss
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # -- Color palette --
    bg_dark = (30, 30, 40)          # near-black background circle
    printer_body = (55, 60, 75)     # dark slate printer
    printer_top = (70, 75, 92)      # slightly lighter top face
    printer_accent = (90, 95, 115)  # edge highlight
    receipt_white = (252, 250, 245)  # warm white receipt paper
    receipt_shadow = (220, 215, 205)
    green = (52, 211, 110)          # vibrant green check
    green_dark = (34, 180, 85)
    orange = (255, 160, 40)         # warm accent for the feed slot

    pad = s * 0.04  # tiny padding

    # -- Background circle (filled, acts as app icon bg) --
    draw.ellipse([pad, pad, s - pad, s - pad], fill=bg_dark)

    # -- Printer body (bottom 55% of icon) --
    px1 = s * 0.12
    px2 = s * 0.88
    py1 = s * 0.42
    py2 = s * 0.82
    r = s * 0.06

    # Body shadow
    draw.rounded_rectangle([px1 + s*0.02, py1 + s*0.02, px2 + s*0.02, py2 + s*0.02],
                           radius=r, fill=(0, 0, 0, 80))
    # Body
    draw.rounded_rectangle([px1, py1, px2, py2], radius=r, fill=printer_body)
    # Top face (slightly lighter strip)
    draw.rounded_rectangle([px1, py1, px2, py1 + s*0.12], radius=r, fill=printer_top)
    # Paper feed slot (orange accent line)
    slot_y = py1 + s * 0.04
    slot_h = s * 0.035
    draw.rounded_rectangle([px1 + s*0.18, slot_y, px2 - s*0.18, slot_y + slot_h],
                           radius=slot_h/2, fill=orange)

    # Subtle edge highlights
    draw.line([(px1 + r, py1), (px2 - r, py1)], fill=printer_accent, width=max(1, int(s * 0.01)))

    # -- Small indicator light (green dot on printer) --
    light_x = px2 - s * 0.18
    light_y = py1 + s * 0.08
    light_r = s * 0.025
    draw.ellipse([light_x - light_r, light_y - light_r,
                  light_x + light_r, light_y + light_r], fill=green)

    # -- Receipt paper (coming out the top of the printer) --
    rw = s * 0.44  # receipt width
    rx1 = s * 0.5 - rw / 2
    rx2 = s * 0.5 + rw / 2
    ry1 = s * 0.10  # top of receipt
    ry2 = py1 + s * 0.06  # overlaps into the printer slot

    # Receipt shadow
    draw.rounded_rectangle([rx1 + s*0.015, ry1 + s*0.01, rx2 + s*0.015, ry2],
                           radius=s*0.02, fill=(0, 0, 0, 50))
    # Receipt paper
    draw.rounded_rectangle([rx1, ry1, rx2, ry2], radius=s*0.02, fill=receipt_white)

    # -- Zigzag torn edge at top of receipt --
    teeth = max(4, int(size * 0.35))
    tooth_w = rw / teeth
    tooth_h = s * 0.03
    for i in range(teeth):
        tx1 = rx1 + i * tooth_w
        tx2 = tx1 + tooth_w / 2
        tx3 = tx1 + tooth_w
        # Cut into the receipt top with background color triangles
        draw.polygon([(tx1, ry1), (tx2, ry1 + tooth_h), (tx3, ry1)], fill=bg_dark)

    # -- Task lines on receipt --
    line_area_top = ry1 + s * 0.07
    line_area_bot = ry2 - s * 0.04
    num_lines = 3
    line_spacing = (line_area_bot - line_area_top) / (num_lines + 0.5)
    line_thickness = max(1, int(s * 0.018))
    cb_size = s * 0.035

    for i in range(num_lines):
        ly = line_area_top + (i + 0.5) * line_spacing
        lx1 = rx1 + s * 0.05
        lx2 = rx2 - s * 0.05

        # Checkbox
        cb_x = lx1
        cb_y = ly - cb_size / 2

        if i == 0:
            # First task: checked (green fill + checkmark)
            draw.rounded_rectangle([cb_x, cb_y, cb_x + cb_size, cb_y + cb_size],
                                   radius=s*0.008, fill=green)
            # Checkmark
            ck_w = max(1, int(s * 0.014))
            draw.line([(cb_x + cb_size*0.2, ly),
                       (cb_x + cb_size*0.45, ly + cb_size*0.3)],
                      fill=(255, 255, 255), width=ck_w)
            draw.line([(cb_x + cb_size*0.45, ly + cb_size*0.3),
                       (cb_x + cb_size*0.8, ly - cb_size*0.2)],
                      fill=(255, 255, 255), width=ck_w)
            # Strikethrough line (completed task)
            task_lx = cb_x + cb_size + s * 0.02
            line_len = (lx2 - task_lx) * 0.85
            draw.line([(task_lx, ly), (task_lx + line_len, ly)],
                      fill=(180, 175, 165), width=line_thickness)
        else:
            # Unchecked box
            draw.rounded_rectangle([cb_x, cb_y, cb_x + cb_size, cb_y + cb_size],
                                   radius=s*0.008, outline=(180, 175, 160), width=max(1, int(s*0.01)))
            # Task line
            task_lx = cb_x + cb_size + s * 0.02
            line_len = (lx2 - task_lx) * (0.9 - i * 0.15)
            draw.line([(task_lx, ly), (task_lx + line_len, ly)],
                      fill=(100, 95, 85), width=line_thickness)

    # -- Big green checkmark badge (bottom-right corner, overlapping printer) --
    badge_r = s * 0.15
    badge_cx = px2 - s * 0.06
    badge_cy = py2 - s * 0.06

    # Badge shadow
    draw.ellipse([badge_cx - badge_r + s*0.01, badge_cy - badge_r + s*0.015,
                  badge_cx + badge_r + s*0.01, badge_cy + badge_r + s*0.015],
                 fill=(0, 0, 0, 90))
    # Badge circle
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                  badge_cx + badge_r, badge_cy + badge_r],
                 fill=green)
    # White border
    draw.ellipse([badge_cx - badge_r, badge_cy - badge_r,
                  badge_cx + badge_r, badge_cy + badge_r],
                 outline=(255, 255, 255, 200), width=max(1, int(s * 0.015)))
    # Checkmark in badge
    ck_w = max(2, int(s * 0.03))
    draw.line([(badge_cx - badge_r*0.45, badge_cy + badge_r*0.05),
               (badge_cx - badge_r*0.05, badge_cy + badge_r*0.4)],
              fill=(255, 255, 255), width=ck_w)
    draw.line([(badge_cx - badge_r*0.05, badge_cy + badge_r*0.4),
               (badge_cx + badge_r*0.45, badge_cy - badge_r*0.3)],
              fill=(255, 255, 255), width=ck_w)

    # Downsample back to target size with high-quality resampling
    img = img.resize((size, size), Image.LANCZOS)

    # Flatten onto solid background (Windows shortcuts don't render alpha well)
    flat = Image.new("RGB", (size, size), bg_dark)
    flat.paste(img, mask=img.split()[3])  # use alpha as mask
    return flat


def main():
    images = [draw_icon(s) for s in SIZES]
    images[-1].save(OUTPUT, format="ICO", sizes=[(s, s) for s in SIZES], append_images=images[:-1])
    print(f"Icon saved to {OUTPUT}")


if __name__ == "__main__":
    main()
