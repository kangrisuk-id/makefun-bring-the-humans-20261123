#!/usr/bin/env python3
"""Synthesise the ad's music bed from scratch (no samples, no downloads).

A 28-second, 122 BPM loop in A minor: a pulsing bass, a bright pluck
arpeggio, soft kick/hat ticks and a gentle pad, written as a 16-bit WAV
with numpy. Everything is generated in this session, so the track is ours
to use in the entry.
"""
import numpy as np, wave, os

SR = 44100
DUR = 28.0
N = int(SR * DUR)
t = np.arange(N) / SR
BPM = 122.0
BEAT = 60.0 / BPM

def env(length, attack=0.005, decay=0.18):
    n = int(length * SR)
    e = np.exp(-np.arange(n) / (decay * SR))
    a = int(attack * SR)
    if a > 0:
        e[:a] *= np.linspace(0, 1, a)
    return e

def add(dst, start, wave_):
    i = int(start * SR)
    j = min(N, i + len(wave_))
    if j > i:
        dst[i:j] += wave_[: j - i]

mix = np.zeros(N)

# chord roots: Am - F - C - G (one bar each, looped)
bars = [110.00, 87.31, 130.81, 98.00]          # A2 F2 C3 G2
arp_notes = [440.00, 523.25, 659.25, 523.25,  # A4 C5 E5 C5
             349.23, 440.00, 523.25, 440.00,  # F4 A4 C5 A4
             523.25, 659.25, 783.99, 659.25,  # C5 E5 G5 E5
             392.00, 493.88, 587.33, 493.88]  # G4 B4 D5 B4
bar_len = 4 * BEAT
total_bars = int(DUR / bar_len) + 1

for b in range(total_bars):
    root = bars[b % 4]
    t0 = b * bar_len
    # bass: eighth-note pulse
    for k in range(8):
        bt = t0 + k * BEAT / 2
        seg = np.sin(2 * np.pi * root * np.arange(int(BEAT / 2 * SR)) / SR)
        add(mix, bt, 0.30 * seg * env(BEAT / 2, decay=0.10))
    # kick on each beat
    for k in range(4):
        kt = t0 + k * BEAT
        n = int(0.12 * SR)
        freq = 120 * np.exp(-np.arange(n) / (0.03 * SR)) + 45
        phase = np.cumsum(freq) / SR
        add(mix, kt, 0.5 * np.sin(2 * np.pi * phase) * env(0.12, decay=0.05))
    # hats on off-beats
    rng = np.random.default_rng(7 + b)
    for k in range(4):
        ht = t0 + (k + 0.5) * BEAT
        n = int(0.05 * SR)
        noise = rng.standard_normal(n) * np.exp(-np.arange(n) / (0.012 * SR))
        add(mix, ht, 0.10 * noise)
    # pluck arpeggio: 16ths
    for k in range(16):
        pt = t0 + k * BEAT / 4
        f = arp_notes[(b % 4) * 4 + (k % 4)] * (2 if k % 8 == 7 else 1)
        n = int(BEAT / 4 * SR)
        seg = np.sin(2 * np.pi * f * np.arange(n) / SR) + 0.4 * np.sin(4 * np.pi * f * np.arange(n) / SR)
        add(mix, pt, 0.16 * seg * env(BEAT / 4, decay=0.07))
    # pad: whole-bar chord wash
    n = int(bar_len * SR)
    chord = [root * 2, root * 2.5, root * 3]
    pad = sum(np.sin(2 * np.pi * f * np.arange(n) / SR) for f in chord) / 3
    add(mix, t0, 0.05 * pad * np.minimum(1, np.arange(n) / (0.4 * SR)))

# overall shape: quick fade in, fade out over the end-card hold
mix *= np.minimum(1, t / 0.15)
mix *= np.where(t > DUR - 1.6, np.maximum(0, (DUR - t) / 1.6), 1.0)
mix = np.clip(mix, -0.9, 0.9)
pcm = (mix * 32767 * 0.8).astype(np.int16)

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "music.wav")
with wave.open(out, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", out, DUR, "seconds")
