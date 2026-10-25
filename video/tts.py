"""Generate one narration clip per script line with edge-tts (en-US-AriaNeural) and record per-word timings."""
import asyncio
import json
import subprocess
from pathlib import Path

import edge_tts

from script import LINES

VID = Path(__file__).parent
AUD = VID / "audio"
VOICE = "en-US-AriaNeural"


async def one(i, text):
    out = AUD / f"line{i:02d}.mp3"
    words = []
    c = edge_tts.Communicate(text, VOICE, rate="+4%", boundary="WordBoundary")
    with open(out, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append(dict(w=ch["text"], t=ch["offset"] / 1e7, d=ch["duration"] / 1e7))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(out)]))
    return dict(i=i, file=out.name, dur=dur, words=words)


async def main():
    AUD.mkdir(exist_ok=True)
    res = []
    for i, l in enumerate(LINES):
        res.append(await one(i, l["say"]))
        print(i, round(res[-1]["dur"], 2), len(res[-1]["words"]))
    (VID / "timing.json").write_text(json.dumps(res, indent=1))
    print("total", round(sum(r["dur"] for r in res), 1))


asyncio.run(main())
