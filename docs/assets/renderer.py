"""
renderer.py
===========
Single rendering layer for the Math-Booklet project.

Location : assets/renderer.py
Import   : from renderer import render_exercise, render_ws_exercise

QMD files call generate() and print ex["rendered"] — nothing else.
This file owns all markdown/HTML generation for both QMD and worksheet.

Public API
----------
render_exercise(ex, ex_num, show_solutions)
    → fills ex["rendered"] with complete QMD markdown block
    → fills ex["layout"] with "grid" or "list"
    → returns ex (mutated in place)

render_ws_exercise(ex)
    → returns worksheet-ready dict for worksheet.js
"""

from exercise_schema import detect_layout, ws_question_latex, PART_LABELS


# ══════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════

# Column count → Quarto grid class
_GRID_COLS = {1: 12, 2: 6, 3: 4, 4: 3, 6: 4}


def _col(n_parts, has_wide=False):
    if has_wide or n_parts == 1:
        return 12
    return _GRID_COLS.get(n_parts, 4)


# ══════════════════════════════════════════════════════════════════
# QMD RENDERER
# ══════════════════════════════════════════════════════════════════

def render_exercise(ex: dict, ex_num: int,
                    show_solutions: bool = False,
                    unit_prefix: str = "u") -> dict:
    """
    Render a complete exercise to QMD markdown.
    Mutates ex["rendered"] and ex["layout"].
    Returns ex.
    """
    ex["number"] = ex_num
    layout = detect_layout(ex)
    ex["layout"] = layout

    if layout == "grid":
        ex["rendered"] = _render_grid(ex, ex_num, show_solutions, unit_prefix)
    else:
        ex["rendered"] = _render_list(ex, ex_num, show_solutions, unit_prefix)

    return ex


# ── Grid renderer ─────────────────────────────────────────────────

def _render_grid(ex, ex_num, show_solutions, unit_prefix):
    parts  = ex["parts"]
    n      = len(parts)
    col    = _col(n)
    lines  = []

    # Exercise header
    lines += [
        f"::::: {{#exr-{unit_prefix}-{ex_num}}}\n",
        f"*{ex['instruction']}*\n",
        ":::: {.grid}\n",
    ]

    # Part cells — expression only
    for p in parts:
        lines += [
            f"::: {{.g-col-{col}}}\n",
            f"**{p['label']})** $\\displaystyle {p['expression']}$\n",
            ":::\n",
        ]
    lines.append("::::\n")

    # Solutions
    if show_solutions:
        lines += [
            '::: {.callout-tip collapse="true"}',
            "## 🔍 View Solutions\n",
        ]
        # solution diagram (grid exercises rarely have one, but support it)
        sol_svg = ex.get("solution_svg", "")
        if sol_svg:
            lines += [
                "::: {.content-visible when-format=\"html\"}",
                sol_svg + "\n",
                ":::\n",
            ]
        for p in parts:
            sol = p.get("solution_latex") or p["answer_latex"]
            lines += [
                f"**{p['label']})**\n",
                "$$\n\\begin{aligned}",
                sol,
                "\\end{aligned}\n$$\n",
            ]
        lines.append(":::\n")

    # Skill badges + close
    lines += _skill_badges(ex["meta"]["skills"])
    lines.append(":::::\n")
    return "\n".join(lines)


# ── List renderer ─────────────────────────────────────────────────

def _render_list(ex, ex_num, show_solutions, unit_prefix):
    lines = []

    # Exercise header
    lines += [
        f"::::: {{#exr-{unit_prefix}-{ex_num}}}\n",
        f"*{ex['instruction']}*\n",
    ]

    # Context paragraph
    if ex["context"]:
        lines.append(ex["context"] + "\n")

    # Given — rendered as a compact inline list
    if ex["given"]:
        given_str = " · ".join(f"${g}$" if "\\" in g else g
                                for g in ex["given"])
        lines.append(f"**Given:** {given_str}\n")

    # Diagram — HTML only, skip for PDF
    if ex["has_diagram"] and ex["diagram_svg"]:
        lines.append("::: {.content-visible when-format=\"html\"}")
        lines.append(ex["diagram_svg"] + "\n")
        lines.append(":::\n")

    # Top-level expression (rare — e.g. "factorise this expression")
    if ex["expression"]:
        lines.append(f"$$\\displaystyle {ex['expression']}$$\n")

    # Parts
    for p in ex["parts"]:
        # Part expression (if set) shown above the question text
        if p["expression"] and p["question"]:
            lines.append(
                f"**({p['label']})** $\\displaystyle {p['expression']}$"
                f" — {p['question']}\n"
            )
        elif p["expression"]:
            lines.append(
                f"**({p['label']})** $\\displaystyle {p['expression']}$\n"
            )
        else:
            lines.append(f"**({p['label']})** {p['question']}\n")

    # Hint (collapsed)
    if ex["hint"]:
        lines += [
            '::: {.callout-note collapse="true"}',
            "## 💡 Hint\n",
            f"$\\displaystyle {ex['hint']}$\n" if "\\" in ex["hint"]
            else ex["hint"] + "\n",
            ":::\n",
        ]

    # Solutions (collapsed)
    if show_solutions:
        lines += [
            '::: {.callout-tip collapse="true"}',
            "## 🔍 View Solution\n",
        ]
        # Solution diagram — same triangle with answer substituted for x
        sol_svg = ex.get("solution_svg", "")
        if sol_svg:
            lines += [
                "::: {.content-visible when-format=\"html\"}",
                sol_svg + "\n",
                ":::\n",
            ]
        for p in ex["parts"]:
            sol = p.get("solution_latex") or p["answer_latex"]
            if sol:
                lines += [
                    f"**{p['label']})**\n",
                    "$$\n\\begin{aligned}",
                    sol,
                    "\\end{aligned}\n$$\n",
                ]
        lines.append(":::\n")

    # Skill badges + close
    lines += _skill_badges(ex["meta"]["skills"])
    lines.append(":::::\n")
    return "\n".join(lines)


# ── Shared components ─────────────────────────────────────────────

def _skill_badges(skills):
    if not skills:
        return []
    badges = "\n".join(
        f'  <span class="skill-badge">{s}</span>' for s in skills
    )
    return [
        "",
        "::: exercise-meta",
        '<div class="skill-container">',
        badges,
        "</div>",
        ":::\n",
    ]


# ══════════════════════════════════════════════════════════════════
# WORKSHEET RENDERER
# ══════════════════════════════════════════════════════════════════

def render_ws_exercise(ex: dict) -> dict:
    """
    Build the worksheet-ready dict for worksheet.js.

    title       → subtopic (shown next to Ex N.)
    instruction → full instruction + context on new line
    parts       → each part has question_latex and answer_latex
    """
    layout = ex.get("layout") or detect_layout(ex)
    ex["layout"] = layout

    ws_parts = []
    for p in ex["parts"]:
        ws_parts.append({
            "label":          p["label"],
            "question_latex": ws_question_latex(ex, p),
            "answer_latex":   p["answer_latex"],
        })

    return {
        "number":      ex["number"],
        "type":        ex["type"],
        "lt":          ex["lt"],
        "difficulty":  ex["difficulty"],
        "title":       ex["subtopic"],
        "instruction": _ws_instruction(ex),
        "diagram_svg": ex.get("diagram_svg", ""),   # SVG string for worksheet
        "parts":       ws_parts,
        "meta": {
            "difficulty": ex["difficulty"],
            "lt":         ex["lt"],
            "skills":     ex["meta"]["skills"],
        },
    }


def _ws_instruction(ex: dict) -> str:
    """
    Build the instruction line shown above an exercise in the worksheet.
    Plain text only — no LaTeX, no $ markers.
    Format: "Instruction — Context sentence."
    Given is omitted from instruction (shown in part cell instead).
    """
    layout = ex.get("layout") or detect_layout(ex)
    if layout == "grid" or not ex["context"]:
        return ex["instruction"]

    # Strip any markdown $ from context for plain-text instruction line
    import re
    ctx = ex["context"].split(".")[0] + "."
    ctx = re.sub(r'\$([^$]+)\$', r'\1', ctx)   # remove $ markers
    ctx = re.sub(r'\\sqrt\{(\d+)\}', r'√\1', ctx)  # √ unicode
    ctx = re.sub(r'\\[a-z]+\{?', '', ctx)           # strip remaining LaTeX
    ctx = ctx.replace('{','').replace('}','').strip()

    return f"{ex['instruction']} — {ctx}"


# ══════════════════════════════════════════════════════════════════
# GENERATE HELPER — called by each unit's generate()
# ══════════════════════════════════════════════════════════════════

def build_output(exercises_raw: list,
                 show_solutions: bool,
                 worksheet_meta: dict,
                 unit_prefix: str = "u") -> dict:
    """
    Takes raw exercise dicts from generators,
    renders them all, returns the standard generate() output dict.

    Used by every unit's generate() function — identical pattern.

    Returns
    -------
    {
        "exercises":     [...],   # _exercises_qmd: has "rendered"
        "exercises_ws":  [...],   # worksheet.js: no "rendered"
        "worksheet":     {...},   # title, unit, date, seed
        "meta":          {...},
    }
    """
    exercises_qmd = []
    exercises_ws  = []

    for i, ex in enumerate(exercises_raw, 1):
        # Ensure solution_svg key exists even for exercises that don't set it
        ex.setdefault("solution_svg", "")

        # Render QMD block
        render_exercise(ex, i, show_solutions, unit_prefix)
        exercises_qmd.append(ex)

        # Build worksheet version
        exercises_ws.append(render_ws_exercise(ex))

    return {
        "_exercises_qmd": exercises_qmd,   # QMD uses ex["rendered"]
        "exercises":       exercises_ws,    # worksheet.js
        "worksheet":       worksheet_meta,
        "meta":            {"total": len(exercises_qmd)},
    }
