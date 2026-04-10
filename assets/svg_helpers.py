"""
svg_helpers.py
==============
Geometry-accurate SVG figure generator.
Location : assets/svg_helpers.py
Import   : from svg_helpers import SVG

Side labels are rendered as plain SVG <text> using Unicode substitution
for LaTeX notation. No MathJax dependency inside SVG.

All fixes applied:
  FIX 1 — arc drawn whenever angle_values[i] is non-empty
  FIX 2 — plain SVG <text> for labels (no foreignObject/MathJax)
  FIX 3 — orientation param BL|BR|TL|TR for right_triangle
  FIX 4 — 3:4 ratio when leg label is a string variable
  FIX 5 — side/angle labels clamped to canvas bounds
  FIX 6 — arc sweep=1 draws arc on INTERIOR of angle
"""

import math
import random
import string
import re as _re

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

VERTEX_LETTERS = list(string.ascii_uppercase)
DEFAULT_SIDES  = [3, 4, 5, 6, 7, 8]
CAPTION_TEXT   = "Not drawn to scale"
SIDE_COLOR     = "#c0392b"
VERTEX_COLOR   = "#1a1a2e"
ANGLE_COLOR    = "#555"
HEIGHT_COLOR   = "#888"
ARC_COLOR      = "#666"


# ══════════════════════════════════════════════════════════════════
# LABEL HELPERS
# ══════════════════════════════════════════════════════════════════

def _latex_to_svg_text(s):
    """
    Convert a LaTeX label to a plain Unicode string for SVG <text>.
    Handles every pattern produced by Trigonometry.py and Indices.py:

      \\theta          -> theta (Unicode θ)
      \\sqrt{n}        -> sqrt(n) using Unicode sqrt symbol
      \\text{unit}     -> unit  (strip command, keep content)
      \\dfrac{a}{b}    -> a/b
      {{...}}          -> {...} (unescape Python f-string double braces)
      plain text       -> unchanged
    """
    if not isinstance(s, str):
        return str(s)
    t = s.strip()
    # Normalise double-backslash escapes from Python repr
    t = t.replace('\\\\', '\\')
    # Unescape double braces from Python f-strings
    t = t.replace('{{', '{').replace('}}', '}')
    # Greek letters
    t = t.replace('\\theta', '\u03b8')
    t = t.replace('\\alpha', '\u03b1')
    t = t.replace('\\beta',  '\u03b2')
    t = t.replace('\\phi',   '\u03c6')
    t = t.replace('\\gamma', '\u03b3')
    # \\sqrt{n} -> unicode sqrt + n
    t = _re.sub(r'\\sqrt\{([^}]+)\}', lambda m: '\u221a' + m.group(1), t)
    # \\text{...} -> content (strip surrounding spaces)
    t = _re.sub(r'\\text\s*\{([^}]*)\}', lambda m: m.group(1).strip(), t)
    # \\dfrac{a}{b} or \\frac{a}{b} -> a/b
    t = _re.sub(r'\\d?frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', t)
    # Remove any remaining LaTeX commands
    t = _re.sub(r'\\[a-zA-Z]+', '', t)
    # Remove remaining braces
    t = t.replace('{', '').replace('}', '')
    return t.strip()



def _assign_labels(pts, sides_with_lengths):
    """
    Assign labels to edges by matching pixel edge lengths to real side lengths.
    Completely index-independent — works for any vertex ordering.

    sides_with_lengths: list of (numeric_length, label_string), one per edge.
      - numeric_length is used only for ranking (not displayed)
      - If a side's real length is unknown (string label), estimate from pixel geometry

    Algorithm: sort edges by pixel length, sort sides by real length,
    match rank-to-rank. Equal real lengths get equal labels.
    """
    import math as _m
    n = len(pts)
    assert len(sides_with_lengths) == n, "Need one (length, label) per edge"

    # Pixel length of each edge
    px = [_m.hypot(pts[(i+1)%n][0]-pts[i][0], pts[(i+1)%n][1]-pts[i][1])
          for i in range(n)]

    # Sort edges by pixel length (ascending)
    px_order = sorted(range(n), key=lambda i: px[i])
    # Sort sides by real length (ascending)
    side_order = sorted(range(n), key=lambda i: sides_with_lengths[i][0])

    labels = [''] * n
    for rank in range(n):
        labels[px_order[rank]] = sides_with_lengths[side_order[rank]][1]
    return labels


def fmt_label(v):
    if isinstance(v, str):  return v
    if isinstance(v, float):
        return str(int(v)) if v == int(v) else f"{v:.2g}"
    return str(v)


def simplify_surd(n):
    n = int(n)
    best = 1
    for k in range(2, int(math.isqrt(n)) + 1):
        if n % (k * k) == 0:
            best = k * k
    return int(math.isqrt(best)), n // best


def _rand_side():
    return random.choice(DEFAULT_SIDES)


def _rand_verts(n):
    """Pick n distinct random uppercase letters for vertex labels."""
    return random.sample(VERTEX_LETTERS, n)


def _parse_side(v):
    """Return (numeric_value_or_None, display_label)."""
    if v is None:
        s = _rand_side()
        return float(s), str(s)
    if isinstance(v, (int, float)):
        return float(v), fmt_label(v)
    try:
        return float(v), fmt_label(float(v))
    except (ValueError, TypeError):
        return None, str(v)


# ══════════════════════════════════════════════════════════════════
# GEOMETRY CORE
# ══════════════════════════════════════════════════════════════════

def _fit_polygon(raw_pts, W, H, pad=40):
    xs = [p[0] for p in raw_pts]; ys = [p[1] for p in raw_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x or 1
    span_y = max_y - min_y or 1
    scale = min((W - 2*pad) / span_x, (H - 2*pad) / span_y)
    cx = (min_x + max_x) / 2; cy = (min_y + max_y) / 2
    return [((x - cx)*scale + W/2, (y - cy)*scale + H/2) for x, y in raw_pts]


def _right_triangle_pts(a_num, b_num):
    """
    FIX 4: fixed 3:4 ratio when either leg label is a string variable,
    so triangle shape is seed-independent.
    Returns (raw_pts, a_used, b_used).
    """
    a, b = a_num, b_num
    if a is None and b is None: a, b = 3.0, 4.0
    elif a is None: a = b * 0.75
    elif b is None: b = a * (4.0 / 3.0)
    return [(0.0, 0.0), (b, 0.0), (0.0, -a)], a, b


def _apply_orientation(raw_pts, orientation, a, b):
    """
    FIX 3: reorient triangle so the right angle sits at the requested corner.
    orientation: "BL" (default) | "BR" | "TL" | "TR"
    Returns (oriented_pts, right_angle_vertex_index).
    """
    ori = (orientation or "BL").upper()
    if ori == "BR":
        return [(b - p[0], p[1]) for p in raw_pts], 1
    elif ori == "TL":
        return [(p[0], -p[1]) for p in raw_pts], 0
    elif ori == "TR":
        return [(b - p[0], -p[1]) for p in raw_pts], 1
    return raw_pts, 0  # "BL" default


def _triangle_from_sides(a, b, c):
    if a + b <= c or a + c <= b or b + c <= a: return None
    cos_A = (b**2 + c**2 - a**2) / (2*b*c)
    cos_A = max(-1, min(1, cos_A))
    A_rad = math.acos(cos_A)
    return [(0,0), (c,0), (b*math.cos(A_rad), -b*math.sin(A_rad))]


def _isosceles_pts(equal, base):
    h = math.sqrt(max(0, equal**2 - (base/2)**2))
    return [(-base/2, 0), (base/2, 0), (0, -h)]


def _equilateral_pts(side):
    h = side * math.sqrt(3) / 2
    return [(-side/2, 0), (side/2, 0), (0, -h)]


def _rectangle_pts(w, h): return [(0,0),(w,0),(w,-h),(0,-h)]
def _square_pts(s):       return _rectangle_pts(s, s)


def _parallelogram_pts(w, h, skew=70):
    a = math.radians(skew); dx = h / math.tan(a)
    return [(0,0),(w,0),(w+dx,-h),(dx,-h)]


def _trapezium_pts(top, bottom, h=None):
    if h is None: h = (top + bottom) / 3
    off = (bottom - top) / 2
    return [(-bottom/2,0),(bottom/2,0),(bottom/2-off,-h),(-bottom/2+off,-h)]


def _rhombus_pts(side, angle_deg=60):
    a = math.radians(angle_deg)
    return [(0,0),(side,0),
            (side+side*math.cos(a),-side*math.sin(a)),
            (side*math.cos(a),-side*math.sin(a))]


def _regular_polygon_pts(n, side):
    r = side / (2*math.sin(math.pi/n))
    return [(r*math.cos(math.pi/2 + 2*math.pi*i/n),
             -r*math.sin(math.pi/2 + 2*math.pi*i/n)) for i in range(n)]


def _semicircle_pts(diameter):
    r = diameter / 2
    return [(-r,0),(r,0),(0,-r)]


# ══════════════════════════════════════════════════════════════════
# FIGURE SPEC
# ══════════════════════════════════════════════════════════════════

class FigureSpec:
    def __init__(self):
        self.shape_type    = ""
        self.vertices_px   = []
        self.n_vertices    = 0
        self.vertex_labels = []
        self.side_labels   = []
        self.side_ticks    = []
        self.angle_values  = []
        self.angle_arcs    = []
        self.right_angle_at = -1
        self.height_label  = ""
        self.height_from   = -1
        self.title         = ""
        self.caption       = CAPTION_TEXT
        self.width         = 260
        self.height        = 190
        self.is_semicircle = False
        self.semicircle_r  = 0


# ══════════════════════════════════════════════════════════════════
# BUILDERS
# ══════════════════════════════════════════════════════════════════

def _build_right_triangle(kw):
    spec = FigureSpec()
    spec.shape_type = "right_triangle"
    spec.n_vertices = 3
    spec.width  = kw.get("width",  260)
    spec.height = kw.get("height", 190)

    sides = kw.get("sides", {})
    a_num, a_lbl = _parse_side(sides.get("a"))
    b_num, b_lbl = _parse_side(sides.get("b"))
    c_lbl        = fmt_label(sides.get("c", "x"))

    raw, a_px, b_px = _right_triangle_pts(a_num, b_num)   # FIX 4
    ori = (kw.get("orientation", "BL") or "BL").upper()
    raw, ra_idx = _apply_orientation(raw, ori, a_px, b_px)  # FIX 3
    spec.vertices_px    = _fit_polygon(raw, spec.width, spec.height)
    spec.right_angle_at = ra_idx

    spec.vertex_labels = (kw.get("vertices") or _rand_verts(3)) \
                         if kw.get("show_vertices", True) else ["", "", ""]

    # Assign labels by edge length — index-independent
    c_num = math.sqrt(a_px**2 + b_px**2)
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (b_px, b_lbl),   # adjacent
        (c_num, c_lbl),  # hypotenuse
        (a_px, a_lbl),   # opposite
    ])
    spec.side_ticks = [0, 0, 0]

    if kw.get("show_angles", True):
        ang_B = math.degrees(math.atan2(a_px, b_px))
        ang_C = 90 - ang_B
        spec.angle_values = ["90\u00b0", f"{ang_B:.0f}\u00b0", f"{ang_C:.0f}\u00b0"]
        spec.angle_arcs   = [1, 1, 1]
    else:
        spec.angle_values = ["", "", ""]
        spec.angle_arcs   = [0, 0, 0]

    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_isosceles(kw):
    spec = FigureSpec()
    spec.shape_type = "isosceles"
    spec.n_vertices = 3
    spec.width  = kw.get("width",  240)
    spec.height = kw.get("height", 210)

    sides = kw.get("sides", {})
    eq_num, eq_lbl = _parse_side(sides.get("equal"))
    ba_num, ba_lbl = _parse_side(sides.get("base"))
    eq_num = eq_num or float(_rand_side())
    ba_num = ba_num or float(_rand_side())
    while eq_num <= ba_num / 2: eq_num = float(_rand_side())

    spec.vertices_px   = _fit_polygon(_isosceles_pts(eq_num, ba_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(3)) \
                         if kw.get("show_vertices", True) else ["", "", ""]
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (ba_num, ba_lbl),  # base (shortest)
        (eq_num, eq_lbl),  # equal side
        (eq_num, eq_lbl),  # equal side
    ])
    # Ticks follow the same length-ranking as labels:
    # base (shortest edge) → no tick, equal sides → one tick each
    spec.side_ticks = _assign_labels(spec.vertices_px, [
        (ba_num, 0),   # base — no tick
        (eq_num, 1),   # equal side — one tick
        (eq_num, 1),   # equal side — one tick
    ])

    if kw.get("show_angles", True):
        h = math.sqrt(eq_num**2 - (ba_num/2)**2)
        ab = math.degrees(math.atan2(h, ba_num/2))
        ap = 180 - 2*ab
        spec.angle_values = [f"{ap:.0f}\u00b0", f"{ab:.0f}\u00b0", f"{ab:.0f}\u00b0"]
        spec.angle_arcs   = [1, 1, 1]
    else:
        spec.angle_values = kw.get("angle_values", ["", "", ""])
        spec.angle_arcs   = [0, 0, 0]

    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_equilateral(kw):
    spec = FigureSpec()
    spec.shape_type = "equilateral"
    spec.n_vertices = 3
    spec.width  = kw.get("width",  240)
    spec.height = kw.get("height", 220)

    sides = kw.get("sides", {})
    s_num, s_lbl = _parse_side(sides.get("a") or sides.get("equal"))
    s_num = s_num or float(_rand_side())

    spec.vertices_px   = _fit_polygon(_equilateral_pts(s_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(3)) \
                         if kw.get("show_vertices", True) else ["", "", ""]
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (s_num, s_lbl), (s_num, s_lbl), (s_num, s_lbl),
    ])
    spec.side_ticks  = [1, 1, 1]

    if kw.get("show_angles", True):
        spec.angle_values = ["60\u00b0", "60\u00b0", "60\u00b0"]
        spec.angle_arcs   = [1, 1, 1]
    else:
        spec.angle_values = ["", "", ""]
        spec.angle_arcs   = [0, 0, 0]

    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_scalene(kw, subtype="scalene"):
    spec = FigureSpec()
    spec.shape_type = subtype
    spec.n_vertices = 3
    spec.width  = kw.get("width",  260)
    spec.height = kw.get("height", 200)

    sides = kw.get("sides", {})
    a_num, a_lbl = _parse_side(sides.get("a"))
    b_num, b_lbl = _parse_side(sides.get("b"))
    c_num, c_lbl = _parse_side(sides.get("c"))

    for _ in range(50):
        av = a_num or float(_rand_side())
        bv = b_num or float(random.choice([s for s in DEFAULT_SIDES if s != av]))
        cv = c_num or float(random.choice([s for s in DEFAULT_SIDES if s != av and s != bv]))
        raw = _triangle_from_sides(av, bv, cv)
        if raw: break
    else:
        av, bv, cv = 3.0, 4.0, 5.0
        raw = _triangle_from_sides(av, bv, cv)

    spec.vertices_px   = _fit_polygon(raw, spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(3)) \
                         if kw.get("show_vertices", True) else ["", "", ""]
    spec.side_labels = [a_lbl or fmt_label(av), b_lbl or fmt_label(bv), c_lbl or fmt_label(cv)]
    spec.side_ticks  = [0, 0, 0]

    if kw.get("show_angles", True):
        def ao(opp, s1, s2):
            c = (s1**2+s2**2-opp**2)/(2*s1*s2)
            return math.degrees(math.acos(max(-1,min(1,c))))
        aA = ao(av,bv,cv); aB = ao(bv,av,cv); aC = 180-aA-aB
        spec.angle_values = [f"{aA:.0f}\u00b0", f"{aB:.0f}\u00b0", f"{aC:.0f}\u00b0"]
        spec.angle_arcs   = [1, 1, 1]
    else:
        spec.angle_values = kw.get("angle_values", ["", "", ""])
        spec.angle_arcs   = [0, 0, 0]

    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_acute(kw):
    for _ in range(100):
        sk = kw.get("sides", {})
        a = float(_parse_side(sk.get("a"))[0] or _rand_side())
        b = float(_parse_side(sk.get("b"))[0] or _rand_side())
        c = float(_parse_side(sk.get("c"))[0] or _rand_side())
        mx = max(a,b,c)
        if mx**2 < (a**2+b**2+c**2-mx**2) and _triangle_from_sides(a,b,c):
            kw = dict(kw, sides={"a":a,"b":b,"c":c}); break
    return _build_scalene(kw, "acute")


def _build_obtuse(kw):
    for _ in range(100):
        a = float(_rand_side()); b = float(_rand_side())
        c = float(random.uniform(max(a,b)*1.1, a+b-0.5))
        if c > 0 and _triangle_from_sides(a,b,c):
            kw = dict(kw, sides={"a":a,"b":b,"c":round(c,1)}); break
    return _build_scalene(kw, "obtuse")


def _build_rectangle(kw):
    spec = FigureSpec()
    spec.shape_type = "rectangle"; spec.n_vertices = 4
    spec.width = kw.get("width", 280); spec.height = kw.get("height", 200)
    sides = kw.get("sides", {})
    w_num, w_lbl = _parse_side(sides.get("w") or sides.get("width"))
    h_num, h_lbl = _parse_side(sides.get("h") or sides.get("height"))
    w_num = w_num or float(_rand_side()); h_num = h_num or float(_rand_side())
    spec.vertices_px   = _fit_polygon(_rectangle_pts(w_num, h_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(4)) \
                         if kw.get("show_vertices", True) else ["","","",""]
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (w_num, w_lbl), (h_num, h_lbl), (w_num, w_lbl), (h_num, h_lbl),
    ])
    spec.side_ticks  = [1, 2, 1, 2]
    spec.right_angle_at = 0
    spec.angle_values = ["","","",""]
    spec.angle_arcs   = [0,0,0,0]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_square(kw):
    spec = FigureSpec()
    spec.shape_type = "square"; spec.n_vertices = 4
    spec.width = kw.get("width", 220); spec.height = kw.get("height", 220)
    sides = kw.get("sides", {})
    s_num, s_lbl = _parse_side(sides.get("a") or sides.get("s"))
    s_num = s_num or float(_rand_side())
    spec.vertices_px   = _fit_polygon(_square_pts(s_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(4)) \
                         if kw.get("show_vertices", True) else ["","","",""]
    # Only label one side (tick marks show equality for others)
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (s_num, s_lbl), (s_num, ''), (s_num, ''), (s_num, ''),
    ])
    spec.side_ticks  = [1,1,1,1]
    spec.right_angle_at = 0
    spec.angle_values = ["","","",""]
    spec.angle_arcs   = [0,0,0,0]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_parallelogram(kw):
    spec = FigureSpec()
    spec.shape_type = "parallelogram"; spec.n_vertices = 4
    spec.width = kw.get("width", 280); spec.height = kw.get("height", 190)
    sides = kw.get("sides", {})
    w_num, w_lbl = _parse_side(sides.get("w") or sides.get("base"))
    h_num, h_lbl = _parse_side(sides.get("h") or sides.get("side"))
    w_num = w_num or float(_rand_side()); h_num = h_num or float(_rand_side())
    angle = kw.get("angle", random.randint(55, 80))
    spec.vertices_px   = _fit_polygon(_parallelogram_pts(w_num, h_num, angle), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(4)) \
                         if kw.get("show_vertices", True) else ["","","",""]
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (w_num, w_lbl), (h_num, h_lbl), (w_num, w_lbl), (h_num, h_lbl),
    ])
    spec.side_ticks  = [1, 2, 1, 2]
    if kw.get("show_angles", True):
        spec.angle_values = [f"{angle}\u00b0",f"{180-angle}\u00b0",f"{angle}\u00b0",f"{180-angle}\u00b0"]
        spec.angle_arcs   = [1,1,1,1]
    else:
        spec.angle_values = ["","","",""]; spec.angle_arcs = [0,0,0,0]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_trapezium(kw):
    spec = FigureSpec()
    spec.shape_type = "trapezium"; spec.n_vertices = 4
    spec.width = kw.get("width", 280); spec.height = kw.get("height", 190)
    sides = kw.get("sides", {})
    t_num, t_lbl = _parse_side(sides.get("top") or sides.get("a"))
    b_num, b_lbl = _parse_side(sides.get("bottom") or sides.get("b"))
    t_num = t_num or float(_rand_side())
    b_num = b_num or float(t_num * random.uniform(1.4, 2.0))
    h_num = kw.get("height_value") or (t_num + b_num) / 3
    spec.vertices_px   = _fit_polygon(_trapezium_pts(t_num, b_num, h_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(4)) \
                         if kw.get("show_vertices", True) else ["","","",""]
    leg_lbl = fmt_label(sides.get("leg", ""))
    # Estimate leg length from geometry for ranking
    _leg_est = math.sqrt(((b_num-t_num)/2)**2 + h_num**2)
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (b_num,    b_lbl),    # bottom (longer parallel)
        (_leg_est, leg_lbl),  # right leg
        (t_num,    t_lbl),    # top (shorter parallel)
        (_leg_est, leg_lbl),  # left leg
    ])
    spec.side_ticks  = [0,0,0,0]
    spec.height_label = kw.get("height_label", "")
    spec.height_from  = 3
    spec.angle_values = ["","","",""]
    spec.angle_arcs   = [0,0,0,0]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_rhombus(kw):
    spec = FigureSpec()
    spec.shape_type = "rhombus"; spec.n_vertices = 4
    spec.width = kw.get("width", 260); spec.height = kw.get("height", 200)
    sides = kw.get("sides", {})
    s_num, s_lbl = _parse_side(sides.get("a"))
    s_num = s_num or float(_rand_side())
    angle = kw.get("angle", random.randint(50, 80))
    spec.vertices_px   = _fit_polygon(_rhombus_pts(s_num, angle), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(4)) \
                         if kw.get("show_vertices", True) else ["","","",""]
    # Only label one side (tick marks show equality for others)
    spec.side_labels = _assign_labels(spec.vertices_px, [
        (s_num, s_lbl), (s_num, ''), (s_num, ''), (s_num, ''),
    ])
    spec.side_ticks  = [1,1,1,1]
    if kw.get("show_angles", True):
        spec.angle_values = [f"{angle}\u00b0",f"{180-angle}\u00b0",f"{angle}\u00b0",f"{180-angle}\u00b0"]
        spec.angle_arcs   = [1,1,1,1]
    else:
        spec.angle_values = ["","","",""]; spec.angle_arcs = [0,0,0,0]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_semicircle(kw):
    spec = FigureSpec()
    spec.shape_type = "semicircle"; spec.n_vertices = 3
    spec.width = kw.get("width", 240); spec.height = kw.get("height", 180)
    spec.is_semicircle = True
    sides = kw.get("sides", {})
    d_num, d_lbl = _parse_side(sides.get("diameter") or sides.get("d"))
    d_num = d_num or float(_rand_side() * 2)
    spec.semicircle_r = d_num / 2
    spec.vertices_px   = _fit_polygon(_semicircle_pts(d_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(3)) \
                         if kw.get("show_vertices", True) else ["","",""]
    spec.side_labels = [d_lbl,"",""]
    spec.side_ticks  = [0,0,0]
    spec.right_angle_at = 2
    spec.angle_values = ["","","90\u00b0"] if kw.get("show_angles", True) else ["","",""]
    spec.angle_arcs   = [0,0,1]
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


def _build_polygon(kw):
    n = kw.get("n", 5)
    spec = FigureSpec()
    spec.shape_type = f"polygon_{n}"; spec.n_vertices = n
    spec.width = kw.get("width", 260); spec.height = kw.get("height", 260)
    sides = kw.get("sides", {})
    s_num, s_lbl = _parse_side(sides.get("a"))
    s_num = s_num or float(_rand_side())
    spec.vertices_px   = _fit_polygon(_regular_polygon_pts(n, s_num), spec.width, spec.height)
    spec.vertex_labels = (kw.get("vertices") or _rand_verts(n)) \
                         if kw.get("show_vertices", True) else [""]*n
    spec.side_labels = [s_lbl] + [""]*(n-1)
    spec.side_ticks  = [1]*n
    interior = round((n-2)*180/n, 1)
    if kw.get("show_angles", True):
        spec.angle_values = [f"{interior}\u00b0"] + [""]*( n-1)
        spec.angle_arcs   = [1]*n
    else:
        spec.angle_values = [""]*n; spec.angle_arcs = [0]*n
    spec.caption = CAPTION_TEXT if kw.get("caption", True) else ""
    return spec


_BUILDERS = {
    "right_triangle": _build_right_triangle,
    "right":          _build_right_triangle,
    "isosceles":      _build_isosceles,
    "equilateral":    _build_equilateral,
    "scalene":        _build_scalene,
    "acute":          _build_acute,
    "obtuse":         _build_obtuse,
    "rectangle":      _build_rectangle,
    "square":         _build_square,
    "parallelogram":  _build_parallelogram,
    "trapezium":      _build_trapezium,
    "trapezoid":      _build_trapezium,
    "rhombus":        _build_rhombus,
    "semicircle":     _build_semicircle,
    "semi":           _build_semicircle,
    "polygon":        _build_polygon,
}


# ══════════════════════════════════════════════════════════════════
# SVG CANVAS
# ══════════════════════════════════════════════════════════════════

class SVGCanvas:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self._els = []

    def add(self, s): self._els.append(s)

    def line(self, x1, y1, x2, y2, color="#333", w=1.8, dash=""):
        da = f'stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                 f'stroke="{color}" stroke-width="{w}" {da}/>')

    def text(self, x, y, s, size=12, anchor="middle",
             color="#222", bold=False, italic=True):
        """Plain SVG text for vertex labels, angle values, captions."""
        fw = "bold" if bold else "normal"
        fs = "italic" if italic else "normal"
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
                 f'dominant-baseline="central" font-size="{size}" '
                 f'font-family="serif" font-weight="{fw}" font-style="{fs}" '
                 f'fill="{color}">{s}</text>')

    def math_text(self, x, y, label, size=13, color=SIDE_COLOR):
        """
        FIX 2: render side label as plain SVG <text> using Unicode substitution.
        No foreignObject, no MathJax dependency — works in every browser context.
        Single-letter variables are italicised; everything else is upright.
        """
        display = _latex_to_svg_text(label)
        if not display:
            return
        single_var = (len(display) == 1 and display.isalpha()
                      and display not in ('\u03b8','\u03b1','\u03b2','\u03c6'))
        fs = "italic" if single_var else "normal"
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
                 f'dominant-baseline="central" font-size="{size}" '
                 f'font-family="serif" font-style="{fs}" fill="{color}">'
                 + display + '</text>')

    def polygon(self, pts, fill="none", stroke="#333", w=2):
        ps = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.add(f'<polygon points="{ps}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')

    def arc_path(self, cx, cy, r, a1_deg, a2_deg, color=ARC_COLOR, w=1.5):
        """
        FIX 6: sweep=1 (clockwise in SVG screen coords) draws the arc on the
        INTERIOR of the angle. Previously sweep=0 drew the exterior arc.
        large_flag is computed from the clockwise span so it is always 0
        for interior angles of any triangle.
        """
        a1 = math.radians(a1_deg); a2 = math.radians(a2_deg)
        x1 = cx + r*math.cos(a1); y1 = cy - r*math.sin(a1)
        x2 = cx + r*math.cos(a2); y2 = cy - r*math.sin(a2)
        # clockwise span in screen coords (sweep=1 direction)
        cw_span = (360 - (a2_deg - a1_deg) % 360) % 360
        large = 1 if cw_span > 180 else 0
        self.add(f'<path d="M {x1:.1f},{y1:.1f} A {r},{r} 0 {large},1 '
                 f'{x2:.1f},{y2:.1f}" fill="none" '
                 f'stroke="{color}" stroke-width="{w}"/>')

    def right_angle_box(self, corner, d1, d2, size=10):
        cx, cy = corner
        n1 = math.hypot(*d1) or 1; n2 = math.hypot(*d2) or 1
        u1 = (d1[0]/n1*size, d1[1]/n1*size)
        u2 = (d2[0]/n2*size, d2[1]/n2*size)
        p1 = (cx+u1[0], cy+u1[1])
        p2 = (cx+u1[0]+u2[0], cy+u1[1]+u2[1])
        p3 = (cx+u2[0], cy+u2[1])
        self.add(f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} '
                 f'{p3[0]:.1f},{p3[1]:.1f}" fill="none" stroke="#333" stroke-width="1.5"/>')

    def tick_mark(self, mid, direction, n=1, size=6):
        mx, my = mid; dx, dy = direction
        nm = math.hypot(dx, dy) or 1
        px_ = -dy/nm; py_ = dx/nm
        for i in range(n):
            off = (i - (n-1)/2) * 5
            ox = mx + off*px_; oy = my + off*py_
            self.add(f'<line x1="{ox-px_*size:.1f}" y1="{oy-py_*size:.1f}" '
                     f'x2="{ox+px_*size:.1f}" y2="{oy+py_*size:.1f}" '
                     f'stroke="#333" stroke-width="1.8"/>')

    def to_svg(self, max_width="280px"):
        body = "\n".join(self._els)
        return (f'<svg viewBox="0 0 {self.W} {self.H}" xmlns="http://www.w3.org/2000/svg" '
                f'style="max-width:{max_width};width:100%;display:block;margin:8px auto">'
                f'{body}</svg>')


# ══════════════════════════════════════════════════════════════════
# ANNOTATION LAYER
# ══════════════════════════════════════════════════════════════════

class AnnotationLayer:

    @staticmethod
    def _centroid(pts):
        return sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)

    @staticmethod
    def _outward(pt, cx, cy, dist):
        dx, dy = pt[0]-cx, pt[1]-cy
        n = math.hypot(dx, dy) or 1
        return pt[0]+dx/n*dist, pt[1]+dy/n*dist

    @staticmethod
    def _clamp(v, lo, hi):
        return max(lo, min(hi, v))

    @staticmethod
    def _bisector_unit(prev_pt, corner, next_pt):
        d1 = (prev_pt[0]-corner[0], prev_pt[1]-corner[1])
        d2 = (next_pt[0]-corner[0], next_pt[1]-corner[1])
        n1 = math.hypot(*d1) or 1; n2 = math.hypot(*d2) or 1
        bx = d1[0]/n1+d2[0]/n2; by = d1[1]/n1+d2[1]/n2
        nb = math.hypot(bx, by) or 1
        return bx/nb, by/nb

    @staticmethod
    def draw(canvas, spec):
        pts = spec.vertices_px
        n   = len(pts)
        if n == 0: return
        cx, cy = AnnotationLayer._centroid(pts)
        W, H   = canvas.W, canvas.H

        # ── Outline ───────────────────────────────────────────────
        if not spec.is_semicircle:
            canvas.polygon(pts)
        else:
            p0, p1 = pts[0], pts[1]
            canvas.line(p0[0], p0[1], p1[0], p1[1])
            r = math.hypot(p1[0]-p0[0], p1[1]-p0[1]) / 2
            canvas.add(f'<path d="M {p0[0]:.1f},{p0[1]:.1f} '
                       f'A {r:.1f},{r:.1f} 0 0,1 {p1[0]:.1f},{p1[1]:.1f}" '
                       f'fill="none" stroke="#333" stroke-width="2"/>')

        # ── Vertex labels ─────────────────────────────────────────
        for i, pt in enumerate(pts):
            lbl = spec.vertex_labels[i] if i < len(spec.vertex_labels) else ""
            if not lbl: continue
            ox, oy = AnnotationLayer._outward(pt, cx, cy, 17)
            canvas.text(ox, oy, lbl, size=13, color=VERTEX_COLOR, bold=True, italic=False)

        # ── Side labels ───────────────────────────────────────────
        for i in range(n):
            if spec.is_semicircle and i > 0: break
            p1_ = pts[i]; p2_ = pts[(i+1) % n]
            mid = ((p1_[0]+p2_[0])/2, (p1_[1]+p2_[1])/2)
            ox, oy = AnnotationLayer._outward(mid, cx, cy, 26)
            # FIX 5: clamp to canvas
            ox = AnnotationLayer._clamp(ox, 12, W-12)
            oy = AnnotationLayer._clamp(oy, 14, H-10)

            lbl = spec.side_labels[i] if i < len(spec.side_labels) else ""
            if lbl:
                canvas.math_text(ox, oy, lbl, size=13, color=SIDE_COLOR)

            ticks = spec.side_ticks[i] if i < len(spec.side_ticks) else 0
            if ticks:
                canvas.tick_mark(mid, (p2_[0]-p1_[0], p2_[1]-p1_[1]), n=ticks)

        # ── Right-angle box ───────────────────────────────────────
        ra = spec.right_angle_at
        if 0 <= ra < n:
            corner = pts[ra]
            canvas.right_angle_box(
                corner,
                (pts[(ra-1)%n][0]-corner[0], pts[(ra-1)%n][1]-corner[1]),
                (pts[(ra+1)%n][0]-corner[0], pts[(ra+1)%n][1]-corner[1]))

        # ── Angle arcs & labels ───────────────────────────────────
        # FIX 1: draw arc whenever angle_values[i] is non-empty,
        # even if angle_arcs[i] == 0 (i.e. show_angles=False but caller
        # passed angle_values override like theta).
        for i in range(n):
            arcs = spec.angle_arcs[i]  if i < len(spec.angle_arcs)  else 0
            aval = spec.angle_values[i] if i < len(spec.angle_values) else ""
            if not arcs and not aval: continue

            prev_pt = pts[(i-1)%n]; corner = pts[i]; next_pt = pts[(i+1)%n]
            bx, by  = AnnotationLayer._bisector_unit(prev_pt, corner, next_pt)

            # FIX 1: always draw at least one arc when label is present
            arc_count = arcs if arcs else (1 if aval else 0)
            for k in range(arc_count):
                r  = 16 + k*7
                d1 = (prev_pt[0]-corner[0], prev_pt[1]-corner[1])
                d2 = (next_pt[0]-corner[0], next_pt[1]-corner[1])
                n1 = math.hypot(*d1) or 1; n2 = math.hypot(*d2) or 1
                a1 = math.degrees(math.atan2(-(d1[1]/n1), d1[0]/n1))
                a2 = math.degrees(math.atan2(-(d2[1]/n2), d2[0]/n2))
                canvas.arc_path(corner[0], corner[1], r, a1, a2)

            if aval:
                dist = 32 + arc_count*7
                lx = AnnotationLayer._clamp(corner[0]+bx*dist, 8, W-8)
                ly = AnnotationLayer._clamp(corner[1]+by*dist, 12, H-8)
                canvas.text(lx, ly, _latex_to_svg_text(aval), size=11, color=ANGLE_COLOR, italic=False)

        # ── Height/altitude ───────────────────────────────────────
        if spec.height_from >= 0 and spec.height_label:
            apex = pts[spec.height_from]
            opp  = (spec.height_from+2) % n
            bp1  = pts[opp]; bp2 = pts[(opp+1)%n]
            bx_  = bp2[0]-bp1[0]; by_ = bp2[1]-bp1[1]
            bn   = bx_**2 + by_**2 or 1
            t    = ((apex[0]-bp1[0])*bx_+(apex[1]-bp1[1])*by_)/bn
            foot = (bp1[0]+t*bx_, bp1[1]+t*by_)
            canvas.line(apex[0], apex[1], foot[0], foot[1], HEIGHT_COLOR, 1.5, "5,3")
            mhx = (apex[0]+foot[0])/2; mhy = (apex[1]+foot[1])/2
            canvas.text(mhx+12, mhy, spec.height_label, size=11, color=HEIGHT_COLOR, italic=True)

        # ── Caption ───────────────────────────────────────────────
        if spec.caption:
            canvas.text(W/2, H-5, spec.caption, size=9, color="#aaa", italic=False, bold=False)

        # ── Title ─────────────────────────────────────────────────
        if spec.title:
            canvas.text(W/2, 13, spec.title, size=11, color="#333", italic=False, bold=True)


# ══════════════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════════════

class SVG:
    """
    Single entry point: SVG.figure(shape_type, **kwargs)

    Key kwargs:
      sides         : dict   e.g. {"a": "x", "b": 5, "c": r"\\sqrt{31}"}
      vertices      : list   override vertex letters
      show_vertices : bool   (default True)
      show_angles   : bool   (default True)
      show_ticks    : bool   (default True)
      caption       : bool   show "Not drawn to scale" (default True)
      angle_values  : list   per-vertex angle label overrides
                             arc auto-drawn for any non-empty entry (FIX 1)
      orientation   : str    right_triangle only: "BL"|"BR"|"TL"|"TR" (FIX 3)
      width, height : int    canvas pixels
    """

    @staticmethod
    def figure(shape_type, **kw):
        key = shape_type.lower().replace(" ", "_")
        builder = _BUILDERS.get(key)
        if builder is None:
            raise ValueError(f"Unknown shape: '{shape_type}'. Available: {sorted(_BUILDERS.keys())}")

        spec = builder(kw)

        if "title"        in kw: spec.title       = kw["title"]
        if isinstance(kw.get("caption"), str): spec.caption = kw["caption"]
        if "height_label" in kw: spec.height_label = kw["height_label"]
        # angle_values override — applied after builder so callers can
        # inject theta labels even when show_angles=False
        if "angle_values" in kw:
            spec.angle_values = list(kw["angle_values"])

        if not kw.get("show_ticks", True):
            spec.side_ticks = [0] * max(spec.n_vertices, 4)

        # Pad lists
        nv = spec.n_vertices
        for attr in ("vertex_labels","side_labels","side_ticks","angle_values","angle_arcs"):
            lst = getattr(spec, attr)
            if len(lst) < nv:
                setattr(spec, attr, lst + [""]*(nv-len(lst)))

        canvas = SVGCanvas(spec.width, spec.height)
        AnnotationLayer.draw(canvas, spec)
        return canvas.to_svg(f"{spec.width}px")

    # ── Backwards-compatible shortcuts ───────────────────────────

    @staticmethod
    def right_triangle(a, b, hyp_label="x", label_a=None, label_b=None, **kw):
        return SVG.figure("right_triangle",
                          sides={"a": label_a or a, "b": label_b or b, "c": hyp_label}, **kw)

    @staticmethod
    def trapezium(a, b, h, label_a=None, label_b=None, label_h=None, **kw):
        return SVG.figure("trapezium",
                          sides={"top": label_a or a, "bottom": label_b or b},
                          height_label=label_h or str(h), **kw)

    @staticmethod
    def rectangle(w_val, h_val, label_w=None, label_h=None, **kw):
        return SVG.figure("rectangle",
                          sides={"w": label_w or w_val, "h": label_h or h_val}, **kw)

    # ── Graphs ────────────────────────────────────────────────────

    @staticmethod
    def linear(m, c_val, x_range=(-4,4), y_range=None,
               points=None, color="#c0392b", width=280, height=240):
        from fractions import Fraction
        m_f = Fraction(m).limit_denominator(10)
        c_f = Fraction(c_val).limit_denominator(10)
        ys  = [float(m_f*x+c_f) for x in x_range]
        y_lo = min(ys)-1; y_hi = max(ys)+1
        if y_range: y_lo, y_hi = y_range
        else: y_lo = min(y_lo,-1); y_hi = max(y_hi,1)
        cv = _AxesCanvas(width, height, x_range[0], x_range[1], y_lo, y_hi)
        cv.draw_axes()
        cv.polyline([(x, float(m_f*x+c_f)) for x in [x_range[0]-0.5, x_range[1]+0.5]], color)
        if points:
            for px_u, py_u in points:
                cv.dot(px_u, py_u, color)
                cv.label_text(px_u+0.2, py_u+0.2, f"({px_u},{py_u})", color)
        return cv.to_svg(f"{width}px")

    @staticmethod
    def parabola(a, h, k, x_range=None, show_vertex=True,
                 show_roots=True, show_axis=True,
                 color="#1d4ed8", width=280, height=240):
        xmn = h-5; xmx = h+5
        if x_range: xmn, xmx = x_range
        ys  = [a*(x-h)**2+k for x in [xmn, xmx]]
        ylo = min(k,*ys)-1; yhi = max(k,*ys)+1
        ylo = min(ylo,-1);  yhi = max(yhi,1)
        cv  = _AxesCanvas(width, height, xmn, xmx, ylo, yhi)
        cv.draw_axes()
        pts = []
        for i in range(81):
            xv = xmn+i*(xmx-xmn)/80; yv = a*(xv-h)**2+k
            if ylo-0.5 <= yv <= yhi+0.5: pts.append((xv, yv))
        cv.polyline(pts, color)
        if show_axis: cv.vline(h, "#e67e22")
        if show_vertex:
            cv.dot(h, k, "#e67e22")
            cv.label_text(h+0.2, k+(0.4 if a>0 else -0.5),
                          f"({fmt_label(round(h,2))},{fmt_label(round(k,2))})", "#e67e22")
        if show_roots and a != 0:
            disc = -k/a
            if disc >= 0:
                sq = math.sqrt(disc)
                for r in [h-sq, h+sq]:
                    rv = round(r,1) if abs(r-round(r))>0.05 else int(round(r))
                    cv.dot(r, 0, "#2e7d32")
                    cv.label_text(r, -0.5, str(rv), "#2e7d32")
        return cv.to_svg(f"{width}px")

    @staticmethod
    def bar_chart(labels, values, color="#6366f1",
                  y_label="Frequency", title="", width=300, height=220):
        return _bar_chart(labels, values, color, y_label, title, width, height)

    @staticmethod
    def histogram(intervals, freqs, color="#6366f1",
                  x_label="", y_label="Frequency", title="", width=300, height=220):
        return _histogram(intervals, freqs, color, x_label, y_label, title, width, height)

    @staticmethod
    def box_plot(minimum, q1, median, q3, maximum, color="#6366f1", width=300, height=120):
        return _box_plot(minimum, q1, median, q3, maximum, color, width, height)

    @staticmethod
    def arrow_diagram(domain, range_vals, arrows,
                      d_label="Domain", r_label="Range", width=260, height=None):
        return _arrow_diagram(domain, range_vals, arrows, d_label, r_label, width, height)

    @staticmethod
    def points(*xy_pairs, labels=None, color="#c0392b",
               x_range=(-5,5), y_range=(-5,5), width=280, height=240):
        cv = _AxesCanvas(width, height, x_range[0], x_range[1], y_range[0], y_range[1])
        cv.draw_axes()
        for i, (x, y) in enumerate(xy_pairs):
            cv.dot(x, y, color)
            lbl = labels[i] if labels else f"({x},{y})"
            cv.label_text(x+0.2, y+0.2, lbl, color)
        return cv.to_svg(f"{width}px")

    @staticmethod
    def curve(fn, x_range=(-4,4), y_range=(-5,5),
              color="#1d4ed8", N=100, width=280, height=240):
        cv = _AxesCanvas(width, height, x_range[0], x_range[1], y_range[0], y_range[1])
        cv.draw_axes()
        pts = []
        for i in range(N+1):
            xv = x_range[0]+i*(x_range[1]-x_range[0])/N
            try:
                yv = fn(xv)
                if y_range[0]-0.5 <= yv <= y_range[1]+0.5: pts.append((xv,yv))
                else:
                    if pts: cv.polyline(pts, color); pts = []
            except: pts = []
        if pts: cv.polyline(pts, color)
        return cv.to_svg(f"{width}px")


# ══════════════════════════════════════════════════════════════════
# AXES CANVAS
# ══════════════════════════════════════════════════════════════════

class _AxesCanvas:
    def __init__(self, W, H, xmn, xmx, ymn, ymx, pad=36):
        self.W,self.H=W,H; self.pad=pad
        self.xmn,self.xmx,self.ymn,self.ymx=xmn,xmx,ymn,ymx
        self._els=[]

    def px(self,x): return self.pad+(x-self.xmn)/(self.xmx-self.xmn)*(self.W-2*self.pad)
    def py(self,y): return self.H-self.pad-(y-self.ymn)/(self.ymx-self.ymn)*(self.H-2*self.pad)
    def add(self,s): self._els.append(s)

    def draw_axes(self):
        self.add('<defs><marker id="ax" markerWidth="8" markerHeight="6" '
                 'refX="6" refY="3" orient="auto">'
                 '<polygon points="0 0,8 3,0 6" fill="#444"/></marker></defs>')
        ox,oy=self.px(0),self.py(0)
        for x in range(int(math.ceil(self.xmn)),int(math.floor(self.xmx))+1):
            self.add(f'<line x1="{self.px(x):.1f}" y1="{self.pad}" '
                     f'x2="{self.px(x):.1f}" y2="{self.H-self.pad}" stroke="#e5e7eb" stroke-width="0.8"/>')
        for y in range(int(math.ceil(self.ymn)),int(math.floor(self.ymx))+1):
            self.add(f'<line x1="{self.pad}" y1="{self.py(y):.1f}" '
                     f'x2="{self.W-self.pad}" y2="{self.py(y):.1f}" stroke="#e5e7eb" stroke-width="0.8"/>')
        self.add(f'<line x1="{self.pad/2:.0f}" y1="{oy:.1f}" '
                 f'x2="{self.W-self.pad/2:.0f}" y2="{oy:.1f}" '
                 f'stroke="#444" stroke-width="1.5" marker-end="url(#ax)"/>')
        self.add(f'<line x1="{ox:.1f}" y1="{self.H-self.pad/2:.0f}" '
                 f'x2="{ox:.1f}" y2="{self.pad/2:.0f}" '
                 f'stroke="#444" stroke-width="1.5" marker-end="url(#ax)"/>')
        self.add(f'<text x="{self.W-self.pad/2+8}" y="{oy+4}" font-size="11" fill="#555">x</text>')
        self.add(f'<text x="{ox+4}" y="{self.pad/2-4}" font-size="11" fill="#555">y</text>')
        for x in range(int(math.ceil(self.xmn)),int(math.floor(self.xmx))+1):
            if x==0: continue
            self.add(f'<text x="{self.px(x):.1f}" y="{oy+14}" text-anchor="middle" font-size="9" fill="#666">{x}</text>')

    def polyline(self, pts, color):
        ps=" ".join(f"{self.px(x):.1f},{self.py(y):.1f}" for x,y in pts)
        self.add(f'<polyline points="{ps}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linejoin="round"/>')

    def dot(self,x,y,color):
        self.add(f'<circle cx="{self.px(x):.1f}" cy="{self.py(y):.1f}" r="4" fill="{color}" stroke="white" stroke-width="1.5"/>')

    def label_text(self,x,y,txt,color):
        self.add(f'<text x="{self.px(x):.1f}" y="{self.py(y):.1f}" font-size="9" fill="{color}">{txt}</text>')

    def vline(self,x,color):
        self.add(f'<line x1="{self.px(x):.1f}" y1="{self.pad}" '
                 f'x2="{self.px(x):.1f}" y2="{self.H-self.pad}" '
                 f'stroke="{color}" stroke-width="1.5" stroke-dasharray="5,4"/>')

    def to_svg(self, max_width="300px"):
        body="\n".join(self._els)
        return (f'<svg viewBox="0 0 {self.W} {self.H}" xmlns="http://www.w3.org/2000/svg" '
                f'style="max-width:{max_width};width:100%;display:block;margin:8px auto">{body}</svg>')


# ══════════════════════════════════════════════════════════════════
# STATS & RELATION HELPERS
# ══════════════════════════════════════════════════════════════════

def _bar_chart(labels, values, color, y_label, title, W, H):
    pl=45;pr=15;pt=30;pb=40;mv=max(values) if values else 1
    cw=W-pl-pr;ch=H-pt-pb;bw=cw/len(values)*0.7;gap=cw/len(values)
    els=[]
    if title: els.append(f'<text x="{W/2}" y="{pt-10}" text-anchor="middle" font-size="11" font-weight="bold">{title}</text>')
    els.append(f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pt+ch}" stroke="#333" stroke-width="1.5"/>')
    els.append(f'<line x1="{pl}" y1="{pt+ch}" x2="{pl+cw}" y2="{pt+ch}" stroke="#333" stroke-width="1.5"/>')
    for i in range(6):
        val=mv*i/5; y=pt+ch-(val/mv)*ch
        els.append(f'<text x="{pl-6}" y="{y+4}" text-anchor="end" font-size="9" fill="#666">{fmt_label(round(val,1))}</text>')
        els.append(f'<line x1="{pl}" y1="{y}" x2="{pl+cw}" y2="{y}" stroke="#f0f0f0" stroke-width="0.8"/>')
    for i,(lbl,val) in enumerate(zip(labels,values)):
        bx=pl+gap*i+(gap-bw)/2; bh=(val/mv)*ch; by=pt+ch-bh
        els.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" stroke="white" stroke-width="1"/>')
        els.append(f'<text x="{bx+bw/2:.1f}" y="{by-4:.1f}" text-anchor="middle" font-size="9" fill="{color}">{fmt_label(val)}</text>')
        els.append(f'<text x="{bx+bw/2:.1f}" y="{pt+ch+14}" text-anchor="middle" font-size="9" fill="#444">{lbl}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'style="max-width:{W}px;width:100%;display:block;margin:8px auto">{"".join(els)}</svg>')


def _histogram(intervals, freqs, color, x_label, y_label, title, W, H):
    pl=45;pr=15;pt=30;pb=40;mf=max(freqs) if freqs else 1
    xl=intervals[0][0];xh=intervals[-1][1];cw=W-pl-pr;ch=H-pt-pb;xs=cw/(xh-xl)
    els=[]
    if title: els.append(f'<text x="{W/2}" y="{pt-10}" text-anchor="middle" font-size="11" font-weight="bold">{title}</text>')
    els.append(f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pt+ch}" stroke="#333" stroke-width="1.5"/>')
    els.append(f'<line x1="{pl}" y1="{pt+ch}" x2="{pl+cw}" y2="{pt+ch}" stroke="#333" stroke-width="1.5"/>')
    for i in range(6):
        val=mf*i/5; y=pt+ch-(val/mf)*ch
        els.append(f'<text x="{pl-6}" y="{y+4}" text-anchor="end" font-size="9" fill="#666">{fmt_label(round(val,1))}</text>')
    for (lo,hi),freq in zip(intervals,freqs):
        bx=pl+(lo-xl)*xs;bw=(hi-lo)*xs;bh=(freq/mf)*ch;by=pt+ch-bh
        els.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" fill="{color}" stroke="white" stroke-width="1.5"/>')
    for lo,_ in intervals:
        els.append(f'<text x="{pl+(lo-xl)*xs:.1f}" y="{pt+ch+14}" text-anchor="middle" font-size="9" fill="#444">{lo}</text>')
    els.append(f'<text x="{pl+cw:.1f}" y="{pt+ch+14}" text-anchor="middle" font-size="9" fill="#444">{intervals[-1][1]}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'style="max-width:{W}px;width:100%;display:block;margin:8px auto">{"".join(els)}</svg>')


def _box_plot(mn, q1, med, q3, mx, color, W, H):
    pl=30;pr=30;pt=35;pb=25;cw=W-pl-pr;span=mx-mn or 1
    my=pt+(H-pt-pb)/2; bh=(H-pt-pb)*0.5
    def xp(v): return pl+(v-mn)/span*cw
    els=[
        f'<line x1="{xp(mn):.1f}" y1="{my:.1f}" x2="{xp(q1):.1f}" y2="{my:.1f}" stroke="{color}" stroke-width="1.5"/>',
        f'<line x1="{xp(q3):.1f}" y1="{my:.1f}" x2="{xp(mx):.1f}" y2="{my:.1f}" stroke="{color}" stroke-width="1.5"/>',
    ]
    for v in [mn,mx]:
        els.append(f'<line x1="{xp(v):.1f}" y1="{my-bh/3:.1f}" x2="{xp(v):.1f}" y2="{my+bh/3:.1f}" stroke="{color}" stroke-width="1.5"/>')
    els.append(f'<rect x="{xp(q1):.1f}" y="{my-bh/2:.1f}" width="{xp(q3)-xp(q1):.1f}" height="{bh:.1f}" fill="#e0e7ff" stroke="{color}" stroke-width="2"/>')
    els.append(f'<line x1="{xp(med):.1f}" y1="{my-bh/2:.1f}" x2="{xp(med):.1f}" y2="{my+bh/2:.1f}" stroke="{color}" stroke-width="2.5"/>')
    for v in [mn,q1,med,q3,mx]:
        els.append(f'<text x="{xp(v):.1f}" y="{pt-6}" text-anchor="middle" font-size="9" fill="#555">{fmt_label(round(v,2))}</text>')
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" '
            f'style="max-width:{W}px;width:100%;display:block;margin:8px auto">{"".join(els)}</svg>')


def _arrow_diagram(domain, range_vals, arrows, d_label, r_label, W, height):
    nd=len(domain); nr=len(range_vals)
    if height is None: height=max(160,44*max(nd,nr)+40)
    dx=65;rx=W-65;dy=height/(nd+1);ry=height/(nr+1)
    dp=[(dx,int((i+1)*dy)) for i in range(nd)]
    rp=[(rx,int((i+1)*ry)) for i in range(nr)]
    oh=height/2-8
    els=[
        '<defs><marker id="ard" markerWidth="8" markerHeight="6" refX="6" refY="3" orient="auto">'
        '<polygon points="0 0,8 3,0 6" fill="#555"/></marker></defs>',
        f'<ellipse cx="{dx}" cy="{height//2}" rx="50" ry="{oh:.0f}" fill="#e8f4fd" stroke="#2c7bb6" stroke-width="1.5"/>',
        f'<ellipse cx="{rx}" cy="{height//2}" rx="50" ry="{oh:.0f}" fill="#e8f5e9" stroke="#2e7d32" stroke-width="1.5"/>',
        f'<text x="{dx}" y="14" text-anchor="middle" font-size="11" font-weight="bold" fill="#2c7bb6">{d_label}</text>',
        f'<text x="{rx}" y="14" text-anchor="middle" font-size="11" font-weight="bold" fill="#2e7d32">{r_label}</text>',
    ]
    for val,(cx,cy) in zip(domain,dp):
        els.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13" fill="#333">{fmt_label(val)}</text>')
    for val,(cx,cy) in zip(range_vals,rp):
        els.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="13" fill="#333">{fmt_label(val)}</text>')
    for di,ri in arrows:
        x1,y1=dp[di]; x2,y2=rp[ri]
        els.append(f'<line x1="{x1+26}" y1="{y1}" x2="{x2-26}" y2="{y2}" stroke="#555" stroke-width="1.5" marker-end="url(#ard)"/>')
    return (f'<svg viewBox="0 0 {W} {height}" xmlns="http://www.w3.org/2000/svg" '
            f'style="max-width:{W}px;width:100%;display:block;margin:8px auto">{"".join(els)}</svg>')


# ══════════════════════════════════════════════════════════════════
# SMOKE TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import os
    random.seed(42)
    out = "/tmp/svg_test"
    os.makedirs(out, exist_ok=True)

    tests = [
        # FIX 2: labels render as plain text, no parentheses
        ("rt_plain_labels",  SVG.figure("right_triangle",
            sides={"a": 5, "b": 9, "c": "10.3"},
            show_angles=False, show_vertices=False,
            angle_values=["", "30\u00b0", ""])),

        # FIX 1+2+6: theta label -> arc on interior, Unicode theta visible
        ("rt_theta_BL",      SVG.figure("right_triangle",
            sides={"a": "x", "b": 5, "c": "\u221a31"},
            show_angles=False, show_vertices=False,
            angle_values=["", "\u03b8", ""])),

        # FIX 2: sqrt label no parens
        ("rt_surd",          SVG.figure("right_triangle",
            sides={"a": "\u221a13", "b": "\u221a6", "c": "x"},
            show_angles=False, show_vertices=False)),

        # FIX 3: orientation BR
        ("rt_BR",            SVG.figure("right_triangle",
            sides={"a": 6, "b": 8, "c": 10},
            show_angles=False, orientation="BR",
            angle_values=["\u03b8", "", ""])),

        # Vertex labels
        ("rt_verts",         SVG.figure("right_triangle",
            sides={"a": "Opp", "b": "Adj", "c": "Hyp"},
            show_vertices=True, show_angles=False,
            angle_values=["", "\u03b8", ""])),

        # Other shapes unchanged
        ("isosceles",        SVG.figure("isosceles", show_angles=False)),
        ("equilateral",      SVG.figure("equilateral")),
        ("rectangle",        SVG.figure("rectangle", sides={"w": 9, "h": 4})),
        ("trapezium",        SVG.figure("trapezium", sides={"top": 4, "bottom": 8},
                                        height_label="h")),
        ("bar_chart",        SVG.bar_chart(["A","B","C","D"], [4,7,3,6])),
        ("parabola",         SVG.parabola(1, 2, -3)),
    ]

    for name, svg in tests:
        path = os.path.join(out, f"{name}.svg")
        with open(path, "w") as f: f.write(svg)

        # No foreignObject anywhere
        assert "foreignObject" not in svg, f"{name}: foreignObject found"
        # No raw LaTeX backslashes in output
        assert "\\theta" not in svg,  f"{name}: raw \\theta in output"
        assert "\\sqrt"  not in svg,  f"{name}: raw \\sqrt in output"
        # Labels with arcs: arc present
        if "theta" in name or name == "rt_BR":
            assert "<path" in svg, f"{name}: no arc for angle label"

        print(f"  \u2713  {name}")

    print(f"\nAll {len(tests)} tests passed -> {out}")
    print("\nFixes applied:")
    print("  FIX 1 - arc always drawn when angle_values[i] is set")
    print("  FIX 2 - plain SVG <text>, no foreignObject, no MathJax in SVG")
    print("  FIX 3 - orientation param BL|BR|TL|TR")
    print("  FIX 4 - 3:4 ratio for unknown legs")
    print("  FIX 5 - label clamping to canvas bounds")
    print("  FIX 6 - arc sweep=1 draws on INTERIOR of angle")
