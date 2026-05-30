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

BG    = (13,  8, 32, 0)
FLOOR = (26, 15, 48, 255)
WALL  = (10, 15, 26, 255)
CYAN  = (0, 255, 255, 255)
AMBER = (255, 107, 53, 255)
RED   = (255, 34, 68, 255)
GREY  = (64, 64, 96, 255)
WHITE = (224, 232, 240, 255)
DARK  = (6,  4, 16, 255)


def new_sprite():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


def draw_android_frame(direction: str, walk_frame: int) -> Image.Image:
    img = new_sprite()
    d = ImageDraw.Draw(img)
    body_color = CYAN if walk_frame == 0 else (0, 200, 220, 255)
    d.rectangle([6, 5, 10, 13], fill=body_color)
    d.rectangle([5, 2, 11, 6], fill=GREY)
    if direction == 'S':
        d.point([(6, 4), (10, 4)], fill=CYAN)
    elif direction == 'N':
        d.point([(6, 3), (10, 3)], fill=CYAN)
    elif direction == 'E':
        d.point([(10, 4)], fill=CYAN)
    else:
        d.point([(6, 4)], fill=CYAN)
    if walk_frame == 0:
        d.rectangle([5, 13, 7, 15], fill=GREY)
        d.rectangle([9, 14, 11, 15], fill=GREY)
    else:
        d.rectangle([5, 14, 7, 15], fill=GREY)
        d.rectangle([9, 13, 11, 15], fill=GREY)
    d.point([(7, 7), (9, 9), (8, 11)], fill=AMBER)
    return img


def make_android_spritesheet() -> Image.Image:
    sheet = Image.new('RGBA', (128, 32), (0, 0, 0, 0))
    for col, direction in enumerate(['S', 'N', 'E', 'W']):
        for walk in range(2):
            frame = draw_android_frame(direction, walk)
            sheet.paste(frame, (col * 32 + walk * 16, 0))
    return sheet


def make_drone() -> Image.Image:
    img = new_sprite()
    d = ImageDraw.Draw(img)
    d.ellipse([1, 5, 15, 11], fill=DARK, outline=GREY)
    d.ellipse([6, 6, 10, 10], fill=RED)
    d.point([(8, 8)], fill=WHITE)
    d.line([8, 5, 8, 2], fill=GREY)
    d.point([(8, 1)], fill=RED)
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
    parser = argparse.ArgumentParser(description='Generate Ghost Protocol sprites')
    parser.add_argument('--output', required=True, help='Output directory for PNG files')
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    sprites = {
        'android_ss.png': make_android_spritesheet(),
        'drone.png':      make_drone(),
        'floor_tile.png': make_floor_tile(),
        'wall_tile.png':  make_wall_tile(),
        'exit_door.png':  make_exit_door(),
    }
    for filename, img in sprites.items():
        path = os.path.join(args.output, filename)
        img.save(path)
        print(f"  wrote {path} ({img.size[0]}x{img.size[1]})")
    print(f"Generated {len(sprites)} sprites in {args.output}")


if __name__ == '__main__':
    main()
