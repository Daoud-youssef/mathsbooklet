"""
generators/fractions.py
========================
All fraction exercises for Unit 1: Operations.
Single source of truth — used by Quarto (Pyodide) and any backend.

Structure:
  Helpers        — math utilities
  Part generators — single question, returns dict
  Exercise builders — group of 6 parts, returns structured exercise
  Worksheet builder — full worksheet JSON
  Pyodide entry  — generate_session() for browser use
  CLI            — python fractions.py
"""

import random
import math
import json
from datetime import date


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def rand_int(a: int, b: int) -> int:
    return random.randint(a, b)


def simplify(n: int, d: int) -> tuple:
    g = math.gcd(abs(n), abs(d))
    return n // g, d // g


def fmt(n: int, d: int) -> str:
    """Plain text fraction for answer checking."""
    n, d = simplify(n, d)
    return str(n) if d == 1 else f"{n}/{d}"


def fmt_latex(n: int, d: int) -> str:
    """LaTeX fraction for display."""
    n, d = simplify(n, d)
    return str(n) if d == 1 else f"\\dfrac{{{n}}}{{{d}}}"


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


def rand_fraction(max_num: int = 9, max_den: int = 12) -> tuple:
    n = rand_int(1, max_num)
    d = rand_int(n + 1, max_den)
    return n, d


PART_LABELS = ["a", "b", "c", "d", "e", "f"]

NAMES = ["Alex", "Sara", "Liam", "Noor", "Omar",
         "Yara", "Mia", "Zaid", "Hana", "Rami"]

ITEMS = ["pizza", "cake", "ribbon", "rope",
         "chocolate bar", "bread", "pie", "sandwich"]


# ══════════════════════════════════════════════════════════════════
# PART GENERATORS — one question each
# ══════════════════════════════════════════════════════════════════

def _part_add_same() -> dict:
    """Add two fractions with the same denominator."""
    d = rand_int(2, 12)
    n1, n2 = rand_int(1, d - 1), rand_int(1, d - 1)
    an, ad = simplify(n1 + n2, d)
    return {
        "question_latex": (
            f"\\dfrac{{{n1}}}{{{d}}} + \\dfrac{{{n2}}}{{{d}}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\dfrac{{{n1}}}{{{d}}} + \\dfrac{{{n2}}}{{{d}}} "
            f"= \\dfrac{{{n1+n2}}}{{{d}}} = {fmt_latex(an, ad)}"
        ),
    }


def _part_add_diff() -> dict:
    """Add two fractions with different denominators."""
    d1, d2 = rand_int(2, 8), rand_int(2, 8)
    while d2 == d1:
        d2 = rand_int(2, 8)
    n1, n2 = rand_int(1, d1 - 1), rand_int(1, d2 - 1)
    l = lcm(d1, d2)
    nn1, nn2 = n1 * (l // d1), n2 * (l // d2)
    an, ad = simplify(nn1 + nn2, l)
    return {
        "question_latex": (
            f"\\dfrac{{{n1}}}{{{d1}}} + \\dfrac{{{n2}}}{{{d2}}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\text{{LCD}}({d1},{d2}) = {l} \\quad "
            f"\\dfrac{{{nn1}}}{{{l}}} + \\dfrac{{{nn2}}}{{{l}}} "
            f"= {fmt_latex(an, ad)}"
        ),
    }


def _part_subtract() -> dict:
    """Subtract two fractions."""
    d1, d2 = rand_int(2, 8), rand_int(2, 8)
    n1, n2 = rand_int(2, d1), rand_int(1, d2 - 1)
    l = lcm(d1, d2)
    nn1, nn2 = n1 * (l // d1), n2 * (l // d2)
    # ensure positive result
    if nn1 < nn2:
        nn1, nn2 = nn2, nn1
        n1, d1, n2, d2 = n2, d2, n1, d1
    an, ad = simplify(nn1 - nn2, l)
    return {
        "question_latex": (
            f"\\dfrac{{{n1}}}{{{d1}}} - \\dfrac{{{n2}}}{{{d2}}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\text{{LCD}}({d1},{d2}) = {l} \\quad "
            f"\\dfrac{{{nn1}}}{{{l}}} - \\dfrac{{{nn2}}}{{{l}}} "
            f"= {fmt_latex(an, ad)}"
        ),
    }


def _part_multiply() -> dict:
    """Multiply two fractions."""
    n1, d1 = rand_fraction(6, 10)
    n2, d2 = rand_fraction(6, 10)
    an, ad = simplify(n1 * n2, d1 * d2)
    return {
        "question_latex": (
            f"\\dfrac{{{n1}}}{{{d1}}} \\times \\dfrac{{{n2}}}{{{d2}}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\dfrac{{{n1} \\times {n2}}}{{{d1} \\times {d2}}} "
            f"= \\dfrac{{{n1*n2}}}{{{d1*d2}}} = {fmt_latex(an, ad)}"
        ),
    }


def _part_divide() -> dict:
    """Divide two fractions (Keep-Change-Flip)."""
    n1, d1 = rand_fraction(6, 10)
    n2, d2 = rand_fraction(6, 10)
    an, ad = simplify(n1 * d2, d1 * n2)
    return {
        "question_latex": (
            f"\\dfrac{{{n1}}}{{{d1}}} \\div \\dfrac{{{n2}}}{{{d2}}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\dfrac{{{n1}}}{{{d1}}} \\times \\dfrac{{{d2}}}{{{n2}}} "
            f"= \\dfrac{{{n1*d2}}}{{{d1*n2}}} = {fmt_latex(an, ad)}"
        ),
    }


def _part_simplify() -> dict:
    """Simplify a fraction to lowest terms."""
    d = rand_int(4, 24)
    factors = [f for f in range(2, d) if d % f == 0]
    if not factors:
        return _part_simplify()
    g = random.choice(factors)
    n = rand_int(1, d // g - 1) * g
    sn, sd = simplify(n, d)
    return {
        "question_latex": f"\\dfrac{{{n}}}{{{d}}}",
        "answer_latex":   fmt_latex(sn, sd),
        "answer":         fmt(sn, sd),
        "solution_latex": (
            f"\\gcd({n},{d}) = {g} \\quad "
            f"\\dfrac{{{n} \\div {g}}}{{{d} \\div {g}}} = {fmt_latex(sn, sd)}"
        ),
    }


def _part_fraction_of_amount() -> dict:
    """Find a fraction of an amount."""
    n, d = rand_fraction()
    amount = rand_int(10, 100)
    answer = round((amount / d) * n, 2)
    ans_str = str(int(answer)) if answer == int(answer) else str(answer)
    return {
        "question_latex": (
            f"\\dfrac{{{n}}}{{{d}}} \\text{{ of }} {amount}"
        ),
        "answer_latex": ans_str,
        "answer":       ans_str,
        "solution_latex": (
            f"\\dfrac{{{n}}}{{{d}}} \\times {amount} "
            f"= \\dfrac{{{n} \\times {amount}}}{{{d}}} = {ans_str}"
        ),
    }


def _part_word_add() -> dict:
    """Word problem — fraction addition."""
    name  = random.choice(NAMES)
    item  = random.choice(ITEMS)
    d     = rand_int(3, 8)
    n1    = rand_int(1, d - 2)
    n2    = rand_int(1, d - n1 - 1)
    an, ad = simplify(n1 + n2, d)
    return {
        "question_latex": (
            f"\\text{{{name} ate }}"
            f"\\dfrac{{{n1}}}{{{d}}}"
            f"\\text{{ of a {item} then }}"
            f"\\dfrac{{{n2}}}{{{d}}}"
            f"\\text{{ more. Total?}}"
        ),
        "answer_latex": fmt_latex(an, ad),
        "answer":       fmt(an, ad),
        "solution_latex": (
            f"\\dfrac{{{n1}}}{{{d}}} + \\dfrac{{{n2}}}{{{d}}} "
            f"= \\dfrac{{{n1+n2}}}{{{d}}} = {fmt_latex(an, ad)}"
        ),
        "is_word": True,
    }


def _part_word_budget() -> dict:
    """Word problem — budget/spending."""
    name   = random.choice(NAMES)
    salary = rand_int(200, 1000)
    rent   = random.choice([(1, 4), (1, 3), (1, 5)])
    food   = random.choice([(1, 5), (1, 4), (2, 7)])
    ra     = round((salary / rent[1]) * rent[0], 2)
    fa     = round((salary / food[1]) * food[0], 2)
    left   = round(salary - ra - fa, 2)
    ans_str = str(int(left)) if left == int(left) else str(left)
    return {
        "question_latex": (
            f"\\text{{{name} earns {salary} QAR. Spends }}"
            f"\\dfrac{{{rent[0]}}}{{{rent[1]}}}"
            f"\\text{{ on rent and }}"
            f"\\dfrac{{{food[0]}}}{{{food[1]}}}"
            f"\\text{{ on food. How much is left?}}"
        ),
        "answer_latex": f"\\text{{{ans_str} QAR}}",
        "answer":       ans_str,
        "solution_latex": (
            f"\\text{{Rent: }}{ra}\\text{{ QAR, Food: }}{fa}"
            f"\\text{{ QAR, Left: }}{salary}-{ra}-{fa}={ans_str}\\text{{ QAR}}"
        ),
        "is_word": True,
    }


# ══════════════════════════════════════════════════════════════════
# EXERCISE BUILDERS — 6 parts per exercise
# ══════════════════════════════════════════════════════════════════

def _build_exercise(number, title, instruction, part_gen,
                    ex_type, skill, difficulty, topic, subtopic) -> dict:
    """Generic exercise builder — 6 parts from any part generator."""
    parts = [part_gen() for _ in range(6)]
    for i, p in enumerate(parts):
        p["label"] = PART_LABELS[i]
    return {
        "number":      number,
        "title":       title,
        "instruction": instruction,
        "parts":       parts,
        "meta": {
            "type":       ex_type,
            "skill":      skill,
            "difficulty": difficulty,
            "topic":      topic,
            "subtopic":   subtopic,
            "unit":       "Unit 1: Operations",
            "curriculum": "MYP5",
        }
    }


def gen_exercise_add_same(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction Addition — Same Denominator",
        instruction = "Add the fractions. Simplify your answer.",
        part_gen    = _part_add_same,
        ex_type     = "add_same_denominator",
        skill       = "fraction_addition",
        difficulty  = "easy",
        topic       = "Fractions",
        subtopic    = "Addition with same denominator",
    )

def gen_exercise_add_diff(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction Addition — Different Denominators",
        instruction = "Find the LCD, then add. Simplify your answer.",
        part_gen    = _part_add_diff,
        ex_type     = "add_different_denominator",
        skill       = "fraction_addition",
        difficulty  = "medium",
        topic       = "Fractions",
        subtopic    = "Addition with different denominators",
    )

def gen_exercise_subtract(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction Subtraction",
        instruction = "Find the LCD, then subtract. Simplify your answer.",
        part_gen    = _part_subtract,
        ex_type     = "subtract_fractions",
        skill       = "fraction_subtraction",
        difficulty  = "medium",
        topic       = "Fractions",
        subtopic    = "Subtraction of fractions",
    )

def gen_exercise_multiply(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction Multiplication",
        instruction = "Multiply the fractions. Simplify your answer.",
        part_gen    = _part_multiply,
        ex_type     = "multiply_fractions",
        skill       = "fraction_multiplication",
        difficulty  = "medium",
        topic       = "Fractions",
        subtopic    = "Multiplication of fractions",
    )

def gen_exercise_divide(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction Division",
        instruction = "Use Keep-Change-Flip, then simplify.",
        part_gen    = _part_divide,
        ex_type     = "divide_fractions",
        skill       = "fraction_division",
        difficulty  = "hard",
        topic       = "Fractions",
        subtopic    = "Division of fractions",
    )

def gen_exercise_simplify(number=1):
    return _build_exercise(
        number      = number,
        title       = "Simplifying Fractions",
        instruction = "Simplify each fraction to its lowest terms.",
        part_gen    = _part_simplify,
        ex_type     = "simplify_fraction",
        skill       = "simplification",
        difficulty  = "easy",
        topic       = "Fractions",
        subtopic    = "Simplification to lowest terms",
    )

def gen_exercise_fraction_of_amount(number=1):
    return _build_exercise(
        number      = number,
        title       = "Fraction of an Amount",
        instruction = "Calculate each fraction of the given amount.",
        part_gen    = _part_fraction_of_amount,
        ex_type     = "fraction_of_amount",
        skill       = "fraction_application",
        difficulty  = "medium",
        topic       = "Fractions",
        subtopic    = "Fraction of a quantity",
    )

def gen_exercise_word_add(number=1):
    return _build_exercise(
        number      = number,
        title       = "Word Problems — Addition",
        instruction = "Read carefully and show your working.",
        part_gen    = _part_word_add,
        ex_type     = "word_problem_add",
        skill       = "fraction_application",
        difficulty  = "medium",
        topic       = "Fractions",
        subtopic    = "Real-world fraction problems",
    )

def gen_exercise_word_budget(number=1):
    return _build_exercise(
        number      = number,
        title       = "Word Problems — Budget",
        instruction = "Read carefully and show your working.",
        part_gen    = _part_word_budget,
        ex_type     = "word_problem_budget",
        skill       = "fraction_application",
        difficulty  = "hard",
        topic       = "Fractions",
        subtopic    = "Real-world fraction problems",
    )


# ══════════════════════════════════════════════════════════════════
# WORKSHEET BUILDER
# ══════════════════════════════════════════════════════════════════

# Registry — maps key → builder function
EXERCISE_REGISTRY = {
    "add_same":           gen_exercise_add_same,
    "add_diff":           gen_exercise_add_diff,
    "subtract":           gen_exercise_subtract,
    "multiply":           gen_exercise_multiply,
    "divide":             gen_exercise_divide,
    "simplify":           gen_exercise_simplify,
    "fraction_of_amount": gen_exercise_fraction_of_amount,
    "word_add":           gen_exercise_word_add,
    "word_budget":        gen_exercise_word_budget,
}


def generate_worksheet(exercise_keys: list = None) -> dict:
    """
    Generate a full worksheet.
    Pass a list of keys from EXERCISE_REGISTRY to choose exercises.
    Default: add_diff, simplify, word_add.
    """
    if exercise_keys is None:
        exercise_keys = ["add_diff", "simplify", "word_add"]

    exercises = []
    for i, key in enumerate(exercise_keys, 1):
        builder = EXERCISE_REGISTRY.get(key)
        if builder:
            exercises.append(builder(number=i))

    return {
        "worksheet": {
            "title":    "Fraction Operations",
            "unit":     "Unit 1: Operations",
            "topic":    "Fractions",
            "date":     str(date.today()),
            "total_parts": sum(len(e["parts"]) for e in exercises),
        },
        "exercises": exercises,
    }


# ══════════════════════════════════════════════════════════════════
# PYODIDE ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def generate_session(exercise_keys: list = None) -> str:
    """Called by Pyodide — returns JSON string."""
    return json.dumps(generate_worksheet(exercise_keys))


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate fraction worksheet")
    parser.add_argument(
        "--exercises", nargs="+",
        default=["add_diff", "simplify", "word_add"],
        choices=list(EXERCISE_REGISTRY.keys()),
        help="Which exercises to include"
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    result = generate_worksheet(args.exercises)
    indent = 2 if args.pretty else None
    print(json.dumps(result, ensure_ascii=False, indent=indent))

