#!/usr/bin/env python3
"""
Sprite generator for Ghost Protocol.
Usage: python3 gen_sprites.py --output /path/to/sprites/

Generates 16x16 pixel art sprites using the cyberpunk palette.
Outputs: android_ss.png (128x32 sprite sheet), drone.png, floor_tile.png,
         wall_tile.png, exit_door.png — all RGBA PNGs.
"""
import argparse
import os
from PIL import Image, ImageDraw

BG        = (13,  8, 32,   0)   # transparent bg
FLOOR     = (26, 15, 48, 255)
WALL      = (10, 15, 26, 255)
CYAN      = (0, 255, 255, 255)
CYAN_DIM  = (0, 170, 200, 255)
AMBER     = (255, 107, 53, 255)
RED       = (255, 34,  68, 255)
GREY      = (64,  64,  96, 255)
WHITE     = (224, 232, 240, 255)
DARK      = (6,   4,  16, 255)
# Android palette
A_BODY    = (30,  45,  61, 255)   # main body dark blue-gray
A_SEAM    = (50,  75, 100, 255)   # panel seam lines
A_ARM     = (38,  56,  76, 255)   # arm segments
A_OUT     = (10,  15,  24, 255)   # near-black outline
# Drone palette
D_BODY    = (26,  26,  46, 255)   # drone body dark navy
D_HI      = (44,  44,  74, 255)   # body bevel highlight
D_SH      = (14,  14,  26, 255)   # body bevel shadow
D_ROTOR   = (38,  38,  66, 255)   # rotor disc
D_ROTOR_C = (62,  62,  98, 255)   # rotor center
D_ARM     = (32,  32,  56, 255)   # arm struts
D_WARN    = (255, 102,   0, 255)  # amber warning light
D_CAM     = (8,    8,  18, 255)   # camera housing
D_LENS    = (160, 160, 255, 255)  # lens highlight pixel


def new_sprite():
    return Image.new("RGBA", (16, 16), (0, 0, 0, 0))


def draw_android_frame(direction: str, walk_frame: int) -> Image.Image:
    img = new_sprite()

    def px(x, y, c):
        if 0 <= x <= 15 and 0 <= y <= 15:
            img.putpixel((x, y), c)

    if direction == "S":
        # -- Helmet --
        for x in range(5, 11):
            for y in range(0, 2):
                px(x, y, A_BODY)
        # Visor band: row 1, cols 4-11 (bright), row 2 (dim)
        for x in range(4, 12):
            px(x, 1, CYAN)
            px(x, 2, CYAN_DIM)
        # Chin
        for x in range(5, 11):
            px(x, 3, A_BODY)
        # -- Shoulders + torso --
        for x in range(4, 12):
            px(x, 4, A_BODY)          # shoulder width
        for y in range(5, 11):
            for x in range(5, 11):
                px(x, y, A_BODY)
        # Arms
        for y in range(5, 9):
            px(3, y, A_ARM); px(4, y, A_ARM)
            px(11, y, A_ARM); px(12, y, A_ARM)
        # Panel seams
        for x in range(5, 11):
            px(x, 8, A_SEAM)          # horizontal seam
        px(7, 6, A_SEAM); px(7, 7, A_SEAM); px(7, 9, A_SEAM)
        # Chest core (overrides seam)
        px(7, 5, CYAN); px(8, 5, CYAN_DIM)
        # -- Legs --
        if walk_frame == 0:
            for y in range(11, 16):
                px(5, y, A_BODY); px(6, y, A_BODY)
                px(9, y, A_BODY); px(10, y, A_BODY)
        else:
            for y in range(10, 15):    # left leg forward
                px(5, y, A_BODY); px(6, y, A_BODY)
            for y in range(12, 16):    # right leg back
                px(9, y, A_BODY); px(10, y, A_BODY)

    elif direction == "N":
        # -- Back of helmet --
        for x in range(5, 11):
            for y in range(0, 4):
                px(x, y, A_BODY)
        # Back panel ridge
        for x in range(5, 11):
            px(x, 2, A_SEAM)
        # -- Shoulders + torso (same as S) --
        for x in range(4, 12):
            px(x, 4, A_BODY)
        for y in range(5, 11):
            for x in range(5, 11):
                px(x, y, A_BODY)
        for y in range(5, 9):
            px(3, y, A_ARM); px(4, y, A_ARM)
            px(11, y, A_ARM); px(12, y, A_ARM)
        # Back panel lines (vertical seam + horizontal)
        for y in range(5, 11):
            px(8, y, A_SEAM)
        for x in range(5, 11):
            px(x, 7, A_SEAM)
        # -- Legs --
        if walk_frame == 0:
            for y in range(11, 16):
                px(5, y, A_BODY); px(6, y, A_BODY)
                px(9, y, A_BODY); px(10, y, A_BODY)
        else:
            for y in range(10, 15):
                px(5, y, A_BODY); px(6, y, A_BODY)
            for y in range(12, 16):
                px(9, y, A_BODY); px(10, y, A_BODY)

    elif direction in ("E", "W"):
        flip = (direction == "W")
        def fpx(x, y, c):
            px(15 - x if flip else x, y, c)

        # -- Profile helmet --
        for x in range(6, 11):
            for y in range(0, 4):
                fpx(x, y, A_BODY)
        # Visor: single column on face side
        for y in range(1, 3):
            fpx(10, y, CYAN)
        # -- Profile body --
        for y in range(4, 11):
            for x in range(6, 11):
                fpx(x, y, A_BODY)
        # Front arm (visible, forward)
        for y in range(5, 9):
            fpx(4, y, A_ARM); fpx(5, y, A_ARM)
        # Panel seam (vertical on profile)
        for y in range(4, 11):
            fpx(8, y, A_SEAM)
        fpx(8, 5, CYAN)    # chest core
        # -- Legs profile --
        if walk_frame == 0:
            for y in range(11, 16):
                fpx(7, y, A_BODY); fpx(8, y, A_BODY)
        else:
            for y in range(10, 15):   # front leg
                fpx(7, y, A_BODY)
            for y in range(12, 16):   # back leg
                fpx(9, y, A_BODY)

    return img


def make_android_spritesheet() -> Image.Image:
    sheet = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    for col, direction in enumerate(["S", "N", "E", "W"]):
        for walk in range(2):
            frame = draw_android_frame(direction, walk)
            sheet.paste(frame, (col * 32 + walk * 16, 0))
    return sheet


def make_drone() -> Image.Image:
    img = new_sprite()

    def px(x, y, c):
        if 0 <= x <= 15 and 0 <= y <= 15:
            img.putpixel((x, y), c)

    # Rotor discs (3x3 at each corner)
    for (cx, cy) in [(1, 1), (14, 1), (1, 14), (14, 14)]:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                px(cx + dx, cy + dy, D_ROTOR)
        px(cx, cy, D_ROTOR_C)    # bright center pixel

    # Arm struts (diagonal, rotor to body corner)
    # Top-left rotor (1,1) to body corner (5,5)
    px(3, 3, D_ARM); px(4, 4, D_ARM)
    # Top-right rotor (14,1) to body corner (10,5)
    px(12, 3, D_ARM); px(11, 4, D_ARM)
    # Bottom-left rotor (1,14) to body corner (5,10)
    px(3, 12, D_ARM); px(4, 11, D_ARM)
    # Bottom-right rotor (14,14) to body corner (10,10)
    px(12, 12, D_ARM); px(11, 11, D_ARM)

    # Central body (6x6: x=5..10, y=5..10)
    for x in range(5, 11):
        for y in range(5, 11):
            px(x, y, D_BODY)
    # Top bevel (highlight)
    for x in range(5, 11):
        px(x, 5, D_HI)
    # Left bevel (highlight)
    for y in range(5, 11):
        px(5, y, D_HI)
    # Bottom bevel (shadow)
    for x in range(5, 11):
        px(x, 10, D_SH)
    # Right bevel (shadow)
    for y in range(5, 11):
        px(10, y, D_SH)

    # Warning light (2px amber on top-center of body)
    px(7, 5, D_WARN); px(8, 5, D_WARN)

    # Camera on RIGHT side (facing right = forward)
    # 2x3 housing jutting right of body
    for y in range(6, 9):
        px(11, y, D_CAM)
        px(12, y, D_CAM)
    # Lens highlight (single bright pixel on front face)
    px(12, 7, D_LENS)

    return img
def make_floor_tile() -> Image.Image:
    img = new_sprite()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 15], fill=FLOOR)
    grid = (30, 20, 55, 255)
    d.line([0, 0, 15, 0], fill=grid)
    d.line([0, 0, 0, 15], fill=grid)
    d.line([8, 0, 8, 15], fill=(20, 12, 40, 255))
    d.line([0, 8, 15, 8], fill=(20, 12, 40, 255))
    return img


def make_wall_tile() -> Image.Image:
    img = new_sprite()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 15], fill=WALL)
    d.rectangle([0, 0, 15, 15], outline=DARK)
    d.line([1, 1, 14, 1], fill=GREY)
    d.line([1, 1, 1, 14], fill=GREY)
    return img


def make_exit_door() -> Image.Image:
    img = new_sprite()
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 15], fill=FLOOR)
    d.rectangle([2, 2, 13, 14], outline=CYAN)
    d.rectangle([3, 3, 12, 13], fill=(10, 30, 50, 255))
    d.polygon([(6, 8), (10, 6), (10, 10)], fill=CYAN)
    return img


def main():
    parser = argparse.ArgumentParser(description="Generate Ghost Protocol sprites")
    parser.add_argument("--output", required=True, help="Output directory for PNG files")
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    sprites = {
        "android_ss.png": make_android_spritesheet(),
        "drone.png":      make_drone(),
        "floor_tile.png": make_floor_tile(),
        "wall_tile.png":  make_wall_tile(),
        "exit_door.png":  make_exit_door(),
    }
    for filename, img in sprites.items():
        path = os.path.join(args.output, filename)
        img.save(path)
        print(f"  wrote {path} ({img.size[0]}x{img.size[1]})")
    print(f"Generated {len(sprites)} sprites in {args.output}")


if __name__ == "__main__":
    main()
