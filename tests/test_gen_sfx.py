import os
import sys
import wave
import subprocess
import pytest

TOOLS_DIR = os.path.join(os.path.dirname(__file__), '..', 'tools')
GEN_SFX = os.path.join(TOOLS_DIR, 'gen_sfx.py')
PYTHON = os.path.expanduser("~/.hermes/hermes-agent/venv/bin/python3")
EXPECTED = ['footstep.wav', 'alert.wav', 'clear.wav', 'caught.wav']


def test_gen_sfx_creates_all_files(tmp_path):
    subprocess.run([PYTHON, GEN_SFX, '--output', str(tmp_path)], check=True)
    for name in EXPECTED:
        assert (tmp_path / name).exists(), f"Missing {name}"


def test_wav_files_are_valid(tmp_path):
    subprocess.run([PYTHON, GEN_SFX, '--output', str(tmp_path)], check=True)
    for name in EXPECTED:
        with wave.open(str(tmp_path / name), 'r') as w:
            assert w.getnchannels() == 1, f"{name}: expected mono"
            assert w.getframerate() == 22050, f"{name}: expected 22050 Hz"
            assert w.getnframes() > 0, f"{name}: no audio frames"


def test_wav_durations_are_short(tmp_path):
    subprocess.run([PYTHON, GEN_SFX, '--output', str(tmp_path)], check=True)
    for name in EXPECTED:
        with wave.open(str(tmp_path / name), 'r') as w:
            duration = w.getnframes() / w.getframerate()
            assert duration <= 1.5, f"{name}: {duration:.2f}s exceeds 1.5s"
