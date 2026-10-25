"""Export key frames (one per script line, mid-line and end-of-line) for visual checking."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
VID = Path(__file__).parent
D = json.loads((VID / "timeline.json").read_text())
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
times = [L["end"] - 0.05 for L in D["lines"]]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome-stable", args=["--no-sandbox"])
    pg = b.new_page(viewport=dict(width=1920, height=1080))
    pg.goto(f"file://{VID / 'index.html'}"); pg.evaluate("window.ready")
    for i, t in enumerate(times):
        pg.evaluate(f"window.seek({t})"); pg.screenshot(path=str(out / f"k{i:02d}.png"))
    b.close()
print(len(times), "frames")
