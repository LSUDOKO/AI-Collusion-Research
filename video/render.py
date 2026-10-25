"""Render index.html with Playwright at 60 sub-frames/s, blend pairs (ffmpeg tmix) to 30 fps for light motion blur,
then mux the narration+music mix. Output: video/Sting_Audits_explainer.mp4"""
import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

VID = Path(__file__).parent
D = json.loads((VID / "timeline.json").read_text())
SUB = 60
n = int(D["T_END"] * SUB)
silent = VID / "silent.mp4"
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(SUB), "-c:v", "mjpeg", "-i", "-",
                       "-vf", "tmix=frames=2,fps=30", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(silent)],
                      stdin=subprocess.PIPE)
t0 = time.time()
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome-stable", args=["--no-sandbox"])
    pg = b.new_page(viewport=dict(width=1920, height=1080))
    pg.goto(f"file://{VID / 'index.html'}"); pg.evaluate("window.ready")
    for i in range(n):
        pg.evaluate(f"window.seek({i / SUB:.4f})")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
        if i % 600 == 0:
            print(f"{i}/{n} frames, {time.time() - t0:.0f}s", flush=True)
    b.close()
ff.stdin.close(); ff.wait()
out = VID / "Sting_Audits_explainer.mp4"
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(silent), "-i", str(VID / "mix.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-shortest", "-movflags", "+faststart", str(out)], check=True)
print("done", out, f"{time.time() - t0:.0f}s")
