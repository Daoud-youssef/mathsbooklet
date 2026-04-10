"""
components.py
=============
Reusable math components for the Math-Booklet project.

Location : assets/components.py
Import   : from components import *

Four categories:
    1. FRACTIONS   — format, simplify, add, subtract, multiply, divide
    2. SURDS       — simplify, format, add, subtract, multiply, rationalise  
    3. EXPONENTS   — format terms, power rules
    4. EXPRESSIONS — linear, quadratic, vertex, factored forms

Plus shared utilities:
    - Random value helpers (ri, rc, rand_coeff, rand_exp, rand_side)
    - Solution step builder (steps)
    - LaTeX primitives (frac, dfrac)

Usage
-----
from components import (
    # Fractions
    Frac, simplify_frac, add_frac, sub_frac, mul_frac, div_frac,
    fmt_fraction, fmt_mixed,

    # Surds
    simplify_surd, fmt_surd, surd_label, add_surds, mul_surds,

    # Exponents
    fmt_exp, fmt_term, fmt_frac,

    # Expressions  
    fmt_linear, fmt_quad, fmt_vertex, fmt_factored,

    # Utilities
    ri, rc, rand_coeff, rand_exp, rand_side, rand_verts,
    steps, sign_str,
)
"""

import math
import random
import string

# ══════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ══════════════════════════════════════════════════════════════════

VARIABLES     = ["a", "b", "c", "m", "n", "x", "y", "k", "p", "t", "w"]
VERTEX_LETTERS = list(string.ascii_uppercase)

def ri(a, b):
    """Random integer in [a, b]."""
    return random.randint(a, b)

def rc(exclude=None):
    """Random variable letter, optionally excluding one."""
    pool = [v for v in VARIABLES if v != exclude]
    return random.choice(pool)

def rand_coeff(low=2, high=9):
    """Random coefficient."""
    return ri(low, high)

def rand_exp(low=2, high=8):
    """Random positive exponent."""
    return ri(low, high)

def rand_side():
    """Random side length."""
    return random.choice([3, 4, 5, 6, 7, 8, 10, 12])

def rand_verts(n):
    """Kept for backwards compatibility. Use pick_verts instead."""
    return random.sample(VERTEX_LETTERS, n)
 
 
def pick_verts(n, exclude=None):
    """
    Pick n distinct random uppercase letters for vertex labels.
    The standard pattern for ALL exercise generators:
 
        apex, bl, br = pick_verts(3)
        svg = SVG.figure("isosceles", vertices=[bl, br, apex], ...)
        context = f"Triangle ${bl}{apex}{br}$: ..."
        question = f"Find angle ${apex}{bl}{br}$."
 
    Name variables by their geometric role (apex, bl, br...)
    not by letter value — those are random every time.
 
    Args:
        n:       number of vertices needed
        exclude: optional list of letters already used elsewhere
                 (useful when two triangles share a diagram)
    """
    pool = [v for v in VERTEX_LETTERS if not exclude or v not in exclude]
    return random.sample(pool, n)

def sign_str(n):
    """
    Format n as a sign string for building expressions.
    e.g.  3 → '+ 3',  -3 → '- 3',  0 → ''
    """
    if n == 0:   return ""
    if n > 0:    return f"+ {n}"
    return f"- {abs(n)}"

def sign_term(coef, var="", power=1):
    """
    Format a signed term for building expressions.
    e.g. (3, 'x', 2) → '+ 3x^{2}',  (-1, 'x', 1) → '- x'
    """
    if coef == 0:   return ""
    sign   = "+" if coef > 0 else "-"
    c      = abs(coef)
    c_str  = "" if c == 1 and var else str(c)
    if not var:
        return f"{sign} {c}"
    if power == 0:
        return f"{sign} {c}"
    if power == 1:
        return f"{sign} {c_str}{var}"
    return f"{sign} {c_str}{var}^{{{power}}}"


# ══════════════════════════════════════════════════════════════════
# 1. FRACTIONS
# ══════════════════════════════════════════════════════════════════

def _gcd(a, b):
    a, b = abs(int(a)), abs(int(b))
    while b: a, b = b, a % b
    return a or 1

def _lcm(a, b):
    return abs(a * b) // _gcd(a, b)

def simplify_frac(num, den):
    """
    Return (num, den) in lowest terms.
    Sign always on numerator.
    e.g. simplify_frac(6, -4) → (-3, 2)
    """
    if den == 0: raise ZeroDivisionError("denominator is zero")
    if num == 0: return (0, 1)
    sign  = -1 if (num < 0) != (den < 0) else 1
    num, den = abs(num), abs(den)
    g = _gcd(num, den)
    return (sign * num // g, den // g)

# Named tuple-like class for fractions
class Frac:
    """
    Immutable fraction with auto-simplification.

    Usage:
        f = Frac(3, 4)           # 3/4
        g = Frac(6, 8)           # also 3/4 (auto-simplified)
        h = f + g                # Frac(3, 2)
        print(f.latex)           # \\dfrac{3}{4}
        print(f.latex_inline)    # \\frac{3}{4}
        print(f.plain)           # 3/4
        print(float(f))          # 0.75
        print(f.is_integer)      # False
        print(Frac(4,2).value)   # 2  (integer when den==1)
    """
    __slots__ = ("num", "den")

    def __init__(self, num, den=1):
        n, d = simplify_frac(int(num), int(den))
        object.__setattr__(self, "num", n)
        object.__setattr__(self, "den", d)

    def __setattr__(self, *_): raise AttributeError("Frac is immutable")

    def __add__(self, other):
        o = other if isinstance(other, Frac) else Frac(other)
        return Frac(self.num*o.den + o.num*self.den, self.den*o.den)

    def __sub__(self, other):
        o = other if isinstance(other, Frac) else Frac(other)
        return Frac(self.num*o.den - o.num*self.den, self.den*o.den)

    def __mul__(self, other):
        o = other if isinstance(other, Frac) else Frac(other)
        return Frac(self.num*o.num, self.den*o.den)

    def __truediv__(self, other):
        o = other if isinstance(other, Frac) else Frac(other)
        return Frac(self.num*o.den, self.den*o.num)

    def __neg__(self):      return Frac(-self.num, self.den)
    def __abs__(self):      return Frac(abs(self.num), self.den)
    def __float__(self):    return self.num / self.den
    def __int__(self):      return self.num // self.den
    def __eq__(self, o):    return isinstance(o,Frac) and self.num==o.num and self.den==o.den
    def __repr__(self):     return f"Frac({self.num},{self.den})"

    @property
    def is_integer(self):   return self.den == 1

    @property
    def value(self):
        """Return int if whole number, else self."""
        return self.num if self.den == 1 else self

    @property
    def latex(self):
        """Display fraction as LaTeX \\dfrac."""
        if self.den == 1: return str(self.num)
        return f"\\dfrac{{{self.num}}}{{{self.den}}}"

    @property
    def latex_inline(self):
        """Inline fraction as LaTeX \\frac."""
        if self.den == 1: return str(self.num)
        return f"\\frac{{{self.num}}}{{{self.den}}}"

    @property
    def plain(self):
        """Plain text: '3/4'."""
        if self.den == 1: return str(self.num)
        return f"{self.num}/{self.den}"


# Convenience operations (functional style)

def add_frac(n1, d1, n2, d2):
    """Add two fractions, return (num, den) simplified."""
    return Frac(n1, d1) + Frac(n2, d2)

def sub_frac(n1, d1, n2, d2):
    """Subtract two fractions, return (num, den) simplified."""
    return Frac(n1, d1) - Frac(n2, d2)

def mul_frac(n1, d1, n2, d2):
    """Multiply two fractions, return (num, den) simplified."""
    return Frac(n1, d1) * Frac(n2, d2)

def div_frac(n1, d1, n2, d2):
    """Divide two fractions, return (num, den) simplified."""
    return Frac(n1, d1) / Frac(n2, d2)

def fmt_fraction(num, den, display=True):
    """
    Format fraction as LaTeX string.
    display=True  → \\dfrac{3}{4}
    display=False → \\frac{3}{4}
    Automatically simplifies and returns integer string if den==1.
    """
    return Frac(num, den).latex if display else Frac(num, den).latex_inline

def fmt_mixed(whole, num, den):
    """
    Format mixed number as LaTeX.
    e.g. fmt_mixed(2, 1, 3) → '2\\frac{1}{3}'
    """
    f = Frac(num, den)
    if f.is_integer: return str(whole + int(f))
    sign = "-" if whole < 0 else ""
    return f"{sign}{abs(whole)}\\frac{{{abs(f.num)}}}{{{f.den}}}"

def fmt_frac(num_latex, den_latex):
    """
    Format arbitrary LaTeX numerator/denominator as \\dfrac.
    For when numerator/denominator are already LaTeX strings.
    e.g. fmt_frac('x^2', 'y^3') → '\\dfrac{x^2}{y^3}'
    """
    return f"\\dfrac{{{num_latex}}}{{{den_latex}}}"

# Addition / subtraction step builders

def steps_add_frac(n1, d1, n2, d2):
    """
    Return LaTeX showing addition steps.
    e.g. steps_add_frac(1,3,1,4) →
        \\dfrac{1}{3} + \\dfrac{1}{4}
        = \\dfrac{4}{12} + \\dfrac{3}{12}
        = \\dfrac{7}{12}
    """
    f1 = Frac(n1, d1); f2 = Frac(n2, d2)
    lcd = _lcm(f1.den, f2.den)
    m1  = lcd // f1.den; m2 = lcd // f2.den
    num1 = f1.num * m1; num2 = f2.num * m2
    result = f1 + f2
    op = "+" if n2 >= 0 else "-"
    return (
        f"{f1.latex} {op} {abs(f2).latex} "
        f"= \\dfrac{{{num1}}}{{{lcd}}} {op} \\dfrac{{{abs(num2)}}}{{{lcd}}} "
        f"= {result.latex}"
    )

def steps_sub_frac(n1, d1, n2, d2):
    return steps_add_frac(n1, d1, -n2, d2)

def steps_mul_frac(n1, d1, n2, d2):
    """
    e.g. steps_mul_frac(2,3,3,4) →
        \\dfrac{2}{3} \\times \\dfrac{3}{4} = \\dfrac{6}{12} = \\dfrac{1}{2}
    """
    f1 = Frac(n1,d1); f2 = Frac(n2,d2)
    result = f1 * f2
    return (f"{f1.latex} \\times {f2.latex} "
            f"= \\dfrac{{{f1.num*f2.num}}}{{{f1.den*f2.den}}} = {result.latex}")

def steps_div_frac(n1, d1, n2, d2):
    """
    e.g. steps_div_frac(2,3,4,5) →
        \\dfrac{2}{3} \\div \\dfrac{4}{5}
        = \\dfrac{2}{3} \\times \\dfrac{5}{4}
        = \\dfrac{10}{12} = \\dfrac{5}{6}
    """
    f1 = Frac(n1,d1); f2 = Frac(n2,d2)
    recip = Frac(f2.den, f2.num)
    result = f1 * recip
    return (f"{f1.latex} \\div {f2.latex} "
            f"= {f1.latex} \\times {recip.latex} "
            f"= \\dfrac{{{f1.num*recip.num}}}{{{f1.den*recip.den}}} = {result.latex}")


# ══════════════════════════════════════════════════════════════════
# 2. SURDS
# ══════════════════════════════════════════════════════════════════

def simplify_surd(n):
    """
    Return (coeff, radicand) in simplest form.
    e.g. simplify_surd(200) → (10, 2)
         simplify_surd(48)  → (4, 3)
         simplify_surd(7)   → (1, 7)
    """
    n = int(n)
    best = 1
    for k in range(2, int(math.isqrt(n)) + 1):
        if n % (k * k) == 0:
            best = k * k
    coeff = int(math.isqrt(best))
    return coeff, n // best

def fmt_surd(coeff, radicand):
    """
    Format a√n as LaTeX.
    e.g. fmt_surd(1,7) → '\\sqrt{7}'
         fmt_surd(3,2) → '3\\sqrt{2}'
         fmt_surd(4,1) → '4'
    """
    if radicand == 1: return str(coeff)
    if coeff == 1:    return f"\\sqrt{{{radicand}}}"
    return f"{coeff}\\sqrt{{{radicand}}}"

def surd_label(n):
    """
    Format √n as Unicode plain text for SVG labels.
    e.g. surd_label(8) → '2√2'
         surd_label(7) → '√7'
    """
    c, r = simplify_surd(n)
    if r == 1:  return str(c)
    if c == 1:  return f"\u221a{n}"
    return f"{c}\u221a{r}"

def add_surds(c1, r1, c2, r2):
    """
    Add two surds: c1√r1 + c2√r2.
    Returns (coeff, radicand) if same radicand, else None.
    e.g. add_surds(3,2,5,2) → (8,2)  →  8√2
         add_surds(3,2,5,3) → None   (different surds)
    """
    if r1 != r2: return None
    return (c1 + c2, r1)

def sub_surds(c1, r1, c2, r2):
    """Subtract two surds: c1√r1 - c2√r2."""
    if r1 != r2: return None
    return (c1 - c2, r1)

def mul_surds(c1, r1, c2, r2):
    """
    Multiply two surds: c1√r1 × c2√r2.
    Returns (coeff, radicand) simplified.
    e.g. mul_surds(2,3,4,3) → (24,1) → 24
         mul_surds(1,2,1,8) → (4,1)  → 4
    """
    coeff_raw = c1 * c2
    rad_raw   = r1 * r2
    c, r = simplify_surd(rad_raw)
    return (coeff_raw * c, r)

def rationalise(num_coeff, den_coeff, den_rad):
    """
    Rationalise: (num_coeff) / (den_coeff√den_rad)
    Multiply top and bottom by √den_rad.
    Returns (new_num_latex, new_den_int).
    e.g. rationalise(3, 2, 5) →
         3/(2√5) × √5/√5 = 3√5/10
    """
    new_den = den_coeff * den_rad
    g = _gcd(num_coeff, new_den)
    nc = num_coeff // g
    nd = new_den   // g
    if nc == 1:
        num_latex = f"\\sqrt{{{den_rad}}}"
    else:
        num_latex = f"{nc}\\sqrt{{{den_rad}}}"
    return num_latex, nd

def steps_simplify_surd(n):
    """
    Return LaTeX showing surd simplification steps.
    e.g. steps_simplify_surd(48) →
        \\sqrt{48} = \\sqrt{16 \\times 3} = 4\\sqrt{3}
    """
    c, r = simplify_surd(n)
    if c == 1: return f"\\sqrt{{{n}}}"
    factor = c * c
    return (f"\\sqrt{{{n}}} = \\sqrt{{{factor} \\times {r}}} "
            f"= {fmt_surd(c, r)}")

def steps_mul_surds(c1, r1, c2, r2):
    """
    Return LaTeX showing surd multiplication steps.
    e.g. steps_mul_surds(2,3,4,3) →
        2\\sqrt{3} \\times 4\\sqrt{3} = 8 \\times 3 = 24
    """
    cr, rr = mul_surds(c1, r1, c2, r2)
    s1 = fmt_surd(c1, r1); s2 = fmt_surd(c2, r2)
    result = fmt_surd(cr, rr)
    if r1 == r2:
        return f"{s1} \\times {s2} = {c1*c2} \\times {r1} = {result}"
    raw_c = c1*c2; raw_r = r1*r2
    c_mid, r_mid = simplify_surd(raw_r)
    return (f"{s1} \\times {s2} = {raw_c}\\sqrt{{{raw_r}}} "
            f"= {raw_c} \\times {c_mid}\\sqrt{{{r_mid}}} = {result}")

def steps_rationalise(num_coeff, den_coeff, den_rad):
    """
    Return LaTeX showing rationalisation steps.
    e.g. steps_rationalise(3,2,5) →
        \\dfrac{3}{2\\sqrt{5}} \\times \\dfrac{\\sqrt{5}}{\\sqrt{5}}
        = \\dfrac{3\\sqrt{5}}{10}
    """
    num_l, new_den = rationalise(num_coeff, den_coeff, den_rad)
    before = fmt_frac(str(num_coeff),
                      fmt_surd(den_coeff, den_rad))
    after  = fmt_frac(f"{num_coeff}\\sqrt{{{den_rad}}}",
                      str(den_coeff * den_rad))
    final  = fmt_frac(num_l, str(new_den))
    return (f"{before} \\times "
            f"\\dfrac{{\\sqrt{{{den_rad}}}}}{{\\sqrt{{{den_rad}}}}} "
            f"= {after} = {final}")


# ══════════════════════════════════════════════════════════════════
# 3. EXPONENTS
# ══════════════════════════════════════════════════════════════════

def fmt_exp(base, power):
    """
    Format base^power as LaTeX.
    e.g. fmt_exp('x', 3) → 'x^{3}'
         fmt_exp('x', 1) → 'x'
         fmt_exp('x', 0) → '1'
    """
    if power == 0: return "1"
    if power == 1: return str(base)
    return f"{base}^{{{power}}}"

def fmt_term(coef, base, power):
    """
    Format coefficient × base^power as LaTeX.
    e.g. fmt_term(3,'x',2) → '3x^{2}'
         fmt_term(1,'x',1) → 'x'
         fmt_term(2,'x',0) → '2'
    """
    c = "" if coef == 1 else str(coef)
    if power == 0: return str(coef)
    if power == 1: return f"{c}{base}"
    return f"{c}{base}^{{{power}}}"

def steps_multiply_exp(v, m, n):
    """
    e.g. steps_multiply_exp('x',3,4) →
        x^{3} \\times x^{4} = x^{3+4} = x^{7}
    """
    ans = m + n
    return (f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)} "
            f"= {v}^{{{m}+{n}}} = {fmt_exp(v,ans)}")

def steps_divide_exp(v, m, n):
    """
    e.g. steps_divide_exp('x',7,3) →
        x^{7} \\div x^{3} = x^{7-3} = x^{4}
    """
    ans = m - n
    return (f"{fmt_exp(v,m)} \\div {fmt_exp(v,n)} "
            f"= {v}^{{{m}-{n}}} = {fmt_exp(v,ans)}")

def steps_power_exp(v, m, n):
    """
    e.g. steps_power_exp('x',3,4) →
        (x^{3})^{4} = x^{3 \\times 4} = x^{12}
    """
    ans = m * n
    return (f"({fmt_exp(v,m)})^{{{n}}} "
            f"= {v}^{{{m} \\times {n}}} = {fmt_exp(v,ans)}")


# ══════════════════════════════════════════════════════════════════
# 4. EXPRESSIONS
# ══════════════════════════════════════════════════════════════════

def fmt_linear(m, c, v="x"):
    """
    Format mx + c as LaTeX.
    e.g. fmt_linear(2,3,'x')  → '2x + 3'
         fmt_linear(-1,0,'x') → '-x'
         fmt_linear(1,-4,'t') → 't - 4'
    """
    from fractions import Fraction
    m_f = Fraction(m).limit_denominator(20)
    c_f = Fraction(c).limit_denominator(20)

    # slope term
    if   m_f == 0:   slope = ""
    elif m_f == 1:   slope = v
    elif m_f == -1:  slope = f"-{v}"
    elif m_f.denominator == 1:
        slope = f"{m_f.numerator}{v}"
    else:
        slope = f"\\frac{{{m_f.numerator}}}{{{m_f.denominator}}}{v}"

    # intercept term
    if c_f == 0:     intercept = ""
    elif c_f > 0:    intercept = f"+ {c_f}" if slope else str(c_f)
    else:            intercept = f"- {abs(c_f)}"

    result = f"{slope} {intercept}".strip()
    return result or "0"

def fmt_quad(a, b, c, v="x"):
    """
    Format ax² + bx + c as LaTeX.
    e.g. fmt_quad(1,-3,2,'x') → 'x^{2} - 3x + 2'
         fmt_quad(2,0,-5,'x') → '2x^{2} - 5'
    """
    parts = []

    # ax² term
    if   a == 1:  parts.append(f"{v}^{{2}}")
    elif a == -1: parts.append(f"-{v}^{{2}}")
    elif a != 0:  parts.append(f"{a}{v}^{{2}}")

    # bx term
    if b != 0:
        bv = abs(b)
        sign = "+" if b > 0 else "-"
        bstr = f"{v}" if bv == 1 else f"{bv}{v}"
        if parts: parts.append(f"{sign} {bstr}")
        else:     parts.append(f"{'-' if b<0 else ''}{bstr}")

    # c term
    if c != 0:
        sign = "+" if c > 0 else "-"
        if parts: parts.append(f"{sign} {abs(c)}")
        else:     parts.append(str(c))

    return " ".join(parts) if parts else "0"

def fmt_vertex(a, h, k, v="x"):
    """
    Format a(x-h)² + k as LaTeX.
    e.g. fmt_vertex(2,3,-1,'x') → '2(x - 3)^{2} - 1'
         fmt_vertex(1,-2,4,'x') → '(x + 2)^{2} + 4'
    """
    a_str = "" if a == 1 else ("-" if a == -1 else str(a))
    h_str = f"({v} - {h})" if h > 0 else (
            f"({v} + {abs(h)})" if h < 0 else f"{v}")
    k_str = f"+ {k}" if k > 0 else (f"- {abs(k)}" if k < 0 else "")
    return f"{a_str}{h_str}^{{2}} {k_str}".strip()

def fmt_factored(a, r1, r2, v="x"):
    """
    Format a(x-r1)(x-r2) as LaTeX.
    e.g. fmt_factored(1,2,-3,'x') → '(x - 2)(x + 3)'
         fmt_factored(2,1,1,'x')  → '2(x - 1)^{2}'
    """
    a_str = "" if a == 1 else ("-" if a == -1 else str(a))

    def factor(r):
        if r == 0:   return f"{v}"
        if r > 0:    return f"({v} - {r})"
        return       f"({v} + {abs(r)})"

    if r1 == r2:
        return f"{a_str}{factor(r1)}^{{2}}"
    return f"{a_str}{factor(r1)}{factor(r2)}"


# ══════════════════════════════════════════════════════════════════
# SOLUTION STEP BUILDER
# ══════════════════════════════════════════════════════════════════

def steps(*lines):
    """
    Build a LaTeX aligned solution block from step strings.
    Each string in lines becomes one line in \\begin{aligned}.
    Use '\\\\' within a string for sub-steps on the same line.

    Usage:
        sol = steps(
            r"x^2 = 3 + 13 = 16",
            r"x = \\sqrt{16} = 4",
        )
    Returns:
        "x^2 = 3 + 13 = 16 \\\\ x = \\sqrt{16} = 4"
    (The renderer wraps this in \\begin{aligned}...\\end{aligned})
    """
    return " \\\\ ".join(str(l) for l in lines if l)


# ══════════════════════════════════════════════════════════════════
# SMOKE TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("── Fractions ─────────────────────────────────────────────")
    f = Frac(3, 4)
    g = Frac(1, 6)
    print(f"  3/4 + 1/6 = {(f+g).latex}")           # 11/12
    print(f"  3/4 - 1/6 = {(f-g).latex}")           # 7/12
    print(f"  3/4 × 1/6 = {(f*g).latex}")           # 1/8
    print(f"  3/4 ÷ 1/6 = {(f/g).latex}")           # 9/2
    print(f"  fmt_fraction(6,8) = {fmt_fraction(6,8)}")  # 3/4
    print(f"  fmt_mixed(2,1,3)  = {fmt_mixed(2,1,3)}")   # 2 1/3
    print(f"  steps add 1/3+1/4: {steps_add_frac(1,3,1,4)}")
    print(f"  steps div 2/3÷4/5: {steps_div_frac(2,3,4,5)}")

    print("\n── Surds ─────────────────────────────────────────────────")
    c, r = simplify_surd(200)
    print(f"  simplify √200 = {fmt_surd(c,r)}")     # 10√2
    print(f"  surd_label(48) = {surd_label(48)}")   # 4√3
    print(f"  steps √48: {steps_simplify_surd(48)}")
    c2, r2 = mul_surds(2, 3, 4, 3)
    print(f"  2√3 × 4√3 = {fmt_surd(c2,r2)}")      # 24
    print(f"  steps mul: {steps_mul_surds(2,3,4,3)}")
    print(f"  steps rationalise 3/(2√5): {steps_rationalise(3,2,5)}")

    print("\n── Exponents ─────────────────────────────────────────────")
    print(f"  fmt_exp('x',3)     = {fmt_exp('x',3)}")
    print(f"  fmt_term(3,'x',2)  = {fmt_term(3,'x',2)}")
    print(f"  steps x³×x⁴: {steps_multiply_exp('x',3,4)}")
    print(f"  steps x⁷÷x³: {steps_divide_exp('x',7,3)}")
    print(f"  steps (x³)⁴: {steps_power_exp('x',3,4)}")

    print("\n── Expressions ───────────────────────────────────────────")
    print(f"  fmt_linear(2,-3,'x')    = {fmt_linear(2,-3,'x')}")
    print(f"  fmt_quad(1,-3,2,'x')    = {fmt_quad(1,-3,2,'x')}")
    print(f"  fmt_vertex(2,3,-1,'x')  = {fmt_vertex(2,3,-1,'x')}")
    print(f"  fmt_factored(1,2,-3)    = {fmt_factored(1,2,-3)}")

    print("\n── steps() builder ───────────────────────────────────────")
    sol = steps(
        r"x^2 = (\sqrt{3})^2 + (\sqrt{13})^2",
        r"x^2 = 3 + 13 = 16",
        r"x = \sqrt{16} = 4",
    )
    print(f"  {sol}")

    print("\n── Utilities ─────────────────────────────────────────────")
    print(f"  ri(2,8)         = {ri(2,8)}")
    print(f"  rc()            = {rc()}")
    print(f"  rand_side()     = {rand_side()}")
    print(f"  rand_verts(3)   = {rand_verts(3)}")
    print(f"  sign_str(-4)    = {sign_str(-4)}")
    print(f"  sign_term(-3,'x',2) = {sign_term(-3,'x',2)}")

    print("\n✓ All components working.")
