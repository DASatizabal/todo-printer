"""
Generate a Todo Printer app icon (.ico).
Run once: python create_icon.py
Requires: pip install Pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

SIZES = [16, 32, 48, 64, 128, 256]
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo_printer.ico")


def draw_icon(size):
    """Draw a receipt/ticket icon with a checkmark."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Receipt background (white rounded rect with slight shadow)
    margin = size // 8
    receipt_top = margin
    receipt_bottom = size - margin
    receipt_left = size // 5
    receipt_right = size - size // 5

    # Shadow
    shadow_offset = max(1, size // 32)
    draw.rounded_rectangle(
        [receipt_left + shadow_offset, receipt_top + shadow_offset,
         receipt_right + shadow_offset, receipt_bottom + shadow_offset],
        radius=size // 16,
        fill=(0, 0, 0, 60),
    )

    # Receipt body
    draw.rounded_rectangle(
        [receipt_left, receipt_top, receipt_right, receipt_bottom],
        radius=size // 16,
        fill=(255, 255, 255, 255),
        outline=(80, 80, 80, 255),
        width=max(1, size // 32),
    )

    # Zigzag bottom edge (receipt tear)
    zigzag_y = receipt_bottom - size // 10
    teeth = max(3, size // 12)
    tooth_width = (receipt_right - receipt_left) / teeth
    for i in range(teeth):
        x1 = receipt_left + i * tooth_width
        x2 = x1 + tooth_width / 2
        x3 = x1 + tooth_width
        draw.polygon(
            [(x1, zigzag_y), (x2, zigzag_y + size // 12), (x3, zigzag_y)],
            fill=(255, 255, 255, 255),
        )

    # "Lines" on receipt (task lines)
    line_y_start = receipt_top + size // 4
    line_spacing = size // 8
    line_left = receipt_left + size // 8
    line_right = receipt_right - size // 8
    line_width = max(1, size // 24)

    for i in range(3):
        y = line_y_start + i * line_spacing
        if y < zigzag_y - size // 12:
            # Small checkbox
            cb_size = max(2, size // 16)
            draw.rectangle(
                [line_left, y - cb_size // 2, line_left + cb_size, y + cb_size // 2],
                outline=(100, 100, 100, 255),
                width=max(1, size // 64),
            )
            # Line
            draw.line(
                [(line_left + cb_size + max(2, size // 20), y),
                 (line_right - (i * size // 10), y)],
                fill=(160, 160, 160, 255),
                width=line_width,
            )

    # Green checkmark overlay (bottom-right)
    check_center_x = receipt_right - size // 8
    check_center_y = receipt_bottom - size // 5
    check_r = size // 5

    draw.ellipse(
        [check_center_x - check_r, check_center_y - check_r,
         check_center_x + check_r, check_center_y + check_r],
        fill=(34, 197, 94, 240),
    )

    # Checkmark
    cw = max(1, size // 20)
    cx, cy = check_center_x, check_center_y
    draw.line(
        [(cx - check_r * 0.4, cy), (cx - check_r * 0.05, cy + check_r * 0.35)],
        fill=(255, 255, 255, 255), width=cw,
    )
    draw.line(
        [(cx - check_r * 0.05, cy + check_r * 0.35), (cx + check_r * 0.4, cy - check_r * 0.3)],
        fill=(255, 255, 255, 255), width=cw,
    )

    return img


def main():
    images = [draw_icon(s) for s in SIZES]
    images[0].save(OUTPUT, format="ICO", sizes=[(s, s) for s in SIZES], append_images=images[1:])
    print(f"Icon saved to {OUTPUT}")


if __name__ == "__main__":
    main()
