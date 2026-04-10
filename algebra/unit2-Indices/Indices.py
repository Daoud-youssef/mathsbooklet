"""
Indices.py
==========
Unit 2: Indices & Surds — exercise generator.

Architecture
------------
- Imports shared assets from assets/: components, exercise_schema, renderer, svg_helpers
- Each generator returns make_exercise() — nothing else
- generate() calls build_output() — nothing else
- QMD calls generate() and prints ex["rendered"] — nothing else

Adding a new exercise type
--------------------------
1. Write gen_mytype() — return make_exercise(...)
2. Add to REGISTRY: "mytype": gen_mytype
3. Add to METADATA: "mytype": {...}
4. Done — appears in QMD and worksheet automatically
"""

import random
import math
import json
from datetime import date

# ── Shared assets ─────────────────────────────────────────────────
# assets/ must be on sys.path before importing this file.
# In QMD: sys.path.insert(0, os.path.abspath('../../assets'))
# In Pyodide: worksheet.js pre-loads all asset files into FS
# In CLI: run from project root or add assets/ manually

try:
    from components import (
        ri, rc, rand_coeff, rand_exp, rand_side,
        fmt_exp, fmt_term, fmt_frac, fmt_surd,
        simplify_surd, surd_label,
        steps,
    )
    from exercise_schema import make_exercise, make_part, make_parts_from_expressions
    from renderer import build_output
    _ASSETS = True
except ImportError:
    _ASSETS = False

try:
    from svg_helpers import SVG
    _SVG = True
except ImportError:
    _SVG = False

if not _ASSETS:
    def ri(a,b):         return random.randint(a,b)
    def rc(exclude=None):
        pool=[v for v in ["a","b","c","m","n","x","y","k","p","t","w"] if v!=exclude]
        return random.choice(pool)
    def rand_coeff(l=2,h=9): return ri(l,h)
    def rand_exp(l=2,h=8):   return ri(l,h)
    def fmt_exp(b,p):
        if p==0: return "1"
        if p==1: return str(b)
        return f"{b}^{{{p}}}"
    def fmt_term(c,b,p):
        cs="" if c==1 else str(c)
        if p==0: return str(c)
        if p==1: return f"{cs}{b}"
        return f"{cs}{b}^{{{p}}}"
    def fmt_frac(n,d):   return f"\\dfrac{{{n}}}{{{d}}}"
    def simplify_surd(n):
        n=int(n); best=1
        for k in range(2,int(math.isqrt(n))+1):
            if n%(k*k)==0: best=k*k
        return int(math.isqrt(best)), n//best
    def fmt_surd(c,r):
        if r==1: return str(c)
        if c==1: return f"\\sqrt{{{r}}}"
        return f"{c}\\sqrt{{{r}}}"
    def surd_label(n):
        c,r=simplify_surd(n)
        if r==1: return str(c)
        if c==1: return f"\u221a{n}"
        return f"{c}\u221a{r}"
    def steps(*lines): return " \\\\ ".join(str(l) for l in lines if l)

    # Minimal schema/renderer fallbacks
    def make_part(label, question="", expression="", answer_latex="", solution_latex=""):
        return {"label":label,"question":question,"expression":expression,
                "answer_latex":answer_latex,"solution_latex":solution_latex}
    def make_parts_from_expressions(expressions, answers, solutions=None):
        if solutions is None: solutions=[""]* len(expressions)
        labels = list("abcdefghijklmnopqrstuvwxyz")
        return [make_part(labels[i],expression=expressions[i],
                          answer_latex=answers[i],solution_latex=solutions[i])
                for i in range(len(expressions))]
    def make_exercise(ex_type, subtopic="", lt="", difficulty="medium", bloom="apply",
                      instruction="", context="", given=None, hint="",
                      expression="", diagram_svg="", parts=None,
                      skills=None, prerequisites=None, strategy=None,
                      common_errors=None, remediation="", flint_prompt="", **kw):
        return {"number":0,"type":ex_type,"topic":"Indices","subtopic":subtopic,
                "lt":lt,"difficulty":difficulty,"bloom":bloom,
                "instruction":instruction,"context":context,"given":given or [],
                "hint":hint,"expression":expression,
                "has_diagram":bool(diagram_svg),"diagram_svg":diagram_svg,
                "parts":parts or [],
                "meta":{"skills":skills or [],"prerequisites":prerequisites or [],
                        "strategy":strategy or [],"common_errors":common_errors or [],
                        "remediation":remediation,"flint_prompt":flint_prompt},
                "rendered":"","layout":""}
    def build_output(exercises_raw, show_solutions, worksheet_meta, unit_prefix="u"):
        # Minimal fallback renderer
        exercises_qmd = []
        exercises_ws  = []
        for i,ex in enumerate(exercises_raw,1):
            ex["number"] = i
            # detect layout
            is_grid = (not ex["context"] and not ex["given"] and not ex["has_diagram"]
                       and ex["parts"] and all(p["expression"] for p in ex["parts"]))
            lines = [f"::::: {{#exr-{unit_prefix}-{i}}}\n", f"*{ex['instruction']}*\n"]
            if is_grid:
                n=len(ex["parts"]); col={1:12,2:6,3:4,4:3}.get(n,4)
                lines.append(":::: {.grid}\n")
                for p in ex["parts"]:
                    lines += [f"::: {{.g-col-{col}}}\n",
                              f"**{p['label']})** $\\displaystyle {p['expression']}$\n",":::\n"]
                lines.append("::::\n")
            else:
                if ex["context"]: lines.append(ex["context"]+"\n")
                if ex["given"]:
                    lines.append("**Given:** "+" · ".join(ex["given"])+"\n")
                if ex["has_diagram"] and ex["diagram_svg"]:
                    lines.append(ex["diagram_svg"]+"\n")
                for p in ex["parts"]:
                    if p["expression"]: lines.append(f"**({p['label']})** $\\displaystyle {p['expression']}$\n")
                    else: lines.append(f"**({p['label']})** {p['question']}\n")
            if show_solutions:
                lines += ['::: {.callout-tip collapse="true"}', "## 🔍 View Solution\n"]
                for p in ex["parts"]:
                    sol=p.get("solution_latex") or p["answer_latex"]
                    if sol: lines += [f"**{p['label']})**\n","$$\n\\begin{aligned}",sol,"\\end{aligned}\n$$\n"]
                lines.append(":::\n")
            if ex["meta"]["skills"]:
                badges="\n".join(f'  <span class="skill-badge">{s}</span>' for s in ex["meta"]["skills"])
                lines += ["","::: exercise-meta",'<div class="skill-container">',badges,"</div>",":::\n"]
            lines.append(":::::\n")
            ex["rendered"] = "\n".join(lines)
            ex["layout"]   = "grid" if is_grid else "list"
            exercises_qmd.append(ex)
            # ws part
            ws_parts = []
            for p in ex["parts"]:
                q_latex = p["expression"] if is_grid else f"\\text{{{p['question']}}}"
                ws_parts.append({"label":p["label"],"question_latex":q_latex,"answer_latex":p["answer_latex"]})
            exercises_ws.append({"number":i,"type":ex["type"],"lt":ex["lt"],
                                  "difficulty":ex["difficulty"],"title":ex["instruction"],
                                  "instruction":ex["instruction"],"parts":ws_parts,
                                  "meta":{"difficulty":ex["difficulty"],"lt":ex["lt"],
                                          "skills":ex["meta"]["skills"]}})
        return {"_exercises_qmd":exercises_qmd,"exercises":exercises_ws,
                "worksheet":worksheet_meta,"meta":{"total":len(exercises_qmd)}}


# ══════════════════════════════════════════════════════════════════
# METADATA CATALOGUE
# One entry per exercise type — all fields used by schema/renderer/AI tutor
# ══════════════════════════════════════════════════════════════════

METADATA = {
    "multiply_simple": {
        "subtopic":"Multiplication Rule","difficulty":"easy","bloom":"remember","lt":"LT1",
        "skills":["Index notation","Same base identification","Addition of integers"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Confirm both terms have the same base.","2. Add the exponents: a^m × a^n = a^(m+n)."],
        "common_errors":["Multiplying exponents instead of adding.","Multiplying the bases."],
    },
    "multiply_three_terms": {
        "subtopic":"Multiplication — Three Terms","difficulty":"easy","bloom":"understand","lt":"LT1",
        "skills":["Index notation","Addition of integers","Multi-step simplification"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. All terms share same base.","2. Add all three exponents."],
        "common_errors":["Only adding two of the three exponents."],
    },
    "multiply_coefficients": {
        "subtopic":"Multiplication with Coefficients","difficulty":"medium","bloom":"apply","lt":"LT1",
        "skills":["Coefficient multiplication","Addition of integers","Separating coefficients"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Multiply the coefficients.","2. Add the exponents."],
        "common_errors":["Adding coefficients instead of multiplying."],
    },
    "multiply_multivariable": {
        "subtopic":"Multiplication — Multi-variable","difficulty":"medium","bloom":"apply","lt":"LT1",
        "skills":["Multi-variable expressions","Coefficient multiplication","Grouping like terms"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Multiply coefficients.","2. Apply index law to each variable separately."],
        "common_errors":["Mixing up exponents between variables."],
    },
    "divide_simple": {
        "subtopic":"Division Rule","difficulty":"easy","bloom":"remember","lt":"LT2",
        "skills":["Index notation","Subtraction of integers"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Subtract exponents: a^m ÷ a^n = a^(m-n)."],
        "common_errors":["Dividing instead of subtracting exponents.","Subtracting in wrong order."],
    },
    "divide_coefficients": {
        "subtopic":"Division with Coefficients","difficulty":"medium","bloom":"apply","lt":"LT2",
        "skills":["Coefficient division","Subtraction of integers"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Divide the coefficients.","2. Subtract the exponents."],
        "common_errors":["Subtracting coefficients instead of dividing."],
    },
    "divide_multivariable": {
        "subtopic":"Division — Multi-variable","difficulty":"medium","bloom":"apply","lt":"LT2",
        "skills":["Multi-variable expressions","Coefficient division","Subtraction of integers"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Divide coefficients.","2. Apply division law to each variable independently."],
        "common_errors":["Mixing exponents between variables."],
    },
    "power_simple": {
        "subtopic":"Power of a Power","difficulty":"easy","bloom":"remember","lt":"LT3",
        "skills":["Index notation","Multiplication of integers","Power of power law"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Multiply the powers: (a^m)^n = a^(m×n)."],
        "common_errors":["Adding instead of multiplying the powers."],
    },
    "power_coefficient": {
        "subtopic":"Power of a Power with Coefficient","difficulty":"medium","bloom":"apply","lt":"LT3",
        "skills":["Power of power law","Coefficient exponentiation","Multiplication of integers"],
        "instruction":"Expand and simplify.",
        "strategy":["1. Raise the coefficient to the outer power.","2. Multiply the variable's exponents."],
        "common_errors":["Multiplying coefficient by outer power instead of raising it."],
    },
    "power_multivariable": {
        "subtopic":"Power of a Power — Multi-variable","difficulty":"medium","bloom":"apply","lt":"LT3",
        "skills":["Power of power law","Coefficient exponentiation","Multi-variable expressions"],
        "instruction":"Expand and simplify.",
        "strategy":["1. Raise coefficient to outer power.","2. Multiply each variable's exponent independently."],
        "common_errors":["Applying outer power to only one variable."],
    },
    "power_negative_outer": {
        "subtopic":"Negative Outer Power","difficulty":"hard","bloom":"analyse","lt":"LT3",
        "skills":["Power of power law","Negative index as reciprocal","Coefficient exponentiation"],
        "instruction":"Simplify. Give your answer with positive exponents.",
        "strategy":["1. Expand bracket.","2. Write as reciprocal due to negative outer power."],
        "common_errors":["Making the result negative instead of taking the reciprocal."],
    },
    "combine_same_power": {
        "subtopic":"Combining Same Powers — (ab)ⁿ = aⁿ×bⁿ","difficulty":"medium","bloom":"understand","lt":"LT3",
        "skills":["Prime factorisation","Perfect square recognition","Power distribution law"],
        "instruction":"Write as a single power by expressing each number as a prime power.",
        "strategy":["1. Write each number as a prime power.","2. Check exponents match.","3. Combine bases."],
        "common_errors":["Adding bases instead of multiplying."],
    },
    "negative_evaluate": {
        "subtopic":"Evaluate Negative Indices","difficulty":"medium","bloom":"understand","lt":"LT5",
        "skills":["Negative index as reciprocal","Integer exponentiation","Fraction notation"],
        "instruction":"Evaluate. Write as a fraction.",
        "strategy":["1. Recall: a^(-n) = 1/a^n.","2. Calculate a^n.","3. Write as fraction."],
        "common_errors":["Making result negative: 4^(-2) = -16 ✗"],
    },
    "negative_fraction_base": {
        "subtopic":"Negative Index — Fraction Base","difficulty":"medium","bloom":"understand","lt":"LT5",
        "skills":["Negative index as reciprocal","Fraction reciprocal"],
        "instruction":"Evaluate. Simplify your answer.",
        "strategy":["1. (a/b)^(-n) = (b/a)^n.","2. Evaluate the resulting positive power."],
        "common_errors":["Forgetting to flip the fraction."],
    },
    "negative_simplify": {
        "subtopic":"Simplify with Negative Indices","difficulty":"medium","bloom":"apply","lt":"LT5",
        "skills":["Addition of integers","Negative integer addition","Index notation"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Add the exponents.","2. Be careful with negative exponent arithmetic."],
        "common_errors":["Sign errors when adding negative exponents."],
    },
    "negative_divide": {
        "subtopic":"Division Giving Negative Index","difficulty":"medium","bloom":"apply","lt":"LT2",
        "skills":["Subtraction of integers","Negative index as reciprocal","Index notation"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Subtract exponents (m-n).","2. If result negative, leave as negative index."],
        "common_errors":["Swapping order: computing n-m instead of m-n."],
    },
    "fractional_unit": {
        "subtopic":"Fractional Index — Unit Fraction","difficulty":"medium","bloom":"understand","lt":"LT6",
        "skills":["Fractional index as root","Perfect square recognition","nth root evaluation"],
        "instruction":"Evaluate.",
        "strategy":["1. a^(1/n) = nth root of a.","2. Evaluate the root."],
        "common_errors":["Dividing base by denominator: 27^(1/3) = 9 ✗"],
    },
    "fractional_nonunit": {
        "subtopic":"Fractional Index — Non-unit","difficulty":"hard","bloom":"apply","lt":"LT6",
        "skills":["Fractional index as root and power","nth root evaluation","Integer exponentiation"],
        "instruction":"Evaluate.",
        "strategy":["1. a^(m/n) = (nth root of a)^m.","2. Find the nth root first.","3. Raise to power m."],
        "common_errors":["Raising to power m before taking the root."],
    },
    "fractional_negative": {
        "subtopic":"Negative Fractional Index","difficulty":"hard","bloom":"analyse","lt":"LT6",
        "skills":["Fractional index as root and power","Negative index as reciprocal"],
        "instruction":"Evaluate.",
        "strategy":["1. a^(-m/n) = 1/a^(m/n).","2. Evaluate a^(m/n).","3. Take reciprocal."],
        "common_errors":["Making result negative rather than taking reciprocal."],
    },
    "fractional_of_fraction": {
        "subtopic":"Fractional Index of a Fraction","difficulty":"hard","bloom":"analyse","lt":"LT6",
        "skills":["Fractional index as root and power","nth root of fraction"],
        "instruction":"Evaluate. Simplify your answer.",
        "strategy":["1. Apply index to numerator and denominator separately.","2. Evaluate each part."],
        "common_errors":["Only applying index to numerator."],
    },
    "zero_index": {
        "subtopic":"Zero Index","difficulty":"easy","bloom":"remember","lt":"LT7",
        "skills":["Zero exponent rule","Index notation"],
        "instruction":"Evaluate.",
        "strategy":["1. Any non-zero base to the power 0 equals 1."],
        "common_errors":["Writing a^0 = 0 or a^0 = a."],
    },
    "fraction_simple": {
        "subtopic":"Complex Fraction","difficulty":"medium","bloom":"apply","lt":"LT8",
        "skills":["Combining multiplication and division laws","Multi-step simplification"],
        "instruction":"Simplify. Give your answer in index form.",
        "strategy":["1. Add exponents in numerator.","2. Subtract denominator exponent."],
        "common_errors":["Subtracting denominator exponent from only one numerator term."],
    },
    "fraction_complex": {
        "subtopic":"Complex Fraction with Coefficients","difficulty":"hard","bloom":"analyse","lt":"LT8",
        "skills":["Coefficient division","Combining multiplication and division laws"],
        "instruction":"Simplify fully.",
        "strategy":["1. Multiply numerator coefficients.","2. Add numerator exponents.","3. Divide coefficient.","4. Subtract denominator exponent."],
        "common_errors":["Applying coefficient division to the exponents."],
    },
    "fraction_multivariable": {
        "subtopic":"Complex Fraction — Multi-variable","difficulty":"hard","bloom":"analyse","lt":"LT8",
        "skills":["Multi-variable expressions","Coefficient division","Multi-step simplification"],
        "instruction":"Simplify fully.",
        "strategy":["1. Divide coefficients.","2. Subtract exponents for each variable."],
        "common_errors":["Mixing exponents between variables."],
    },
    "fraction_nested_power": {
        "subtopic":"Nested Power in Fraction","difficulty":"hard","bloom":"analyse","lt":"LT8",
        "skills":["Power of power law","Combining multiplication and division laws"],
        "instruction":"Simplify fully.",
        "strategy":["1. Expand nested power first.","2. Add numerator exponents.","3. Subtract denominator exponent."],
        "common_errors":["Skipping nested power expansion."],
    },
    "numeric_multiply": {
        "subtopic":"Numeric Index Laws — Multiply","difficulty":"medium","bloom":"apply","lt":"LT9",
        "skills":["Numeric base recognition","Addition of integers","Expressing as single power"],
        "instruction":"Simplify. Give your answer as a single power.",
        "strategy":["1. Confirm same numeric base.","2. Add exponents."],
        "common_errors":["Evaluating numerically instead of leaving as index form."],
    },
    "numeric_divide": {
        "subtopic":"Numeric Index Laws — Divide","difficulty":"medium","bloom":"apply","lt":"LT9",
        "skills":["Numeric base recognition","Subtraction of integers","Expressing as single power"],
        "instruction":"Simplify. Give your answer as a single power.",
        "strategy":["1. Subtract exponents."],
        "common_errors":["Dividing exponents instead of subtracting."],
    },
    "numeric_mixed": {
        "subtopic":"Numeric Index Laws — Mixed","difficulty":"hard","bloom":"analyse","lt":"LT9",
        "skills":["Combining multiplication and division laws","Negative integer addition"],
        "instruction":"Simplify. Give your answer as a single power.",
        "strategy":["1. Add all numerator exponents.","2. Subtract denominator exponent."],
        "common_errors":["Sign errors with negative exponents."],
    },
    "write_as_power": {
        "subtopic":"Write as Power of n","difficulty":"medium","bloom":"understand","lt":"LT10",
        "skills":["Prime factorisation","Index notation","Negative index as reciprocal","Zero exponent rule"],
        "instruction":"Write as a single power of the given base.",
        "strategy":["1. Express number as repeated multiplication of base.","2. Count multiplications = exponent."],
        "common_errors":["Confusing base with exponent.","Not recognising 1/8 = 2^(-3)."],
    },
    "find_missing_index": {
        "subtopic":"Find Missing Index","difficulty":"medium","bloom":"apply","lt":"LT11",
        "skills":["Reverse index law","Subtraction of integers","Algebraic reasoning"],
        "instruction":"Find the missing index.",
        "strategy":["1. Set up equation from index law.","2. Solve for missing value."],
        "common_errors":["Adding instead of subtracting to find missing exponent."],
    },
    "find_missing_divide": {
        "subtopic":"Find Missing Index — Division","difficulty":"medium","bloom":"apply","lt":"LT11",
        "skills":["Reverse index law","Subtraction of integers","Algebraic reasoning"],
        "instruction":"Find the missing index.",
        "strategy":["1. m - □ = result.","2. □ = m - result."],
        "common_errors":["Setting up the equation backwards."],
    },
    "find_missing_power": {
        "subtopic":"Find Missing Power","difficulty":"hard","bloom":"analyse","lt":"LT11",
        "skills":["Reverse power of power law","Division of integers","Algebraic reasoning"],
        "instruction":"Find the missing power.",
        "strategy":["1. m × □ = total.","2. □ = total ÷ m."],
        "common_errors":["Using subtraction instead of division."],
    },
    "identify_error": {
        "subtopic":"Identify and Correct Error","difficulty":"hard","bloom":"evaluate","lt":"LT11",
        "skills":["Mathematical reasoning","Error analysis","Verbal mathematical explanation"],
        "instruction":"Identify the mistake and write the correct answer.",
        "strategy":["1. Identify which index law is being applied.","2. Apply correctly yourself.","3. Name the specific mistake."],
        "common_errors":["Vague explanations like 'they got it wrong'."],
    },
    # Surds
    "surd_add_simple": {
        "subtopic":"Adding Like Surds","difficulty":"easy","bloom":"remember","lt":"LT7s",
        "skills":["Like surd identification","Integer addition"],
        "instruction":"Simplify.",
        "strategy":["1. Check radicands match.","2. Add coefficients."],
        "common_errors":["Adding radicands: √3+√3=√6 ✗"],
    },
    "surd_subtract_simple": {
        "subtopic":"Subtracting Like Surds","difficulty":"easy","bloom":"remember","lt":"LT7s",
        "skills":["Like surd identification","Integer subtraction"],
        "instruction":"Simplify.",
        "strategy":["1. Check radicands match.","2. Subtract coefficients."],
        "common_errors":["Subtracting radicands."],
    },
    "surd_add_mixed": {
        "subtopic":"Adding Mixed Surds","difficulty":"medium","bloom":"understand","lt":"LT7s",
        "skills":["Like surd identification","Collecting like terms","Integer addition"],
        "instruction":"Simplify by collecting like surds.",
        "strategy":["1. Identify like surds.","2. Add their coefficients.","3. Leave unlike surds separate."],
        "common_errors":["Combining unlike surds."],
    },
    "surd_subtract_mixed": {
        "subtopic":"Subtracting Mixed Surds","difficulty":"medium","bloom":"understand","lt":"LT7s",
        "skills":["Like surd identification","Collecting like terms"],
        "instruction":"Simplify by collecting like surds.",
        "strategy":["1. Group like surds.","2. Add/subtract coefficients."],
        "common_errors":["Combining unlike surds."],
    },
    "surd_multiply_simple": {
        "subtopic":"Multiplying Surds","difficulty":"easy","bloom":"remember","lt":"LT7s",
        "skills":["Surd multiplication","Surd simplification"],
        "instruction":"Simplify.",
        "strategy":["1. √a × √b = √(ab).","2. Simplify if possible."],
        "common_errors":["Not simplifying the result."],
    },
    "surd_multiply_coeff": {
        "subtopic":"Multiplying Surds with Coefficients","difficulty":"medium","bloom":"apply","lt":"LT7s",
        "skills":["Surd multiplication","Coefficient multiplication","Surd simplification"],
        "instruction":"Simplify.",
        "strategy":["1. Multiply coefficients.","2. Multiply radicands.","3. Simplify."],
        "common_errors":["Not simplifying the final surd."],
    },
    "surd_multiply_chain": {
        "subtopic":"Multiplying Three Surds","difficulty":"medium","bloom":"apply","lt":"LT7s",
        "skills":["Surd multiplication","Multi-step simplification"],
        "instruction":"Simplify.",
        "strategy":["1. Multiply all coefficients.","2. Multiply all radicands.","3. Simplify."],
        "common_errors":["Only multiplying two of the three terms."],
    },
    "surd_divide_simple": {
        "subtopic":"Dividing Surds","difficulty":"easy","bloom":"remember","lt":"LT7s",
        "skills":["Surd division","Surd simplification"],
        "instruction":"Simplify.",
        "strategy":["1. √a/√b = √(a/b).","2. Simplify."],
        "common_errors":["Subtracting instead of dividing radicands."],
    },
    "surd_divide_coeff": {
        "subtopic":"Dividing Surds with Coefficients","difficulty":"medium","bloom":"apply","lt":"LT7s",
        "skills":["Surd division","Coefficient division","Surd simplification"],
        "instruction":"Simplify.",
        "strategy":["1. Divide coefficients.","2. Divide radicands.","3. Simplify."],
        "common_errors":["Not simplifying the final surd."],
    },
    "surd_simplify_basic": {
        "subtopic":"Simplify √n","difficulty":"easy","bloom":"understand","lt":"LT8s",
        "skills":["Perfect square recognition","Surd simplification"],
        "instruction":"Simplify fully.",
        "strategy":["1. Find largest perfect square factor.","2. Split: √(a²×b) = a√b."],
        "common_errors":["Not finding the largest square factor."],
    },
    "surd_simplify_coeff": {
        "subtopic":"Simplify a√n","difficulty":"medium","bloom":"apply","lt":"LT8s",
        "skills":["Perfect square recognition","Surd simplification","Coefficient multiplication"],
        "instruction":"Simplify fully.",
        "strategy":["1. Simplify the surd.","2. Multiply by the outer coefficient."],
        "common_errors":["Forgetting to multiply the outer coefficient."],
    },
    "surd_simplify_fraction": {
        "subtopic":"Rationalise k/√n","difficulty":"medium","bloom":"apply","lt":"LT8s",
        "skills":["Rationalise denominator","Surd multiplication"],
        "instruction":"Rationalise the denominator and simplify.",
        "strategy":["1. Multiply top and bottom by √n.","2. Simplify."],
        "common_errors":["Not simplifying after rationalising."],
    },
    "surd_simplify_product": {
        "subtopic":"Simplify √a × √b","difficulty":"medium","bloom":"apply","lt":"LT8s",
        "skills":["Surd multiplication","Surd simplification"],
        "instruction":"Simplify fully.",
        "strategy":["1. √a × √b = √(ab).","2. Simplify."],
        "common_errors":["Not simplifying the product."],
    },
    "surd_simplify_mixed_ops": {
        "subtopic":"Mixed Surd Operations","difficulty":"hard","bloom":"analyse","lt":"LT8s",
        "skills":["Surd simplification","Collecting like terms","Multi-step simplification"],
        "instruction":"Simplify fully.",
        "strategy":["1. Simplify each surd.","2. Collect like surds."],
        "common_errors":["Not simplifying before collecting."],
    },
    "surd_simplify_chain": {
        "subtopic":"Chain Surd Simplification","difficulty":"hard","bloom":"analyse","lt":"LT8s",
        "skills":["Surd simplification","Multi-step simplification","Collecting like terms"],
        "instruction":"Simplify fully.",
        "strategy":["1. Simplify each surd first.","2. Then collect like terms."],
        "common_errors":["Collecting before simplifying."],
    },
    "surd_expand_single": {
        "subtopic":"Expand Single Bracket with Surds","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["Distributive law","Surd multiplication","Surd simplification"],
        "instruction":"Expand and simplify.",
        "strategy":["1. Distribute over each term.","2. Simplify each product."],
        "common_errors":["Not distributing to all terms."],
    },
    "surd_expand_double_simple": {
        "subtopic":"Expand Double Brackets with Surds","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["FOIL method","Surd multiplication","Collecting like terms"],
        "instruction":"Expand and simplify.",
        "strategy":["1. Use FOIL.","2. Simplify surd products.","3. Collect like terms."],
        "common_errors":["Sign errors in FOIL.","Not simplifying surd products."],
    },
    "surd_expand_double_mixed": {
        "subtopic":"Expand Mixed Double Brackets","difficulty":"hard","bloom":"analyse","lt":"LT9s",
        "skills":["FOIL method","Surd multiplication","Collecting like terms"],
        "instruction":"Expand and simplify.",
        "strategy":["1. FOIL.","2. Simplify each product.","3. Collect surds."],
        "common_errors":["Sign errors.","Forgetting to simplify surds."],
    },
    "surd_expand_conjugate": {
        "subtopic":"Expand Conjugate Pairs","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["Difference of squares","Conjugate pairs","Surd simplification"],
        "instruction":"Expand and simplify.",
        "strategy":["1. (a+b)(a-b) = a²-b².","2. (√m+n)(√m-n) = m-n²."],
        "common_errors":["Not recognising conjugate pair pattern."],
    },
    "surd_expand_square": {
        "subtopic":"Expand (√a + b)²","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["Squaring binomials","Surd multiplication","Collecting like terms"],
        "instruction":"Expand and simplify.",
        "strategy":["1. (a+b)² = a²+2ab+b².","2. Simplify each term."],
        "common_errors":["Writing (√a+b)² = a+b² ✗"],
    },
    "surd_rationalise_simple": {
        "subtopic":"Rationalise a/√b","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["Rationalise denominator","Surd multiplication","Fraction simplification"],
        "instruction":"Rationalise the denominator and simplify.",
        "strategy":["1. Multiply by √b/√b.","2. Simplify."],
        "common_errors":["Not simplifying after rationalising."],
    },
    "surd_rationalise_coeff": {
        "subtopic":"Rationalise a/(b√c)","difficulty":"medium","bloom":"apply","lt":"LT9s",
        "skills":["Rationalise denominator","Surd multiplication","Fraction simplification"],
        "instruction":"Rationalise the denominator and simplify.",
        "strategy":["1. Multiply by √c/√c.","2. Simplify fraction."],
        "common_errors":["Forgetting to simplify the resulting fraction."],
    },
    "surd_rationalise_binomial": {
        "subtopic":"Rationalise with Binomial Denominator","difficulty":"hard","bloom":"analyse","lt":"LT9s",
        "skills":["Conjugate pairs","Difference of squares","Rationalise denominator"],
        "instruction":"Rationalise the denominator and simplify.",
        "strategy":["1. Multiply by conjugate.","2. Denominator = difference of squares.","3. Simplify."],
        "common_errors":["Using wrong conjugate sign."],
    },
    "surd_rationalise_full": {
        "subtopic":"Full Conjugate Rationalisation","difficulty":"hard","bloom":"evaluate","lt":"LT9s",
        "skills":["Conjugate pairs","Difference of squares","Multi-step rationalisation"],
        "instruction":"Rationalise the denominator fully and simplify.",
        "strategy":["1. State the conjugate.","2. Multiply top and bottom.","3. Simplify."],
        "common_errors":["Incorrect conjugate.","Sign errors in numerator expansion."],
    },
    "surd_rationalise_sum": {
        "subtopic":"Rationalise and Add Fractions","difficulty":"hard","bloom":"evaluate","lt":"LT9s",
        "skills":["Rationalise denominator","Adding fractions","Multi-step simplification"],
        "instruction":"Rationalise each denominator and add.",
        "strategy":["1. Rationalise each fraction separately.","2. Add the results."],
        "common_errors":["Adding before rationalising."],
    },
    "surd_rationalise_frac_sum": {
        "subtopic":"(√a + n)/√c — Split and Simplify","difficulty":"hard","bloom":"evaluate","lt":"LT9s",
        "skills":["Splitting fractions","Rationalise denominator","Surd simplification"],
        "instruction":"Rationalise and simplify.",
        "strategy":["1. Split fraction.","2. Simplify each term."],
        "common_errors":["Not splitting the fraction first."],
    },
    "surd_find_xy": {
        "subtopic":"Find Unknown Indices by Matching Coefficients","difficulty":"hard","bloom":"evaluate","lt":"LT9s",
        "skills":["Coefficient matching","Surd expansion","Algebraic reasoning"],
        "instruction":"Find the values of x and y.",
        "strategy":["1. Expand the bracket.","2. Match surd and integer coefficients."],
        "common_errors":["Matching wrong terms."],
    },
    "surd_pythagoras": {
        "subtopic":"Pythagoras with Surds","difficulty":"hard","bloom":"apply","lt":"LT9s",
        "skills":["Pythagoras theorem","Surd simplification","Surd arithmetic"],
        "instruction":"Use Pythagoras' theorem. Give your answer as a simplified surd.",
        "strategy":["1. x² = a² + b².","2. Add the values.","3. Simplify √result."],
        "common_errors":["Not simplifying the final surd."],
    },
    "surd_trapezium_area": {
        "subtopic":"Trapezium Area with Surds","difficulty":"hard","bloom":"evaluate","lt":"LT9s",
        "skills":["Area formula","Surd division","Rationalise denominator","Multi-step simplification"],
        "instruction":"Show your working clearly.",
        "strategy":["1. Use Area = ½(a+b)h.","2. Substitute and rearrange for k.","3. Simplify surd."],
        "common_errors":["Forgetting the ½ in the area formula."],
    },
}


# ══════════════════════════════════════════════════════════════════
# GENERATORS — each returns make_exercise()
# ══════════════════════════════════════════════════════════════════

def _meta(ex_type):
    """Get metadata for an exercise type."""
    return METADATA.get(ex_type, {})

def _ex(ex_type, parts, **extra):
    """Shorthand: make_exercise with metadata from METADATA catalogue."""
    m = _meta(ex_type)
    return make_exercise(
        ex_type      = ex_type,
        topic        = "Indices & Surds",
        subtopic     = m.get("subtopic",""),
        lt           = m.get("lt",""),
        difficulty   = m.get("difficulty","medium"),
        bloom        = m.get("bloom","apply"),
        instruction  = m.get("instruction","Simplify."),
        skills       = m.get("skills",[]),
        strategy     = m.get("strategy",[]),
        common_errors= m.get("common_errors",[]),
        parts        = parts,
        **extra
    )

# ── LT1 Multiplication ────────────────────────────────────────────

def gen_multiply_simple():
    v=rc(); m=rand_exp(2,7); n=rand_exp(2,7)
    return _ex("multiply_simple", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}"],
        [fmt_exp(v, m+n)],
        [f"{v}^{{{m}+{n}}} = {fmt_exp(v,m+n)}"],
    ))

def gen_multiply_three_terms():
    v=rc(); m,n,p=rand_exp(2,6),rand_exp(2,6),rand_exp(2,6)
    return _ex("multiply_three_terms", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)} \\times {fmt_exp(v,p)}"],
        [fmt_exp(v, m+n+p)],
        [f"{v}^{{{m}+{n}+{p}}} = {fmt_exp(v,m+n+p)}"],
    ))

def gen_multiply_coefficients():
    v=rc(); c1=rand_coeff(2,6); c2=rand_coeff(2,6); m=rand_exp(2,7); n=rand_exp(2,7)
    return _ex("multiply_coefficients", make_parts_from_expressions(
        [f"{fmt_term(c1,v,m)} \\times {fmt_term(c2,v,n)}"],
        [fmt_term(c1*c2, v, m+n)],
        [f"{c1}\\times {c2}={c1*c2},\\quad {v}^{{{m}+{n}}}={v}^{{{m+n}}}"],
    ))

def gen_multiply_multivariable():
    v1=rc(); v2=rc(exclude=v1)
    c1,c2=rand_coeff(2,5),rand_coeff(2,5); m,n=rand_exp(2,5),rand_exp(2,5); p,q=rand_exp(1,4),rand_exp(1,4)
    return _ex("multiply_multivariable", make_parts_from_expressions(
        [f"{fmt_term(c1,v1,m)}{fmt_exp(v2,p)} \\times {fmt_term(c2,v1,n)}{fmt_exp(v2,q)}"],
        [f"{fmt_term(c1*c2,v1,m+n)}{fmt_exp(v2,p+q)}"],
        [f"{c1}\\times {c2}={c1*c2},\\quad {v1}^{{{m}+{n}}}={v1}^{{{m+n}}},\\quad {v2}^{{{p}+{q}}}={v2}^{{{p+q}}}"],
    ))

# ── LT2 Division ──────────────────────────────────────────────────

def gen_divide_simple():
    v=rc(); n=rand_exp(2,5); m=n+ri(1,6)
    return _ex("divide_simple", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\div {fmt_exp(v,n)}"],
        [fmt_exp(v,m-n)],
        [f"{v}^{{{m}-{n}}} = {fmt_exp(v,m-n)}"],
    ))

def gen_divide_coefficients():
    v=rc(); n=rand_exp(2,5); m=n+ri(1,5)
    c2=random.choice([2,3,4,5,6]); c1=c2*ri(2,5); cr=c1//c2
    return _ex("divide_coefficients", make_parts_from_expressions(
        [f"{fmt_term(c1,v,m)} \\div {fmt_term(c2,v,n)}"],
        [fmt_term(cr,v,m-n)],
        [f"\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad {v}^{{{m}-{n}}}={v}^{{{m-n}}}"],
    ))

def gen_divide_multivariable():
    v1=rc(); v2=rc(exclude=v1)
    n1,n2=rand_exp(1,4),rand_exp(1,3); m1=n1+ri(1,4); m2=n2+ri(0,3)
    c2=random.choice([2,3,4]); c1=c2*ri(2,4); cr=c1//c2
    return _ex("divide_multivariable", make_parts_from_expressions(
        [fmt_frac(f"{fmt_term(c1,v1,m1)}{fmt_exp(v2,m2)}", f"{fmt_term(c2,v1,n1)}{fmt_exp(v2,n2)}")],
        [f"{fmt_term(cr,v1,m1-n1)}{fmt_exp(v2,m2-n2)}"],
        [f"\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad {v1}^{{{m1}-{n1}}}={v1}^{{{m1-n1}}},\\quad {v2}^{{{m2}-{n2}}}={v2}^{{{m2-n2}}}"],
    ))

# ── LT3 Power of a Power ──────────────────────────────────────────

def gen_power_simple():
    v=rc(); m=rand_exp(2,6); n=rand_exp(2,5)
    return _ex("power_simple", make_parts_from_expressions(
        [f"({fmt_exp(v,m)})^{{{n}}}"],
        [fmt_exp(v, m*n)],
        [f"{v}^{{{m}\\times {n}}} = {fmt_exp(v,m*n)}"],
    ))

def gen_power_coefficient():
    v=rc(); c=rand_coeff(2,5); m=rand_exp(2,5); n=rand_exp(2,4)
    return _ex("power_coefficient", make_parts_from_expressions(
        [f"({fmt_term(c,v,m)})^{{{n}}}"],
        [fmt_term(c**n, v, m*n)],
        [f"{c}^{{{n}}}={c**n},\\quad {v}^{{{m}\\times {n}}}={v}^{{{m*n}}}"],
    ))

def gen_power_multivariable():
    v1=rc(); v2=rc(exclude=v1); c=rand_coeff(2,4); m=rand_exp(1,4); p=rand_exp(1,4); n=rand_exp(2,3)
    return _ex("power_multivariable", make_parts_from_expressions(
        [f"({fmt_term(c,v1,m)}{fmt_exp(v2,p)})^{{{n}}}"],
        [f"{fmt_term(c**n,v1,m*n)}{fmt_exp(v2,p*n)}"],
        [f"{c}^{{{n}}}={c**n},\\quad {v1}^{{{m}\\times {n}}}={v1}^{{{m*n}}},\\quad {v2}^{{{p}\\times {n}}}={v2}^{{{p*n}}}"],
    ))

def gen_power_negative_outer():
    v=rc(); c=rand_coeff(2,4); m=rand_exp(2,4); n=ri(1,3)
    return _ex("power_negative_outer", make_parts_from_expressions(
        [f"({fmt_term(c,v,m)})^{{-{n}}}"],
        [fmt_frac("1", fmt_term(c**n, v, m*n))],
        [f"\\dfrac{{1}}{{{c}^{{{n}}}{v}^{{{m}\\times {n}}}}} = \\dfrac{{1}}{{{fmt_term(c**n,v,m*n)}}}"],
    ))

def gen_combine_same_power():
    """aⁿ × bⁿ = (ab)ⁿ — pick two prime bases and a random power, compute everything."""
    primes = [2, 3, 5, 7]
    for _ in range(50):
        b1 = random.choice(primes)
        b2 = random.choice([p for p in primes if p != b1])
        pw = random.choice([2, 3, 4, 5])
        n1 = b1 ** pw
        n2 = b2 ** pw
        cb = b1 * b2
        cv = cb ** pw
        if cv < 10000:  # keep numbers manageable
            break
    return _ex("combine_same_power", make_parts_from_expressions(
        [f"{n1} \\times {n2}"],
        [f"{cb}^{{{pw}}}"],
        [f"{n1}\\times {n2}={b1}^{{{pw}}}\\times {b2}^{{{pw}}}=({b1}\\times {b2})^{{{pw}}}={cb}^{{{pw}}}={cv}"],
    ))

# ── LT5 Negative Indices ──────────────────────────────────────────

def gen_negative_evaluate():
    base=random.choice([2,3,4,5,7,10]); n=ri(1,4); val=base**n
    return _ex("negative_evaluate", make_parts_from_expressions(
        [fmt_exp(str(base),-n)],
        [fmt_frac("1",str(val))],
        [f"{base}^{{-{n}}} = \\dfrac{{1}}{{{base}^{{{n}}}}} = \\dfrac{{1}}{{{val}}}"],
    ))

def gen_negative_fraction_base():
    a,b = random.choice([(2,3),(3,5),(2,5),(3,4),(4,5)]); n=ri(1,3)
    an=b**n; ad=a**n
    if n==1: ans=fmt_frac(str(b),str(a)); sol=f"\\text{{Flip: }}\\left(\\dfrac{{{b}}}{{{a}}}\\right)^{{{n}}}=\\dfrac{{{an}}}{{{ad}}}"
    else:    ans=fmt_frac(str(an),str(ad)); sol=f"\\left(\\dfrac{{{b}}}{{{a}}}\\right)^{{{n}}}=\\dfrac{{{b}^{{{n}}}}}{{{a}^{{{n}}}}}=\\dfrac{{{an}}}{{{ad}}}"
    return _ex("negative_fraction_base", make_parts_from_expressions(
        [f"\\left(\\dfrac{{{a}}}{{{b}}}\\right)^{{-{n}}}"], [ans], [sol],
    ))

def gen_negative_simplify():
    v=rc(); m=rand_exp(2,6); n=ri(-5,-1); an=m+n
    return _ex("negative_simplify", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}"],
        [fmt_exp(v,an)],
        [f"{v}^{{{m}+({n})}} = {fmt_exp(v,an)}"],
    ))

def gen_negative_divide_to_negative():
    v=rc(); m=rand_exp(2,5); n=m+ri(1,4); an=m-n
    return _ex("negative_divide", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\div {fmt_exp(v,n)}"],
        [fmt_exp(v,an)],
        [f"{v}^{{{m}-{n}}} = {fmt_exp(v,an)}"],
    ))

# ── LT6 Fractional Indices ────────────────────────────────────────

def gen_fractional_unit():
    """a^(1/n) = nth root of a — generate valid perfect nth powers dynamically."""
    from fractions import Fraction
    for _ in range(100):
        n    = random.choice([2, 3, 4, 5])
        root = random.randint(2, 10)
        base = root ** n
        if base <= 1024:
            break
    return _ex("fractional_unit", make_parts_from_expressions(
        [f"{base}^{{\\frac{{1}}{{{n}}}}}"],
        [str(root)],
        [f"\\sqrt[{n}]{{{base}}} = {root}"],
    ))

def gen_fractional_nonunit():
    """a^(m/n) = (nth root of a)^m — generate dynamically."""
    for _ in range(100):
        n    = random.choice([2, 3, 4, 5])
        root = random.randint(2, 8)
        base = root ** n
        m    = random.randint(2, 4)
        ans  = root ** m
        if base <= 1000 and ans <= 1000 and m != n:
            break
    step = f"\\left(\\sqrt[{n}]{{{base}}}\\right)^{{{m}}}={root}^{{{m}}}={ans}"
    return _ex("fractional_nonunit", make_parts_from_expressions(
        [f"{base}^{{\\frac{{{m}}}{{{n}}}}}"],
        [str(ans)],
        [step],
    ))

def gen_fractional_negative():
    """a^(-m/n) = 1/a^(m/n) — dynamic."""
    from fractions import Fraction
    for _ in range(100):
        n    = random.choice([2, 3, 4])
        root = random.randint(2, 7)
        base = root ** n
        m    = random.randint(1, 3)
        ans_num = 1
        ans_den = root ** m
        if base <= 1000 and ans_den <= 100:
            break
    ans = fmt_frac("1", str(ans_den))
    sol = (f"{base}^{{-\\frac{{{m}}}{{{n}}}}} "
           f"= \\dfrac{{1}}{{{base}^{{\\frac{{{m}}}{{{n}}}}}}}"
           f"= \\dfrac{{1}}"
           f"{{\\left(\\sqrt[{n}]{{{base}}}\\right)^{{{m}}}}}"
           f"= \\dfrac{{1}}{{{root}^{{{m}}}}} = {ans}")
    return _ex("fractional_negative", make_parts_from_expressions(
        [f"{base}^{{-\\frac{{{m}}}{{{n}}}}}"], [ans], [sol],
    ))

def gen_fractional_of_fraction():
    """(p/q)^(m/n) — generate valid perfect-power fractions dynamically."""
    for _ in range(100):
        n     = random.choice([2, 3])
        rp    = random.randint(2, 6)   # root of numerator
        rq    = random.randint(2, 6)   # root of denominator
        if rp == rq: continue
        p     = rp ** n
        q     = rq ** n
        m     = random.randint(1, 3)
        from fractions import Fraction
        ans_f = Fraction(rp**m, rq**m)
        if ans_f.denominator <= 200:
            break
    ans = fmt_frac(str(ans_f.numerator), str(ans_f.denominator)) \
          if ans_f.denominator > 1 else str(ans_f.numerator)
    sol = (f"\\left(\\sqrt[{n}]{{\\dfrac{{{p}}}{{{q}}}}}\\right)^{{{m}}}"
           f"=\\left(\\dfrac{{{rp}}}{{{rq}}}\\right)^{{{m}}}"
           f"=\\dfrac{{{rp}^{{{m}}}}}{{{rq}^{{{m}}}}}={ans}")
    return _ex("fractional_of_fraction", make_parts_from_expressions(
        [f"\\left(\\dfrac{{{p}}}{{{q}}}\\right)^{{\\frac{{{m}}}{{{n}}}}}"],
        [ans], [sol],
    ))

# ── LT7 Zero Index ────────────────────────────────────────────────

def gen_zero_index():
    base=random.choice([rc(), str(ri(2,9)), f"{ri(2,5)}{rc()}"])
    return _ex("zero_index", make_parts_from_expressions(
        [fmt_exp(base,0)], ["1"],
        [f"{base}^{{0}}=1\\quad\\text{{(any non-zero base to power 0 = 1)}}"],
    ))

# ── LT8 Complex Fractions ─────────────────────────────────────────

def gen_fraction_simple():
    v=rc(); m=rand_exp(2,6); n=rand_exp(2,5); top=m+n; p=ri(1,top-1); ans=top-p
    return _ex("fraction_simple", make_parts_from_expressions(
        [fmt_frac(f"{fmt_exp(v,m)} \\times {fmt_exp(v,n)}", fmt_exp(v,p))],
        [fmt_exp(v,ans)],
        [f"{v}^{{{m}+{n}-{p}}}={v}^{{{ans}}}"],
    ))

def gen_fraction_complex():
    v=rc(); m,n=rand_exp(2,5),rand_exp(2,4); top_e=m+n; p=ri(1,top_e-1); ans_e=top_e-p
    ca=random.choice([2,3,4]); cb=random.choice([2,3,4]); cc=ca*cb
    cd=random.choice([f for f in range(2,cc+1) if cc%f==0]); cr=cc//cd
    return _ex("fraction_complex", make_parts_from_expressions(
        [fmt_frac(f"{fmt_term(ca,v,m)} \\times {fmt_term(cb,v,n)}", fmt_term(cd,v,p))],
        [fmt_term(cr,v,ans_e)],
        [f"{ca}\\times {cb}={cc},\\;{v}^{{{m}+{n}}}={v}^{{{top_e}}}\\quad\\dfrac{{{cc}}}{{{cd}}}={cr},\\;{v}^{{{top_e}-{p}}}={v}^{{{ans_e}}}"],
    ))

def gen_fraction_multivariable():
    v1=rc(); v2=rc(exclude=v1)
    n1,n2=rand_exp(1,4),rand_exp(1,3); m1=n1+ri(1,4); m2=n2+ri(1,3)
    c2=random.choice([2,3,4]); c1=c2*ri(2,4); cr=c1//c2
    return _ex("fraction_multivariable", make_parts_from_expressions(
        [fmt_frac(f"{fmt_term(c1,v1,m1)}{fmt_exp(v2,m2)}", f"{fmt_term(c2,v1,n1)}{fmt_exp(v2,n2)}")],
        [f"{fmt_term(cr,v1,m1-n1)}{fmt_exp(v2,m2-n2)}"],
        [f"\\dfrac{{{c1}}}{{{c2}}}={cr},\\quad {v1}^{{{m1}-{n1}}}={v1}^{{{m1-n1}}},\\quad {v2}^{{{m2}-{n2}}}={v2}^{{{m2-n2}}}"],
    ))

def gen_fraction_nested_power():
    v=rc(); m=rand_exp(2,5); n=rand_exp(2,4); p=rand_exp(2,3); np_=n*p
    top=m+np_; q_=ri(1,top-1); ans=top-q_
    return _ex("fraction_nested_power", make_parts_from_expressions(
        [fmt_frac(f"{fmt_exp(v,m)} \\times ({fmt_exp(v,n)})^{{{p}}}", fmt_exp(v,q_))],
        [fmt_exp(v,ans)],
        [f"({v}^{{{n}}})^{{{p}}}={v}^{{{np_}}},\\quad "
       f"{v}^{{{m}}}\\times {v}^{{{np_}}}={v}^{{{top}}},\\quad "
       f"{v}^{{{top}-{q_}}}={fmt_exp(v,ans)}"],
    ))

# ── LT9 Numeric ───────────────────────────────────────────────────

def gen_numeric_multiply():
    base=random.choice([2,3,5]); m=ri(2,6); n=ri(2,6)
    return _ex("numeric_multiply", make_parts_from_expressions(
        [f"{base}^{{{m}}} \\times {base}^{{{n}}}"],
        [f"{base}^{{{m+n}}}"],
        [f"{base}^{{{m}+{n}}}={base}^{{{m+n}}}"],
    ))

def gen_numeric_divide():
    base=random.choice([2,3,5]); n=ri(2,5); m=n+ri(1,5)
    return _ex("numeric_divide", make_parts_from_expressions(
        [f"{base}^{{{m}}} \\div {base}^{{{n}}}"],
        [f"{base}^{{{m-n}}}"],
        [f"{base}^{{{m}-{n}}}={base}^{{{m-n}}}"],
    ))

def gen_numeric_mixed():
    base=random.choice([2,3,5]); m=ri(4,9); n=ri(-3,-1); p=ri(1,4); ans=m+n-p
    return _ex("numeric_mixed", make_parts_from_expressions(
        [fmt_frac(f"{base}^{{{m}}} \\times {base}^{{{n}}}", f"{base}^{{{p}}}")],
        [f"{base}^{{{ans}}}"],
        [f"{base}^{{{m}+({n})-{p}}}={base}^{{{ans}}}"],
    ))

# ── LT10 Write as Power ───────────────────────────────────────────

def gen_write_as_power():
    options=[
        ("4",2,"2^{2}"),("8",2,"2^{3}"),("32",2,"2^{5}"),("16",2,"2^{4}"),("64",2,"2^{6}"),
        ("\\frac{1}{2}",2,"2^{-1}"),("\\frac{1}{4}",2,"2^{-2}"),
        ("25",5,"5^{2}"),("125",5,"5^{3}"),("1",5,"5^{0}"),("\\frac{1}{5}",5,"5^{-1}"),
        ("9",3,"3^{2}"),("27",3,"3^{3}"),("81",3,"3^{4}"),("\\frac{1}{3}",3,"3^{-1}"),
        ("1000",10,"10^{3}"),("100",10,"10^{2}"),
    ]
    expr,base,a = random.choice(options)
    return _ex("write_as_power", make_parts_from_expressions(
        [f"\\text{{Write }}{expr}\\text{{ as a power of }}{base}"], [a], [f"{expr}={a}"],
    ))

# ── LT11 Find Missing ─────────────────────────────────────────────

def gen_find_missing_index():
    v=rc(); ans=ri(2,7); m=ri(2,7); total=m+ans
    return _ex("find_missing_index", make_parts_from_expressions(
        [f"{fmt_exp(v,m)} \\times {v}^{{\\square}} = {fmt_exp(v,total)}"],
        [str(ans)],
        [f"\\square = {total} - {m} = {ans}"],
    ))

def gen_find_missing_divide():
    v=rc(); ans=ri(1,5); total=ri(ans+1,ans+6); m=total+ans
    return _ex("find_missing_divide", make_parts_from_expressions(
        [f"\\dfrac{{{fmt_exp(v,m)}}}{{{v}^{{\\square}}}} = {fmt_exp(v,total)}"],
        [str(ans)],
        [f"\\square = {m} - {total} = {ans}"],
    ))

def gen_find_missing_power():
    v=rc(); m=ri(2,5); ans=ri(2,4); total=m*ans
    return _ex("find_missing_power", make_parts_from_expressions(
        [f"({fmt_exp(v,m)})^{{\\square}} = {fmt_exp(v,total)}"],
        [str(ans)],
        [f"\\square = {total} \\div {m} = {ans}"],
    ))

def gen_identify_error():
    errors = [
        {
            "context": r"A student wrote: $y^8 \times y^3 = y^{24}$",
            "parts":[
                make_part("a", question="Identify the mistake.",
                          answer_latex=r"\text{Powers should be added, not multiplied.}",
                          solution_latex=r"\text{Index law: }a^m\times a^n=a^{m+n}\text{, not }a^{mn}"),
                make_part("b", question="Write the correct answer.",
                          answer_latex=r"y^{11}",
                          solution_latex=r"y^{8+3}=y^{11}"),
            ],
        },
        {
            "context": r"A student wrote: $9^{-2} = -81$",
            "parts":[
                make_part("a", question="Is this correct? Explain.",
                          answer_latex=r"\text{No. }a^{-n}=\dfrac{1}{a^n}\text{, never negative.}",
                          solution_latex=r"9^{-2}=\dfrac{1}{9^2}=\dfrac{1}{81}"),
                make_part("b", question="Write the correct value.",
                          answer_latex=r"\dfrac{1}{81}",
                          solution_latex=r"\dfrac{1}{9^2}=\dfrac{1}{81}"),
            ],
        },
        {
            "context": r"A student wrote: $27^{\frac{1}{3}} = 9$ (claiming $\frac{1}{3}\times27=9$)",
            "parts":[
                make_part("a", question="Identify the mistake.",
                          answer_latex=r"\text{a}^{\frac{1}{n}}=\sqrt[n]{a}\text{, not }\frac{1}{n}\times a",
                          solution_latex=r"a^{\frac{1}{n}}=\sqrt[n]{a}\text{, not }\frac{1}{n}\times a"),
                make_part("b", question="Write the correct answer.",
                          answer_latex=r"3",
                          solution_latex=r"\sqrt[3]{27}=3"),
            ],
        },
    ]
    e = random.choice(errors)
    return _ex("identify_error", e["parts"], context=e["context"])

# ── LT7s Surds: Operate ───────────────────────────────────────────

def gen_surd_add_simple():
    n=random.choice([2,3,5,6,7,10,11,13]); a=ri(2,8); b=ri(2,8)
    return _ex("surd_add_simple", make_parts_from_expressions(
        [f"{fmt_surd(a,n)} + {fmt_surd(b,n)}"],
        [fmt_surd(a+b,n)],
        [f"({a}+{b})\\sqrt{{{n}}}={a+b}\\sqrt{{{n}}}"],
    ))

def gen_surd_subtract_simple():
    n=random.choice([2,3,5,6,7,10,11,13]); b=ri(2,6); a=b+ri(1,5)
    return _ex("surd_subtract_simple", make_parts_from_expressions(
        [f"{fmt_surd(a,n)} - {fmt_surd(b,n)}"],
        [fmt_surd(a-b,n)],
        [f"({a}-{b})\\sqrt{{{n}}}={a-b}\\sqrt{{{n}}}"],
    ))

def gen_surd_add_mixed():
    m=random.choice([2,3,5,7]); n=random.choice([2,3,5,7])
    while n==m: n=random.choice([2,3,5,7])
    a=ri(2,7); b=ri(2,6); c=ri(1,5)
    return _ex("surd_add_mixed", make_parts_from_expressions(
        [f"{fmt_surd(a,m)}+{fmt_surd(b,n)}+{fmt_surd(c,m)}"],
        [f"{fmt_surd(a+c,m)}+{fmt_surd(b,n)}"],
        [f"({a}+{c})\\sqrt{{{m}}}+{fmt_surd(b,n)}={fmt_surd(a+c,m)}+{fmt_surd(b,n)}"],
    ))

def gen_surd_subtract_mixed():
    m=random.choice([2,3,5,7]); n=random.choice([2,3,5,7])
    while n==m: n=random.choice([2,3,5,7])
    a=ri(3,8); b=ri(3,7); c=ri(1,a-1); d=ri(1,b-1)
    return _ex("surd_subtract_mixed", make_parts_from_expressions(
        [f"{fmt_surd(a,m)}+{fmt_surd(b,n)}-{fmt_surd(c,m)}-{fmt_surd(d,n)}"],
        [f"{fmt_surd(a-c,m)}+{fmt_surd(b-d,n)}"],
        [f"({a}-{c})\\sqrt{{{m}}}+({b}-{d})\\sqrt{{{n}}}={fmt_surd(a-c,m)}+{fmt_surd(b-d,n)}"],
    ))

def gen_surd_multiply_simple():
    pairs=[(2,3),(2,5),(2,6),(3,5),(3,7),(5,6),(5,7),(2,7),(6,7)]
    a,b=random.choice(pairs); c,r=simplify_surd(a*b)
    return _ex("surd_multiply_simple", make_parts_from_expressions(
        [f"\\sqrt{{{a}}} \\times \\sqrt{{{b}}}"],
        [fmt_surd(c,r)],
        [f"\\sqrt{{{a}\\times {b}}}=\\sqrt{{{a*b}}}={fmt_surd(c,r)}"],
    ))

def gen_surd_multiply_coeff():
    for _ in range(40):
        a=ri(2,5); b=random.choice([2,3,5,6,7]); c=ri(2,5); d=random.choice([2,3,5,6,7])
        cc,rr=simplify_surd(b*d); tc=a*c*cc
        if tc<=30: break
    return _ex("surd_multiply_coeff", make_parts_from_expressions(
        [f"{fmt_surd(a,b)} \\times {fmt_surd(c,d)}"],
        [fmt_surd(tc,rr)],
        [f"{a}\\times {c}={a*c},\\quad\\sqrt{{{b}}}\\times\\sqrt{{{d}}}=\\sqrt{{{b*d}}}={fmt_surd(cc,rr)}\\quad\\Rightarrow{fmt_surd(tc,rr)}"],
    ))

def gen_surd_multiply_chain():
    for _ in range(40):
        a=ri(2,3); b=random.choice([2,3,5]); c=ri(2,3); d=random.choice([2,3,5])
        e=ri(2,3); f=random.choice([2,3,5])
        fc,fr=simplify_surd(b*d*f); total=a*c*e*fc
        if total<=50: break
    return _ex("surd_multiply_chain", make_parts_from_expressions(
        [f"{fmt_surd(a,b)}\\times {fmt_surd(c,d)}\\times {fmt_surd(e,f)}"],
        [fmt_surd(total,fr)],
        [f"{a}\\times {c}\\times {e}={a*c*e},\\quad\\sqrt{{{b*d*f}}}={fmt_surd(fc,fr)}\\quad\\Rightarrow{fmt_surd(total,fr)}"],
    ))

def gen_surd_divide_simple():
    """√a / √b = √(a/b) — generate dynamically: pick b, multiplier k, so a=k²b."""
    for _ in range(50):
        b = random.choice([2, 3, 5, 6, 7])
        k = random.randint(2, 6)
        a = k * k * b   # ensures a/b = k² — perfect square
        c, r = simplify_surd(a // b)
        if r == 1 and c > 1:   # answer is integer
            break
    return _ex("surd_divide_simple", make_parts_from_expressions(
        [f"\\dfrac{{\\sqrt{{{a}}}}}{{\\sqrt{{{b}}}}}"],
        [fmt_surd(c, r)],
        [f"\\sqrt{{\\dfrac{{{a}}}{{{b}}}}}=\\sqrt{{{a//b}}}={fmt_surd(c,r)}"],
    ))

def gen_surd_divide_coeff():
    """a√b / c√d — divide coefficients and radicands dynamically."""
    for _ in range(50):
        d  = random.choice([2, 3, 5])
        k  = random.randint(1, 4)
        b  = d * k * k              # ensures b/d = k² — perfect square
        cd = random.choice([2, 3, 4])
        cn = cd * random.randint(2, 4)
        cc, cr = simplify_surd(b // d)
        res = (cn // cd) * cc
        if res <= 20 and cn % cd == 0 and cr >= 1:
            break
    else:
        cn, cd, b, d, res, cr = 6, 2, 6, 2, 3, 1; cc = 1
    return _ex("surd_divide_coeff", make_parts_from_expressions(
        [f"\\dfrac{{{fmt_surd(cn,b)}}}{{{fmt_surd(cd,d)}}}"],
        [fmt_surd(res, cr)],
        [f"\\dfrac{{{cn}}}{{{cd}}}={cn//cd},\\quad"
         f"\\dfrac{{\\sqrt{{{b}}}}}{{\\sqrt{{{d}}}}}=\\sqrt{{{b//d}}}={fmt_surd(cc,cr)}"
         f"\\quad\\Rightarrow{fmt_surd(res,cr)}"],
    ))

def gen_surd_simplify_basic():
    """√n — find largest perfect square factor dynamically."""
    for _ in range(50):
        c = random.randint(2, 12)   # coefficient
        r = random.choice([2, 3, 5, 6, 7, 10, 11, 13])  # non-square radicand
        n = c * c * r
        cc, rr = simplify_surd(n)
        if cc == c and rr == r:  # confirms our factorisation
            break
    sq = c * c
    return _ex("surd_simplify_basic", make_parts_from_expressions(
        [f"\\sqrt{{{n}}}"], [fmt_surd(c, r)],
        [f"\\sqrt{{{n}}}=\\sqrt{{{sq}\\times {r}}}=\\sqrt{{{sq}}}\\times\\sqrt{{{r}}}={c}\\sqrt{{{r}}}={fmt_surd(c,r)}"],
    ))

def gen_surd_simplify_coeff():
    """a√n — outer coefficient × simplified surd dynamically."""
    for _ in range(50):
        a   = random.randint(2, 5)
        ic  = random.randint(2, 6)   # inner surd coefficient
        r   = random.choice([2, 3, 5, 6, 7])
        n   = ic * ic * r            # inner radicand before simplification
        c   = a * ic                 # final coefficient
        if c <= 20:
            break
    return _ex("surd_simplify_coeff", make_parts_from_expressions(
        [f"{a}\\sqrt{{{n}}}"], [fmt_surd(c, r)],
        [f"{a}\\sqrt{{{n}}}={a}\\times {fmt_surd(ic,r)}={a*ic}\\sqrt{{{r}}}={fmt_surd(c,r)}"],
    ))

def gen_surd_simplify_fraction():
    """k/√n — rationalise denominator dynamically."""
    for _ in range(50):
        n  = random.choice([2, 3, 5, 6, 7])
        k  = random.randint(1, 6) * n   # ensure k/n simplifies cleanly
        from fractions import Fraction
        f  = Fraction(k, n)             # simplified coefficient
        c_num, c_den = f.numerator, f.denominator
        if c_den == 1:
            ans = fmt_surd(c_num, n)
        else:
            ans = fmt_frac(f"{c_num}\\sqrt{{{n}}}", str(c_den))
        break
    sol = (f"\\dfrac{{{k}}}{{\\sqrt{{{n}}}}}\\times\\dfrac{{\\sqrt{{{n}}}}}{{\\sqrt{{{n}}}}}"
           f"=\\dfrac{{{k}\\sqrt{{{n}}}}}{{{n}}}={ans}")
    return _ex("surd_simplify_fraction", make_parts_from_expressions(
        [fmt_frac(str(k), f"\\sqrt{{{n}}}")], [ans], [sol],
    ))

def gen_surd_simplify_product():
    for _ in range(40):
        a=random.choice([2,3,5,6,7,10]); b=random.choice([2,3,5,6,7,10])
        c,r=simplify_surd(a*b)
        if c>1 and r>1: break
    return _ex("surd_simplify_product", make_parts_from_expressions(
        [f"\\sqrt{{{a}}} \\times \\sqrt{{{b}}}"], [fmt_surd(c,r)],
        [f"\\sqrt{{{a*b}}}={fmt_surd(c,r)}"],
    ))

def gen_surd_simplify_mixed_ops():
    for _ in range(40):
        n1=random.choice([2,3,5,7]); c1=ri(2,5)
        n2=n1; c2=ri(1,4)
        a_n,a_c=simplify_surd(n1*ri(1,3)); b_n,b_c=simplify_surd(n2*ri(1,3))
        if a_n==n1 and b_n==n1: break
    else: n1=2; c1=3; c2=2; a_c=2; a_n=2; b_c=3; b_n=2
    q=f"{c1}\\sqrt{{{a_n*a_c**2}}}+{c2}\\sqrt{{{b_n*b_c**2}}}"
    r_c=c1*a_c+c2*b_c
    a_s=fmt_surd(r_c,n1)
    sol=f"{c1}\\times {a_c}\\sqrt{{{n1}}}+{c2}\\times {b_c}\\sqrt{{{n1}}}=({c1*a_c}+{c2*b_c})\\sqrt{{{n1}}}={fmt_surd(r_c,n1)}"
    return _ex("surd_simplify_mixed_ops", make_parts_from_expressions([q],[a_s],[sol]))

def gen_surd_simplify_chain():
    for _ in range(40):
        n=random.choice([2,3,5,6]); a=ri(2,4); b=ri(2,4)
        c1,r1=simplify_surd(n*a**2); c2,r2=simplify_surd(n*b**2)
        if r1==n and r2==n and a*c1+b*c2<=20: break
    else: n=2; a=2; b=3; c1=2; c2=3; r1=2; r2=2
    q=f"\\sqrt{{{n*a**2}}}+\\sqrt{{{n*b**2}}}"
    total=c1+c2; a_s=fmt_surd(total,n)
    sol=f"{fmt_surd(c1,r1)}+{fmt_surd(c2,r2)}={total}\\sqrt{{{n}}}"
    return _ex("surd_simplify_chain", make_parts_from_expressions([q],[a_s],[sol]))

# ── LT9s Surds: Expand & Rationalise ─────────────────────────────

def gen_surd_expand_single():
    """√m(√n + c) or √m(a√m + b) — dynamic distribution."""
    m = random.choice([2, 3, 5, 6])
    form = random.choice(["mixed", "same"])

    if form == "same":
        # √m(a√m + b) = am + b√m
        a = ri(1, 4); b = ri(1, 6)
        const = a * m
        q   = f"\\sqrt{{{m}}}({a}\\sqrt{{{m}}} + {b})"
        ans = f"{const} + {b}\\sqrt{{{m}}}"
        sol = f"\\sqrt{{{m}}}\\times {a}\\sqrt{{{m}}} + {b}\\sqrt{{{m}}} = {a}\\times {m} + {b}\\sqrt{{{m}}} = {ans}"
    else:
        # √m(√n + c) = √(mn) + c√m, simplify √(mn)
        n = random.choice([s for s in [2,3,5,7] if s != m])
        c = ri(1, 5)
        cc, rr = simplify_surd(m * n)
        ans = f"{fmt_surd(cc,rr)} + {c}\\sqrt{{{m}}}"
        q   = f"\\sqrt{{{m}}}(\\sqrt{{{n}}} + {c})"
        sol = f"\\sqrt{{{m*n}}} + {c}\\sqrt{{{m}}} = {fmt_surd(cc,rr)} + {c}\\sqrt{{{m}}}"

    return _ex("surd_expand_single", make_parts_from_expressions([q],[ans],[sol]))

def gen_surd_expand_double_simple():
    """(√m + a)(√m + b) = m + (a+b)√m + ab — dynamic."""
    m = random.choice([2, 3, 5, 7])
    a = ri(1, 5); b = ri(1, 5)
    # Always use + for simplicity; negate b sometimes
    b_sign = random.choice([1, -1])
    b2 = b * b_sign
    const  = m + a * b2
    surd_c = a + b2
    q   = (f"(\\sqrt{{{m}}} {'+' if a>=0 else '-'} {abs(a)})"
           f"(\\sqrt{{{m}}} {'+' if b2>=0 else '-'} {abs(b2)})")
    ans = (f"{const} {'+' if surd_c>=0 else '-'} {abs(surd_c)}\\sqrt{{{m}}}"
           if surd_c != 0 else str(const))
    sol = (f"m + (a+b)\\sqrt{{m}} + ab = {m} + {surd_c}\\sqrt{{{m}}} + {a*b2} = {ans}")
    return _ex("surd_expand_double_simple", make_parts_from_expressions([q],[ans],[sol]))

def gen_surd_expand_double_mixed():
    """(a√m + b)(c√m + d) — dynamic FOIL."""
    m  = random.choice([2, 3, 5])
    a  = ri(1, 3); b = ri(1, 4)
    c  = ri(1, 3); d_sign = random.choice([1, -1]); d = ri(1, 4) * d_sign
    # FOIL: a√m·c√m + a√m·d + b·c√m + b·d
    #     = acm + (ad + bc)√m + bd
    const  = a * c * m + b * d
    surd_c = a * d + b * c
    a_str  = "" if a == 1 else str(a)
    c_str  = "" if c == 1 else str(c)
    b_str  = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    d_str  = f"+ {abs(d)}" if d >= 0 else f"- {abs(d)}"
    q   = f"({a_str}\\sqrt{{{m}}} {b_str})({c_str}\\sqrt{{{m}}} {d_str})"
    ans_surd = (f"{'+' if surd_c >= 0 else '-'} {abs(surd_c)}\\sqrt{{{m}}}"
                if surd_c != 0 else "")
    ans = f"{const} {ans_surd}".strip()
    sol = (f"{a}\\times {c}\\times {m}={a*c*m},\\quad"
           f"({a}\\times {d}+{b}\\times {c})\\sqrt{{{m}}}={surd_c}\\sqrt{{{m}}},\\quad"
           f"\\text{{const}}={b*d} \\Rightarrow {ans}")
    return _ex("surd_expand_double_mixed", make_parts_from_expressions([q],[ans],[sol]))

def gen_surd_expand_conjugate():
    """
    (a√m + b√n)(a√m - b√n) = a²m - b²n
    Three forms chosen randomly each render:
      Form 1: (√m + b)(√m - b)        → m - b²
      Form 2: (a√m + √n)(a√m - √n)    → a²m - n
      Form 3: (a√m + b)(a√m - b)      → a²m - b²
    All values computed — nothing hardcoded.
    """
    form = random.choice([1, 2, 3])

    non_sq = [2, 3, 5, 6, 7, 10, 11, 13]   # non-perfect-square radicands

    if form == 1:
        # (√m + b)(√m - b) = m - b²
        m = random.choice(non_sq)
        b = ri(1, 5)
        ans = m - b**2
        q   = f"(\\sqrt{{{m}}}+{b})(\\sqrt{{{m}}}-{b})"
        sol = f"(\\sqrt{{{m}}})^2 - {b}^2 = {m} - {b**2} = {ans}"

    elif form == 2:
        # (a√m + √n)(a√m - √n) = a²m - n
        m = random.choice(non_sq)
        n = random.choice([s for s in non_sq if s != m])
        a = ri(1, 3)
        ans = a**2 * m - n
        a_str = "" if a == 1 else str(a)
        q   = f"({a_str}\\sqrt{{{m}}}+\\sqrt{{{n}}})({a_str}\\sqrt{{{m}}}-\\sqrt{{{n}}})"
        sol = f"({a_str}\\sqrt{{{m}}})^2 - (\\sqrt{{{n}}})^2 = {a**2}\\times {m} - {n} = {a**2*m} - {n} = {ans}"

    else:
        # (a√m + b)(a√m - b) = a²m - b²
        m = random.choice(non_sq)
        a = ri(1, 3)
        b = ri(1, 4)
        ans = a**2 * m - b**2
        a_str = "" if a == 1 else str(a)
        q   = f"({a_str}\\sqrt{{{m}}}+{b})({a_str}\\sqrt{{{m}}}-{b})"
        sol = f"({a_str}\\sqrt{{{m}}})^2 - {b}^2 = {a**2*m} - {b**2} = {ans}"

    return _ex("surd_expand_conjugate", make_parts_from_expressions(
        [q], [str(ans)], [sol],
    ))

def gen_surd_expand_square():
    for _ in range(40):
        a=random.choice([2,3,5,7]); b=ri(1,5)
        const=a+b*b; sc=2*b
        if const<=30 and sc<=15: break
    else: a=2; b=2; const=6; sc=4
    return _ex("surd_expand_square", make_parts_from_expressions(
        [f"(\\sqrt{{{a}}}+{b})^2"],
        [f"{const}+{sc}\\sqrt{{{a}}}"],
        [f"(\\sqrt{{{a}}})^2+2\\times {b}\\times\\sqrt{{{a}}}+{b}^2={a}+{sc}\\sqrt{{{a}}}+{b*b}={const}+{sc}\\sqrt{{{a}}}"],
    ))

def gen_surd_rationalise_simple():
    """a/√b — dynamic: pick b and a, compute rationalised form."""
    from fractions import Fraction
    b  = random.choice([2, 3, 5, 6, 7])
    a  = random.randint(1, 8)
    f  = Fraction(a, b)
    if f.denominator == 1:
        ans = fmt_surd(f.numerator, b)
    else:
        ans = fmt_frac(f"{f.numerator}\\sqrt{{{b}}}", str(f.denominator))
    sol = (f"\\dfrac{{{a}}}{{\\sqrt{{{b}}}}}\\times\\dfrac{{\\sqrt{{{b}}}}}{{\\sqrt{{{b}}}}}"
           f"=\\dfrac{{{a}\\sqrt{{{b}}}}}{{{b}}}={ans}")
    return _ex("surd_rationalise_simple", make_parts_from_expressions(
        [fmt_frac(str(a), f"\\sqrt{{{b}}}")], [ans], [sol],
    ))

def gen_surd_rationalise_coeff():
    """a/(b√c) — dynamic: pick values, compute simplified result."""
    from fractions import Fraction
    for _ in range(50):
        c   = random.choice([2, 3, 5, 6, 7])
        b   = random.choice([2, 3, 4, 5])
        a   = b * c * random.randint(1, 4)  # ensure a/(bc) simplifies cleanly
        f   = Fraction(a, b * c)
        if f.denominator == 1:
            ans = fmt_surd(f.numerator, c)
        else:
            ans = fmt_frac(f"{f.numerator}\\sqrt{{{c}}}", str(f.denominator))
        break
    sol = (f"\\dfrac{{{a}}}{{{b}\\sqrt{{{c}}}}}\\times\\dfrac{{\\sqrt{{{c}}}}}{{\\sqrt{{{c}}}}}"
           f"=\\dfrac{{{a}\\sqrt{{{c}}}}}{{{b*c}}}={ans}")
    return _ex("surd_rationalise_coeff", make_parts_from_expressions(
        [fmt_frac(str(a), f"{b}\\sqrt{{{c}}}")], [ans], [sol],
    ))

def gen_surd_rationalise_binomial():
    """a/(√m + b) — multiply by conjugate (√m - b), dynamic."""
    m = random.choice([2, 3, 5, 6, 7])
    b = ri(1, 3)
    a = ri(1, 4)
    denom_sq = m - b**2   # (√m)² - b²

    if denom_sq == 0:     # degenerate — pick new values
        m = 5; b = 1; a = 2; denom_sq = 4

    # a/(√m + b) × (√m - b)/(√m - b) = a(√m - b) / (m - b²)
    from math import gcd as _gcd_fn
    g   = _gcd_fn(abs(a), abs(denom_sq))
    nc  = a // g;  nd = denom_sq // g

    if abs(nd) == 1:
        ans = f"{nc}(\\sqrt{{{m}}}-{b})" if nc != 1 else f"\\sqrt{{{m}}}-{b}"
        if nd < 0: ans = f"-({ans})"
    else:
        ans = fmt_frac(f"{nc}(\\sqrt{{{m}}}-{b})", str(abs(nd)))
        if nd < 0: ans = f"-{ans}"

    sol = (f"\\dfrac{{{a}}}{{\\sqrt{{{m}}}+{b}}}\\times"
           f"\\dfrac{{\\sqrt{{{m}}}-{b}}}{{\\sqrt{{{m}}}-{b}}}"
           f"=\\dfrac{{{a}(\\sqrt{{{m}}}-{b})}}{{{m}-{b}^2}}"
           f"=\\dfrac{{{a}(\\sqrt{{{m}}}-{b})}}{{{denom_sq}}}={ans}")

    return _ex("surd_rationalise_binomial", make_parts_from_expressions(
        [fmt_frac(str(a), f"\\sqrt{{{m}}}+{b}")], [ans], [sol],
    ))

def gen_surd_rationalise_full():
    """(a + √m)/(√n - b) — full conjugate rationalisation, dynamic."""
    m  = random.choice([2, 3, 5, 6])
    n  = random.choice([2, 3, 5, 7])
    a  = ri(1, 4)
    b  = ri(1, 3)
    # denominator: √n - b,  conjugate: √n + b
    # (√n - b)(√n + b) = n - b²
    denom = n - b**2
    if denom == 0: n=5; b=1; denom=4
    # numerator after multiply: (a + √m)(√n + b) = a√n + ab + √(mn) + b√m
    mn_c, mn_r = simplify_surd(m * n)
    # Build display
    q_num = f"{a}+\\sqrt{{{m}}}"
    q_den = f"\\sqrt{{{n}}}-{b}"
    q     = fmt_frac(q_num, q_den)
    conj  = f"\\sqrt{{{n}}}+{b}"
    sol   = (f"\\dfrac{{({q_num})({conj})}}{{(\\sqrt{{{n}}})^2-{b}^2}}"
             f"=\\dfrac{{{a}\\sqrt{{{n}}}+{a*b}+{fmt_surd(mn_c,mn_r)}+{b}\\sqrt{{{m}}}}}{{{denom}}}")
    ans = sol.split("=")[-1]

    return _ex("surd_rationalise_full",
        parts=[
            make_part("a", question="State the conjugate of the denominator.",
                      answer_latex=conj,
                      solution_latex=f"\\text{{Conjugate of }}({q_den})\\text{{ is }}({conj})"),
            make_part("b", question="Multiply numerator and denominator by the conjugate and simplify.",
                      answer_latex=ans,
                      solution_latex=sol),
        ],
        context=f"Rationalise the denominator: ${q}$",
    )

def gen_surd_rationalise_sum():
    options=[
        {"q":    r"\dfrac{1}{\sqrt{2}-1}+\dfrac{1}{2-\sqrt{2}}",
         "ans":  r"1+\sqrt{2}",
         "sol_a": r"\dfrac{1}{\sqrt{2}-1}\times\dfrac{\sqrt{2}+1}{\sqrt{2}+1}=\dfrac{\sqrt{2}+1}{1}=\sqrt{2}+1 \\ \dfrac{1}{2-\sqrt{2}}\times\dfrac{2+\sqrt{2}}{2+\sqrt{2}}=\dfrac{2+\sqrt{2}}{2}=1+\dfrac{\sqrt{2}}{2}",
         "sol_b": r"(\sqrt{2}+1)+\left(1+\dfrac{\sqrt{2}}{2}\right)=2+\dfrac{3\sqrt{2}}{2}"},
        {"q":    r"\dfrac{2}{\sqrt{3}-1}+\dfrac{2}{3-\sqrt{3}}",
         "ans":  r"\sqrt{3}+1",
         "sol_a": r"\dfrac{2}{\sqrt{3}-1}\times\dfrac{\sqrt{3}+1}{\sqrt{3}+1}=\dfrac{2(\sqrt{3}+1)}{2}=\sqrt{3}+1 \\ \dfrac{2}{3-\sqrt{3}}\times\dfrac{3+\sqrt{3}}{3+\sqrt{3}}=\dfrac{2(3+\sqrt{3})}{6}=\dfrac{3+\sqrt{3}}{3}",
         "sol_b": r"(\sqrt{3}+1)+\dfrac{3+\sqrt{3}}{3}=\dfrac{3\sqrt{3}+3+3+\sqrt{3}}{3}=\dfrac{4\sqrt{3}+6}{3}"},
    ]
    e = random.choice(options)
    return _ex("surd_rationalise_sum",
        parts=[
            make_part("a", question="Rationalise each fraction separately.",
                      answer_latex=r"\text{See working}",
                      solution_latex=e["sol_a"]),
            make_part("b", question="Add the simplified fractions together.",
                      answer_latex=e["ans"],
                      solution_latex=e["sol_b"]),
        ],
        context=f"Rationalise and simplify: ${e['q']}$",
    )

def gen_surd_rationalise_frac_sum():
    options=[
        (18,10,2,r"3+5\sqrt{2}",
         r"\dfrac{\sqrt{18}}{\sqrt{2}}+\dfrac{10}{\sqrt{2}}=\sqrt{9}+\dfrac{10\sqrt{2}}{2}=3+5\sqrt{2}"),
        (12,6,3,r"2+2\sqrt{3}",
         r"\dfrac{\sqrt{12}}{\sqrt{3}}+\dfrac{6}{\sqrt{3}}=\sqrt{4}+\dfrac{6\sqrt{3}}{3}=2+2\sqrt{3}"),
        (50,10,2,r"5+5\sqrt{2}",
         r"\dfrac{\sqrt{50}}{\sqrt{2}}+\dfrac{10}{\sqrt{2}}=\sqrt{25}+\dfrac{10\sqrt{2}}{2}=5+5\sqrt{2}"),
    ]
    a,n,c,ans,sol=random.choice(options)
    return _ex("surd_rationalise_frac_sum", make_parts_from_expressions(
        [fmt_frac(f"\\sqrt{{{a}}}+{n}",f"\\sqrt{{{c}}}")], [ans], [sol],
    ))

def gen_surd_find_xy():
    options=[(5,2,27,10),(4,2,18,8),(3,2,11,6),(6,2,38,12),(7,2,51,14)]
    a,x,y,b=random.choice(options)
    return _ex("surd_find_xy", make_parts_from_expressions(
        [f"({a}-\\sqrt{{x}})^2 = y - {b}\\sqrt{{2}}"],
        [f"x={x},\\; y={y}"],
        [f"({a})^2-{2*a}\\sqrt{{x}}+x \\Rightarrow x={x},\\; y={a**2}+{x}={y}"],
    ))

# ══════════════════════════════════════════════════════════════════
# LT_SURDS — PYTHAGORAS WITH SURDS
# ══════════════════════════════════════════════════════════════════

def gen_surd_pythagoras():
    """
    Right-angled triangle: one unknown side, surd answers.
    Unknown can be hypotenuse OR either leg.
    """
    NON_SQ = [2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23]

    for _ in range(100):
        case = random.choice(["find_hyp", "find_leg_a", "find_leg_b"])

        if case == "find_hyp":
            sa = random.choice(NON_SQ)
            sb = random.choice(NON_SQ)
            sc = sa + sb
            a_val, a_rad = simplify_surd(sa)
            b_val, b_rad = simplify_surd(sb)
            c_val, c_rad = simplify_surd(sc)
            if c_val == 1:
                continue
            break

        elif case == "find_leg_a":
            sc = random.randint(12, 40)
            sb = random.choice(NON_SQ)
            sa = sc - sb
            if sa <= 0:
                continue
            a_val, a_rad = simplify_surd(sa)
            b_val, b_rad = simplify_surd(sb)
            c_val, c_rad = simplify_surd(sc)
            if a_val == 1:
                continue
            break

        else:  # find_leg_b
            sc = random.randint(12, 40)
            sa = random.choice(NON_SQ)
            sb = sc - sa
            if sb <= 0:
                continue
            a_val, a_rad = simplify_surd(sa)
            b_val, b_rad = simplify_surd(sb)
            c_val, c_rad = simplify_surd(sc)
            if b_val == 1:
                continue
            break
    else:
        raise ValueError("gen_surd_pythagoras: failed after 100 attempts")

    # ── Format labels ──────────────────────────────────────────
    la = fmt_surd(a_val, a_rad)
    lb = fmt_surd(b_val, b_rad)
    lc = fmt_surd(c_val, c_rad)

    # ── Build per-case SVG / solution / answer ─────────────────
    if case == "find_hyp":
        svg = SVG.figure("right_triangle",
                         sides={"a": la, "b": lb, "c": "x"},
                         show_angles=False, show_vertices=False)
        solution = steps(
            f"x^2 = ({la})^2 + ({lb})^2 = {sa} + {sb} = {sc}",
            f"x = \\sqrt{{{sc}}} = {lc}",
        )
        answer = lc
        context = "The diagram shows a right-angled triangle with legs " \
                  f"${la}$ and ${lb}$."

    elif case == "find_leg_a":
        svg = SVG.figure("right_triangle",
                         sides={"a": "x", "b": lb, "c": lc},
                         show_angles=False, show_vertices=False)
        solution = steps(
            f"x^2 = ({lc})^2 - ({lb})^2 = {sc} - {sb} = {sa}",
            f"x = \\sqrt{{{sa}}} = {la}",
        )
        answer = la
        context = "The diagram shows a right-angled triangle with hypotenuse " \
                  f"${lc}$ and one leg ${lb}$."

    else:  # find_leg_b
        svg = SVG.figure("right_triangle",
                         sides={"a": la, "b": "x", "c": lc},
                         show_angles=False, show_vertices=False)
        solution = steps(
            f"x^2 = ({lc})^2 - ({la})^2 = {sc} - {sa} = {sb}",
            f"x = \\sqrt{{{sb}}} = {lb}",
        )
        answer = lb
        context = "The diagram shows a right-angled triangle with hypotenuse " \
                  f"${lc}$ and one leg ${la}$."

    return _ex(
        "surd_pythagoras",
        parts=[
            make_part(
                "a",
                question="Find the exact value of $x$. Give your answer in simplest surd form.",
                answer_latex=answer,
                solution_latex=solution,
            )
        ],
        context=context,
        given=[],
        diagram_svg=svg,
    )
def gen_surd_trapezium_area():
    options=[
        (5,6,4,3,r"10\sqrt{2}-4",r"\frac{(4+k)\sqrt{3}}{2}=5\sqrt{6} \\ 4+k=10\sqrt{2} \\ k=10\sqrt{2}-4"),
        (6,6,2,3,r"12\sqrt{2}-2",r"\frac{(2+k)\sqrt{3}}{2}=6\sqrt{6} \\ 2+k=12\sqrt{2} \\ k=12\sqrt{2}-2"),
        (4,6,6,3,r"8\sqrt{2}-6",r"\frac{(6+k)\sqrt{3}}{2}=4\sqrt{6} \\ 6+k=8\sqrt{2} \\ k=8\sqrt{2}-6"),
    ]
    ac,sr,top,hsq,ans,sol=random.choice(options)
    ws_q=(f"\\text{{Trapezium: sides }}{top}\\text{{ cm, }}k\\text{{ cm,}}\\\\"
          f"\\text{{height }}\\sqrt{{{hsq}}}\\text{{ cm, area }}"
          f"{ac}\\sqrt{{{sr}}}\\text{{ cm}}^2\\text{{. Find }}k.")
    p=make_part("a",question=f"Show that $k = {ans}$.",
                answer_latex=ans,solution_latex=sol)
    p["ws_question_latex"]=ws_q
    return _ex("surd_trapezium_area",[p],
               context=(f"A trapezium has parallel sides of length ${top}$ cm and $k$ cm, "
                        f"a perpendicular height of $\\sqrt{{{hsq}}}$ cm, "
                        f"and an area of ${ac}\\sqrt{{{sr}}}$ cm²."),
               given=[]   # all info is in context — given is redundant here
               )


# ══════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    "multiply_simple":           gen_multiply_simple,
    "multiply_three_terms":      gen_multiply_three_terms,
    "multiply_coefficients":     gen_multiply_coefficients,
    "multiply_multivariable":    gen_multiply_multivariable,
    "divide_simple":             gen_divide_simple,
    "divide_coefficients":       gen_divide_coefficients,
    "divide_multivariable":      gen_divide_multivariable,
    "power_simple":              gen_power_simple,
    "power_coefficient":         gen_power_coefficient,
    "power_multivariable":       gen_power_multivariable,
    "power_negative_outer":      gen_power_negative_outer,
    "combine_same_power":        gen_combine_same_power,
    "negative_evaluate":         gen_negative_evaluate,
    "negative_fraction_base":    gen_negative_fraction_base,
    "negative_simplify":         gen_negative_simplify,
    "negative_divide":           gen_negative_divide_to_negative,
    "fractional_unit":           gen_fractional_unit,
    "fractional_nonunit":        gen_fractional_nonunit,
    "fractional_negative":       gen_fractional_negative,
    "fractional_of_fraction":    gen_fractional_of_fraction,
    "zero_index":                gen_zero_index,
    "fraction_simple":           gen_fraction_simple,
    "fraction_complex":          gen_fraction_complex,
    "fraction_multivariable":    gen_fraction_multivariable,
    "fraction_nested_power":     gen_fraction_nested_power,
    "numeric_multiply":          gen_numeric_multiply,
    "numeric_divide":            gen_numeric_divide,
    "numeric_mixed":             gen_numeric_mixed,
    "write_as_power":            gen_write_as_power,
    "find_missing_index":        gen_find_missing_index,
    "find_missing_divide":       gen_find_missing_divide,
    "find_missing_power":        gen_find_missing_power,
    "identify_error":            gen_identify_error,
    "surd_add_simple":           gen_surd_add_simple,
    "surd_subtract_simple":      gen_surd_subtract_simple,
    "surd_add_mixed":            gen_surd_add_mixed,
    "surd_subtract_mixed":       gen_surd_subtract_mixed,
    "surd_multiply_simple":      gen_surd_multiply_simple,
    "surd_multiply_coeff":       gen_surd_multiply_coeff,
    "surd_multiply_chain":       gen_surd_multiply_chain,
    "surd_divide_simple":        gen_surd_divide_simple,
    "surd_divide_coeff":         gen_surd_divide_coeff,
    "surd_simplify_basic":       gen_surd_simplify_basic,
    "surd_simplify_coeff":       gen_surd_simplify_coeff,
    "surd_simplify_fraction":    gen_surd_simplify_fraction,
    "surd_simplify_product":     gen_surd_simplify_product,
    "surd_simplify_mixed_ops":   gen_surd_simplify_mixed_ops,
    "surd_simplify_chain":       gen_surd_simplify_chain,
    "surd_expand_single":        gen_surd_expand_single,
    "surd_expand_double_simple": gen_surd_expand_double_simple,
    "surd_expand_double_mixed":  gen_surd_expand_double_mixed,
    "surd_expand_conjugate":     gen_surd_expand_conjugate,
    "surd_expand_square":        gen_surd_expand_square,
    "surd_rationalise_simple":   gen_surd_rationalise_simple,
    "surd_rationalise_coeff":    gen_surd_rationalise_coeff,
    "surd_rationalise_binomial": gen_surd_rationalise_binomial,
    "surd_rationalise_full":     gen_surd_rationalise_full,
    "surd_rationalise_sum":      gen_surd_rationalise_sum,
    "surd_rationalise_frac_sum": gen_surd_rationalise_frac_sum,
    "surd_find_xy":              gen_surd_find_xy,
    "surd_pythagoras":           gen_surd_pythagoras,
    "surd_trapezium_area":       gen_surd_trapezium_area,
}


# ══════════════════════════════════════════════════════════════════
# GENERATE — called by QMD, identical pattern for all units
# ══════════════════════════════════════════════════════════════════

def generate(types, seed=None, count=6, counts=None, show_solutions=False):
    """
    Generate exercises.

    types         : list of type name strings from REGISTRY
    seed          : random seed for reproducibility
    count         : default number of parts per grid exercise
    counts        : dict of per-type overrides {"surd_pythagoras": 1}
    show_solutions: include solutions in rendered output
    """
    if seed is not None:
        random.seed(seed)

    _counts = counts or {}
    exercises_raw = []

    for ex_type in types:
        if ex_type not in REGISTRY:
            raise ValueError(f"Unknown type: '{ex_type}'. Available: {sorted(REGISTRY.keys())}")

        gen_fn = REGISTRY[ex_type]
        n      = _counts.get(ex_type, count)

        # List-type exercises (diagram, context, word problems)
        # should default to 1 unless explicitly overridden
        # Generate one, check if it's a list type, cap at 1 if so
        test_ex = gen_fn()
        if test_ex is None:
            continue
        is_list = (test_ex.get("context") or test_ex.get("has_diagram")
                   or (test_ex["parts"] and not all(p["expression"] for p in test_ex["parts"])))
        if is_list and ex_type not in _counts:
            n = 1   # list exercises default to 1 unless explicitly set

        # Generate remaining n-1 (we already have test_ex)
        raw_exercises = [test_ex]
        for _ in range(n - 1):
            ex = gen_fn()
            if ex is not None:
                raw_exercises.append(ex)

        if not raw_exercises:
            continue

        # Merge parts from all generated exercises into one
        merged = raw_exercises[0]
        if len(raw_exercises) > 1:
            labels = list("abcdefghijklmnopqrstuvwxyz")
            all_parts = []
            for i, ex in enumerate(raw_exercises):
                for j, p in enumerate(ex["parts"]):
                    p["label"] = labels[len(all_parts)]
                    all_parts.append(p)
            merged["parts"] = all_parts

        exercises_raw.append(merged)

    return build_output(
        exercises_raw,
        show_solutions = show_solutions,
        worksheet_meta = {
            "title":          "Indices & Surds",
            "unit":           "Unit 2: Indices & Surds",
            "date":           str(date.today()),
            "seed":           seed,
            "show_solutions": show_solutions,
        },
        unit_prefix = "u2",
    )


# ── Pyodide entry point ───────────────────────────────────────────
def generate_session(types_json, seed=None, count=6, counts_json=None):
    types  = json.loads(types_json)
    counts = json.loads(counts_json) if counts_json else None
    return json.dumps(generate(types=types, seed=seed, count=count, counts=counts))


# ── CLI ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Indices & Surds exercises")
    parser.add_argument("--types", nargs="+", default=["multiply_simple"])
    parser.add_argument("--seed",  type=int, default=None)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--solutions", action="store_true")
    parser.add_argument("--list-types", action="store_true")
    args = parser.parse_args()

    if args.list_types:
        diff_badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}
        for k in sorted(REGISTRY.keys()):
            d = METADATA.get(k,{}).get("difficulty","?")
            print(f"  {diff_badge.get(d,'⚪')}  {k:<35} {METADATA.get(k,{}).get('subtopic','')}")
    else:
        result = generate(types=args.types, seed=args.seed,
                          count=args.count, show_solutions=args.solutions)
        print(f"Generated {len(result['_exercises_qmd'])} exercises.")
        for ex in result["_exercises_qmd"]:
            print(f"\n{'='*60}")
            print(f"Type: {ex['type']} | Difficulty: {ex['difficulty']} | Layout: {ex['layout']}")
            print(ex["rendered"][:400])
