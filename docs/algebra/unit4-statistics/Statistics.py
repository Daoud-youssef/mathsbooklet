"""
Statistics.py
=============
Single source of truth for ALL Unit 4 Statistics exercises.
Follows the exact same architecture as Indices.py / Mensuration.py.

Covers:
  LT1 — Averages from a list (mean, median, mode, range)
  LT2 — Frequency tables (ungrouped)
  LT3 — Grouped frequency tables
  LT4 — Cumulative frequency
  LT5 — Box plots & IQR

Usage:
    from Statistics import generate
    data = generate(types=["mean_simple","freq_table_mean"], seed=42, count=4)
"""

import math
import random
import json
from datetime import date
from collections import Counter

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")
ri = random.randint

def _fmt(x):
    if isinstance(x, float) and x == int(x):
        return str(int(x))
    if isinstance(x, float):
        return str(round(x, 2))
    return str(x)

def _part(question_latex, answer_latex, solution_latex,
          answer_plain="", is_word=False, is_wide=False):
    return {
        "question_latex": question_latex,
        "answer_latex":   answer_latex,
        "answer":         answer_plain or answer_latex,
        "solution_latex": solution_latex,
        "is_word":        is_word,
        "is_wide":        is_wide,
    }

def _median(lst):
    s = sorted(lst); n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n//2 - 1] + s[n//2]) / 2

def _quartiles(lst):
    s = sorted(lst); n = len(s)
    mid = n // 2
    lower = s[:mid]
    upper = s[mid:] if n % 2 == 0 else s[mid+1:]
    return _median(lower), _median(s), _median(upper)

def _mode(lst):
    c = Counter(lst)
    mx = max(c.values())
    modes = sorted([k for k, v in c.items() if v == mx])
    return modes

# ══════════════════════════════════════════════════════════════════
# SVG ENGINE
# ══════════════════════════════════════════════════════════════════

def _svg_wrap(content, vw, vh):
    return (f'<svg width="{int(vw)}" height="{int(vh)}" '
            f'viewBox="0 0 {int(vw)} {int(vh)}" '
            f'style="display:block;margin:8px auto;font-family:serif;" '
            f'xmlns="http://www.w3.org/2000/svg">{content}</svg>')

def _txt(x, y, text, size=12, color="black", anchor="middle", bold=False):
    fw = "bold" if bold else "normal"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-weight="{fw}" font-family="serif">{text}</text>')

def _line(x1, y1, x2, y2, color="#333", sw=1, dash=""):
    da = f'stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{sw}" {da}/>')

def _rect(x, y, w, h, fill="#eee", stroke="#333", sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

# ─── STEM AND LEAF SVG ────────────────────────────────────────────
def svg_stem_leaf(stems, leaves_dict, title="Stem & Leaf Diagram",
                  key_stem=None, key_leaf=None, key_value=None):
    """
    stems: list of stem values e.g. [3,4,5,6,7]
    leaves_dict: {stem: [leaf, leaf, ...]} e.g. {3:[1,2,7,9,9], 4:[0,0,2,3]}
    key_stem, key_leaf, key_value: for key row e.g. 3,1,"31"
    """
    cell_w = 22; stem_w = 36; pad_x = 20; pad_y = 36
    max_leaves = max(len(v) for v in leaves_dict.values()) if leaves_dict else 1
    row_h = 26; header_h = 32; key_h = 28

    # Canvas
    total_w = pad_x*2 + stem_w + max_leaves * cell_w + 20
    total_h = pad_y + header_h + len(stems) * row_h + key_h + pad_y

    body = ""
    # Title
    body += _txt(total_w/2, 18, title, size=13, bold=True)

    # Header row
    hy = pad_y + header_h/2
    body += _rect(pad_x, pad_y, stem_w, header_h, "#2255aa", "#2255aa")
    body += _txt(pad_x + stem_w/2, hy, "Stem", size=11, color="white", bold=True)
    body += _rect(pad_x + stem_w, pad_y, total_w - pad_x*2 - stem_w - 10,
                  header_h, "#2255aa", "#2255aa")
    body += _txt(pad_x + stem_w + (total_w - pad_x*2 - stem_w - 10)/2,
                 hy, "Leaves", size=11, color="white", bold=True)

    # Data rows
    for i, stem in enumerate(stems):
        ry = pad_y + header_h + i * row_h
        fill = "#f0f4ff" if i % 2 == 0 else "#ffffff"
        body += _rect(pad_x, ry, stem_w, row_h, fill, "#aabbcc")
        body += _txt(pad_x + stem_w/2, ry + row_h/2, str(stem),
                     size=12, color="#1a3a6e", bold=True)
        leaves = leaves_dict.get(stem, [])
        body += _rect(pad_x + stem_w, ry,
                      total_w - pad_x*2 - stem_w - 10, row_h, fill, "#aabbcc")
        for j, lf in enumerate(leaves):
            lx = pad_x + stem_w + 12 + j * cell_w
            body += _txt(lx, ry + row_h/2, str(lf), size=12, color="#333")

    # Key
    ky = pad_y + header_h + len(stems) * row_h + 8
    if key_stem is not None:
        key_text = f"Key:  {key_stem} | {key_leaf}  represents  {key_value}"
        body += _txt(pad_x, ky + key_h/2, key_text,
                     size=11, color="#555", anchor="start")

    return _svg_wrap(body, total_w, total_h)


# ─── BOX PLOT SVG ─────────────────────────────────────────────────
def svg_box_plot(min_val, q1, median, q3, max_val,
                 outliers=None, label="", scale_min=None, scale_max=None):
    """Draw a horizontal box-and-whisker plot."""
    outliers = outliers or []
    pad_x = 50; pad_y = 40; plot_h = 60; tick_h = 8
    vw = 480; vh = pad_y * 2 + plot_h + 30

    s_min = scale_min if scale_min is not None else min(min_val, *outliers, min_val) - 2
    s_max = scale_max if scale_max is not None else max(max_val, *outliers, max_val) + 2
    span = s_max - s_min

    def px(v):
        return pad_x + (v - s_min) / span * (vw - pad_x * 2)

    cy = pad_y + plot_h / 2
    body = ""

    # Axis line
    body += _line(pad_x, cy + plot_h/2 + 10, vw - pad_x, cy + plot_h/2 + 10, "#888", 1)

    # Tick marks and labels
    step = _nice_step(span, 8)
    v = math.ceil(s_min / step) * step
    while v <= s_max:
        x = px(v)
        body += _line(x, cy + plot_h/2 + 6, x, cy + plot_h/2 + 14, "#666", 1)
        body += _txt(x, cy + plot_h/2 + 24, _fmt(v), size=10, color="#444")
        v = round(v + step, 10)

    # Whiskers
    body += _line(px(min_val), cy, px(q1), cy, "#1a3a8f", 2)
    body += _line(px(q3), cy, px(max_val), cy, "#1a3a8f", 2)
    # End caps
    body += _line(px(min_val), cy - tick_h, px(min_val), cy + tick_h, "#1a3a8f", 2)
    body += _line(px(max_val), cy - tick_h, px(max_val), cy + tick_h, "#1a3a8f", 2)

    # Box
    box_w = px(q3) - px(q1)
    body += _rect(px(q1), cy - plot_h/4, box_w, plot_h/2, "#c8d8f8", "#1a3a8f", 2)

    # Median line
    body += _line(px(median), cy - plot_h/4, px(median), cy + plot_h/4, "#c0392b", 2)

    # Outliers
    for o in outliers:
        body += (f'<circle cx="{px(o):.1f}" cy="{cy:.1f}" r="4" '
                 f'fill="none" stroke="#e74c3c" stroke-width="1.5"/>')
        body += _line(px(o), cy - tick_h, px(o), cy + tick_h, "#e74c3c", 1, "3")

    # Shape labels only (no values — students must calculate from data)
    for v, lbl in [(min_val,"Min"),(q1,"Q₁"),(median,"Q₂"),(q3,"Q₃"),(max_val,"Max")]:
        body += _txt(px(v), cy - plot_h/4 - 10, lbl, size=9, color="#888")

    if label:
        body += _txt(vw/2, 14, label, size=12, bold=True)

    return _svg_wrap(body, vw, vh)


def _nice_step(span, max_ticks=8):
    raw = span / max_ticks
    mag = 10 ** math.floor(math.log10(raw))
    for s in [1, 2, 5, 10]:
        if raw <= s * mag:
            return s * mag
    return mag * 10


# ─── CUMULATIVE FREQUENCY SVG ─────────────────────────────────────
def svg_cumfreq(upper_bounds, cum_freqs, total,
                xlabel="Value", title="Cumulative Frequency"):
    """Draw a cumulative frequency curve with Q1/median/Q3 lines."""
    pad_x = 55; pad_y = 30; pad_b = 50; pad_r = 20
    vw = 480; vh = 340
    plot_w = vw - pad_x - pad_r
    plot_h = vh - pad_y - pad_b

    x_min = 0; x_max = upper_bounds[-1]
    y_min = 0; y_max = total

    def px(v): return pad_x + (v - x_min) / (x_max - x_min) * plot_w
    def py(v): return pad_y + plot_h - (v - y_min) / (y_max - y_min) * plot_h

    body = ""
    # Background
    body += _rect(pad_x, pad_y, plot_w, plot_h, "#f9f9f9", "#ccc")

    # Grid lines
    y_step = _nice_step(total, 6)
    yv = 0
    while yv <= total:
        body += _line(pad_x, py(yv), pad_x + plot_w, py(yv), "#ddd", 1)
        body += _txt(pad_x - 6, py(yv), str(int(yv)), size=9,
                     color="#666", anchor="end")
        yv += y_step

    x_step = _nice_step(x_max - x_min, 6)
    xv = x_min
    while xv <= x_max:
        body += _line(px(xv), pad_y, px(xv), pad_y + plot_h, "#ddd", 1)
        body += _txt(px(xv), pad_y + plot_h + 14, str(int(xv) if xv == int(xv) else round(xv,1)),
                     size=9, color="#666")
        xv = round(xv + x_step, 10)

    # Axes
    body += _line(pad_x, pad_y, pad_x, pad_y + plot_h, "#333", 1.5)
    body += _line(pad_x, pad_y + plot_h, pad_x + plot_w, pad_y + plot_h, "#333", 1.5)

    # Curve — start from (x_min, 0)
    pts = [(x_min, 0)] + list(zip(upper_bounds, cum_freqs))
    path_d = f"M {px(pts[0][0]):.1f},{py(pts[0][1]):.1f}"
    for xv, yv in pts[1:]:
        path_d += f" L {px(xv):.1f},{py(yv):.1f}"
    body += (f'<path d="{path_d}" fill="none" stroke="#2255aa" '
             f'stroke-width="2" stroke-linejoin="round"/>')
    # Points
    for xv, yv in pts:
        body += (f'<circle cx="{px(xv):.1f}" cy="{py(yv):.1f}" r="4" '
                 f'fill="#2255aa" stroke="white" stroke-width="1"/>')

    # Q1, median, Q3 dashed reference lines
    for frac, color, lbl in [(0.25,"#e74c3c","Q₁"),
                              (0.50,"#27ae60","Q₂"),
                              (0.75,"#8e44ad","Q₃")]:
        yval = frac * total
        # Interpolate x
        for i in range(len(cum_freqs)):
            cf_prev = 0 if i == 0 else cum_freqs[i-1]
            if cum_freqs[i] >= yval >= cf_prev:
                x_prev = x_min if i == 0 else upper_bounds[i-1]
                x_cur  = upper_bounds[i]
                if cum_freqs[i] == cf_prev:
                    xval = x_prev
                else:
                    t = (yval - cf_prev) / (cum_freqs[i] - cf_prev)
                    xval = x_prev + t * (x_cur - x_prev)
                break
        else:
            xval = upper_bounds[-1]
        body += _line(pad_x, py(yval), px(xval), py(yval), color, 1, "5")
        body += _line(px(xval), py(yval), px(xval), pad_y + plot_h, color, 1, "5")
        body += _txt(px(xval), pad_y + plot_h + 26, lbl, size=9,
                     color=color, bold=True)

    # Axis labels
    body += _txt(pad_x + plot_w/2, pad_y + plot_h + 40, xlabel,
                 size=11, color="#333")
    body += (f'<text transform="rotate(-90,{pad_x-38},{pad_y+plot_h/2:.0f})" '
             f'x="{pad_x-38:.0f}" y="{pad_y+plot_h/2:.0f}" '
             f'font-size="11" fill="#333" text-anchor="middle" '
             f'font-family="serif">Cumulative Frequency</text>')
    body += _txt(vw/2, 16, title, size=12, bold=True)

    return _svg_wrap(body, vw, vh)



def svg_box_plot_grid(min_val, q1, median, q3, max_val):
    """Box plot with grid and numbered axis. No quartile labels — students read values."""
    pad_x = 60; pad_y = 50; plot_h = 70; tick_h = 10
    vw = 520; vh = pad_y + plot_h + 60

    s_min = min_val - (max_val - min_val) * 0.15
    s_max = max_val + (max_val - min_val) * 0.15
    span  = s_max - s_min

    def px(v):
        return pad_x + (v - s_min) / span * (vw - pad_x - 30)

    cy = pad_y + plot_h / 2
    body = ""

    # Grid lines
    step = _nice_step(span, 8)
    v = math.ceil(s_min / step) * step
    while v <= s_max:
        x = px(v)
        body += _line(x, pad_y, x, pad_y + plot_h, "#dddddd", 1)
        body += _line(x, pad_y + plot_h, x, pad_y + plot_h + tick_h, "#888", 1)
        body += _txt(x, pad_y + plot_h + tick_h + 12,
                     str(int(v) if v == int(v) else round(v,1)),
                     size=11, color="#444")
        v = round(v + step, 10)

    # Axis line
    body += _line(pad_x, pad_y + plot_h, vw - 30, pad_y + plot_h, "#555", 1.5)

    # Whiskers
    body += _line(px(min_val), cy, px(q1), cy, "#1a3a8f", 2)
    body += _line(px(q3), cy, px(max_val), cy, "#1a3a8f", 2)
    body += _line(px(min_val), cy - tick_h, px(min_val), cy + tick_h, "#1a3a8f", 2)
    body += _line(px(max_val), cy - tick_h, px(max_val), cy + tick_h, "#1a3a8f", 2)

    # Box
    box_w = px(q3) - px(q1)
    body += _rect(px(q1), cy - plot_h / 4, box_w, plot_h / 2,
                  "#c8d8f8", "#1a3a8f", 2)

    # Median line
    body += _line(px(median), cy - plot_h/4, px(median), cy + plot_h/4,
                  "#c0392b", 2.5)

    # Title
    body += _txt(vw/2, 18, "Box Plot", size=12, bold=True)

    return _svg_wrap(body, vw, vh)

# ══════════════════════════════════════════════════════════════════
# LT1 — AVERAGES FROM A LIST
# ══════════════════════════════════════════════════════════════════

def gen_mean_simple():
    n = ri(5, 8)
    data = [ri(2, 20) for _ in range(n)]
    mean = round(sum(data) / n, 2)
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = f"\\bar{{x}} = {_fmt(mean)}"
    sol = f"\\dfrac{{{'+'.join(str(x) for x in data)}}}{{{n}}} = {_fmt(mean)}"
    return _part(q, a, sol, _fmt(mean), is_wide=True)


def gen_median_simple():
    n = random.choice([5, 6, 7, 8, 9])
    data = sorted([ri(1, 20) for _ in range(n)])
    med = _median(data)
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    if n % 2 == 1:
        pos = n // 2 + 1
        a = f"\\text{{Median}} = {_fmt(med)}"
        sol = f"\\text{{Ordered. Position }}\\frac{{n+1}}{{2}}={pos}\\text{{th value}} = {_fmt(med)}"
    else:
        p1, p2 = n//2, n//2 + 1
        v1, v2 = data[p1-1], data[p2-1]
        a = f"\\text{{Median}} = {_fmt(med)}"
        sol = f"\\text{{Mean of positions {p1} and {p2}: }}\\frac{{{v1}+{v2}}}{{2}}={_fmt(med)}"
    return _part(q, a, sol, _fmt(med), is_wide=True)


def gen_mode_simple():
    base = [ri(1, 12) for _ in range(4)]
    # Ensure one clear mode
    mode_val = random.choice(base)
    data = base + [mode_val, mode_val]
    random.shuffle(data)
    modes = _mode(data)
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = f"\\text{{Mode}} = {', '.join(str(m) for m in modes)}"
    sol = f"\\text{{Most frequent value(s): }}{', '.join(str(m) for m in modes)}"
    return _part(q, a, sol, is_wide=True)


def gen_range_simple():
    n = ri(5, 9)
    data = [ri(2, 30) for _ in range(n)]
    rng = max(data) - min(data)
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = f"\\text{{Range}} = {rng}"
    sol = f"{max(data)} - {min(data)} = {rng}"
    return _part(q, a, sol, str(rng), is_wide=True)


def gen_averages_combined():
    """Find mean, median, mode and range from same dataset."""
    n = ri(6, 10)
    # Ensure a clear mode
    base = [ri(2, 15) for _ in range(n - 2)]
    mode_val = random.choice(base)
    data = base + [mode_val, mode_val]
    random.shuffle(data)
    mean = round(sum(data) / len(data), 2)
    med  = _median(sorted(data))
    modes = _mode(data)
    rng  = max(data) - min(data)
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = (f"\\text{{Mean}}={_fmt(mean)},\\ "
         f"\\text{{Median}}={_fmt(med)},\\ "
         f"\\text{{Mode}}={', '.join(str(m) for m in modes)},\\ "
         f"\\text{{Range}}={rng}")
    sol = (f"\\bar{{x}}=\\frac{{{sum(data)}}}{{{len(data)}}}={_fmt(mean)}"
           f"\\quad \\text{{Median}}={_fmt(med)}"
           f"\\quad \\text{{Mode}}={', '.join(str(m) for m in modes)}"
           f"\\quad \\text{{Range}}={rng}")
    return _part(q, a, sol, is_wide=True)


def gen_mean_find_missing():
    """
    Three subtypes chosen randomly:
    1. Mean of n numbers given, find missing value
    2. Mean updates when new value added
    3. Missing value given ratio between unknowns
    """
    subtype = random.choice(["missing_val", "updated_mean", "ratio"])

    if subtype == "missing_val":
        n = ri(4, 7)
        mean = ri(5, 15)
        total = mean * n
        known = [ri(2, 20) for _ in range(n - 1)]
        x = total - sum(known)
        known_str = ",\\ ".join(str(v) for v in known)
        q = (f"\\text{{Mean}} = {mean},\\quad n={n}"
             f"\\\\[4pt]\\text{{Numbers: }}{known_str},\\ x")
        a = f"x = {x}"
        sol = (f"\\text{{Total}} = {mean}\\times{n}={total}"
               f"\\quad x = {total}-({'+'.join(str(v) for v in known)}) = {x}")
        return _part(q, a, sol, str(x), is_wide=True)

    elif subtype == "updated_mean":
        n  = ri(5, 12)
        m1 = ri(3, 15)
        new_val = ri(1, 25)
        total_new = m1 * n + new_val
        m2 = round(total_new / (n + 1), 2)
        q = (f"\\text{{Mean of }}{n}\\text{{ numbers}} = {m1},"
             f"\\quad\\text{{new value}} = {new_val}")
        a = f"\\text{{New mean}} = {_fmt(m2)}"
        sol = (f"\\text{{Old total}} = {m1}\\times{n} = {m1*n}"
               f"\\quad \\text{{New total}} = {m1*n}+{new_val} = {total_new}"
               f"\\quad \\bar{{x}}_{{\\text{{new}}}} = \\frac{{{total_new}}}{{{n+1}}} = {_fmt(m2)}")
        return _part(q, a, sol, _fmt(m2), is_wide=True)

    else:  # ratio
        n = 5
        mean = ri(20, 40)
        total = mean * n
        n_known = 3
        known = [ri(10, 40) for _ in range(n_known)]
        remainder = total - sum(known)
        # ratio p:q, remainder = p*k + q*k
        p, q_r = 1, ri(2, 4)
        while remainder % (p + q_r) != 0:
            known = [ri(10, 40) for _ in range(n_known)]
            remainder = total - sum(known)
        k = remainder // (p + q_r)
        x1, x2 = p * k, q_r * k
        known_str = ",\\ ".join(str(v) for v in known)
        q_str = (f"\\text{{Mean}} = {mean},\\quad\\text{{three values: }}{known_str}"
                 f"\\\\[4pt]\\text{{Other two in ratio }}1:{q_r}")
        a = f"{x1}\\text{{ and }}{x2}"
        sol = (f"\\text{{Step 1: Total}}={mean}\\times5={total}"
               f"\\\\[4pt]\\text{{Step 2: Remaining}}={total}-({'+'.join(str(v) for v in known)})={remainder}"
               f"\\\\[4pt]\\text{{Step 3: Ratio }}1:{q_r}\\text{{ → }}"
               f"{p+q_r}\\text{{ equal parts, each }}=\\frac{{{remainder}}}{{{p+q_r}}}={k}"
               f"\\\\[4pt]\\text{{Step 4: Numbers are }}{x1}\\text{{ and }}{x2}")
        return _part(q_str, a, sol, f"{x1} and {x2}", is_wide=True)


def gen_stem_leaf_averages():
    """
    Generate stem & leaf diagram, ask for median, range, and modal class.
    Returns exercise with ex_svg (shown once above all parts).
    """
    # Generate data: 2-digit numbers, 3–4 stems
    stems_pool = random.choice([
        [2, 3, 4, 5],
        [3, 4, 5, 6, 7],
        [4, 5, 6, 7],
        [1, 2, 3, 4, 5],
    ])
    leaves_dict = {}
    all_data = []
    for s in stems_pool:
        n_leaves = ri(2, 6)
        leaves = sorted([ri(0, 9) for _ in range(n_leaves)])
        leaves_dict[s] = leaves
        for lf in leaves:
            all_data.append(s * 10 + lf)

    all_data.sort()
    n = len(all_data)
    med = _median(all_data)
    rng = all_data[-1] - all_data[0]
    # Mode = most frequent value in all_data
    from collections import Counter as _C
    cnt = _C(all_data)
    mode_val = cnt.most_common(1)[0][0]

    key_stem = stems_pool[0]
    key_leaf = leaves_dict[stems_pool[0]][0]
    key_value = f"{key_stem}{key_leaf}"

    svg = svg_stem_leaf(
        stems_pool, leaves_dict,
        title="Stem and Leaf Diagram",
        key_stem=key_stem, key_leaf=key_leaf, key_value=key_value
    )

    q_a = f"\\text{{Find the median.}}"
    q_b = f"\\text{{Find the range.}}"
    q_c = f"\\text{{Find the mode.}}"

    a_a = f"\\text{{Median}} = {_fmt(med)}"
    a_b = f"\\text{{Range}} = {rng}"
    a_c = f"\\text{{Mode}} = {mode_val}"

    sol_a = (f"\\text{{Ordered: }}{n}\\text{{ values, middle}} = {_fmt(med)}")
    sol_b = f"{all_data[-1]} - {all_data[0]} = {rng}"
    sol_c = f"\\text{{Most frequent value: }}{mode_val}"

    parts = [
        {**_part(q_a, a_a, sol_a, is_wide=False), "label": "a"},
        {**_part(q_b, a_b, sol_b, is_wide=False), "label": "b"},
        {**_part(q_c, a_c, sol_c, is_wide=False), "label": "c"},
    ]
    return parts, svg


# ══════════════════════════════════════════════════════════════════
# LT2 — FREQUENCY TABLES (UNGROUPED)
# ══════════════════════════════════════════════════════════════════

def _make_freq_table(values=None, n_values=5, min_v=1, max_v=8,
                     min_f=1, max_f=10):
    """Generate a frequency table. Returns (values, freqs)."""
    if values is None:
        values = sorted(random.sample(range(min_v, max_v + 1), n_values))
    freqs = [ri(min_f, max_f) for _ in values]
    return values, freqs

def _freq_table_latex(values, freqs, val_label="x", freq_label="f"):
    """Render frequency table as LaTeX array."""
    vals  = " & ".join(str(v) for v in values)
    freqs_s = " & ".join(str(f) for f in freqs)
    cols = "l" + "c" * len(values)
    return (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
            f"\\begin{{array}}{{{cols}}}\n"
            f"\\hline {val_label} & {vals} \\\\[4pt]\n"
            f"\\hline {freq_label} & {freqs_s} \\\\[4pt]\n"
            f"\\hline\n\\end{{array}}}}")

def gen_freq_table_mean():
    values, freqs = _make_freq_table(n_values=ri(4,6), min_v=1, max_v=10)
    total_f = sum(freqs)
    total_fx = sum(v * f for v, f in zip(values, freqs))
    mean = round(total_fx / total_f, 2)
    tbl = _freq_table_latex(values, freqs)
    q = tbl
    a = f"\\bar{{x}} = {_fmt(mean)}"
    fx_terms = "+".join(f"{v}\\times{f}" for v,f in zip(values,freqs))
    sol = f"\\frac{{{fx_terms}}}{{{total_f}}} = \\frac{{{total_fx}}}{{{total_f}}} = {_fmt(mean)}"
    return _part(q, a, sol, _fmt(mean), is_wide=True)


def gen_freq_table_median():
    values, freqs = _make_freq_table(n_values=ri(4,6), min_v=1, max_v=10)
    total_f = sum(freqs)
    # Build expanded list
    expanded = []
    for v, f in zip(values, freqs):
        expanded.extend([v] * f)
    med = _median(expanded)
    tbl = _freq_table_latex(values, freqs)
    q = tbl
    a = f"\\text{{Median}} = {_fmt(med)}"
    cf = 0
    sol_parts = []
    for v, f in zip(values, freqs):
        cf += f
        sol_parts.append(f"\\text{{CF up to }}{v}\\text{{ = }}{cf}")
    sol = f"n={total_f}\\quad \\text{{Middle position }}\\frac{{n+1}}{{2}}={round((total_f+1)/2,1)}\\quad \\text{{Median}}={_fmt(med)}"
    return _part(q, a, sol, _fmt(med), is_wide=True)


def gen_freq_table_mode():
    values, freqs = _make_freq_table(n_values=ri(4,6), min_v=1, max_v=10)
    max_f = max(freqs)
    modes = [v for v, f in zip(values, freqs) if f == max_f]
    tbl = _freq_table_latex(values, freqs)
    q = tbl
    a = f"\\text{{Mode}} = {', '.join(str(m) for m in modes)}"
    sol = f"\\text{{Highest frequency is }}{max_f}\\text{{, giving mode(s): }}{', '.join(str(m) for m in modes)}"
    return _part(q, a, sol, is_wide=True)


def gen_freq_table_full():
    """One freq table, three parts asking mean/median/mode."""
    values, freqs = _make_freq_table(n_values=ri(4,6), min_v=1, max_v=9)
    total_f = sum(freqs)
    total_fx = sum(v * f for v, f in zip(values, freqs))
    mean = round(total_fx / total_f, 2)
    expanded = []
    for v, f in zip(values, freqs):
        expanded.extend([v] * f)
    med = _median(expanded)
    max_f = max(freqs)
    modes = [v for v, f in zip(values, freqs) if f == max_f]
    tbl = _freq_table_latex(values, freqs)

    fx_terms = "+".join(f"{v}\\times{f}" for v,f in zip(values,freqs))
    # Build CF column string for median solution
    cf_str = ""; cf = 0
    for v, f in zip(values, freqs):
        cf += f
        cf_str += f"{v}: CF={cf},\\ "

    pa = _part(
        f"\\text{{Calculate the mean.}}",
        f"\\bar{{x}} = {_fmt(mean)}",
        f"\\bar{{x}}=\\dfrac{{\\sum fx}}{{\\sum f}}=\\dfrac{{{fx_terms}}}{{{total_f}}}=\\dfrac{{{total_fx}}}{{{total_f}}}={_fmt(mean)}",
        is_wide=True
    )
    pb = _part(
        f"\\text{{Find the median.}}",
        f"\\text{{Median}} = {_fmt(med)}",
        f"n={total_f}\\quad \\text{{Position }}\\frac{{n+1}}{{2}}={round((total_f+1)/2,1)}"
        f"\\quad \\text{{Build CF: }}{cf_str.rstrip(', ')}\\quad \\text{{Median}}={_fmt(med)}",
        is_wide=True
    )
    pc = _part(
        f"\\text{{(c) Find the mode.}}",
        f"\\text{{Mode}} = {', '.join(str(m) for m in modes)}",
        f"\\text{{Highest frequency = }}{max_f}\\text{{ at }}x={', '.join(str(m) for m in modes)}",
        is_wide=True
    )
    parts = [pa, pb, pc]
    for j, p in enumerate(parts):
        p["label"] = PART_LABELS[j]
        p["_tbl"] = tbl   # carry table for exercise-level render
    return parts


def gen_freq_table_median_find_x():
    """
    Frequency table with unknown x in one frequency.
    Given the median, find the largest/smallest possible x.
    """
    scores = [5, 6, 7, 8]
    # Fix freqs for known positions, x in position 2 (score=7)
    f5 = ri(3, 6); f6 = ri(5, 9); f8 = ri(4, 8)
    # Median = 6 means cumulative up to 6 >= n/2
    # We need to find range of x
    # total_f = f5 + f6 + x + f8
    # median position = (total_f+1)/2
    # For median=6: cumulative up to 6 (f5+f6) >= (total_f+1)/2
    #               cumulative up to 5 (f5) < (total_f+1)/2
    target_median = 6
    # f5 + f6 >= ceil((f5+f6+x+f8+1)/2)   →  smallest x
    # f5 < ceil((f5+f6+x+f8+1)/2)           →  always true for reasonable x
    # Max x: f5+f6 >= (total_f+1)/2  → 2(f5+f6) >= total_f+1
    #         → 2(f5+f6) >= f5+f6+x+f8+1  → f5+f6-f8-1 >= x
    x_max = f5 + f6 - f8 - 1
    if x_max < 1:
        f8 = ri(1, 3); x_max = f5 + f6 - f8 - 1
    # Min x: f5 < (total_f+1)/2 (median not in score 5 group)
    # This is usually satisfied; x_min = 0 or 1
    x_min = 0
    tbl = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
           f"\\begin{{array}}{{lcccc}}\n"
           f"\\hline \\text{{Score}} & 5 & 6 & 7 & 8 \\\\[4pt]\n"
           f"\\hline \\text{{Freq}} & {f5} & {f6} & x & {f8} \\\\[4pt]\n"
           f"\\hline\n\\end{{array}}}}")
    q = (f"\\text{{Median}} = 6\\\\[6pt]{tbl}")
    a = f"x_{{\\min}} = {x_min},\\ x_{{\\max}} = {x_max}"
    sol = (f"\\text{{For median = 6: cumulative freq up to 6}} \\geq \\frac{{n+1}}{{2}}"
           f"\\quad \\text{{Largest: }}{f5}+{f6}-{f8}-1={x_max}"
           f"\\quad \\text{{Smallest: }}{x_min}")
    return _part(q, a, sol, is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT3 — GROUPED FREQUENCY TABLES
# ══════════════════════════════════════════════════════════════════

def _make_grouped_table(n_groups=5, start=10, width=5, min_f=3, max_f=20):
    """Returns (lower_bounds, upper_bounds, midpoints, freqs)."""
    lowers = [start + i * width for i in range(n_groups)]
    uppers = [l + width for l in lowers]
    mids   = [l + width/2 for l in lowers]
    freqs  = [ri(min_f, max_f) for _ in range(n_groups)]
    return lowers, uppers, mids, freqs

def _grouped_table_latex(lowers, uppers, freqs,
                          var="x", unit="", show_mid=False, mids=None):
    rows = ""
    for i, (l, u, f) in enumerate(zip(lowers, uppers, freqs)):
        mid_col = f" & {_fmt(mids[i])}" if show_mid else ""
        rows += f"{l} \\leq {var} < {u} {mid_col} & {f} \\\\[4pt]\n\\hline "
    mid_header = " & \\text{Midpoint}" if show_mid else ""
    cols = f"l{'c' if show_mid else ''}c"
    return (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
            f"\\begin{{array}}{{{cols}}}\n"
            f"\\hline \\text{{Class}}{mid_header} & \\text{{Frequency}} \\\\[4pt]\n"
            f"\\hline {rows}\\end{{array}}}}")

def gen_grouped_mean():
    n_g = ri(4, 6)
    lowers, uppers, mids, freqs = _make_grouped_table(n_g, ri(10,30), ri(4,10))
    total_f = sum(freqs)
    total_fx = sum(m * f for m, f in zip(mids, freqs))
    mean = round(total_fx / total_f, 1)
    tbl = _grouped_table_latex(lowers, uppers, freqs, show_mid=True, mids=mids)
    q = tbl
    a = f"\\text{{Estimated mean}} \\approx {_fmt(mean)}"
    terms = "+".join(f"{_fmt(m)}\\times{f}" for m,f in zip(mids,freqs))
    sol = (f"\\frac{{{terms}}}{{{total_f}}}"
           f"= \\frac{{{_fmt(total_fx)}}}{{{total_f}}} \\approx {_fmt(mean)}")
    return _part(q, a, sol, _fmt(mean), is_wide=True)


def gen_grouped_modal_class():
    n_g = ri(4, 6)
    lowers, uppers, mids, freqs = _make_grouped_table(n_g, ri(5,20), ri(5,10))
    max_f = max(freqs)
    idx = freqs.index(max_f)
    modal = f"{lowers[idx]} \\leq x < {uppers[idx]}"
    tbl = _grouped_table_latex(lowers, uppers, freqs)
    q = tbl
    a = f"\\text{{Modal class: }}{modal}"
    sol = f"\\text{{Highest frequency = }}{max_f}\\text{{, class: }}{modal}"
    return _part(q, a, sol, is_wide=True)


def gen_grouped_median_class():
    n_g = ri(4, 6)
    lowers, uppers, mids, freqs = _make_grouped_table(n_g, ri(5,20), ri(5,10))
    total_f = sum(freqs)
    mid_pos = total_f / 2
    cf = 0
    for i, (l, u, f) in enumerate(zip(lowers, uppers, freqs)):
        cf += f
        if cf >= mid_pos:
            median_class = f"{l} \\leq x < {u}"
            break
    tbl = _grouped_table_latex(lowers, uppers, freqs)
    q = tbl
    a = f"\\text{{Median class: }}{median_class}"
    sol = (f"n={total_f}\\quad \\frac{{n}}{{2}}={_fmt(mid_pos)}"
           f"\\quad \\text{{Median class: }}{median_class}")
    return _part(q, a, sol, is_wide=True)


def gen_grouped_full():
    """One grouped table, three parts: modal class / median class / mean."""
    n_g = ri(4, 6)
    lowers, uppers, mids, freqs = _make_grouped_table(n_g, ri(5,20), ri(5,10))
    total_f = sum(freqs)
    total_fx = sum(m * f for m, f in zip(mids, freqs))
    mean = round(total_fx / total_f, 1)
    max_f = max(freqs); idx_mode = freqs.index(max_f)
    modal = f"{lowers[idx_mode]} \\leq x < {uppers[idx_mode]}"
    mid_pos = total_f / 2; cf = 0
    for l, u, f in zip(lowers, uppers, freqs):
        cf += f
        if cf >= mid_pos:
            median_class = f"{l} \\leq x < {u}"; break
    tbl = _grouped_table_latex(lowers, uppers, freqs, show_mid=True, mids=mids)
    fx_terms = "+".join(f"{_fmt(m)}\\times{f}" for m,f in zip(mids,freqs))

    pa = _part(
        "\\text{{Write down the modal class.}}",
        f"\\text{{Modal class: }}{modal}",
        f"\\text{{Highest frequency = }}{max_f}\\text{{ → modal class: }}{modal}",
        is_wide=True
    )
    pb = _part(
        "\\text{{Identify the median class.}}",
        f"\\text{{Median class: }}{median_class}",
        f"n={total_f}\\quad \\frac{{n}}{{2}}={_fmt(mid_pos)}"
        f"\\quad \\text{{Build CF to find class containing position }}{_fmt(mid_pos)}"
        f"\\quad \\text{{Median class: }}{median_class}",
        is_wide=True
    )
    pc = _part(
        "\\text{{Estimate the mean.}}",
        f"\\bar{{x}} \\approx {_fmt(mean)}",
        f"\\bar{{x}}=\\dfrac{{\\sum fx}}{{\\sum f}}=\\dfrac{{{fx_terms}}}{{{total_f}}}"
        f"=\\dfrac{{{_fmt(total_fx)}}}{{{total_f}}}\\approx{_fmt(mean)}",
        is_wide=True
    )
    parts = [pa, pb, pc]
    for j, p in enumerate(parts):
        p["label"] = PART_LABELS[j]
        p["_tbl"] = tbl
    return parts


def gen_grouped_combined_mean():
    """
    Two groups with different sizes and means — find combined mean.
    e.g. 100 sentences with mean 18, next 50 with mean 17.3 → mean of all 150.
    """
    n1 = random.choice([50, 80, 100, 120])
    n2 = random.choice([20, 30, 50])
    m1 = round(random.uniform(12, 25), 1)
    m2 = round(random.uniform(10, 24), 1)
    combined_mean = round((n1 * m1 + n2 * m2) / (n1 + n2), 2)
    q = (f"n_1={n1},\\ \\bar{{x}}_1={m1}"
         f"\\\\[4pt]n_2={n2},\\ \\bar{{x}}_2={m2}")
    a = f"\\text{{Combined mean}} = {_fmt(combined_mean)}"
    sol = (f"\\frac{{{n1}\\times{m1}+{n2}\\times{m2}}}{{{n1}+{n2}}}"
           f"=\\frac{{{round(n1*m1,1)}+{round(n2*m2,1)}}}{{{n1+n2}}}"
           f"=\\frac{{{round(n1*m1+n2*m2,1)}}}{{{n1+n2}}}"
           f"={_fmt(combined_mean)}")
    return _part(q, a, sol, _fmt(combined_mean), is_wide=True)


def gen_grouped_find_missing_freq():
    """
    Grouped table with two unknown frequencies a and b.
    Given total n and estimated mean, find a and b.
    """
    # Fixed structure: 5 classes, two unknowns in last two
    width = 10; start = 20
    lowers = [start + i*width for i in range(5)]
    uppers = [l + width for l in lowers]
    mids   = [l + width/2 for l in lowers]
    known_freqs = [ri(8, 20), ri(15, 30), ri(25, 45)]
    n = random.choice([80, 100, 120, 150])
    mean_est = round(random.uniform(mids[1], mids[3]), 0)

    # Solve: known_sum + a + b = n
    #        known_fx + mids[3]*a + mids[4]*b = mean_est * n
    known_sum = sum(known_freqs)
    known_fx  = sum(m*f for m,f in zip(mids[:3], known_freqs))
    # a + b = n - known_sum
    ab_sum = n - known_sum
    # mids[3]*a + mids[4]*b = mean_est*n - known_fx
    ab_fx = mean_est * n - known_fx
    # Solve: a = (ab_fx - mids[4]*ab_sum) / (mids[3] - mids[4])
    denom = mids[3] - mids[4]
    if denom == 0:
        denom = width
    # Guarantee positive a and b — brute force with fixed safe values
    a_val = round((ab_fx - mids[4] * ab_sum) / denom)
    b_val = ab_sum - a_val
    if a_val < 2 or b_val < 2:
        # Use a guaranteed-valid combination
        n = 100; known_freqs = [15, 25, 35]; known_sum = 75
        # Pick mean_est so that a and b come out positive and reasonable
        # With mids = [25,35,45,55,65], target a~10, b~15
        # a+b=25, 55a+65b=mean_est*100-known_fx
        # Set a=10, b=15: 55*10+65*15=550+975=1525
        # known_fx=25*15+35*25+45*35=375+875+1575=2825
        # mean_est*100=1525+2825=4350 → mean_est=43.5
        known_fx = 25*15 + 35*25 + 45*35
        a_val = 10; b_val = 15
        ab_sum = 25; mean_est = 43.5; ab_fx = 1525.0

    all_freqs = known_freqs + [a_val, b_val]
    # Build table with a and b as unknowns
    rows = ""
    for i, (l, u, f) in enumerate(zip(lowers, uppers, all_freqs)):
        fstr = "a" if i == 3 else ("b" if i == 4 else str(f))
        rows += f"{l} \\leq x < {u} & {fstr} \\\\[4pt]\n\\hline "
    tbl = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
           f"\\begin{{array}}{{lc}}\n"
           f"\\hline \\text{{Class}} & \\text{{Frequency}} \\\\[4pt]\n"
           f"\\hline {rows}\\end{{array}}}}")
    q = (f"n = {n},\\quad \\bar{{x}} \\approx {_fmt(mean_est)}"
         f"\\\\[6pt]{tbl}")
    a_ans = f"a = {a_val},\\ b = {b_val}"
    sol = (f"\\text{{Step 1: }}a+b={n}-{known_sum}={ab_sum}"
           f"\\\\[4pt]\\text{{Step 2: }}\\Sigma fx={_fmt(mean_est)}\\times{n}={_fmt(mean_est*n)}"
           f"\\\\[4pt]\\text{{Known }}\\Sigma fx={_fmt(known_fx)}"
           f"\\quad\\Rightarrow {_fmt(mids[3])}a+{_fmt(mids[4])}b={_fmt(ab_fx)}"
           f"\\\\[4pt]\\text{{Step 3: Solve simultaneously: }}"
           f"a={a_val},\\ b={b_val}")
    return _part(q, a_ans, sol, f"a={a_val}, b={b_val}", is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT4 — CUMULATIVE FREQUENCY
# ══════════════════════════════════════════════════════════════════

def _make_cf_data(n_groups=6, start=10, width=10, min_f=4, max_f=25):
    lowers = [start + i*width for i in range(n_groups)]
    uppers = [l + width for l in lowers]
    freqs  = [ri(min_f, max_f) for _ in range(n_groups)]
    cum    = []
    cf = 0
    for f in freqs:
        cf += f
        cum.append(cf)
    return lowers, uppers, freqs, cum

def gen_cumfreq_table():
    """Build cumulative frequency table from frequency table."""
    lowers, uppers, freqs, cum = _make_cf_data(ri(5,7), ri(10,40), ri(5,10))
    total = cum[-1]
    freq_rows = " \\\\[4pt]\n\\hline ".join(
        f"{l} \\leq x < {u} & {f}" for l,u,f in zip(lowers,uppers,freqs))
    tbl_freq = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
                f"\\begin{{array}}{{lc}}\n"
                f"\\hline \\text{{Class}} & f \\\\[4pt]\n"
                f"\\hline {freq_rows} \\\\[4pt]\n"
                f"\\hline\n\\end{{array}}}}")
    cum_rows = " \\\\[4pt]\n\\hline ".join(
        f"x < {u} & {c}" for u,c in zip(uppers,cum))
    tbl_cum = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
               f"\\begin{{array}}{{lc}}\n"
               f"\\hline x & \\text{{Cum. Freq}} \\\\[4pt]\n"
               f"\\hline {cum_rows} \\\\[4pt]\n"
               f"\\hline\n\\end{{array}}}}")
    q = tbl_freq
    # Strip \renewcommand so MathJax renders cleanly
    a = _strip_rc(tbl_cum)
    sol = f"\\text{{Running totals: }}" + ", ".join(str(c) for c in cum)
    p = _part(q, a, sol, is_wide=True)
    # SVG of the CF curve
    p["ex_svg"] = svg_cumfreq(uppers, cum, total,
                              xlabel=f"x", title="Cumulative Frequency Curve")
    return p


def gen_cumfreq_read():
    """Read values from cumulative frequency table — shows CF table, asks two questions."""
    lowers, uppers, freqs, cum = _make_cf_data(ri(5,7), ri(20,50), ri(10,20))
    total = cum[-1]
    idx = ri(1, len(uppers)-2)
    val = uppers[idx]
    below = cum[idx]
    above = total - below
    # Build CF table
    cum_rows = " \\\\[4pt]\n\\hline ".join(
        f"x < {u} & {c}" for u,c in zip(uppers,cum))
    tbl = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
           f"\\begin{{array}}{{lc}}\n"
           f"\\hline x & \\text{{Cum. Freq}} \\\\[4pt]\n"
           f"\\hline {cum_rows} \\\\[4pt]\n"
           f"\\hline\n\\end{{array}}}}")
    q = (f"{tbl}"
         f"\\\\[8pt]\\text{{(a) Items}} \\leq {val}\\text{{?}}"
         f"\\\\[6pt]\\text{{(b) Items}} > {val}\\text{{?}}")
    a = f"\\text{{(a) }}{below}\\quad\\text{{(b) }}{above}"
    sol = (f"\\text{{(a) CF at }}{val}={below}"
           f"\\quad\\text{{(b) }}{total}-{below}={above}")
    return _part(q, a, sol, is_wide=True)


def gen_cumfreq_iqr():
    """One CF dataset: (a) complete table (b) median (c) IQR (d) above value."""
    lowers, uppers, freqs, cum = _make_cf_data(ri(5,7), ri(10,30), ri(10,20))
    total = cum[-1]

    def interp(frac):
        target = frac * total
        for i in range(len(cum)):
            prev_cf = 0 if i == 0 else cum[i-1]
            if cum[i] >= target >= prev_cf:
                x_prev = lowers[0] if i == 0 else uppers[i-1]
                x_cur  = uppers[i]
                if cum[i] == prev_cf:
                    return x_prev
                t = (target - prev_cf) / (cum[i] - prev_cf)
                return round(x_prev + t * (x_cur - x_prev), 1)
        return uppers[-1]

    q1v = interp(0.25); q3v = interp(0.75); iqr = round(q3v - q1v, 1)
    med = interp(0.5)

    # Estimate above a value near the 70th percentile
    above_val = round(interp(0.65))
    idx_av = 0
    for i, u in enumerate(uppers):
        if u >= above_val:
            idx_av = i; break
    prev_cf_av = 0 if idx_av == 0 else cum[idx_av-1]
    x_prev_av  = lowers[0] if idx_av == 0 else uppers[idx_av-1]
    t_av = (above_val - x_prev_av) / (uppers[idx_av] - x_prev_av) if uppers[idx_av] != x_prev_av else 0
    cf_at_av = round(prev_cf_av + t_av * (cum[idx_av] - prev_cf_av))
    above_count = total - cf_at_av

    # Frequency table latex
    freq_rows = " \\\\[4pt]\n\\hline ".join(
        f"{l} \\leq x < {u} & {f}" for l,u,f in zip(lowers,uppers,freqs))
    tbl_freq = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
                f"\\begin{{array}}{{lc}}\n"
                f"\\hline \\text{{Class}} & f \\\\[4pt]\n"
                f"\\hline {freq_rows} \\\\[4pt]\n"
                f"\\hline\n\\end{{array}}}}")

    # CF table latex
    cum_rows = " \\\\[4pt]\n\\hline ".join(
        f"x < {u} & {c}" for u,c in zip(uppers,cum))
    tbl_cum = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
               f"\\begin{{array}}{{lc}}\n"
               f"\\hline x & \\text{{Cum. Freq}} \\\\[4pt]\n"
               f"\\hline {cum_rows} \\\\[4pt]\n"
               f"\\hline\n\\end{{array}}}}")

    svg = svg_cumfreq(uppers, cum, total, xlabel="x",
                      title="Cumulative Frequency Curve")

    pa = _part(
        "\\text{{Complete the CF table.}}",
        tbl_cum,
        f"\\text{{Running totals: }}" + ", ".join(str(c) for c in cum),
        is_wide=True
    )
    pb = _part(
        "\\text{{Estimate the median from the graph.}}",
        f"\\text{{Median}} \\approx {_fmt(med)}",
        f"\\text{{Read at }}"
        f"\\frac{{n}}{{2}}=\\frac{{{total}}}{{2}}={total//2}\\text{{ on CF axis}}"
        f"\\quad \\text{{Median}}\\approx{_fmt(med)}",
        is_wide=True
    )
    pc = _part(
        "\\text{{Estimate the IQR.}}",
        f"\\text{{IQR}} = {_fmt(iqr)}",
        f"Q_1\\approx{_fmt(q1v)}\\text{{ (read at }}{round(0.25*total,0)}\\text{{)}}"
        f"\\quad Q_3\\approx{_fmt(q3v)}\\text{{ (read at }}{round(0.75*total,0)}\\text{{)}}"
        f"\\quad \\text{{IQR}}={_fmt(q3v)}-{_fmt(q1v)}={_fmt(iqr)}",
        is_wide=True
    )
    pd_ = _part(
        f"\\text{{How many items are above }}{above_val}?",
        f"\\approx {above_count}\\text{{ items}}",
        f"\\text{{Read CF at }}{above_val}\\approx{cf_at_av}"
        f"\\quad \\text{{Above: }}{total}-{cf_at_av}={above_count}",
        is_wide=True
    )
    parts = [pa, pb, pc, pd_]
    for j, p in enumerate(parts):
        p["label"] = PART_LABELS[j]
        p["_tbl"] = tbl_freq
        p["ex_svg"] = svg
    return parts


def gen_cumfreq_above_value():
    """Estimate how many items lie above a given value."""
    lowers, uppers, freqs, cum = _make_cf_data(ri(5,7), ri(10,40), ri(10,20))
    total = cum[-1]
    # Pick value between penultimate and last upper bound
    idx = ri(len(uppers)//2, len(uppers)-2)
    val = round(lowers[idx] + random.uniform(0.3, 0.8) *
                (uppers[idx] - lowers[idx]), 0)
    # Interpolate CF at val
    prev_cf = 0 if idx == 0 else cum[idx-1]
    x_prev  = lowers[0] if idx == 0 else uppers[idx-1]
    t = (val - x_prev) / (uppers[idx] - x_prev)
    cf_val  = round(prev_cf + t * (cum[idx] - prev_cf))
    above   = total - cf_val
    # Build CF table for context
    cum_rows2 = " \\\\[4pt]\n\\hline ".join(
        f"x < {u} & {c}" for u,c in zip(uppers,cum))
    tbl2 = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
            f"\\begin{{array}}{{lc}}\n"
            f"\\hline x & \\text{{CF}} \\\\[4pt]\n"
            f"\\hline {cum_rows2} \\\\[4pt]\n"
            f"\\hline\n\\end{{array}}}}")
    q = (f"{tbl2}\\\\[8pt]"
         f"\\text{{How many items above }}{int(val)}?")
    a = f"\\approx {above}"
    sol = (f"\\text{{Read CF at }}{int(val)}\\approx{cf_val}"
           f"\\quad {total}-{cf_val}={above}")
    p = _part(q, a, sol, str(above), is_wide=True)
    p["svg"] = svg_cumfreq(uppers, cum, total,
                           xlabel="x", title="Cumulative Frequency")
    return p


def gen_cumfreq_find_ab():
    """
    Cumulative frequency table with two missing values A and B.
    Student finds them from partial CF table.
    """
    lowers, uppers, freqs, cum = _make_cf_data(5, ri(10,30), ri(5,10))
    # Hide positions 1 and 3 (0-indexed)
    A_idx, B_idx = 1, 3
    A_val, B_val = cum[A_idx], cum[B_idx]
    rows = ""
    for i, (u, c) in enumerate(zip(uppers, cum)):
        cstr = "A" if i == A_idx else ("B" if i == B_idx else str(c))
        rows += f"x < {u} & {cstr} \\\\[4pt]\n\\hline "
    tbl = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
           f"\\begin{{array}}{{lc}}\n"
           f"\\hline x & \\text{{Cum. Freq}} \\\\[4pt]\n"
           f"\\hline {rows}\\end{{array}}}}")
    q = (f"\\text{{Find A and B.}}"
         f"\\\\[6pt]{tbl}")
    a = f"A = {A_val},\\ B = {B_val}"
    sol = (f"A = {cum[A_idx-1]}+{freqs[A_idx]}={A_val}"
           f"\\quad B = {cum[B_idx-1]}+{freqs[B_idx]}={B_val}")
    return _part(q, a, sol, f"A={A_val}, B={B_val}", is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT5 — BOX PLOTS & IQR
# ══════════════════════════════════════════════════════════════════

def gen_boxplot_iqr():
    """Calculate IQR from a dataset."""
    n = random.choice([9, 11, 13, 15])
    data = sorted([ri(2, 30) for _ in range(n)])
    q1, med, q3 = _quartiles(data)
    iqr = q3 - q1
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = f"\\text{{IQR}} = {_fmt(iqr)}"
    sol = (f"Q_1={_fmt(q1)},\\ Q_3={_fmt(q3)}"
           f"\\quad \\text{{IQR}}={_fmt(q3)}-{_fmt(q1)}={_fmt(iqr)}")
    p = _part(q, a, sol, _fmt(iqr))
    p["svg"] = svg_box_plot(data[0], q1, med, q3, data[-1],
                            label="Box Plot")
    return p


def gen_boxplot_draw():
    """Given five-number summary, describe/draw box plot."""
    min_v = ri(2, 15)
    q1    = min_v + ri(3, 8)
    med   = q1 + ri(2, 6)
    q3    = med + ri(2, 6)
    max_v = q3 + ri(3, 10)
    iqr   = q3 - q1
    q = (f"\\min={min_v},\\ Q_1={q1},\\ \\text{{med}}={med},"
         f"\\ Q_3={q3},\\ \\max={max_v}")
    a = f"\\text{{IQR}}={iqr}"
    sol = f"\\text{{IQR}}=Q_3-Q_1={q3}-{q1}={iqr}"
    p = _part(q, a, sol, str(iqr), is_wide=True)
    p["sol_svg"] = svg_box_plot(min_v, q1, med, q3, max_v,
                                label="Box Plot")
    return p


def gen_boxplot_outlier():
    """
    Identify outliers using 1.5 × IQR rule.
    Show that a given value is (or isn't) an outlier.
    """
    n = random.choice([9, 11, 13])
    core = sorted([ri(10, 70) for _ in range(n - 1)])
    outlier_val = core[-1] + ri(20, 50)  # guaranteed outlier
    data = sorted(core + [outlier_val])
    q1, med, q3 = _quartiles(data)
    iqr = q3 - q1
    upper_fence = q3 + 1.5 * iqr
    lower_fence = q1 - 1.5 * iqr
    data_str = ",\\ ".join(str(x) for x in data)
    q = data_str
    a = (f"Q_1={_fmt(q1)},\\ Q_3={_fmt(q3)},\\ \\text{{IQR}}={_fmt(iqr)}"
         f"\\\\\\text{{Upper fence}}={_fmt(upper_fence)}"
         f"\\\\{outlier_val}>{_fmt(upper_fence)}\\Rightarrow\\text{{outlier}}")
    sol = (f"\\text{{Step 1: }}Q_1={_fmt(q1)},\\ Q_3={_fmt(q3)}"
           f"\\\\[4pt]\\text{{Step 2: IQR}}=Q_3-Q_1={_fmt(q3)}-{_fmt(q1)}={_fmt(iqr)}"
           f"\\\\[4pt]\\text{{Step 3: Upper fence}}=Q_3+1.5\\times\\text{{IQR}}"
           f"={_fmt(q3)}+1.5\\times{_fmt(iqr)}={_fmt(upper_fence)}"
           f"\\\\[4pt]\\text{{Step 4: }}{outlier_val}>{_fmt(upper_fence)}"
           f"\\therefore\\text{{ outlier }}\\checkmark")
    # Box plot whisker ends at last non-outlier
    last_non_outlier = max(x for x in data if x <= upper_fence)
    p = _part(q, a, sol, is_wide=True)
    p["svg"] = svg_box_plot(
        data[0], q1, med, q3, last_non_outlier,
        outliers=[outlier_val], label="Box Plot with Outlier"
    )
    return p


def gen_boxplot_find_unknowns():
    """
    Ordered list with unknowns h, j, k satisfying:
    - given median
    - given mode
    - given range
    Find h, j, k.
    Pattern: h, a, b, c, j, d, k, k
    """
    a_v = ri(5, 9); b_v = a_v + ri(0,1); c_v = b_v + ri(1,2)
    d_v = ri(c_v+2, c_v+8)
    # k is mode (appears twice, must be > d_v)
    k = d_v + ri(2, 6)
    # median of 8 values = mean of 4th and 5th = mean(c_v, j)
    median_target = ri(c_v+1, k-1)
    j = 2 * median_target - c_v
    if j <= c_v or j >= d_v:
        j = c_v + ri(2, 4)
        median_target = (c_v + j) / 2
    # range = k - h
    range_target = ri(k - a_v + 2, k - 2)
    h = k - range_target
    if h >= a_v:
        h = a_v - ri(1, 3)
        range_target = k - h

    q = (f"h,\\ {a_v},\\ {b_v},\\ {c_v},\\ j,\\ {d_v},\\ k,\\ k"
         f"\\\\[6pt]\\text{{Median}}={_fmt(median_target)},\\ "
         f"\\text{{Mode}}={k},\\ "
         f"\\text{{Range}}={range_target}")
    a = f"h={h},\\ j={j},\\ k={k}"
    sol = (f"k={k}\\text{{ (mode, appears twice)}}"
           f"\\quad h=k-{range_target}={h}\\text{{ (range)}}"
           f"\\quad j=2\\times{_fmt(median_target)}-{c_v}={j}\\text{{ (median)}}")
    return _part(q, a, sol, f"h={h}, j={j}, k={k}", is_wide=True)



def gen_boxplot_read():
    """Type 2: drawn box plot, students read Q1/Q2/Q3/IQR from diagram."""
    min_v = ri(5, 20)
    q1    = min_v + ri(4, 10)
    med   = q1 + ri(3, 8)
    q3    = med + ri(3, 8)
    max_v = q3 + ri(4, 12)
    iqr   = q3 - q1

    svg = svg_box_plot_grid(min_v, q1, med, q3, max_v)

    pa = _part("\\text{Write down the minimum value.}",
               f"\\text{{Min}} = {min_v}",
               f"\\text{{Read the left whisker end: }}{min_v}")
    pb = _part(f"\\text{{Write down }}Q_1.",
               f"Q_1 = {q1}",
               f"\\text{{Read the left edge of the box: }}{q1}")
    pc = _part("\\text{Write down the median.}",
               f"\\text{{Median}} = {med}",
               f"\\text{{Read the line inside the box: }}{med}")
    pd = _part(f"\\text{{Write down }}Q_3.",
               f"Q_3 = {q3}",
               f"\\text{{Read the right edge of the box: }}{q3}")
    pe = _part("\\text{Calculate the IQR.}",
               f"\\text{{IQR}} = {iqr}",
               f"\\text{{IQR}} = Q_3 - Q_1 = {q3} - {q1} = {iqr}")

    parts = [pa, pb, pc, pd, pe]
    for j, p in enumerate(parts):
        p["label"] = PART_LABELS[j]
        p["ex_svg"] = svg
    return parts


def gen_cumfreq_full():
    """Type 2: one CF dataset — complete table, read median/IQR/above from curve."""
    lowers, uppers, freqs, cum = _make_cf_data(ri(5,7), ri(10,30), ri(8,18))
    total = cum[-1]

    def interp(frac):
        target = frac * total
        for i in range(len(cum)):
            prev_cf = 0 if i == 0 else cum[i-1]
            if cum[i] >= target >= prev_cf:
                x_prev = lowers[0] if i == 0 else uppers[i-1]
                x_cur  = uppers[i]
                if cum[i] == prev_cf:
                    return x_prev
                t = (target - prev_cf) / (cum[i] - prev_cf)
                return round(x_prev + t * (x_cur - x_prev), 1)
        return uppers[-1]

    q1v  = interp(0.25)
    med  = interp(0.50)
    q3v  = interp(0.75)
    iqr  = round(q3v - q1v, 1)

    # Above value near 70th percentile
    above_val = int(round(interp(0.68)))
    idx_av = next((i for i,u in enumerate(uppers) if u >= above_val), len(uppers)-1)
    prev_cf_av = 0 if idx_av == 0 else cum[idx_av-1]
    x_prev_av  = lowers[0] if idx_av == 0 else uppers[idx_av-1]
    denom_av   = uppers[idx_av] - x_prev_av
    t_av = (above_val - x_prev_av) / denom_av if denom_av else 0
    cf_at_av   = round(prev_cf_av + t_av * (cum[idx_av] - prev_cf_av))
    above_count = total - cf_at_av

    # Frequency table (no CF column — student completes it)
    freq_rows = " \\\\[4pt]\n\\hline ".join(
        f"{l} \\leq x < {u} & {f}" for l,u,f in zip(lowers,uppers,freqs))
    tbl_freq = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
                f"\\begin{{array}}{{lc}}\n"
                f"\\hline \\text{{Class}} & f \\\\[4pt]\n"
                f"\\hline {freq_rows} \\\\[4pt]\n"
                f"\\hline\n\\end{{array}}}}")

    # Completed CF table (for solution)
    cum_rows_sol = " \\\\[4pt]\n\\hline ".join(
        f"x < {u} & {c}" for u,c in zip(uppers,cum))
    tbl_cum_sol = (f"{{\\renewcommand{{\\arraystretch}}{{1.6}}"
                   f"\\begin{{array}}{{lc}}\n"
                   f"\\hline x & \\text{{CF}} \\\\[4pt]\n"
                   f"\\hline {cum_rows_sol} \\\\[4pt]\n"
                   f"\\hline\n\\end{{array}}}}")

    svg = svg_cumfreq(uppers, cum, total,
                      xlabel="x", title="Cumulative Frequency Curve")

    # Strip \renewcommand from answer table — MathJax renders array natively
    tbl_cum_ans = _strip_rc(tbl_cum_sol)
    pa = _part(
        "\\text{Complete the cumulative frequency table.}",
        tbl_cum_ans,
        f"\\text{{Running totals: }}" + ", ".join(str(c) for c in cum),
        is_wide=True
    )
    pb = _part(
        "\\text{Estimate the median from the graph.}",
        f"\\text{{Median}} \\approx {_fmt(med)}",
        f"\\text{{Read at }}\\frac{{n}}{{2}}=\\frac{{{total}}}{{2}}={total//2}"
        f"\\quad \\Rightarrow \\text{{Median}}\\approx{_fmt(med)}"
    )
    pc = _part(
        f"\\text{{Estimate }}Q_1\\text{{ and }}Q_3.",
        f"Q_1 \\approx {_fmt(q1v)},\\quad Q_3 \\approx {_fmt(q3v)}",
        f"Q_1\\text{{: read at }}\\frac{{n}}{{4}}={round(total/4,1)}"
        f"\\Rightarrow Q_1\\approx{_fmt(q1v)}"
        f"\\\\[4pt]Q_3\\text{{: read at }}\\frac{{3n}}{{4}}={round(3*total/4,1)}"
        f"\\Rightarrow Q_3\\approx{_fmt(q3v)}"
    )
    pd = _part(
        "\\text{Calculate the IQR.}",
        f"\\text{{IQR}} = {_fmt(iqr)}",
        f"\\text{{IQR}} = Q_3 - Q_1 = {_fmt(q3v)} - {_fmt(q1v)} = {_fmt(iqr)}"
    )
    pe = _part(
        f"\\text{{Estimate how many items are above }}{above_val}.",
        f"\\approx {above_count}\\text{{ items}}",
        f"\\text{{Read CF at }}{above_val}\\approx{cf_at_av}"
        f"\\quad {total}-{cf_at_av}={above_count}"
    )

    parts = [pa, pb, pc, pd, pe]
    for j, p in enumerate(parts):
        p["label"] = PART_LABELS[j]
        p["_tbl"] = tbl_freq
        p["ex_svg"] = svg
    return parts


def _strip_rc(tbl):
    """Strip \\renewcommand prefix for MathJax rendering (it handles arrays natively)."""
    import re as _re
    t = _re.sub(r'^\{\\renewcommand\{\\arraystretch\}\{[0-9.]+\}', '', tbl)
    if t != tbl and t.endswith('}'):
        t = t[:-1]
    return t

# ══════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    # LT1 — Averages from a list
    "mean_simple":           gen_mean_simple,
    "median_simple":         gen_median_simple,
    "mode_simple":           gen_mode_simple,
    "range_simple":          gen_range_simple,
    "averages_combined":     gen_averages_combined,
    "mean_find_missing":     gen_mean_find_missing,
    "stem_leaf_averages":    None,   # multi-part: handled specially in generate()

    # LT2 — Frequency tables
    "freq_table_mean":            gen_freq_table_mean,
    "freq_table_median":          gen_freq_table_median,
    "freq_table_mode":            gen_freq_table_mode,
    "freq_table_full":            None,   # multi-part: one dataset
    "freq_table_median_find_x":   gen_freq_table_median_find_x,

    # LT3 — Grouped frequency tables
    "grouped_mean":               gen_grouped_mean,
    "grouped_modal_class":        gen_grouped_modal_class,
    "grouped_median_class":       gen_grouped_median_class,
    "grouped_full":               None,   # multi-part: one dataset
    "grouped_combined_mean":      gen_grouped_combined_mean,
    "grouped_find_missing_freq":  gen_grouped_find_missing_freq,

    # LT4 — Cumulative frequency
    "cumfreq_full":               None,   # multi-part: full CF exercise
    "cumfreq_table":              gen_cumfreq_table,
    "cumfreq_read":               gen_cumfreq_read,
    "cumfreq_iqr":                None,   # multi-part: one dataset
    "cumfreq_above_value":        gen_cumfreq_above_value,
    "cumfreq_find_ab":            gen_cumfreq_find_ab,

    # LT5 — Box plots
    "boxplot_read":               None,   # multi-part: one box plot
    "boxplot_iqr":                gen_boxplot_iqr,
    "boxplot_draw":               gen_boxplot_draw,
    "boxplot_outlier":            gen_boxplot_outlier,
    "boxplot_find_unknowns":      gen_boxplot_find_unknowns,
}

# ══════════════════════════════════════════════════════════════════
# METADATA
# ══════════════════════════════════════════════════════════════════

METADATA = {
    "mean_simple":          {"subtopic":"Mean from a List","difficulty":"easy","bloom":"remember","lt":["LT1"],"prerequisites":[],"skills":["sum_of_values","division","mean_formula"],"strategy":["1. Add all values.","2. Divide by count."],"common_errors":["Dividing by wrong n."],"remediation":None,"instruction":"Calculate the mean.","flint_prompt":"What do we divide the sum by?"},
    "median_simple":        {"subtopic":"Median from a List","difficulty":"easy","bloom":"remember","lt":["LT1"],"prerequisites":[],"skills":["ordering_data","locating_middle"],"strategy":["1. Order the data.","2. Find middle value."],"common_errors":["Forgetting to sort first."],"remediation":None,"instruction":"Find the median.","flint_prompt":"Have you sorted the data first?"},
    "mode_simple":          {"subtopic":"Mode from a List","difficulty":"easy","bloom":"remember","lt":["LT1"],"prerequisites":[],"skills":["frequency_counting"],"strategy":["1. Count each value.","2. Most frequent = mode."],"common_errors":["Stating frequency not value."],"remediation":None,"instruction":"Find the mode.","flint_prompt":"Which value appears most often?"},
    "range_simple":         {"subtopic":"Range from a List","difficulty":"easy","bloom":"remember","lt":["LT1"],"prerequisites":[],"skills":["max_min","subtraction"],"strategy":["1. Range = max − min."],"common_errors":["Adding instead of subtracting."],"remediation":None,"instruction":"Find the range.","flint_prompt":"Range = largest − smallest."},
    "averages_combined":    {"subtopic":"Mean, Median, Mode and Range","difficulty":"medium","bloom":"apply","lt":["LT1"],"prerequisites":["mean_simple","median_simple","mode_simple","range_simple"],"skills":["all_averages","ordering_data"],"strategy":["1. Sort data.","2. Calculate each measure."],"common_errors":["Median from unsorted data."],"remediation":"median_simple","instruction":"Find the mean, median, mode and range.","flint_prompt":"Tackle one measure at a time."},
    "mean_find_missing":    {"subtopic":"Find Missing Value / Updated Mean","difficulty":"hard","bloom":"apply","lt":["LT1"],"prerequisites":["mean_simple"],"skills":["rearranging_formula","sum_from_mean"],"strategy":["1. Total = mean × n.","2. Subtract known values."],"common_errors":["Using wrong n."],"remediation":"mean_simple","instruction":"Find the missing value or new mean.","flint_prompt":"Find the total first."},
    "stem_leaf_averages":   {"subtopic":"Averages from Stem & Leaf","difficulty":"hard","bloom":"apply","lt":["LT1"],"prerequisites":["median_simple","mode_simple","range_simple"],"skills":["reading_stem_leaf","ordering_data"],"strategy":["1. Read values from diagram.","2. Apply average formulas."],"common_errors":["Misreading leaf values."],"remediation":"median_simple","instruction":"Use the stem and leaf diagram to find the median, range and modal class.","flint_prompt":"Remember: stem × 10 + leaf gives the value."},
    "freq_table_mean":      {"subtopic":"Mean from Frequency Table","difficulty":"easy","bloom":"apply","lt":["LT2"],"prerequisites":["mean_simple"],"skills":["fx_column","sum_of_frequencies"],"strategy":["1. Calculate fx for each row.","2. Mean = Σfx / Σf."],"common_errors":["Dividing by number of rows not Σf."],"remediation":"mean_simple","instruction":"Calculate the mean from the frequency table.","flint_prompt":"Σfx ÷ Σf — not sum of x ÷ number of rows."},
    "freq_table_median":    {"subtopic":"Median from Frequency Table","difficulty":"medium","bloom":"apply","lt":["LT2"],"prerequisites":["median_simple"],"skills":["cumulative_frequency","locating_middle"],"strategy":["1. Build cumulative frequency.","2. Find (n+1)/2 th position."],"common_errors":["Not building CF first."],"remediation":"median_simple","instruction":"Find the median from the frequency table.","flint_prompt":"Build a cumulative frequency column first."},
    "freq_table_mode":      {"subtopic":"Mode from Frequency Table","difficulty":"easy","bloom":"remember","lt":["LT2"],"prerequisites":["mode_simple"],"skills":["reading_frequency_table"],"strategy":["1. Find value with highest frequency."],"common_errors":["Stating frequency not value."],"remediation":"mode_simple","instruction":"Find the mode from the frequency table.","flint_prompt":"Which x has the highest f?"},
    "freq_table_full":      {"subtopic":"Mean, Median & Mode from Table","difficulty":"medium","bloom":"apply","lt":["LT2"],"prerequisites":["freq_table_mean","freq_table_median","freq_table_mode"],"skills":["fx_column","cumulative_frequency","reading_frequency_table"],"strategy":["1. fx column for mean.","2. CF for median.","3. Max f for mode."],"common_errors":["Mixing up methods."],"remediation":"freq_table_mean","instruction":"Find the mean, median and mode from the frequency table.","flint_prompt":"Three separate calculations — do them one at a time."},
    "freq_table_median_find_x": {"subtopic":"Find x Given Median (Frequency Table)","difficulty":"hard","bloom":"analyse","lt":["LT2"],"prerequisites":["freq_table_median"],"skills":["cumulative_frequency","inequality_reasoning"],"strategy":["1. Set up CF inequality.","2. Solve for range of x."],"common_errors":["Off-by-one in CF boundary."],"remediation":"freq_table_median","instruction":"Find the largest and smallest possible values of x such that the median is as given.","flint_prompt":"For median = k: CF up to k must be ≥ n/2."},
    "grouped_mean":         {"subtopic":"Estimated Mean (Grouped)","difficulty":"easy","bloom":"apply","lt":["LT3"],"prerequisites":["freq_table_mean"],"skills":["midpoints","fx_column"],"strategy":["1. Find midpoint of each class.","2. Mean ≈ Σfx / Σf."],"common_errors":["Using class boundary not midpoint."],"remediation":"freq_table_mean","instruction":"Estimate the mean from the grouped frequency table.","flint_prompt":"Use the midpoint of each class interval."},
    "grouped_modal_class":  {"subtopic":"Modal Class (Grouped)","difficulty":"easy","bloom":"remember","lt":["LT3"],"prerequisites":["freq_table_mode"],"skills":["reading_grouped_table"],"strategy":["1. Find class with highest frequency."],"common_errors":["Giving frequency not class."],"remediation":"freq_table_mode","instruction":"Write down the modal class.","flint_prompt":"Modal class = class with highest frequency."},
    "grouped_median_class": {"subtopic":"Median Class (Grouped)","difficulty":"medium","bloom":"apply","lt":["LT3"],"prerequisites":["freq_table_median"],"skills":["cumulative_frequency","locating_middle"],"strategy":["1. Find n/2.","2. Locate which class contains that cumulative position."],"common_errors":["Using n/2 + 1 instead of n/2."],"remediation":"freq_table_median","instruction":"Identify the median class.","flint_prompt":"Find n/2 then locate which class contains that running total."},
    "grouped_full":         {"subtopic":"Modal, Median & Mean (Grouped)","difficulty":"hard","bloom":"analyse","lt":["LT3"],"prerequisites":["grouped_mean","grouped_modal_class","grouped_median_class"],"skills":["midpoints","cumulative_frequency","reading_grouped_table"],"strategy":["1. Modal: highest f.","2. Median class: CF ≥ n/2.","3. Mean: Σfx/Σf with midpoints."],"common_errors":["Confusing modal class with median class."],"remediation":"grouped_mean","instruction":"Find the modal class, median class, and estimated mean.","flint_prompt":"Three separate tasks — work through each in order."},
    "grouped_combined_mean":{"subtopic":"Combined Mean (Two Groups)","difficulty":"hard","bloom":"analyse","lt":["LT3"],"prerequisites":["grouped_mean"],"skills":["weighted_mean","total_from_mean"],"strategy":["1. Total₁ = n₁ × mean₁.","2. Total₂ = n₂ × mean₂.","3. Combined mean = (Total₁+Total₂)/(n₁+n₂)."],"common_errors":["Averaging the two means directly."],"remediation":"grouped_mean","instruction":"Find the combined mean of the two groups.","flint_prompt":"You cannot average two means directly — you need the totals."},
    "grouped_find_missing_freq":{"subtopic":"Find Missing Frequencies (Grouped)","difficulty":"hard","bloom":"analyse","lt":["LT3"],"prerequisites":["grouped_mean"],"skills":["simultaneous_equations","mean_formula"],"strategy":["1. a+b = n − known sum.","2. midpoint·a + midpoint·b = mean·n − known Σfx.","3. Solve simultaneously."],"common_errors":["Setting up equations incorrectly."],"remediation":"grouped_mean","instruction":"Find the values of a and b.","flint_prompt":"Set up two equations: one for total frequency, one for Σfx."},
    "cumfreq_full":         {"subtopic":"Cumulative Frequency — Full Analysis","difficulty":"hard","bloom":"analyse","lt":["LT4"],"prerequisites":["cumfreq_table","cumfreq_iqr"],"skills":["cumulative_frequency","interpolation","quartile_location","iqr_calculation","reading_cf_graph"],"strategy":["1. Complete CF table.","2. Read median at n/2.","3. Q1 at n/4, Q3 at 3n/4.","4. IQR = Q3 − Q1.","5. Above = total − CF at value."],"common_errors":["Wrong quartile positions.","Forgetting to read from graph not table."],"remediation":"cumfreq_iqr","instruction":"Use the frequency table and cumulative frequency graph to answer the questions.","flint_prompt":"Work through each part in order — table first, then graph."},
    "cumfreq_table":        {"subtopic":"Build Cumulative Frequency Table","difficulty":"easy","bloom":"remember","lt":["LT4"],"prerequisites":["grouped_modal_class"],"skills":["running_totals"],"strategy":["1. Add frequencies cumulatively."],"common_errors":["Resetting running total."],"remediation":None,"instruction":"Complete the cumulative frequency table.","flint_prompt":"Each row = previous total + current frequency."},
    "cumfreq_read":         {"subtopic":"Read Cumulative Frequency Table","difficulty":"easy","bloom":"understand","lt":["LT4"],"prerequisites":["cumfreq_table"],"skills":["reading_cf_table","subtraction"],"strategy":["1. Read CF at given value.","2. Above = total − CF."],"common_errors":["Confusing CF with frequency."],"remediation":"cumfreq_table","instruction":"Use the table to answer the questions.","flint_prompt":"For 'more than': total − CF at that value."},
    "cumfreq_iqr":          {"subtopic":"IQR from Cumulative Frequency","difficulty":"medium","bloom":"apply","lt":["LT4"],"prerequisites":["cumfreq_table"],"skills":["interpolation","quartile_location"],"strategy":["1. Q₁ at n/4, Q₃ at 3n/4.","2. Read from CF graph.","3. IQR = Q₃ − Q₁."],"common_errors":["Using n/4 + 1 for Q₁."],"remediation":"cumfreq_table","instruction":"Use the cumulative frequency graph to estimate the IQR.","flint_prompt":"Q₁ is at n/4, Q₃ is at 3n/4 on the CF axis."},
    "cumfreq_above_value":  {"subtopic":"Estimate Frequency Above a Value","difficulty":"hard","bloom":"apply","lt":["LT4"],"prerequisites":["cumfreq_iqr"],"skills":["interpolation","reading_cf_graph"],"strategy":["1. Read CF at value (interpolate).","2. Above = total − CF."],"common_errors":["Reading wrong axis."],"remediation":"cumfreq_iqr","instruction":"Estimate the number of items above the given value.","flint_prompt":"Interpolate between the two surrounding CF points."},
    "cumfreq_find_ab":      {"subtopic":"Find Missing CF Values A and B","difficulty":"hard","bloom":"apply","lt":["LT4"],"prerequisites":["cumfreq_table"],"skills":["running_totals","algebraic_reasoning"],"strategy":["1. A = previous CF + frequency.","2. B similarly."],"common_errors":["Skipping intermediate totals."],"remediation":"cumfreq_table","instruction":"Find the values of A and B in the cumulative frequency table.","flint_prompt":"Each CF value = previous CF + frequency for that class."},
    "boxplot_read":         {"subtopic":"Read a Box Plot","difficulty":"medium","bloom":"apply","lt":["LT5"],"prerequisites":["boxplot_iqr"],"skills":["reading_box_plot","quartile_identification","iqr_calculation"],"strategy":["1. Read min from left whisker.","2. Q1 from left box edge.","3. Median from centre line.","4. Q3 from right box edge.","5. IQR = Q3 − Q1."],"common_errors":["Confusing whisker ends with quartiles."],"remediation":"boxplot_iqr","instruction":"Use the box plot to answer the questions.","flint_prompt":"Read each value directly from the diagram."},
    "boxplot_iqr":          {"subtopic":"IQR from Raw Data","difficulty":"easy","bloom":"apply","lt":["LT5"],"prerequisites":["median_simple"],"skills":["quartile_calculation","subtraction"],"strategy":["1. Sort data.","2. Find Q₁ and Q₃.","3. IQR = Q₃ − Q₁."],"common_errors":["Wrong quartile positions."],"remediation":"median_simple","instruction":"Find the interquartile range.","flint_prompt":"Q₁ is the median of the lower half; Q₃ the median of the upper half."},
    "boxplot_draw":         {"subtopic":"Draw Box Plot from 5-Number Summary","difficulty":"medium","bloom":"apply","lt":["LT5"],"prerequisites":["boxplot_iqr"],"skills":["five_number_summary","box_plot_construction"],"strategy":["1. IQR = Q₃ − Q₁.","2. Draw box from Q₁ to Q₃.","3. Median line inside box.","4. Whiskers to min/max."],"common_errors":["Drawing whiskers to Q₁/Q₃ not min/max."],"remediation":"boxplot_iqr","instruction":"Find the IQR and draw a box plot.","flint_prompt":"Box spans Q₁ to Q₃; whiskers extend to min and max."},
    "boxplot_outlier":      {"subtopic":"Identify Outliers (1.5 × IQR Rule)","difficulty":"hard","bloom":"analyse","lt":["LT5"],"prerequisites":["boxplot_iqr"],"skills":["outlier_rule","quartile_calculation"],"strategy":["1. Find Q₁, Q₃, IQR.","2. Fences: Q₁−1.5×IQR and Q₃+1.5×IQR.","3. Values outside fences = outliers."],"common_errors":["Using 2×IQR instead of 1.5×IQR."],"remediation":"boxplot_iqr","instruction":"Identify outliers using the 1.5 × IQR rule and draw a box plot.","flint_prompt":"Upper fence = Q₃ + 1.5 × IQR. Any value beyond this is an outlier."},
    "boxplot_find_unknowns":{"subtopic":"Find Unknown Values from Box Plot Conditions","difficulty":"medium","bloom":"analyse","lt":["LT5"],"prerequisites":["boxplot_iqr","median_simple","mode_simple","range_simple"],"skills":["simultaneous_conditions","median_rule","mode_rule","range_rule"],"strategy":["1. Use mode to find k.","2. Use range to find h.","3. Use median to find j."],"common_errors":["Applying conditions in wrong order."],"remediation":"boxplot_iqr","instruction":"Find the unknown values using the given conditions.","flint_prompt":"Start with mode (easiest), then range, then median."},
}

DIFFICULTY = {k: v["difficulty"] for k, v in METADATA.items()}
SUBTOPIC   = {k: v["subtopic"]   for k, v in METADATA.items()}


def clean_skills(skills):
    return [s.replace("_", " ").capitalize() for s in skills]


def generate(types, seed=None, count=4, show_solutions=False):
    if seed is not None:
        random.seed(seed)

    exercises = []
    for i, ex_type in enumerate(types, 1):
        if ex_type not in REGISTRY:
            raise ValueError(
                f"Unknown type: '{ex_type}'. "
                f"Available: {sorted(REGISTRY.keys())}"
            )

        m = METADATA.get(ex_type, {})

        # ── Multi-part generators (one dataset, multiple sub-questions) ──
        # stem_leaf_averages: returns (parts_list, svg)
        # freq_table_full, grouped_full, cumfreq_iqr: return list of parts
        MULTIPART_TYPES = {
            "freq_table_full", "grouped_full",
            "cumfreq_iqr",     "cumfreq_full",
            "boxplot_read"
        }
        # stem_leaf_averages: count independent exercises, each with own diagram
        if ex_type == "stem_leaf_averages":
            for _k in range(count):
                parts_list, svg = gen_stem_leaf_averages()
                for j, p in enumerate(parts_list):
                    p["label"] = PART_LABELS[j]
                    if not show_solutions:
                        p.pop("solution_latex", None)
                ex = {
                    "number":      i,
                    "title":       m.get("subtopic", ex_type),
                    "instruction": m.get("instruction", "Use the diagram."),
                    "parts":       parts_list,
                    "ex_svg":      svg,
                    "meta": {
                        "type":          ex_type,
                        "subtopic":      m.get("subtopic",""),
                        "topic":         "Statistics",
                        "unit":          "Unit 4: Statistics",
                        "curriculum":    "MYP5",
                        "difficulty":    m.get("difficulty","medium"),
                        "bloom":         m.get("bloom","apply"),
                        "lt":            m.get("lt",[]),
                        "prerequisites": m.get("prerequisites",[]),
                        "skills":        clean_skills(m.get("skills",[])),
                        "strategy":      m.get("strategy",[]),
                        "common_errors": m.get("common_errors",[]),
                        "remediation":   m.get("remediation",None),
                        "flint_prompt":  m.get("flint_prompt",""),
                    }
                }
                exercises.append(ex)
            continue

        if ex_type in MULTIPART_TYPES:
            all_parts = []
            ex_svg_out = None
            ex_tbl_out = None

            # generate ONE dataset, use its parts only once
            gen_fn = {
                "freq_table_full": gen_freq_table_full,
                "grouped_full":    gen_grouped_full,
                "cumfreq_iqr":     gen_cumfreq_iqr,
                "cumfreq_full":    gen_cumfreq_full,
                "boxplot_read":    gen_boxplot_read,
            }[ex_type]
            result = gen_fn()
            all_parts = result
            for p in all_parts:
                if ex_tbl_out is None and p.get("_tbl"):
                    ex_tbl_out = p.pop("_tbl")
                else:
                    p.pop("_tbl", None)
                if ex_svg_out is None and p.get("ex_svg"):
                    ex_svg_out = p.pop("ex_svg")
                else:
                    p.pop("ex_svg", None)

            # Re-label all parts
            for j, p in enumerate(all_parts):
                p["label"] = PART_LABELS[j % len(PART_LABELS)]
                if not show_solutions:
                    p.pop("solution_latex", None)

            ex = {
                "number":      i,
                "title":       m.get("subtopic", ex_type),
                "instruction": m.get("instruction", "Answer the questions."),
                "parts":       all_parts,
                "meta": {
                    "type":          ex_type,
                    "subtopic":      m.get("subtopic", ""),
                    "topic":         "Statistics",
                    "unit":          "Unit 4: Statistics",
                    "curriculum":    "MYP5",
                    "difficulty":    m.get("difficulty", "medium"),
                    "bloom":         m.get("bloom", "apply"),
                    "lt":            m.get("lt", []),
                    "prerequisites": m.get("prerequisites", []),
                    "skills":        clean_skills(m.get("skills", [])),
                    "strategy":      m.get("strategy", []),
                    "common_errors": m.get("common_errors", []),
                    "remediation":   m.get("remediation", None),
                    "flint_prompt":  m.get("flint_prompt", ""),
                }
            }
            if ex_svg_out:
                ex["ex_svg"] = ex_svg_out
            if ex_tbl_out:
                ex["ex_tbl"] = ex_tbl_out
            exercises.append(ex)
            continue

        # ── Normal case ──────────────────────────────────────────
        gen   = REGISTRY[ex_type]
        parts = [gen() for _ in range(count)]

        # Extract exercise-level SVG if present
        ex_svg = None
        for p in parts:
            if "ex_svg" in p:
                ex_svg = p.pop("ex_svg")
                break
        for p in parts:
            p.pop("ex_svg", None)

        for j, p in enumerate(parts):
            p["label"] = PART_LABELS[j]
            if not show_solutions:
                p.pop("solution_latex", None)

        ex = {
            "number":      i,
            "title":       m.get("subtopic", ex_type),
            "instruction": m.get("instruction", "Answer the question."),
            "parts":       parts,
            "meta": {
                "type":          ex_type,
                "subtopic":      m.get("subtopic", ""),
                "topic":         "Statistics",
                "unit":          "Unit 4: Statistics",
                "curriculum":    "MYP5",
                "difficulty":    m.get("difficulty", "medium"),
                "bloom":         m.get("bloom", "apply"),
                "lt":            m.get("lt", []),
                "prerequisites": m.get("prerequisites", []),
                "skills":        clean_skills(m.get("skills", [])),
                "strategy":      m.get("strategy", []),
                "common_errors": m.get("common_errors", []),
                "remediation":   m.get("remediation", None),
                "flint_prompt":  m.get("flint_prompt", ""),
            }
        }
        if ex_svg:
            ex["ex_svg"] = ex_svg
        exercises.append(ex)

    return {
        "worksheet": {
            "title":          "Unit 4: Statistics",
            "unit":           "Unit 4: Statistics",
            "topic":          "Statistics",
            "date":           str(date.today()),
            "total_parts":    sum(len(e["parts"]) for e in exercises),
            "seed":           seed,
            "show_solutions": show_solutions,
        },
        "exercises": exercises,
    }


def generate_session(types_json, seed=None, count=4):
    types = json.loads(types_json)
    return json.dumps(generate(types=types, seed=seed, count=count))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Statistics exercises")
    parser.add_argument("--types", nargs="+", default=["mean_simple"])
    parser.add_argument("--seed",           type=int,  default=None)
    parser.add_argument("--count",          type=int,  default=4)
    parser.add_argument("--show-solutions", action="store_true")
    parser.add_argument("--pretty",         action="store_true")
    parser.add_argument("--list-types",     action="store_true")
    args = parser.parse_args()
    if args.list_types:
        print("\nAvailable exercise types:\n")
        for k in sorted(REGISTRY.keys()):
            diff  = DIFFICULTY.get(k, "?")
            badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(diff,"⚪")
            print(f"  {badge}  {k:<35} {SUBTOPIC.get(k,'')}")
        print()
    else:
        result = generate(types=args.types, seed=args.seed,
                          count=args.count, show_solutions=args.show_solutions)
        print(json.dumps(result, ensure_ascii=False,
                         indent=2 if args.pretty else None))
