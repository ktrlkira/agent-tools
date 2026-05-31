#!/usr/bin/env python3
"""Tests for gen_sprites.py output dimensions and key pixel colors."""
import pytest
from PIL import Image
import gen_sprites as gs

CYAN     = (0, 255, 255, 255)
WARN     = (255, 102, 0, 255)
LENS     = (160, 160, 255, 255)

def test_android_spritesheet_size():
    sheet = gs.make_android_spritesheet()
    assert sheet.size == (128, 32), f"Expected 128x32, got {sheet.size}"

def test_android_frame_size():
    frame = gs.draw_android_frame('S', 0)
    assert frame.size == (16, 16)

def test_android_south_has_cyan_visor():
    frame = gs.draw_android_frame('S', 0)
    # Visor band is row y=1, cols x=4..11 -- must be cyan
    visor_pixels = [frame.getpixel((x, 1)) for x in range(4, 12)]
    assert all(p == CYAN for p in visor_pixels), f"Visor not cyan: {visor_pixels}"

def test_android_south_has_chest_core():
    frame = gs.draw_android_frame('S', 0)
    # Chest core at (7, 5) must be cyan
    assert frame.getpixel((7, 5)) == CYAN, "Chest core not cyan"

def test_android_all_frames_opaque_center():
    # Center pixels of the body should be opaque in all frames
    for direction in ['S', 'N', 'E', 'W']:
        for walk in [0, 1]:
            frame = gs.draw_android_frame(direction, walk)
            r, g, b, a = frame.getpixel((8, 6))
            assert a == 255, f"{direction} walk={walk} center pixel transparent"

def test_drone_size():
    img = gs.make_drone()
    assert img.size == (16, 16)

def test_drone_has_warning_light():
    img = gs.make_drone()
    warn_pixels = [img.getpixel((7, 5)), img.getpixel((8, 5))]
    assert any(p == WARN for p in warn_pixels), f"No warning light: {warn_pixels}"

def test_drone_has_camera_lens():
    img = gs.make_drone()
    assert img.getpixel((12, 7)) == LENS, "Camera lens pixel missing"

def test_drone_body_opaque():
    img = gs.make_drone()
    # Central body pixels must be opaque
    for x in range(5, 11):
        for y in range(5, 11):
            r, g, b, a = img.getpixel((x, y))
            assert a == 255, f"Body pixel ({x},{y}) transparent"
