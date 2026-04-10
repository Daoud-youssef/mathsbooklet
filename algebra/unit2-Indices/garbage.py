import random
from datetime import date
import json
from collections import defaultdict

# ══════════════════════════════════════════════════════════════════
# CONSTANTS & HELPERS
# ══════════════════════════════════════════════════════════════════

PART_LABELS = "abcdefghijklmnopqrstuvwxyz"

def _render_stimulus(stim):
    if not stim: return ""
    return f"$$\n{stim}\n$$\n" if "\\" in stim else f"{stim}\n"

# ══════════════════════════════════════════════════════════════════
# CORE ENGINE: INDEX OBJECTS
# ══════════════════════════════════════════════════════════════════

class IndexTerm:
    def __init__(self, coeff=1, base="x", exp=1):
        self.coeff = coeff
        self.base = str(base)
        self.exp = exp

    def __mul__(self, other):
        if self.base != other.base:
            return f"{self.to_latex()}{other.to_latex()}"
        return IndexTerm(self.coeff * other.coeff, self.base, self.exp + other.exp)

    def __truediv__(self, other):
        if isinstance(self.coeff, int) and isinstance(other.coeff, int):
            if self.coeff % other.coeff == 0:
                c = self.coeff // other.coeff
            else:
                c = f"\\frac{{{self.coeff}}}{{{other.coeff}}}"
        else:
            c = f"\\frac{{{self.coeff}}}{{{other.coeff}}}"
        return IndexTerm(c, self.base, self.exp - other.exp)

    def __pow__(self, pwr):
        if isinstance(self.coeff, int) and pwr >= 0:
            new_c = self.coeff ** pwr
        else:
            new_c = f"{self.coeff}^{{{pwr}}}"
        return IndexTerm(new_c, self.base, self.exp * pwr)

    def to_latex(self):
        c = "" if self.coeff == 1 else str(self.coeff)
        if self.exp == 0: return str(self.coeff)
        if self.exp == 1: return f"{c}{self.base}"
        e_str = f"{{{self.exp}}}"
        return f"{c}{self.base}^{e_str}"

# ══════════════════════════════════════════════════════════════════
# GENERATORS
# ══════════════════════════════════════════════════════════════════

def gen_multiply_simple():
    v = random.choice("abcdpqr")
    m, n = random.randint(2, 8), random.randint(2, 8)
    t1, t2 = IndexTerm(1, v, m), IndexTerm(1, v, n)
    res = t1 * t2
    return {
        "equation": f"{t1.to_latex()} \\times {t2.to_latex()}",
        "answer": res.to_latex(),
        "solution": f"{v}^{{{m}+{n}}} = {res.to_latex()}"
    }

def gen_divide_coefficients():
    v = random.choice("xyz")
    c2 = random.randint(2, 5)
    c1 = c2 * random.randint(2, 6)
    m, n = random.randint(7, 12), random.randint(2, 6)
    t1, t2 = IndexTerm(c1, v, m), IndexTerm(c2, v, n)
    res = t1 / t2
    return {
        "equation": f"{t1.to_latex()} \\div {t2.to_latex()}",
        "answer": res.to_latex(),
        "solution": f"({c1} \\div {c2}){v}^{{{m}-{n}}} = {res.to_latex()}"
    }

def gen_power_coefficient():
    v, m, p = random.choice("hkmn"), random.randint(2, 5), random.randint(2, 4)
    c = random.randint(2, 4)
    t = IndexTerm(c, v, m)
    res = t ** p
    return {
        "equation": f"({t.to_latex()})^{{{p}}}",
        "answer": res.to_latex(),
        "solution": f"{c}^{{{p}}} \\times {v}^{{{m} \\times {p}}} = {res.to_latex()}"
    }

def gen_negative_evaluate():
    base = random.choice([2, 3, 5, 10])
    p = random.randint(1, 3)
    val = base ** p
    return {
        "equation": f"{base}^{{-{p}}}",
        "answer": f"\\frac{{1}}{{{val}}}",
        "solution": f"\\frac{{1}}{{{base}^{{{p}}}}} = \\frac{{1}}{{{val}}}"
    }
    

def gen_surd_simplify():
    # Square numbers: 4, 9, 16, 25, 36
    square = random.choice([4, 9, 16, 25])
    non_square = random.choice([2, 3, 5, 6, 7])
    num = square * non_square
    coeff = int(square**0.5)
    return {
        "equation": f"\\sqrt{{{num}}}",
        "answer": f"{coeff}\\sqrt{{{non_square}}}",
        "solution": f"\\sqrt{{{square} \\times {non_square}}} = \\sqrt{{{square}}} \\times \\sqrt{{{non_square}}} = {coeff}\\sqrt{{{non_square}}}"
    }

def gen_surd_multiply():
    a, b = random.sample([2, 3, 5, 6, 7, 10], 2)
    return {
        "equation": f"\\sqrt{{{a}}} \\times \\sqrt{{{b}}}",
        "answer": f"\\sqrt{{{a*b}}}",
        "solution": f"\\sqrt{{{a} \\times {b}}} = \\sqrt{{{a*b}}}"
    }

def gen_rationalise_simple():
    num = random.randint(1, 10)
    den = random.choice([2, 3, 5, 6, 7])
    return {
        "equation": f"\\frac{{{num}}}{{\\sqrt{{{den}}}}}",
        "answer": f"\\frac{{{num}\\sqrt{{{den}}}}}{{{den}}}",
        "solution": f"\\frac{{{num}}}{{\\sqrt{{{den}}}}} \\times \\frac{{\\sqrt{{{den}}}}}{{\\sqrt{{{den}}}}} = \\frac{{{num}\\sqrt{{{den}}}}}{{{den}}}"
    }
    
def gen_surd_algebra_find_xy():
    """Based on Question 11/12: Find x and y in (a - √x)² = y - b√2."""
    # Pattern: (5 - √x)² = 25 - 10√x + x = (25+x) - 10√x
    a = random.randint(3, 6)
    x = 2 # Usually a small prime for these exam questions
    y = a**2 + x
    b = 2 * a
    return {
        "equation": rf"({a} - \sqrt{{x}})^2 = y - {b}\sqrt{{2}}",
        "answer": rf"x=2, y={y}",
        "solution": rf"({a} - \sqrt{{x}})^2 = {a**2} - {2*a}\sqrt{{x}} + x \\ \text{{Match terms: }} {2*a}\sqrt{{x}} = {b}\sqrt{{2}} \rightarrow x=2 \\ y = {a**2} + x = {a**2} + 2 = {y}"
    }

def gen_rationalise_sum():
    """Based on Question 7/18: (√a + √b) / √c."""
    # Pattern: (√18 + 10) / √2 = √9 + 10/√2 = 3 + 5√2
    a_sq = random.choice([9, 16, 25])
    c = 2
    a = a_sq * c
    num2 = random.choice([4, 6, 8, 10])
    return {
        "equation": rf"\frac{{\sqrt{{{a}}} + {num2}}}{{\sqrt{{{c}}}}}",
        "answer": rf"{int(a_sq**0.5)} + {num2//c}\sqrt{{{c}}}",
        "solution": rf"\frac{{\sqrt{{{a}}}}}{{\sqrt{{{c}}}}} + \frac{{{num2}}}{{\sqrt{{{c}}}}} = \sqrt{{{a//c}}} + \frac{{{num2}\sqrt{{{c}}}}}{{{c}}} = {int(a_sq**0.5)} + {num2//c}\sqrt{{{c}}}"
    }

def gen_trapezium_area():
    """Based on Question 13: Area of trapezium with surds."""
    h = 3 # height is √3
    parallel_a = 4
    # Area = 0.5 * (a + k) * h = 5√6
    # (4 + k) * √3 = 10√6 -> 4 + k = 10√2 -> k = 10√2 - 4
    area_coeff = random.choice([5, 10, 15])
    return {
        "stimulus": rf"A trapezium has area ${area_coeff}\sqrt{{6}}\text{{ cm}}^2$, height $\sqrt{{3}}\text{{ cm}}$, and top side $4\text{{ cm}}$.",
        "parts": [{"label": "a", "text": "Calculate the length of the base $k$ in the form $a\sqrt{b} - c$."}],
        "answer": rf"{area_coeff*2}\sqrt{{2}} - 4",
        "solution": rf"\text{{Area}} = \frac{{(4+k)\sqrt{{3}}}}{{2}} = {area_coeff}\sqrt{{6}} \\ (4+k)\sqrt{{3}} = {area_coeff*2}\sqrt{{6}} \\ 4+k = \frac{{{area_coeff*2}\sqrt{{6}}}}{{\sqrt{{3}}}} = {area_coeff*2}\sqrt{{2}} \\ k = {area_coeff*2}\sqrt{{2}} - 4"
    }
    
    import random
from datetime import date
import json

# ══════════════════════════════════════════════════════════════════
# GEOMETRY HELPERS (SVG)
# ══════════════════════════════════════════════════════════════════

def draw_triangle_svg(a_label, b_label, c_label):
    """Draws a right-angled triangle with labels for surd problems."""
    return f'''
<svg width="200" height="120" viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg">
  <path d="M 40 20 L 40 100 L 160 100 Z" fill="none" stroke="black" stroke-width="2"/>
  <rect x="40" y="90" width="10" height="10" fill="none" stroke="black" stroke-width="1"/>
  <text x="15" y="65" font-family="serif" font-style="italic" font-size="14">{a_label}</text>
  <text x="90" y="115" font-family="serif" font-style="italic" font-size="14">{b_label}</text>
  <text x="110" y="55" font-family="serif" font-style="italic" font-size="14">{c_label}</text>
</svg>
'''

═══════════════════════════════════════════════════════════════

def gen_surd_expansion_double():
    """Questions like (a + √b)(c + √d) - Question 14 in screenshots."""
    a = random.randint(1, 5)
    b_base = random.choice([2, 3, 5])
    c = random.randint(1, 5)
    # Generate (a + √b)(c + √b) for simplicity or different roots
    return {
        "equation": rf"({a} + \sqrt{{{b_base}}})({c} + \sqrt{{{b_base}}})",
        "answer": rf"{a*c + b_base} + {a+c}\sqrt{{{b_base}}}",
        "solution": rf"{a*c} + {a}\sqrt{{{b_base}}} + {c}\sqrt{{{b_base}}} + {b_base} = {a*c + b_base} + {a+c}\sqrt{{{b_base}}}"
    }

def gen_rationalise_conjugate():
    """Questions like 6 / (3 - √2) - Question 17 in screenshots."""
    num = random.randint(2, 8)
    a = random.randint(2, 5)
    b = random.choice([2, 3, 5])
    denom_val = a**2 - b
    return {
        "equation": rf"\frac{{{num}}}{{{a} - \sqrt{{{b}}}}}",
        "answer": rf"\frac{{{num}({a} + \sqrt{{{b}}})}}{{{denom_val}}}",
        "solution": rf"\frac{{{num}}}{{{a} - \sqrt{{{b}}}}} \times \frac{{{a} + \sqrt{{{b}}}}}{{{a} + \sqrt{{{b}}}}} = \frac{{{num}({a} + \sqrt{{{b}}})}}{{{a}^2 - {b}}}"
    }

def gen_pythagoras_surd():
    """Right angled triangle problems - Question 3 in screenshots."""
    # Finding hypotenuse x: x^2 = a + b
    a_base = random.choice([2, 3, 5])
    b_base = random.choice([6, 7, 10])
    a_sq, b_sq = random.randint(2, 10), random.randint(2, 10)
    
    # Side labels
    side_a = rf"\sqrt{{{a_sq}}}"
    side_b = rf"\sqrt{{{b_sq}}}"
    
    return {
        "stimulus": draw_triangle_svg(side_a, side_b, "x"),
        "parts": [
            {"label": "a", "text": rf"Calculate the missing side $x$. Give your answer as a simplified surd."}
        ],
        "answer": rf"\sqrt{{{a_sq + b_sq}}}",
        "solution": rf"x^2 = (\sqrt{{{a_sq}}})^2 + (\sqrt{{{b_sq}}})^2 \\ x^2 = {a_sq} + {b_sq} = {a_sq + b_sq} \\ x = \sqrt{{{a_sq+b_sq}}}"
    }




# ══════════════════════════════════════════════════════════════════
# REGISTRY & MAPPING
# ══════════════════════════════════════════════════════════════════

SKILLS_MAP = {
    "LT1": ["Multiplication Law", "Adding indices"],
    "LT2": ["Division Law", "Subtracting indices", "Coefficients"],
    "LT3": ["Power of a Power", "Multiplying indices"],
    "LT4": ["Negative indices", "Reciprocals"],
    "LT_S1": ["Simplifying Surds", "Square factors"],
    "LT_S2": ["Surd Operations", "Multiplying Surds"],
    "LT_S3": ["Rationalising", "Denominators"],
}

INSTRUCTIONS_MAP = {
    "multiply_simple": "Simplify the following using the first law of indices.",
    "divide_coefficients": "Simplify the following expressions involving coefficients.",
    "power_coefficient": "Expand the brackets using the power of a power law.",
    "negative_evaluate": "Evaluate the following without using a calculator.",
    "surd_simplify": "Simplify the following surds by extracting square factors.",
    "surd_multiply": "Multiply the surds and simplify where possible.",
    "rationalise_simple": "Rationalise the denominator for each expression.",
}

REGISTRY = {
    "multiply_simple":    (gen_multiply_simple,      6, "grid", "easy",   "LT1"),
    "divide_coefficients": (gen_divide_coefficients, 6, "grid", "medium", "LT2"),
    "power_coefficient":   (gen_power_coefficient,    6, "grid", "medium", "LT3"),
    "negative_evaluate":   (gen_negative_evaluate,   6, "grid", "hard",   "LT4"),
    "surd_simplify":      (gen_surd_simplify,      6, "grid", "easy",   "LT_S1"),
    "surd_multiply":      (gen_surd_multiply,      6, "grid", "medium", "LT_S2"),
    "rationalise_simple": (gen_rationalise_simple, 6, "grid", "hard",   "LT_S3"),

}

# ══════════════════════════════════════════════════════════════════
# RENDERING FUNCTIONS (Uniform across all units)
# ══════════════════════════════════════════════════════════════════

def render_grid_block(ex_num, items, instruction, lt, skills, show_solutions):
    n = len(items)
    wide = any(it.get("is_wide") for it in items)
    col = 12 if (wide or n == 1) else {2: 6, 3: 4, 4: 3, 6: 4}.get(n, 4)

    lines = [f"::::: {{#exr-u2-{ex_num}}}\n",
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
                      "$$\n", it["solution"], "\n$$\n"]
        lines.append(":::")

    lines += ["", "::: exercise-meta",
              '<div class="skill-container">',
              *[f'  <span class="skill-badge">{s}</span>' for s in skills],
              "</div>", ":::", "", ":::::\n"]
    return "\n".join(lines)

def render_list_block(ex_num, item, instruction, lt, skills, show_solutions):
    inst = item.get("override_instruction") or instruction
    lines = [f"::::: {{#exr-u2-{ex_num}}}\n"]
    if inst: lines.append(f"*{inst}*\n")
    if "stimulus" in item: lines.append(_render_stimulus(item["stimulus"]))
    
    for p in item.get("parts", []):
        lines.append(f"**({p['label']})** {p['text']}\n")

    if show_solutions:
        lines += ['::: {.callout-tip collapse="true"}', "## 🔍 View Solution\n"]
        lines += ["$$\n", item["solution"], "\n$$\n", ":::"]

    lines += ["", "::: exercise-meta", '<div class="skill-container">',
              *[f'  <span class="skill-badge">{s}</span>' for s in skills],
              "</div>", ":::", "", ":::::\n"]
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
# MAIN GENERATE FUNCTION
# ══════════════════════════════════════════════════════════════════

def generate(types, seed=None, count=None, show_solutions=False):
    if seed is not None:
        random.seed(seed)

    exercises_qmd = []
    exercises_ws  = []
    ex_num = 1

    for ex_type in types:
        if ex_type not in REGISTRY: continue

        gen_fn, default_count, layout, difficulty, lt = REGISTRY[ex_type]
        n = count if count is not None else default_count
        instruction = INSTRUCTIONS_MAP.get(ex_type, "")
        skills = SKILLS_MAP.get(lt, [ex_type])

        if layout == "grid":
            items = []
            for j in range(n):
                item = gen_fn()
                item["label"] = PART_LABELS[j]
                items.append(item)
            
            rendered = render_grid_block(ex_num, items, instruction, lt, skills, show_solutions)
            exercises_qmd.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "difficulty": difficulty, "rendered": rendered,
                "answer": "; ".join(it["answer"] for it in items),
            })
            exercises_ws.append({
                "number": ex_num, "title": instruction, "difficulty": difficulty,
                "parts": [{"label": it["label"], "question_latex": it["equation"], "answer_latex": it["answer"]} for it in items],
                "meta": {"difficulty": difficulty, "lt": lt, "skills": skills},
            })

        else: # list layout
            item = gen_fn()
            rendered = render_list_block(ex_num, item, instruction, lt, skills, show_solutions)
            exercises_qmd.append({
                "number": ex_num, "type": ex_type, "lt": lt,
                "difficulty": difficulty, "rendered": rendered,
                "answer": item["answer"],
            })
            exercises_ws.append({
                "number": ex_num, "title": instruction, "difficulty": difficulty,
                "parts": item.get("parts", []),
                "meta": {"difficulty": difficulty, "lt": lt, "skills": skills},
            })
            
        ex_num += 1

    return {
        "_exercises_qmd": exercises_qmd,
        "exercises": exercises_ws,
        "worksheet": {
            "title": "Laws of Indices",
            "unit": "Unit 2: Indices",
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
    # Test execution
    data = generate(types=["multiply_simple", "divide_coefficients"], seed=42, show_solutions=True)
    for ex in data["_exercises_qmd"]:
        print(ex["rendered"])
