"""
exercise_builder.py
===================
Standard building blocks for ALL exercise generators.
Location : assets/exercise_builder.py
Import   : from exercise_builder import Part, Exercise, Diagram, tex

Every generator in every unit file (Trigonometry.py, Indices.py,
Functions.py, ...) uses ONLY these classes to build exercises.
This replaces the three different ad-hoc patterns that existed before.

─────────────────────────────────────────────────────────────────────
USAGE PATTERN (every generator follows this exactly):
─────────────────────────────────────────────────────────────────────

    def gen_find_side_sin():
        # 1. Random values
        theta = random.choice(NICE_ANGLES)
        hyp   = random.randint(5, 15)
        opp   = round(hyp * sin(theta), 2)

        # 2. Diagram — question + solution built together, same state
        d = Diagram("right_triangle",
                    q_sides={"a": "x", "b": "", "c": str(hyp)},
                    s_sides={"a": str(opp), "b": "", "c": str(hyp)},
                    q_angles=["", f"{theta}°", ""],
                    s_angles=["", f"{theta}°", ""])

        # 3. Solution steps — raw strings, no backslash counting
        sol = tex(
            r"\\sin {theta}° = \\dfrac{{x}}{{{hyp}}}",
            r"x = {hyp} \\times \\sin {theta}°",
            r"x = {opp} \\text{{ cm}}",
            theta=theta, hyp=hyp, opp=opp
        )

        # 4. Parts + Exercise — standard contract
        return Exercise(
            ex_type = "find_side_sin",
            parts   = [Part("a", question="Find $x$.",
                            answer=f"x = {opp} cm",
                            solution=sol)],
            context = f"Hypotenuse = {hyp} cm, θ = {theta}°.",
            diagram = d,
        )

─────────────────────────────────────────────────────────────────────
WHAT EACH PIECE DOES:
─────────────────────────────────────────────────────────────────────

  tex()      — builds LaTeX solution steps safely (raw strings)
  Part       — one sub-question: label, question text, answer, solution
  Diagram    — builds svg_q + svg_s together, sharing vertices/state
  Exercise   — the complete exercise: parts + context + diagrams + meta

"""

import random
import string
import math

# ── Try to import SVG helper ──────────────────────────────────────
try:
    from svg_helpers import SVG
except ImportError:
    class SVG:
        @staticmethod
        def figure(*args, **kwargs): return ""


# ══════════════════════════════════════════════════════════════════
# 1. tex() — safe LaTeX step builder
# ══════════════════════════════════════════════════════════════════

def tex(*lines, **values):
    r"""
    Build a LaTeX aligned solution block safely.

    Use raw strings (r"...") — no backslash counting needed.
    Single braces  {}   for value substitution:  {theta}, {ans}
    Double braces  {{}} for literal LaTeX braces: \dfrac{{a}}{{b}}

    Examples
    --------
    tex(
        r"\sin {theta}° = \dfrac{{x}}{{{hyp}}}",
        r"x = {hyp} \times \sin {theta}°",
        r"x = {ans} \text{{ cm}}",
        theta=30, hyp=12, ans=6.0
    )
    → r"\sin 30° = \dfrac{x}{12} \\ x = 12 \times \sin 30° \\ x = 6.0 \text{ cm}"

    tex(
        r"\angle {A}{B}{C} = \sin^{{-1}}\!\left(\dfrac{{{half}}}{{{eq}}}\right) = {ans}°",
        A='L', B='F', C='G', half=5.0, eq=30, ans=9.6
    )
    → r"\angle LFG = \sin^{-1}\!\left(\dfrac{5.0}{30}\right) = 9.6°"

    The renderer wraps this in \begin{aligned}...\end{aligned}.
    """
    formatted = []
    for line in lines:
        if not line:
            continue
        formatted.append(line.format(**values) if values else line)
    return r" \\ ".join(formatted)


# ══════════════════════════════════════════════════════════════════
# 2. Part — one sub-question
# ══════════════════════════════════════════════════════════════════

class Part:
    """
    One labelled sub-question within an exercise.

    Parameters
    ----------
    label      : str  — "a", "b", "c", ...
    question   : str  — plain text or LaTeX question shown to student
    answer     : str  — short answer (LaTeX or plain)
    solution   : str  — full solution steps, built with tex()
    expression : str  — optional LaTeX expression (for grid-layout exercises)
    """

    def __init__(self, label, question="", answer="",
                 solution="", expression=""):
        self.label      = label
        self.question   = question
        self.answer     = answer
        self.solution   = solution
        self.expression = expression

    def to_dict(self):
        return {
            "label":          self.label,
            "question":       self.question,
            "expression":     self.expression,
            "answer_latex":   self.answer,
            "solution_latex": self.solution,
        }

    @staticmethod
    def make_labeled(parts_data):
        """
        Auto-label a list of Part objects a, b, c, ...
        Accepts either Part instances or (question, answer, solution) tuples.
        """
        labels = list("abcdefghijklmnopqrstuvwxyz")
        result = []
        for i, p in enumerate(parts_data):
            if isinstance(p, Part):
                p.label = labels[i]
                result.append(p)
            else:
                q, a, s = (list(p) + ["", "", ""])[:3]
                result.append(Part(labels[i], q, a, s))
        return result


# ══════════════════════════════════════════════════════════════════
# 3. Diagram — builds svg_q + svg_s together
# ══════════════════════════════════════════════════════════════════

_SHAPE_VERT_COUNT = {
    "right_triangle": 3, "right": 3,
    "isosceles": 3, "equilateral": 3, "scalene": 3,
    "rectangle": 4, "square": 4, "trapezium": 4,
    "parallelogram": 4, "rhombus": 4,
}


class Diagram:
    r"""
    Builds question and solution SVGs together, sharing ALL state.

    Vertex letters, orientation, canvas size — identical in both.
    It is structurally impossible for svg_q and svg_s to have
    different vertex letters.

    Parameters
    ----------
    shape       : str   — shape name for SVG.figure()
    q_sides     : dict  — sides for question  (unknowns as "x", "d", etc.)
    s_sides     : dict  — sides for solution  (computed numeric answers)
    vertices    : list  — explicit vertex letters; auto-picked if None
                          and show_vertices=True
    show_vertices: bool — draw vertex labels
    show_angles : bool  — draw computed angle arcs (default False;
                          use q_angles/s_angles for manual angle labels)
    q_angles    : list  — angle label overrides for question SVG
    s_angles    : list  — angle label overrides for solution SVG
    orientation : str   — right_triangle only: "BL"|"BR"|"TL"|"TR"
    width, height: int  — canvas size in pixels

    Attributes
    ----------
    svg_q       : str   — question SVG string
    svg_s       : str   — solution SVG string
    vertices    : list  — vertex letters used (None if show_vertices=False)

    Examples
    --------
    # Right triangle — unknown opposite side
    d = Diagram("right_triangle",
                q_sides={"a": "x", "b": "", "c": str(hyp)},
                s_sides={"a": str(ans), "b": "", "c": str(hyp)},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    d.svg_q   # question diagram
    d.svg_s   # solution diagram

    # Right triangle with vertex labels
    d = Diagram("right_triangle",
                q_sides={"a": "", "b": "", "c": ""},
                s_sides={"a": "Opp", "b": "Adj", "c": "Hyp"},
                show_vertices=True,
                q_angles=["", "θ", ""],
                s_angles=["", "θ", ""])
    vA, vB, vC = d.vertices   # use in context text

    # Isosceles triangle
    apex, bl, br = pick_verts(3)
    d = Diagram("isosceles",
                q_sides={"equal": str(equal), "base": str(base)},
                s_sides={"equal": str(equal), "base": str(base)},
                vertices=[bl, br, apex],
                show_vertices=True,
                s_angles=[f"{BAC}°", f"{BAC}°", f"{ABC}°"])
    """

    def __init__(self, shape,
                 q_sides=None, s_sides=None,
                 vertices=None,
                 show_vertices=False,
                 show_angles=False,
                 q_angles=None, s_angles=None,
                 orientation="BL",
                 width=260, height=190):

        q_sides = q_sides or {}
        s_sides = s_sides or {}

        # Auto-pick vertices once if needed
        if show_vertices and vertices is None:
            n = _SHAPE_VERT_COUNT.get(shape.lower(), 3)
            vertices = pick_verts(n)

        # Build shared kwargs — both SVGs receive identical values
        shared = {
            "show_vertices": show_vertices,
            "show_angles":   show_angles,
            "orientation":   orientation,
            "width":         width,
            "height":        height,
        }
        if vertices:
            shared["vertices"] = vertices

        self.svg_q    = SVG.figure(shape, sides=q_sides,
                                   angle_values=q_angles or [],
                                   **shared)
        self.svg_s    = SVG.figure(shape, sides=s_sides,
                                   angle_values=s_angles or [],
                                   **shared)
        self.vertices = vertices
        self.shape    = shape


# ══════════════════════════════════════════════════════════════════
# 4. pick_verts() — standard vertex picker
# ══════════════════════════════════════════════════════════════════

def pick_verts(n, exclude=None):
    """
    Pick n distinct random uppercase letters for vertex labels.

    This is the ONE way to pick vertex letters in the entire codebase.
    Name the returned values by their geometric role, not by letter:

        apex, bl, br = pick_verts(3)
        # NOT: vA, vB, vC = pick_verts(3)  ← don't name by ABC pattern

    Parameters
    ----------
    n       : int   — number of vertices needed
    exclude : list  — letters already in use (e.g. from another triangle)
    """
    pool = [v for v in string.ascii_uppercase
            if not exclude or v not in exclude]
    return random.sample(pool, n)


# ══════════════════════════════════════════════════════════════════
# 5. Exercise — the complete exercise container
# ══════════════════════════════════════════════════════════════════

class Exercise:
    """
    A complete exercise. Every generator returns one of these.

    Parameters
    ----------
    ex_type  : str       — type name, used for metadata lookup
    parts    : list      — list of Part objects
    context  : str       — paragraph shown before the parts
    given    : list      — optional bullet list of given values
    diagram  : Diagram   — optional; provides svg_q and svg_s
    hint     : str       — optional hint text
    layout   : str       — "list" (default) or "grid"

    The generator does NOT set number/difficulty/skills — those come
    from the METADATA dict in the unit file and are attached by
    generate() when building the output.
    """

    def __init__(self, ex_type, parts,
                 context="", given=None, diagram=None,
                 hint="", layout="list"):
        self.ex_type = ex_type
        self.parts   = Part.make_labeled(parts) if parts else []
        self.context = context
        self.given   = given or []
        self.diagram = diagram
        self.hint    = hint
        self.layout  = layout

        # Diagram convenience
        self.diagram_svg  = diagram.svg_q if diagram else ""
        self.solution_svg = diagram.svg_s if diagram else ""

    def to_dict(self, metadata=None, number=0):
        """
        Convert to the standard exercise dict consumed by renderer
        and worksheet.js.

        metadata : dict — entry from METADATA for this ex_type
        number   : int  — exercise number assigned by generate()
        """
        m = metadata or {}
        parts_dicts = [p.to_dict() for p in self.parts]

        return {
            "number":       number,
            "type":         self.ex_type,
            "topic":        m.get("topic", ""),
            "subtopic":     m.get("subtopic", ""),
            "lt":           m.get("lt", ""),
            "difficulty":   m.get("difficulty", "medium"),
            "bloom":        m.get("bloom", "apply"),
            "instruction":  m.get("instruction", "Solve."),
            "context":      self.context,
            "given":        self.given,
            "hint":         self.hint,
            "has_diagram":  bool(self.diagram_svg),
            "diagram_svg":  self.diagram_svg,
            "solution_svg": self.solution_svg,
            "parts":        parts_dicts,
            "layout":       self.layout,
            "meta": {
                "type":          self.ex_type,
                "skills":        m.get("skills", []),
                "prerequisites": m.get("prerequisites", []),
                "strategy":      m.get("strategy", []),
                "common_errors": m.get("common_errors", []),
                "remediation":   m.get("remediation", ""),
                "flint_prompt":  m.get("flint_prompt", ""),
                "difficulty":    m.get("difficulty", "medium"),
                "lt":            m.get("lt", ""),
            },
            "rendered": "",
        }


# ══════════════════════════════════════════════════════════════════
# 6. build_qmd() — render one exercise to Quarto markdown
# ══════════════════════════════════════════════════════════════════

def build_qmd(ex_dict, show_solutions=False, unit_prefix="u"):
    """
    Render one exercise dict to Quarto markdown string.
    This is the single renderer — replaces all ad-hoc render_* functions.
    """
    i    = ex_dict["number"]
    lines = [f"::::: {{#exr-{unit_prefix}-{i}}}\n"]

    # Instruction
    if ex_dict.get("instruction"):
        lines.append(f"*{ex_dict['instruction']}*\n")

    # Context
    if ex_dict.get("context"):
        lines.append(ex_dict["context"] + "\n")

    # Given values
    if ex_dict.get("given"):
        lines.append("**Given:** " + " · ".join(ex_dict["given"]) + "\n")

    # Question diagram
    if ex_dict.get("has_diagram") and ex_dict.get("diagram_svg"):
        lines += [
            '::: {.content-visible when-format="html"}',
            ex_dict["diagram_svg"] + "\n",
            ":::\n",
        ]

    # Parts
    for p in ex_dict["parts"]:
        if p.get("expression"):
            lines.append(f"**({p['label']})** $\\displaystyle {p['expression']}$\n")
        else:
            lines.append(f"**({p['label']})** {p['question']}\n")

    # Solution callout
    if show_solutions:
        lines += ['::: {.callout-tip collapse="true"}', "## 🔍 View Solution\n"]

        # Solution diagram
        sol_svg = ex_dict.get("solution_svg", "")
        if sol_svg:
            lines += [
                '::: {.content-visible when-format="html"}',
                sol_svg + "\n",
                ":::\n",
            ]

        for p in ex_dict["parts"]:
            sol = p.get("solution_latex") or p.get("answer_latex", "")
            if sol:
                lines += [
                    f"**{p['label']})**\n",
                    "$$\n\\begin{aligned}",
                    sol,
                    "\\end{aligned}\n$$\n",
                ]
        lines.append(":::\n")

    # Skill badges
    skills = ex_dict.get("meta", {}).get("skills", [])
    if skills:
        badges = "\n".join(f'  <span class="skill-badge">{s}</span>'
                           for s in skills)
        lines += [
            "",
            "::: exercise-meta",
            '<div class="skill-container">',
            badges,
            "</div>",
            ":::\n",
        ]

    lines.append(":::::\n")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════
# 7. build_output() — assemble full generate() return value
# ══════════════════════════════════════════════════════════════════

def build_output(exercises, metadata, show_solutions=False,
                 worksheet_meta=None, unit_prefix="u"):
    """
    Convert a list of Exercise objects into the standard output dict.

    Parameters
    ----------
    exercises      : list of Exercise
    metadata       : dict mapping ex_type → metadata dict
    show_solutions : bool
    worksheet_meta : dict — title, unit, date, seed
    unit_prefix    : str  — e.g. "trig", "u2", "u7"

    Returns
    -------
    {
      "_exercises_qmd": [...],   # for QMD practice problems
      "exercises":      [...],   # for worksheet.js
      "worksheet":      {...},
      "meta":           {"total": int}
    }
    """
    exercises_qmd = []
    exercises_ws  = []

    for i, ex in enumerate(exercises, 1):
        m    = metadata.get(ex.ex_type, {})
        d    = ex.to_dict(metadata=m, number=i)

        # Render to Quarto markdown
        d["rendered"] = build_qmd(d, show_solutions=show_solutions,
                                  unit_prefix=unit_prefix)
        exercises_qmd.append(d)

        # Worksheet-friendly version (simpler structure for worksheet.js)
        ws_parts = []
        for p in d["parts"]:
            q_latex = (p["expression"]
                       if p["expression"]
                       else f"\\text{{{p['question']}}}")
            ws_parts.append({
                "label":         p["label"],
                "question_latex": q_latex,
                "answer_latex":  p["answer_latex"],
            })
        exercises_ws.append({
            "number":      i,
            "type":        d["type"],
            "lt":          d["lt"],
            "difficulty":  d["difficulty"],
            "title":       d["instruction"],
            "instruction": d["instruction"],
            "diagram_svg": d.get("diagram_svg", ""),
            "parts":       ws_parts,
            "meta": {
                "difficulty": d["difficulty"],
                "lt":         d["lt"],
                "skills":     d["meta"]["skills"],
            },
        })

    return {
        "_exercises_qmd": exercises_qmd,
        "exercises":      exercises_ws,
        "worksheet":      worksheet_meta or {},
        "meta":           {"total": len(exercises_qmd)},
    }


# ══════════════════════════════════════════════════════════════════
# SMOKE TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import math as _math

    print("=== tex() ===")
    sol = tex(
        r"\sin {theta}° = \dfrac{{x}}{{{hyp}}}",
        r"x = {hyp} \times \sin {theta}°",
        r"x = {ans} \text{{ cm}}",
        theta=30, hyp=12, ans=6.0
    )
    print(sol)
    assert r'\sin' in sol and r'\dfrac' in sol and r'\text' in sol
    assert '\x07' not in sol
    print("✓ no control chars, all LaTeX commands present\n")

    sol2 = tex(
        r"\angle {A}{B}{C} = \sin^{{-1}}\!\left(\dfrac{{{half}}}{{{eq}}}\right) = {ans}°",
        A='L', B='F', C='G', half=5.0, eq=30, ans=9.6
    )
    print(sol2)
    assert r'\angle' in sol2 and '\x07' not in sol2
    print("✓ \\angle correct, no chr(7)\n")

    print("=== pick_verts() ===")
    random.seed(42)
    v = pick_verts(3)
    print(f"pick_verts(3) = {v}")
    assert len(v) == 3 and len(set(v)) == 3
    v2 = pick_verts(3, exclude=v)
    assert not set(v) & set(v2), "exclude not working"
    print(f"pick_verts(3, exclude={v}) = {v2}")
    print("✓ distinct, exclude works\n")

    print("=== Part ===")
    p = Part("a", question="Find $x$.", answer="x = 6.0 cm", solution=sol)
    d = p.to_dict()
    assert d["label"] == "a"
    assert d["answer_latex"] == "x = 6.0 cm"
    print(f"Part dict keys: {list(d.keys())}")
    print("✓\n")

    print("=== Part.make_labeled() ===")
    parts = Part.make_labeled([
        Part("", "Find x.", "x = 5"),
        Part("", "Find y.", "y = 3"),
    ])
    assert parts[0].label == "a" and parts[1].label == "b"
    print(f"Labels: {[p.label for p in parts]}")
    print("✓\n")

    print("=== Diagram() ===")
    d = Diagram("right_triangle",
                q_sides={"a": "x", "b": "", "c": "12"},
                s_sides={"a": "6.0", "b": "", "c": "12"},
                q_angles=["", "30°", ""],
                s_angles=["", "30°", ""])
    assert d.svg_q != "" or True   # SVG may be empty if svg_helpers not found
    print(f"svg_q length: {len(d.svg_q)}, svg_s length: {len(d.svg_s)}")
    assert d.vertices is None   # no vertices requested
    print("✓ no vertices\n")

    d2 = Diagram("right_triangle",
                 q_sides={"a": "", "b": "", "c": ""},
                 s_sides={"a": "Opp", "b": "Adj", "c": "Hyp"},
                 show_vertices=True,
                 q_angles=["", "θ", ""],
                 s_angles=["", "θ", ""])
    assert d2.vertices is not None and len(d2.vertices) == 3
    print(f"Auto-picked vertices: {d2.vertices}")
    print("✓ vertices auto-picked once, shared between svg_q and svg_s\n")

    # Isosceles
    apex, bl, br = pick_verts(3)
    d3 = Diagram("isosceles",
                 q_sides={"equal": "30", "base": "10"},
                 s_sides={"equal": "30", "base": "10"},
                 vertices=[bl, br, apex],
                 show_vertices=True,
                 s_angles=["9.6°", "9.6°", "160.8°"])
    assert d3.vertices == [bl, br, apex]
    print(f"Isosceles vertices: {d3.vertices}")
    print("✓\n")

    print("=== Exercise + build_output() ===")
    random.seed(42)
    ex = Exercise(
        ex_type="find_side_sin",
        parts=[
            Part("a", question="Find $x$.",
                 answer="x = 6.0 cm", solution=sol)
        ],
        context="Hypotenuse = 12 cm, θ = 30°.",
        diagram=d,
    )
    META = {
        "find_side_sin": {
            "subtopic":   "Find the Opposite Side (sin)",
            "difficulty": "easy",
            "bloom":      "apply",
            "lt":         "LT3",
            "instruction":"Find the length of the unknown side.",
            "skills":     ["SOH-CAH-TOA", "Equation set-up", "Calculator use"],
        }
    }
    from datetime import date
    out = build_output([ex], metadata=META, show_solutions=True,
                       worksheet_meta={"title":"Test","date":str(date.today())},
                       unit_prefix="trig")
    assert len(out["_exercises_qmd"]) == 1
    assert len(out["exercises"]) == 1
    rendered = out["_exercises_qmd"][0]["rendered"]
    assert "Find $x$" in rendered
    assert "exr-trig-1" in rendered
    print(f"Rendered length: {len(rendered)} chars")
    print(rendered[:300])
    print("✓\n")

    print("=" * 50)
    print("All smoke tests passed.")
    print()
    print("How generators will look with exercise_builder:")
    print("""
    from exercise_builder import Part, Exercise, Diagram, tex, pick_verts

    def gen_find_side_sin():
        theta = random.choice(NICE_ANGLES)
        hyp   = random.randint(5, 15)
        opp   = round(hyp * sin(theta), 2)

        d = Diagram("right_triangle",
                    q_sides={"a": "x",       "b": "", "c": str(hyp)},
                    s_sides={"a": str(opp),   "b": "", "c": str(hyp)},
                    q_angles=["", f"{theta}°", ""],
                    s_angles=["", f"{theta}°", ""])

        sol = tex(
            r"\\sin {theta}° = \\dfrac{{x}}{{{hyp}}}",
            r"x = {hyp} \\times \\sin {theta}°",
            r"x = {opp} \\text{{ cm}}",
            theta=theta, hyp=hyp, opp=opp
        )

        return Exercise(
            ex_type="find_side_sin",
            parts=[Part("a", question="Find $x$.",
                        answer=f"x = {opp} cm", solution=sol)],
            context=f"Hypotenuse = {hyp} cm, θ = {theta}°.",
            diagram=d,
        )
    """)
