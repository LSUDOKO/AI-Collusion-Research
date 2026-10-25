"""Narration track (clips placed at their timeline start) + quiet original synthesized background music (no samples,
no licensing issues), ducked under speech. Writes video/mix.wav."""
import json
import subprocess
from pathlib import Path

import numpy as np

VID = Path(__file__).parent
SR = 48000
D = json.loads((VID / "timeline.json").read_text())
T = D["T_END"]
N = int(T * SR)


def load(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


voice = np.zeros(N, np.float32)
for L in D["lines"]:
    a = load(VID / "audio" / L["file"]); s = int(L["t"] * SR)
    voice[s:s + len(a)] += a[: max(0, N - s)]

# music: slow Am-F-C-G pad (detuned sines, soft attack) + sparse plucked arpeggio, 84 bpm
t = np.arange(N) / SR
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]   # Am F C G
bar = 4 * 60 / 84
music = np.zeros(N, np.float32)
for k in range(int(T / bar) + 1):
    s, e = int(k * bar * SR), min(N, int((k + 1.15) * bar * SR))
    if s >= N:
        break
    tt = t[s:e] - k * bar
    env = np.minimum(1, tt / 1.2) * np.minimum(1, np.maximum(0, (bar * 1.15 - tt) / 1.0))
    ch = prog[k % 4]
    sig = sum(np.sin(2 * np.pi * mid(m) * tt) + 0.6 * np.sin(2 * np.pi * mid(m) * 1.003 * tt) for m in ch)
    sig += 0.5 * np.sin(2 * np.pi * mid(ch[0] - 12) * tt)
    music[s:e] += 0.05 * env * sig
    for j in range(8):                                   # arpeggio eighth notes
        st = int((k * bar + j * bar / 8) * SR)
        if st >= N:
            break
        m = ch[j % 3] + 12
        ln = min(N - st, int(0.9 * SR)); tn = np.arange(ln) / SR
        music[st:st + ln] += 0.035 * np.exp(-tn * 4.5) * np.sin(2 * np.pi * mid(m) * tn) * (1 - np.exp(-tn * 200))
# gentle low-pass (one-pole) to soften
y = np.zeros_like(music); a = 0.18
for i in range(1, N):
    y[i] = y[i - 1] + a * (music[i] - y[i - 1])
music = y
# fade in/out, duck under narration
music *= np.minimum(1, t / 2.5) * np.minimum(1, (T - t) / 3.0)
win = int(0.25 * SR)
env = np.convolve(np.abs(voice), np.ones(win) / win, mode="same")
duck = 1 - 0.55 * np.clip(env / (env.max() * 0.15 + 1e-9), 0, 1)
music *= duck
music *= 0.12 / (np.abs(music).max() + 1e-9)          # quiet bed, peak ~ -18 dBFS
voice *= 0.85 / (np.abs(voice).max() + 1e-9)
mix = np.clip(voice + music, -1, 1)
pcm = (mix * 32767).astype(np.int16).tobytes()
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", str(VID / "mix.wav")], input=pcm, check=True)
print("mix.wav", round(T, 1), "s")
