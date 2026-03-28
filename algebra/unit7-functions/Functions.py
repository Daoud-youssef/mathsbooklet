"""
Functions.py  —  Unit 7: Linear & Quadratic Functions (MYP 5)
=============================================================
generate() returns {"_exercises_qmd", "exercises", "worksheet", "meta"}
"""

import random, math, json
from fractions import Fraction
from datetime import date

# ══════════════════════════════════════════════════════════════════
# CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════

PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")
VARIABLES   = ["x", "y", "n", "m", "t", "p"]
NAMES = ["Ahmed","Sara","Omar","Layla","Yusuf","Nour",
         "James","Emma","Liam","Olivia","Noah","Sophia"]

def ri(a, b):  return random.randint(a, b)
def rv():      return random.choice(VARIABLES)
def rname():   return random.choice(NAMES)

def frac(f):
    f = Fraction(f)
    if f.denominator == 1: return str(f.numerator)
    sign = "-" if f < 0 else ""
    return f"{sign}\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"

def frac_plain(f):
    """Plain-text fraction for SVG labels — no LaTeX commands."""
    f = Fraction(f).limit_denominator(10)
    if f.denominator == 1: return str(f.numerator)
    sign = "-" if f < 0 else ""
    return f"{sign}{abs(f.numerator)}/{f.denominator}"

def fmt_linear(m, c, v="x"):
    m, c = Fraction(m), Fraction(c)
    parts = []
    if m == 1:    parts.append(v)
    elif m == -1: parts.append(f"-{v}")
    elif m != 0:  parts.append(f"{frac(m)}{v}")
    if c > 0 and parts:   parts.append(f"+ {frac(c)}")
    elif c < 0 and parts: parts.append(f"- {frac(abs(c))}")
    elif c != 0:           parts.append(frac(c))
    return " ".join(parts) if parts else "0"

def fmt_quad(a, b, c, v="x"):
    a, b, c = Fraction(a), Fraction(b), Fraction(c)
    parts = []
    if a == 1:    parts.append(f"{v}^2")
    elif a == -1: parts.append(f"-{v}^2")
    elif a != 0:  parts.append(f"{frac(a)}{v}^2")
    if b == 1 and parts:    parts.append(f"+ {v}")
    elif b == -1 and parts: parts.append(f"- {v}")
    elif b > 0 and parts:   parts.append(f"+ {frac(b)}{v}")
    elif b < 0 and parts:   parts.append(f"- {frac(abs(b))}{v}")
    elif b != 0:             parts.append(f"{frac(b)}{v}")
    if c > 0 and parts:   parts.append(f"+ {frac(c)}")
    elif c < 0 and parts: parts.append(f"- {frac(abs(c))}")
    elif c != 0:           parts.append(frac(c))
    return " ".join(parts) if parts else "0"

def fmt_vertex(a, h, k, v="x"):
    a, h, k = Fraction(a), Fraction(h), Fraction(k)
    a_s = "" if a == 1 else ("-" if a == -1 else f"{frac(a)}")
    inner = (f"{v} - {frac(h)}" if h > 0 else
             f"{v} + {frac(abs(h))}" if h < 0 else v)
    k_s = (f"+ {frac(k)}" if k > 0 else
           f"- {frac(abs(k))}" if k < 0 else "")
    return f"{a_s}({inner})^2 {k_s}".strip()

def fmt_factored(a, r1, r2, v="x"):
    a, r1, r2 = Fraction(a), Fraction(r1), Fraction(r2)
    a_s = "" if a == 1 else ("-" if a == -1 else f"{frac(a)}")
    def factor(r):
        if r == 0:  return f"({v})"
        if r > 0:   return f"({v} - {frac(r)})"
        return f"({v} + {frac(abs(r))})"
    return f"{a_s}{factor(r1)}{factor(r2)}"

def sign_str(n):
    """Return '+ n' or '- |n|' for use in expressions."""
    n = Fraction(n)
    if n >= 0: return f"+ {frac(n)}"
    return f"- {frac(abs(n))}"

# ══════════════════════════════════════════════════════════════════
# SVG HELPERS
# ══════════════════════════════════════════════════════════════════

def _arrow_diagram_svg(domain, range_vals, arrows):
    n_d, n_r = len(domain), len(range_vals)
    H = max(160, 44 * max(n_d, n_r) + 40)
    W = 260
    d_x, r_x = 65, 195
    dy = H / (n_d + 1)
    ry = H / (n_r + 1)
    d_pts = [(d_x, int((i + 1) * dy)) for i in range(n_d)]
    r_pts = [(r_x, int((i + 1) * ry)) for i in range(n_r)]
    lines = [
        f'<svg viewBox="0 -18 {W} {H+18}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:280px;margin:8px auto;display:block">',
        '<defs><marker id="arr" markerWidth="8" markerHeight="6" '
        'refX="6" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#555"/></marker></defs>',
        f'<ellipse cx="{d_x}" cy="{H//2}" rx="50" ry="{H//2-8}" '
        f'fill="#e8f4fd" stroke="#2c7bb6" stroke-width="1.5"/>',
        f'<ellipse cx="{r_x}" cy="{H//2}" rx="50" ry="{H//2-8}" '
        f'fill="#e8f5e9" stroke="#2e7d32" stroke-width="1.5"/>',
        f'<text x="{d_x}" y="-4" text-anchor="middle" font-size="11" '
        f'font-weight="bold" fill="#2c7bb6">Domain</text>',
        f'<text x="{r_x}" y="-4" text-anchor="middle" font-size="11" '
        f'font-weight="bold" fill="#2e7d32">Range</text>',
    ]
    for val, (cx, cy) in zip(domain, d_pts):
        lines.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" '
                     f'font-size="13" fill="#333">{val}</text>')
    for val, (cx, cy) in zip(range_vals, r_pts):
        lines.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" '
                     f'font-size="13" fill="#333">{val}</text>')
    for di, ri2 in arrows:
        x1, y1 = d_pts[di]; x2, y2 = r_pts[ri2]
        lines.append(f'<line x1="{x1+24}" y1="{y1}" x2="{x2-24}" y2="{y2}" '
                     f'stroke="#555" stroke-width="1.5" marker-end="url(#arr)"/>')
    lines.append('</svg>')
    return "\n".join(lines)


def _linear_svg(m, c, v="x", x_min=-4, x_max=4):
    m, c = Fraction(m), Fraction(c)
    W, H, pad = 260, 220, 34
    # y range based on line values
    ys = [float(m * x + c) for x in [x_min, x_max]]
    y_min_v = min(ys) - 1; y_max_v = max(ys) + 1
    y_min_v = min(y_min_v, -1); y_max_v = max(y_max_v, 1)
    sx = (W - 2 * pad) / (x_max - x_min)
    sy = (H - 2 * pad) / (y_max_v - y_min_v)

    def px(x): return int(pad + (float(x) - x_min) * sx)
    def py(y): return int(H - pad - (float(y) - y_min_v) * sy)

    ox = px(0); oy = py(0)
    x1p, x2p = px(x_min - 0.5), px(x_max + 0.5)
    y1p, y2p = py(float(m * (x_min - 0.5) + c)), py(float(m * (x_max + 0.5) + c))

    # Two labelled integer points
    label_pts = []
    for x in range(x_min, x_max + 1):
        y = m * x + c
        if y.denominator == 1:
            label_pts.append((x, int(y)))
    label_pts = label_pts[::max(1, len(label_pts) // 2)][:2]

    lines = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:{W}px;margin:8px auto;display:block">',
        '<defs><marker id="axh" markerWidth="8" markerHeight="6" '
        'refX="6" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#333"/></marker></defs>',
    ]
    # Grid
    for x in range(x_min, x_max + 1):
        lines.append(f'<line x1="{px(x)}" y1="{pad}" x2="{px(x)}" y2="{H-pad}" '
                     f'stroke="#e0e0e0" stroke-width="1"/>')
    for y in range(int(y_min_v), int(y_max_v) + 1):
        lines.append(f'<line x1="{pad}" y1="{py(y)}" x2="{W-pad}" y2="{py(y)}" '
                     f'stroke="#e0e0e0" stroke-width="1"/>')
    # Axes
    lines += [
        f'<line x1="{pad}" y1="{oy}" x2="{W-pad}" y2="{oy}" stroke="#444" '
        f'stroke-width="1.5" marker-end="url(#axh)"/>',
        f'<line x1="{ox}" y1="{H-pad}" x2="{ox}" y2="{pad}" stroke="#444" '
        f'stroke-width="1.5" marker-end="url(#axh)"/>',
        f'<text x="{W-pad+5}" y="{oy+4}" font-size="12" fill="#333">{v}</text>',
        f'<text x="{ox+5}" y="{pad-4}" font-size="12" fill="#333">y</text>',
    ]
    # Tick labels
    for x in range(x_min, x_max + 1):
        if x != 0:
            lines.append(f'<line x1="{px(x)}" y1="{oy-3}" x2="{px(x)}" y2="{oy+3}" '
                         f'stroke="#444" stroke-width="1"/>')
            lines.append(f'<text x="{px(x)}" y="{oy+15}" text-anchor="middle" '
                         f'font-size="10" fill="#666">{x}</text>')
    # Line
    lines.append(f'<line x1="{x1p}" y1="{y1p}" x2="{x2p}" y2="{y2p}" '
                 f'stroke="#c0392b" stroke-width="2.5"/>')
    # Points
    for lx, ly in label_pts:
        lines += [
            f'<circle cx="{px(lx)}" cy="{py(ly)}" r="4" fill="#c0392b"/>',
            f'<text x="{px(lx)+7}" y="{py(ly)-5}" font-size="10" fill="#c0392b">'
            f'({lx},{ly})</text>',
        ]
    lines.append('</svg>')
    return "\n".join(lines)


def _parabola_svg(a, h, k, show_vertex=True, show_axis=True, show_roots=True, v="x"):
    a_f, h_f, k_f = float(a), float(h), float(k)
    W, H, pad = 280, 240, 36
    x_range = 5
    x_min, x_max = h_f - x_range, h_f + x_range
    # y bounds
    y_at_edges = [a_f * (x_min - h_f)**2 + k_f, a_f * (x_max - h_f)**2 + k_f]
    y_min_v = min(k_f, *y_at_edges) - 1
    y_max_v = max(k_f, *y_at_edges) + 1
    y_min_v = min(y_min_v, -1); y_max_v = max(y_max_v, 1)
    sx = (W - 2 * pad) / (x_max - x_min)
    sy = (H - 2 * pad) / (y_max_v - y_min_v)

    def px(x): return int(pad + (x - x_min) * sx)
    def py(y): return int(H - pad - (y - y_min_v) * sy)

    ox, oy = px(0), py(0)

    # Parabola path
    pts = []
    for i in range(81):
        xv = x_min + i * (x_max - x_min) / 80
        yv = a_f * (xv - h_f)**2 + k_f
        if pad - 5 < py(yv) < H - pad + 5:
            pts.append(f"{px(xv)},{py(yv)}")
    path = "M " + " L ".join(pts) if pts else ""

    lines = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
        f'style="max-width:{W}px;margin:8px auto;display:block">',
        '<defs><marker id="axp" markerWidth="8" markerHeight="6" '
        'refX="6" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#333"/></marker></defs>',
    ]
    # Grid
    for x in range(int(x_min), int(x_max) + 1):
        lines.append(f'<line x1="{px(x)}" y1="{pad}" x2="{px(x)}" y2="{H-pad}" '
                     f'stroke="#eee" stroke-width="1"/>')
    for y in range(int(y_min_v), int(y_max_v) + 1):
        lines.append(f'<line x1="{pad}" y1="{py(y)}" x2="{W-pad}" y2="{py(y)}" '
                     f'stroke="#eee" stroke-width="1"/>')
    # Axes
    lines += [
        f'<line x1="{pad}" y1="{oy}" x2="{W-pad}" y2="{oy}" stroke="#444" '
        f'stroke-width="1.5" marker-end="url(#axp)"/>',
        f'<line x1="{ox}" y1="{H-pad}" x2="{ox}" y2="{pad}" stroke="#444" '
        f'stroke-width="1.5" marker-end="url(#axp)"/>',
        f'<text x="{W-pad+4}" y="{oy+4}" font-size="12" fill="#333">{v}</text>',
        f'<text x="{ox+4}" y="{pad-4}" font-size="12" fill="#333">y</text>',
    ]
    if path:
        lines.append(f'<path d="{path}" fill="none" stroke="#1d4ed8" stroke-width="2.5"/>')
    # Axis of symmetry
    if show_axis:
        lines += [
            f'<line x1="{px(h_f)}" y1="{pad}" x2="{px(h_f)}" y2="{H-pad}" '
            f'stroke="#e67e22" stroke-width="1.5" stroke-dasharray="5,4"/>',
            f'<text x="{px(h_f)+4}" y="{pad+12}" font-size="10" fill="#e67e22">'
            f'x={frac_plain(h)}</text>',
        ]
    # Vertex
    if show_vertex:
        vx_p, vy_p = px(h_f), py(k_f)
        offset = -14 if a_f > 0 else 18
        lines += [
            f'<circle cx="{vx_p}" cy="{vy_p}" r="5" fill="#e67e22" '
            f'stroke="white" stroke-width="1.5"/>',
            f'<text x="{vx_p+7}" y="{vy_p+offset}" font-size="10" fill="#e67e22">'
            f'({frac_plain(h)}, {frac_plain(k)})</text>',
        ]
    # Roots
    if show_roots and a_f != 0:
        disc_val = -k_f / a_f
        if disc_val >= 0:
            sq = math.sqrt(disc_val)
            for r in [h_f - sq, h_f + sq]:
                r_disp = round(r, 1) if abs(r - round(r)) > 0.05 else int(round(r))
                lines += [
                    f'<circle cx="{px(r)}" cy="{oy}" r="4" fill="#2e7d32" '
                    f'stroke="white" stroke-width="1.5"/>',
                    f'<text x="{px(r)}" y="{oy+16}" text-anchor="middle" '
                    f'font-size="10" fill="#2e7d32">{r_disp}</text>',
                ]
    lines.append('</svg>')
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
# EXERCISE BUILDERS
# ══════════════════════════════════════════════════════════════════

def make_equation(equation, answer, solution, v="x",
                  is_wide=False, override_instruction=None):
    return {"item_type": "equation",
            "stimulus": {"text": "", "points": [], "svg": None},
            "equation": equation, "parts": [], "answer": answer,
            "solution": solution, "v": v, "is_wide": is_wide,
            "override_instruction": override_instruction}

def make_multipart(stimulus_text, stimulus_points, stimulus_svg,
                   parts, answer, solution, override_instruction=None, solution_svg=None):
    return {"item_type": "multipart",
            "stimulus": {"text": stimulus_text, "points": stimulus_points,
                         "svg": stimulus_svg},
            "equation": "", "parts": parts, "answer": answer,
            "solution": solution, "solution_svg": solution_svg, "v": "x",
            "override_instruction": override_instruction}

def part(label, text):
    return {"label": label, "text": text}

# ══════════════════════════════════════════════════════════════════
# LT1 — RELATIONS & FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def gen_relation_mapping():
    is_func = random.choice([True, True, False])
    domain = random.sample(range(1, 9), ri(3, 4))
    range_pool = random.sample(range(1, 9), ri(3, 5))
    if is_func:
        arrows = [(i, random.randint(0, len(range_pool) - 1))
                  for i in range(len(domain))]
    else:
        arrows = [(i, i % len(range_pool)) for i in range(len(domain))]
        dup = random.randint(0, len(domain) - 1)
        other = (arrows[dup][1] + 1) % len(range_pool)
        arrows.append((dup, other))
    svg = _arrow_diagram_svg(domain, range_pool, arrows)
    verdict = ("Yes — every input has exactly one output."
               if is_func else
               "No — one input maps to more than one output.")
    sol = ("\\text{Check: does each domain element have exactly one arrow?} \\\\[4pt] "
           f"\\text{{{verdict}}}")
    ans = "Function ✓" if is_func else "Not a function ✗"
    return make_multipart(
        stimulus_text="The arrow diagram shows a relation.",
        stimulus_points=[], stimulus_svg=svg,
        parts=[part("a", "State the domain and range of this relation."),
               part("b", "Is this relation a function? Justify your answer.")],
        answer=ans, solution=sol)


def gen_relation_ordered_pairs():
    is_func = random.choice([True, True, False])
    xs = random.sample(range(-4, 6), ri(4, 5))
    pairs = [(x, ri(-4, 5)) for x in xs]
    if not is_func:
        pairs.append((xs[0], pairs[0][1] + 1))
    random.shuffle(pairs)
    pairs_str = ", ".join(f"({x},\\ {y})" for x, y in pairs)
    domain = sorted(set(x for x, y in pairs))
    rng    = sorted(set(y for x, y in pairs))
    d_str  = ", ".join(str(x) for x in domain)
    r_str  = ", ".join(str(y) for y in rng)
    yes_no = "Yes" if is_func else "No"
    reason = ("no $x$-value repeats" if is_func
              else "one $x$-value maps to two outputs")
    sol = (f"\\text{{Domain: }} \\{{{d_str}\\}} \\\\[4pt] "
           f"\\text{{Range: }} \\{{{r_str}\\}} \\\\[4pt] "
           f"\\text{{Function? {yes_no} — {reason}.}}")
    func_word = "Function" if is_func else "Not a function"
    return make_multipart(
        stimulus_text=f"Consider the relation: $\\{{\\, {pairs_str} \\,\\}}$",
        stimulus_points=[], stimulus_svg=None,
        parts=[part("a", "State the domain and range."),
               part("b", "Is this a function? Explain.")],
        answer=f"Domain: {{{d_str}}}, Range: {{{r_str}}}, {func_word}",
        solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT2 — REPRESENTATIONS
# ══════════════════════════════════════════════════════════════════

def gen_repr_table_to_eq():
    for _ in range(200):
        m = random.choice([-3, -2, -1, 1, 2, 3,
                            Fraction(1, 2), Fraction(-1, 2), Fraction(3, 2)])
        c = ri(-5, 5)
        xs = sorted(random.sample(range(-3, 5), 4))
        ys = [m * x + c for x in xs]
        if not all(Fraction(y).denominator == 1 for y in ys):
            continue
        ys_i = [int(y) for y in ys]
        row_x = " & ".join(str(x) for x in xs)
        row_y = " & ".join(str(y) for y in ys_i)
        eq = f"y = {fmt_linear(m, c)}"
        dy = ys_i[1] - ys_i[0]; dx = xs[1] - xs[0]
        sol = (f"\\text{{Slope: }} m = \\dfrac{{\\Delta y}}{{\\Delta x}} = "
               f"\\dfrac{{{dy}}}{{{dx}}} = {frac(m)} \\\\[4pt] "
               f"\\text{{Substitute }} ({xs[0]}, {ys_i[0]}): "
               f"{ys_i[0]} = {frac(m)}({xs[0]}) + c \\\\[4pt] "
               f"c = {frac(c)} \\\\[4pt] "
               f"{eq}")
        table = (f"\\begin{{array}}{{c|{'c'*4}}} x & {row_x} \\\\ "
                 f"\\hline y & {row_y} \\end{{array}}")
        return make_equation(table, eq, sol, "x", is_wide=True,
            override_instruction="")


def gen_repr_eq_to_table():
    for _ in range(200):
        m = random.choice([-2, -1, 1, 2, 3, Fraction(1, 2)])
        c = ri(-4, 4)
        xs = sorted(random.sample(range(-2, 5), 4))
        ys = [m * x + c for x in xs]
        if not all(Fraction(y).denominator == 1 for y in ys):
            continue
        ys_i = [int(y) for y in ys]
        show_idx = sorted(random.sample(range(4), 2))
        hide_idx = [i for i in range(4) if i not in show_idx]
        row_y = []
        for i, y in enumerate(ys_i):
            row_y.append(str(y) if i in show_idx else "\\square")
        row_x = " & ".join(str(x) for x in xs)
        row_y_s = " & ".join(row_y)
        eq_str = f"y = {fmt_linear(m, c)}"
        table = (f"{eq_str} \\qquad "
                 f"\\begin{{array}}{{c|{'c'*4}}} x & {row_x} \\\\ "
                 f"\\hline y & {row_y_s} \\end{{array}}")
        sol = " \\\\[4pt] ".join(
            f"x = {xs[i]}: \\quad y = {frac(m)}({xs[i]}) {sign_str(c)} = {ys_i[i]}"
            for i in hide_idx)
        ans = ", ".join(str(ys_i[i]) for i in hide_idx)
        return make_equation(table, ans, sol, "x", is_wide=True,
            override_instruction="")

# ══════════════════════════════════════════════════════════════════
# LT3 — DOMAIN & RANGE
# ══════════════════════════════════════════════════════════════════

def gen_domain_range_set():
    pairs = [(ri(-4, 4), ri(-4, 4)) for _ in range(ri(4, 6))]
    seen = set(); uniq = []
    for p in pairs:
        if p[0] not in seen:
            seen.add(p[0]); uniq.append(p)
    pairs = uniq[:5]
    pairs_str = ", ".join(f"({x},\\ {y})" for x, y in pairs)
    domain = sorted(set(x for x, y in pairs))
    rng    = sorted(set(y for x, y in pairs))
    d_str  = ", ".join(str(x) for x in domain)
    r_str  = ", ".join(str(y) for y in rng)
    sol = (f"\\text{{Domain (all }}x\\text{{-values): }} \\{{{d_str}\\}} \\\\[4pt] "
           f"\\text{{Range (all }}y\\text{{-values): }} \\{{{r_str}\\}}")
    return make_equation(
        f"\\{{\\,{pairs_str}\\,\\}}",
        f"D={{{d_str}}}, R={{{r_str}}}",
        sol, "x", is_wide=True)


def gen_domain_range_linear():
    m = random.choice([-3, -2, -1, 1, 2, 3])
    c = ri(-5, 5)
    eq_str = f"f(x) = {fmt_linear(m, c)}"
    sol = ("\\text{Linear functions are defined for all real numbers.} \\\\[4pt] "
           "\\text{Domain: } x \\in \\mathbb{R} \\\\[4pt] "
           "\\text{Range: } y \\in \\mathbb{R}")
    return make_equation(eq_str, "Domain: ℝ, Range: ℝ", sol, "x",
        override_instruction="")

# ══════════════════════════════════════════════════════════════════
# LT4 — LINEAR FUNCTIONS
# ══════════════════════════════════════════════════════════════════

def gen_linear_identify():
    m = random.choice([-3, -2, -1, 1, 2, 3])
    c = ri(-5, 5)
    v = rv()
    linear_eq = fmt_linear(m, c, v)
    a2 = random.choice([2, 3]); b2 = ri(-3, 3); c2 = ri(-4, 4)
    quad_eq  = fmt_quad(a2, b2, c2, v)
    recip_eq = f"\\dfrac{{1}}{{{v}}} + {ri(1, 4)}"
    abs_c = ri(1, 5)
    abs_eq   = f"|{v}| + {abs_c}"
    options  = [linear_eq, quad_eq, recip_eq, abs_eq]
    random.shuffle(options)
    correct  = options.index(linear_eq)
    labels   = ["A", "B", "C", "D"]
    opts_str = " \\qquad ".join(
        f"\\text{{{labels[i]}:}}\\; {o}" for i, o in enumerate(options))
    sol = (f"\\text{{A linear function has degree 1 (form }} f(x) = mx + c\\text{{).}} \\\\[4pt] "
           f"\\text{{Answer: }} {labels[correct]} \\text{{ — }} f(x) = {linear_eq} \\text{{ has degree 1. }}\\checkmark")
    return make_equation(opts_str, labels[correct], sol, v, is_wide=True,
        override_instruction="")


def gen_linear_evaluate():
    m = random.choice([-3, -2, -1, 1, 2, 3])
    c = ri(-6, 6)
    x_vals = random.sample([-3, -2, -1, 0, 1, 2, 3, 4], 3)
    eq_str = f"f(x) = {fmt_linear(m, c)}"
    def step(x):
        val = int(m * x + c)
        m_term = f"{frac(Fraction(m))} \\cdot ({x})"
        c_part = sign_str(c)
        return f"f({x}) = {m_term} {c_part} = {val}"
    sol = " \\\\[4pt] ".join(step(x) for x in x_vals)
    ans = ", ".join(f"f({x})\\!=\\!{int(m*x+c)}" for x in x_vals)
    q_str = f"{eq_str} \\quad \\text{{Find: }} " + \
            ", ".join(f"f({x})" for x in x_vals)
    return make_equation(q_str, ans, sol, "x", is_wide=True,
        override_instruction="")


def gen_linear_interpret():
    contexts = [
        dict(text="A taxi charges a base fare of ${c} plus ${m} per km.",
             x_var="d", y_var="C", x_name="km", y_unit=r"\$",
             slope_meaning="cost per km driven",
             intercept_meaning="base fare (fixed charge)"),
        dict(text="A phone plan costs ${c} per month plus ${m} per GB of data.",
             x_var="g", y_var="T", x_name="GB", y_unit=r"\$",
             slope_meaning="cost per GB used",
             intercept_meaning="monthly base cost"),
    ]
    ctx = random.choice(contexts)
    m = ri(2, 8); c = ri(5, 30)
    x5_val = m * 5 + c
    eq = f"{ctx['y_var']} = {m}{ctx['x_var']} + {c}"
    sol = (f"\\text{{(a) }} {eq} \\\\[4pt] "
           f"\\text{{(b) Slope }} = {m}: \\text{{ {ctx['slope_meaning']}}} \\\\[4pt] "
           f"\\text{{Intercept }} = {c}: \\text{{ {ctx['intercept_meaning']}}} \\\\[4pt] "
           f"\\text{{(c) When }} {ctx['x_var']} = 5: "
           f"{ctx['y_var']} = {m}(5) + {c} = {x5_val} \\text{{ {ctx['y_unit']}}}")
    return make_multipart(
        stimulus_text=ctx['text'].format(m=m, c=c),
        stimulus_points=[], stimulus_svg=None,
        parts=[part("a", f"Write an equation for ${ctx['y_var']}$ in terms of ${ctx['x_var']}$."),
               part("b", "Interpret the slope and intercept in context."),
               part("c", f"Find the value when ${ctx['x_var']} = 5$."), ],
        answer=eq, solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT5 — SLOPE & RATE OF CHANGE
# ══════════════════════════════════════════════════════════════════

def gen_slope_two_points():
    x1 = ri(-4, 3); y1 = ri(-4, 3)
    dx = random.choice([-3, -2, -1, 1, 2, 3, 4])
    dy = random.choice([-4, -3, -2, -1, 1, 2, 3, 4])
    x2, y2 = x1 + dx, y1 + dy
    m = Fraction(dy, dx)
    sol = (f"m = \\dfrac{{y_2 - y_1}}{{x_2 - x_1}} = "
           f"\\dfrac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = "
           f"\\dfrac{{{dy}}}{{{dx}}} = {frac(m)}")
    return make_equation(
        f"({x1},\\ {y1}) \\text{{ and }} ({x2},\\ {y2})",
        frac(m), sol, "x",
        override_instruction="")


def gen_slope_from_table():
    for _ in range(200):
        m = random.choice([-3, -2, -1, 1, 2, 3,
                            Fraction(1, 2), Fraction(-1, 2)])
        c = ri(-4, 4)
        xs = sorted(random.sample(range(-2, 6), 4))
        ys = [m * x + c for x in xs]
        if not all(Fraction(y).denominator == 1 for y in ys):
            continue
        ys_i = [int(y) for y in ys]
        row_x = " & ".join(str(x) for x in xs)
        row_y = " & ".join(str(y) for y in ys_i)
        dy = ys_i[1] - ys_i[0]; dx = xs[1] - xs[0]
        sol = (f"\\text{{Rate of change}} = \\dfrac{{\\Delta y}}{{\\Delta x}} = "
               f"\\dfrac{{{dy}}}{{{dx}}} = {frac(m)} \\\\[4pt] "
               f"\\text{{Constant rate → linear, slope }} m = {frac(m)}")
        table = (f"\\begin{{array}}{{c|{'c'*4}}} x & {row_x} \\\\ "
                 f"\\hline y & {row_y} \\end{{array}}")
        return make_equation(table, frac(m), sol, "x", is_wide=True,
            override_instruction="")


def gen_slope_interpret():
    scenarios = [
        dict(text="A plumber charges a call-out fee of ${c} plus ${m} per hour. The equation is $C = {m}h + {c}$.",
             x_var="h", y_var="C", x_unit="hour",
             slope_meaning="cost per hour of work",
             intercept_meaning="fixed call-out fee"),
        dict(text="A plant grows at a constant rate. Its height (cm) after $w$ weeks is $H = {m}w + {c}$.",
             x_var="w", y_var="H", x_unit="week",
             slope_meaning="growth rate ({m} cm per week)",
             intercept_meaning="initial height of the plant"),
    ]
    s = random.choice(scenarios)
    m = ri(2, 9); c = ri(5, 40)
    slope_m = s['slope_meaning'].format(m=m)
    sol = (f"\\text{{(a) Slope }} = {m} \\text{{ ({s['y_var']} per {s['x_unit']})}} \\\\[4pt] "
           f"\\text{{{slope_m}}} \\\\[4pt] "
           f"\\text{{(b) Intercept }} = {c}: \\text{{ {s['intercept_meaning']}}}")
    return make_multipart(
        stimulus_text=s['text'].format(m=m, c=c),
        stimulus_points=[], stimulus_svg=None,
        parts=[part("a", "Identify the slope and interpret it in context."),
               part("b", "What does the intercept represent?")],
        answer=f"slope={m} ({slope_m})", solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT6 — LINEAR EQUATIONS & GRAPHS
# ══════════════════════════════════════════════════════════════════

def gen_linear_graph_plot():
    for _ in range(200):
        m = random.choice([-2, -1, 1, 2, Fraction(1, 2), Fraction(-1, 2)])
        c = ri(-4, 4)
        if c == 0: c = 2
        x_int = Fraction(-c, m)
        if x_int.denominator > 2: continue
        svg = _linear_svg(m, c)
        y_int = c
        sol = (f"y\\text{{-int: set }}x=0: y = {frac(Fraction(c))} \\\\[4pt] "
               f"x\\text{{-int: set }}y=0: 0 = {fmt_linear(m, c)} "
               f"\\Rightarrow x = {frac(x_int)} \\\\[4pt] "
               f"\\text{{Plot the points: x-int at }}({frac(x_int)},\\, 0)\\text{{ and y-int at }}(0,\\ {c}).")
        return make_multipart(
            stimulus_text=f"Consider the linear function $y = {fmt_linear(m, c)}$.",
            stimulus_points=[], stimulus_svg=svg,
            parts=[part("a", "Find the $x$-intercept and $y$-intercept."),
                   part("b", "Use the graph to verify your intercepts.")],
            answer=f"x-int: {frac(x_int)}, y-int: {c}",
            solution=sol)


def gen_linear_write_from_graph():
    for _ in range(200):
        m = random.choice([-2, -1, 1, 2, Fraction(1, 2), Fraction(3, 2)])
        c = ri(-5, 4)
        x1, x2 = random.sample(range(-3, 4), 2)
        y1 = m * x1 + c; y2 = m * x2 + c
        if y1.denominator != 1 or y2.denominator != 1: continue
        y1, y2 = int(y1), int(y2)
        eq_str = f"y = {fmt_linear(m, c)}"
        dy_s = y2 - y1; dx_s = x2 - x1
        sol = (f"m = \\dfrac{{{y2} - ({y1})}}{{{x2} - ({x1})}} = {frac(m)} \\\\[4pt] "
               f"y - ({y1}) = {frac(m)}(x - ({x1})) \\\\[4pt] "
               f"{eq_str}")
        svg = _linear_svg(m, c)
        return make_multipart(
            stimulus_text=f"A line passes through $({x1},\\ {y1})$ and $({x2},\\ {y2})$.",
            stimulus_points=[], stimulus_svg=svg,
            parts=[part("a", "Calculate the slope of the line."),
                   part("b", "Write the equation in the form $y = mx + c$.")],
            answer=eq_str, solution=sol)


def gen_linear_parallel():
    m = random.choice([-2, -1, 1, 2, 3])
    c = ri(-5, 5)
    x0, y0 = ri(-3, 3), ri(-3, 3)
    c_new = y0 - m * x0
    eq_given = f"y = {fmt_linear(m, c)}"
    eq_new   = f"y = {fmt_linear(m, c_new)}"
    sol = (f"\\text{{Parallel lines have equal slopes: }} m = {m} \\\\[4pt] "
           f"\\text{{Through }}({x0},\\ {y0}): {y0} = {m}({x0}) + c \\\\[4pt] "
           f"c = {c_new} \\\\[4pt] "
           f"{eq_new}")
    return make_equation(
        f"\\text{{Parallel to }} {eq_given}\\text{{, through }} ({x0},\\ {y0})",
        eq_new, sol, "x", is_wide=True,
        override_instruction="")


def gen_linear_perpendicular():
    for _ in range(200):
        m = random.choice([-2, -1, 1, 2, Fraction(1, 2), Fraction(-1, 2)])
        c = ri(-4, 4)
        m_perp = Fraction(-1, m)
        x0, y0 = ri(-2, 2), ri(-2, 3)
        c_new = Fraction(y0) - m_perp * x0
        if c_new.denominator > 4: continue
        eq_given = f"y = {fmt_linear(m, c)}"
        eq_new   = f"y = {fmt_linear(m_perp, c_new)}"
        sol = (f"\\text{{Perpendicular slope: }} m_\\perp = \\dfrac{{-1}}{{{frac(m)}}} = {frac(m_perp)} \\\\[4pt] "
               f"\\text{{Through }}({x0},\\ {y0}): {y0} = {frac(m_perp)}({x0}) + c \\\\[4pt] "
               f"c = {frac(c_new)} \\\\[4pt] "
               f"{eq_new}")
        return make_equation(
            f"\\text{{Perpendicular to }} {eq_given}\\text{{, through }} ({x0},\\ {y0})",
            eq_new, sol, "x", is_wide=True,
            override_instruction="")

# ══════════════════════════════════════════════════════════════════
# LT7 — LINEAR MODELING
# ══════════════════════════════════════════════════════════════════

def gen_linear_model_word():
    templates = [
        dict(text="A taxi charges a base fare of ${c} plus ${m} per km.",
             x_var="d", y_var="C", x_unit="km", y_unit=r"\$",
             q_a="Write an equation for total cost $C$ after driving $d$ km.",
             q_b="Find the cost for a 30 km journey.",
             q_c="How far can you travel with ${budget}?"),
        dict(text="A phone plan charges ${c} per month plus ${m} per GB of data.",
             x_var="g", y_var="T", x_unit="GB", y_unit=r"\$",
             q_a="Write an equation for total monthly bill $T$ after using $g$ GB.",
             q_b="Find the bill for 12 GB usage.",
             q_c="How many GB can be used for ${budget}?"),
    ]
    t = random.choice(templates)
    m = ri(2, 6); c = ri(10, 35)
    budget = c + m * random.choice([20, 25, 30, 40])
    x_budget = (budget - c) // m
    val_b = m * (12 if t['x_var'] == 'g' else 30) + c
    x_b = 12 if t['x_var'] == 'g' else 30
    eq = f"{t['y_var']} = {m}{t['x_var']} + {c}"
    sol = (f"\\text{{(a) }} {eq} \\\\[4pt] "
           f"\\text{{(b) }} {t['y_var']} = {m}({x_b}) + {c} = {val_b} \\text{{ {t['y_unit']}}} \\\\[4pt] "
           f"\\text{{(c) }} {budget} = {m}{t['x_var']} + {c} "
           f"\\Rightarrow {t['x_var']} = {x_budget} \\text{{ {t['x_unit']}}}")
    return make_multipart(
        stimulus_text=t['text'].format(m=m, c=c),
        stimulus_points=[], stimulus_svg=None,
        parts=[part("a", t['q_a']),
               part("b", t['q_b']),
               part("c", t['q_c'].format(budget=budget))],
        answer=f"{eq}; {x_budget} {t['x_unit']}", solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT8 — QUADRATIC FUNCTIONS & FORM CONVERSIONS
# ══════════════════════════════════════════════════════════════════

def gen_quadratic_identify():
    a = random.choice([-2, -1, 1, 2, 3])
    b, c_v = ri(-4, 4), ri(-4, 4)
    v = rv()
    quad_eq  = fmt_quad(a, b, c_v, v)
    lin_eq   = fmt_linear(random.choice([-3,-2,-1,1,2,3]), ri(-4,4), v)
    cubic_a  = random.choice([2, 3])
    cb = ri(-2,2); cc = ri(1,4)
    cb_s = ("+ " if cb >= 0 else "- ") + str(abs(cb)) if cb != 0 else ""
    cubic_eq = f"{cubic_a}{v}^3 {cb_s}{v}^2 + {cc}"
    const_eq = str(ri(1, 9))
    options  = [quad_eq, lin_eq, cubic_eq, const_eq]
    random.shuffle(options)
    correct  = options.index(quad_eq)
    labels   = ["A", "B", "C", "D"]
    opts_str = " \\qquad ".join(
        f"\\text{{{labels[i]}:}}\\; {o}" for i, o in enumerate(options))
    sol = (f"\\text{{A quadratic has highest degree 2.}} \\\\[4pt] "
           f"\\text{{Answer: }} {labels[correct]} \\text{{ — }} f(x) = {quad_eq} \\text{{ has degree 2. }}\\checkmark")
    return make_equation(opts_str, labels[correct], sol, v, is_wide=True,
        override_instruction="")


def gen_quadratic_evaluate():
    a = random.choice([-2, -1, 1, 2])
    b, c_v = ri(-4, 4), ri(-4, 4)
    v = rv()
    xs = random.sample([-2, -1, 0, 1, 2, 3], 3)
    eq_str = f"f({v}) = {fmt_quad(a, b, c_v, v)}"
    def step(x):
        val = a * x * x + b * x + c_v
        b_part = sign_str(b * x) if b != 0 else ""
        c_part = sign_str(c_v)   if c_v != 0 else ""
        return f"f({x}) = {a}({x})^2 {b_part} {c_part} = {val}"
    sol = " \\\\[4pt] ".join(step(x) for x in xs)
    ans = ", ".join(f"f({x})\\!=\\!{a*x*x+b*x+c_v}" for x in xs)
    q_str = (f"{eq_str} \\quad \\text{{Find: }} "
             + ", ".join(f"f({x})" for x in xs))
    return make_equation(q_str, ans, sol, v, is_wide=True,
        override_instruction="")


def gen_quadratic_graph():
    a = random.choice([-1, 1, 1, 2, -2])
    h = ri(-3, 3); k = ri(-4, 4)
    b = -2 * a * h; c_v = a * h * h + k
    svg = _parabola_svg(a, h, k, show_vertex=True, show_axis=True, show_roots=True)
    eq_v = f"f(x) = {fmt_vertex(a, h, k)}"
    eq_s = f"f(x) = {fmt_quad(a, b, c_v)}"
    direction = "upward" if a > 0 else "downward"
    sol = (f"\\text{{(a) Vertex: }} ({h},\\ {k}), \\text{{ axis: }} x = {h} \\\\[4pt] "
           f"\\text{{(b) Opens {direction} since }} a = {a} "
           + ("\\text{{ > 0}}" if a > 0 else "\\text{{ < 0}}") + " \\\\[4pt] "
           f"\\text{{(c) Standard form: }} {eq_s}")
    return make_multipart(
        stimulus_text=f"The parabola is given by ${eq_v}$.",
        stimulus_points=[], stimulus_svg=svg,
        parts=[part("a", "State the vertex and axis of symmetry."),
               part("b", "Does the parabola open upward or downward? Why?"),
               part("c", "Write the equation in standard form $f(x) = ax^2 + bx + c$.")],
        answer=f"Vertex ({h},{k}), axis x={h}, opens {direction}",
        solution=sol)


def gen_vertex_to_standard():
    a = random.choice([-2, -1, 1, 2, 3])
    h = ri(-4, 4); k = ri(-6, 6)
    b = -2 * a * h; c_v = a * h * h + k
    eq_v = fmt_vertex(a, h, k)
    eq_s = fmt_quad(a, b, c_v)
    # Expansion step: a(x-h)^2 = a(x^2 - 2hx + h^2)
    inner = fmt_quad(1, -2 * h, h * h)
    sol = (f"\\text{{Expand the bracket:}} \\\\[4pt] "
           f"= {a}({inner}) {sign_str(k)} \\\\[4pt] "
           f"= {eq_s}")
    return make_equation(f"f(x) = {eq_v}", eq_s, sol, "x", is_wide=True,
        override_instruction="")


def gen_vertex_to_factored():
    for _ in range(400):
        a = random.choice([-1, 1, 1, 2])
        h = ri(-4, 4)
        # Use integer root offsets for clean rational roots
        offset = random.choice([1, 4, 9])
        k = -a * offset         # ensures disc = offset, perfect square
        sq = int(math.sqrt(offset))
        r1, r2 = h - sq, h + sq
        if r1 == r2: continue
        eq_v = fmt_vertex(a, h, k)
        eq_f = fmt_factored(a, r1, r2)
        k_over_a = Fraction(-k, a)
        sol = (f"\\text{{Set }} f(x) = 0: \\\\[4pt] "
               f"(x - ({h}))^2 = {frac(k_over_a)} \\\\[4pt] "
               f"x {sign_str(-h)} = \\pm {sq} \\\\[4pt] "
               f"x = {r1} \\text{{ or }} x = {r2} \\\\[4pt] "
               f"\\therefore f(x) = {eq_f}")
        return make_equation(f"f(x) = {eq_v}", eq_f, sol, "x", is_wide=True,
            override_instruction="")


def gen_standard_to_vertex():
    a = random.choice([1, 1, 2, 3, -1])
    h = ri(-4, 4); k = ri(-6, 6)
    b = -2 * a * h; c_v = a * h * h + k
    eq_s = fmt_quad(a, b, c_v)
    eq_v = fmt_vertex(a, h, k)
    if a == 1:
        half_b = Fraction(b, 2)
        hb_sq = half_b * half_b
        adj = c_v - int(hb_sq)  # = k already
        adj_s = sign_str(adj)
        sol = (f"\\text{{Complete the square:}} \\\\[4pt] "
               f"= (x {sign_str(half_b)})^2 - {frac(hb_sq)} {sign_str(c_v)} \\\\[4pt] "
               f"= (x {sign_str(half_b)})^2 {adj_s} \\\\[4pt] "
               f"= {eq_v}")
    else:
        half_ba = Fraction(b, 2 * a)
        # a*(x+half_ba)^2 = ax^2 + bx + a*half_ba^2
        # so ax^2+bx+c = a*(x+half_ba)^2 + (c - a*half_ba^2) = a*(x+half_ba)^2 + k
        inner_sq_pos = Fraction(b * b, 4 * abs(a))  # always positive
        sign_inner = "+" if a < 0 else "-"  # a<0: a*(half_ba)^2 is negative → add
        sol = (f"\\text{{Factor out }} {a}\\text{{:}} \\\\[4pt] "
               f"= {a}\\left(x^2 {sign_str(Fraction(b, a))}x\\right) {sign_str(c_v)} \\\\[4pt] "
               f"= {a}\\left(x {sign_str(half_ba)}\\right)^2 "
               f"{sign_inner} {frac(inner_sq_pos)} {sign_str(c_v)} \\\\[4pt] "
               f"= {eq_v}")
    return make_equation(f"f(x) = {eq_s}", eq_v, sol, "x", is_wide=True,
        override_instruction="")


def gen_factored_to_standard():
    a = random.choice([-1, 1, 1, 2])
    r1 = ri(-5, 4); r2 = ri(-4, 5)
    if r1 == r2: r2 += 1
    b  = -a * (r1 + r2)
    c_v = a * r1 * r2
    eq_f = fmt_factored(a, r1, r2)
    eq_s = fmt_quad(a, b, c_v)
    inner = fmt_quad(1, -(r1 + r2), r1 * r2)
    sol = (f"\\text{{Expand}} \\\\[4pt] "
           f"= {a}({inner}) \\\\[4pt] "
           f"= {eq_s}")
    return make_equation(f"f(x) = {eq_f}", eq_s, sol, "x", is_wide=True,
        override_instruction="")

# ══════════════════════════════════════════════════════════════════
# LT9 — KEY FEATURES OF GRAPHS
# ══════════════════════════════════════════════════════════════════

def gen_quadratic_vertex_formula():
    a = random.choice([-2, -1, 1, 2, 3])
    h = ri(-4, 4); k = ri(-6, 6)
    b = -2 * a * h; c_v = a * h * h + k
    eq_s = fmt_quad(a, b, c_v)
    # Evaluate y by substituting x=h into the quadratic
    bh = b * h; y_check = a*h*h + b*h + c_v  # = k
    bh_s = sign_str(bh) if bh != 0 else ""
    cv_s = sign_str(c_v) if c_v != 0 else ""
    sol = (f"x_{{\\text{{vertex}}}} = \\dfrac{{-b}}{{2a}} = "
           f"\\dfrac{{-({b})}}{{2({a})}} = {h} \\\\[4pt] "
           f"y = {a}({h})^2 {bh_s} {cv_s} = {k} \\\\[4pt] "
           f"\\text{{Vertex: }}\\ x={frac(Fraction(h))},\\ y={k}")
    return make_equation(f"f(x) = {eq_s}", f"({h}, {k})", sol, "x")


def gen_quadratic_axis_symmetry():
    a = random.choice([-2, -1, 1, 2, 3])
    h = ri(-5, 5); k = ri(-6, 6)
    b = -2 * a * h; c_v = a * h * h + k
    eq_s = fmt_quad(a, b, c_v)
    sol = (f"x = \\dfrac{{-b}}{{2a}} = "
           f"\\dfrac{{-({b})}}{{2({a})}} = {h}")
    return make_equation(f"f(x) = {eq_s}", f"x = {h}", sol, "x")


def gen_quadratic_roots_graph():
    a = random.choice([-1, 1, 1])
    r1, r2 = sorted(random.sample(range(-5, 6), 2))
    h = Fraction(r1 + r2, 2)
    k = int(a * (h - r1) * (h - r2))
    svg = _parabola_svg(a, float(h), k,
                        show_vertex=True, show_axis=True, show_roots=True)
    h_s = frac(h)
    sol = (f"\\text{{Roots: }} x = {r1} \\text{{ and }} x = {r2} \\\\[4pt] "
           f"\\text{{Vertex: }} ({h_s},\\ {k}) \\\\[4pt] "
           f"\\text{{Axis of symmetry: }} x = {h_s}")
    return make_multipart(
        stimulus_text="The graph of a quadratic function is shown.",
        stimulus_points=[], stimulus_svg=svg,
        parts=[part("a", "State the roots of the function."),
               part("b", "State the coordinates of the vertex."),
               part("c", "Write the equation of the axis of symmetry.")],
        answer=f"Roots: x={r1}, x={r2}; Vertex: ({frac(h)},{k}); Axis: x={frac(h)}",
        solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT12 — DOMAIN & RANGE (QUADRATIC)
# ══════════════════════════════════════════════════════════════════

def gen_quadratic_domain_range():
    a = random.choice([-2, -1, 1, 2])
    h = ri(-4, 4); k = ri(-5, 5)
    eq_v = fmt_vertex(a, h, k)
    direction = "upward" if a > 0 else "downward"
    range_str = (f"y \\geq {k}" if a > 0 else f"y \\leq {k}")
    range_plain = (f"y ≥ {k}" if a > 0 else f"y ≤ {k}")
    sol = (f"\\text{{Domain: all real numbers}} \\\\[4pt] "
           f"x \\in \\mathbb{{R}} \\\\[4pt] "
           f"\\text{{Parabola opens {direction}; vertex at }}({h},\\ {k}) \\\\[4pt] "
           f"\\text{{Range: }} {range_str}")
    return make_equation(f"f(x) = {eq_v}", range_plain, sol, "x", is_wide=True)


def gen_quadratic_dr_from_graph():
    a = random.choice([-1, 1, 1, -2, 2])
    h = ri(-3, 3); k = ri(-4, 4)
    svg = _parabola_svg(a, h, k, show_vertex=True,
                        show_axis=False, show_roots=False)
    direction = "upward" if a > 0 else "downward"
    range_str  = (f"y \\geq {k}" if a > 0 else f"y \\leq {k}")
    range_plain = (f"y ≥ {k}" if a > 0 else f"y ≤ {k}")
    sol = (f"\\text{{(a) Domain: }} x \\in \\mathbb{{R}} \\\\[4pt] "
           f"\\text{{(b) Vertex at }}({h},\\ {k})\\text{{; opens {direction}}} \\\\[4pt] "
           f"\\text{{Range: }} {range_str}")
    return make_multipart(
        stimulus_text="The graph of a quadratic function is shown.",
        stimulus_points=[], stimulus_svg=svg,
        parts=[part("a", "State the domain of the function."),
               part("b", "State the range of the function.")],
        answer=f"Domain: ℝ, Range: {range_plain}",
        solution=sol)

# ══════════════════════════════════════════════════════════════════
# LT13 — QUADRATIC MODELING
# ══════════════════════════════════════════════════════════════════

def gen_quadratic_model_projectile():
    v0 = random.choice([10, 15, 20, 25])
    h0 = random.choice([0, 5, 10, 20])
    t_v = Fraction(v0, 10)
    h_max = int(-5 * t_v**2 + v0 * t_v + h0)
    svg = _parabola_svg(-5, float(t_v), h_max,
                        show_vertex=True, show_axis=True, show_roots=True, v="t")
    h0_part = f" + {h0}" if h0 > 0 else ""
    sol = (f"\\text{{(a) }} h(0) = {h0} \\text{{ m — initial height}} \\\\[4pt] "
           f"\\text{{(b) Vertex: }} t = \\dfrac{{-{v0}}}{{2(-5)}} = {frac(t_v)} \\text{{ s}} \\\\[4pt] "
           f"\\text{{Max height }} = {h_max} \\text{{ m}} \\\\[4pt] "
           f"\\text{{(c) Set }} h = 0: -5t^2 + {v0}t{h0_part} = 0")
    return make_multipart(

        stimulus_text=(f"A ball is thrown upward. Its height (m) after $t$ seconds is "
                       f"$h(t) = -5t^2 + {v0}t{h0_part}$."),
        stimulus_points=[], stimulus_svg=svg,
        parts=[part("a", "What is the initial height of the ball?"),
               part("b", "Find the maximum height and when it occurs."),
               part("c", "Set up the equation to find when the ball hits the ground.")],
        answer=f"Initial: {h0} m; Max: {h_max} m at t={frac(t_v)} s",
        solution=sol)


def gen_quadratic_model_revenue():
    k  = random.choice([100, 120, 150, 200])
    m  = random.choice([2, 4, 5])
    p_opt = Fraction(k, 2 * m)
    R_max = int(k * p_opt - m * p_opt**2)
    sol = (f"\\text{{(a) Demand }} = {k} - {m}p \\\\[4pt] "
           f"R = p({k} - {m}p) = {k}p - {m}p^2 \\\\[4pt] "
           f"\\text{{(b) Vertex: }} p = \\dfrac{{{k}}}{{2 \\times {m}}} = {frac(p_opt)} \\\\[4pt] "
           f"R_{{\\text{{max}}}} = {R_max}")
    return make_multipart(
        stimulus_text=(f"A company sells items at price $p$ dollars. "
                       f"Demand is ${k} - {m}p$ units."),
        stimulus_points=[], stimulus_svg=None,
        parts=[part("a", "Write an equation for revenue $R$ in terms of $p$."),
               part("b", "Find the price that maximises revenue and state the maximum revenue.")],
        answer=f"p = {frac(p_opt)}, R_max = {R_max}",
        solution=sol)


# ══════════════════════════════════════════════════════════════════
# LT9 EXTENSION — READ UNLABELLED GRAPH + FIND EQUATION
# ══════════════════════════════════════════════════════════════════

def gen_quadratic_read_graph():
    """Clean SVG parabola with integer roots & vertex.
    No vertex/axis labels on the graph.
    Questions: roots, vertex, axis, equation."""
    for _ in range(300):
        a = random.choice([-1, 1, 1, 2, -2])
        r1 = ri(-4, 2); r2 = ri(r1 + 1, 5)
        h = Fraction(r1 + r2, 2)
        k = int(a * (h - r1) * (h - r2))
        # Ensure integer vertex
        if h.denominator != 1: continue
        h_i = int(h)
        if abs(k) > 8: continue
        eq_f = fmt_factored(a, r1, r2)
        b = -a * (r1 + r2); c_v = a * r1 * r2
        eq_s = fmt_quad(a, b, c_v)
        # SVG — NO vertex label, NO axis label, NO root labels
        svg = _parabola_svg(a, h_i, k, show_vertex=False,
                            show_axis=False, show_roots=False)
        sol = (f"\\text{{(a) Roots: }} x = {r1} \\text{{ and }} x = {r2} \\\\[4pt] "
               f"\\text{{(b) Vertex: }} ({h_i},\\ {k}) \\\\[4pt] "
               f"\\text{{(c) Axis of symmetry: }} x = {h_i} \\\\[4pt] "
               f"\\text{{(d) Equation: }} {eq_f} \\text{{ or }} {eq_s}")
        return make_multipart(
            stimulus_text="The graph of a quadratic function is shown.",
            stimulus_points=[], stimulus_svg=svg,
            parts=[part("a", "State the roots (x-intercepts) of the function."),
                   part("b", "State the coordinates of the vertex."),
                   part("c", "Write the equation of the axis of symmetry."),
                   part("d", "Write the equation of the quadratic function.")],
            answer=f"Roots: {r1},{r2}; Vertex: ({h_i},{k}); Axis: x={h_i}; f(x)={eq_s}",
            solution=sol)


# ══════════════════════════════════════════════════════════════════
# NEW — LINEAR-QUADRATIC INTERSECTION
# ══════════════════════════════════════════════════════════════════

def gen_linear_quadratic_intersection():
    """Find intersection of f(x)=ax²+bx+c and g(x)=mx+d.
    Set equal, solve, state coordinates. Sometimes no real intersection."""
    for _ in range(400):
        # Build so that intersection is clean integers
        a_q = random.choice([-1, 1, 1, 2])
        # Choose two integer x-values where they intersect
        x1 = ri(-3, 2); x2 = ri(x1 + 1, 5)
        # Linear: g(x) = m*x + d — pick m
        m = random.choice([-2, -1, 0, 1, 2, 3])
        d = ri(-5, 5)
        y1 = m * x1 + d; y2 = m * x2 + d
        # Quadratic through (x1,y1) and (x2,y2) with leading coeff a_q
        # a_q*x^2 + b*x + c = y at x1 and x2
        # a_q*x1^2 + b*x1 + c = y1
        # a_q*x2^2 + b*x2 + c = y2
        # Subtract: a_q*(x1^2-x2^2) + b*(x1-x2) = y1-y2
        # a_q*(x1+x2) + b = (y1-y2)/(x1-x2) = m
        b_q = m - a_q * (x1 + x2)
        c_q = y1 - a_q * x1**2 - b_q * x1
        if not isinstance(c_q, int): continue
        # Equation: a_q*x^2 + b_q*x + c_q = m*x + d
        # a_q*x^2 + (b_q-m)*x + (c_q-d) = 0
        A = a_q; B = b_q - m; C = c_q - d
        disc = B*B - 4*A*C
        if disc < 0:
            # No real intersection — use this as a "does it intersect?" question
            continue
        if disc == 0:
            continue  # tangent — skip for clarity
        import math as _m
        sq = int(_m.sqrt(disc))
        if sq*sq != disc: continue
        sol_x1 = (-B + sq) // (2*A); sol_x2 = (-B - sq) // (2*A)
        if 2*A*sol_x1 != -B+sq: continue
        if set([sol_x1, sol_x2]) != set([x1, x2]): continue
        y_at_x1 = m * x1 + d; y_at_x2 = m * x2 + d
        eq_q = f"f(x) = {fmt_quad(a_q, b_q, c_q)}"
        eq_l = f"g(x) = {fmt_linear(m, d)}"
        eq_combined = fmt_quad(A, B, C) + " = 0"
        ans_str, steps, _ = fmt_surd_roots_fn(A, B, C)
        sol = (f"\\textbf{{(a)}} \\quad {fmt_quad(a_q, b_q, c_q)} = {fmt_linear(m, d)} "
               f"\\implies {eq_combined} \\\\[6pt] "
               f"\\textbf{{(b)}} \\quad {fmt_factored(A, x1, x2)} = 0 "
               f"\\implies x = {x1} \\text{{ or }} x = {x2} \\\\[6pt] "
               f"\\textbf{{(c)}} \\quad ({x1},\\ {y_at_x1}) \\text{{ and }} ({x2},\\ {y_at_x2})")
        return make_multipart(
            stimulus_text=f"${eq_q}$ and ${eq_l}$",
            stimulus_points=[], stimulus_svg=None,
            parts=[part("a", "Set $f(x) = g(x)$ and form a quadratic equation."),
                   part("b", "Solve to find the $x$-coordinates of the intersection points."),
                   part("c", "State the coordinates of the intersection points.")],
            answer=f"({x1}, {y_at_x1}) and ({x2}, {y_at_x2})",
            solution=sol)

def fmt_surd_roots_fn(A, B, C, v="x"):
    """Helper: return (ans_str, steps, roots) for ax^2+bx+c=0."""
    from fractions import Fraction
    import math
    disc = B*B - 4*A*C
    if disc < 0:
        return "No real roots", "\\text{Discriminant < 0: no real intersection}", []
    sq = int(math.sqrt(disc))
    if sq*sq == disc:
        x1 = Fraction(-B + sq, 2*A)
        x2 = Fraction(-B - sq, 2*A)
        ans = f"{v} = {frac(x1)} \\text{{ or }} {v} = {frac(x2)}"
        steps = (f"{v} = \\dfrac{{-({B}) \\pm {sq}}}{{2({A})}} \\\\[4pt] "
                 f"{ans}")
        return ans, steps, [x1, x2]
    return f"{v} = \\dfrac{{-({B}) \\pm \\sqrt{{{disc}}}}}{{2({A})}}", "", []


# ══════════════════════════════════════════════════════════════════
# LT1 EXTENSION — VERTICAL LINE TEST
# ══════════════════════════════════════════════════════════════════

def _vlt_one_curve(seed_offset=0):
    """Generate ONE curve for the VLT grid — returns SVG + answer."""
    import math

    W, H, pad = 160, 140, 22
    xmin, xmax, ymin, ymax = -4, 4, -4, 4

    def px(x): return int(pad + (x-xmin)/(xmax-xmin)*(W-2*pad))
    def py(y): return int(H - pad - (y-ymin)/(ymax-ymin)*(H-2*pad))

    # Axes + grid
    ox, oy = px(0), py(0)
    svg = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" ',
        f'style="width:100%;max-width:{W}px;display:block;margin:auto">',
        '<defs><marker id="a{s}" markerWidth="6" markerHeight="4" '.format(s=seed_offset),
        'refX="4" refY="2" orient="auto"><polygon points="0 0,6 2,0 4" fill="#555"/></marker></defs>',
    ]
    # light grid
    for x in range(int(xmin), int(xmax)+1):
        svg.append(f'<line x1="{px(x)}" y1="{pad}" x2="{px(x)}" y2="{H-pad}" stroke="#ddd" stroke-width="0.8"/>')
    for y in range(int(ymin), int(ymax)+1):
        svg.append(f'<line x1="{pad}" y1="{py(y)}" x2="{W-pad}" y2="{py(y)}" stroke="#ddd" stroke-width="0.8"/>')
    # axes
    aid = f"a{seed_offset}"
    svg += [
        f'<line x1="{pad}" y1="{oy}" x2="{W-pad}" y2="{oy}" stroke="#555" stroke-width="1.2" marker-end="url(#{aid})"/>',
        f'<line x1="{ox}" y1="{H-pad}" x2="{ox}" y2="{pad}" stroke="#555" stroke-width="1.2" marker-end="url(#{aid})"/>',
        f'<text x="{W-pad+2}" y="{oy+4}" font-size="8" fill="#555">x</text>',
        f'<text x="{ox+2}" y="{pad-2}" font-size="8" fill="#555">y</text>',
    ]

    curve_type = [
        'parabola_up', 'parabola_down', 'cubic', 'abs_value',
        'circle', 'ellipse', 'sideways_parabola', 'upper_semi',
        'lower_semi', 'sine_wave', 'line',
    ][seed_offset % 11]

    def polyline(pts_xy, color="#1d4ed8"):
        ps = " ".join(f"{px(x)},{py(y)}" for x,y in pts_xy if ymin-0.5<=y<=ymax+0.5)
        if not ps: return ""
        return f'<polyline points="{ps}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round"/>'

    N = 80
    xs = [xmin + i*(xmax-xmin)/N for i in range(N+1)]

    if curve_type == 'parabola_up':
        h, k = random.choice([(-1,0),(0,-2),(1,-1),(0,-1)])
        pts = [(x, (x-h)**2+k) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'parabola_down':
        h, k = random.choice([(0,3),(1,2),(-1,2)])
        pts = [(x, -(x-h)**2+k) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'cubic':
        pts = [(x, x**3/8) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'abs_value':
        h, k = random.choice([(0,-2),(1,-1),(-1,-1)])
        pts = [(x, abs(x-h)+k) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'line':
        m = random.choice([-2,-1,1,2])
        c = random.choice([-1,0,1])
        pts = [(x, m*x+c) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'sine_wave':
        pts = [(x, 2*math.sin(x)) for x in xs]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'upper_semi':
        r = 3
        pts = [(x, math.sqrt(max(0, r**2-x**2))) for x in xs if abs(x)<=r]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'lower_semi':
        r = 3
        pts = [(x, -math.sqrt(max(0, r**2-x**2))) for x in xs if abs(x)<=r]
        svg.append(polyline(pts))
        is_func = True

    elif curve_type == 'circle':
        N2 = 120
        top = [(3*math.cos(2*math.pi*i/N2), 3*math.sin(2*math.pi*i/N2)) for i in range(N2+1)]
        # draw as two halves to avoid jump
        t_pts = [(x,y) for x,y in top if y>=0]
        b_pts = [(x,y) for x,y in top if y<=0]
        svg.append(polyline(t_pts))
        svg.append(polyline(b_pts))
        is_func = False

    elif curve_type == 'ellipse':
        N2 = 120
        top = [(3.5*math.cos(2*math.pi*i/N2), 2*math.sin(2*math.pi*i/N2)) for i in range(N2+1)]
        t_pts = [(x,y) for x,y in top if y>=0]
        b_pts = [(x,y) for x,y in top if y<=0]
        svg.append(polyline(t_pts))
        svg.append(polyline(b_pts))
        is_func = False

    else:  # sideways_parabola: x = y^2/4
        # upper half y>=0
        ys_pos = [i*ymax/60 for i in range(61)]
        t_pts = [(y**2/4, y) for y in ys_pos if xmin<=y**2/4<=xmax]
        # lower half y<=0
        ys_neg = [-i*abs(ymin)/60 for i in range(61)]
        b_pts = [(y**2/4, y) for y in ys_neg if xmin<=y**2/4<=xmax]
        svg.append(polyline(t_pts))
        svg.append(polyline(b_pts))
        is_func = False

    svg.append('</svg>')
    return '\n'.join(svg), is_func


def gen_vertical_line_test():
    """4-curve grid: each cell shows a curve, student writes Yes or No."""
    # Pick 4 distinct curve types — mix functions and non-functions
    all_types = list(range(11))  # 11 types in _vlt_one_curve
    # Ensure at least 1 function and 1 non-function
    # Types 0-7 are functions (0=par_up,1=par_down,2=cubic,3=abs,4=line[idx10 mod11=10],
    # 5=sine[idx9],6=upper_semi[idx7],7=lower_semi[idx8])
    # Non-functions: circle(idx4), ellipse(idx5), sideways(idx6)
    func_offsets    = [0, 1, 2, 3, 7, 8, 9, 10]  # is_func=True
    nonfunc_offsets = [4, 5, 6]                    # is_func=False
    
    chosen = (random.sample(func_offsets, 2) + random.sample(nonfunc_offsets, 2))
    random.shuffle(chosen)

    items = []
    for idx, offset in enumerate(chosen):
        svg, is_func = _vlt_one_curve(offset)
        answer = "Yes" if is_func else "No"
        sol = ("Yes — passes VLT" if is_func else "No — fails VLT")
        items.append({
            "label": list("abcd")[idx],
            "equation": "",   # no equation for this type
            "svg": svg,
            "answer": answer,
            "solution": sol,
            "is_function": is_func,
        })
    return items   # returns list of 4 items for special grid renderer


def _render_stimulus(stim):
    out = []
    if stim["text"]:
        out.append(stim["text"] + "\n")
    if stim["points"]:
        for p in stim["points"]:
            out.append(f"- {p}")
        out.append("")
    if stim["svg"]:
        out.append(stim["svg"] + "\n")
    return "\n".join(out)


SKILLS_MAP = {
    "LT1":  ["Function definition", "Domain & range", "Arrow diagrams"],
    "LT2":  ["Table of values", "Linear equations", "Representations"],
    "LT3":  ["Domain", "Range", "Set notation"],
    "LT4":  ["Linear functions", "Slope", "y-intercept"],
    "LT5":  ["Rate of change", "Slope formula", "Interpretation"],
    "LT6":  ["Graphing", "Intercepts", "Parallel & perpendicular"],
    "LT7":  ["Linear modelling", "Real-world context", "Interpretation"],
    "LT8":  ["Quadratic functions", "Form conversions", "Vertex form"],
    "LT9":  ["Vertex", "Axis of symmetry", "Roots"],
    "LT12": ["Domain & range", "Vertex", "Quadratic functions"],
    "LT13": ["Quadratic modelling", "Projectile motion", "Revenue"],
    "LT6_LT9": ["Intersection", "Linear & quadratic", "Solving systems"],
}

INSTRUCTIONS_MAP = {
    "relation_mapping":          "Analyse the arrow diagram.",
    "relation_ordered_pairs":    "Analyse the relation.",
    "repr_table_to_eq":          "Find the equation of the linear function shown in the table.",
    "repr_eq_to_table":          "Complete the table of values.",
    "domain_range_set":          "State the domain and range of each relation.",
    "domain_range_linear":       "State the domain and range of each function.",
    "linear_identify":           "Identify which expression represents a linear function.",
    "linear_evaluate":           "Evaluate the function at each given value.",
    "linear_interpret":          "Read and interpret the linear function.",
    "slope_two_points":          "Find the slope of the line through each pair of points.",
    "slope_from_table":          "Find the rate of change from the table.",
    "slope_interpret":           "Interpret the slope in context.",
    "linear_graph_plot":         "Find intercepts and analyse the graph.",
    "linear_write_from_graph":   "Write the equation of the line.",
    "linear_parallel":           "Find the equation of each line described.",
    "linear_perpendicular":      "Find the equation of each line described.",
    "linear_model_word":         "Form and solve a linear model.",
    "quadratic_identify":        "Identify which expression represents a quadratic function.",
    "quadratic_evaluate":        "Evaluate each quadratic function at the given values.",
    "quadratic_graph":           "Analyse the parabola.",
    "vertex_to_standard":        "Convert from vertex form to standard form.",
    "vertex_to_factored":        "Convert from vertex form to factored form.",
    "standard_to_vertex":        "Convert to vertex form by completing the square.",
    "factored_to_standard":      "Expand to standard form.",
    "quadratic_vertex_formula":  "Find the vertex of each quadratic function.",
    "quadratic_axis_symmetry":   "State the equation of the axis of symmetry.",
    "quadratic_roots_graph":     "Read key features from the graph.",
    "quadratic_domain_range":    "State the domain and range of each quadratic function.",
    "quadratic_dr_from_graph":   "State the domain and range from the graph.",
    "quadratic_model_projectile": "Analyse the projectile model.",
    "quadratic_model_revenue":   "Analyse the revenue model.",
    "quadratic_read_graph":      "Read the graph and find the equation.",
    "linear_quadratic_intersection": "Find the intersection of the two functions.",
    "vertical_line_test":        "State whether each graph represents a function. Write Yes or No.",
}

REGISTRY = {
    # LT1
    "relation_mapping":          (gen_relation_mapping,          1, "list", "easy",   "LT1"),
    "relation_ordered_pairs":    (gen_relation_ordered_pairs,    1, "list", "easy",   "LT1"),
    # LT2
    "repr_table_to_eq":          (gen_repr_table_to_eq,          4, "grid", "easy",   "LT2"),
    "repr_eq_to_table":          (gen_repr_eq_to_table,          4, "grid", "easy",   "LT2"),
    # LT3
    "domain_range_set":          (gen_domain_range_set,          4, "grid", "easy",   "LT3"),
    "domain_range_linear":       (gen_domain_range_linear,       4, "grid", "easy",   "LT3"),
    # LT4
    "linear_identify":           (gen_linear_identify,           4, "grid", "easy",   "LT4"),
    "linear_evaluate":           (gen_linear_evaluate,           4, "grid", "easy",   "LT4"),
    "linear_interpret":          (gen_linear_interpret,          1, "list", "medium", "LT4"),
    # LT5
    "slope_two_points":          (gen_slope_two_points,          6, "grid", "easy",   "LT5"),
    "slope_from_table":          (gen_slope_from_table,          4, "grid", "easy",   "LT5"),
    "slope_interpret":           (gen_slope_interpret,           1, "list", "medium", "LT5"),
    # LT6
    "linear_graph_plot":         (gen_linear_graph_plot,         1, "list", "medium", "LT6"),
    "linear_write_from_graph":   (gen_linear_write_from_graph,   1, "list", "medium", "LT6"),
    "linear_parallel":           (gen_linear_parallel,           4, "grid", "hard",   "LT6"),
    "linear_perpendicular":      (gen_linear_perpendicular,      4, "grid", "hard",   "LT6"),
    # LT7
    "linear_model_word":         (gen_linear_model_word,         1, "list", "hard",   "LT7"),
    # LT8
    "quadratic_identify":        (gen_quadratic_identify,        4, "grid", "easy",   "LT8"),
    "quadratic_evaluate":        (gen_quadratic_evaluate,        4, "grid", "easy",   "LT8"),
    "quadratic_graph":           (gen_quadratic_graph,           1, "list", "medium", "LT8"),
    "vertex_to_standard":        (gen_vertex_to_standard,        4, "grid", "medium", "LT8"),
    "vertex_to_factored":        (gen_vertex_to_factored,        4, "grid", "hard",   "LT8"),
    "standard_to_vertex":        (gen_standard_to_vertex,        4, "grid", "hard",   "LT8"),
    "factored_to_standard":      (gen_factored_to_standard,      4, "grid", "medium", "LT8"),
    # LT9
    "quadratic_vertex_formula":  (gen_quadratic_vertex_formula,  6, "grid", "medium", "LT9"),
    "quadratic_axis_symmetry":   (gen_quadratic_axis_symmetry,   6, "grid", "easy",   "LT9"),
    "quadratic_roots_graph":     (gen_quadratic_roots_graph,     1, "list", "medium", "LT9"),
    # LT12
    "quadratic_domain_range":    (gen_quadratic_domain_range,    4, "grid", "medium", "LT12"),
    "quadratic_dr_from_graph":   (gen_quadratic_dr_from_graph,   1, "list", "medium", "LT12"),
    # LT13
    "quadratic_model_projectile":(gen_quadratic_model_projectile,1, "list", "hard",   "LT13"),
    "quadratic_model_revenue":   (gen_quadratic_model_revenue,   1, "list", "hard",   "LT13"),
    # LT9 ext
    "quadratic_read_graph":      (gen_quadratic_read_graph,      1, "list", "medium", "LT9"),
    # LT6/LT9
    "linear_quadratic_intersection": (gen_linear_quadratic_intersection, 1, "list", "hard", "LT9"),
    # LT1 — VLT
    "vertical_line_test":        (gen_vertical_line_test,        1, "vlt",  "easy",   "LT1"),
}


def render_grid_block(ex_num, items, instruction, lt, skills, show_solutions):
    n = len(items)
    wide = any(it.get("is_wide") for it in items)
    col = 12 if (wide or n == 1) else {2: 6, 3: 4, 4: 3, 6: 4}.get(n, 4)

    lines = [f"::::: {{#exr-u7-{ex_num}}}\n",
             f"*{instruction}*\n",
             ":::: {.grid}\n"]
    for it in items:
        lines += [f"::: {{.g-col-{col}}}\n",
                  f"**{it['label']})** $\\displaystyle {it['equation']}$\n",
                  ":::\n"]
    lines.append("::::\n")

    if show_solutions:
        lines += ['::: {.callout-tip collapse="true"}',
                  "## 🔍 View Solutions\n"]
        for it in items:
            lines += [f"**{it['label']})**\n",
                      "$$\n\\begin{aligned}", it["solution"], "\\end{aligned}\n$$"]
        lines.append(":::")

    lines += ["", "::: exercise-meta",
              '<div class="skill-container">',
              *[f'  <span class="skill-badge">{s}</span>' for s in skills],
              "</div>", ":::", "", ":::::\n"]
    return "\n".join(lines)


def render_list_block(ex_num, item, instruction, lt, skills, show_solutions):
    inst = item.get("override_instruction") or instruction
    lines = [f"::::: {{#exr-u7-{ex_num}}}\n"]
    if inst:
        lines.append(f"*{inst}*\n")
    lines.append(_render_stimulus(item["stimulus"]))
    for p in item["parts"]:
        lines.append(f"**({p['label']})** {p['text']}\n")

    if show_solutions:
        sol_lines = ['::: {.callout-tip collapse="true"}',
                     "## 🔍 View Solution\n"]
        if item.get("solution_svg"):
            sol_lines.append(item["solution_svg"] + "\n")
        sol_lines += ["$$\n\\begin{aligned}", item["solution"], "\\end{aligned}\n$$",
                      ":::"]
        lines += sol_lines

    lines += ["", "::: exercise-meta",
              '<div class="skill-container">',
              *[f'  <span class="skill-badge">{s}</span>' for s in skills],
              "</div>", ":::", "", ":::::\n"]
    return "\n".join(lines)


def render_vlt_block(ex_num, items, instruction, lt, skills, show_solutions):
    """Render 4-curve VLT as a 2x2 grid."""
    lines = [f"::::: {{#exr-u7-{ex_num}}}\n",
             f"*{instruction}*\n",
             ":::: {.grid}\n"]
    for it in items:
        lines += [
            "::: {.g-col-6}\n",
            f"**{it['label']})**\n",
            it['svg'] + "\n",
            ":::\n",
        ]
    lines.append(":::::\n")

    if show_solutions:
        lines += ['::: {.callout-tip collapse="true"}',
                  "## 🔍 View Solutions\n"]
        for it in items:
            mark = "✅" if it["is_function"] else "❌"
            ans = ("**Yes** — passes the Vertical Line Test"
                   if it["is_function"]
                   else "**No** — fails the Vertical Line Test")
            lines.append(f"{mark} **({it['label']})** {ans}  ")
        lines.append("\n:::")

    lines += ["", "::: exercise-meta",
              '<div class="skill-container">',
              *[f'  <span class="skill-badge">{s}</span>' for s in skills],
              "</div>", ":::", "", ":::::\n"]
    return "\n".join(lines)


def generate(types, seed=None, count=None, show_solutions=False):
    if seed is not None:
        random.seed(seed)

    exercises_qmd = []
    exercises_ws  = []
    ex_num = 1

    for ex_type in types:
        if ex_type not in REGISTRY:
            raise ValueError(f"Unknown type: '{ex_type}'. "
                             f"Available: {sorted(REGISTRY.keys())}")

        gen_fn, default_count, layout, difficulty, lt = REGISTRY[ex_type]
        n = count if count is not None else default_count
        instruction = INSTRUCTIONS_MAP.get(ex_type, "")
        skills = SKILLS_MAP.get(lt, [ex_type])

        if layout == "grid":
            items = []
            for j in range(n):
                for _ in range(40):
                    item = gen_fn()
                    if item is not None:
                        item["label"] = PART_LABELS[j]
                        items.append(item)
                        break
            if not items:
                continue
            instr = items[0].get("override_instruction") or instruction
            rendered = render_grid_block(ex_num, items, instr, lt, skills, show_solutions)
            exercises_qmd.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "difficulty": difficulty, "rendered": rendered,
                "answer": "; ".join(it["answer"] for it in items),
            })
            exercises_ws.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "title": INSTRUCTIONS_MAP.get(ex_type, ex_type),
                "difficulty": difficulty, "instruction": "",
                "parts": [{"label": it["label"],
                            "question_latex": it["equation"],
                            "answer_latex": it["answer"]} for it in items],
                "meta": {"difficulty": difficulty, "lt": lt, "skills": skills},
            })

        elif layout == "vlt":
            items = gen_fn()
            if not items:
                continue
            rendered = render_vlt_block(ex_num, items, instruction, lt, skills, show_solutions)
            exercises_qmd.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "difficulty": difficulty, "rendered": rendered,
                "answer": "; ".join(f"({it['label']}) {it['answer']}" for it in items),
            })
            exercises_ws.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "title": INSTRUCTIONS_MAP.get(ex_type, ex_type),
                "difficulty": difficulty, "instruction": "",
                "parts": [{"label": it["label"],
                            "question_latex": "",
                            "answer_latex": it["answer"]} for it in items],
                "meta": {"difficulty": difficulty, "lt": lt, "skills": skills},
            })

        else:  # list
            item = None
            for _ in range(40):
                item = gen_fn()
                if item is not None:
                    break
            if item is None:
                continue
            instr = item.get("override_instruction") or instruction
            rendered = render_list_block(ex_num, item, instr, lt, skills, show_solutions)
            exercises_qmd.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "difficulty": difficulty, "rendered": rendered,
                "answer": item["answer"],
            })
            exercises_ws.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "title": INSTRUCTIONS_MAP.get(ex_type, ex_type),
                "difficulty": difficulty, "instruction": instr,
                "parts": [{"label": p["label"], "question_latex": p["text"],
                            "answer_latex": ""} for p in item["parts"]],
                "meta": {"difficulty": difficulty, "lt": lt, "skills": skills},
            })
        ex_num += 1

    return {
        "_exercises_qmd": exercises_qmd,
        "exercises": exercises_ws,
        "worksheet": {
            "title": "Linear & Quadratic Functions",
            "unit": "Unit 7: Functions",
            "date": str(date.today()),
            "seed": seed,
            "show_solutions": show_solutions,
        },
        "meta": {"total": len(exercises_qmd)},
    }


def generate_session(types_json, seed=None, count=6):
    types = json.loads(types_json)
    return json.dumps(generate(types=types, seed=seed, count=count))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--types", nargs="+", default=["slope_two_points"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--solutions", action="store_true")
    parser.add_argument("--list-types", action="store_true")
    args = parser.parse_args()
    if args.list_types:
        for k, (_, cnt, layout, diff, lt) in sorted(REGISTRY.items()):
            badge = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(diff, "⚪")
            print(f"  {badge}  {lt:<5}  {k:<35}  {layout}")
    else:
        data = generate(types=args.types, seed=args.seed,
                        show_solutions=args.solutions)
        for ex in data["_exercises_qmd"]:
            print(ex["rendered"])
