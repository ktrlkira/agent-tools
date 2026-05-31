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
    frame = gs.draw_android_frame(S, 0)
    assert frame.size == (16, 16)

def test_android_south_has_cyan_visor():
    frame = gs.draw_android_frame(S, 0)
    # Visor band is row y=1, cols x=4..11 — must be cyan
    visor_pixels = [frame.getpixel((x, 1)) for x in range(4, 12)]
    assert all(p == CYAN for p in visor_pixels), f"Visor not cyan: {visor_pixels}"

def test_android_south_has_chest_core():
    frame = gs.draw_android_frame(S, 0)
    # Chest core at (7, 5) must be cyan
    pixel = frame.getpixel((7, 5))
    assert pixel == CYAN, f"Chest core not cyan: {pixel}"

def test_android_south_has_warn_shoulder():
    frame = gs.draw_android_frame(S, 0)
    # Right shoulder warning light at (10, 4) must be warn orange
    pixel = frame.getpixel((10, 4))
    assert pixel == WARN, f"Shoulder warning light not orange: {pixel}"

def test_android_south_has_lens_eyes():
    frame = gs.draw_android_frame(S, 0)
    # Eyes at (5, 2) and (8, 2) must be lens blue
    left_eye = frame.getpixel((5, 2))
    right_eye = frame.getpixel((8, 2))
    assert left_eye == LENS, f"Left eye not lens blue: {left_eye}"
    assert right_eye == LENS, f"Right eye not lens blue: {right_eye}"

def test_android_frame_has_alpha_channel():
    frame = gs.draw_android_frame(N, 0)
    # All frames should have alpha channel for transparency
    assert frame.mode == RGBA, f"Frame mode is {frame.mode}, expected RGBA"
