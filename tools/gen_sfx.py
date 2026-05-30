#!/usr/bin/env python3
"""
SFX generator for Ghost Protocol.
Usage: python3 gen_sfx.py --output /path/to/audio/

Generates four 8-bit-style WAV files using Python stdlib only (wave + math).
  footstep.wav  50ms  — soft low thud
  alert.wav    400ms  — rising alarm sweep (300Hz->800Hz)
  clear.wav    500ms  — C major arpeggio chime
  caught.wav   600ms  — descending noise burst (600Hz->100Hz)
"""
import argparse
import math
import os
import struct
import wave

SAMPLE_RATE = 22050
AMPLITUDE = 16000


def sine(freq: float, t: float) -> float:
    return math.sin(2 * math.pi * freq * t)


def noise(t: float) -> float:
    import random
    return random.uniform(-1, 1)


def write_wav(path: str, frames: list) -> None:
    with wave.open(path, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        data = struct.pack(f'<{len(frames)}h', *frames)
        w.writeframes(data)


def make_footstep() -> list:
    n = int(SAMPLE_RATE * 0.05)
    return [
        max(-32767, min(32767, int(
            (sine(80, i / SAMPLE_RATE) * 0.6 + noise(i) * 0.4) * (1.0 - i / n) * AMPLITUDE
        ))) for i in range(n)
    ]


def make_alert() -> list:
    n = int(SAMPLE_RATE * 0.4)
    frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 300 + (800 - 300) * (i / n)
        pulse = 1.0 if int(i / (SAMPLE_RATE * 0.05)) % 2 == 0 else 0.3
        frames.append(max(-32767, min(32767, int(sine(freq, t) * pulse * AMPLITUDE))))
    return frames


def make_clear() -> list:
    note_dur = int(SAMPLE_RATE * 0.12)
    frames = []
    for freq in [523, 659, 784, 1047]:
        for i in range(note_dur):
            t = len(frames) / SAMPLE_RATE
            env = 1.0 - (i / note_dur) * 0.5
            frames.append(max(-32767, min(32767, int(sine(freq, t) * env * AMPLITUDE * 0.7))))
    total = int(SAMPLE_RATE * 0.5)
    frames.extend([0] * (total - len(frames)))
    return frames


def make_caught() -> list:
    n = int(SAMPLE_RATE * 0.6)
    frames = []
    for i in range(n):
        t = i / SAMPLE_RATE
        freq = 600 - (600 - 100) * (i / n)
        env = 1.0 - (i / n) * 0.7
        frames.append(max(-32767, min(32767, int(
            (sine(freq, t) * 0.7 + noise(t) * 0.3) * env * AMPLITUDE
        ))))
    return frames


def main():
    parser = argparse.ArgumentParser(description='Generate Ghost Protocol SFX')
    parser.add_argument('--output', required=True, help='Output directory for WAV files')
    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)
    sfx = {
        'footstep.wav': make_footstep(),
        'alert.wav':    make_alert(),
        'clear.wav':    make_clear(),
        'caught.wav':   make_caught(),
    }
    for filename, frames in sfx.items():
        path = os.path.join(args.output, filename)
        write_wav(path, frames)
        print(f"  wrote {path} ({len(frames)/SAMPLE_RATE:.2f}s)")
    print(f"Generated {len(sfx)} SFX files in {args.output}")


if __name__ == '__main__':
    main()
