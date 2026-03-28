"""
Quadratics.py
=============
Unit 6 — Quadratic Equations (MYP5)

Architecture
------------
1. GENERATORS  — pure math, return a data dict (no markdown)
2. REGISTRY    — maps type name → (generator, count, layout, difficulty, lt, cols)
3. RENDERER    — converts data dict → complete Pandoc markdown string
4. generate()  — called by QMD; returns data dict with _exercises_qmd, exercises, worksheet

QMD only needs:
    data = generate(types=[...], seed=42)
    for ex in data["_exercises_qmd"]:
        print(ex["rendered"])
"""

import random
import math
import json
from fractions import Fraction
from datetime import date
from functools import reduce

# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

VARIABLES   = ["x", "y", "n", "m"]
PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")
NAMES = [
    "Ahmed","Sara","Omar","Layla","Yusuf","Nour",
    "Ibrahim","Fatima","Khalid","Mariam","Hassan","Aisha",
    "James","Emma","Liam","Olivia","Noah","Sophia","Lucas","Amelia",
]

# ══════════════════════════════════════════════════════════════════
# MATH HELPERS
# ══════════════════════════════════════════════════════════════════

def ri(a, b):           return random.randint(a, b)
def rv():               return random.choice(VARIABLES)
def one_name():         return random.choice(NAMES)
def name_pair():        return random.sample(NAMES, 2)

def frac(n, d=1):
    f = Fraction(n, d)
    if f.denominator == 1: return str(f.numerator)
    sign = "-" if f < 0 else ""
    return f"{sign}\\dfrac{{{abs(f.numerator)}}}{{{f.denominator}}}"

def coeff(c, v):
    c = Fraction(c)
    if c == 1:  return v
    if c == -1: return f"-{v}"
    if c.denominator == 1: return f"{c.numerator}{v}"
    return f"\\dfrac{{{c.numerator}}}{{{c.denominator}}}{v}"

def fmt_quad(a, b, c, v="x"):
    """Format ax²+bx+c as LaTeX, suppressing 1/-1 coefficients and 0 terms."""
    parts = []
    # ax² term
    if a == 1:    parts.append(f"{v}^2")
    elif a == -1: parts.append(f"-{v}^2")
    elif a != 0:  parts.append(f"{a}{v}^2")
    # bx term
    if b == 1:
        parts.append(f"+ {v}" if parts else v)
    elif b == -1:
        parts.append(f"- {v}")
    elif b > 0:
        parts.append(f"+ {b}{v}" if parts else f"{b}{v}")
    elif b < 0:
        parts.append(f"- {abs(b)}{v}")
    # c term
    if c > 0:  parts.append(f"+ {c}" if parts else str(c))
    elif c < 0: parts.append(f"- {abs(c)}")
    return " ".join(parts) if parts else "0"

def fmt_factor(a, b, v="x"):
    """Format (av + b) suppressing a=1/-1 and b=0."""
    if a == 1 and b == 0:  return f"({v})"
    if a == 1 and b > 0:   return f"({v} + {b})"
    if a == 1 and b < 0:   return f"({v} - {abs(b)})"
    if a == -1 and b == 0: return f"(-{v})"
    if a == -1 and b > 0:  return f"(-{v} + {b})"
    if a == -1 and b < 0:  return f"(-{v} - {abs(b)})"
    if b == 0:             return f"({a}{v})"
    if b > 0:              return f"({a}{v} + {b})"
    return f"({a}{v} - {abs(b)})"

def discriminant(a, b, c):
    return b*b - 4*a*c

def simplify_surd(n):
    """Return (k, m) such that √n = k√m (m square-free). n must be ≥ 0."""
    if n < 0: return (0, -1)   # signal: non-real
    if n == 0: return (0, 0)
    k = 1
    m = n
    i = 2
    while i * i <= m:
        while m % (i * i) == 0:
            m //= i * i
            k *= i
        i += 1
    return (k, m)

def fmt_surd_roots(a, b, c, v="x"):
    """
    Full quadratic formula working as LaTeX steps.
    Returns (roots_str, steps_latex, discriminant_val)
    roots_str: human-readable answer string
    v: variable letter to use (default 'x')
    """
    disc = discriminant(a, b, c)
    steps = []
    steps.append(f"{v} = \\dfrac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{{2*a}}}")
    # Second step: show simplified discriminant
    _k_s, _m_s = simplify_surd(disc)
    if _m_s <= 1:  # perfect square or zero
        steps.append(f"{v} = \\dfrac{{{-b} \\pm {_k_s}}}{{{2*a}}}")
    else:
        steps.append(f"{v} = \\dfrac{{{-b} \\pm \\sqrt{{{disc}}}}}{{{2*a}}}")


    if disc < 0:
        steps.append(f"\\text{{Discriminant }} = {disc} < 0 \\\\[4pt] \\text{{No real solutions}}")
        return "No real solutions", " \\\\[4pt] ".join(steps), disc

    k, m = simplify_surd(disc)

    if m == 0:
        # disc = 0, one repeated root
        x_val = Fraction(-b, 2*a)
        steps.append(f"{v} = \\dfrac{{{-b}}}{{{2*a}}} = {frac(x_val)}")
        return f"{v} = {frac(x_val)}", " \\\\[4pt] ".join(steps), disc

    if m == 1:
        # Perfect square: k² = disc
        x1 = Fraction(-b + k, 2*a)
        x2 = Fraction(-b - k, 2*a)
        steps.append(f"{v} = \\dfrac{{{-b} \\pm {k}}}{{{2*a}}}")
        steps.append(f"{v} = {frac(x1)} \\text{{ or }} {v} = {frac(x2)}")
        return f"{v} = {frac(x1)} or {v} = {frac(x2)}", " \\\\[4pt] ".join(steps), disc

    # Irrational: simplify surd
    # If m==1 after simplify_surd, disc was a perfect square — handle as integer roots
    if m == 1:
        x1 = Fraction(-b + k, 2*a)
        x2 = Fraction(-b - k, 2*a)
        # step 2 already added "± k", just add final answers
        steps.append(f"{v} = {frac(x1)} \\text{{ or }} {v} = {frac(x2)}")
        return f"{v} = {frac(x1)} or {v} = {frac(x2)}", " \\\\[4pt] ".join(steps), disc
    g = math.gcd(math.gcd(abs(-b), k), abs(2*a))
    nb = -b // g; nk = k // g; nd = (2*a) // g

    if nd == 1:
        if nb == 0:
            surd_str = f"\\pm {nk}\\sqrt{{{m}}}"
            ans_str  = f"{v} = \\pm {nk}\\sqrt{{{m}}}" if nk != 1 else f"{v} = \\pm \\sqrt{{{m}}}"
        else:
            surd_str = f"{nb} \\pm {nk}\\sqrt{{{m}}}" if nk != 1 else f"{nb} \\pm \\sqrt{{{m}}}"
            ans_str  = f"{v} = {surd_str}"
    else:
        if nb == 0:
            surd_str = f"\\dfrac{{\\pm {nk}\\sqrt{{{m}}}}}{{{nd}}}"
        else:
            nk_str = f"{nk}\\sqrt{{{m}}}" if nk != 1 else f"\\sqrt{{{m}}}"
            surd_str = f"\\dfrac{{{nb} \\pm {nk_str}}}{{{nd}}}"
        ans_str = f"{v} = {surd_str}"

    if g > 1:
        steps.append(f"{v} = \\dfrac{{{-b} \\pm {k}\\sqrt{{{m}}}}}{{{2*a}}}")
    steps.append(ans_str)

    sq = math.sqrt(m)
    x1_dec = round((-b + k*sq) / (2*a), 3)
    x2_dec = round((-b - k*sq) / (2*a), 3)
    return f"{ans_str.replace(v + ' = ','')}", " \\\\[4pt] ".join(steps), disc

def round_dp(val, dp):
    """Round float to dp decimal places, return as string."""
    return f"{val:.{dp}f}"

def sum_product_steps(b, c):
    """Find p, q such that p*q=c and p+q=b. Returns (p, q) or None."""
    for p in range(-abs(c)-1, abs(c)+2):
        if p == 0: continue
        if c % p == 0:
            q = c // p
            if p + q == b:
                return (p, q)
    return None

# ══════════════════════════════════════════════════════════════════
# DATA DICT BUILDERS
# ══════════════════════════════════════════════════════════════════

def make_equation(equation, answer, solution, v="x", is_wide=False, override_instruction=None):
    return {
        "item_type":            "equation",
        "stimulus":             {"text": "", "points": [], "svg": None},
        "equation":             equation,
        "parts":                [],
        "answer":               answer,
        "solution":             solution,
        "v":                    v,
        "is_wide":              is_wide,
        "override_instruction": override_instruction,
    }

def make_multipart(stimulus_text, stimulus_points, stimulus_svg,
                   parts, answer, solution):
    return {
        "item_type": "multipart",
        "stimulus":  {"text": stimulus_text, "points": stimulus_points, "svg": stimulus_svg},
        "equation":  "",
        "parts":     parts,
        "answer":    answer,
        "solution":  solution,
        "v":         "x",
    }

def part(label, prompt):
    return {"label": label, "prompt": prompt}

# ══════════════════════════════════════════════════════════════════
# LT1 — FACTORISING SIMPLE (a=1)
# ══════════════════════════════════════════════════════════════════

def gen_factorise_simple():
    """Factorise x²+bx+c where both roots positive."""
    for _ in range(300):
        p = ri(1, 10); q = ri(1, 10)
        b = p + q; c = p * q
        if b == 0 or c == 0: continue
        v = rv()
        eq  = fmt_quad(1, b, c, v)
        ans = f"{fmt_factor(1,p,v)}{fmt_factor(1,q,v)}"
        sol = (f"\\text{{Find }} p, q: p \\times q = {c},\\; p + q = {b} \\\\[4pt] "
               f"p = {p},\\; q = {q} \\\\[4pt] "
               f"{eq} = {ans}")
        return make_equation(eq, ans, sol, v)

def gen_factorise_negative_c():
    """Factorise x²+bx+c where c<0 (roots opposite signs)."""
    for _ in range(300):
        p = ri(1, 10); q = ri(1, 9)
        if p == q: continue
        b = p - q; c = -p * q   # roots are p and -q
        v = rv()
        eq  = fmt_quad(1, b, c, v)
        ans = f"{fmt_factor(1,p,v)}{fmt_factor(1,-q,v)}"
        sol = (f"\\text{{Find }} p, q: p \\times q = {c},\\; p + q = {b} \\\\[4pt] "
               f"p = {p},\\; q = {-q} \\\\[4pt] "
               f"{eq} = {ans}")
        return make_equation(eq, ans, sol, v)

def gen_factorise_both_negative():
    """Factorise x²+bx+c where b<0, c>0 (both roots negative)."""
    for _ in range(300):
        p = ri(1, 10); q = ri(1, 10)
        b = -(p + q); c = p * q
        if b == 0 or c == 0: continue
        v = rv()
        eq  = fmt_quad(1, b, c, v)
        ans = f"{fmt_factor(1,-p,v)}{fmt_factor(1,-q,v)}"
        sol = (f"\\text{{Find }} p, q: p \\times q = {c},\\; p + q = {b} \\\\[4pt] "
               f"p = {-p},\\; q = {-q} \\\\[4pt] "
               f"{eq} = {ans}")
        return make_equation(eq, ans, sol, v)

# ══════════════════════════════════════════════════════════════════
# LT2 — FACTORISING HARDER (a≠1)
# ══════════════════════════════════════════════════════════════════

def gen_factorise_hard():
    """Factorise ax²+bx+c, a≠1, using ac-method."""
    for _ in range(400):
        a = ri(2, 5)
        r1 = ri(1, 6); r2 = ri(1, 6)
        # (ax + r1)(x + r2) = ax² + (ar2+r1)x + r1*r2
        b = a*r2 + r1; c = r1*r2
        if b <= 0 or c <= 0: continue
        ac = a * c
        pq = sum_product_steps(b, ac)
        if not pq: continue
        p, q = pq
        v = rv()
        eq  = fmt_quad(a, b, c, v)
        ans_orig = f"{fmt_factor(a,r1)}{fmt_factor(1,r2)}"
        # fmt_factor uses 'x' by default — rebuild with correct variable
        def _fv(co, b_offset, var):
            if co == 1 and b_offset == 0:  return f"({var})"
            if co == 1 and b_offset > 0:   return f"({var} + {b_offset})"
            if co == 1 and b_offset < 0:   return f"({var} - {abs(b_offset)})"
            if b_offset == 0:              return f"({co}{var})"
            if b_offset > 0:               return f"({co}{var} + {b_offset})"
            return f"({co}{var} - {abs(b_offset)})"
        ans = f"{_fv(a,r1,v)}{_fv(1,r2,v)}"
        sol = (f"ac = {a} \\times {c} = {ac} \\\\[4pt] "
               f"\\text{{Find }} p, q: p \\times q = {ac},\\; p + q = {b} \\\\[4pt] "
               f"p = {p},\\; q = {q} \\\\[4pt] "
               f"{a}{v}^2 + {p if p > 1 else ''}{v} + {q if q > 1 else ''}{v} + {c} \\\\[4pt] "
               f"{v}({a}{v} + {p//math.gcd(p,a) if a else p}) + "
               f"\\text{{group}} \\\\[4pt] "
               f"{eq} = {ans}")
        return make_equation(eq, ans, sol, v)

def gen_factorise_hard_negative():
    """Factorise ax²+bx+c, a≠1, with negative terms."""
    for _ in range(400):
        a = ri(2, 4)
        r1 = ri(1, 5); r2 = ri(1, 5)
        # (ax - r1)(x - r2) = ax² - (ar2+r1)x + r1r2
        b = -(a*r2 + r1); c = r1*r2
        if b == 0 or c == 0: continue
        ac = a * c
        pq = sum_product_steps(b, ac)
        if not pq: continue
        p, q = pq
        v = rv()
        eq  = fmt_quad(a, b, c, v)
        def _fvn(co, b_offset, var):
            if co == 1 and b_offset == 0:  return f"({var})"
            if co == 1 and b_offset > 0:   return f"({var} + {b_offset})"
            if co == 1 and b_offset < 0:   return f"({var} - {abs(b_offset)})"
            if b_offset == 0:              return f"({co}{var})"
            if b_offset > 0:              return f"({co}{var} + {b_offset})"
            return f"({co}{var} - {abs(b_offset)})"
        ans = f"{_fvn(a,-r1,v)}{_fvn(1,-r2,v)}"
        sol = (f"ac = {a} \\times {c} = {ac} \\\\[4pt] "
               f"\\text{{Find }} p, q: p \\times q = {ac},\\; p + q = {b} \\\\[4pt] "
               f"p = {p},\\; q = {q} \\\\[4pt] "
               f"{eq} = {ans}")
        return make_equation(eq, ans, sol, v)

# ══════════════════════════════════════════════════════════════════
# LT3 — SPECIAL FORMS
# ══════════════════════════════════════════════════════════════════

def gen_diff_two_squares():
    """Factorise a²x² - b² = (ax+b)(ax-b)."""
    for _ in range(200):
        a = random.choice([1,1,1,2,3])
        b = ri(1, 12)
        v = rv()
        if a == 1:
            eq  = fmt_quad(1, 0, -(b*b), v)
            ans = f"({v} + {b})({v} - {b})"
            sol = (f"{v}^2 - {b}^2 = ({v} + {b})({v} - {b})")
        else:
            eq  = f"{a**2}{v}^2 - {b**2}"
            ans = f"({a}{v} + {b})({a}{v} - {b})"
            sol = (f"({a}{v})^2 - ({b})^2 = ({a}{v} + {b})({a}{v} - {b})")
        return make_equation(eq, ans, sol, v)

def gen_perfect_square():
    """Factorise x²±2bx+b² = (x±b)²."""
    for _ in range(200):
        b = ri(1, 10)
        sign = random.choice([1, -1])
        mid = 2 * b * sign
        v = rv()
        eq  = fmt_quad(1, mid, b*b, v)
        if sign == 1:
            ans = f"({v} + {b})^2"
            sol = f"({v} + {b})^2 \\quad \\text{{[perfect square]}}"
        else:
            ans = f"({v} - {b})^2"
            sol = f"({v} - {b})^2 \\quad \\text{{[perfect square]}}"
        return make_equation(eq, ans, sol, v)

# ══════════════════════════════════════════════════════════════════
# LT4 — SOLVE BY FACTORISING
# ══════════════════════════════════════════════════════════════════

def gen_solve_simple():
    """Solve x²+bx+c=0 by factorising (a=1)."""
    for _ in range(300):
        p = ri(-8, 8); q = ri(-8, 8)
        if p == 0 or q == 0 or p == q: continue
        b = p + q; c = p * q
        v = rv()
        eq   = f"{fmt_quad(1, b, c, v)} = 0"
        fact = f"{fmt_factor(1,p,v)}{fmt_factor(1,q,v)} = 0"
        ans  = f"{v} = {-p} \\text{{ or }} {v} = {-q}"
        sol  = (f"\\text{{Find }} p, q: p \\times q = {c},\\; p + q = {b} \\\\[4pt] "
                f"p = {p},\\; q = {q} \\\\[4pt] "
                f"{fact} \\\\[4pt] "
                f"{v} = {-p} \\text{{ or }} {v} = {-q}")
        return make_equation(eq, ans, sol, v)

def gen_solve_hard():
    """Solve ax²+bx+c=0 by factorising (a≠1)."""
    for _ in range(400):
        a = ri(2, 4)
        r1 = ri(-6, 6); r2 = ri(-6, 6)
        if r1 == 0 or r2 == 0 or r1 == r2: continue
        # roots: x = -r1/a and x = -r2 (from (ax+r1)(x+r2)=0)
        b = a*r2 + r1; c = r1*r2
        if b == 0: continue
        v = rv()
        eq   = f"{fmt_quad(a, b, c, v)} = 0"
        fact = f"{fmt_factor(a,r1,v)}{fmt_factor(1,r2,v)} = 0"
        x1   = frac(Fraction(-r1, a)); x2 = str(-r2)
        ans  = f"{v} = {x1} \\text{{ or }} {v} = {x2}"
        ac   = a * c
        pq   = sum_product_steps(b, ac)
        if not pq: continue
        p, q = pq
        sol  = (f"ac = {a} \\times {c} = {ac} \\\\[4pt] "
                f"p = {p},\\; q = {q} \\\\[4pt] "
                f"{fact} \\\\[4pt] "
                f"{v} = {x1} \\text{{ or }} {v} = {x2}")
        return make_equation(eq, ans, sol, v)

def gen_solve_special():
    """Solve using DOTS or perfect square."""
    choice = random.choice(["dots", "perfect"])
    v = rv()
    if choice == "dots":
        b = ri(2, 10)
        a = random.choice([1, 1, 2, 3])
        if a == 1:
            eq   = f"{fmt_quad(1, 0, -(b*b), v)} = 0"
            ans  = f"{v} = {b} \\text{{ or }} {v} = -{b}"
            sol  = (f"({v} + {b})({v} - {b}) = 0 \\\\[4pt] {ans}")
        else:
            eq   = f"{a**2}{v}^2 - {b**2} = 0"
            x1   = frac(Fraction(b, a)); x2 = frac(Fraction(-b, a))
            ans  = f"{v} = {x1} \\text{{ or }} {v} = {x2}"
            sol  = (f"({a}{v} + {b})({a}{v} - {b}) = 0 \\\\[4pt] {ans}")
    else:
        b = ri(1, 8)
        sign = random.choice([1, -1])
        mid  = 2 * b * sign
        eq   = f"{fmt_quad(1, mid, b*b, v)} = 0"
        root = -b * sign
        ans  = f"{v} = {root} \\text{{ (repeated root)}}"
        bs   = "+" if sign == 1 else "-"
        sol  = (f"({v} {bs} {b})^2 = 0 \\\\[4pt] {ans}")
    return make_equation(eq, ans, sol, v)

# ══════════════════════════════════════════════════════════════════
# LT5 — QUADRATIC FORMULA
# ══════════════════════════════════════════════════════════════════

def gen_formula_integer():
    """ax²+bx+c=0 → integer roots via formula (shows full surd working)."""
    for _ in range(400):
        p = ri(-8, 8); q = ri(-8, 8)
        if p == 0 or q == 0 or p == q: continue
        a = random.choice([1, 1, 2])
        b = -a*(p+q); c = a*p*q
        disc = discriminant(a, b, c)
        if disc < 0: continue
        k, m = simplify_surd(disc)
        if m != 1: continue   # must be perfect square
        v = rv()
        eq  = f"{fmt_quad(a, b, c, v)} = 0"
        ans_str, steps, _ = fmt_surd_roots(a, b, c, v=v)
        return make_equation(eq, ans_str, steps, v)

def gen_formula_surd():
    """ax²+bx+c=0 → irrational surd roots."""
    for _ in range(400):
        a = random.choice([1, 1, 1, 2])
        b = ri(-8, 8)
        c = ri(-6, 6)
        if b == 0 and c == 0: continue
        disc = discriminant(a, b, c)
        if disc <= 0: continue
        k, m = simplify_surd(disc)
        if m == 1: continue   # skip integer roots
        v = rv()
        eq  = f"{fmt_quad(a, b, c, v)} = 0"
        ans_str, steps, _ = fmt_surd_roots(a, b, c, v=v)
        return make_equation(eq, ans_str, steps, v)
    return gen_formula_integer()

def gen_formula_non_real():
    """ax²+bx+c=0 where discriminant<0 → no real roots."""
    for _ in range(300):
        a = ri(1, 3)
        b = ri(-4, 4)
        c = ri(1, 8)
        disc = discriminant(a, b, c)
        if disc >= 0: continue
        v = rv()
        eq  = f"{fmt_quad(a, b, c, v)} = 0"
        ans = "\\text{No real solutions}"
        _, steps, _ = fmt_surd_roots(a, b, c, v=v)
        return make_equation(eq, ans, steps, v)

# ══════════════════════════════════════════════════════════════════
# LT6 — COMPLETING THE SQUARE
# ══════════════════════════════════════════════════════════════════

def gen_complete_square_form():
    """Write x²+bx+c in (x+p)²+q form."""
    for _ in range(200):
        b = ri(-10, 10)
        if b == 0: continue
        c = ri(-10, 10)
        p = Fraction(b, 2)
        q = c - p*p
        v = rv()
        eq  = fmt_quad(1, b, c, v)
        p_s = frac(p); q_s = frac(q)
        if p > 0:
            ans = f"({v} + {p_s})^2 + {q_s}" if q >= 0 else f"({v} + {p_s})^2 - {frac(abs(q))}"
            sol = (f"\\left({v} + \\dfrac{{{b}}}{{2}}\\right)^2 - "
                   f"\\left(\\dfrac{{{b}}}{{2}}\\right)^2 {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                   f"({v} + {p_s})^2 - {frac(p*p)} {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                   f"({v} + {p_s})^2 + {q_s}" if q >= 0 else
                   f"({v} + {p_s})^2 - {frac(abs(q))}")
        else:
            abs_p = frac(abs(p))
            ans = f"({v} - {abs_p})^2 + {q_s}" if q >= 0 else f"({v} - {abs_p})^2 - {frac(abs(q))}"
            sol = (f"\\left({v} - \\dfrac{{{abs(b)}}}{{2}}\\right)^2 - "
                   f"\\left(\\dfrac{{{abs(b)}}}{{2}}\\right)^2 {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                   f"({v} - {abs_p})^2 - {frac(p*p)} {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                   + (f"({v} - {abs_p})^2 + {q_s}" if q >= 0 else f"({v} - {abs_p})^2 - {frac(abs(q))}"))
        return make_equation(eq, ans, sol, v)

def gen_complete_square_nonmonic():
    """Write ax²+bx+c in a(x+p)²+q form, a≠1."""
    for _ in range(200):
        a = random.choice([2, 2, 3, -1, -2])
        b = ri(-8, 8)
        if b == 0: continue
        c = ri(-6, 6)
        p = Fraction(b, 2*a)
        q = c - a*p*p
        v = rv()
        eq   = fmt_quad(a, b, c, v)
        p_s  = frac(p); q_s = frac(q); a_s = str(a)
        p_sign = "+" if p > 0 else "-"
        ans  = f"{a_s}({v} {p_sign} {frac(abs(p))})^2 + {q_s}" if q >= 0 else \
               f"{a_s}({v} {p_sign} {frac(abs(p))})^2 - {frac(abs(q))}"
        sol  = (f"{a_s}\\left[{v}^2 + \\dfrac{{{b}}}{{{a}}}{v}\\right] {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                f"{a_s}\\left({v} + \\dfrac{{{b}}}{{{2*a}}}\\right)^2 "
                f"{'-' if b**2//(4*a) >= 0 else '+'} \\dfrac{{{b**2}}}{{{abs(4*a)}}} {'+' if c >= 0 else '-'} {abs(c)} \\\\[4pt] "
                f"{ans}")
        return make_equation(eq, ans, sol, v)

def gen_complete_square_solve():
    """Solve x²+bx+c=0 by completing the square."""
    for _ in range(300):
        b = ri(-8, 8)
        if b == 0: continue
        c = ri(-8, 8)
        p = Fraction(b, 2)
        rhs = p*p - c
        if rhs <= 0: continue
        k, m = simplify_surd(int(rhs) if rhs.denominator == 1 else 0)
        if rhs.denominator != 1: continue
        v = rv()
        eq    = f"{fmt_quad(1, b, c, v)} = 0"
        p_s   = frac(abs(p))
        p_sign = "+" if p > 0 else "-"
        rhs_s = frac(rhs)
        if m == 1:
            x1 = frac(-p + k); x2 = frac(-p - k)
            ans = f"{v} = {x1} \\text{{ or }} {v} = {x2}"
            surd_part = str(k)
        else:
            k_s = f"{k}\\sqrt{{{m}}}" if k != 1 else f"\\sqrt{{{m}}}"
            x1s = f"{frac(-p)} + {k_s}"; x2s = f"{frac(-p)} - {k_s}"
            ans = f"{v} = {x1s} \\text{{ or }} {v} = {x2s}"
            surd_part = k_s
        sol = (f"({v} {p_sign} {p_s})^2 = {rhs_s} \\\\[4pt] "
               f"{v} {p_sign} {p_s} = \\pm {surd_part} \\\\[4pt] "
               f"{ans}")
        full_eq = f"{fmt_quad(1, b, c, v)} = 0 \\\\[4pt] ({v} {p_sign} {p_s})^2 - {rhs_s} = 0 \\\\[4pt] " + sol
        return make_equation(eq, ans, full_eq, v)

def gen_complete_square_nonmonic_solve():
    """Solve ax^2+bx+c=0 by completing the square, a != 1."""
    import math as _m2
    from math import gcd as _gcd2
    for _ in range(300):
        a = random.choice([2, 3, 2])
        b = ri(-8, 8)
        if b == 0: continue
        c = ri(-6, 6)
        disc = discriminant(a, b, c)
        if disc <= 0: continue
        p = Fraction(b, 2*a)
        rhs_num = disc; rhs_den = 4*a*a
        g = _gcd2(rhs_num, rhs_den)
        rn, rd = rhs_num//g, rhs_den//g
        sq_rd = int(_m2.sqrt(rd))
        if sq_rd*sq_rd != rd: continue
        k_r, m_r = simplify_surd(rn)
        v = rv()
        eq = f"{fmt_quad(a, b, c, v)} = 0"
        p_sign = "+" if p > 0 else "-"
        p_abs = frac(abs(p))
        if m_r == 1:
            surd_s = frac(Fraction(k_r, sq_rd))
            x1_s = frac(-p + Fraction(k_r, sq_rd))
            x2_s = frac(-p - Fraction(k_r, sq_rd))
            ans_str = f"{v} = {x1_s} \\text{{ or }} {v} = {x2_s}"
        else:
            numer = f"{k_r}\\sqrt{{{m_r}}}" if k_r != 1 else f"\\sqrt{{{m_r}}}"
            surd_s = f"\\dfrac{{{numer}}}{{{sq_rd}}}" if sq_rd != 1 else numer
            ans_str = f"{v} = {frac(-p)} + {surd_s} \\text{{ or }} {v} = {frac(-p)} - {surd_s}"
        ba = frac(Fraction(b, a)); ca = frac(Fraction(c, a))
        rhs_s = f"\\dfrac{{{rn}}}{{{rd}}}" if rd != 1 else str(rn)
        b_over_a = Fraction(b, a); c_over_a = Fraction(c, a)
        _ba_coef = int(b_over_a) if b_over_a.denominator == 1 else None
        _ba_str = ('' if _ba_coef == 1 else '-' if _ba_coef == -1 else ba)
        sol = (f"\\text{{Divide by }} {a}: "
               f"{v}^2 {'+' if b_over_a>0 else ''}{_ba_str}{v} "
               f"{'+' if c_over_a>=0 else ''}{ca} = 0 \\\\[4pt] "
               f"\\text{{Complete the square:}} \\\\[4pt] "
               f"\\left({v} {p_sign} {p_abs}\\right)^2 = {rhs_s} \\\\[4pt] "
               f"{v} {p_sign} {p_abs} = \\pm {surd_s} \\\\[4pt] "
               f"{ans_str}")
        return make_equation(eq, ans_str, sol, v)

# ══════════════════════════════════════════════════════════════════
# LT7 — WORD PROBLEMS
# ══════════════════════════════════════════════════════════════════

def gen_word_area():
    """Rectangle: length = x+a, width = x+b, area = k → solve quadratic."""
    for _ in range(300):
        a = ri(1, 8); b = ri(1, 6)
        x_val = ri(2, 10)
        area = (x_val + a) * (x_val + b)
        # x² + (a+b)x + ab - area = 0
        B = a + b; C = a*b - area
        disc = discriminant(1, B, C)
        if disc <= 0: continue
        k, m = simplify_surd(disc)
        if m != 1: continue   # keep integer roots for area problems
        x1 = (-B + k) // 2; x2 = (-B - k) // 2
        pos = max(x1, x2)
        if pos <= 0: continue
        eq = f"{fmt_quad(1, B, C, 'x')} = 0"
        ans_str, steps, _ = fmt_surd_roots(1, B, C, v="x")
        length = pos + a; width = pos + b
        sol = (f"\\text{{(i) }} (x + {a})(x + {b}) = {area} \\\\[4pt] "
               f"x^2 + {B}x + {a*b} = {area} \\\\[4pt] "
               f"x^2 {'+' if B>=0 else ''}{B}x {'+' if C>=0 else '-'} {abs(C)} = 0 \\\\[4pt] "
               f"\\text{{(ii) }} " + steps + f" \\\\[4pt] "
               f"\\text{{(iii) Taking positive root: }} x = {pos} \\\\[4pt] "
               f"\\text{{Length }} = {pos} + {a} = {length} \\text{{ cm, }}"
               f"\\text{{ Width }} = {pos} + {b} = {width} \\text{{ cm}}")
        return make_multipart(
            stimulus_text=(f"A rectangle has length $(x + {a})$ cm and width $(x + {b})$ cm. "
                           f"The area is {area} cm²."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Form a quadratic equation in $x$."),
                part("ii",  "Solve the equation, giving exact answers."),
                part("iii", "Find the dimensions of the rectangle."),
            ],
            answer=f"x = {pos}",
            solution=sol,
        )

def gen_word_consecutive():
    """Product of two consecutive integers = k."""
    for _ in range(300):
        x_val = ri(3, 15)
        prod = x_val * (x_val + 1)
        # x² + x - prod = 0
        disc = discriminant(1, 1, -prod)
        if disc <= 0: continue
        k, m = simplify_surd(disc)
        if m != 1: continue
        eq = f"n^2 + n - {prod} = 0"
        ans_str, steps, _ = fmt_surd_roots(1, 1, -prod, v="n")
        sol = (f"\\text{{(i) }} n(n+1) = {prod} \\\\[4pt] "
               f"n^2 + n - {prod} = 0 \\\\[4pt] "
               f"\\text{{(ii) }} " + steps + f" \\\\[4pt] "
               f"\\text{{(iii) Since integers are positive, }} n = {x_val} \\\\[4pt] "
               f"\\text{{Integers: }} {x_val} \\text{{ and }} {x_val + 1}")
        return make_multipart(
            stimulus_text=(f"The product of two consecutive positive integers is {prod}."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Form a quadratic equation in $n$."),
                part("ii",  "Solve the equation exactly."),
                part("iii", "Find the two integers."),
            ],
            answer=f"Integers: {x_val} and {x_val + 1}",
            solution=sol,
        )

def gen_word_projectile():
    """h = -5t² + vt + h0, find when h=0 (hits ground)."""
    for _ in range(300):
        v0 = random.choice([10, 15, 20, 25, 30])
        h0 = random.choice([5, 10, 15, 20])
        # -5t² + v0*t + h0 = 0  →  5t² - v0*t - h0 = 0
        a = 5; b = -v0; c = -h0
        disc = discriminant(a, b, c)
        if disc <= 0: continue
        k, m = simplify_surd(disc)
        t_pos = (-b + math.sqrt(disc)) / (2*a)
        if t_pos <= 0: continue
        t_round = round_dp(t_pos, 2)
        ans_str, steps, _ = fmt_surd_roots(a, b, c, v="t")
        sol = (f"\\text{{(i) The constant term {h0} is the initial height (height at }} t=0\\text{{).}} \\\\[4pt] "
               f"\\text{{(ii) Set }} h=0: \\\\[4pt] "
               f"-5t^2 + {v0}t + {h0} = 0 \\\\[4pt] "
               f"5t^2 - {v0}t - {h0} = 0 \\\\[4pt] "
               + steps + f" \\\\[4pt] "
               f"\\text{{(iii) Taking positive root: }} t \\approx {t_round} \\text{{ s}} \\\\[4pt] "
               f"\\text{{This is the time when the ball hits the ground.}}")
        return make_multipart(
            stimulus_text=(f"A ball is thrown upward with initial velocity {v0} m/s. "
                           f"Its height (m) after $t$ seconds is $h = -5t^2 + {v0}t + {h0}$."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   f"What does the constant {h0} represent in this context?"),
                part("ii",  "Find when the ball hits the ground. Give exact answers in surd form."),
                part("iii", "Find the time to 2 d.p. and interpret your answer."),
            ],
            answer=f"t \\approx {t_round} \\text{{ s (time to hit ground)}}",
            solution=sol,
        )

# ══════════════════════════════════════════════════════════════════
# LT8 — GEOMETRY
# ══════════════════════════════════════════════════════════════════

def gen_geo_rectangle():
    """Rectangle: perimeter fixed, area expressed as quadratic."""
    for _ in range(300):
        perim = random.choice([20, 24, 28, 32, 36, 40])
        # length = x, width = perim/2 - x
        half = perim // 2
        # area = x(half - x) = k → x² - half*x + k = 0
        x_val = ri(2, half - 2)
        area = x_val * (half - x_val)
        # x² - half*x + area = 0
        disc = discriminant(1, -half, area)
        if disc < 0: continue
        k_s, m = simplify_surd(disc)
        if m != 1: continue
        x1 = (half + k_s) // 2; x2 = (half - k_s) // 2
        if x1 <= 0 or x2 <= 0: continue
        eq = f"x^2 - {half}x + {area} = 0"
        ans_str, steps, _ = fmt_surd_roots(1, -half, area, v="x")
        sol = (f"\\text{{(i) }} x({half} - x) = {area} \\\\[4pt] "
               f"x^2 - {half}x {'+'if area>=0 else '-'} {abs(area)} = 0 \\\\[4pt] "
               f"\\text{{(ii) }} " + steps + f" \\\\[4pt] "
               f"\\text{{(iii) }} x = {x1} \\text{{ or }} x = {x2} \\\\[4pt] "
               f"\\text{{Length }} = {max(x1,x2)} \\text{{ cm, Width }} = {min(x1,x2)} \\text{{ cm}}")
        return make_multipart(
            stimulus_text=(f"A rectangle has perimeter {perim} cm and area {area} cm². "
                           f"Let the length be $x$ cm, so the width is $({half} - x)$ cm."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Show that $x^2 - {half}x + {area} = 0$.".replace("{half}", str(half)).replace("{area}", str(area))),
                part("ii",  "Solve the equation exactly."),
                part("iii", "Find the dimensions of the rectangle."),
            ],
            answer=f"Length = {max(x1,x2)} cm, Width = {min(x1,x2)} cm",
            solution=sol,
        )

def gen_geo_right_triangle():
    """Right triangle: sides x, x+a, hypotenuse c → Pythagoras → quadratic."""
    for _ in range(400):
        a = ri(1, 6)
        x_val = ri(3, 12)
        leg1 = x_val; leg2 = x_val + a
        hyp2 = leg1**2 + leg2**2
        k_h, m_h = simplify_surd(hyp2)
        # Use integer hypotenuse only for cleaner problems
        if m_h != 1: continue
        hyp = k_h
        # leg1² + leg2² = hyp²
        # x² + (x+a)² = hyp²  →  2x² + 2ax + a² - hyp² = 0
        A = 2; B = 2*a; C = a**2 - hyp**2
        disc = discriminant(A, B, C)
        if disc <= 0: continue
        k2, m2 = simplify_surd(disc)
        if m2 != 1: continue
        x1 = (-B + k2) // (2*A); x2 = (-B - k2) // (2*A)
        if x1 != x_val and x2 != x_val: continue
        pos = max(x1, x2)
        if pos <= 0: continue
        eq = f"{fmt_quad(A, B, C, 'x')} = 0"
        ans_str, steps, _ = fmt_surd_roots(A, B, C, v="x")
        t_dec = round_dp(pos, 1)
        sol = (f"\\text{{(i) Pythagoras: }} x^2 + (x+{a})^2 = {hyp}^2 \\\\[4pt] "
               f"x^2 + x^2 + {2*a}x + {a**2} = {hyp**2} \\\\[4pt] "
               f"2x^2 + {2*a}x {'+' if (a**2 - hyp**2) >= 0 else '-'} {abs(a**2 - hyp**2)} = 0 \\\\[4pt] "
               f"\\text{{(ii) }} " + steps + f" \\\\[4pt] "
               f"\\text{{(iii) }} x = {pos} \\text{{ cm}}")
        return make_multipart(
            stimulus_text=(f"A right-angled triangle has legs $x$ cm and $(x + {a})$ cm. "
                           f"The hypotenuse is {hyp} cm."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Use Pythagoras' theorem to form a quadratic equation."),
                part("ii",  "Solve the equation exactly."),
                part("iii", "Find the lengths of the two legs."),
            ],
            answer=f"x = {pos} \\text{{ cm, legs: }} {pos} \\text{{ and }} {pos+a} \\text{{ cm}}",
            solution=sol,
        )


# ══════════════════════════════════════════════════════════════════
# LT5 EXTENSION — DISCRIMINANT ANALYSIS
# ══════════════════════════════════════════════════════════════════

def gen_discriminant_nature():
    """Given ax²+bx+c, compute Δ=b²-4ac and state nature of roots."""
    for _ in range(300):
        a = random.choice([1, 1, 1, 2, 3])
        b = ri(-8, 8)
        c = ri(-6, 6)
        if b == 0 and c == 0: continue
        disc = discriminant(a, b, c)
        v = rv()
        eq = f"{fmt_quad(a, b, c, v)} = 0"
        disc_val = b*b - 4*a*c
        if disc_val > 0:
            nature = "\\text{Two distinct real roots}"
            nature_plain = "Two distinct real roots"
        elif disc_val == 0:
            nature = "\\text{One repeated real root}"
            nature_plain = "One repeated real root"
        else:
            nature = "\\text{No real roots}"
            nature_plain = "No real roots"
        four_ac = 4*a*c
        sol = (f"\\Delta = b^2 - 4ac = ({b})^2 - 4({a})({c}) \\\\[4pt] "
               f"\\Delta = {b*b} {'-' if four_ac >= 0 else '+'} {abs(four_ac)} = {disc_val} \\\\[4pt] "
               f"\\Delta {'>' if disc_val > 0 else '=' if disc_val == 0 else '<'} 0 \\Rightarrow {nature}")
        ans = nature_plain
        return make_equation(eq, ans, sol, v)

def gen_discriminant_find_k():
    """Find value of k for given root condition: equal roots, real roots, or no real roots."""
    for _ in range(300):
        # Form: x² + kx + c = 0 or x² + bx + k = 0
        choice = random.choice(["k_in_b", "k_in_c"])
        condition = random.choice(["equal", "real", "no_real"])
        v = rv()
        if choice == "k_in_b":
            # x² + kx + c = 0 → Δ = k² - 4c
            c = random.choice([1, 4, 9, 16, 25, 3, 5, 7])
            if condition == "equal":
                # k² = 4c → k = ±2√c
                sq = int(math.sqrt(4*c))
                if sq*sq != 4*c: continue
                k_vals = [sq, -sq]
                eq = f"{v}^2 + k{v} + {c} = 0"
                cond_text = "equal roots"
                sol = (f"\\text{{For equal roots: }} \\Delta = 0 \\\\[4pt] "
                       f"k^2 - 4({c}) = 0 \\\\[4pt] "
                       f"k^2 = {4*c} \\\\[4pt] "
                       f"k = \\pm {sq}")
                ans = f"k = \\pm {sq}"
            elif condition == "real":
                sq = int(math.sqrt(4*c))
                if sq*sq != 4*c: continue
                eq = f"{v}^2 + k{v} + {c} = 0"
                cond_text = "real roots"
                sol = (f"\\text{{For real roots: }} \\Delta \\geq 0 \\\\[4pt] "
                       f"k^2 - 4({c}) \\geq 0 \\\\[4pt] "
                       f"k^2 \\geq {4*c} \\\\[4pt] "
                       f"k \\leq -{sq} \\text{{ or }} k \\geq {sq}")
                ans = f"k \\leq -{sq} \\text{{ or }} k \\geq {sq}"
            else:  # no_real
                sq = int(math.sqrt(4*c))
                if sq*sq != 4*c: continue
                eq = f"{v}^2 + k{v} + {c} = 0"
                cond_text = "no real roots"
                sol = (f"\\text{{For no real roots: }} \\Delta < 0 \\\\[4pt] "
                       f"k^2 - 4({c}) < 0 \\\\[4pt] "
                       f"k^2 < {4*c} \\\\[4pt] "
                       f"-{sq} < k < {sq}")
                ans = f"-{sq} < k < {sq}"
        else:
            # x² + bx + k = 0 → Δ = b² - 4k
            b = ri(2, 8) * random.choice([-1, 1])
            b2 = b * b
            if condition == "equal":
                k_val = b2 // 4
                if 4 * k_val != b2: continue
                eq = f"{v}^2 + {b}{v} + k = 0" if b > 0 else f"{v}^2 - {abs(b)}{v} + k = 0"
                cond_text = "equal roots"
                sol = (f"\\text{{For equal roots: }} \\Delta = 0 \\\\[4pt] "
                       f"({b})^2 - 4k = 0 \\\\[4pt] "
                       f"{b2} = 4k \\\\[4pt] "
                       f"k = {k_val}")
                ans = f"k = {k_val}"
            elif condition == "real":
                k_val = b2 // 4
                if 4 * k_val != b2: continue
                eq = f"{v}^2 + {b}{v} + k = 0" if b > 0 else f"{v}^2 - {abs(b)}{v} + k = 0"
                cond_text = "real roots"
                sol = (f"\\text{{For real roots: }} \\Delta \\geq 0 \\\\[4pt] "
                       f"({b})^2 - 4k \\geq 0 \\\\[4pt] "
                       f"{b2} \\geq 4k \\\\[4pt] "
                       f"k \\leq {k_val}")
                ans = f"k \\leq {k_val}"
            else:  # no_real
                k_val = b2 // 4
                if 4 * k_val != b2: continue
                eq = f"{v}^2 + {b}{v} + k = 0" if b > 0 else f"{v}^2 - {abs(b)}{v} + k = 0"
                cond_text = "no real roots"
                sol = (f"\\text{{For no real roots: }} \\Delta < 0 \\\\[4pt] "
                       f"({b})^2 - 4k < 0 \\\\[4pt] "
                       f"{b2} < 4k \\\\[4pt] "
                       f"k > {k_val}")
                ans = f"k > {k_val}"

        instruction = f"Find the value(s) of $k$ for which the equation has {cond_text}."
        full_eq = f"{eq}"
        return make_equation(
            f"{full_eq}",
            ans,
            f"\\text{{Given: }} {full_eq} \\\\[4pt] " + sol,
            v,
            is_wide=True,
            override_instruction=instruction
        )


# ══════════════════════════════════════════════════════════════════
# LT9 — FORMING EQUATIONS FROM ROOTS (VIETA'S FORMULAS)
# ══════════════════════════════════════════════════════════════════

def gen_roots_to_equation():
    """Given roots α and β (integers or simple fractions), form x²-(α+β)x+αβ=0."""
    options = [
        (2, 3),    (1, 5),    (3, 4),    (2, 7),    (1, 8),
        (-1, 3),   (-2, 5),   (1, -4),   (-3, 4),   (-1, -2),
        (-2, -3),  (-1, -5),  (2, -7),   (-4, -1),
        (Fraction(1,2), 3), (Fraction(-1,2), 4), (Fraction(3,2), -1),
        (2+math.sqrt(3), 2-math.sqrt(3)),  # surd pair
    ]
    # Filter to integer/fraction pairs only for clean exercises
    int_opts = [(a, b) for a, b in options if isinstance(a, (int, Fraction)) and isinstance(b, (int, Fraction))]
    alpha, beta = random.choice(int_opts)
    s = alpha + beta      # sum
    p = alpha * beta      # product
    v = rv()
    s_str = frac(s); p_str = frac(p)
    if isinstance(s, Fraction):
        # Multiply through to get integer coefficients
        denom = s.denominator
        B_f = int(-s * denom); C_f = int(p * denom)
        _Bf_s = '' if B_f==1 else '-' if B_f==-1 else str(B_f)
        eq = f"{denom}{v}^2 {'+' if B_f>0 else ''}{_Bf_s}{v} {'+' if C_f>=0 else ''}{C_f} = 0"
    else:
        # Standard form
        b_coeff = -int(s)
        c_coeff = int(p)
        eq = fmt_quad(1, b_coeff, c_coeff, v) + " = 0"
    alpha_s = frac(alpha); beta_s = frac(beta)
    sol = (f"\\text{{Sum of roots: }} \\alpha + \\beta = {alpha_s} + ({beta_s}) = {s_str} \\\\[4pt] "
           f"\\text{{Product of roots: }} \\alpha\\beta = ({alpha_s}) \\times ({beta_s}) = {p_str} \\\\[4pt] "
           f"\\text{{Equation: }} {v}^2 - (\\alpha+\\beta){v} + \\alpha\\beta = 0 \\\\[4pt] "
           f"{eq}")
    return make_equation(
        f"\\alpha = {alpha_s},\\; \\beta = {beta_s}",
        eq, sol, v, is_wide=True,
        override_instruction=f"Form a quadratic equation with roots $\\alpha$ and $\\beta$. Give your answer in the form ${v}^2 + p{v} + q = 0$."
    )


def gen_roots_symmetric():
    """Given ax²+bx+c=0 with roots α,β, find expressions like α²+β², α³+β³, 1/α+1/β."""
    cases = [
        # (a, b, c, expression_latex, solution_latex, answer_latex)
        lambda a,b,c,S,P: (
            "\\alpha^2 + \\beta^2",
            f"(\\alpha+\\beta)^2 - 2\\alpha\\beta = ({frac(S)})^2 - 2({frac(P)}) = {frac(S*S - 2*P)}",
            frac(S*S - 2*P)
        ),
        lambda a,b,c,S,P: (
            "\\dfrac{1}{\\alpha} + \\dfrac{1}{\\beta}",
            f"\\dfrac{{\\alpha+\\beta}}{{\\alpha\\beta}} = \\dfrac{{{frac(S)}}}{{{frac(P)}}} = {frac(Fraction(S)/P if P != 0 else 0)}",
            frac(Fraction(S)/P) if P != 0 else "undefined"
        ) if P != 0 else None,
        lambda a,b,c,S,P: (
            "(\\alpha - \\beta)^2",
            f"(\\alpha+\\beta)^2 - 4\\alpha\\beta = ({frac(S)})^2 - 4({frac(P)}) = {frac(S*S - 4*P)}",
            frac(S*S - 4*P)
        ),
        lambda a,b,c,S,P: (
            "\\alpha^2\\beta + \\alpha\\beta^2",
            f"\\alpha\\beta(\\alpha+\\beta) = ({frac(P)})({frac(S)}) = {frac(P*S)}",
            frac(P*S)
        ),
    ]
    for _ in range(300):
        a = random.choice([1, 1, 2])
        b = ri(-6, 6)
        c = ri(-6, 6)
        if b == 0 or c == 0: continue
        disc = discriminant(a, b, c)
        if disc < 0: continue
        S = Fraction(-b, a)   # sum = -b/a
        P = Fraction(c, a)    # product = c/a
        v = rv()
        eq_str = f"{fmt_quad(a, b, c, v)} = 0"
        # Pick a valid expression
        valid = [f for f in cases if f is not None]
        random.shuffle(valid)
        for fn in valid:
            result = fn(a, b, c, S, P)
            if result is None: continue
            expr, sol_steps, ans = result
            if ans == "undefined": continue
            # Check answer is a clean fraction
            full_sol = (f"\\text{{From }} {eq_str}: \\\\[4pt] "
                       f"\\alpha + \\beta = \\dfrac{{-b}}{{a}} = \\dfrac{{{-b}}}{{{a}}} = {frac(S)} \\\\[4pt] "
                       f"\\alpha\\beta = \\dfrac{{c}}{{a}} = \\dfrac{{{c}}}{{{a}}} = {frac(P)} \\\\[4pt] "
                       f"{expr} = {sol_steps}")
            return make_equation(
                eq_str, str(ans), full_sol, v, is_wide=True,
                override_instruction=f"The equations below have roots $\\alpha$ and $\\beta$. Use Vieta's formulas to find the given expression."
            )



# ══════════════════════════════════════════════════════════════════
# LT7 EXTENSION — WORD PROBLEMS (more integer types)
# ══════════════════════════════════════════════════════════════════

def gen_word_even_integers():
    """Product of two consecutive even integers = k."""
    for _ in range(300):
        n = ri(1, 12) * 2   # even integer n
        prod = n * (n + 2)
        # n² + 2n - prod = 0
        disc = 1 + prod     # disc of n²+2n-prod: 4+4prod → simplified: 1+prod after /4
        # Actually disc = (2)²+4*prod = 4+4prod
        full_disc = 4 + 4*prod
        k, m = simplify_surd(full_disc)
        if m != 1: continue
        # n = (-2 ± k) / 2
        n1 = (-2 + k) // 2; n2 = (-2 - k) // 2
        if 2*n1 != -2 + k: continue
        pos = max(n1, n2)
        if pos <= 0 or pos % 2 != 0: continue
        ans_str, steps, _ = fmt_surd_roots(1, 2, -prod, v="n")
        sol = (f"\\text{{(i) }} n(n+2) = {prod} \\\\[4pt] "
               f"n^2 + 2n - {prod} = 0 \\\\[4pt] "
               f"\\text{{(ii) }} " + steps + f" \\\\[4pt] "
               f"\\text{{Since integers are positive even, }} n = {pos} \\\\[4pt] "
               f"\\text{{Integers: }} {pos} \\text{{ and }} {pos+2}")
        return make_multipart(
            stimulus_text=(f"The product of two consecutive positive even integers is {prod}."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Form a quadratic equation in $n$."),
                part("ii",  "Solve the equation exactly."),
                part("iii", "Find the two integers."),
            ],
            answer=f"Integers: {pos} and {pos+2}",
            solution=sol,
        )

def gen_word_odd_integers():
    """More complex: product of larger and twice the smaller = k (consecutive odd)."""
    for _ in range(300):
        n = ri(1, 10) * 2 - 1   # odd integer n (the smaller)
        # larger = n+2, relationship: (n+2) * 2n = k  OR  n*(n+2) with twist
        # Vary the relationship
        choice = random.choice(["product", "larger_twice_smaller"])
        if choice == "product":
            prod = n * (n + 2)
            # n² + 2n - prod = 0
            disc_full = 4 + 4*prod
            k, m = simplify_surd(disc_full)
            if m != 1: continue
            n1 = (-2 + k)//2; n2 = (-2 - k)//2
            if 2*n1 != -2+k: continue
            pos = max(n1, n2)
            if pos <= 0 or pos % 2 != 1: continue
            ans_str, steps, _ = fmt_surd_roots(1, 2, -prod, v="n")
            stmt = f"The product of two consecutive positive odd integers is {prod}."
            sol = (f"\\\\text{{(i) }} n(n+2) = {prod} \\\\\\\\[4pt] "
                   f"n^2 + 2n - {prod} = 0 \\\\\\\\[4pt] "
                   f"\\\\text{{(ii) }} " + steps + f" \\\\\\\\[4pt] "
                   f"\\\\text{{Since integers are positive odd, }} n = {pos} \\\\\\\\[4pt] "
                   f"\\\\text{{Integers: }} {pos} \\\\text{{ and }} {pos+2}")
            ans = f"Integers: {pos} and {pos+2}"
        else:
            # larger × 2×smaller = k  →  (n+2)(2n) = k  →  2n²+4n-k=0
            k_val = (n + 2) * (2 * n)
            # 2n² + 4n - k_val = 0
            disc_full = 16 + 8*k_val
            ks, ms = simplify_surd(disc_full)
            if ms != 1: continue
            n1 = (-4 + ks)//4; n2 = (-4 - ks)//4
            if 4*n1 != -4+ks: continue
            pos = max(n1, n2)
            if pos <= 0 or pos % 2 != 1: continue
            ans_str, steps, _ = fmt_surd_roots(2, 4, -k_val, v="n")
            stmt = (f"Two consecutive positive odd integers: the product of the larger "
                    f"and twice the smaller is {k_val}.")
            sol = (f"\\\\text{{(i) }} (n+2)(2n) = {k_val} \\\\\\\\[4pt] "
                   f"2n^2 + 4n - {k_val} = 0 \\\\\\\\[4pt] "
                   f"\\\\text{{(ii) }} " + steps + f" \\\\\\\\[4pt] "
                   f"\\\\text{{Since integers are positive odd, }} n = {pos} \\\\\\\\[4pt] "
                   f"\\\\text{{Integers: }} {pos} \\\\text{{ and }} {pos+2}")
            ans = f"Integers: {pos} and {pos+2}"
        return make_multipart(
            stimulus_text=stmt,
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("i",   "Form a quadratic equation in $n$."),
                part("ii",  "Solve the equation exactly."),
                part("iii", "Find the two integers."),
            ],
            answer=ans,
            solution=sol,
        )


# ══════════════════════════════════════════════════════════════════
# LT8 EXTENSION — GEOMETRY (more shape types)
# ══════════════════════════════════════════════════════════════════

def _right_triangle_svg(leg1_expr, leg2_expr, hyp_expr):
    """Generate SVG of a right-angled triangle with labels positioned outside edges."""
    return (
        '<svg viewBox="-10 0 260 180" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:260px;margin:8px auto;display:block">'
        '<polygon points="40,150 40,20 180,150" '
        '  fill="#e8f4fd" stroke="#2c7bb6" stroke-width="2"/>'
        '<rect x="40" y="134" width="16" height="16" '
        '  fill="none" stroke="#2c7bb6" stroke-width="1.5"/>'
        # leg1 (vertical) — label to the LEFT of the vertical side
        f'<text x="30" y="92" font-size="13" fill="#2c7bb6" '
        f'  font-family="serif" font-style="italic" text-anchor="end">{leg1_expr}</text>'
        # leg2 (horizontal) — label BELOW the horizontal side
        f'<text x="110" y="172" font-size="13" fill="#2c7bb6" '
        f'  font-family="serif" font-style="italic" text-anchor="middle">{leg2_expr}</text>'
        # hypotenuse — label to the upper-right, outside
        f'<text x="128" y="72" font-size="13" fill="#2c7bb6" '
        f'  font-family="serif" font-style="italic" text-anchor="start">{hyp_expr}</text>'
        '</svg>'
    )

def gen_geo_right_triangle_area():
    """Right triangle with 3 algebraic sides: show equation, solve, find area."""
    # Pattern: legs (ax+b) and (cx+d), hypotenuse (ex+f)
    # Use Pythagorean triples scaled by x to guarantee integer solutions
    triples = [
        # (leg1_coef, leg1_const, leg2_coef, leg2_const, hyp_coef, hyp_const, x_val)
        (1, 5, 1, -2, 2, -1, 7),   # x+5, x-2, 2x-1
        (2, 10, 1, 3, 2, -2, 6),   # 2x+10, x+3, 4x-2  (Image 2 style)
        (1, 4, 1, -3, 2, 0, 5),    # x+4, x-3, 2x
        (1, 3, 1, -1, 1, 4, 8),    # x+3, x-1, x+4
        (2, 1, 1, -2, 2, -3, 5),   # 2x+1, x-2, 2x-3
    ]
    for _ in range(200):
        a1,b1, a2,b2, ah,bh, xv = random.choice(triples)
        leg1 = a1*xv + b1; leg2 = a2*xv + b2; hyp = ah*xv + bh
        if leg1 <= 0 or leg2 <= 0 or hyp <= 0: continue
        if abs(leg1**2 + leg2**2 - hyp**2) > 0.01: continue
        # Expand: (a1x+b1)² + (a2x+b2)² = (ah x+bh)²
        # A = a1²+a2²-ah², B = 2(a1b1+a2b2-ah*bh), C = b1²+b2²-bh²
        A = a1**2 + a2**2 - ah**2
        B = 2*(a1*b1 + a2*b2 - ah*bh)
        C = b1**2 + b2**2 - bh**2
        if A == 0: continue
        disc = B**2 - 4*A*C
        if disc < 0: continue
        ks, ms = simplify_surd(disc)
        if ms != 1: continue
        x1 = (-B + ks)//(2*A); x2 = (-B - ks)//(2*A)
        if 2*A*x1 != -B+ks: continue
        # Pick positive root
        pos = x1 if x1 > 0 else x2
        if pos <= 0: continue
        l1 = a1*pos+b1; l2 = a2*pos+b2; h = ah*pos+bh
        if l1 <= 0 or l2 <= 0 or h <= 0: continue
        area = Fraction(l1 * l2, 2)
        # Format side labels
        def side(a, b):
            if b > 0: return f"{a if a!=1 else ''}x + {b}" if a else str(b)
            if b < 0: return f"{a if a!=1 else ''}x - {abs(b)}" if a else str(b)
            return f"{a if a!=1 else ''}x"
        l1_str = side(a1, b1); l2_str = side(a2, b2); h_str = side(ah, bh)
        if A < 0: A, B, C = -A, -B, -C
        import math as _gm
        _g = _gm.gcd(_gm.gcd(abs(A),abs(B)),abs(C))
        An,Bn,Cn = A//_g, B//_g, C//_g
        eq_str = fmt_quad(An, Bn, Cn, 'x') + ' = 0'
        ans_str, steps, _ = fmt_surd_roots(An, Bn, Cn, v="x")
        neg = x2 if pos == x1 else x1

        sol = (f"\\text{{(a) Pythagoras: }} ({l1_str})^2 + ({l2_str})^2 = ({h_str})^2 \\\\[4pt] "
               f"{'' if An==1 else An}x^2 {'+' if Bn>=0 else ''}{Bn}x {'+' if Cn>=0 else ''}{Cn} = 0 \\\\[4pt] "
               f"{eq_str} \\\\[4pt] "
               f"\\text{{(b) }} " + steps + f" \\\\[4pt] "
               f"\\text{{Taking positive root: }} x = {pos} \\\\[4pt] "
               f"\\text{{(c) Legs: }} {l1} \\text{{ cm and }} {l2} \\text{{ cm}} \\\\[4pt] "
               f"\\text{{Area }} = \\tfrac{{1}}{{2}} \\times {l1} \\times {l2} = {frac(area)} \\text{{ cm}}^2")
        svg = _right_triangle_svg(l1_str, l2_str, h_str)
        return make_multipart(
            stimulus_text="Shown is a right-angled triangle. All sides are in cm.",
            stimulus_points=[],
            stimulus_svg=svg,
            parts=[
                part("a", f"Show that ${eq_str}$."),
                part("b", "Find $x$."),
                part("c", "Find the area of the triangle."),
            ],
            answer=f"x = {pos},\\; \\text{{Area}} = {frac(area)} \\text{{ cm}}^2",
            solution=sol,
        )


def gen_geo_L_shape():
    """L-shaped region: total area = k → quadratic."""
    for _ in range(300):
        # L-shape = big rectangle - small cutout
        # Big: (3x-a) × (x+b), Cutout: c × d (constant)
        a = ri(1, 5); b = ri(2, 7); c = ri(1, 4); d = ri(1, 4)
        x_val = ri(3, 9)
        big = (3*x_val - a) * (x_val + b)
        cutout = c * d
        total = big - cutout
        if total <= 20: continue
        # Expand: 3x²+(3b-a)x-ab - cutout = total
        # 3x²+(3b-a)x-(ab+cutout+total) -- no, set = total:
        # 3x²+(3b-a)x-ab = total + cutout  BUT cutout is already removed
        # Area = (3x-a)(x+b) - c*d = total
        # 3x²+(3b-a)x-ab - c*d - total = 0
        A = 3; B_c = 3*b - a; C_c = -(a*b) - c*d - total
        disc = B_c**2 - 4*A*C_c
        if disc < 0: continue
        ks, ms = simplify_surd(disc)
        if ms != 1: continue
        x1 = (-B_c + ks)//(2*A); x2 = (-B_c - ks)//(2*A)
        if 2*A*x1 != -B_c+ks: continue
        pos = x1 if x1 == x_val else x2
        if pos != x_val: continue
        # Simplify equation by GCD
        from math import gcd
        g = gcd(gcd(abs(A), abs(B_c)), abs(C_c))
        Ar, Br, Cr = A//g, B_c//g, C_c//g
        eq_str = fmt_quad(Ar, Br, Cr, 'x') + " = 0"
        ans_str, steps, _ = fmt_surd_roots(Ar, Br, Cr, v="x")
        neg = x1 if pos == x2 else x2
        sol = (f"\\text{{(a) Area: }} (3x-{a})(x+{b}) - {c*d} = {total} \\\\[4pt] "
               f"3x^2 {'+' if B_c>0 else ''}{''  if B_c==1 else '-' if B_c==-1 else B_c}x - {a*b} - {c*d} = {total} \\\\[4pt] "
               f"3x^2 {'+' if B_c>0 else ''}{''  if B_c==1 else '-' if B_c==-1 else B_c}x - {a*b + c*d + total} = 0 \\\\[4pt] "
               f"{eq_str} \\\\[4pt] "
               f"\\text{{(b) }} " + steps + f" \\\\[4pt] "
               f"\\text{{Taking positive root: }} x = {pos}")
        # L-shape SVG with clear separate dimension labels
        l_svg = (
            '<svg viewBox="0 0 310 215" xmlns="http://www.w3.org/2000/svg" '
            'style="max-width:300px;margin:8px auto;display:block">'
            '<polygon points="20,185 20,90 120,90 120,20 240,20 240,185" '
            '  fill="#e8f5e9" stroke="#2e7d32" stroke-width="2"/>'
            '<rect x="120" y="20" width="120" height="70" fill="none" '
            '  stroke="#999" stroke-width="1.5" stroke-dasharray="5,4"/>'
            f'<text x="2" y="142" font-size="12" fill="#2e7d32" font-family="serif" font-style="italic">x+{b}</text>'
            f'<text x="130" y="202" font-size="12" fill="#2e7d32" font-family="serif" font-style="italic" text-anchor="middle">3x\u2212{a}</text>'
            f'<text x="180" y="12" font-size="11" fill="#777" font-family="serif" font-style="italic" text-anchor="middle">{c}</text>'
            f'<text x="246" y="60" font-size="11" fill="#777" font-family="serif" font-style="italic">{d}</text>'
            '</svg>'
        )
        return make_multipart(
            stimulus_text=(f"The area of the L-shaped region is {total} cm². "
                           f"The big rectangle is $(3x-{a})$ cm by $(x+{b})$ cm "
                           f"with a ${c}$ cm $\\times$ ${d}$ cm rectangle removed."),
            stimulus_points=[],
            stimulus_svg=l_svg,
            parts=[
                part("a", f"Show that ${eq_str}$."),
                part("b", "Solve to find $x$."),
            ],
            answer=f"x = {pos}",
            solution=sol,
        )


def gen_geo_cuboid_surface():
    """Cuboid x by x by (x+a): surface area = k → quadratic → find volume."""
    for _ in range(300):
        a = ri(2, 8)
        x_val = ri(3, 10)
        # Cuboid: x × x × (x+a)
        # SA = 2x² + 2x(x+a) + 2x(x+a) = 2x² + 4x(x+a)
        # = 2x² + 4x²+4ax = 6x²+4ax
        # Actually: SA = 2(lb+lh+bh) = 2(x²+x(x+a)+x(x+a)) = 2x²+4x(x+a)
        sa = 2*x_val**2 + 4*x_val*(x_val+a)
        # 6x²+4ax - sa = 0  →  divide if possible
        A = 6; B_s = 4*a; C_s = -sa
        from math import gcd
        g = gcd(gcd(abs(A), abs(B_s)), abs(C_s))
        Ar, Br, Cr = A//g, B_s//g, C_s//g
        disc = Br**2 - 4*Ar*Cr
        if disc < 0: continue
        ks, ms = simplify_surd(disc)
        if ms != 1: continue
        x1 = (-Br + ks)//(2*Ar); x2 = (-Br - ks)//(2*Ar)
        if 2*Ar*x1 != -Br+ks: continue
        pos = x1 if x1 > 0 else x2
        if pos != x_val: continue
        vol = x_val**2 * (x_val + a)
        eq_str = fmt_quad(Ar, Br, Cr, 'x') + " = 0"
        ans_str, steps, _ = fmt_surd_roots(Ar, Br, Cr, v="x")
        sol = (f"\\text{{(a) Surface area: }} 2x^2 + 4x(x+{a}) = {sa} \\\\[4pt] "
               f"6x^2 + {4*a}x - {sa} = 0 \\\\[4pt] "
               f"{eq_str} \\\\[4pt] "
               f"\\text{{(b) }} " + steps + f" \\\\[4pt] "
               f"x = {pos} \\text{{ cm}} \\\\[4pt] "
               f"\\text{{(c) Volume }} = {pos}^2 \\cdot ({pos+a}) = {vol} \\text{{ cm}}^3")
        return make_multipart(
            stimulus_text=(f"A cuboid has dimensions $x$ cm, $x$ cm and $(x+{a})$ cm. "
                           f"Its surface area is {sa} cm²."),
            stimulus_points=[],
            stimulus_svg=None,
            parts=[
                part("a", f"Show that ${eq_str}$."),
                part("b", "Find $x$."),
                part("c", "Find the volume of the cuboid."),
            ],
            answer=f"x = {pos},\\; V = {vol} \\text{{ cm}}^3",
            solution=sol,
        )


def gen_geo_cuboid_volume():
    """Cuboid x by (2x-a) by b: volume = k → quadratic."""
    for _ in range(300):
        a = ri(5, 15) * 2  # even for cleaner algebra
        b = random.choice([8, 10, 12, 15, 20])
        x_val = ri(max(3, a//2+1), 18)
        if 2*x_val - a <= 0: continue
        vol = x_val * (2*x_val - a) * b
        # b·x·(2x-a) = vol  →  2bx² - abx - vol = 0  →  divide by b:
        # 2x² - ax - vol/b = 0  if vol divisible by b
        if vol % b != 0: continue
        k_vol = vol // b
        # 2x² - ax - k_vol = 0
        A = 2; B_v = -a; C_v = -k_vol
        disc = B_v**2 - 4*A*C_v
        ks, ms = simplify_surd(disc)
        if ms != 1: continue
        x1 = (-B_v + ks)//(2*A); x2 = (-B_v - ks)//(2*A)
        if 2*A*x1 != -B_v+ks: continue
        pos = x1 if x1 > 0 else x2
        if pos != x_val: continue
        eq_str = fmt_quad(A, B_v, C_v, 'x') + " = 0"
        ans_str, steps, _ = fmt_surd_roots(A, B_v, C_v, v="x")
        sol = (f"\\text{{(a) Volume: }} {b} \\times x \\times (2x-{a}) = {vol} \\\\[4pt] "
               f"{b}x(2x-{a}) = {vol} \\\\[4pt] "
               f"2x^2 - {a}x - {k_vol} = 0 \\\\[4pt] "
               f"{eq_str} \\\\[4pt] "
               f"\\text{{(b) }} " + steps + f" \\\\[4pt] "
               f"\\text{{Taking positive root: }} x = {pos} \\text{{ cm}}")
        cub_svg = (
            '<svg viewBox="-30 0 310 195" xmlns="http://www.w3.org/2000/svg" '
            'style="max-width:300px;margin:8px auto;display:block">'
            '<polygon points="50,55 50,165 190,165 190,55" fill="#dbeafe" stroke="#1d4ed8" stroke-width="2"/>'
            '<polygon points="50,55 90,25 230,25 190,55" fill="#bfdbfe" stroke="#1d4ed8" stroke-width="2"/>'
            '<polygon points="190,55 230,25 230,135 190,165" fill="#93c5fd" stroke="#1d4ed8" stroke-width="2"/>'
            f'<text x="120" y="183" font-size="12" fill="#1d4ed8" font-family="serif" font-style="italic" text-anchor="middle">x</text>'
            f'<text x="42" y="115" font-size="12" fill="#1d4ed8" font-family="serif" font-style="italic" text-anchor="end">2x\u2212{a}</text>'
            f'<text x="234" y="88" font-size="12" fill="#1d4ed8" font-family="serif" font-style="italic">{b}</text>'
            '</svg>'
        )
        return make_multipart(
            stimulus_text=(f"A cuboid has dimensions $x$ cm, $(2x - {a})$ cm and ${b}$ cm. "
                           f"Its volume is {vol} cm³."),
            stimulus_points=[],
            stimulus_svg=cub_svg,
            parts=[
                part("a", f"Show that ${eq_str}$."),
                part("b", "Find $x$."),
            ],
            answer=f"x = {pos}",
            solution=sol,
        )

# ══════════════════════════════════════════════════════════════════
# LT10 — ALGEBRAIC FRACTION EQUATIONS
# ══════════════════════════════════════════════════════════════════

def gen_frac_equation_simple():
    """a/x + b/(x+c) = k  →  multiply through, collect, solve quadratic."""
    for _ in range(500):
        a = ri(1, 6)
        c = ri(1, 6) * random.choice([-1, 1])
        if c == 0: continue
        k = ri(1, 4)
        # a/(x) + b/(x+c) = k
        # a(x+c) + bx = kx(x+c)
        # Choose b so roots are integers: pick roots r1, r2
        r1 = ri(1, 8)
        r2 = ri(-8, -1)
        if r1 == 0 or r2 == 0 or r1 + r2 == 0: continue
        # kx² + (kc - a - b)x - ac = 0
        # roots are r1, r2 → k(x-r1)(x-r2) = kx² - k(r1+r2)x + k*r1*r2
        # So: kc - a - b = -k(r1+r2)  →  b = kc - a + k(r1+r2)
        #     -ac = k*r1*r2            →  a*c = -k*r1*r2
        # Let's choose a,c,k,r1,r2 so ac = -k*r1*r2
        k2 = ri(1, 3)
        r1 = ri(1, 6); r2 = ri(1, 6)
        if r1 == r2: continue
        # ac = -k2*r1*r2  → pick a=r1, c=-r2, k2
        a2 = r1; c2 = -r2
        b2 = k2*c2 - a2 + k2*(r1+r2)   # = k2*(-r2) - r1 + k2*(r1+r2) = k2*r1 - r1 = r1(k2-1)
        # Simplify: b2 = r1*(k2-1) — could be 0 if k2=1
        if b2 == 0 or a2 == 0: continue
        # Equation: a2/x + b2/(x+c2) = k2
        # Solution: multiply by x(x+c2):
        # a2(x+c2) + b2*x = k2*x(x+c2)
        # a2*x + a2*c2 + b2*x = k2*x² + k2*c2*x
        # (a2+b2)*x + a2*c2 = k2*x² + k2*c2*x
        # k2*x² + (k2*c2 - a2 - b2)*x - a2*c2 = 0
        A = k2; B = k2*c2 - a2 - b2; C = -a2*c2
        disc_val = B*B - 4*A*C
        if disc_val < 0: continue
        import math as _math
        sq = int(_math.sqrt(disc_val))
        if sq*sq != disc_val: continue
        root1 = (-B + sq) // (2*A)
        root2 = (-B - sq) // (2*A)
        if (2*A*root1 != -B + sq) or (2*A*root2 != -B - sq): continue
        if root1 == 0 or root2 == 0: continue   # x=0 excluded (denominator)
        if root1 == -c2 or root2 == -c2: continue  # x=-c excluded

        v = "x"
        # Format equation
        b2_str = f"{b2}" if b2 > 0 else f"({b2})"
        c2_str = f"x + {c2}" if c2 > 0 else f"x - {abs(c2)}"
        denom_str = f"x - {abs(c2)}" if c2 < 0 else f"x + {c2}"
        eq = (f"\\dfrac{{{a2}}}{{{v}}} + \\dfrac{{{b2}}}{{{denom_str}}} = {k2}"
              if b2 > 0 else
              f"\\dfrac{{{a2}}}{{{v}}} - \\dfrac{{{abs(b2)}}}{{{denom_str}}} = {k2}")
        ans = f"{v} = {root1} \\text{{ or }} {v} = {root2}"
        sol = (f"\\text{{Multiply through by }} {v}({denom_str}): \\\\[4pt] "
               f"{a2}({denom_str}) {'+'if b2>0 else '-'} {abs(b2)}{v} = {k2}{v}({denom_str}) \\\\[4pt] "
               f"{fmt_quad(A, B, C, v)} = 0 \\\\[4pt] "
               f"({v} - {root1})({v} - {root2}) = 0 \\\\[4pt] "
               f"{ans}")
        return make_equation(eq, ans, sol, v, is_wide=True)
    return None


def gen_frac_equation_diff():
    """a/(x+b) - c/(x+d) = k  →  cross-multiply, solve quadratic."""
    for _ in range(500):
        b = ri(1, 5)
        d = ri(-5, -1)
        if b == d or d == 0: continue
        k = random.choice([1, 2, -1, -2])
        # a/(x+b) - c/(x+d) = k
        # pick integer roots r1, r2 (not -b or -d)
        r1 = ri(-4, 8); r2 = ri(-4, 8)
        if r1 == r2 or r1 == -b or r1 == -d or r2 == -b or r2 == -d: continue
        # k(x+b)(x+d) - a(x+d) + c(x+b) = 0
        # k·x² + k(b+d)x + k·b·d  - a·x - a·d + c·x + c·b = 0
        # k·x² + [k(b+d) - a + c]x + [kbd - ad + cb] = 0
        # roots r1, r2: k(x-r1)(x-r2) = kx² - k(r1+r2)x + k·r1·r2
        # So: -k(r1+r2) = k(b+d) - a + c  and  k·r1·r2 = kbd - ad + cb
        # From 2nd: a·d - c·b = kbd - k·r1·r2 = k(bd - r1·r2)
        # From 1st: a - c = k(b+d) + k(r1+r2) = k(b+d+r1+r2)
        # Let a - c = k*(b+d+r1+r2) and a*d - c*b = k*(b*d - r1*r2)
        # Solve for a,c:
        S = k * (b + d + r1 + r2)      # a - c
        P = k * (b*d - r1*r2)          # ad - cb
        # a - c = S, ad - cb = P
        # a·d - c·b = P → (c+S)d - cb = P → c(d-b) = P - Sd → c = (P-Sd)/(d-b)
        if (d - b) == 0: continue
        c_frac = Fraction(P - S*d, d - b)
        if c_frac.denominator != 1: continue
        c_val = int(c_frac)
        a_val = c_val + S
        if a_val == 0 or c_val == 0: continue
        if abs(a_val) > 10 or abs(c_val) > 10: continue

        v = "x"
        b_str = f"x + {b}"
        d_str = f"x + {d}" if d > 0 else f"x - {abs(d)}"
        a_str = str(a_val)
        c_str = str(abs(c_val))
        op = "-" if c_val > 0 else "+"
        eq = (f"\\dfrac{{{a_str}}}{{{b_str}}} {op} \\dfrac{{{c_str}}}{{{d_str}}} = {k}")
        A = k; B = k*(b+d) - a_val + c_val; C = k*b*d - a_val*d + c_val*b
        ans = f"{v} = {r1} \\text{{ or }} {v} = {r2}"
        # Solution steps
        sol = (f"\\text{{Multiply by }} ({b_str})({d_str}): \\\\[4pt] "
               f"{a_val}({d_str}) {op} {abs(c_val)}({b_str}) = {k}({b_str})({d_str}) \\\\[4pt] "
               f"{fmt_quad(A, B, C, v)} = 0 \\\\[4pt] "
               f"({v} {'-' if r1>=0 else '+ '}{abs(r1)})({v} {'-' if r2>=0 else '+ '}{abs(r2)}) = 0 \\\\[4pt] "
               f"{ans}")
        return make_equation(eq, ans, sol, v, is_wide=True)
    return None


# ══════════════════════════════════════════════════════════════════
# LT11 — DISGUISED QUADRATICS
# ══════════════════════════════════════════════════════════════════

def gen_disguised_biquadratic():
    """x⁴ + bx² + c = 0  — substitute u = x²."""
    for _ in range(300):
        # Choose integer roots for u: u = p, u = q (both positive for real x roots)
        p = ri(1, 9); q = ri(1, 9)
        if p == q: continue
        b = -(p + q); c = p * q
        # x⁴ + bx² + c = 0  →  (x²-p)(x²-q)=0  →  x=±√p, ±√q
        # For clean answers use perfect squares
        sp = int(p**0.5); sq_q = int(q**0.5)
        if sp*sp == p and sq_q*sq_q == q:
            ans_parts = [f"x = \\pm {sp}", f"x = \\pm {sq_q}"]
            ans = f"x = \\pm {sp} \\text{{ or }} x = \\pm {sq_q}"
            root_str = (f"x^2 = {p} \\Rightarrow x = \\pm {sp} \\\\[4pt] "
                       f"x^2 = {q} \\Rightarrow x = \\pm {sq_q}")
        else:
            def _sr(n):
                s = int(n**0.5)
                return str(s) if s*s==n else f"\\sqrt{{{n}}}"
            ans = f"x = \\pm{_sr(p)} \\text{{ or }} x = \\pm{_sr(q)}"
            root_str = (f"x^2 = {p} \\Rightarrow x = \\pm{_sr(p)} \\\\[4pt] "
                       f"x^2 = {q} \\Rightarrow x = \\pm{_sr(q)}")
        b_str = f"{b}" if b < 0 else f"+ {b}"
        c_str = f"+ {c}" if c > 0 else f"- {abs(c)}"
        eq = f"x^4 {b_str}x^2 {c_str} = 0"
        sol = (f"\\text{{Let }} u = x^2: \\quad u^2 {b_str}u {c_str} = 0 \\\\[4pt] "
               f"(u {'-' if p>=0 else '+ '}{abs(p)})(u {'-' if q>=0 else '+ '}{abs(q)}) = 0 \\\\[4pt] "
               f"u = {p} \\text{{ or }} u = {q} \\\\[4pt] "
               f"{root_str}")
        return make_equation(eq, ans, sol, "x", is_wide=True)


def gen_disguised_linear_sub():
    """(x+a)² + b(x+a) + c = 0  — substitute u = x+a."""
    for _ in range(300):
        a = ri(1, 5) * random.choice([-1, 1])
        # Choose u-roots p, q
        p = ri(-6, 6); q = ri(-6, 6)
        if p == 0 or q == 0 or p == q: continue
        b_coeff = -(p + q)   # coefficient of u
        c_coeff = p * q      # constant
        # x-roots: u=p → x=p-a; u=q → x=q-a
        x1 = p - a; x2 = q - a
        # Format (x+a) nicely
        inner = f"(x + {a})" if a > 0 else f"(x - {abs(a)})"
        b_str = f"+ {b_coeff}" if b_coeff > 0 else f"- {abs(b_coeff)}" if b_coeff < 0 else ""
        c_str = f"+ {c_coeff}" if c_coeff > 0 else f"- {abs(c_coeff)}" if c_coeff < 0 else ""
        eq = f"{inner}^2 {b_str}{inner} {c_str} = 0"
        u_inner = f"x + {a}" if a > 0 else f"x - {abs(a)}"
        ans = f"x = {x1} \\text{{ or }} x = {x2}"
        sol = (f"\\text{{Let }} u = {inner}: \\quad u^2 {b_str}u {c_str} = 0 \\\\[4pt] "
               f"(u {'-' if p>=0 else '+ '}{abs(p)})(u {'-' if q>=0 else '+ '}{abs(q)}) = 0 \\\\[4pt] "
               f"u = {p} \\Rightarrow {u_inner} = {p} \\Rightarrow x = {x1} \\\\[4pt] "
               f"u = {q} \\Rightarrow {u_inner} = {q} \\Rightarrow x = {x2}")
        return make_equation(eq, ans, sol, "x", is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT12 — SURD EQUATIONS
# ══════════════════════════════════════════════════════════════════

def gen_surd_simple():
    """√(x+a) = x + b  — square both sides, check extraneous roots."""
    for _ in range(300):
        # Choose a valid root x=r, then derive a and b
        r = ri(0, 8)
        b = ri(-3, 3)
        # √(r+a) = r+b  →  r+a = (r+b)²  →  a = (r+b)² - r
        a = (r + b)**2 - r
        if a < 0: continue            # need x+a ≥ 0
        if r + b < 0: continue        # RHS must be ≥ 0 at root
        # Check no extraneous root causes issues
        # Squaring gives x² + (2b-1)x + (b²-a) = 0
        B = 2*b - 1; C = b**2 - a
        disc_val = B*B - 4*C
        if disc_val < 0: continue
        sq = int(disc_val**0.5)
        if sq*sq != disc_val: continue
        r1 = (-B + sq) // 2; r2 = (-B - sq) // 2
        if 2*r1 != -B + sq or 2*r2 != -B - sq: continue
        # Find which roots are valid (LHS must equal RHS)
        valid = []
        for rx in [r1, r2]:
            lhs_sq = rx + a
            rhs = rx + b
            if lhs_sq >= 0 and rhs >= 0 and abs(lhs_sq - rhs**2) < 1e-9:
                valid.append(rx)
        if not valid: continue
        if len(valid) == 2 and r1 == r2: continue

        a_str = f"x + {a}" if a > 0 else f"x - {abs(a)}" if a < 0 else "x"
        b_str = f"x + {b}" if b > 0 else f"x - {abs(b)}" if b < 0 else "x"
        eq = f"\\sqrt{{{a_str}}} = {b_str}"
        if len(valid) == 1:
            ans = f"x = {valid[0]}"
            extraneous = r1 if valid[0] == r2 else r2
            ea = extraneous + a
            ea_str = str(int(ea**0.5)) if int(ea**0.5)**2==ea else f"\\sqrt{{{ea}}}"
            # Show √(ea) simplified (avoid √1)
            ea_disp = ea_str if int(ea**0.5)**2==ea else f"\\sqrt{{{ea}}}"
            check_note = (f"\\text{{Check }} x={extraneous}: "
                         f"{ea_disp} = {ea_str} \\neq {extraneous+b}"
                         f" \\text{{ (extraneous)}} \\\\[4pt] "
                         f"\\text{{Valid: }} x = {valid[0]}")
        else:
            ans = f"x = {valid[0]} \\text{{ or }} x = {valid[1]}"
            check_note = ans

        sol = (f"\\text{{Square both sides: }} {a_str} = ({b_str})^2 \\\\[4pt] "
               f"{fmt_quad(1, B, C, 'x')} = 0 \\\\[4pt] "
               f"(x {'-' if r1>=0 else '+ '}{abs(r1)})(x {'-' if r2>=0 else '+ '}{abs(r2)}) = 0 \\\\[4pt] "
               f"x = {r1} \\text{{ or }} x = {r2} \\\\[4pt] "
               f"\\text{{Check both in original equation:}} \\\\[4pt] "
               f"{check_note}")
        return make_equation(eq, ans, sol, "x", is_wide=True)
    return None


def gen_surd_difference():
    """√(x+a) - √(b-x) = c  — isolate one surd, square twice."""
    for _ in range(300):
        # Choose x=r and second surd value s2 = √(b-r)
        r = ri(0, 8)
        b = r + ri(1, 6)    # b > r so b-r > 0
        s1 = int((r + ri(1,8))**0.5)   # want integer √(r+a)
        a = s1*s1 - r
        if a < 0: continue
        s2_sq = b - r
        s2 = int(s2_sq**0.5)
        if s2*s2 != s2_sq: continue    # need integer √(b-r)
        c = s1 - s2
        if c <= 0: continue             # want positive RHS

        # Equation: √(x+a) - √(b-x) = c
        # Isolate: √(x+a) = c + √(b-x)
        # Square: x+a = c² + 2c√(b-x) + b-x
        # 2c√(b-x) = x+a - c² - b + x = 2x + a - c² - b
        # Let K = a - c**2 - b
        K = a - c**2 - b
        # 2c√(b-x) = 2x + K  →  4c²(b-x) = (2x+K)²
        # 4c²b - 4c²x = 4x² + 4Kx + K²
        # 4x² + (4K+4c²)x + K² - 4c²b = 0
        A2 = 4; B2 = 4*K + 4*c**2; C2 = K**2 - 4*c**2*b
        disc2 = B2*B2 - 4*A2*C2
        if disc2 < 0: continue
        sq2 = int(disc2**0.5)
        if sq2*sq2 != disc2: continue
        rx1 = (-B2 + sq2) // (2*A2)
        if 2*A2*rx1 != -B2 + sq2: continue
        rx2 = (-B2 - sq2) // (2*A2)
        # Validate
        valid = []
        for rx in [rx1, rx2]:
            if rx + a < 0 or b - rx < 0: continue
            import math as _m
            lhs = _m.sqrt(rx+a) - _m.sqrt(b-rx)
            if abs(lhs - c) < 1e-9:
                valid.append(rx)
        if not valid: continue

        a_str = f"x + {a}" if a > 0 else f"x - {abs(a)}" if a < 0 else "x"
        eq = f"\\sqrt{{{a_str}}} - \\sqrt{{{b} - x}} = {c}"
        ans = f"x = {valid[0]}" if len(valid)==1 else f"x = {valid[0]} \\text{{ or }} x = {valid[1]}"
        sol = (f"\\text{{Isolate: }} \\sqrt{{{a_str}}} = {c} + \\sqrt{{{b}-x}} \\\\[4pt] "
               f"\\text{{Square: }} {a_str} = {c}^2 + 2({c})\\sqrt{{{b}-x}} + ({b}-x) \\\\[4pt] "
               f"2({c})\\sqrt{{{b}-x}} = 2x {'+' if K>=0 else '-'} {abs(K)} \\\\[4pt] "
               f"\\text{{Square again: }} {A2}({c**2})({b}-x) = (2x {'+' if K>=0 else ''}{K})^2 \\\\[4pt] "
               f"{A2}x^2 {'+'if B2>=0 else ''}{B2}x {'+'if C2>=0 else ''}{C2} = 0 \\\\[4pt] "
               f"{ans} \\\\[4pt] "
               f"\\text{{(check both roots in original)}}")
        return make_equation(eq, ans, sol, "x", is_wide=True)
    return None


# ══════════════════════════════════════════════════════════════════
# LT13 — INDICES EQUATIONS LEADING TO QUADRATICS
# ══════════════════════════════════════════════════════════════════

def gen_indices_quadratic():
    """
    (b^(x+p))^(x+q) = b^k  →  (x+p)(x+q) = k  →  quadratic.
    Also: b^(x²+bx) = b^c  →  x²+bx-c = 0.
    Covers the pattern from Image 3: (3^(x-7))^(x-5) = 27.
    """
    for _ in range(500):
        choice = random.choice(["power_of_power", "same_base"])

        if choice == "power_of_power":
            # (b^(x+p))^(x+q) = b^k
            # exponent = (x+p)(x+q) = k
            # pick integer roots r1, r2 of (x+p)(x+q)=k
            # i.e. x²+(p+q)x+(pq-k)=0, roots r1,r2
            base = random.choice([2, 3, 5])
            r1 = ri(-6, 8); r2 = ri(-6, 8)
            if r1 == r2: continue
            # Choose p, q as offsets: p = -r1+a, q = -r2+b for some shifts
            # Simpler: just pick p, q and compute k = (r1+p)(r1+q) = (r2+p)(r2+q)
            # That requires (r1+p)(r1+q) = (r2+p)(r2+q) — not generally true
            # Better: pick p, q freely; then k must satisfy both roots
            # k = (r1+p)(r1+q); verify r2 also a root: (r2+p)(r2+q) = k
            # This means r1 and r2 are roots of (x+p)(x+q) = k
            # (x+p)(x+q) - k = 0  →  x² + (p+q)x + pq - k = 0
            # roots: r1+r2 = -(p+q), r1*r2 = pq-k
            p = ri(-5, 5); q = ri(-5, 5)
            if p == 0 and q == 0: continue
            k = (r1 + p) * (r1 + q)
            # Verify r2 is also a root
            if (r2 + p) * (r2 + q) != k: continue
            if k <= 0: continue
            # k must be a power of base
            import math as _m
            log_k = _m.log(k, base)
            if abs(log_k - round(log_k)) > 1e-9: continue
            exp_rhs = int(round(log_k))  # b^exp_rhs = k

            # Format (x+p) and (x+q)
            def pm(n):
                if n > 0: return f"x + {n}"
                if n < 0: return f"x - {abs(n)}"
                return "x"

            lhs = f"({{base}}^{{{pm(p)}}})^{{{pm(q)}}}"
            rhs = f"{base}^{{{exp_rhs}}}" if exp_rhs != 1 else str(base)
            # Actual rhs value
            rhs_val = base**exp_rhs
            eq = f"\\left({base}^{{{pm(p)}}}\\right)^{{{pm(q)}}} = {rhs_val}"

            # Quadratic: (x+p)(x+q) = exp_rhs
            B_q = p + q; C_q = p*q - exp_rhs
            disc = B_q**2 - 4*C_q
            if disc < 0: continue
            ks, ms = simplify_surd(disc)
            if ms != 1: continue

            ans_str, steps, _ = fmt_surd_roots(1, B_q, C_q, v="x")
            sol = (f"\\text{{Use index law: }} (a^m)^n = a^{{mn}} \\\\[4pt] "
                   f"{base}^{{({pm(p)})({pm(q)})}} = {base}^{{{exp_rhs}}} \\\\[4pt] "
                   f"\\text{{Equate exponents: }} ({pm(p)})({pm(q)}) = {exp_rhs} \\\\[4pt] "
                   f"x^2 {'+' if B_q>=0 else ''}{B_q if B_q!=0 else ''}x {'+ ' + str(p*q) if p*q > 0 else str(p*q) if p*q < 0 else ''} = {exp_rhs} \\\\[4pt] "
                   f"x^2 {'+' if B_q>=0 else ''}{B_q if B_q!=0 else ''}x {'+ ' + str(C_q) if C_q > 0 else str(C_q) if C_q < 0 else ''} = 0 \\\\[4pt] "
                   + steps)
            return make_equation(
                eq, ans_str, sol, "x", is_wide=True,
                override_instruction=(
                    "Solve. (Hint: use the index law $(a^m)^n = a^{mn}$, "
                    "equate exponents, then solve the resulting quadratic.)"
                )
            )

        else:
            # b^(x²+bx+c) = b^k  →  x²+bx+c-k = 0
            base = random.choice([2, 3, 5])
            r1 = ri(-5, 6); r2 = ri(-5, 6)
            if r1 == r2: continue
            B_q = -(r1 + r2); C_q = r1 * r2
            k = ri(1, 8)
            # Exponent = x²+B_q*x+C_q = k  →  x²+B_q*x+(C_q-k) = 0
            C_final = C_q - k
            # Verify roots r1, r2
            if r1**2 + B_q*r1 + C_q != k: continue
            if r2**2 + B_q*r2 + C_q != k: continue

            def pm(n):
                if n > 0: return f"+ {n}"
                if n < 0: return f"- {abs(n)}"
                return ""

            exp_str = f"x^2 {pm(B_q)}x {pm(C_q)}" if C_q != 0 else f"x^2 {pm(B_q)}x"
            eq = f"{base}^{{{{{exp_str}}}}} = {base}^{{{k}}}"
            ans_str, steps, _ = fmt_surd_roots(1, B_q, C_final, v="x")
            sol = (f"\\text{{Same base: equate exponents}} \\\\[4pt] "
                   f"{exp_str} = {k} \\\\[4pt] "
                   f"x^2 {'+' if B_q>=0 else ''}{B_q if B_q!=0 else ''}x {'+' if C_final>=0 else ''}{C_final if C_final!=0 else ''} = 0 \\\\[4pt] "
                   + steps)
            return make_equation(
                eq, ans_str, sol, "x", is_wide=True,
                override_instruction=(
                    "Solve. (Hint: since the bases are equal, equate the exponents.)"
                )
            )
    return None

# ══════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    # LT1 — Factorising simple
    "factorise_simple":        (gen_factorise_simple,        8, "grid", "easy",   "LT1", 2),
    "factorise_negative_c":    (gen_factorise_negative_c,    8, "grid", "easy",   "LT1", 2),
    "factorise_both_negative": (gen_factorise_both_negative, 6, "grid", "medium", "LT1", 2),
    # LT2 — Factorising harder
    "factorise_hard":          (gen_factorise_hard,          6, "grid", "medium", "LT2", 2),
    "factorise_hard_negative": (gen_factorise_hard_negative, 4, "grid", "hard",   "LT2", 1),
    # LT3 — Special forms
    "diff_two_squares":        (gen_diff_two_squares,        8, "grid", "easy",   "LT3", 3),
    "perfect_square":          (gen_perfect_square,          6, "grid", "easy",   "LT3", 2),
    # LT4 — Solve by factorising
    "solve_simple":            (gen_solve_simple,            8, "grid", "easy",   "LT4", 2),
    "solve_hard":              (gen_solve_hard,              6, "grid", "medium", "LT4", 2),
    "solve_special":           (gen_solve_special,           6, "grid", "medium", "LT4", 2),
    # LT5 — Quadratic formula
    "formula_integer":         (gen_formula_integer,         6, "grid", "medium", "LT5", 2),
    "formula_surd":            (gen_formula_surd,            4, "grid", "hard",   "LT5", 1),
    "formula_non_real":        (gen_formula_non_real,        4, "grid", "hard",   "LT5", 2),
    # LT6 — Completing the square
    "complete_square_form":           (gen_complete_square_form,           6, "grid", "medium", "LT6", 2),
    "complete_square_nonmonic":       (gen_complete_square_nonmonic,       4, "grid", "hard",   "LT6", 1),
    "complete_square_solve":          (gen_complete_square_solve,          4, "grid", "hard",   "LT6", 1),
    "complete_square_nonmonic_solve": (gen_complete_square_nonmonic_solve, 3, "grid", "hard",   "LT6", 1),
    # LT7 — Word problems
    "word_area":        (gen_word_area,        3, "list", "medium", "LT7", 1),
    "word_consecutive": (gen_word_consecutive, 3, "list", "medium", "LT7", 1),
    "word_projectile":  (gen_word_projectile,  2, "list", "hard",   "LT7", 1),
    # LT7 extension — more integer word problems
    "word_even_integers": (gen_word_even_integers, 3, "list", "medium", "LT7", 1),
    "word_odd_integers":  (gen_word_odd_integers,  3, "list", "hard",   "LT7", 1),
    # LT8 — Geometry
    "geo_rectangle":           (gen_geo_rectangle,           2, "list", "medium", "LT8", 1),
    "geo_right_triangle":      (gen_geo_right_triangle,      2, "list", "hard",   "LT8", 1),
    "geo_right_triangle_area": (gen_geo_right_triangle_area, 2, "list", "hard",   "LT8", 1),
    "geo_L_shape":             (gen_geo_L_shape,             2, "list", "hard",   "LT8", 1),
    "geo_cuboid_surface":      (gen_geo_cuboid_surface,      2, "list", "hard",   "LT8", 1),
    "geo_cuboid_volume":       (gen_geo_cuboid_volume,       2, "list", "hard",   "LT8", 1),
    # LT5 extension — Discriminant
    "discriminant_nature": (gen_discriminant_nature, 6, "grid", "medium", "LT5", 2),
    "discriminant_find_k": (gen_discriminant_find_k, 4, "grid", "hard",   "LT5", 1),
    # LT9 — Forming equations from roots
    "roots_to_equation":  (gen_roots_to_equation,  4, "grid", "medium", "LT9", 1),
    "roots_symmetric":    (gen_roots_symmetric,     4, "grid", "hard",   "LT9", 1),
    # LT10 — Algebraic fraction equations
    "frac_equation_simple": (gen_frac_equation_simple, 4, "grid", "hard",   "LT10", 1),
    "frac_equation_diff":   (gen_frac_equation_diff,   4, "grid", "hard",   "LT10", 1),
    # LT11 — Disguised quadratics
    "disguised_biquadratic":  (gen_disguised_biquadratic,  4, "grid", "hard",   "LT11", 1),
    "disguised_linear_sub":   (gen_disguised_linear_sub,   4, "grid", "hard",   "LT11", 1),
    # LT12 — Surd equations
    "surd_simple":     (gen_surd_simple,     4, "grid", "hard",   "LT12", 1),
    "surd_difference": (gen_surd_difference, 3, "grid", "hard",   "LT12", 1),
    # LT13 — Indices equations leading to quadratics
    "indices_quadratic": (gen_indices_quadratic, 4, "grid", "hard", "LT13", 1),
}

# ══════════════════════════════════════════════════════════════════
# RENDERER  (identical contract to LinearEquations.py)
# ══════════════════════════════════════════════════════════════════

def _render_stimulus(s):
    out = ["\n"]
    if s["svg"]:   out.append(f"\n{s['svg']}\n")
    if s["text"]:  out.append(f"\n{s['text']}\n")
    if s["points"]:
        out.append("\n")
        for pt in s["points"]: out.append(f"- {pt}\n")
        out.append("\n")
    return "".join(out)

def _render_solution_callout(item):
    raw = item["solution"]
    for tag in ["\\\\[8pt]", "\\\\[4pt]", "\\[8pt]", "\\[4pt]"]:
        raw = raw.replace(tag, " \\\\")
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

def render_grid_block(items, labels, ex_numbers, cols=3,
                      show_solution=True, ex_id=None, instruction=None):
    col_width = 12 // cols
    rows       = [items[i:i+cols]  for i in range(0, len(items), cols)]
    row_labels = [labels[i:i+cols] for i in range(0, len(labels), cols)]
    lines = []
    if ex_id: lines.append(f"\n::::: {{#exr-u6-{ex_id}}}\n")
    if instruction: lines.append(f"\n*{instruction}*\n")
    for row, rlabels in zip(rows, row_labels):
        lines.append("\n:::: {.grid}\n")
        for item, lbl in zip(row, rlabels):
            lines.append(f"\n::: {{.g-col-{col_width}}}\n")
            lines.append(f"\n**{lbl})** $\\displaystyle {item['equation']}$\n")
            lines.append("\n:::\n")
        lines.append("\n::::\n")
    if show_solution:
        lines.append('\n::: {.callout-tip collapse="true"}')
        lines.append("\n## \U0001f50d View Solutions\n")
        for item, lbl in zip(items, labels):
            raw = item["solution"]
            for tag in ["\\\\[8pt]","\\\\[4pt]","\\[8pt]","\\[4pt]"]:
                raw = raw.replace(tag, " \\\\")
            steps = [s.strip() for s in raw.split("\\\\") if s.strip()]
            seen = []; deduped = []
            for s in steps:
                if s not in seen: seen.append(s); deduped.append(s)
            sol = " \\\\ ".join(deduped)
            math_b = "\\begin{align*}\n" + sol + "\n\\end{align*}"
            lines.append(f"\n**{lbl})** $\\displaystyle {item['equation']}$\n")
            lines.append("\n" + math_b + "\n")
        lines.append("\n:::\n")
    if ex_id: lines.append("\n:::::\n")
    return "".join(lines)

def render_list_block(items, labels, ex_id, show_solution=True):
    lines = []
    for k, item in enumerate(items):
        item_id = f"{ex_id}-{k+1}" if len(items) > 1 else ex_id
        lines.append(f"\n::::: {{#exr-u6-{item_id}}}\n")
        lines.append("\n```{=html}\n<!-- ex-body -->\n```\n")
        lines.append(_render_stimulus(item["stimulus"]))
        for p in item["parts"]:
            lines.append(f"\n**({p['label']})** {p['prompt']}\n")
        if show_solution:
            lines.append(_render_solution_callout(item))
        lines.append("\n:::::\n")
    return "".join(lines)

# ══════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════

def generate(types, seed=42, show_solutions=True,
             count_override=None, count=None, layout_override=None):
    if count is not None and count_override is None:
        count_override = count
    if seed is not None:
        random.seed(seed)

    exercises_qmd = []
    global_label_idx = 0

    for ex_type in types:
        if ex_type not in REGISTRY:
            raise ValueError(f"Unknown type: '{ex_type}'. Available: {sorted(REGISTRY.keys())}")

        gen_fn, default_count, default_layout, difficulty, lt, grid_cols = REGISTRY[ex_type]
        cnt    = count_override if count_override is not None else default_count
        layout = layout_override if layout_override is not None else default_layout

        items = []
        attempts = 0
        while len(items) < cnt and attempts < cnt * 30:
            try:
                item = gen_fn()
                if item: items.append(item)
            except Exception:
                pass
            attempts += 1

        if not items: continue

        labels = [PART_LABELS[i % 26] for i in range(len(items))]
        global_label_idx += 1
        ex_id  = str(global_label_idx)
        ex_nums = [f"{ex_id}-{i+1}" for i in range(len(items))]

        # Pick instruction based on type
        _instr_map = {
            "factorise_simple": "Factorise each expression.",
            "factorise_negative_c": "Factorise each expression.",
            "factorise_both_negative": "Factorise each expression.",
            "factorise_hard": "Factorise each expression.",
            "factorise_hard_negative": "Factorise each expression.",
            "diff_two_squares": "Factorise using the difference of two squares.",
            "perfect_square": "Recognise and factorise each perfect square.",
            "solve_simple": "Solve each quadratic equation.",
            "solve_hard": "Solve each quadratic equation.",
            "solve_special": "Solve each equation.",
            "formula_integer": "Solve using the quadratic formula.",
            "formula_surd": "Solve using the quadratic formula. Leave answers in surd form.",
            "formula_non_real": "Use the discriminant to determine the nature of roots.",
            "complete_square_form": "Write each expression in completed square form.",
            "complete_square_nonmonic": "Write in the form $a(x+p)^2 + q$.",
            "complete_square_solve": "Solve by completing the square.",
            "complete_square_nonmonic_solve": "Solve by completing the square.",
            "discriminant_nature": "Find the discriminant and state the nature of the roots.",
            "discriminant_find_k": "Find the value(s) of $k$.",
            "roots_to_equation":   "Form a quadratic equation with the given roots.",
            "roots_symmetric":     "Use Vieta's formulas to find the expression.",
            "frac_equation_simple": "Solve. State any values of $x$ that must be excluded.",
            "frac_equation_diff":   "Solve. State any values of $x$ that must be excluded.",
            "disguised_biquadratic":  "Solve using the substitution $u = x^2$.",
            "disguised_linear_sub":   "Solve using an appropriate substitution.",
            "surd_simple":     "Solve. Check for extraneous roots.",
            "surd_difference": "Solve. Check for extraneous roots.",
            "indices_quadratic": "Find all possible values of $x$.",
            "word_even_integers": "Form and solve a quadratic equation.",
            "word_odd_integers":  "Form and solve a quadratic equation.",
            "geo_right_triangle_area": "Use Pythagoras to form a quadratic, then find the area.",
            "geo_L_shape":        "Form a quadratic from the area, then solve.",
            "geo_cuboid_surface": "Form a quadratic from the surface area, then find the volume.",
            "geo_cuboid_volume":  "Form a quadratic from the volume, then solve.",
        }
        ex_instruction = _instr_map.get(ex_type, "Simplify or solve.")
        # Allow individual items to override the instruction
        if items and items[0].get("override_instruction"):
            ex_instruction = items[0]["override_instruction"]

        if layout == "grid" and all(it["item_type"] == "equation" for it in items):
            rendered = render_grid_block(items, labels, ex_nums,
                                         cols=grid_cols,
                                         show_solution=show_solutions,
                                         ex_id=ex_id,
                                         instruction=ex_instruction)
        else:
            rendered = render_list_block(items, labels, ex_id,
                                          show_solution=show_solutions)

        ex_title = ex_type.replace("_", " ").title()
        exercises_qmd.append({
            "type":       ex_type,
            "title":      ex_title,
            "difficulty": difficulty,
            "lt":         lt,
            "rendered":   rendered,
            "items":      items,
        })

    # Worksheet-compatible exercises (equation types only)
    ws_exercises = []
    for i, ex in enumerate(exercises_qmd, 1):
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
                "instruction": "Simplify or solve.",
                "parts":       parts,
            })

    ws_meta = {
        "title":       "Quadratic Equations",
        "unit":        "Unit 6 · Quadratic Equations",
        "date":        str(date.today()),
        "total_parts": sum(len(e["parts"]) for e in ws_exercises),
        "seed":        seed,
    }

    return {
        "worksheet":       ws_meta,
        "exercises":       ws_exercises,
        "_exercises_qmd":  exercises_qmd,
        "meta": {"date": str(date.today()), "seed": seed, "types": types},
    }

def generate_session(types_json, seed=42, count=None, show_solutions=False):
    """Called by Pyodide worksheet."""
    types = json.loads(types_json)
    data  = generate(types=types, seed=seed, count_override=count,
                     show_solutions=show_solutions)
    return json.dumps({"worksheet": data["worksheet"], "exercises": data["exercises"]})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--types", nargs="+", default=["factorise_simple"])
    parser.add_argument("--seed",  type=int, default=42)
    parser.add_argument("--list-types", action="store_true")
    args = parser.parse_args()
    if args.list_types:
        print("\nAvailable types:\n")
        for k, (_, cnt, lay, diff, lt, cols) in sorted(REGISTRY.items()):
            badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(diff,"⚪")
            print(f"  {badge} {k:<35} count={cnt:<2} layout={lay:<5} cols={cols} {lt}")
        print()
    else:
        data = generate(types=args.types, seed=args.seed, show_solutions=True)
        for ex in data["_exercises_qmd"]:
            print(ex["rendered"])
