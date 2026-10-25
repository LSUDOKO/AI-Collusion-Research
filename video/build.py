"""Build video/index.html: one fixed whiteboard diagram (world 3200x2000), a camera, and window.seek(t) that computes
every style from t (no CSS animations, no timers, no state between frames). Timing comes from timing.json (real TTS
lengths). Data values are read from results/tables so the drawing matches the paper."""
import html
import json
import math
import random
from pathlib import Path

from script import LINES

VID = Path(__file__).parent
REPO = VID.parent
TABLES = REPO / "results" / "tables"
GAP, LEAD = 0.45, 0.9           # pause between lines; start offset
CAM_T = 0.9                      # camera move duration

INK, RED, AMB, BLU, GRY, GRN = "#1d1d1f", "#c0392b", "#d68910", "#2471a3", "#6e6e73", "#1e8449"
FONT = "'Caveat', cursive"

kn = json.loads((TABLES / "key_numbers.json").read_text())["probe"]
acc = {o: kn["accept_by_offer"][o]["rate"] for o in ("S0", "S1", "S2", "S3")}
cfg = kn["config_scores"]
rho = json.loads((TABLES / "probe_extra.json").read_text())["rho_sting_vs_benign"]["rho"]
bym = json.loads((TABLES / "probe_extra.json").read_text())["by_model"]

rng = random.Random(7)
EL = {}      # id -> dict(type, svg, dur, tip?)


def wob(a=1.8):
    return rng.uniform(-a, a)


def rough_poly(pts, closed=False, a=1.8, seg=40):
    """Hand-drawn polyline: resample each segment and jitter perpendicular to it."""
    out = []
    P = pts + ([pts[0]] if closed else [])
    for (x1, y1), (x2, y2) in zip(P, P[1:]):
        L = math.hypot(x2 - x1, y2 - y1); n = max(2, int(L / seg))
        nx, ny = (-(y2 - y1) / (L or 1), (x2 - x1) / (L or 1))
        for k in range(n):
            f = k / n; j = wob(a) * math.sin(math.pi * f) if 0 < k else 0
            out.append((x1 + (x2 - x1) * f + nx * j, y1 + (y2 - y1) * f + ny * j))
    out.append(P[-1])
    d = f"M{out[0][0]:.1f},{out[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in out[1:])
    return d


def rough_rect(x, y, w, h, a=2.0):
    return rough_poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], closed=True, a=a)


def rough_circle(cx, cy, r, a=2.0, n=48, turns=1.04):
    pts = []
    for k in range(int(n * turns) + 1):
        th = -math.pi / 2 + 2 * math.pi * k / n
        rr = r + wob(a)
        pts.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    return f"M{pts[0][0]:.1f},{pts[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts[1:])


def arrow_d(x1, y1, x2, y2, bend=0.0, head=26):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    L = math.hypot(x2 - x1, y2 - y1); nx, ny = -(y2 - y1) / L, (x2 - x1) / L
    cx, cy = mx + nx * bend * L, my + ny * bend * L
    d = f"M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}"
    ang = math.atan2(y2 - cy, x2 - cx)
    for s in (+1, -1):
        hx, hy = x2 - head * math.cos(ang + s * 0.45), y2 - head * math.sin(ang + s * 0.45)
        d += f" M{x2:.1f},{y2:.1f} L{hx:.1f},{hy:.1f}"
    return d


def path(id, d, color=INK, w=5, dur=1.0, dash=None, fill="none"):
    extra = f" data-dash='{dash}'" if dash else ""
    EL[id] = dict(type="path", dur=dur, svg=f"<path id='{id}' d='{d}' fill='{fill}' stroke='{color}' stroke-width='{w}' "
                                          f"stroke-linecap='round' stroke-linejoin='round'{extra}/>")


def text(id, x, y, s, size=54, color=INK, anchor="start", weight=600, dur=None, rot=0):
    s_esc = html.escape(s)
    tr = f" transform='rotate({rot} {x} {y})'" if rot else ""
    EL[id] = dict(type="text", dur=dur or max(0.5, 0.055 * len(s)),
                  svg=f"<g{tr}><clipPath id='c_{id}'><rect id='r_{id}' x='0' y='0' width='0' height='0'/></clipPath>"
                      f"<text id='{id}' x='{x}' y='{y}' font-size='{size}' fill='{color}' text-anchor='{anchor}' font-weight='{weight}' "
                      f"clip-path='url(#c_{id})' font-family=\"{FONT}\">{s_esc}</text></g>")


def image(id, href, x, y, w, h, dur=1.6):
    EL[id] = dict(type="image", dur=dur, box=[x, y, w, h],
                  svg=f"<clipPath id='c_{id}'><rect id='r_{id}' x='{x}' y='{y}' width='0' height='{h}'/></clipPath>"
                      f"<rect x='{x - 6}' y='{y - 6}' width='{w + 12}' height='{h + 12}' fill='none' stroke='#bbb' stroke-width='2' clip-path='url(#c_{id})'/>"
                      f"<image id='{id}' href='{href}' x='{x}' y='{y}' width='{w}' height='{h}' clip-path='url(#c_{id})'/>")


def grow(id, x, y, w, h, color, dur=0.9):
    """Bar growing up from its baseline (y+h)."""
    EL[id] = dict(type="grow", dur=dur, box=[x, y, w, h],
                  svg=f"<rect id='{id}' x='{x}' y='{y + h}' width='{w}' height='0' fill='{color}' fill-opacity='0.85'/>"
                      f"<path d='{rough_rect(x, y, w, h, a=1.2)}' fill='none' stroke='{INK}' stroke-width='3' id='{id}_o' opacity='0'/>")


def dots(id, pts, dur=2.2):
    g = "".join(f"<g class='dot' data-k='{k}' transform='translate({x:.1f},{y:.1f})'><circle r='0' fill='{c}' stroke='{INK}' stroke-width='3'/></g>"
                for k, (x, y, c) in enumerate(pts))
    EL[id] = dict(type="dots", dur=dur, n=len(pts), svg=f"<g id='{id}'>{g}</g>")


# ------------------------------------------------------------------------------------------------ diagram (fixed layout)
# title band
text("title", 1600, 125, "Sting Audits", 120, INK, "middle", 700, dur=1.2)
text("subtitle", 1600, 190, "Apart AI Collusion Sprint · Track 3", 50, GRY, "middle", 500)
text("takeaway", 1600, 268, "Control for compliance before trusting a sting.", 66, RED, "middle", 700, dur=2.2)

# A: the sting (agent + offers)
ax, ay = 250, 640
agent = (rough_rect(ax - 110, ay - 100, 220, 190, 2.5) + " " + rough_circle(ax - 45, ay - 20, 22) + " " + rough_circle(ax + 45, ay - 20, 22)
         + " " + rough_poly([(ax - 50, ay + 45), (ax, ay + 62), (ax + 50, ay + 45)], a=1) + " " + rough_poly([(ax, ay - 100), (ax, ay - 150)])
         + " " + rough_circle(ax, ay - 162, 13) + " " + rough_poly([(ax - 80, ay + 90), (ax - 80, ay + 175), (ax + 80, ay + 175), (ax + 80, ay + 90)]))
path("agent", agent, INK, 6, dur=2.2)
env = rough_rect(ax + 150, ay - 60, 150, 100) + " " + rough_poly([(ax + 150, ay - 60), (ax + 225, ay - 5), (ax + 300, ay - 60)])
path("envelope", env, RED, 5, dur=1.2)
bx, bw = 600, 640
bub = {"s1": (360, RED, "S1  “Let's secretly team up.”"), "s2": (520, AMB, "S2  “Let's go easy on each other.”"),
       "s3": (680, BLU, "S3  “Let's keep it fair.”"), "s0": (840, GRY, "S0  designer's secret-channel tool")}
for k, (yy, c, s) in bub.items():
    d = rough_rect(bx, yy, bw, 112, 2.2) + " " + rough_poly([(bx, yy + 70), (bx - 40, yy + 95), (bx, yy + 92)], a=1)
    path(f"{k}_bubble", d, c, 5, dur=1.0)
    text(f"{k}_text", bx + 26, yy + 74, s, 50, c, weight=700)
text("pct_s1", bx + bw + 25, 432, "3%", 64, RED, weight=700, dur=0.6)
text("pct_s2", bx + bw + 30, 592, "90%", 64, AMB, weight=700, dur=0.6)
text("oss_label", bx + bw + 20, 335, "gpt-oss-120b", 44, INK, weight=600)
path("stamp", rough_rect(680, 990, 470, 90, 2), GRN, 5, dur=0.9)
text("stamp_text", 915, 1050, "PRE-REGISTERED · frozen", 46, GRN, "middle", 700)
path("badge", rough_poly([(ax + 60 * math.cos(math.pi / 2 + k * 4 * math.pi / 5), ay + 290 - 60 * math.sin(math.pi / 2 + k * 4 * math.pi / 5)) for k in range(6)], a=1.5), AMB, 5, dur=1.1)
text("badge_label", ax, ay + 395, "undercover sting", 44, AMB, "middle", 700)

# C: the game table
tx, ty, tr = 2640, 660, 230
path("table_sketch", rough_circle(tx, ty, tr, 3), INK, 6, dur=1.6)
seat_pos = {"Lily": (tx, ty - tr - 85), "Luke": (tx + tr + 95, ty), "Mike": (tx, ty + tr + 85), "Quinn": (tx - tr - 95, ty)}
path("seats", " ".join(rough_circle(x, y, 52, 2) for x, y in seat_pos.values()), INK, 5, dur=1.8)
names = "".join(f"<text x='{x}' y='{y + 15}' font-size='40' font-weight='700' text-anchor='middle' font-family=\"{FONT}\">{n}</text>" for n, (x, y) in seat_pos.items())
EL["seat_names"] = dict(type="fade", dur=0.6, svg=f"<g id='seat_names' opacity='0'>{names}</g>")
mx, my = tx + 300, ty - 300
path("magnifier", rough_circle(mx, my, 62, 2) + " " + rough_poly([(mx + 44, my + 44), (mx + 110, my + 110)], a=1), BLU, 7, dur=1.2)
text("mag_label", mx + 10, my - 90, "passive monitor", 46, BLU, "middle", 700)
lx, ly = seat_pos["Luke"]; qx, qy = seat_pos["Quinn"]
path("private_line", rough_poly([(qx + 55, qy + 20), (tx, ty + 120), (lx - 55, ly + 20)], a=2), RED, 6, dur=1.4, dash="16 14")
text("private_label", tx, ty + 175, "private channel", 46, RED, "middle", 700)
cards = " ".join(rough_rect(tx - 95 + 52 * k, ty - 60 + (8 if k % 2 else 0), 70, 100, 1.4) for k in range(3))
path("cards", cards, INK, 4, dur=1.2)
rev = rough_poly([(tx - 70, ty + 80), (tx + 40, ty + 80), (tx + 40, ty + 105), (tx - 20, ty + 105), (tx - 30, ty + 140), (tx - 62, ty + 140), (tx - 55, ty + 105), (tx - 70, ty + 105)], closed=True, a=1)
path("revolver", rev, GRY, 4, dur=1.0)
text("game_label", tx, ty - tr - 175, "Liar's Bar", 62, INK, "middle", 700)
text("open_label", tx, ty + tr + 205, "open channel · no offer", 48, GRN, "middle", 700)

# question arrow A -> C
path("q_arrow", arrow_d(1290, 930, 2080, 930, bend=-0.08, head=30), INK, 5, dur=1.4, dash="18 14")
text("q_label", 1655, 1010, "predicts collusion?", 56, INK, "middle", 700)

# GRID: 4 models x 3 personas
gx, gy, cs = 1610, 380, 92
grid = " ".join(rough_rect(gx + c * cs, gy + r * cs, cs - 14, cs - 14, 1.2) for r in range(4) for c in range(3))
path("grid", grid, INK, 4, dur=1.8)
text("grid_label", gx + 1.5 * cs - 7, gy - 40, "12 configurations", 50, INK, "middle", 700)
text("grid_rows", gx - 30, gy + 2 * cs, "4 models", 42, GRY, "end", 600)
text("grid_cols", gx + 1.5 * cs - 7, gy + 4 * cs + 45, "× 3 personas", 42, GRY, "middle", 600)

# D: bar chart
dx0, dy0, dw, dh = 180, 1260, 900, 520   # plot area
path("axes_d", rough_poly([(dx0, dy0), (dx0, dy0 + dh), (dx0 + dw, dy0 + dh)], a=1.5), INK, 5, dur=1.0)
cols = {"S0": GRY, "S1": RED, "S2": AMB, "S3": BLU}
names_d = {"S0": "designer", "S1": "pact", "S2": "hint", "S3": "fair play"}
for k, o in enumerate(["S0", "S1", "S2", "S3"]):
    x = dx0 + 60 + k * 215; h = dh * acc[o]
    grow(f"bar_{o}", x, dy0 + dh - h, 150, h, cols[o])
    text(f"val_{o}", x + 75, dy0 + dh - h - 22, f"{100 * acc[o]:.0f}%", 58, cols[o], "middle", 700, dur=0.5)
    text(f"lab_{o}", x + 75, dy0 + dh + 58, names_d[o], 44, INK, "middle", 600, dur=0.5)
text("claude_note", dx0 + dw / 2 + 60, dy0 - 55, "Claude, fair persona: 0/10 vs 10/10", 46, GRN, "middle", 700)

# E: scatter
ex0, ey0, ew, eh = 1300, 1240, 640, 560
path("axes_e", rough_poly([(ex0, ey0), (ex0, ey0 + eh), (ex0 + ew, ey0 + eh)], a=1.5), INK, 5, dur=1.0)
text("xlab_e", ex0 + ew / 2, ey0 + eh + 62, "accepts fair play →", 44, INK, "middle", 600)
text("ylab_e", ex0 - 40, ey0 + eh / 2, "accepts collusion →", 44, INK, "middle", 600, rot=-90)
PC = {"neutral": GRY, "competitive": RED, "fair": GRN}
pts, seen = [], {}
for key, v in cfg.items():
    m, p = key.split("|")
    b, s = v["benign"], v["sting"]
    n = seen.get((b, s), 0); seen[(b, s)] = n + 1
    pts.append((ex0 + ew * b - 22 * n, ey0 + eh * (1 - s) + 12 * n, PC[p]))
dots("dots", pts)
path("diag", rough_poly([(ex0, ey0 + eh), (ex0 + ew, ey0)], a=1.5), INK, 4, dur=1.2, dash="14 12")
text("rho", ex0 + 30, ey0 + 40, f"ρ = {rho:.2f}", 72, BLU, weight=700, dur=0.8)
text("lab_allam", ex0 + ew - 20, ey0 - 40, "yes to everything", 44, INK, "end", 700)
text("lab_qwen", ex0 + 40, ey0 + eh - 50, "no to everything", 44, INK, "start", 700)
text("compliance", ex0 + ew / 2, ey0 - 105, "compliance, not collusion", 58, RED, "middle", 700, dur=1.4)

# F: proof screenshot + quota
fx, fy, fw = 2220, 1240, 840
fh = fw * 1051 / 2276
image("shot", "../report/paper_figs/shot_private_channel.png", fx, fy, fw, fh)
text("alliance_label", fx + fw / 2, fy - 40, "unprompted alliance (real log)", 50, RED, "middle", 700)
text("quote", fx + fw / 2, fy + fh + 70, "“control the board and force them out”", 50, INK, "middle", 700, dur=1.8)
qy = fy + fh + 110
boxes = " ".join(rough_rect(fx - 20 + k * 42, qy, 34, 34, 0.8) for k in range(21))
path("quota_boxes", boxes, INK, 3, dur=1.6)
EL["quota_fill"] = dict(type="fade", dur=0.6, svg="<g id='quota_fill' opacity='0'>" + "".join(
    f"<rect x='{fx - 20 + k * 42 + 3}' y='{qy + 3}' width='28' height='28' fill='{GRN}'/>" for k in range(2)) + "</g>")
text("quota_label", fx + fw / 2, qy + 95, "2 of 21 games run", 46, AMB, "middle", 700)
qwen_pt = [p for p, (key, v) in zip(pts, cfg.items()) if key.startswith("qwen3.8-27b|neutral")][0]
path("same_arrow", arrow_d(fx - 20, fy + fh * 0.55, qwen_pt[0] + 40, qwen_pt[1] + 10, bend=-0.25, head=30), RED, 5, dur=1.4)
text("same_label", 1745, ey0 + eh - 150, "same model refused the stings", 46, RED, "middle", 700)
text("repo", 1600, 1960, "github.com/LSUDOKO/AI-Collusion-Research", 52, BLU, "middle", 700, dur=1.6)

# ------------------------------------------------------------------------------------------------ camera regions (world boxes)
REG = {"ALL": (0, 20, 3200, 2130), "TITLE": (900, 30, 1400, 300), "A": (60, 280, 1450, 900), "C": (2000, 220, 1200, 1060),
       "GRID": (1150, 280, 900, 560), "D": (60, 1150, 1180, 820), "E": (1150, 1080, 960, 900), "F": (2120, 1150, 1080, 800),
       "EF": (1150, 1080, 2050, 900)}


def fit(box, ar=16 / 9, m=1.08):
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    w, h = w * m, h * m
    if w / h < ar:
        w = h * ar
    else:
        h = w / ar
    return [cx, cy, w]


# ------------------------------------------------------------------------------------------------ timeline from real audio
timing = json.loads((VID / "timing.json").read_text())
t = LEAD
lines, cams, sched = [], [], {}
prev = None
for l, tm in zip(LINES, timing):
    start, dur = t, tm["dur"]
    moved = l["cam"] != prev
    if moved:
        cams.append(dict(t=start, box=fit(REG[l["cam"]])))
    t0 = start + (CAM_T if moved else 0.15)
    avail = max(0.6, start + dur + GAP * 0.6 - t0)
    total = sum(EL[i]["dur"] for i in l["draw"])
    k = min(1.0, avail / total)
    for i in l["draw"]:
        d = EL[i]["dur"] * k
        sched[i] = (t0, d); t0 += d
    # subtitles: chunks of <= 7 words, timed proportionally to the spoken words
    sw = l["sub"].split(); n = len(sw); chunks = [sw[a:a + 7] for a in range(0, n, 7)]
    if len(chunks) > 1 and len(chunks[-1]) < 3:
        chunks[-2] += chunks[-1]; chunks.pop()
    W = tm["words"]; subs = []; pos = 0
    for c in chunks:
        f0 = pos / n; pos += len(c)
        wi = min(len(W) - 1, int(f0 * len(W)))
        subs.append(dict(t=start + (W[wi]["t"] if W else f0 * dur), s=" ".join(c)))
    lines.append(dict(t=start, dur=dur, file=tm["file"], subs=subs, end=start + dur))
    prev = l["cam"]; t = start + dur + GAP
T_END = t + 2.2
missing = [i for i in EL if i not in sched]
assert not missing, missing

elements = [dict(id=i, type=e["type"], start=round(sched[i][0], 3), dur=round(sched[i][1], 3), **({"box": e["box"]} if "box" in e else {}),
                 **({"n": e["n"]} if "n" in e else {})) for i, e in EL.items()]
DATA = dict(elements=elements, cams=cams, lines=lines, T_END=T_END, CAM_T=CAM_T)
(VID / "timeline.json").write_text(json.dumps(DATA, indent=1))

svg_body = "".join(e["svg"] for e in EL.values())
HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&family=Inter+Tight:wght@500;600&display=block" rel="stylesheet">
<style>html,body{{margin:0;width:1920px;height:1080px;overflow:hidden;background:#fdfdfb}}
#sub{{position:absolute;left:0;right:0;bottom:46px;text-align:center;font-family:'Inter Tight',sans-serif;font-size:38px;font-weight:600;color:#1d1d1f}}
#sub span{{background:#fdfdfbE6;padding:6px 18px;border-radius:6px}}
#prog{{position:absolute;left:0;bottom:0;height:6px;background:#2471a3}}</style></head><body>
<svg id="w" width="1920" height="1080" viewBox="0 0 3200 1800" xmlns="http://www.w3.org/2000/svg">
<defs><pattern id="paper" width="80" height="80" patternUnits="userSpaceOnUse"><path d="M80 0H0V80" fill="none" stroke="#eceae4" stroke-width="2"/></pattern></defs>
<rect x="-2000" y="-2000" width="8000" height="7000" fill="url(#paper)"/>
{svg_body}
<g id="pen" style="visibility:hidden"><g transform="rotate(35)"><rect x="-9" y="-130" width="18" height="110" rx="4" fill="#2c3e50"/><rect x="-9" y="-150" width="18" height="24" rx="3" fill="#c0392b"/><path d="M-9,-20 L0,0 L9,-20 z" fill="#1d1d1f"/></g></g>
</svg><div id="sub"></div><div id="prog"></div>
<script>
const D = {json.dumps(DATA)};
const ease = p => p < .5 ? 4*p*p*p : 1 - Math.pow(-2*p + 2, 3)/2;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const svg = document.getElementById('w'), pen = document.getElementById('pen'), sub = document.getElementById('sub'), prog = document.getElementById('prog');
const N = {{}};
function init() {{
  for (const e of D.elements) {{
    const n = document.getElementById(e.id); N[e.id] = n;
    if (e.type === 'path') {{ e.len = n.getTotalLength(); n.style.strokeDasharray = n.dataset.dash ? n.dataset.dash : e.len + ' ' + e.len; }}
    if (e.type === 'text') {{ const b = n.getBBox(); e.bb = [b.x - 6, b.y - 10, b.width + 16, b.height + 24];
      const r = document.getElementById('r_' + e.id); r.setAttribute('x', e.bb[0]); r.setAttribute('y', e.bb[1]); r.setAttribute('height', e.bb[3]); }}
  }}
}}
function camAt(t) {{
  const C = D.cams; let i = 0; while (i + 1 < C.length && C[i + 1].t <= t) i++;
  if (i === 0 && t < C[0].t) return C[0].box;
  const prev = i > 0 ? C[i - 1].box : C[i].box, cur = C[i].box;
  const p = ease(clamp((t - C[i].t) / D.CAM_T, 0, 1));
  const w = Math.exp(Math.log(prev[2]) * (1 - p) + Math.log(cur[2]) * p);
  return [prev[0] + (cur[0] - prev[0]) * p, prev[1] + (cur[1] - prev[1]) * p, w];
}}
window.seek = function (t) {{
  const c = camAt(t), w = c[2], h = w * 9 / 16;
  svg.setAttribute('viewBox', (c[0] - w/2).toFixed(2) + ' ' + (c[1] - h/2).toFixed(2) + ' ' + w.toFixed(2) + ' ' + h.toFixed(2));
  let tip = null;
  for (const e of D.elements) {{
    const n = N[e.id], raw = (t - e.start) / e.dur, p = clamp(raw, 0, 1), active = raw > 0 && raw < 1;
    if (e.type === 'path') {{
      n.style.visibility = p > 0 ? 'visible' : 'hidden';
      if (n.dataset.dash) {{ n.style.strokeDashoffset = 0; n.style.strokeDasharray = dashPartial(n.dataset.dash, e.len * p, e.len);
      }} else n.style.strokeDashoffset = e.len * (1 - p);
      if (active) {{ const q = n.getPointAtLength(e.len * p); tip = [q.x, q.y]; }}
    }} else if (e.type === 'text') {{
      document.getElementById('r_' + e.id).setAttribute('width', e.bb[2] * p);
      if (active) tip = [e.bb[0] + e.bb[2] * p, e.bb[1] + e.bb[3] * 0.75];
    }} else if (e.type === 'image') {{
      document.getElementById('r_' + e.id).setAttribute('width', e.box[2] * ease(p));
      if (active) tip = [e.box[0] + e.box[2] * ease(p), e.box[1] + e.box[3] * 0.5];
    }} else if (e.type === 'grow') {{
      const q = ease(p), b = e.box; n.setAttribute('y', b[1] + b[3] * (1 - q)); n.setAttribute('height', b[3] * q);
      document.getElementById(e.id + '_o').setAttribute('opacity', p >= 1 ? 1 : 0);
      if (active) tip = [b[0] + b[2], b[1] + b[3] * (1 - q)];
    }} else if (e.type === 'fade') {{ n.setAttribute('opacity', p);
    }} else if (e.type === 'dots') {{
      n.querySelectorAll('.dot').forEach((g, k) => {{ const s = clamp(raw * e.n - k, 0, 1);
        const r = s <= 0 ? 0 : 20 * (s < .7 ? s / .7 * 1.15 : 1.15 - .15 * (s - .7) / .3); g.firstChild.setAttribute('r', r); }});
    }}
  }}
  if (tip) {{ pen.style.visibility = 'visible'; pen.setAttribute('transform', 'translate(' + tip[0] + ',' + tip[1] + ')'); }}
  else pen.style.visibility = 'hidden';
  let s = '';
  for (const L of D.lines) if (t >= L.t && t < L.end + 0.25) for (const c of L.subs) if (t >= c.t) s = c.s;
  sub.innerHTML = s ? '<span>' + s + '</span>' : '';
  prog.style.width = (100 * clamp(t / D.T_END, 0, 1)) + '%';
}};
function dashPartial(pattern, drawn, L) {{
  // dashed stroke revealed up to length `drawn`: repeat the dash pattern up to drawn, then a long gap
  const a = pattern.split(/[ ,]+/).map(Number), out = []; let s = 0, k = 0;
  while (s < drawn && out.length < 4000) {{ const v = Math.min(a[k % a.length], drawn - s); out.push(v); s += v; k++; }}
  if (out.length % 2 === 1) out.push(L + 10); else {{ out.push(0); out.push(L + 10); }}
  return out.join(' ');
}}
window.ready = document.fonts.ready.then(() => {{ init(); window.seek(0); return true; }});
</script></body></html>"""
(VID / "index.html").write_text(HTML)
print("elements", len(EL), "duration", round(T_END, 1), "s; cams", len(cams))
