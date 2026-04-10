"""
exercise_schema.py
==================
Single exercise schema used by every unit in the Math-Booklet project.

Location : assets/exercise_schema.py
Import   : from exercise_schema import make_exercise, make_part

Every generator returns ONE dict built by make_exercise().
The renderer reads that dict — no generator ever builds markdown.

Schema
------
{
    # IDENTITY
    "number":     int,
    "type":       str,
    "topic":      str,
    "subtopic":   str,
    "lt":         str,
    "difficulty": "easy" | "medium" | "hard",
    "bloom":      str,

    # CONTENT
    "context":    str,        # narrative setup paragraph (word problems)
    "given":      [str],      # measurable facts: ["a = √3 cm", "b = √5 cm"]
    "instruction":str,        # what to do: "Simplify." / "Find the hypotenuse."
    "hint":       str,        # optional scaffold shown collapsed

    # EXPRESSION  (grid-type: the single LaTeX expression for this exercise)
    "expression": str,        # e.g. "x^3 \\times x^4"  — empty for word problems

    # DIAGRAM
    "has_diagram":  bool,
    "diagram_svg":  str,      # complete SVG string shown in question, "" if none
    "solution_svg": str,      # complete SVG string shown in solution, "" if none
                              # (same triangle with answer value substituted for x)

    # PARTS — every exercise has at least one part
    "parts": [
        {
            "label":          str,   # "a", "b", "c" …
            "question":       str,   # plain-text question for this part
            "expression":     str,   # LaTeX if this part has its own expression
            "answer_latex":   str,   # answer in LaTeX
            "solution_latex": str,   # full working steps in LaTeX
        }
    ],

    # METADATA
    "meta": {
        "skills":        [str],
        "prerequisites": [str],
        "strategy":      [str],
        "common_errors": [str],
        "remediation":   str,
        "flint_prompt":  str,
    },

    # SET BY RENDERER — generators never touch these
    "rendered":    str,       # complete QMD markdown block
    "layout":      str,       # "grid" | "list"  (detected, not set)
}

Layout detection (automatic, no flag needed)
--------------------------------------------
GRID  →  no context, no given, no diagram,
          every part has expression set
LIST  →  anything else
"""

PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")


# ══════════════════════════════════════════════════════════════════
# PART BUILDER
# ══════════════════════════════════════════════════════════════════

def make_part(label,
              question="",
              expression="",
              answer_latex="",
              solution_latex=""):
    """
    Build one part dict.

    label          : "a", "b", "c" …
    question       : plain-text question for list exercises
    expression     : LaTeX expression for grid exercises
    answer_latex   : answer
    solution_latex : full working
    """
    return {
        "label":          label,
        "question":       question,
        "expression":     expression,
        "answer_latex":   answer_latex,
        "solution_latex": solution_latex,
    }


def make_parts_from_expressions(expressions, answers, solutions=None):
    """
    Convenience: build parts list from parallel lists.
    Used by grid generators that produce N expression+answer pairs.

    expressions : list of LaTeX strings
    answers     : list of LaTeX answer strings
    solutions   : list of LaTeX solution strings (optional)
    """
    if solutions is None:
        solutions = [""] * len(expressions)
    return [
        make_part(
            label=PART_LABELS[i],
            expression=expressions[i],
            answer_latex=answers[i],
            solution_latex=solutions[i],
        )
        for i in range(len(expressions))
    ]


# ══════════════════════════════════════════════════════════════════
# EXERCISE BUILDER
# ══════════════════════════════════════════════════════════════════

def make_exercise(
    # Identity
    ex_type,
    topic        = "",
    subtopic     = "",
    lt           = "",
    difficulty   = "medium",
    bloom        = "apply",

    # Content
    instruction  = "",
    context      = "",
    given        = None,
    hint         = "",

    # Expression (grid type)
    expression   = "",

    # Diagram
    diagram_svg  = "",
    solution_svg = "",        # triangle with answer filled in, shown in solution callout

    # Parts
    parts        = None,

    # Metadata
    skills       = None,
    prerequisites= None,
    strategy     = None,
    common_errors= None,
    remediation  = "",
    flint_prompt = "",
):
    """
    Build a complete exercise dict.

    Generators call this and return the result.
    They never build markdown — the renderer does that.

    solution_svg : optional SVG string shown inside the solution callout.
                   Typically the same diagram as diagram_svg but with the
                   unknown value substituted for x (e.g. x → 7.23 cm).
                   Geometry generators populate this automatically.

    Grid exercise example:
        make_exercise(
            ex_type     = "multiply_simple",
            subtopic    = "Multiplication Rule",
            lt          = "LT1",
            difficulty  = "easy",
            instruction = "Simplify. Give your answer in index form.",
            parts = make_parts_from_expressions(
                expressions = ["x^3 \\\\times x^4", "a^2 \\\\times a^5"],
                answers     = ["x^7", "a^7"],
                solutions   = ["x^{3+4}=x^7", "a^{2+5}=a^7"],
            )
        )

    List exercise example:
        make_exercise(
            ex_type     = "surd_pythagoras",
            subtopic    = "Pythagoras with Surds",
            lt          = "LT9s",
            difficulty  = "hard",
            instruction = "Use Pythagoras' theorem.",
            context     = "The diagram shows a right-angled triangle.",
            given       = ["leg a = √3 cm", "leg b = √5 cm"],
            hint        = "Use x² = a² + b²",
            diagram_svg = svg_string,
            solution_svg= svg_solution_string,
            parts = [
                make_part("a",
                    question       = "Find the exact length of the hypotenuse x.",
                    answer_latex   = "2\\\\sqrt{2}",
                    solution_latex = "x^2=3+5=8 \\\\\\\\ x=\\\\sqrt{8}=2\\\\sqrt{2}",
                )
            ]
        )
    """
    return {
        # Identity
        "number":      0,        # set by generate() loop
        "type":        ex_type,
        "topic":       topic,
        "subtopic":    subtopic,
        "lt":          lt,
        "difficulty":  difficulty,
        "bloom":       bloom,

        # Content
        "instruction": instruction,
        "context":     context,
        "given":       given or [],
        "hint":        hint,

        # Expression
        "expression":  expression,

        # Diagram
        "has_diagram":  bool(diagram_svg),
        "diagram_svg":  diagram_svg,
        "solution_svg": solution_svg,

        # Parts
        "parts":       parts or [],

        # Metadata
        "meta": {
            "skills":        skills        or [],
            "prerequisites": prerequisites or [],
            "strategy":      strategy      or [],
            "common_errors": common_errors or [],
            "remediation":   remediation,
            "flint_prompt":  flint_prompt,
        },

        # Set by renderer
        "rendered": "",
        "layout":   "",
    }


# ══════════════════════════════════════════════════════════════════
# LAYOUT DETECTION
# ══════════════════════════════════════════════════════════════════

def detect_layout(ex: dict) -> str:
    """
    Detect whether an exercise should render as grid or list.

    GRID  : no context, no given, no diagram,
            every part has an expression set
    LIST  : anything else
    """
    if ex["context"] or ex["given"] or ex["has_diagram"]:
        return "list"
    if ex["parts"] and all(p["expression"] for p in ex["parts"]):
        return "grid"
    return "list"


# ══════════════════════════════════════════════════════════════════
# WORKSHEET PART BUILDER
# ══════════════════════════════════════════════════════════════════

def ws_question_latex(ex: dict, part: dict) -> str:
    """
    Build the question_latex shown in a worksheet cell.

    Grid exercises  → expression only (e.g. x^3 × x^4)
    List exercises  → part question only, short and clean
                      context lives in the instruction line above
    If part has ws_question_latex set explicitly, use that.
    """
    # Generator can override per-part
    if part.get("ws_question_latex"):
        return part["ws_question_latex"]

    layout = ex.get("layout") or detect_layout(ex)

    if layout == "grid":
        return part["expression"]

    # List: just the part question as \text{...}
    # If part also has an expression, show that too
    if part["expression"] and part["question"]:
        return f"{part['expression']} \\quad \\text{{{part['question']}}}"
    if part["expression"]:
        return part["expression"]
    return f"\\text{{{part['question']}}}" if part["question"] else ""
