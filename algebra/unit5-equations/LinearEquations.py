"""
LinearEquations.py
==================
Unit 5 — Linear Equations

Architecture
------------
1. GENERATORS  — pure math, return a data dict (no markdown)
2. REGISTRY    — maps type name → (generator, default_count, layout, difficulty)
3. RENDERER    — converts data dict → complete Pandoc markdown string
4. generate()  — called by QMD; returns list of rendered exercise dicts

QMD only needs:
    data = generate(types=[...], seed=42)
    for ex in data["exercises"]:
        print(ex["rendered"])
"""

import random
import json
import math
from fractions import Fraction
from datetime import date
from functools import reduce


# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

VARIABLES   = ["x", "y", "n", "m", "p", "t"]
PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")
NAMES = [
    "Ahmed",   "Sara",    "Omar",   "Layla",   "Yusuf",  "Nour",
    "Ibrahim", "Fatima",  "Khalid", "Mariam",  "Hassan", "Aisha",
    "James",   "Emma",    "Liam",   "Olivia",  "Noah",   "Sophia",
    "Lucas",   "Amelia",  "Ethan",  "Mia",     "Jack",   "Zara",
]


# ══════════════════════════════════════════════════════════════════
# MATH HELPERS  (pure python, no markdown)
# ══════════════════════════════════════════════════════════════════

def ri(a, b):           return random.randint(a, b)
def rv():               return random.choice(VARIABLES)
def name_pair():        return random.sample(NAMES, 2)
def one_name():         return random.choice(NAMES)

def frac(n, d=1):
    """Return a Fraction, formatted as LaTeX string."""
    f = Fraction(n, d)
    if f.denominator == 1:
        return str(f.numerator)
    sign = "-" if f < 0 else ""
    return f"{sign}\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"

def coeff(c, v):
    """Format c*v as LaTeX: '' for 1, '-' for -1."""
    c = Fraction(c)
    if c == 1:   return v
    if c == -1:  return f"-{v}"
    if c.denominator == 1: return f"{c.numerator}{v}"
    return f"\\dfrac{{{c.numerator}}}{{{c.denominator}}}{v}"

def side(a, b, v):
    """Format ax+b as LaTeX side of equation."""
    a, b = Fraction(a), Fraction(b)
    parts = []
    if a != 0: parts.append(coeff(a, v))
    if b != 0:
        if b > 0 and parts: parts.append(f"+ {frac(b)}")
        elif b < 0 and parts: parts.append(f"- {frac(abs(b))}")
        else: parts.append(frac(b))
    return " ".join(parts) if parts else "0"

def solve_ax_b_cx_d(a, b, c, d, v):
    """Solve ax+b=cx+d. Returns (x_val as Fraction, solution_steps as LaTeX)."""
    a, b, c, d = Fraction(a), Fraction(b), Fraction(c), Fraction(d)
    lc = a - c
    rc = d - b
    if lc == 0:
        raise ValueError("Degenerate equation")
    x = rc / lc
    steps = []
    if c != 0:
        steps.append(f"{side(a-c, b, v)} = {frac(d)}")
    if b != 0:
        steps.append(f"{coeff(lc, v)} = {frac(rc)}")
    steps.append(f"{v} = {frac(x)}")
    return x, " \\\\[4pt] ".join(steps)

def lcm_of(*args):
    return reduce(lambda a, b: a * b // math.gcd(a, b), args)

def term(coef, var, const=None):
    """Format coef*var [+ const] suppressing 1-coeff and 0-const."""
    c = Fraction(coef)
    if c == 0: t = "0"
    elif c == 1: t = var
    elif c == -1: t = f"-{var}"
    elif c.denominator == 1: t = f"{c.numerator}{var}"
    else: t = f"\\dfrac{{{c.numerator}}}{{{c.denominator}}}{var}"
    if const is None: return t
    b = Fraction(const)
    if b == 0: return t
    if b > 0: return f"{t} + {frac(b)}"
    return f"{t} - {frac(abs(b))}"


# ══════════════════════════════════════════════════════════════════
# DATA DICT BUILDERS
# These are the only shapes generators return.
# ══════════════════════════════════════════════════════════════════

def make_equation(equation, answer, solution, v="x"):
    """Type 1 — plain equation drill."""
    return {
        "item_type": "equation",
        "stimulus":  {"text": "", "points": [], "svg": None},
        "equation":  equation,
        "parts":     [],
        "answer":    answer,
        "solution":  solution,
        "v":         v,
    }

def make_multipart(stimulus_text, stimulus_points, stimulus_svg,
                   parts, answer, solution):
    """Type 2 — contextual multi-part (word / geo)."""
    return {
        "item_type": "multipart",
        "stimulus":  {
            "text":   stimulus_text,
            "points": stimulus_points,
            "svg":    stimulus_svg,
        },
        "equation":  "",
        "parts":     parts,   # [{"label":"i","prompt":"..."}]
        "answer":    answer,
        "solution":  solution,
        "v":         "x",
    }

def part(label, prompt):
    return {"label": label, "prompt": prompt}


# ══════════════════════════════════════════════════════════════════
# LT1 — ONE-STEP EQUATIONS
# ══════════════════════════════════════════════════════════════════

def gen_one_step_add():
    v = rv()
    b = ri(-12, 12)
    while b == 0: b = ri(-12, 12)
    d = ri(-15, 25)
    x, sol = solve_ax_b_cx_d(1, b, 0, d, v)
    eq = f"{side(1, b, v)} = {frac(d)}"
    return make_equation(eq, f"{v} = {frac(x)}", sol, v)

def gen_one_step_mult():
    v = rv()
    a = ri(2, 12)
    x_val = ri(-10, 14)
    d = a * x_val
    x, sol = solve_ax_b_cx_d(a, 0, 0, d, v)
    eq = f"{side(a, 0, v)} = {frac(d)}"
    return make_equation(eq, f"{v} = {frac(x)}", sol, v)

def gen_one_step_div():
    v = rv()
    a = ri(2, 10)
    x_val = ri(-10, 15)
    eq = f"\\dfrac{{{v}}}{{{a}}} = {x_val}"
    sol = f"{v} = {x_val * a}"
    return make_equation(eq, f"{v} = {x_val * a}", sol, v)


# ══════════════════════════════════════════════════════════════════
# LT2 — TWO-STEP EQUATIONS
# ══════════════════════════════════════════════════════════════════

def gen_two_step():
    v = rv()
    a = ri(2, 10)
    b = ri(-10, 10)
    while b == 0: b = ri(-10, 10)
    denom = random.choice([1, 1, 1, 2])
    x = Fraction(ri(-8, 12), denom)
    d = a * x + b
    eq = f"{side(a, b, v)} = {frac(d)}"
    x_val, sol = solve_ax_b_cx_d(a, b, 0, d, v)
    return make_equation(eq, f"{v} = {frac(x_val)}", sol, v)

def gen_two_step_div():
    v = rv()
    a = ri(2, 8)
    b = ri(-8, 8)
    while b == 0: b = ri(-8, 8)
    for _ in range(200):
        x = ri(-10, 15)
        d = Fraction(x + b, a)
        if d.denominator == 1:
            break
    else:
        return gen_two_step_div()
    d = int(d)
    bs = "+" if b >= 0 else "-"
    eq = f"\\dfrac{{{v} {bs} {abs(b)}}}{{{a}}} = {d}"
    sol = (f"{v} {bs} {abs(b)} = {d * a} \\\\[4pt] "
           f"{v} = {x}")
    return make_equation(eq, f"{v} = {x}", sol, v)

def gen_two_step_bracket():
    v = rv()
    a = ri(2, 8)
    b = ri(-8, 8)
    while b == 0: b = ri(-8, 8)
    x = ri(-8, 12)
    d = a * (x + b)
    bs = "+" if b >= 0 else "-"
    eq = f"{a}({v} {bs} {abs(b)}) = {d}"
    sol = (f"{v} {bs} {abs(b)} = {d // a} \\\\[4pt] "
           f"{v} = {x}")
    return make_equation(eq, f"{v} = {x}", sol, v)


# ══════════════════════════════════════════════════════════════════
# LT3 — UNKNOWNS BOTH SIDES
# ══════════════════════════════════════════════════════════════════

def gen_both_sides():
    v = rv()
    while True:
        a = ri(2, 10); c = ri(1, 8)
        if a != c: break
    b = ri(-10, 10)
    x = ri(-8, 12)
    d = a * x + b - c * x
    eq = f"{side(a, b, v)} = {side(c, d, v)}"
    x_val, sol = solve_ax_b_cx_d(a, b, c, d, v)
    return make_equation(eq, f"{v} = {frac(x_val)}", sol, v)

def gen_both_sides_bracket():
    v = rv()
    while True:
        a = ri(2, 8); c = ri(2, 8)
        if a != c: break
    b = ri(-6, 6)
    x = ri(-8, 12)
    lhs = a * (x + b)
    for _ in range(100):
        if (lhs - c * x) % c == 0:
            break
        x = ri(-8, 12); lhs = a * (x + b)
    d = (lhs - c * x) // c
    bs = "+" if b >= 0 else "-"
    ds = "+" if d >= 0 else "-"
    eq = f"{a}({v} {bs} {abs(b)}) = {c}({v} {ds} {abs(d)})"
    exp_a, exp_b = a, a * b
    exp_c, exp_d = c, c * d
    x_val, sol = solve_ax_b_cx_d(exp_a, exp_b, exp_c, exp_d, v)
    return make_equation(eq, f"{v} = {frac(x_val)}", sol, v)


# ══════════════════════════════════════════════════════════════════
# LT4 — EXPAND AND SOLVE
# ══════════════════════════════════════════════════════════════════

def gen_expand_single():
    v = rv()
    a = ri(2, 6); b = ri(2, 6); c = ri(-8, 8)
    while c == 0: c = ri(-8, 8)
    x = ri(-6, 10)
    d = a * (b * x + c)
    def _brs(co, ia, ib, var):
        ias = var if ia == 1 else f"{ia}{var}"
        if ib == 0:    inner = ias
        elif ib > 0:   inner = f"{ias} + {ib}"
        else:          inner = f"{ias} - {abs(ib)}"
        return f"{co}({inner})"
    eq = f"{_brs(a,b,c,v)} = {d}"
    ab, ac = a * b, a * c
    sol = (f"{ab}{v} {'+'if ac>=0 else '-'} {abs(ac)} = {d} \\\\[4pt] "
           f"{ab}{v} = {d - ac} \\\\[4pt] "
           f"{v} = {frac(Fraction(x))}")
    return make_equation(eq, f"{v} = {x}", sol, v)

def gen_expand_double():
    v = rv()
    a = ri(2, 5); b = ri(1, 4); c = ri(-6, 6)
    while c == 0: c = ri(-6, 6)
    d = ri(2, 5); e = ri(1, 4); f_ = ri(-6, 6)
    while f_ == 0: f_ = ri(-6, 6)
    x = ri(-5, 8)
    g = a * (b * x + c) + d * (e * x + f_)
    ab, ac = a * b, a * c
    de_, df = d * e, d * f_
    tc = ab + de_; tk = ac + df
    if tc == 0: return gen_expand_double()
    def _br2(co, ia, ib, var):
        ias = var if ia == 1 else f"{ia}{var}"
        if ib == 0:    inner = ias
        elif ib > 0:   inner = f"{ias} + {ib}"
        else:          inner = f"{ias} - {abs(ib)}"
        return f"{co}({inner})"
    eq = f"{_br2(a,b,c,v)} + {_br2(d,e,f_,v)} = {g}"
    tc_v = v if tc == 1 else f"{tc}{v}"
    sol = (f"{term(ab,v,ac)} + {term(de_,v,df)} = {g} \\\\[4pt] "
           f"{term(tc,v,tk)} = {g} \\\\[4pt] "
           f"{tc_v} = {g - tk} \\\\[4pt] "
           f"{v} = {frac(Fraction(x))}")
    return make_equation(eq, f"{v} = {x}", sol, v)

def gen_expand_cancel():
    """(ax+b)^2 = (ax+c)(ax+d) — quadratic cancels, linear remains."""
    v = rv()
    for _ in range(300):
        a = ri(1, 3); b = ri(2, 8)
        c = ri(1, 6); d = ri(1, 6)
        while c == b or d == b or c == d:
            c = ri(1, 6); d = ri(1, 6)
        lx = 2*a*b; rx = a*(c+d)
        cx = lx - rx; cn = c*d - b*b
        if cx == 0 or cn % cx != 0: continue
        x = cn // cx
        lhs = f"({a}{v} + {b})^{{2}}" if a != 1 else f"({v} + {b})^{{2}}"
        rhs = (f"({a}{v} + {c})({a}{v} + {d})"
               if a != 1 else f"({v} + {c})({v} + {d})")
        eq = f"{lhs} = {rhs}"
        sol = (f"\\text{{Expand both sides, }} {a*a}{v}^2 \\text{{ cancels:}} \\\\[4pt] "
               f"{lx}{v} + {b*b} = {a*(c+d)}{v} + {c*d} \\\\[4pt] "
               f"{cx}{v} = {cn} \\\\[4pt] "
               f"{v} = {frac(Fraction(x))}")
        return make_equation(eq, f"{v} = {x}", sol, v)
    return gen_expand_single()

def gen_bracket_neg():
    """a(bx+c) + d(ex+f) = -g(hx+k)"""
    v = rv()
    a = ri(2, 5); b = ri(1, 3); c = ri(-6, 6)
    while c == 0: c = ri(-6, 6)
    d = ri(2, 4); e = ri(1, 3); f_ = ri(-6, 6)
    while f_ == 0: f_ = ri(-6, 6)
    g = ri(1, 3); h = ri(1, 3); k = ri(-6, 6)
    while k == 0: k = ri(-6, 6)
    lx = a*b + d*e; lc = a*c + d*f_
    rx = -g*h;      rc = -g*k
    cx = lx - rx;   cn = rc - lc
    if cx == 0: return gen_bracket_neg()
    x = Fraction(cn, cx)
    def _br(co, inner_a, inner_b, var):
        """Format co(inner_a*var + inner_b) suppressing 1-coefficients and 0-constants."""
        ia_str = var if inner_a == 1 else f"{inner_a}{var}"
        if inner_b == 0:
            inner = ia_str
        elif inner_b > 0:
            inner = f"{ia_str} + {inner_b}"
        else:
            inner = f"{ia_str} - {abs(inner_b)}"
        return f"{co}({inner})"
    eq = (f"{_br(a,b,c,v)} + {_br(d,e,f_,v)} = -{_br(g,h,k,v)}")
    ac_ = a*c; df_ = d*f_; gk = g*k
    def _t(co, var, cn_):  # format term, suppress 1/-1 coeff and 0-const
        if co == 1:    ts = var
        elif co == -1: ts = f"-{var}"
        else:          ts = f"{co}{var}"
        if cn_ == 0:   return ts
        elif cn_ > 0:  return f"{ts} + {cn_}"
        else:          return f"{ts} - {abs(cn_)}"
    sol = (f"{_t(a*b,v,ac_)} + {_t(d*e,v,df_)} = {_t(-g*h,v,-gk)} \\\\[4pt] "
           f"{_t(lx,v,lc)} = {_t(rx,v,rc)} \\\\[4pt] "
           f"{cx}{v} = {cn} \\\\[4pt] "
           f"{v} = {frac(x)}")
    return make_equation(eq, f"{v} = {frac(x)}", sol, v)


# ══════════════════════════════════════════════════════════════════
# LT5 — ALGEBRAIC FRACTIONS
# ══════════════════════════════════════════════════════════════════

def gen_frac_simple():
    """(ax+b)/c = d"""
    for _ in range(300):
        v = rv(); a = ri(2, 6); b = ri(-8, 8)
        if b == 0: continue
        c = ri(2, 6); x = ri(-6, 10)
        d = Fraction(a*x+b, c)
        if d.denominator != 1: continue
        d = int(d)
        bs = "+" if b >= 0 else "-"
        num = ("" if a==1 else str(a)) + f"{v} {bs} {abs(b)}"
        eq = f"\\dfrac{{{num}}}{{{c}}} = {d}"
        sol = (f"{num} = {d*c} \\\\[4pt] "
               f"{a}{v} = {d*c - b} \\\\[4pt] "
               f"{v} = {frac(Fraction(x))}")
        return make_equation(eq, f"{v} = {x}", sol, v)
    return gen_two_step()

def gen_frac_both_sides():
    """(ax+b)/c = (dx+e)/f"""
    for _ in range(300):
        v = rv(); a = ri(2, 5); c = ri(2, 4)
        d = ri(1, 4); f_ = ri(2, 4)
        if f_*a == c*d: continue
        b = ri(-5, 5); x = ri(-5, 8)
        lhs = f_*(a*x+b)
        rem = lhs - c*d*x
        if rem % c != 0: continue
        e = rem // c
        def _nc(co, va, cn):
            xs = va if co==1 else f"{co}{va}"
            if cn == 0: return xs
            return f"{xs} + {cn}" if cn > 0 else f"{xs} - {abs(cn)}"
        n1 = _nc(a, v, b); n2 = _nc(d, v, e)
        eq = f"\\dfrac{{{n1}}}{{{c}}} = \\dfrac{{{n2}}}{{{f_}}}"
        fa = f_*a; fb = f_*b; cd = c*d; ce = c*e
        lx = fa - cd
        if lx == 1:    lx_str = v
        elif lx == -1: lx_str = f"-{v}"
        else:          lx_str = f"{lx}{v}"
        sol = (f"\\text{{Cross multiply: }} {f_}({n1}) = {c}({n2}) \\\\[4pt] "
               f"{term(fa,v,fb)} = {term(cd,v,ce)} \\\\[4pt] "
               f"{lx_str} = {ce-fb} \\\\[4pt] "
               f"{v} = {frac(Fraction(x))}")
        return make_equation(eq, f"{v} = {x}", sol, v)
    return gen_frac_simple()

def gen_frac_add():
    """(ax+b)/c + (dx+e)/f = g"""
    for _ in range(300):
        v = rv(); c = ri(2, 5); f_ = ri(2, 5)
        lc = lcm_of(c, f_)
        if lc > 30: continue
        a = ri(1, 4); d = ri(1, 4)
        b = ri(-5, 5); e = ri(-5, 5)
        x = ri(-8, 15)
        g = Fraction(a*x+b, c) + Fraction(d*x+e, f_)
        if g.denominator != 1: continue
        g = int(g)
        def _n(co, va, cn):
            xs = va if co==1 else f"{co}{va}"
            if cn == 0: return xs
            return f"{xs} + {cn}" if cn > 0 else f"{xs} - {abs(cn)}"
        n1 = _n(a, v, b); n2 = _n(d, v, e)
        eq = f"\\dfrac{{{n1}}}{{{c}}} + \\dfrac{{{n2}}}{{{f_}}} = {g}"
        t1a = lc//c*a; t1b = lc//c*b
        t2a = lc//f_*d; t2b = lc//f_*e
        tc = t1a+t2a; tk = t1b+t2b; rhs = g*lc
        sol = (f"\\text{{Multiply by }}{lc}: "
               f"{term(t1a,v,t1b)} + {term(t2a,v,t2b)} = {rhs} \\\\[4pt] "
               f"{term(tc,v,tk)} = {rhs} \\\\[4pt] "
               f"{tc}{v} = {rhs-tk} \\\\[4pt] "
               f"{v} = {frac(Fraction(x))}")
        return make_equation(eq, f"{v} = {x}", sol, v)
    return gen_frac_simple()

def gen_frac_four_terms():
    """(ax+b)/c - (dx+e)/f = (gx+h)/i + (jx+k)/l"""
    for _ in range(400):
        v = rv()
        c = ri(2, 4); f_ = ri(2, 5); i_ = ri(2, 4); l_ = ri(2, 4)
        lc = lcm_of(c, f_, i_, l_)
        if lc > 60: continue
        a = ri(1, 3); d = ri(1, 3); g = ri(1, 3)
        b = ri(-4, 4); e = ri(-4, 4); h = ri(-4, 4)
        x = ri(-5, 8)
        lhs = Fraction(a*x+b, c) - Fraction(d*x+e, f_)
        rhs_fixed = Fraction(g*x+h, i_)
        rem = lhs - rhs_fixed
        jx_k = rem * l_
        found = False
        for j in range(1, 5):
            k_frac = jx_k - Fraction(j*x)
            if k_frac.denominator == 1:
                k = int(k_frac); found = True; break
        if not found: continue
        check = (Fraction(a*x+b,c) - Fraction(d*x+e,f_)
                 - Fraction(g*x+h,i_) - Fraction(j*x+k,l_))
        if check != 0: continue
        def ns(co, va, cn):
            s = "+" if cn >= 0 else "-"
            co2 = "" if co == 1 else str(co)
            if cn == 0: return f"{co2}{va}"
            return f"{co2}{va} {s} {abs(cn)}"
        n1=ns(a,v,b); n2=ns(d,v,e); n3=ns(g,v,h); n4=ns(j,v,k)
        eq = (f"\\dfrac{{{n1}}}{{{c}}} - \\dfrac{{{n2}}}{{{f_}}} = "
              f"\\dfrac{{{n3}}}{{{i_}}} + \\dfrac{{{n4}}}{{{l_}}}")
        m1a=lc//c*a; m1b=lc//c*b
        m2a=lc//f_*d; m2b=lc//f_*e
        m3a=lc//i_*g; m3b=lc//i_*h
        m4a=lc//l_*j; m4b=lc//l_*k
        lx=m1a-m2a-m3a-m4a; lc2=m1b-m2b-m3b-m4b
        if lx == 0: continue
        sol = (f"\\text{{Multiply by }}{lc}: "
               f"{term(m1a,v,m1b)} - {term(m2a,v,m2b)} "
               f"= {term(m3a,v,m3b)} + {term(m4a,v,m4b)} \\\\[4pt] "
               f"{term(lx,v)} = {-lc2} \\\\[4pt] "
               f"{v} = {frac(Fraction(x))}")
        return make_equation(eq, f"{v} = {x}", sol, v)
    return gen_frac_simple()


# ══════════════════════════════════════════════════════════════════
# LT6 — WORD PROBLEMS
# ══════════════════════════════════════════════════════════════════

_WORD_SUBTYPES = ["number", "ages", "consecutive", "formula", "geo_word"]
_word_subtype_counts = {}

def _next_word_subtype():
    """Rotate through subtypes, max 2 of each."""
    available = [s for s in _WORD_SUBTYPES
                 if _word_subtype_counts.get(s, 0) < 2]
    if not available:
        _word_subtype_counts.clear()
        available = _WORD_SUBTYPES
    chosen = random.choice(available)
    _word_subtype_counts[chosen] = _word_subtype_counts.get(chosen, 0) + 1
    return chosen

def gen_word_problem():
    """Dispatch to a word subtype, rotating to avoid repetition."""
    subtype = _next_word_subtype()
    return {
        "number":      _word_number,
        "ages":        _word_ages,
        "consecutive": _word_consecutive,
        "formula":     _word_formula,
        "geo_word":    _word_geo_prose,
    }[subtype]()

def _word_number():
    a = ri(2, 8); b = ri(1, 10)
    x = ri(2, 20)
    while x % a != 0: x = ri(2, 20)
    ops = [
        (f"I think of a number. I multiply it by {a} and add {b}. The answer is {a*x+b}.",
         a, b, a*x+b),
        (f"I think of a number. I multiply it by {a} and subtract {b}. The answer is {a*x-b}.",
         a, -b, a*x-b),
    ]
    desc, ca, cb, d = random.choice(ops)
    v = "x"
    eq = f"{side(ca, cb, v)} = {frac(Fraction(d))}"
    sol = (f"\\text{{(i) }} {eq} \\\\[4pt] "
           f"\\text{{(ii) }} {coeff(ca, v)} = {frac(Fraction(d-cb))} \\\\[4pt] "
           f"x = {frac(Fraction(x))}")
    return make_multipart(
        stimulus_text=desc,
        stimulus_points=[],
        stimulus_svg=None,
        parts=[
            part("i",  "Write an equation in $x$."),
            part("ii", "Solve to find the number."),
        ],
        answer=f"x = {frac(Fraction(x))}",
        solution=sol,
    )

def _word_ages():
    n1, n2 = name_pair()
    diff = ri(1, 8); x_val = ri(8, 25)
    total = x_val + (x_val + diff)
    n2_age = x_val + diff
    eq = f"x + (x + {diff}) = {total}"
    sol = (f"\\text{{(i) }} x + (x + {diff}) = {total} \\\\[4pt] "
           f"\\text{{(ii) }} 2x + {diff} = {total} \\\\[4pt] "
           f"2x = {total-diff} \\\\[4pt] "
           f"x = {frac(Fraction(x_val))} \\\\[4pt] "
           f"\\text{{{n1} = {x_val}, {n2} = {n2_age}}}")
    return make_multipart(
        stimulus_text=(f"{n1} is $x$ years old. "
                       f"{n2} is {diff} years older than {n1}. "
                       f"The sum of their ages is {total}."),
        stimulus_points=[],
        stimulus_svg=None,
        parts=[
            part("i",  "Form an equation in $x$."),
            part("ii", f"Find the ages of {n1} and {n2}."),
        ],
        answer=f"x = {x_val},\\; {n1}={x_val},\\; {n2}={n2_age}",
        solution=sol,
    )

def _word_consecutive():
    n = random.choice([3, 4, 5])
    x_val = ri(3, 18)
    total = sum(x_val + i for i in range(n))
    ordinal = {3:"three", 4:"four", 5:"five"}[n]
    terms = " + ".join(["x"] + [f"(x + {i})" for i in range(1, n)])
    coeff_ = n; const = sum(range(n))
    nums = ", ".join(str(x_val+i) for i in range(n))
    sol = (f"\\text{{(i) }} {terms} = {total} \\\\[4pt] "
           f"\\text{{(ii) }} {coeff_}x + {const} = {total} \\\\[4pt] "
           f"x = {frac(Fraction(x_val))} \\\\[4pt] "
           f"\\text{{Numbers: }} {nums}")
    return make_multipart(
        stimulus_text=(f"The sum of {ordinal} consecutive integers is {total}."),
        stimulus_points=[],
        stimulus_svg=None,
        parts=[
            part("i",  "Let the first integer be $x$. Write an equation."),
            part("ii", "Find the numbers."),
        ],
        answer=f"x = {x_val},\\; \\text{{numbers: }} {nums}",
        solution=sol,
    )

def _word_formula():
    n1 = one_name()
    p = ri(3, 8); q = ri(2, 6)
    while q >= p: q = ri(2, 6)
    a = ri(2, 6); b = ri(2, 8)
    T = p*a + q*b
    formula = f"T = {p}a + {q}c"
    eq = f"{p} \\times {a} + {q}c = {T}"
    sol = (f"\\text{{(i) }} T = {p}a + {q}c \\\\[4pt] "
           f"\\text{{(ii) }} {p*a} + {q}c = {T} \\\\[4pt] "
           f"{q}c = {T - p*a} \\\\[4pt] "
           f"c = {frac(Fraction(b))}")
    return make_multipart(
        stimulus_text=(f"{n1} buys tickets. "
                       f"Adult tickets cost \\${p} each and "
                       f"child tickets cost \\${q} each. "
                       f"The total cost is \\${T}. "
                       f"{n1} bought {a} adult tickets."),
        stimulus_points=[],
        stimulus_svg=None,
        parts=[
            part("i",  "Write a formula for the total cost $T$."),
            part("ii", "How many child tickets were bought?"),
        ],
        answer=f"T = {p}a + {q}c,\\; c = {b}",
        solution=sol,
    )

def _word_geo_prose():
    """Triangle angles word problem — prose only, no SVG."""
    for _ in range(200):
        x_val = ri(10, 35)
        a1, b1 = ri(1, 3), ri(5, 25)
        a2, b2 = ri(1, 3), ri(5, 25)
        a3 = ri(1, 3)
        b3 = 180 - (a1+a2+a3)*x_val - b1 - b2
        if b3 < 5: continue
        ang1 = a1*x_val+b1; ang2 = a2*x_val+b2; ang3 = a3*x_val+b3
        tb = b1+b2+b3; ta = a1+a2+a3
        sol = (f"\\text{{(i) }} {ta}x + {tb} = 180 \\\\[4pt] "
               f"\\text{{(ii) }} x = {frac(Fraction(x_val))} \\\\[4pt] "
               f"\\text{{Angles: }}{ang1}^\\circ,\\; {ang2}^\\circ,\\; {ang3}^\\circ")
        def _ang(a, b): return ("x" if a==1 else f"{a}x") + (f" + {b}" if b>0 else f" - {abs(b)}" if b<0 else "")
        return make_multipart(
            stimulus_text=(f"The angles of a triangle are "
                           f"$({_ang(a1,b1)})^\\circ$, "
                           f"$({_ang(a2,b2)})^\\circ$ and "
                           f"$({_ang(a3,b3)})^\\circ$."),
            stimulus_points=["Angles in a triangle sum to $180^\\circ$."],
            stimulus_svg=None,
            parts=[
                part("i",  "Form an equation in $x$."),
                part("ii", "Find $x$ and each angle."),
            ],
            answer=f"x = {x_val},\\; {ang1}^\\circ,\\; {ang2}^\\circ,\\; {ang3}^\\circ",
            solution=sol,
        )
    return _word_consecutive()


# ══════════════════════════════════════════════════════════════════
# LT7 — GEOMETRY WITH SVG
# ══════════════════════════════════════════════════════════════════

# ── SVG builders ─────────────────────────────────────────────────

def _svg_scalene(s_left, s_bottom, s_right):
    """Scalene triangle. Labels sit parallel to and outside each side."""
    # Vertices: A(80,225) B(390,225) C(315,30)
    # Left side AC: midpoint (197,127), slope angle ≈ -64°, offset 22px left
    # Right side BC: midpoint (352,127), slope angle ≈ 57°, offset 22px right
    return (
        '<svg viewBox="0 0 480 265" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:440px;display:block;margin:0.5rem 0;">'
        '<polygon points="55,230 370,230 300,28" '
        'fill="none" stroke="currentColor" stroke-width="1.8"/>'
        f'<text text-anchor="middle" font-size="13" font-family="serif" '
        f'transform="translate(140,130) rotate(-63)">{s_left}</text>'
        f'<text x="212" y="251" text-anchor="middle" font-size="13" '
        f'font-family="serif">{s_bottom}</text>'
        f'<text text-anchor="middle" font-size="13" font-family="serif" '
        f'transform="translate(375,130) rotate(56)">{s_right}</text>'
        '<text x="212" y="264" text-anchor="middle" font-size="11" '
        'font-style="italic" fill="gray">Diagram NOT accurately drawn</text>'
        '</svg>'
    )

def _svg_isosceles(s_left, s_right, s_base):
    """Isosceles triangle — two different labels (equal in value)."""
    return (
        '<svg viewBox="0 0 440 250" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:400px;display:block;margin:0.5rem 0;">'
        '<polygon points="220,25 50,210 390,210" '
        'fill="none" stroke="currentColor" stroke-width="1.8"/>'
        '<line x1="122" y1="122" x2="132" y2="112" stroke="currentColor" stroke-width="1.5"/>'
        '<line x1="117" y1="117" x2="127" y2="107" stroke="currentColor" stroke-width="1.5"/>'
        '<line x1="302" y1="112" x2="312" y2="122" stroke="currentColor" stroke-width="1.5"/>'
        '<line x1="307" y1="107" x2="317" y2="117" stroke="currentColor" stroke-width="1.5"/>'
        f'<text x="108" y="130" text-anchor="middle" font-size="13" '
        f'font-family="serif" transform="rotate(-62,108,130)">{s_left}</text>'
        f'<text x="326" y="130" text-anchor="middle" font-size="13" '
        f'font-family="serif" transform="rotate(62,326,130)">{s_right}</text>'
        f'<text x="220" y="228" text-anchor="middle" font-size="13" '
        f'font-family="serif">{s_base}</text>'
        '<text x="220" y="244" text-anchor="middle" font-size="11" '
        'font-style="italic" fill="gray">Diagram NOT accurately drawn</text>'
        '</svg>'
    )

def _svg_rectangle(s_len, s_wid):
    return (
        '<svg viewBox="0 0 420 200" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:380px;display:block;margin:0.5rem 0;">'
        '<rect x="55" y="35" width="305" height="130" '
        'fill="none" stroke="currentColor" stroke-width="1.8"/>'
        '<polyline points="55,35 70,35 70,50" fill="none" '
        'stroke="currentColor" stroke-width="1.2"/>'
        f'<text x="208" y="26" text-anchor="middle" font-size="13" '
        f'font-family="serif">{s_len}</text>'
        f'<text x="46" y="102" text-anchor="middle" font-size="13" '
        f'font-family="serif" transform="rotate(-90,46,102)">{s_wid}</text>'
        '<text x="208" y="190" text-anchor="middle" font-size="11" '
        'font-style="italic" fill="gray">Diagram NOT accurately drawn</text>'
        '</svg>'
    )

def _svg_trapezium(ang_A, ang_B, ang_D):
    """Trapezium ABCD, BC ∥ AD. Three angle labels."""
    return (
        '<svg viewBox="0 0 460 220" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:420px;display:block;margin:0.5rem 0;">'
        '<polygon points="75,185 155,50 375,50 415,185" '
        'fill="none" stroke="currentColor" stroke-width="1.8"/>'
        '<line x1="252" y1="50" x2="262" y2="50" stroke="currentColor" stroke-width="1.5"/>'
        '<polyline points="258,45 264,50 258,55" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<line x1="232" y1="185" x2="242" y2="185" stroke="currentColor" stroke-width="1.5"/>'
        '<polyline points="238,180 244,185 238,190" fill="none" stroke="currentColor" stroke-width="1.5"/>'
        '<text x="63" y="200" font-size="13" font-style="italic" font-family="serif">A</text>'
        '<text x="145" y="44" font-size="13" font-style="italic" font-family="serif">B</text>'
        '<text x="377" y="44" font-size="13" font-style="italic" font-family="serif">C</text>'
        '<text x="418" y="200" font-size="13" font-style="italic" font-family="serif">D</text>'
        f'<text x="96" y="180" font-size="12" font-family="serif">{ang_A}</text>'
        f'<text x="162" y="84" font-size="12" font-family="serif">{ang_B}</text>'
        f'<text x="358" y="175" font-size="12" font-family="serif">{ang_D}</text>'
        '<path d="M 163,68 A 16,16 0 0,1 172,60" fill="none" stroke="currentColor" stroke-width="1.2"/>'
        '</svg>'
    )

def _svg_triangle_angles(a1, b1, a2, b2, a3, b3):
    def _al(a, b):
        xs = "x" if a == 1 else f"{a}x"
        if b == 0: return f"({xs})°"
        return f"({xs} + {b})°" if b > 0 else f"({xs} - {abs(b)})°"
    l1 = _al(a1, b1); l2 = _al(a2, b2); l3 = _al(a3, b3)
    return (
        '<svg viewBox="0 0 420 220" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:380px;display:block;margin:0.5rem 0;">'
        '<polygon points="210,25 45,195 375,195" '
        'fill="none" stroke="currentColor" stroke-width="1.8"/>'
        f'<text x="210" y="50" text-anchor="middle" font-size="12" font-family="serif">{l1}</text>'
        f'<text x="58" y="186" font-size="12" font-family="serif">{l2}</text>'
        f'<text x="316" y="186" font-size="12" font-family="serif">{l3}</text>'
        '<text x="210" y="212" text-anchor="middle" font-size="11" '
        'font-style="italic" fill="gray">Diagram NOT accurately drawn</text>'
        '</svg>'
    )

# ── Geo generators ────────────────────────────────────────────────

def gen_geo_triangle_perimeter():
    v = "x"
    outer = ri(2, 4); ia = ri(1, 3); ib = ri(-5, 5)
    while ib == 0: ib = ri(-5, 5)
    ca, cb = ri(2, 5), ri(-4, 8)
    ea, eb = ri(1, 4), ri(1, 7)
    s1a, s1b = outer*ia, outer*ib
    tx = s1a + ca + ea; tc = s1b + cb + eb
    for x_val in range(3, 25):
        P = tx*x_val + tc
        if P > 15: break
    def fmt_bracket(o, a, b):
        bs = "+" if b >= 0 else "-"
        inner = (f"x {bs} {abs(b)}" if a == 1
                 else f"{a}x {bs} {abs(b)}")
        return f"{o}({inner})" if o > 1 else inner
    s1_lbl = fmt_bracket(outer, ia, ib)
    def _lbl(a, b):
        xs = "x" if a == 1 else f"{a}x"
        if b == 0: return xs
        return f"{xs} {'+'if b>=0 else '-'} {abs(b)}"
    s2_lbl = _lbl(ca, cb)
    s3_lbl = _lbl(ea, eb)
    if tc == 0:    pe = f"{tx}x"
    elif tc > 0:   pe = f"{tx}x + {tc}"
    else:          pe = f"{tx}x - {abs(tc)}"
    ans_x = frac(Fraction(P - tc, tx))
    sol_a = f"({s1_lbl}) + ({s2_lbl}) + ({s3_lbl}) = {pe} \\text{{ cm}}"
    sol_b = (f"{pe} = {P} \\\\[4pt] "
             f"{tx}x = {P-tc} \\\\[4pt] x = {ans_x}")
    use_svg = random.random() < 0.5
    svg = _svg_scalene(s1_lbl, s2_lbl, s3_lbl) if use_svg else None
    return make_multipart(
        stimulus_text=(f"The lengths, in cm, of the sides of the triangle are "
                       f"${s1_lbl}$, ${s2_lbl}$ and ${s3_lbl}$."),
        stimulus_points=[],
        stimulus_svg=svg,
        parts=[
            part("i",  "Write an expression for the perimeter of the triangle."),
            part("ii", f"The perimeter is {P} cm. Find $x$."),
        ],
        answer=f"(i)\\; {pe} \\text{{ cm}},\\quad (ii)\\; x = {ans_x}",
        solution=f"\\text{{(i) }} {sol_a} \\\\[8pt] \\text{{(ii) }} {sol_b}",
    )

def gen_geo_triangle_angles():
    for _ in range(200):
        x_val = ri(10, 35)
        a1, b1 = ri(1, 3), ri(5, 25)
        a2, b2 = ri(1, 3), ri(5, 25)
        a3 = ri(1, 3)
        b3 = 180 - (a1+a2+a3)*x_val - b1 - b2
        if b3 < 5: continue
        ang1 = a1*x_val+b1; ang2 = a2*x_val+b2; ang3 = a3*x_val+b3
        tb = b1+b2+b3; ta = a1+a2+a3
        use_svg = random.random() < 0.5
        svg = _svg_triangle_angles(a1,b1,a2,b2,a3,b3) if use_svg else None
        sol = (f"\\text{{(i) }} {ta}x + {tb} = 180 \\\\[4pt] "
               f"\\text{{(ii) }} x = {frac(Fraction(x_val))} \\\\[4pt] "
               f"\\text{{Angles: }}{ang1}^\\circ,\\; {ang2}^\\circ,\\; {ang3}^\\circ")
        def _ang(a, b): return ("x" if a==1 else f"{a}x") + (f" + {b}" if b>0 else f" - {abs(b)}" if b<0 else "")
        return make_multipart(
            stimulus_text=(f"The angles of a triangle are "
                           f"$({_ang(a1,b1)})^\\circ$, "
                           f"$({_ang(a2,b2)})^\\circ$ and "
                           f"$({_ang(a3,b3)})^\\circ$."),
            stimulus_points=["Angles in a triangle sum to $180^\\circ$."],
            stimulus_svg=svg,
            parts=[
                part("i",  "Form an equation in $x$."),
                part("ii", "Find $x$ and each angle."),
            ],
            answer=f"x={x_val},\\; {ang1}^\\circ,\\; {ang2}^\\circ,\\; {ang3}^\\circ",
            solution=sol,
        )
    return _word_geo_prose()

def gen_geo_trapezium():
    for _ in range(300):
        a_a, a_b = ri(3, 6), ri(20, 35)
        b_a, b_b = ri(2, 4), ri(40, 60)
        ta = a_a + b_a; tb = b_b - a_b
        if (180 - tb) % ta != 0: continue
        x_val = (180 - tb) // ta
        if x_val < 5: continue
        ang_A = a_a*x_val - a_b; ang_B = b_a*x_val + b_b
        if ang_A < 30 or ang_B < 60: continue
        d_a, d_e = ri(2, 4), ri(5, 20)
        ang_D = d_a*x_val + d_e
        ang_C = 360 - ang_A - ang_B - ang_D
        if ang_C < 30: continue
        largest = max(ang_A, ang_B, ang_C, ang_D)
        lA = f"({a_a}x - {a_b})°"; lB = f"({b_a}x + {b_b})°"
        lD = f"({d_a}x + {d_e})°"
        use_svg = random.random() < 0.5
        svg = _svg_trapezium(lA, lB, lD) if use_svg else None
        sol = (f"\\text{{(i) Co-interior: }} ({a_a}x-{a_b}) + ({b_a}x+{b_b}) = 180 \\\\[4pt] "
               f"{ta}x + {tb} = 180 \\\\[4pt] "
               f"x = {frac(Fraction(x_val))} \\\\[4pt] "
               f"\\text{{(ii) }} \\text{{A=}}{ang_A}^\\circ,\\; \\text{{B=}}{ang_B}^\\circ,\\; "
               f"\\text{{C=}}{ang_C}^\\circ,\\; \\text{{D=}}{ang_D}^\\circ \\\\[4pt] "
               f"\\text{{Largest = }}{largest}^\\circ")
        return make_multipart(
            stimulus_text="ABCD is a trapezium.",
            stimulus_points=[
                "BC is parallel to AD.",
                f"Angle A = ${lA}$,  Angle B = ${lB}$,  Angle D = ${lD}$.",
            ],
            stimulus_svg=svg,
            parts=[
                part("i",  "Find $x$."),
                part("ii", "Find the size of the largest angle in the trapezium."),
            ],
            answer=f"x={x_val},\\; \\text{{largest}} = {largest}^\\circ",
            solution=sol,
        )
    return gen_geo_triangle_angles()

def gen_geo_rectangle():
    for _ in range(200):
        a, b = ri(2, 5), ri(1, 8)
        c, d = ri(1, 3), ri(1, 6)
        while a == c: c = ri(1, 3)
        x_val = ri(3, 12)
        P = 2*((a*x_val+b) + (c*x_val+d))
        if P > 20: break
    def _gl(a, b):
        xs = "x" if a==1 else f"{a}x"
        if b == 0: return xs
        return xs + (f" + {b}" if b>0 else f" - {abs(b)}")
    l_lbl = _gl(a, b); w_lbl = _gl(c, d)
    ta = 2*(a+c); tb_ = 2*(b+d)
    if tb_ == 0:   pe = f"{ta}x"
    elif tb_ > 0:  pe = f"{ta}x + {tb_}"
    else:          pe = f"{ta}x - {abs(tb_)}"
    ans_x = frac(Fraction(x_val))
    use_svg = random.random() < 0.5
    svg = _svg_rectangle(f"{l_lbl} cm", f"{w_lbl} cm") if use_svg else None
    sol_a = f"2({l_lbl} + {w_lbl}) = {pe} \\text{{ cm}}"
    sol_b = (f"{pe} = {P} \\\\[4pt] "
             f"{ta}x = {P-tb_} \\\\[4pt] x = {ans_x}")
    return make_multipart(
        stimulus_text=(f"A rectangle has length $({l_lbl})$ cm "
                       f"and width $({w_lbl})$ cm."),
        stimulus_points=[],
        stimulus_svg=svg,
        parts=[
            part("i",  "Write an expression for the perimeter."),
            part("ii", f"The perimeter is {P} cm. Find $x$."),
        ],
        answer=f"(i)\\; {pe} \\text{{ cm}},\\quad (ii)\\; x = {ans_x}",
        solution=f"\\text{{(i) }} {sol_a} \\\\[8pt] \\text{{(ii) }} {sol_b}",
    )

def gen_geo_isosceles():
    for _ in range(200):
        a1, b1 = ri(2, 5), ri(-4, 8)
        a2 = ri(1, a1-1) if a1 > 1 else 1
        x_val = ri(3, 12)
        b2 = (a1-a2)*x_val + b1
        if b2 < 1: continue
        ba, bb = ri(1, 3), ri(1, 6)
        side_len = a1*x_val + b1
        perim = 2*side_len + ba*x_val + bb
        if side_len > 5 and perim > 10: break
    b1s = "+" if b1 >= 0 else "-"
    def _xl(a, b):
        xs = "x" if a==1 else f"{a}x"
        if b == 0: return xs
        return xs + (f" + {b}" if b>0 else f" - {abs(b)}")
    l1 = _xl(a1, b1); l2 = _xl(a2, b2)
    base_lbl = _xl(ba, bb)
    eq = f"{l1} = {l2}"
    ans_x = frac(Fraction(x_val))
    use_svg = random.random() < 0.5
    svg = _svg_isosceles(l1, l2, base_lbl) if use_svg else None
    coeff_sol = a1 - a2
    c_str = "x" if coeff_sol == 1 else f"{coeff_sol}x"
    sol = (f"\\text{{(i) }} {eq} \\\\[4pt] "
           f"{c_str} = {b2-b1} \\\\[4pt] "
           f"x = {ans_x} \\\\[4pt] "
           f"\\text{{(ii) Perimeter}} = {perim} \\text{{ cm}}")
    return make_multipart(
        stimulus_text=(f"An isosceles triangle has equal sides "
                       f"$({l1})$ cm and $({l2})$ cm. "
                       f"The base is $({base_lbl})$ cm."),
        stimulus_points=[],
        stimulus_svg=svg,
        parts=[
            part("i",  "Find $x$."),
            part("ii", "Find the perimeter of the triangle."),
        ],
        answer=f"x = {ans_x},\\; P = {perim} \\text{{ cm}}",
        solution=sol,
    )


# ══════════════════════════════════════════════════════════════════
# REGISTRY
# Each entry: (generator_fn, default_count, layout, difficulty, lt)
# layout: "grid" = compact 3-col  |  "list" = full-width one per row
# ══════════════════════════════════════════════════════════════════

# REGISTRY: (generator, default_count, layout, difficulty, lt, grid_cols)
# grid_cols only used when layout="grid": 3=short eqs, 2=medium, 1=long
REGISTRY = {
    # LT1
    "one_step_add":          (gen_one_step_add,          12, "grid",  "easy",   "LT1", 3),
    "one_step_mult":         (gen_one_step_mult,         12, "grid",  "easy",   "LT1", 3),
    "one_step_div":          (gen_one_step_div,          8,  "grid",  "easy",   "LT1", 3),
    # LT2
    "two_step":              (gen_two_step,              8,  "grid",  "easy",   "LT2", 3),
    "two_step_div":          (gen_two_step_div,          6,  "grid",  "medium", "LT2", 3),
    "two_step_bracket":      (gen_two_step_bracket,      6,  "grid",  "medium", "LT2", 3),
    # LT3
    "both_sides":            (gen_both_sides,            6,  "grid",  "medium", "LT3", 2),
    "both_sides_bracket":    (gen_both_sides_bracket,    4,  "grid",  "medium", "LT3", 2),
    # LT4
    "expand_single":         (gen_expand_single,         6,  "grid",  "medium", "LT4", 2),
    "expand_double":         (gen_expand_double,         4,  "grid",  "hard",   "LT4", 1),
    "expand_cancel":         (gen_expand_cancel,         4,  "grid",  "hard",   "LT4", 2),
    "bracket_neg":           (gen_bracket_neg,           4,  "grid",  "hard",   "LT4", 1),
    # LT5
    "frac_simple":           (gen_frac_simple,           6,  "grid",  "medium", "LT5", 3),
    "frac_both_sides":       (gen_frac_both_sides,       4,  "grid",  "hard",   "LT5", 2),
    "frac_add":              (gen_frac_add,              4,  "grid",  "hard",   "LT5", 2),
    "frac_four_terms":       (gen_frac_four_terms,       3,  "grid",  "hard",   "LT5", 1),
    # LT6
    "word_problem":          (gen_word_problem,          4,  "list",  "medium", "LT6", 1),
    # LT7
    "geo_triangle_perimeter":(gen_geo_triangle_perimeter,2,  "list",  "medium", "LT7", 1),
    "geo_triangle_angles":   (gen_geo_triangle_angles,   2,  "list",  "medium", "LT7", 1),
    "geo_trapezium":         (gen_geo_trapezium,         2,  "list",  "hard",   "LT7", 1),
    "geo_rectangle":         (gen_geo_rectangle,         2,  "list",  "medium", "LT7", 1),
    "geo_isosceles":         (gen_geo_isosceles,         2,  "list",  "medium", "LT7", 1),
}


# ══════════════════════════════════════════════════════════════════
# RENDERER
# Converts a data dict → complete Pandoc markdown string.
# This is the ONLY place that knows about markdown syntax.
# ══════════════════════════════════════════════════════════════════

def _render_stimulus(s):
    """Render the stimulus block: SVG, text, bullet points.
    Always opens with a blank line so text never runs inline with heading."""
    out = ["\n"]   # guaranteed blank line before any content
    if s["svg"]:
        out.append(f"\n{s['svg']}\n")
    if s["text"]:
        out.append(f"\n{s['text']}\n")
    if s["points"]:
        out.append("\n")
        for pt in s["points"]:
            out.append(f"- {pt}\n")
        out.append("\n")
    return "".join(out)

def _render_solution_callout(item):
    """Collapsed solution callout with vertically aligned steps."""
    # Generators use \\[4pt] as step separator.
    # In align* we need \\ (two backslashes in output = one line break).
    # Python string \\\\  = 4 backslashes = \\ in output (align* newline).
    raw = item["solution"]
    raw = raw.replace("\\\\[8pt]", " \\\\")
    raw = raw.replace("\\\\[4pt]", " \\\\")
    raw = raw.replace("\\[8pt]", " \\\\")
    raw = raw.replace("\\[4pt]", " \\\\")
    steps = [s.strip() for s in raw.split("\\\\") if s.strip()]
    seen = []; deduped = []
    for s in steps:
        if s not in seen: seen.append(s); deduped.append(s)
    sol = " \\\\ ".join(deduped)
    math_block = "\\begin{align*}\n" + sol + "\n\\end{align*}"
    out = []
    out.append('\n::: {.callout-tip collapse="true"}')
    out.append("\n## \U0001f50d View Solution\n")
    out.append("\n" + math_block + "\n")
    out.append("\n**Answer:** $" + item["answer"] + "$\n")
    out.append(":::\n")
    return "".join(out)

def render_item(item, outer_label, ex_number, show_solution=True):
    """
    Render one exercise item to a complete Pandoc markdown string.
    outer_label = "a", "b", "c" ...
    ex_number   = used for cross-reference id
    """
    lines = []

    # ── Exercise div open (label is inside, no duplicate heading) ──
    lines.append(f"\n::::: {{#exr-u5-{ex_number}}}\n")

    # ── Stimulus ──
    lines.append(_render_stimulus(item["stimulus"]))

    # ── Task ──
    if item["item_type"] == "equation":
        # Type 1: display the equation
        lines.append(f"\n$$\n{item['equation']}\n$$\n")
    else:
        # Type 2: sub-parts (i)(ii)
        for p in item["parts"]:
            lines.append(f"\n**({p['label']})** {p['prompt']}\n")

    # ── Solution ──
    if show_solution:
        lines.append(_render_solution_callout(item))

    # ── Exercise div close ──
    lines.append("\n:::::\n")

    return "".join(lines)


def render_list_block(items, labels, ex_id, show_solution=True):
    """
    Each word/geo item = its own exercise block.
    Uses a plain div with manual heading to avoid Quarto pulling
    the first paragraph inline with the exercise number.
    """
    lines = []
    for k, item in enumerate(items):
        item_id = f"{ex_id}-{k+1}" if len(items) > 1 else ex_id
        # Use standard Quarto exercise div
        lines.append(f"\n::::: {{#exr-u5-{item_id}}}\n")
        # HTML block comment forces Quarto to treat next paragraph as body, not caption
        lines.append("\n```{=html}\n<!-- ex-body -->\n```\n")
        lines.append(_render_stimulus(item["stimulus"]))
        for p in item["parts"]:
            lines.append(f"\n**({p['label']})** {p['prompt']}\n")
        if show_solution:
            lines.append(_render_solution_callout(item))
        lines.append("\n:::::\n")
    return "".join(lines)


def render_grid_block(items, labels, ex_numbers, cols=3,
                      show_solution=True, ex_id=None):
    """
    Render all equation items as ONE exercise block.
    ONE #exr div, grid layout inside, ONE shared solution callout.
    """
    col_width = 12 // cols
    rows       = [items[i:i+cols]  for i in range(0, len(items), cols)]
    row_labels = [labels[i:i+cols] for i in range(0, len(labels), cols)]
    lines = []

    # Open single exercise div
    if ex_id:
        lines.append(f"\n::::: {{#exr-u5-{ex_id}}}\n")

    # Grid rows — label + equation on one line, no solution per cell
    for row, rlabels in zip(rows, row_labels):
        lines.append("\n:::: {.grid}\n")
        for item, lbl in zip(row, rlabels):
            lines.append(f"\n::: {{.g-col-{col_width}}}\n")
            lines.append(f"\n**{lbl})** $\\displaystyle {item['equation']}$\n")
            lines.append("\n:::\n")
        lines.append("\n::::}\n".replace("}", ""))

    # ONE solution callout for entire exercise block
    if show_solution:
        lines.append('\n::: {.callout-tip collapse="true"}')
        lines.append("\n## \U0001f50d View Solutions\n")
        for item, lbl in zip(items, labels):
            raw = item["solution"].replace("\\\\[8pt]", " \\\\")
            raw = raw.replace("\\\\[4pt]", " \\\\")
            raw = raw.replace("\\[8pt]", " \\\\")
            raw = raw.replace("\\[4pt]", " \\\\")
            # Deduplicate repeated steps (e.g. one-step solutions)
            steps = [s.strip() for s in raw.split("\\\\") if s.strip()]
            seen = []; deduped = []
            for s in steps:
                if s not in seen: seen.append(s); deduped.append(s)
            sol = " \\\\ ".join(deduped)
            math_b = "\\begin{align*}\n" + sol + "\n\\end{align*}"
            lines.append(f"\n**{lbl})** $\\displaystyle {item['equation']}$\n")
            lines.append("\n" + math_b + "\n")
        lines.append("\n:::\n")

    # Close exercise div
    if ex_id:
        lines.append("\n:::::\n")

    return "".join(lines)


def generate(types, seed=42, show_solutions=True,
             count_override=None, count=None, layout_override=None):
    # count is an alias for count_override (used by worksheet.js)
    if count is not None and count_override is None:
        count_override = count
    """
    Generate and render all exercises.

    Parameters
    ----------
    types          : list of type names from REGISTRY
    seed           : random seed (reproducible output)
    show_solutions : include solution callouts
    count_override : override default count for ALL types
    layout_override: override default layout for ALL types

    Returns
    -------
    dict with keys:
      "exercises" : list of dicts, each with:
                      "rendered"   → complete Pandoc markdown string
                      "difficulty" → for tab grouping in QMD
                      "lt"         → learning target
                      "type"       → exercise type name
      "meta"      : worksheet metadata
    """
    if seed is not None:
        random.seed(seed)
    _word_subtype_counts.clear()

    exercises = []
    global_label_idx = 0  # counts exercise blocks (one per type)

    for ex_type in types:
        if ex_type not in REGISTRY:
            raise ValueError(f"Unknown type: '{ex_type}'. "
                             f"Available: {sorted(REGISTRY.keys())}")

        gen_fn, default_count, default_layout, difficulty, lt, grid_cols = REGISTRY[ex_type]
        count  = count_override  if count_override  is not None else default_count
        layout = layout_override if layout_override is not None else default_layout

        # Generate items
        items = []
        attempts = 0
        while len(items) < count and attempts < count * 20:
            try:
                item = gen_fn()
                items.append(item)
            except Exception:
                pass
            attempts += 1

        if not items:
            continue

        # Assign labels (restart a,b,c... per block) and exercise ID
        labels  = [PART_LABELS[i % 26] for i in range(len(items))]
        global_label_idx += 1
        ex_id   = str(global_label_idx)
        ex_nums = [f"{ex_id}-{i+1}" for i in range(len(items))]

        # Render
        if layout == "grid" and all(it["item_type"] == "equation" for it in items):
            rendered = render_grid_block(items, labels, ex_nums,
                                         cols=grid_cols, show_solution=show_solutions,
                                         ex_id=ex_id)
        else:
            # All list items wrapped in ONE exercise div — labels a) b) inside
            rendered = render_list_block(items, labels, ex_id,
                                         show_solution=show_solutions)

        # Clean title from type name
        ex_title = ex_type.replace("_", " ").title()
        exercises.append({
            "type":       ex_type,
            "title":      ex_title,
            "difficulty": difficulty,
            "lt":         lt,
            "rendered":   rendered,
            "items":      items,   # raw items for worksheet
        })

    # Build worksheet-compatible exercise list (for worksheet.js)
    ws_exercises = []
    for i, ex in enumerate(exercises, 1):
        parts = []
        for j, item in enumerate(ex.get("items", [])):
            if item.get("item_type") == "equation":
                parts.append({
                    "label":          PART_LABELS[j % 26],
                    "question_latex": item.get("equation", ""),
                    "answer_latex":   item.get("answer", ""),
                    "solution_latex": item.get("solution", ""),
                    "is_wide":        False,
                    "is_word":        False,
                })
        if parts:
            ws_exercises.append({
                "number":      i,
                "title":       ex["title"],
                "instruction": "Solve for the unknown variable.",
                "parts":       parts,
            })

    ws_meta = {
        "title":       "Linear Equations",
        "unit":        "Unit 5 · Linear Equations",
        "date":        str(date.today()),
        "total_parts": sum(len(e["parts"]) for e in ws_exercises),
        "seed":        seed,
    }
    return {
        "worksheet": ws_meta,
        "exercises": ws_exercises,       # worksheet.js reads this
        "_exercises_qmd": exercises,     # QMD reads this
        "meta": {
            "date":  str(date.today()),
            "seed":  seed,
            "types": types,
        },
    }


# ══════════════════════════════════════════════════════════════════
# PYODIDE ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def generate_session(types_json, seed=42, count=None, show_solutions=False):
    """Called by Pyodide worksheet. Returns {worksheet, exercises} for worksheet.js."""
    types = json.loads(types_json)
    data = generate(types=types, seed=seed, count_override=count,
                    show_solutions=show_solutions)
    return json.dumps({"worksheet": data["worksheet"], "exercises": data["exercises"]})



# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--types", nargs="+", default=["two_step"])
    parser.add_argument("--seed",  type=int,  default=42)
    parser.add_argument("--list-types", action="store_true")
    args = parser.parse_args()

    if args.list_types:
        print("\nAvailable types:\n")
        for k, (_, cnt, lay, diff, lt) in sorted(REGISTRY.items()):
            badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(diff,"⚪")
            print(f"  {badge} {k:<28} count={cnt:<3} layout={lay:<5} {lt}")
        print()
    else:
        data = generate(types=args.types, seed=args.seed, show_solutions=True)
        for ex in data["_exercises_qmd"]:
            print(ex["rendered"])
