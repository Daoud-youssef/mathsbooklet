"""
generators/indices.py
======================
Single source of truth for ALL indices/exponent exercises.
Covers the full exercise bank from Corbettmaths, MathsGenie,
KutaSoftware, and scanned worksheets.

YAML controls everything — never edit this file for content changes.

Usage:
    from generators.indices import generate

    # Static (fixed numbers)
    data = generate(types=["multiply_simple", "divide_simple"], seed=42, count=6)

    # Dynamic (random)
    data = generate(types=["multiply_simple"], seed=None, count=6)

    # CLI
    python indices.py --types multiply_simple divide_simple --seed 42 --count 6 --pretty
"""

import random
import math
import json
from datetime import date


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

VARIABLES  = ["a", "b", "c", "m", "n", "x", "y", "k", "p", "t", "w"]
PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")

def ri(a, b):
    """Random integer between a and b inclusive."""
    return random.randint(a, b)

def rc(exclude=None):
    """Random variable letter, optionally excluding one."""
    pool = [v for v in VARIABLES if v != exclude]
    return random.choice(pool)

def coeff(low=2, high=9):
    """Random coefficient."""
    return ri(low, high)

def exp(low=2, high=8):
    """Random positive exponent."""
    return ri(low, high)

def neg_exp(low=-5, high=-1):
    """Random negative exponent."""
    return ri(low, high)

def fmt_exp(base, power):
    """Format base^power as LaTeX."""
    if power == 0:
        return "1"
    if power == 1:
        return f"{base}"
    return f"{base}^{{{power}}}"

def fmt_term(coef, base, power):
    """Format coefficient × base^power as LaTeX."""
    c = "" if coef == 1 else str(coef)
    if power == 0:
        return str(coef)
    if power == 1:
        return f"{c}{base}"
    return f"{c}{base}^{{{power}}}"

def fmt_frac(num_latex, den_latex):
    """Format LaTeX fraction."""
    return f"\\dfrac{{{num_latex}}}{{{den_latex}}}"

def _part(question_latex, answer_latex, solution_latex, answer_plain="",
          is_word=False, is_wide=False):
    """Standard part dict."""
    return {
        "question_latex":  question_latex,
        "answer_latex":    answer_latex,
        "answer":          answer_plain or answer_latex,
        "solution_latex":  solution_latex,
        "is_word":         is_word,
        "is_wide":         is_wide,
    }

def _exercise(number, title, instruction, parts, ex_type,
              skill, difficulty, subtopic, lt):
    """Standard exercise dict."""
    labeled = []
    for i, p in enumerate(parts):
        p = dict(p)
        p["label"] = PART_LABELS[i]
        labeled.append(p)
    return {
        "number":      number,
        "title":       title,
        "instruction": instruction,
        "parts":       labeled,
        "meta": {
            "type":       ex_type,
            "skill":      skill,
            "difficulty": difficulty,
            "topic":      "Indices",
            "subtopic":   subtopic,
            "lt":         lt,
            "unit":       "Unit 1: Operations",
            "curriculum": "MYP5",
        }
    }


# ══════════════════════════════════════════════════════════════════
# LT1 — MULTIPLICATION (add powers)
# ══════════════════════════════════════════════════════════════════

def gen_multiply_simple():
    """a^m × a^n = a^(m+n)  — no coefficients."""
    v   = rc()
    m   = exp(2, 7)
    n   = exp(2, 7)
    ans = m + n
    q   = f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}"
    a   = fmt_exp(v, ans)
    sol = f"{v}^{{{m}}} \\times {v}^{{{n}}} = {v}^{{{m}+{n}}} = {a}"
    return _part(q, a, sol, f"{v}^{ans}")


def gen_multiply_three_terms():
    """a^m × a^n × a^p = a^(m+n+p)."""
    v      = rc()
    m, n, p = exp(2,6), exp(2,6), exp(2,6)
    ans    = m + n + p
    q   = (f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)} "
           f"\\times {fmt_exp(v,p)}")
    a   = fmt_exp(v, ans)
    sol = f"{v}^{{{m}+{n}+{p}}} = {a}"
    return _part(q, a, sol, f"{v}^{ans}")


def gen_multiply_coefficients():
    """ca^m × da^n = (cd)a^(m+n)."""
    v    = rc()
    c1   = coeff(2, 6)
    c2   = coeff(2, 6)
    m    = exp(2, 7)
    n    = exp(2, 7)
    ca   = c1 * c2
    ea   = m + n
    q    = f"{fmt_term(c1,v,m)} \\times {fmt_term(c2,v,n)}"
    a    = fmt_term(ca, v, ea)
    sol  = f"\\text{{Coefficients: }}{c1} \\times {c2} = {ca},\\quad {v}^{{{m}+{n}}} = {v}^{{{ea}}}"
    return _part(q, a, sol, f"{ca}{v}^{ea}")


def gen_multiply_multivariable():
    """ca^m b^p × da^n b^q = (cd)a^(m+n) b^(p+q)."""
    v1 = rc()
    v2 = rc(exclude=v1)
    c1, c2 = coeff(2,5), coeff(2,5)
    m, n   = exp(2,5), exp(2,5)
    p, q   = exp(1,4), exp(1,4)
    ca = c1 * c2
    ea = m + n
    eb = p + q
    q_str = (f"{fmt_term(c1,v1,m)}{fmt_exp(v2,p)} "
             f"\\times {fmt_term(c2,v1,n)}{fmt_exp(v2,q)}")
    a_str = f"{fmt_term(ca,v1,ea)}{fmt_exp(v2,eb)}"
    sol   = (f"{c1} \\times {c2}={ca},\\quad "
             f"{v1}^{{{m}+{n}}}={v1}^{{{ea}}},\\quad "
             f"{v2}^{{{p}+{q}}}={v2}^{{{eb}}}")
    return _part(q_str, a_str, sol)


# ══════════════════════════════════════════════════════════════════
# LT2 — DIVISION (subtract powers)
# ══════════════════════════════════════════════════════════════════

def gen_divide_simple():
    """a^m ÷ a^n = a^(m-n)  — no coefficients."""
    v   = rc()
    n   = exp(2, 5)
    m   = n + ri(1, 6)       # ensure m > n for positive result
    ans = m - n
    q   = f"{fmt_exp(v,m)} \\div {fmt_exp(v,n)}"
    a   = fmt_exp(v, ans)
    sol = f"{v}^{{{m}-{n}}} = {a}"
    return _part(q, a, sol, f"{v}^{ans}")


def gen_divide_coefficients():
    """ca^m ÷ da^n — divide coefficients, subtract powers."""
    v   = rc()
    n   = exp(2, 5)
    m   = n + ri(1, 5)
    # Pick c1, c2 so c1/c2 is integer
    c2  = random.choice([2, 3, 4, 5, 6])
    c1  = c2 * ri(2, 5)
    cr  = c1 // c2
    er  = m - n
    q   = f"{fmt_term(c1,v,m)} \\div {fmt_term(c2,v,n)}"
    a   = fmt_term(cr, v, er)
    sol = (f"\\text{{Coefficients: }}\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad "
           f"{v}^{{{m}-{n}}}={v}^{{{er}}}")
    return _part(q, a, sol)


def gen_divide_multivariable():
    """ca^m b^p ÷ da^n b^q."""
    v1 = rc()
    v2 = rc(exclude=v1)
    n1, n2 = exp(1,4), exp(1,3)
    m1 = n1 + ri(1,4)
    m2 = n2 + ri(0,3)
    c2 = random.choice([2,3,4])
    c1 = c2 * ri(2,4)
    cr = c1 // c2
    e1 = m1 - n1
    e2 = m2 - n2
    q  = fmt_frac(
        f"{fmt_term(c1,v1,m1)}{fmt_exp(v2,m2)}",
        f"{fmt_term(c2,v1,n1)}{fmt_exp(v2,n2)}"
    )
    a  = f"{fmt_term(cr,v1,e1)}{fmt_exp(v2,e2)}"
    sol = (f"\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad "
           f"{v1}^{{{m1}-{n1}}}={v1}^{{{e1}}},\\quad "
           f"{v2}^{{{m2}-{n2}}}={v2}^{{{e2}}}")
    return _part(q, a, sol)


# ══════════════════════════════════════════════════════════════════
# LT3 — POWER OF A POWER
# ══════════════════════════════════════════════════════════════════

def gen_power_simple():
    """(a^m)^n = a^(mn)  — no coefficient."""
    v   = rc()
    m   = exp(2, 6)
    n   = exp(2, 5)
    ans = m * n
    q   = f"({fmt_exp(v,m)})^{{{n}}}"
    a   = fmt_exp(v, ans)
    sol = f"{v}^{{{m} \\times {n}}} = {a}"
    return _part(q, a, sol, f"{v}^{ans}")


def gen_power_coefficient():
    """(ca^m)^n = c^n × a^(mn)."""
    v   = rc()
    c   = coeff(2, 5)
    m   = exp(2, 5)
    n   = exp(2, 4)
    cn  = c ** n
    en  = m * n
    q   = f"({fmt_term(c,v,m)})^{{{n}}}"
    a   = fmt_term(cn, v, en)
    sol = f"{c}^{{{n}}}={cn},\\quad {v}^{{{m} \\times {n}}}={v}^{{{en}}}"
    return _part(q, a, sol)


def gen_power_multivariable():
    """(ca^m b^p)^n = c^n a^(mn) b^(pn)."""
    v1 = rc()
    v2 = rc(exclude=v1)
    c  = coeff(2, 4)
    m  = exp(1, 4)
    p  = exp(1, 4)
    n  = exp(2, 3)
    cn = c ** n
    en1 = m * n
    en2 = p * n
    q   = f"({fmt_term(c,v1,m)}{fmt_exp(v2,p)})^{{{n}}}"
    a   = f"{fmt_term(cn,v1,en1)}{fmt_exp(v2,en2)}"
    sol = (f"{c}^{{{n}}}={cn},\\quad "
           f"{v1}^{{{m}\\times{n}}}={v1}^{{{en1}}},\\quad "
           f"{v2}^{{{p}\\times{n}}}={v2}^{{{en2}}}")
    return _part(q, a, sol)


def gen_power_negative_outer():
    """(ca^m)^(-n) — negative outer power → result with positive exponents."""
    v   = rc()
    c   = coeff(2, 4)
    m   = exp(2, 4)
    n   = ri(1, 3)
    cn  = c ** n
    en  = m * n
    q   = f"({fmt_term(c,v,m)})^{{-{n}}}"
    a   = fmt_frac("1", fmt_term(cn, v, en))
    sol = f"\\dfrac{{1}}{{{c}^{{{n}}}{v}^{{{m}\\times{n}}}}} = \\dfrac{{1}}{{{fmt_term(cn,v,en)}}}"
    return _part(q, a, sol)


# ══════════════════════════════════════════════════════════════════
# LT5 — NEGATIVE INDICES
# ══════════════════════════════════════════════════════════════════

def gen_negative_evaluate():
    """Evaluate a^(-n) as fraction."""
    base = random.choice([2, 3, 4, 5, 7, 10])
    n    = ri(1, 4)
    val  = base ** n
    q    = fmt_exp(str(base), -n)
    a    = fmt_frac("1", str(val))
    sol  = f"{base}^{{-{n}}} = \\dfrac{{1}}{{{base}^{{{n}}}}} = \\dfrac{{1}}{{{val}}}"
    return _part(q, a, sol, f"1/{val}")


def gen_negative_fraction_base():
    """(a/b)^(-n) = (b/a)^n."""
    pairs = [(2,3),(3,5),(2,5),(3,4),(4,5)]
    a, b  = random.choice(pairs)
    n     = ri(1, 3)
    # answer numerator and denominator
    an = b ** n
    ad = a ** n
    q  = f"\\left(\\dfrac{{{a}}}{{{b}}}\\right)^{{-{n}}}"
    if n == 1:
        ans = fmt_frac(str(b), str(a))
        sol = f"\\text{{Flip: }}\\left(\\dfrac{{{b}}}{{{a}}}\\right)^{{{n}}} = \\dfrac{{{an}}}{{{ad}}}"
    else:
        ans = fmt_frac(str(an), str(ad))
        sol = (f"\\text{{Flip and raise: }}"
               f"\\left(\\dfrac{{{b}}}{{{a}}}\\right)^{{{n}}} = "
               f"\\dfrac{{{b}^{{{n}}}}}{{{a}^{{{n}}}}} = \\dfrac{{{an}}}{{{ad}}}")
    return _part(q, ans, sol, f"{an}/{ad}")


def gen_negative_simplify():
    """Simplify expression with negative indices e.g. w³ × w⁻⁵."""
    v  = rc()
    m  = exp(2, 6)
    n  = neg_exp(-5, -1)
    an = m + n
    q  = f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}"
    a  = fmt_exp(v, an)
    sol = f"{v}^{{{m}+({n})}} = {a}"
    return _part(q, a, sol, f"{v}^{an}")


def gen_negative_divide_to_negative():
    """a^m ÷ a^n where result is negative index."""
    v = rc()
    m = exp(2, 5)
    n = m + ri(1, 4)      # n > m so result is negative
    an = m - n
    q  = f"{fmt_exp(v,m)} \\div {fmt_exp(v,n)}"
    a  = fmt_exp(v, an)
    sol = f"{v}^{{{m}-{n}}} = {a}"
    return _part(q, a, sol, f"{v}^{an}")


# ══════════════════════════════════════════════════════════════════
# LT6 — FRACTIONAL INDICES
# ══════════════════════════════════════════════════════════════════

def gen_fractional_unit():
    """a^(1/n) = nth root of a — unit fraction only."""
    # Curated perfect powers so answer is integer
    options = [
        (4,   2, 2),    # 4^(1/2) = 2
        (9,   2, 3),    # 9^(1/2) = 3
        (16,  2, 4),    # 16^(1/2) = 4
        (25,  2, 5),
        (36,  2, 6),
        (49,  2, 7),
        (64,  2, 8),
        (100, 2, 10),
        (8,   3, 2),    # 8^(1/3) = 2
        (27,  3, 3),
        (64,  3, 4),
        (125, 3, 5),
        (16,  4, 2),    # 16^(1/4) = 2
        (81,  4, 3),
        (32,  5, 2),    # 32^(1/5) = 2
    ]
    base, n, ans = random.choice(options)
    q   = f"{base}^{{\\frac{{1}}{{{n}}}}}"
    a   = str(ans)
    sol = f"\\sqrt[{n}]{{{base}}} = {ans}"
    return _part(q, a, sol, a)


def gen_fractional_nonunit():
    """a^(m/n) = (nth root of a)^m — non-unit fraction."""
    options = [
        (4,   3, 2, 8),       # 4^(3/2) = 8
        (8,   2, 3, 4),       # 8^(2/3) = 4
        (27,  2, 3, 9),       # 27^(2/3) = 9
        (16,  3, 2, 64),      # 16^(3/2) = 64
        (16,  3, 4, 8),       # 16^(3/4) = 8
        (25,  3, 2, 125),     # 25^(3/2) = 125
        (64,  2, 3, 16),      # 64^(2/3) = 16
        (32,  3, 5, 8),       # 32^(3/5) = 8
        (100, 3, 2, 1000),    # 100^(3/2) = 1000
        (10000, 3, 4, 1000),  # 10000^(3/4) = 1000
        (125, 2, 3, 25),      # 125^(2/3) = 25
        (9,   3, 2, 27),      # 9^(3/2) = 27
    ]
    base, m, n, ans = random.choice(options)
    q   = f"{base}^{{\\frac{{{m}}}{{{n}}}}}"
    a   = str(ans)
    sol = (f"\\left(\\sqrt[{n}]{{{base}}}\\right)^{{{m}}} "
           f"= {round(base**(1/n))}^{{{m}}} = {ans}")
    return _part(q, a, sol, a)


def gen_fractional_negative():
    """a^(-m/n) = 1 / a^(m/n)."""
    options = [
        (49,  1, 2, "1/7"),
        (81,  3, 4, "1/27"),
        (16,  1, 2, "1/4"),
        (27,  1, 3, "1/3"),
        (32, -4, 5, "1/16"),
        (25,  1, 2, "1/5"),
        (64,  1, 3, "1/4"),
    ]
    base, m, n, ans_str = random.choice(options)
    neg_m = -abs(m)
    q   = f"{base}^{{\\frac{{{neg_m}}}{{{n}}}}}"
    a   = ans_str
    sol = f"\\dfrac{{1}}{{{base}^{{\\frac{{{abs(m)}}}{{{n}}}}}}} = {ans_str}"
    return _part(q, a, sol, ans_str)


def gen_fractional_of_fraction():
    """(a/b)^(m/n)."""
    options = [
        ("16/25", 1, 2, "4/5"),
        ("9/25",  3, 2, "27/125"),
        ("27/1000", 2, 3, "9/100"),
        ("4/9",   1, 2, "2/3"),
        ("8/27",  2, 3, "4/9"),
    ]
    frac_str, m, n, ans = random.choice(options)
    num, den = frac_str.split("/")
    q   = f"\\left(\\dfrac{{{num}}}{{{den}}}\\right)^{{\\frac{{{m}}}{{{n}}}}}"
    a   = ans
    sol = (f"\\sqrt[{n}]{{\\dfrac{{{num}}}{{{den}}}}}^{{{m}}} = {ans}")
    return _part(q, a, sol, ans)


# ══════════════════════════════════════════════════════════════════
# LT7 — ZERO INDEX
# ══════════════════════════════════════════════════════════════════

def gen_zero_index():
    """a^0 = 1."""
    options = [
        ("any base", "1"),
    ]
    base = random.choice([rc(), str(ri(2,9)), f"{ri(2,5)}{rc()}"])
    q   = fmt_exp(base, 0)
    a   = "1"
    sol = f"{base}^{{0}} = 1 \\quad \\text{{(any non-zero base to power 0 = 1)}}"
    return _part(q, a, sol, "1")


# ══════════════════════════════════════════════════════════════════
# LT8 — COMPLEX FRACTIONS
# ══════════════════════════════════════════════════════════════════

def gen_fraction_simple():
    """(a^m × a^n) / a^p — simplify."""
    v    = rc()
    m    = exp(2, 6)
    n    = exp(2, 5)
    top  = m + n
    p    = ri(1, top - 1)      # ensure positive result
    ans  = top - p
    num  = f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}"
    den  = fmt_exp(v, p)
    q    = fmt_frac(num, den)
    a    = fmt_exp(v, ans)
    sol  = f"{v}^{{{m}+{n}-{p}}} = {v}^{{{ans}}}"
    return _part(q, a, sol, f"{v}^{ans}")


def gen_fraction_complex():
    """(ca^m × da^n) / (ea^p) — coefficients + multiple index laws."""
    v    = rc()
    m, n = exp(2,5), exp(2,4)
    top_e = m + n
    p    = ri(1, top_e - 1)
    ans_e = top_e - p
    # coefficients that divide cleanly
    c2   = random.choice([2,3,4,6])
    c1   = c2 * ri(2,4)
    c3   = ri(2,4)
    top_c = c1 * c3 // c2   # may not be integer — keep simple
    c1   = c2 * c3           # ensure divisible
    top_c = c1 // c2 * c3
    top_c = c3
    # simpler: just two coefficients
    ca   = random.choice([2,3,4])
    cb   = random.choice([2,3,4])
    cc   = ca * cb
    cd   = random.choice([f for f in range(2, cc+1) if cc % f == 0])
    cr   = cc // cd
    num  = f"{fmt_term(ca,v,m)} \\times {fmt_term(cb,v,n)}"
    den  = fmt_term(cd, v, p)
    q    = fmt_frac(num, den)
    a    = fmt_term(cr, v, ans_e)
    sol  = (f"\\text{{Num: }}{ca}\\times{cb}={cc},\\;{v}^{{{m}+{n}}}={v}^{{{top_e}}}"
            f"\\quad\\text{{Result: }}\\dfrac{{{cc}}}{{{cd}}}={cr},\\;{v}^{{{top_e}-{p}}}={v}^{{{ans_e}}}")
    return _part(q, a, sol)


def gen_fraction_multivariable():
    """ca^m b^p / da^n b^q — multi-variable fraction."""
    v1 = rc()
    v2 = rc(exclude=v1)
    n1, n2 = exp(1,4), exp(1,3)
    m1 = n1 + ri(1,4)
    m2 = n2 + ri(1,3)
    c2 = random.choice([2,3,4])
    c1 = c2 * ri(2,4)
    cr = c1 // c2
    e1 = m1 - n1
    e2 = m2 - n2
    num = f"{fmt_term(c1,v1,m1)}{fmt_exp(v2,m2)}"
    den = f"{fmt_term(c2,v1,n1)}{fmt_exp(v2,n2)}"
    q   = fmt_frac(num, den)
    a   = f"{fmt_term(cr,v1,e1)}{fmt_exp(v2,e2)}"
    sol = (f"\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad "
           f"{v1}^{{{m1}-{n1}}}={v1}^{{{e1}}},\\quad "
           f"{v2}^{{{m2}-{n2}}}={v2}^{{{e2}}}")
    return _part(q, a, sol)


def gen_fraction_nested_power():
    """a^m × (a^n)^p / a^q — nested power inside fraction."""
    v    = rc()
    m    = exp(2, 5)
    n    = exp(2, 4)
    p    = exp(2, 3)
    np_  = n * p
    top  = m + np_
    q_   = ri(1, top - 1)
    ans  = top - q_
    num  = f"{fmt_exp(v,m)} \\times ({fmt_exp(v,n)})^{{{p}}}"
    den  = fmt_exp(v, q_)
    q    = fmt_frac(num, den)
    a    = fmt_exp(v, ans)
    sol  = (f"({v}^{{{n}}})^{{{p}}}={v}^{{{np_}}},\\quad "
            f"{v}^{{{m}}}\\times{v}^{{{np_}}}={v}^{{{top}}},\\quad "
            f"{v}^{{{top}-{q_}}}={a}")
    return _part(q, a, sol, f"{v}^{ans}")


# ══════════════════════════════════════════════════════════════════
# LT9 — NUMERIC INDEX LAWS
# ══════════════════════════════════════════════════════════════════

def gen_numeric_multiply():
    """2^m × 2^n = 2^? — numeric base."""
    base = random.choice([2, 3, 5])
    m    = ri(2, 6)
    n    = ri(2, 6)
    ans  = m + n
    q    = f"{base}^{{{m}}} \\times {base}^{{{n}}}"
    a    = f"{base}^{{{ans}}}"
    sol  = f"{base}^{{{m}+{n}}} = {base}^{{{ans}}}"
    return _part(q, a, sol, f"{base}^{ans}")


def gen_numeric_divide():
    """2^m ÷ 2^n — numeric base."""
    base = random.choice([2, 3, 5])
    n    = ri(2, 5)
    m    = n + ri(1, 5)
    ans  = m - n
    q    = f"{base}^{{{m}}} \\div {base}^{{{n}}}"
    a    = f"{base}^{{{ans}}}"
    sol  = f"{base}^{{{m}-{n}}} = {base}^{{{ans}}}"
    return _part(q, a, sol, f"{base}^{ans}")


def gen_numeric_mixed():
    """More complex numeric: 2^9 × 2^(-2) / 2^3."""
    base = random.choice([2, 3, 5])
    m    = ri(4, 9)
    n    = neg_exp(-3, -1)
    p    = ri(1, 4)
    ans  = m + n - p
    num  = f"{base}^{{{m}}} \\times {base}^{{{n}}}"
    den  = f"{base}^{{{p}}}"
    q    = fmt_frac(num, den)
    a    = f"{base}^{{{ans}}}"
    sol  = f"{base}^{{{m}+({n})-{p}}} = {base}^{{{ans}}}"
    return _part(q, a, sol, f"{base}^{ans}")


# ══════════════════════════════════════════════════════════════════
# LT10 — WRITE AS POWER OF N
# ══════════════════════════════════════════════════════════════════

def gen_write_as_power():
    """Express a number as a power of given base."""
    options = [
        # (expression_latex, base, answer_latex, answer_plain)
        ("4",    2, "2^{2}", "2^2"),
        ("8",    2, "2^{3}", "2^3"),
        ("32",   2, "2^{5}", "2^5"),
        ("16",   2, "2^{4}", "2^4"),
        ("64",   2, "2^{6}", "2^6"),
        ("\\frac{1}{2}", 2, "2^{-1}", "2^(-1)"),
        ("\\frac{1}{4}", 2, "2^{-2}", "2^(-2)"),
        ("5",    5, "5^{1}", "5^1"),
        ("25",   5, "5^{2}", "5^2"),
        ("125",  5, "5^{3}", "5^3"),
        ("625",  5, "5^{4}", "5^4"),
        ("1",    5, "5^{0}", "5^0"),
        ("\\frac{1}{5}", 5, "5^{-1}", "5^(-1)"),
        ("9",    3, "3^{2}", "3^2"),
        ("27",   3, "3^{3}", "3^3"),
        ("81",   3, "3^{4}", "3^4"),
        ("\\frac{1}{3}", 3, "3^{-1}", "3^(-1)"),
        ("1000", 10, "10^{3}", "10^3"),
        ("100",  10, "10^{2}", "10^2"),
    ]
    expr, base, a_latex, a_plain = random.choice(options)
    q   = f"\\text{{Write }} {expr} \\text{{ as a power of }} {base}"
    sol = f"{expr} = {a_latex}"
    return _part(q, a_latex, sol, a_plain, is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT11 — FIND MISSING INDEX
# ══════════════════════════════════════════════════════════════════

def gen_find_missing_index():
    """p^m × p^? = p^n — solve for missing exponent."""
    v    = rc()
    ans  = ri(2, 7)
    m    = ri(2, 7)
    total = m + ans
    # present as: v^m × v^□ = v^total
    q   = f"{fmt_exp(v,m)} \\times {v}^{{\\square}} = {fmt_exp(v,total)}"
    a   = str(ans)
    sol = f"{v}^{{{m}}} \\times {v}^{{\\square}} = {v}^{{{total}}} \\Rightarrow \\square = {total} - {m} = {ans}"
    return _part(q, a, sol, a, is_wide=True)


def gen_find_missing_divide():
    """p^m / p^□ = p^n."""
    v    = rc()
    ans  = ri(1, 5)
    total = ri(ans+1, ans+6)
    m    = total + ans
    q   = f"\\dfrac{{{fmt_exp(v,m)}}}{{{v}^{{\\square}}}} = {fmt_exp(v,total)}"
    a   = str(ans)
    sol = f"{v}^{{{m}-\\square}} = {v}^{{{total}}} \\Rightarrow \\square = {m} - {total} = {ans}"
    return _part(q, a, sol, a, is_wide=True)


def gen_find_missing_power():
    """(v^m)^□ = v^n."""
    v   = rc()
    m   = ri(2, 5)
    ans = ri(2, 4)
    total = m * ans
    q   = f"({fmt_exp(v,m)})^{{\\square}} = {fmt_exp(v,total)}"
    a   = str(ans)
    sol = f"{v}^{{{m} \\times \\square}} = {v}^{{{total}}} \\Rightarrow \\square = {total} \\div {m} = {ans}"
    return _part(q, a, sol, a, is_wide=True)


# ══════════════════════════════════════════════════════════════════
# LT11 — IDENTIFY ERRORS (Reasoning)
# ══════════════════════════════════════════════════════════════════

def gen_identify_error():
    """Student made a mistake — identify and correct it."""
    errors = [
        {
            "question_latex":  (r"y^8 \times y^3 = y^{24}\text{. "
                                r"Explain the mistake.}"),
            "answer_latex":    (r"\text{Powers should be added, not multiplied. "
                                r"Correct: } y^{8+3} = y^{11}"),
            "answer":          "Powers added not multiplied. y^11",
            "solution_latex":  (r"\text{Index law: } a^m \times a^n = a^{m+n}"
                                r"\text{, not } a^{mn}"),
            "is_word":         True,
            "is_wide":         True,
        },
        {
            "question_latex":  (r"9^{-2} = -81\text{. Is this correct? Explain.}"),
            "answer_latex":    (r"\text{No. } 9^{-2} = \dfrac{1}{9^2} = \dfrac{1}{81}"),
            "answer":          "No. 9^(-2) = 1/81",
            "solution_latex":  (r"a^{-n} = \dfrac{1}{a^n} \text{, never negative}"),
            "is_word":         True,
            "is_wide":         True,
        },
        {
            "question_latex":  (r"27^{\frac{1}{3}} = 9"
                                r"\text{ (claim: } \frac{1}{3} \text{ of } 27 = 9\text{). Correct?}"),
            "answer_latex":    (r"\text{No. } 27^{\frac{1}{3}} = \sqrt[3]{27} = 3"),
            "answer":          "No. Cube root of 27 = 3",
            "solution_latex":  (r"a^{\frac{1}{n}} = \sqrt[n]{a}"
                                r"\text{, not } \frac{1}{n} \times a"),
            "is_word":         True,
            "is_wide":         True,
        },
    ]
    return random.choice(errors)

def gen_combine_same_power():
    """
    Write as a single power using aⁿ × bⁿ = (ab)ⁿ.

    e.g.  4 × 9 = 2² × 3² = (2×3)² = 6²

    Student must:
      1. Recognise each number as a perfect power
      2. Express both with the SAME exponent
      3. Combine bases by multiplying: (a×b)ⁿ
    """
    options = [
        # (num1, base1, num2, base2, power, combined_base, final_value)
        (4,   2,  9,   3,  2,  6,   36),
        (8,   2,  27,  3,  3,  6,   216),
        (4,   2,  25,  5,  2,  10,  100),
        (8,   2,  125, 5,  3,  10,  1000),
        (4,   2,  49,  7,  2,  14,  196),
        (8,   2,  343, 7,  3,  14,  2744),
        (25,  5,  49,  7,  2,  35,  1225),
        (27,  3,  125, 5,  3,  15,  3375),
        (16,  2,  81,  3,  4,  6,   1296),
        (9,   3,  25,  5,  2,  15,  225),
        (32,  2,  243, 3,  5,  6,   7776),
    ]
    n1, b1, n2, b2, pw, cb, cv = random.choice(options)

    q   = f"{n1} \\times {n2}"
    a   = f"{cb}^{{{pw}}}"
    sol = (
        f"{n1} \\times {n2}"
        f" = {b1}^{{{pw}}} \\times {b2}^{{{pw}}}"
        f" = ({b1} \\times {b2})^{{{pw}}}"
        f" = {cb}^{{{pw}}}"
        f" = {cv}"
    )
    return _part(q, a, sol, f"{cb}^{pw} = {cv}", is_wide=True)
# ══════════════════════════════════════════════════════════════════
# REGISTRY — maps YAML type names to generator functions
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    # LT1 — Multiplication
    "multiply_simple":           gen_multiply_simple,
    "multiply_three_terms":      gen_multiply_three_terms,
    "multiply_coefficients":     gen_multiply_coefficients,
    "multiply_multivariable":    gen_multiply_multivariable,

    # LT2 — Division
    "divide_simple":             gen_divide_simple,
    "divide_coefficients":       gen_divide_coefficients,
    "divide_multivariable":      gen_divide_multivariable,


    # LT3 — Power of a power
    "power_simple":              gen_power_simple,
    "power_coefficient":         gen_power_coefficient,
    "power_multivariable":       gen_power_multivariable,
    "power_negative_outer":      gen_power_negative_outer,
    "combine_same_power": gen_combine_same_power,
    # LT5 — Negative indices
    "negative_evaluate":         gen_negative_evaluate,
    "negative_fraction_base":    gen_negative_fraction_base,
    "negative_simplify":         gen_negative_simplify,
    "negative_divide":           gen_negative_divide_to_negative,

    # LT6 — Fractional indices
    "fractional_unit":           gen_fractional_unit,
    "fractional_nonunit":        gen_fractional_nonunit,
    "fractional_negative":       gen_fractional_negative,
    "fractional_of_fraction":    gen_fractional_of_fraction,

    # LT7 — Zero index
    "zero_index":                gen_zero_index,

    # LT8 — Complex fractions
    "fraction_simple":           gen_fraction_simple,
    "fraction_complex":          gen_fraction_complex,
    "fraction_multivariable":    gen_fraction_multivariable,
    "fraction_nested_power":     gen_fraction_nested_power,

    # LT9 — Numeric index laws
    "numeric_multiply":          gen_numeric_multiply,
    "numeric_divide":            gen_numeric_divide,
    "numeric_mixed":             gen_numeric_mixed,

    # LT10 — Write as power of n
    "write_as_power":            gen_write_as_power,

    # LT11 — Find missing index
    "find_missing_index":        gen_find_missing_index,
    "find_missing_divide":       gen_find_missing_divide,
    "find_missing_power":        gen_find_missing_power,

    # Reasoning
    "identify_error":            gen_identify_error,
}

# ══════════════════════════════════════════════════════════════════
# EXERCISE METADATA CATALOGUE
# ══════════════════════════════════════════════════════════════════
# Each entry is a complete AI-readable profile for one exercise type.
# Used by:
#   - Book renderer      → difficulty badge, instruction, subtopic
#   - Adaptive platform  → prerequisites, remediation, sequencing
#   - AI tutor (Flint)   → strategy, common errors, hints
#   - Analytics engine   → skill tags, learning target mapping
#
# Schema per entry:
#   subtopic        : human-readable name
#   difficulty      : easy | medium | hard
#   bloom           : remember | understand | apply | analyse | evaluate | create
#   lt              : learning target(s) this exercise addresses
#   prerequisites   : list of exercise types student must master first
#   skills          : flat list of skill tags for competency tracking
#   strategy        : step-by-step solving strategy (AI can read to give hints)
#   common_errors   : list of typical mistakes students make
#   remediation     : which type to fall back to if student struggles
#   instruction     : default instruction shown to student
#   flint_prompt    : suggested Flint AI activity prompt for this type
# ══════════════════════════════════════════════════════════════════

METADATA = {

    "multiply_simple": {
        "subtopic":      "Multiplication Rule",
        "difficulty":    "easy",
        "bloom":         "remember",
        "lt":            ["LT1"],
        "prerequisites": [],
        "skills": [
            "index_notation",
            "same_base_identification",
            "addition_of_integers",
        ],
        "strategy": [
            "1. Confirm both terms have the same base.",
            "2. Keep the base unchanged.",
            "3. Add the exponents: a^m × a^n = a^(m+n).",
            "4. Write the simplified result.",
        ],
        "common_errors": [
            "Multiplying exponents instead of adding (a^3 × a^4 = a^12 ✗).",
            "Multiplying the bases as well (a^3 × a^4 = a²^7 ✗).",
            "Forgetting that a = a^1 when one term has no visible power.",
        ],
        "remediation":   None,
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Guide the student to simplify expressions like a^3 × a^4 using "
            "the multiplication index law. Never give the answer. Ask: what do "
            "we do with the powers when the bases are the same?"
        ),
    },

    "multiply_three_terms": {
        "subtopic":      "Multiplication Rule — Three Terms",
        "difficulty":    "easy",
        "bloom":         "understand",
        "lt":            ["LT1"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "index_notation",
            "same_base_identification",
            "addition_of_integers",
            "multi_step_simplification",
        ],
        "strategy": [
            "1. Confirm all terms share the same base.",
            "2. Add all three exponents: a^m × a^n × a^p = a^(m+n+p).",
            "3. Work left to right if it helps: (a^m × a^n) × a^p.",
        ],
        "common_errors": [
            "Only adding two of the three exponents.",
            "Multiplying exponents instead of adding.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "The student is simplifying a product of three index terms with the "
            "same base. Ask them to add the exponents one pair at a time."
        ),
    },

    "multiply_coefficients": {
        "subtopic":      "Multiplication with Coefficients",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1", "LT4"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "index_notation",
            "coefficient_multiplication",
            "addition_of_integers",
            "separating_coefficients_from_indices",
        ],
        "strategy": [
            "1. Separate coefficients from index terms.",
            "2. Multiply the coefficients together.",
            "3. Add the exponents (same base rule).",
            "4. Combine: new coefficient × base^(sum of exponents).",
        ],
        "common_errors": [
            "Adding coefficients instead of multiplying them.",
            "Applying the index law to the coefficients (e.g. 3^2 × 5^4 ✗).",
            "Forgetting to multiply coefficients at all.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Guide student through 3a² × 5a³ style questions. "
            "Ask: what do we do with the numbers out front? "
            "Then what do we do with the powers?"
        ),
    },

    "multiply_multivariable": {
        "subtopic":      "Multiplication — Multi-variable",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1", "LT4", "LT9"],
        "prerequisites": ["multiply_simple", "multiply_coefficients"],
        "skills": [
            "multi_variable_expressions",
            "coefficient_multiplication",
            "addition_of_integers",
            "grouping_like_terms",
        ],
        "strategy": [
            "1. Multiply coefficients.",
            "2. Apply index law to first variable.",
            "3. Apply index law to second variable independently.",
            "4. Combine all parts.",
        ],
        "common_errors": [
            "Mixing up exponents between different variables.",
            "Applying one variable's exponent to another.",
        ],
        "remediation":   "multiply_coefficients",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is multiplying two-variable index expressions. "
            "Ask them to handle one variable at a time."
        ),
    },

    "divide_simple": {
        "subtopic":      "Division Rule",
        "difficulty":    "easy",
        "bloom":         "remember",
        "lt":            ["LT2"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "index_notation",
            "same_base_identification",
            "subtraction_of_integers",
        ],
        "strategy": [
            "1. Confirm both terms share the same base.",
            "2. Subtract the denominator exponent from the numerator: a^m ÷ a^n = a^(m-n).",
            "3. Write the simplified result.",
        ],
        "common_errors": [
            "Dividing exponents instead of subtracting (a^8 ÷ a^2 = a^4 ✗).",
            "Subtracting in the wrong order (n - m instead of m - n).",
            "Dividing the bases as well.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Guide student through a^8 ÷ a^3 style questions. "
            "Ask: what do we do with the powers when dividing same base terms?"
        ),
    },

    "divide_coefficients": {
        "subtopic":      "Division with Coefficients",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT2", "LT4"],
        "prerequisites": ["divide_simple", "multiply_coefficients"],
        "skills": [
            "coefficient_division",
            "subtraction_of_integers",
            "separating_coefficients_from_indices",
        ],
        "strategy": [
            "1. Divide the coefficients.",
            "2. Subtract the exponents (same base rule).",
            "3. Combine result.",
        ],
        "common_errors": [
            "Subtracting coefficients instead of dividing.",
            "Applying division to exponents instead of subtraction.",
        ],
        "remediation":   "divide_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is dividing index terms with coefficients. "
            "Ask: what happens to the numbers in front? What happens to the powers?"
        ),
    },

    "divide_multivariable": {
        "subtopic":      "Division — Multi-variable",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT2", "LT4", "LT9"],
        "prerequisites": ["divide_coefficients", "multiply_multivariable"],
        "skills": [
            "multi_variable_expressions",
            "coefficient_division",
            "subtraction_of_integers",
            "grouping_like_terms",
        ],
        "strategy": [
            "1. Divide coefficients.",
            "2. Apply division law to each variable independently.",
            "3. Combine.",
        ],
        "common_errors": [
            "Mixing exponents between variables.",
            "Subtracting in wrong order for one variable.",
        ],
        "remediation":   "divide_coefficients",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is dividing multi-variable index fractions. "
            "Ask them to handle coefficients first, then each variable separately."
        ),
    },

    "power_simple": {
        "subtopic":      "Power of a Power",
        "difficulty":    "easy",
        "bloom":         "remember",
        "lt":            ["LT3"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "index_notation",
            "multiplication_of_integers",
            "power_of_power_law",
        ],
        "strategy": [
            "1. Identify the inner and outer powers.",
            "2. Multiply them: (a^m)^n = a^(m×n).",
            "3. Write result.",
        ],
        "common_errors": [
            "Adding instead of multiplying the powers ((a^3)^4 = a^7 ✗).",
            "Only keeping the outer power and ignoring the inner.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Guide student through (a^3)^4 style questions. "
            "Ask: when a power is raised to another power, what operation do we use on the indices?"
        ),
    },

    "power_coefficient": {
        "subtopic":      "Power of a Power with Coefficient",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT3", "LT4"],
        "prerequisites": ["power_simple"],
        "skills": [
            "power_of_power_law",
            "coefficient_exponentiation",
            "multiplication_of_integers",
        ],
        "strategy": [
            "1. Raise the coefficient to the outer power.",
            "2. Multiply the variable's exponents.",
            "3. Combine: (ca^m)^n = c^n × a^(mn).",
        ],
        "common_errors": [
            "Multiplying coefficient by outer power instead of raising it: (3a^2)^3 = 9a^6 ✗.",
            "Forgetting to apply outer power to the coefficient at all.",
        ],
        "remediation":   "power_simple",
        "instruction":   "Expand and simplify.",
        "flint_prompt":  (
            "Student is expanding (3a^2)^4 style expressions. Ask: "
            "the power outside the bracket applies to everything inside — "
            "what does that mean for the number 3?"
        ),
    },

    "power_multivariable": {
        "subtopic":      "Power of a Power — Multi-variable",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT3", "LT4", "LT9"],
        "prerequisites": ["power_coefficient", "multiply_multivariable"],
        "skills": [
            "power_of_power_law",
            "coefficient_exponentiation",
            "multi_variable_expressions",
        ],
        "strategy": [
            "1. Raise coefficient to outer power.",
            "2. Multiply each variable's exponent by outer power independently.",
            "3. Combine all parts.",
        ],
        "common_errors": [
            "Applying outer power to only one variable.",
            "Adding instead of multiplying exponents.",
        ],
        "remediation":   "power_coefficient",
        "instruction":   "Expand and simplify.",
        "flint_prompt":  (
            "Student is expanding multi-variable bracket powers. "
            "Ask: the outer power applies to every factor inside — go through each one."
        ),
    },

    "power_negative_outer": {
        "subtopic":      "Negative Outer Power",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT3", "LT5"],
        "prerequisites": ["power_coefficient", "negative_evaluate"],
        "skills": [
            "power_of_power_law",
            "negative_index_as_reciprocal",
            "coefficient_exponentiation",
        ],
        "strategy": [
            "1. Expand bracket ignoring negative sign: (ca^m)^n.",
            "2. Write as reciprocal due to negative outer power.",
            "3. Result: 1 / (c^n × a^(mn)).",
        ],
        "common_errors": [
            "Making the entire result negative instead of taking the reciprocal.",
            "Forgetting to apply the negative to the coefficient.",
        ],
        "remediation":   "negative_evaluate",
        "instruction":   "Simplify. Give your answer with positive exponents.",
        "flint_prompt":  (
            "Student is simplifying (2a^3)^(-2). Ask: what does a negative index mean? "
            "How does that apply when the whole bracket has a negative outer power?"
        ),
    },

    "negative_evaluate": {
        "subtopic":      "Evaluate Negative Indices",
        "difficulty":    "medium",
        "bloom":         "understand",
        "lt":            ["LT5"],
        "prerequisites": ["divide_simple"],
        "skills": [
            "negative_index_as_reciprocal",
            "integer_exponentiation",
            "fraction_notation",
        ],
        "strategy": [
            "1. Recall: a^(-n) = 1 / a^n.",
            "2. Calculate a^n.",
            "3. Write as fraction 1 / (a^n).",
        ],
        "common_errors": [
            "Making result negative: 4^(-2) = -16 ✗.",
            "Multiplying base by negative exponent: 4^(-2) = 4×(-2) = -8 ✗.",
            "Confusing (-4)^2 with 4^(-2).",
        ],
        "remediation":   "divide_simple",
        "instruction":   "Evaluate. Write as a fraction.",
        "flint_prompt":  (
            "Student is evaluating negative indices. Ask: what is the rule for "
            "a negative exponent? Can the result ever be a negative number?"
        ),
    },

    "negative_fraction_base": {
        "subtopic":      "Negative Index — Fraction Base",
        "difficulty":    "medium",
        "bloom":         "understand",
        "lt":            ["LT5"],
        "prerequisites": ["negative_evaluate"],
        "skills": [
            "negative_index_as_reciprocal",
            "fraction_reciprocal",
            "integer_exponentiation",
        ],
        "strategy": [
            "1. Negative index on a fraction = flip the fraction.",
            "2. (a/b)^(-n) = (b/a)^n.",
            "3. Evaluate the resulting positive power.",
        ],
        "common_errors": [
            "Negating the numerator only.",
            "Forgetting to flip — applying negative to both top and bottom separately.",
        ],
        "remediation":   "negative_evaluate",
        "instruction":   "Evaluate. Simplify your answer.",
        "flint_prompt":  (
            "Student is evaluating (2/3)^(-2). Ask: what do we do when a fraction "
            "has a negative exponent? What is the reciprocal of 2/3?"
        ),
    },

    "negative_simplify": {
        "subtopic":      "Simplify with Negative Indices",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1", "LT5"],
        "prerequisites": ["multiply_simple", "negative_evaluate"],
        "skills": [
            "addition_of_integers",
            "negative_integer_addition",
            "index_notation",
        ],
        "strategy": [
            "1. Apply multiplication index law: add the exponents.",
            "2. Be careful with negative exponent arithmetic.",
            "3. If result is negative, leave in index form a^(-n).",
        ],
        "common_errors": [
            "Sign errors when adding negative exponents.",
            "Making the result negative in value rather than keeping index form.",
        ],
        "remediation":   "negative_evaluate",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is simplifying w^3 × w^(-5). Ask: we still add the powers — "
            "what is 3 + (−5)?"
        ),
    },

    "negative_divide": {
        "subtopic":      "Division Giving Negative Index",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT2", "LT5"],
        "prerequisites": ["divide_simple", "negative_evaluate"],
        "skills": [
            "subtraction_of_integers",
            "negative_index_as_reciprocal",
            "index_notation",
        ],
        "strategy": [
            "1. Apply division index law: subtract exponents (m - n).",
            "2. If result is negative, the answer is a negative index.",
            "3. Leave in index form unless asked to evaluate.",
        ],
        "common_errors": [
            "Swapping order: computing n - m instead of m - n.",
            "Writing negative result as a fraction when not required.",
        ],
        "remediation":   "divide_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is dividing to get a negative index. Ask: what is m − n "
            "when n is larger than m? Is a negative index the same as a negative number?"
        ),
    },

    "fractional_unit": {
        "subtopic":      "Fractional Index — Unit Fraction",
        "difficulty":    "medium",
        "bloom":         "understand",
        "lt":            ["LT6"],
        "prerequisites": ["power_simple", "negative_evaluate"],
        "skills": [
            "fractional_index_as_root",
            "perfect_square_recognition",
            "perfect_cube_recognition",
            "nth_root_evaluation",
        ],
        "strategy": [
            "1. Recall: a^(1/n) = nth root of a.",
            "2. Identify which root is needed (denominator of fraction).",
            "3. Evaluate the root.",
        ],
        "common_errors": [
            "Dividing base by denominator: 27^(1/3) = 9 ✗ (dividing 27 by 3).",
            "Confusing square root with cube root.",
            "Not recognising perfect cubes/squares.",
        ],
        "remediation":   "power_simple",
        "instruction":   "Evaluate.",
        "flint_prompt":  (
            "Student is evaluating 64^(1/3). Ask: what does a fractional index mean? "
            "What root does 1/3 represent?"
        ),
    },

    "fractional_nonunit": {
        "subtopic":      "Fractional Index — Non-unit",
        "difficulty":    "hard",
        "bloom":         "apply",
        "lt":            ["LT6"],
        "prerequisites": ["fractional_unit"],
        "skills": [
            "fractional_index_as_root_and_power",
            "nth_root_evaluation",
            "integer_exponentiation",
            "order_of_operations",
        ],
        "strategy": [
            "1. Recall: a^(m/n) = (nth root of a)^m.",
            "2. Find the nth root first (easier with smaller numbers).",
            "3. Raise the result to the power m.",
        ],
        "common_errors": [
            "Raising to power m before taking the root (harder, rounding errors).",
            "Confusing numerator and denominator roles.",
            "Computing a^m then taking nth root — valid but error-prone.",
        ],
        "remediation":   "fractional_unit",
        "instruction":   "Evaluate.",
        "flint_prompt":  (
            "Student is evaluating 27^(2/3). Ask: which part tells us the root? "
            "Which part tells us the power? Which should we do first?"
        ),
    },

    "fractional_negative": {
        "subtopic":      "Negative Fractional Index",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT5", "LT6"],
        "prerequisites": ["fractional_nonunit", "negative_evaluate"],
        "skills": [
            "fractional_index_as_root_and_power",
            "negative_index_as_reciprocal",
            "nth_root_evaluation",
            "combining_index_laws",
        ],
        "strategy": [
            "1. Split: a^(-m/n) = 1 / a^(m/n).",
            "2. Evaluate a^(m/n): take nth root, raise to m.",
            "3. Take reciprocal.",
        ],
        "common_errors": [
            "Making result negative rather than taking reciprocal.",
            "Applying negative to the root instead of the whole expression.",
        ],
        "remediation":   "fractional_nonunit",
        "instruction":   "Evaluate.",
        "flint_prompt":  (
            "Student is evaluating 49^(-1/2). Ask: two things are happening here — "
            "what does the fractional part mean? What does the negative part mean?"
        ),
    },

    "fractional_of_fraction": {
        "subtopic":      "Fractional Index of a Fraction",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT6"],
        "prerequisites": ["fractional_nonunit", "negative_fraction_base"],
        "skills": [
            "fractional_index_as_root_and_power",
            "fraction_exponentiation",
            "nth_root_of_fraction",
        ],
        "strategy": [
            "1. Apply index to numerator and denominator separately.",
            "2. (a/b)^(m/n) = (a^(m/n)) / (b^(m/n)).",
            "3. Evaluate each part.",
        ],
        "common_errors": [
            "Only applying index to numerator.",
            "Not recognising perfect powers in numerator or denominator.",
        ],
        "remediation":   "fractional_nonunit",
        "instruction":   "Evaluate. Simplify your answer.",
        "flint_prompt":  (
            "Student is evaluating (9/25)^(3/2). Ask: can we apply the index to "
            "the top and bottom separately?"
        ),
    },

    "zero_index": {
        "subtopic":      "Zero Index",
        "difficulty":    "easy",
        "bloom":         "remember",
        "lt":            ["LT7"],
        "prerequisites": ["divide_simple"],
        "skills": [
            "zero_exponent_rule",
            "index_notation",
        ],
        "strategy": [
            "1. Recall: any non-zero base to the power 0 equals 1.",
            "2. a^0 = 1 for all a ≠ 0.",
        ],
        "common_errors": [
            "Writing a^0 = 0.",
            "Writing a^0 = a.",
            "Applying zero index to coefficient but not variable or vice versa.",
        ],
        "remediation":   None,
        "instruction":   "Evaluate.",
        "flint_prompt":  (
            "Student is evaluating expressions with zero index. Ask: "
            "what does any base to the power of zero always equal? Can you prove it using the division law?"
        ),
    },

    "fraction_simple": {
        "subtopic":      "Complex Fraction",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1", "LT2", "LT8"],
        "prerequisites": ["multiply_simple", "divide_simple"],
        "skills": [
            "combining_multiplication_and_division_laws",
            "multi_step_simplification",
            "index_notation",
        ],
        "strategy": [
            "1. Simplify the numerator: add exponents in multiplication.",
            "2. Apply division law: subtract denominator exponent.",
            "3. Single combined step: a^(m+n-p).",
        ],
        "common_errors": [
            "Forgetting to add numerator exponents before subtracting denominator.",
            "Subtracting denominator exponent from only one numerator term.",
        ],
        "remediation":   "divide_simple",
        "instruction":   "Simplify. Give your answer in index form.",
        "flint_prompt":  (
            "Student is simplifying (a^3 × a^5) / a^4. Ask: what is the first step "
            "— should we deal with the numerator or the whole fraction first?"
        ),
    },

    "fraction_complex": {
        "subtopic":      "Complex Fraction with Coefficients",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT1", "LT2", "LT4", "LT8"],
        "prerequisites": ["fraction_simple", "divide_coefficients"],
        "skills": [
            "coefficient_division",
            "combining_multiplication_and_division_laws",
            "multi_step_simplification",
            "separating_coefficients_from_indices",
        ],
        "strategy": [
            "1. Multiply numerator coefficients.",
            "2. Add numerator exponents.",
            "3. Divide combined coefficient by denominator coefficient.",
            "4. Subtract denominator exponent.",
        ],
        "common_errors": [
            "Applying coefficient division to the exponents.",
            "Losing track of multi-step order.",
            "Arithmetic errors with larger coefficients.",
        ],
        "remediation":   "fraction_simple",
        "instruction":   "Simplify fully.",
        "flint_prompt":  (
            "Student is simplifying (4a^2 × 3a^3) / 6a^4. Ask them to handle "
            "the numbers and the letters as two separate sub-problems."
        ),
    },

    "fraction_multivariable": {
        "subtopic":      "Complex Fraction — Multi-variable",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT2", "LT4", "LT8", "LT9"],
        "prerequisites": ["fraction_complex", "divide_multivariable"],
        "skills": [
            "multi_variable_expressions",
            "coefficient_division",
            "multi_step_simplification",
            "grouping_like_terms",
        ],
        "strategy": [
            "1. Handle coefficients: divide.",
            "2. Handle first variable: subtract exponents.",
            "3. Handle second variable: subtract exponents.",
            "4. Combine all three results.",
        ],
        "common_errors": [
            "Mixing exponents between variables.",
            "Subtracting exponents in wrong order.",
        ],
        "remediation":   "fraction_complex",
        "instruction":   "Simplify fully.",
        "flint_prompt":  (
            "Student is simplifying a multi-variable fraction. "
            "Ask them to treat coefficients, first variable, second variable as three separate mini-problems."
        ),
    },

    "fraction_nested_power": {
        "subtopic":      "Nested Power in Fraction",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT1", "LT2", "LT3", "LT8"],
        "prerequisites": ["fraction_simple", "power_simple"],
        "skills": [
            "power_of_power_law",
            "combining_multiplication_and_division_laws",
            "multi_step_simplification",
            "order_of_operations",
        ],
        "strategy": [
            "1. Expand the nested power first: (a^n)^p = a^(np).",
            "2. Add exponents in numerator.",
            "3. Subtract denominator exponent.",
        ],
        "common_errors": [
            "Adding instead of multiplying in the nested power step.",
            "Skipping nested power expansion and going straight to addition.",
        ],
        "remediation":   "fraction_simple",
        "instruction":   "Simplify fully.",
        "flint_prompt":  (
            "Student is simplifying a^m × (a^n)^p / a^q. Ask: which law do we apply first, "
            "and why does order matter here?"
        ),
    },

    "numeric_multiply": {
        "subtopic":      "Numeric Index Laws — Multiply",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "numeric_base_recognition",
            "addition_of_integers",
            "expressing_as_single_power",
        ],
        "strategy": [
            "1. Confirm same numeric base.",
            "2. Add exponents.",
            "3. Express as single power of that base.",
        ],
        "common_errors": [
            "Evaluating 2^5 × 2^3 = 32 × 8 = 256 instead of keeping as 2^8.",
            "Multiplying the bases: 2^3 × 2^4 = 4^7 ✗.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Simplify. Give your answer as a single power.",
        "flint_prompt":  (
            "Student is simplifying 2^5 × 2^3. Ask: do we need to calculate the "
            "actual value, or can we express it as a single power of 2?"
        ),
    },

    "numeric_divide": {
        "subtopic":      "Numeric Index Laws — Divide",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT2"],
        "prerequisites": ["divide_simple", "numeric_multiply"],
        "skills": [
            "numeric_base_recognition",
            "subtraction_of_integers",
            "expressing_as_single_power",
        ],
        "strategy": [
            "1. Confirm same numeric base.",
            "2. Subtract exponents.",
            "3. Express as single power.",
        ],
        "common_errors": [
            "Dividing exponents instead of subtracting.",
            "Evaluating numerically instead of leaving as index form.",
        ],
        "remediation":   "divide_simple",
        "instruction":   "Simplify. Give your answer as a single power.",
        "flint_prompt":  (
            "Student is simplifying 3^7 ÷ 3^2. Ask: what law applies here? "
            "Express as a single power of 3."
        ),
    },

    "numeric_mixed": {
        "subtopic":      "Numeric Index Laws — Mixed",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT1", "LT2", "LT5", "LT8"],
        "prerequisites": ["numeric_divide", "negative_evaluate"],
        "skills": [
            "numeric_base_recognition",
            "combining_multiplication_and_division_laws",
            "negative_integer_addition",
            "multi_step_simplification",
        ],
        "strategy": [
            "1. Deal with numerator: add all exponents (including negatives).",
            "2. Subtract denominator exponent.",
            "3. Express as single power.",
        ],
        "common_errors": [
            "Sign errors with negative exponents in numerator.",
            "Subtracting denominator exponent before combining numerator.",
        ],
        "remediation":   "numeric_divide",
        "instruction":   "Simplify. Give your answer as a single power.",
        "flint_prompt":  (
            "Student is working through 2^9 × 2^(-2) / 2^3. "
            "Ask: how many index laws are involved here? Take them one at a time."
        ),
    },

    "write_as_power": {
        "subtopic":      "Write as Power of n",
        "difficulty":    "medium",
        "bloom":         "understand",
        "lt":            ["LT10"],
        "prerequisites": ["multiply_simple", "negative_evaluate", "zero_index"],
        "skills": [
            "prime_factorisation",
            "index_notation",
            "negative_index_as_reciprocal",
            "zero_exponent_rule",
        ],
        "strategy": [
            "1. Identify the base.",
            "2. Express number as repeated multiplication of that base.",
            "3. Count how many times: that is the exponent.",
            "4. For fractions: use negative exponent.",
            "5. For 1: use zero exponent.",
        ],
        "common_errors": [
            "Confusing base with exponent.",
            "Writing 1 as base^1 instead of base^0.",
            "Not recognising that 1/8 = 2^(-3).",
        ],
        "remediation":   "zero_index",
        "instruction":   "Write as a single power of the given base.",
        "flint_prompt":  (
            "Student needs to write 32 as a power of 2. Ask: "
            "how many times do you multiply 2 by itself to get 32?"
        ),
    },

    "find_missing_index": {
        "subtopic":      "Find Missing Index",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT1", "LT11"],
        "prerequisites": ["multiply_simple"],
        "skills": [
            "reverse_index_law",
            "subtraction_of_integers",
            "algebraic_reasoning",
        ],
        "strategy": [
            "1. Apply the index law to set up an equation.",
            "2. For multiplication: total = known + missing → missing = total - known.",
            "3. Solve for the missing value.",
        ],
        "common_errors": [
            "Adding instead of subtracting to find missing exponent.",
            "Confusing which exponent is missing.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Find the missing index.",
        "flint_prompt":  (
            "Student is solving a^5 × a^□ = a^9. Ask: "
            "if the total power is 9 and one part is 5, how do we find the other part?"
        ),
    },

    "find_missing_divide": {
        "subtopic":      "Find Missing Index — Division",
        "difficulty":    "medium",
        "bloom":         "apply",
        "lt":            ["LT2", "LT11"],
        "prerequisites": ["divide_simple", "find_missing_index"],
        "skills": [
            "reverse_index_law",
            "subtraction_of_integers",
            "algebraic_reasoning",
        ],
        "strategy": [
            "1. Apply division law: numerator - denominator = result.",
            "2. Set up equation: m - □ = result.",
            "3. Solve: □ = m - result.",
        ],
        "common_errors": [
            "Setting up the equation backwards.",
            "Using addition instead of subtraction.",
        ],
        "remediation":   "find_missing_index",
        "instruction":   "Find the missing index.",
        "flint_prompt":  (
            "Student is solving a^8 / a^□ = a^3. Ask: "
            "what equation do the exponents satisfy here?"
        ),
    },

    "find_missing_power": {
        "subtopic":      "Find Missing Power",
        "difficulty":    "hard",
        "bloom":         "analyse",
        "lt":            ["LT3", "LT11"],
        "prerequisites": ["power_simple", "find_missing_index"],
        "skills": [
            "reverse_power_of_power_law",
            "division_of_integers",
            "algebraic_reasoning",
        ],
        "strategy": [
            "1. Apply power of power law: (a^m)^□ = a^(m×□).",
            "2. Set up: m × □ = total.",
            "3. Solve: □ = total ÷ m.",
        ],
        "common_errors": [
            "Using subtraction instead of division to find the missing power.",
            "Confusing inner and outer exponents.",
        ],
        "remediation":   "power_simple",
        "instruction":   "Find the missing power.",
        "flint_prompt":  (
            "Student is solving (a^3)^□ = a^12. Ask: "
            "if 3 times something equals 12, what is that something?"
        ),
    },
    "combine_same_power": {
        "subtopic":      "Combining Same Powers — (ab)ⁿ = aⁿ×bⁿ",
        "difficulty":    "medium",
        "bloom":         "understand",
        "lt":            ["LT3", "LT4"],
        "prerequisites": ["power_coefficient"],
        "skills":        ["prime_factorisation", "perfect_square_recognition",
                          "perfect_cube_recognition", "power_distribution_law"],
        "strategy":      ["1. Write each number as a prime power.",
                          "2. Check both have the same exponent.",
                          "3. Combine bases: aⁿ × bⁿ = (a×b)ⁿ.",
                          "4. Multiply the bases."],
        "common_errors": ["Adding bases instead of multiplying: 2²×3²=5² ✗",
                          "Not recognising numbers as perfect powers.",
                          "Trying to combine when exponents differ."],
        "remediation":   "power_coefficient",
        "instruction":   "Write as a single power by expressing each number as a prime power.",
        "flint_prompt":  "Ask: can you write 4 as a power? Can you write 9 as a power? Do they have the same exponent? What can we do when exponents match?",
    },
    "identify_error": {
        "subtopic":      "Identify and Correct Error",
        "difficulty":    "hard",
        "bloom":         "evaluate",
        "lt":            ["LT1", "LT5", "LT6"],
        "prerequisites": [
            "multiply_simple",
            "negative_evaluate",
            "fractional_unit",
        ],
        "skills": [
            "mathematical_reasoning",
            "error_analysis",
            "verbal_mathematical_explanation",
            "index_notation",
        ],
        "strategy": [
            "1. Identify which index law is being applied.",
            "2. Apply the law correctly yourself.",
            "3. Compare with the given (wrong) answer.",
            "4. Name the specific mistake made.",
            "5. Write a corrected solution.",
        ],
        "common_errors": [
            "Accepting the wrong answer without checking.",
            "Vague explanations like 'they got it wrong'.",
            "Not providing the corrected solution.",
        ],
        "remediation":   "multiply_simple",
        "instruction":   "Identify the mistake and write the correct answer.",
        "flint_prompt":  (
            "Student is analysing a wrong answer. Ask: which law is being applied here? "
            "What should the correct result be? Can you explain the mistake in one sentence?"
        ),
    },
}


# ── Convenience flat maps (kept for backwards compatibility) ──────

DIFFICULTY = {k: v["difficulty"] for k, v in METADATA.items()}
SUBTOPIC   = {k: v["subtopic"]   for k, v in METADATA.items()}




# ══════════════════════════════════════════════════════════════════
# MAIN GENERATE FUNCTION — called by YAML / Pyodide
# ══════════════════════════════════════════════════════════════════
# --------------------------
# Utility to clean skills
# --------------------------
def clean_skills(skills):
    """
    Convert ['index_notation', 'same_base_identification'] 
    → ['Index notation', 'Same base identification']
    """
    return [s.replace("_", " ").capitalize() for s in skills]

# --------------------------
# MAIN GENERATE FUNCTION
# --------------------------
def generate(types, seed=None, count=6, show_solutions=False):
    """
    Generate exercises for given types.
    """
    if seed is not None:
        random.seed(seed)

    exercises = []
    for i, ex_type in enumerate(types, 1):
        if ex_type not in REGISTRY:
            raise ValueError(
                f"Unknown type: '{ex_type}'. "
                f"Available: {sorted(REGISTRY.keys())}"
            )

        gen = REGISTRY[ex_type]
        parts = [gen() for _ in range(count)]

        for j, p in enumerate(parts):
            p["label"] = PART_LABELS[j]
            if not show_solutions:
                p.pop("solution_latex", None)

        m = METADATA.get(ex_type, {})
        # Clean skills right here
        skills_clean = clean_skills(m.get("skills", ["Index Laws"]))
        exercises.append({
            "number":      i,
            "title":       m.get("subtopic", ex_type),
            "instruction": m.get("instruction", "Simplify. Give your answer in index form."),
            "parts":       parts,
            "meta": {
                "type":          ex_type,
                "subtopic":      m.get("subtopic", ""),
                "topic":         "Indices",
                "unit":          "Unit 2: Indices",
                "curriculum":    "MYP5",
                "difficulty":    m.get("difficulty", "medium"),
                "bloom":         m.get("bloom", "apply"),
                "lt":            m.get("lt", []),
                "prerequisites": m.get("prerequisites", []),
                "skills":        skills_clean,  # <-- already cleaned
                "strategy":      m.get("strategy", []),
                "common_errors": m.get("common_errors", []),
                "remediation":   m.get("remediation", None),
                "flint_prompt":  m.get("flint_prompt", ""),
            }
        })

    return {
        "worksheet": {
            "title":          "Laws of Indices",
            "unit":           "Unit 2: Indices",
            "topic":          "Indices",
            "date":           str(date.today()),
            "total_parts":    len(types) * count,
            "seed":           seed,
            "show_solutions": show_solutions,
        },
        "exercises": exercises,
    }
 
# ── Pyodide entry point ──────────────────────────────────────────
def generate_session(types_json, seed=None, count=6):
    """Called by Pyodide in dynamic mode."""
    types = json.loads(types_json)
    return json.dumps(generate(types=types, seed=seed, count=count))


# ── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate indices exercises"
    )
    parser.add_argument(
        "--types", nargs="+", default=["multiply_simple"],
        help=f"Exercise types. Available: {sorted(REGISTRY.keys())}"
    )
    parser.add_argument("--seed",           type=int,  default=None)
    parser.add_argument("--count",          type=int,  default=6)
    parser.add_argument("--show-solutions", action="store_true")
    parser.add_argument("--pretty",         action="store_true")
    parser.add_argument("--list-types",     action="store_true",
                        help="Print all available type names and exit")
    args = parser.parse_args()

    if args.list_types:
        print("\nAvailable exercise types:\n")
        for k in sorted(REGISTRY.keys()):
            diff = DIFFICULTY.get(k, "?")
            badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(diff,"⚪")
            print(f"  {badge}  {k:<30} {SUBTOPIC.get(k,'')}")
        print()
    else:
        result = generate(
            types=args.types,
            seed=args.seed,
            count=args.count,
            show_solutions=args.show_solutions,
        )
        print(json.dumps(result, ensure_ascii=False,
                         indent=2 if args.pretty else None))

