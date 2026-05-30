import os
import sys
import subprocess
import pytest
from PIL import Image

TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tools')
GEN_SPRITES = os.path.join(TOOLS_DIR, 'gen_sprites.py')
PYTHON = os.path.expanduser("~/.hermes/hermes-agent/venv/bin/python3")


def test_gen_sprites_creates_all_files(tmp_path):
    subprocess.run([PYTHON, GEN_SPRITES, '--output', str(tmp_path)], check=True)
    for name in ['android_ss.png', 'drone.png', 'floor_tile.png', 'wall_tile.png', 'exit_door.png']:
        assert (tmp_path / name).exists(), f"Missing {name}"


def test_android_spritesheet_dimensions(tmp_path):
    subprocess.run([PYTHON, GEN_SPRITES, '--output', str(tmp_path)], check=True)
    img = Image.open(tmp_path / 'android_ss.png')
    assert img.size == (128, 32), f"Expected 128x32, got {img.size}"


def test_single_sprites_are_16x16(tmp_path):
    subprocess.run([PYTHON, GEN_SPRITES, '--output', str(tmp_path)], check=True)
    for name in ['drone.png', 'floor_tile.png', 'wall_tile.png', 'exit_door.png']:
        img = Image.open(tmp_path / name)
        assert img.size == (16, 16), f"{name}: expected 16x16, got {img.size}"


def test_sprites_have_alpha(tmp_path):
    subprocess.run([PYTHON, GEN_SPRITES, '--output', str(tmp_path)], check=True)
    img = Image.open(tmp_path / 'android_ss.png')
    assert img.mode == 'RGBA', f"Expected RGBA, got {img.mode}"
