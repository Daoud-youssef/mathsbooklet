"""
Trigonometry.py
===============
Unit 1: Trigonometry — exercise generator.
Rebuilt using exercise_builder.py pattern.

Every generator:
  1. Computes random values
  2. Builds Diagram (shares vertices between svg_q and svg_s)
  3. Writes solution with tex() — raw strings, no backslash counting
  4. Returns Exercise(type, parts, context, diagram)
"""

import random
import math
import json
import string
from datetime import date

from exercise_builder import Part, Exercise, Diagram, tex, pick_verts, build_output

# ── Trig helpers ──────────────────────────────────────────────────
NICE_ANGLES = [25, 30, 35, 40, 45, 50, 55, 60, 65]

def _sin(d): return math.sin(math.radians(d))
def _cos(d): return math.cos(math.radians(d))
def _tan(d): return math.tan(math.radians(d))
def _asin(r): return round(math.degrees(math.asin(max(-1, min(1, r)))), 1)
def _acos(r): return round(math.degrees(math.acos(max(-1, min(1, r)))), 1)
def _atan(r): return round(math.degrees(math.atan(r)), 1)
def _r2(x):   return round(x, 2)
def _r1(x):   return round(x, 1)
def _ns():    return random.choice([5,6,7,8,9,10,11,12,13,14,15])
def _fmt(v):  return str(int(v)) if float(v) == int(float(v)) else str(v)
def _deg(n):  return f"{n}°"


# ══════════════════════════════════════════════════════════════════
# METADATA — one entry per exercise type
# ══════════════════════════════════════════════════════════════════

METADATA = {
    "label_sides": {
        "subtopic": "Labelling Triangle Sides", "difficulty": "easy",
        "bloom": "remember", "lt": "LT1", "topic": "Trigonometry",
        "skills": ["Hypotenuse identification", "Opposite side", "Adjacent side"],
        "instruction": "Label the hypotenuse, opposite, and adjacent sides relative to the marked angle.",
        "strategy": ["1. Hypotenuse is always opposite the right angle.",
                     "2. Opposite is across from θ.", "3. Adjacent is next to θ (not hypotenuse)."],
        "common_errors": ["Swapping opposite and adjacent when θ changes."],
    },
    "write_ratio": {
        "subtopic": "Writing Trig Ratios", "difficulty": "easy",
        "bloom": "understand", "lt": "LT2", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Fraction form", "Ratio identification"],
        "instruction": "Write the trigonometric ratio as a fraction.",
        "strategy": ["1. Identify the two sides.", "2. Select SOH/CAH/TOA.", "3. Write as fraction."],
        "common_errors": ["Inverting the fraction."],
    },
    "identify_ratio": {
        "subtopic": "Identifying the Correct Ratio", "difficulty": "easy",
        "bloom": "understand", "lt": "LT2", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Ratio selection", "Side identification"],
        "instruction": "State which trigonometric ratio should be used and write the equation.",
        "strategy": ["1. Label known and unknown sides.", "2. Match to SOH/CAH/TOA."],
        "common_errors": ["Using tan when hypotenuse is involved."],
    },
    "find_side_sin": {
        "subtopic": "Find the Opposite Side (sin)", "difficulty": "easy",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Equation set-up", "Calculator use"],
        "instruction": "Find the length of the unknown side. Give your answer to 2 decimal places.",
        "strategy": ["1. sin θ = x/H  →  x = H × sin θ."],
        "common_errors": ["Dividing instead of multiplying."],
    },
    "find_side_cos": {
        "subtopic": "Find the Adjacent Side (cos)", "difficulty": "easy",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Equation set-up", "Calculator use"],
        "instruction": "Find the length of the unknown side. Give your answer to 2 decimal places.",
        "strategy": ["1. cos θ = x/H  →  x = H × cos θ."],
        "common_errors": ["Confusing adjacent with opposite."],
    },
    "find_side_tan": {
        "subtopic": "Find the Opposite Side (tan)", "difficulty": "easy",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Equation set-up", "Calculator use"],
        "instruction": "Find the length of the unknown side. Give your answer to 2 decimal places.",
        "strategy": ["1. tan θ = x/A  →  x = A × tan θ."],
        "common_errors": ["Using sin when hypotenuse not involved."],
    },
    "find_side_hyp_sin": {
        "subtopic": "Find the Hypotenuse (sin)", "difficulty": "medium",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Rearranging equations", "Calculator use"],
        "instruction": "Find the length of the hypotenuse. Give your answer to 2 decimal places.",
        "strategy": ["1. sin θ = O/x  →  x = O/sin θ."],
        "common_errors": ["Multiplying instead of dividing."],
    },
    "find_side_hyp_cos": {
        "subtopic": "Find the Hypotenuse (cos)", "difficulty": "medium",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Rearranging equations", "Calculator use"],
        "instruction": "Find the length of the hypotenuse. Give your answer to 2 decimal places.",
        "strategy": ["1. cos θ = A/x  →  x = A/cos θ."],
        "common_errors": ["Multiplying instead of dividing."],
    },
    "find_side_hyp_tan": {
        "subtopic": "Find the Adjacent Side (tan)", "difficulty": "medium",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["SOH-CAH-TOA", "Rearranging equations", "Calculator use"],
        "instruction": "Find the length of the unknown side. Give your answer to 2 decimal places.",
        "strategy": ["1. tan θ = O/x  →  x = O/tan θ."],
        "common_errors": ["Multiplying instead of dividing."],
    },
    "find_angle_sin": {
        "subtopic": "Find an Angle Using sin⁻¹", "difficulty": "medium",
        "bloom": "apply", "lt": "LT4", "topic": "Trigonometry",
        "skills": ["Inverse trig functions", "Two-side ratio", "Degree rounding"],
        "instruction": "Find the size of angle θ. Give your answer to 1 decimal place.",
        "strategy": ["1. sin θ = O/H.", "2. θ = sin⁻¹(O/H)."],
        "common_errors": ["Forgetting inverse function."],
    },
    "find_angle_cos": {
        "subtopic": "Find an Angle Using cos⁻¹", "difficulty": "medium",
        "bloom": "apply", "lt": "LT4", "topic": "Trigonometry",
        "skills": ["Inverse trig functions", "Two-side ratio", "Degree rounding"],
        "instruction": "Find the size of angle θ. Give your answer to 1 decimal place.",
        "strategy": ["1. cos θ = A/H.", "2. θ = cos⁻¹(A/H)."],
        "common_errors": ["Using sin⁻¹ for adj/hyp."],
    },
    "find_angle_tan": {
        "subtopic": "Find an Angle Using tan⁻¹", "difficulty": "medium",
        "bloom": "apply", "lt": "LT4", "topic": "Trigonometry",
        "skills": ["Inverse trig functions", "Two-side ratio", "Degree rounding"],
        "instruction": "Find the size of angle θ. Give your answer to 1 decimal place.",
        "strategy": ["1. tan θ = O/A.", "2. θ = tan⁻¹(O/A)."],
        "common_errors": ["Using tan when hypotenuse given."],
    },
    "elevation_basic": {
        "subtopic": "Angle of Elevation — Find Height", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["Elevation diagram", "tan ratio", "Real-world modelling"],
        "instruction": "Use trigonometry to find the unknown measurement. Give your answer to 2 decimal places.",
        "strategy": ["1. tan θ = height/base.", "2. Rearrange and evaluate."],
        "common_errors": ["Placing θ at top."],
    },
    "depression_basic": {
        "subtopic": "Angle of Depression — Find Distance", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["Depression diagram", "tan ratio", "Alternate angles"],
        "instruction": "Use trigonometry to find the unknown measurement. Give your answer to 2 decimal places.",
        "strategy": ["1. Depression angle = interior angle of triangle.",
                     "2. tan θ = height/distance."],
        "common_errors": ["Confusing depression with interior angle."],
    },
    "elevation_word": {
        "subtopic": "Elevation — Word Problem", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["Problem decomposition", "Diagram construction", "tan ratio"],
        "instruction": "Draw a diagram, label all measurements, and find the answer. Give your answer to 2 decimal places.",
        "strategy": ["1. Identify observer, object, unknown.",
                     "2. Draw and label.", "3. Apply trig."],
        "common_errors": ["Angle inside triangle not from horizontal."],
    },
    "depression_word": {
        "subtopic": "Depression — Word Problem", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["Problem decomposition", "Diagram construction", "Alternate angles"],
        "instruction": "Draw a diagram, label all measurements, and find the answer. Give your answer to 2 decimal places.",
        "strategy": ["1. Draw horizontal at observer level.",
                     "2. Transfer depression angle."],
        "common_errors": ["Forgetting horizontal line."],
    },
    "shadow_flagpole": {
        "subtopic": "Shadow — Find Height", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["tan ratio", "Shadow geometry", "Real-world modelling"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. tan(elev) = height/shadow.", "2. height = shadow × tan(elev)."],
        "common_errors": ["Using shadow as hypotenuse."],
    },
    "hill_gradient": {
        "subtopic": "Hill Gradient", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["sin for height", "cos for horizontal", "Hill geometry"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. height = distance × sin(angle).",
                     "2. horizontal = distance × cos(angle)."],
        "common_errors": ["Confusing distance with height."],
    },
    "train_gradient": {
        "subtopic": "Train Gradient — Find Angle", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["sin⁻¹", "Gradient geometry", "Small angles"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. sin θ = rise/track.", "2. θ = sin⁻¹(rise/track)."],
        "common_errors": ["Using tan (track is hypotenuse)."],
    },
    "elevation_depression_pair": {
        "subtopic": "Elevation & Depression — Same Point", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["Elevation angle", "Depression angle", "Alternate angles"],
        "instruction": "Show all working. Give your answer to 1 decimal place.",
        "strategy": ["1. tan θ = height/distance.",
                     "2. Depression = elevation (alternate angles)."],
        "common_errors": ["Thinking angles differ."],
    },
    "kite_height": {
        "subtopic": "Kite Height — String Angle", "difficulty": "medium",
        "bloom": "apply", "lt": "LT5", "topic": "Trigonometry",
        "skills": ["sin ratio", "Height calculation", "Unit conversion"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. Vertical = string × sin θ.",
                     "2. Add handle height.", "3. Convert cm to m."],
        "common_errors": ["Forgetting handle height.", "Not converting units."],
    },
    "multi_step_two_triangles": {
        "subtopic": "Multi-step — Two Triangles", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Multi-step reasoning", "Shared side", "Combined trig"],
        "instruction": "Show all working clearly. Give your answer to 2 decimal places.",
        "strategy": ["1. Find shared side.", "2. Use in second triangle.",
                     "3. Round final only."],
        "common_errors": ["Rounding intermediate values."],
    },
    "multi_step_bearing": {
        "subtopic": "Multi-step — Bearing & Trig", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Bearing interpretation", "North reference", "Multi-step trig"],
        "instruction": "Show all working clearly. Give your answer to 2 decimal places.",
        "strategy": ["1. Draw North line.", "2. Mark bearing clockwise.",
                     "3. Apply trig."],
        "common_errors": ["Bearing from South not North."],
    },
    "ladder_safety": {
        "subtopic": "Ladder Safety — Angle Check", "difficulty": "medium",
        "bloom": "apply", "lt": "LT3", "topic": "Trigonometry",
        "skills": ["tan ratio", "Angle calculation", "Safety constraint"],
        "instruction": "Show all working. Give angles to 1 decimal place.",
        "strategy": ["1. tan θ = h/d.", "2. θ = tan⁻¹(h/d).",
                     "3. Check 70° ≤ θ ≤ 80°.", "4. L = √(h²+d²)."],
        "common_errors": ["Forgetting to check both bounds."],
    },
    "ramp_angle": {
        "subtopic": "Ramp Angle — Unit Conversion", "difficulty": "medium",
        "bloom": "apply", "lt": "LT4", "topic": "Trigonometry",
        "skills": ["Unit conversion", "tan⁻¹", "Ramp geometry"],
        "instruction": "Convert units where needed. Give your answer to 2 decimal places.",
        "strategy": ["1. Convert to same unit.", "2. tan θ = h/d.",
                     "3. θ = tan⁻¹(h/d)."],
        "common_errors": ["Mixing m and cm."],
    },
    "two_triangles_vertex": {
        "subtopic": "Two Triangles — Vertex Labels", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Multi-step reasoning", "Vertex labelling", "Combined trig"],
        "instruction": "Show all working clearly. Give your answer to 2 decimal places.",
        "strategy": ["1. Find BD using triangle ABD.", "2. Use BD in BCD."],
        "common_errors": ["Not identifying which triangle to solve first."],
    },
    "ratio_split_angle": {
        "subtopic": "Ratio Split Angle", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Ratio splitting", "Multi-step trig", "Angle arithmetic"],
        "instruction": "Show all working clearly. Give your answer to 2 decimal places.",
        "strategy": ["1. Find DBC from ratio.", "2. Find BD.", "3. Find CD."],
        "common_errors": ["Splitting ratio incorrectly."],
    },
    "isosceles_split": {
        "subtopic": "Isosceles — Perpendicular Split", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Isosceles properties", "Perpendicular bisector", "sin application"],
        "instruction": "Show all working. Give your answer to 1 decimal place.",
        "strategy": ["1. Drop perpendicular from apex.",
                     "2. Half-base and equal side form right triangle.",
                     "3. Apply sin."],
        "common_errors": ["Using full base instead of half."],
    },
    "bearing_triangle": {
        "subtopic": "Bearing — Distance & Direction", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Pythagoras", "tan⁻¹ for bearing", "Compass directions"],
        "instruction": "Show all working. Give bearing to nearest degree.",
        "strategy": ["1. Pythagoras for distance.",
                     "2. tan⁻¹(east/north) for angle.",
                     "3. Convert to bearing."],
        "common_errors": ["Not converting angle to bearing."],
    },
    "cliff_lighthouse": {
        "subtopic": "Cliff & Lighthouse", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Multi-step trig", "Total height", "Elevation angles"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. Total height = cliff + lighthouse.",
                     "2. Find distance.", "3. Find angle to cliff top."],
        "common_errors": ["Using only one height."],
    },
    "circle_chord_radius": {
        "subtopic": "Circle — Chord & Radius", "difficulty": "hard",
        "bloom": "analyse", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Circle geometry", "sin ratio", "Right triangle in circle"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. Half-chord and radius = right triangle.",
                     "2. sin θ = half-chord/radius."],
        "common_errors": ["Using full chord."],
    },
    "flagpole_two_elevations": {
        "subtopic": "Flagpole — Two Elevations", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Multi-step trig", "Two-angle setup", "Subtraction"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. h1 = d·tan α.", "2. h2 = d·tan β.",
                     "3. flagpole = h2 - h1."],
        "common_errors": ["Not subtracting."],
    },
    "cliff_boat_closer": {
        "subtopic": "Cliff — Boat Moving Closer", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Two depression angles", "Distance difference", "Multi-step trig"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. d1 = h/tan α.", "2. d2 = h/tan β.",
                     "3. moved = d1 - d2."],
        "common_errors": ["Using elevation not depression."],
    },
    "helicopter_overhead": {
        "subtopic": "Helicopter — Speed & Height", "difficulty": "hard",
        "bloom": "evaluate", "lt": "LT6", "topic": "Trigonometry",
        "skills": ["Speed-distance-time", "tan ratio", "Unit conversion"],
        "instruction": "Show all working. Give your answer to 2 decimal places.",
        "strategy": ["1. dist = speed × time (convert units).",
                     "2. h = dist × tan(elevation)."],
        "common_errors": ["Not converting km/h."],
    },
}


# ══════════════════════════════════════════════════════════════════
# LT1 — LABELLING SIDES
# ══════════════════════════════════════════════════════════════════

def gen_label_sides():
    # right-angle corner, theta corner, top corner
    ra, th, top = pick_verts(3)

    d = Diagram("right_triangle",
                q_sides={"a": "",    "b": "",    "c": ""},
                s_sides={"a": "Opp", "b": "Adj", "c": "Hyp"},
                vertices=[ra, th, top],
                show_vertices=True,
                q_angles=["", "θ", ""],
                s_angles=["", "θ", ""])

    hyp_name = f"{th}{top}"
    opp_name = f"{ra}{top}"
    adj_name = f"{ra}{th}"

    return Exercise("label_sides",
        parts=[
            Part("a", question="Which side is the hypotenuse?",
                 answer=f"\\text{{{hyp_name}}}",
                 solution=tex(r"\text{{Hyp = {h} (opposite right angle at {ra})}}",
                              h=hyp_name, ra=ra)),
            Part("b", question="Which side is opposite to angle θ?",
                 answer=f"\\text{{{opp_name}}}",
                 solution=tex(r"\text{{Opp = {o} (across from }} \theta \text{{ at {th})}}",
                              o=opp_name, th=th)),
            Part("c", question="Which side is adjacent to angle θ?",
                 answer=f"\\text{{{adj_name}}}",
                 solution=tex(r"\text{{Adj = {a} (next to }} \theta \text{{, not hyp)}}",
                              a=adj_name)),
        ],
        context=(f"Triangle ${ra}{th}{top}$ has a right angle at ${ra}$ "
                 f"and angle $\\theta$ at ${th}$."),
        diagram=d)


# ══════════════════════════════════════════════════════════════════
# LT2 — WRITING RATIOS
# ══════════════════════════════════════════════════════════════════

def gen_write_ratio():
    theta = random.choice(NICE_ANGLES)
    opp = _ns(); adj = _ns()
    hyp = _r2(math.sqrt(opp**2 + adj**2))
    ratio = random.choice(["sin", "cos", "tan"])

    if ratio == "sin":
        ans = f"\\dfrac{{{opp}}}{{{hyp}}}"
        sol = tex(r"\sin\theta = \dfrac{{\text{{Opp}}}}{{\text{{Hyp}}}} = \dfrac{{{opp}}}{{{hyp}}}",
                  opp=opp, hyp=hyp)
    elif ratio == "cos":
        ans = f"\\dfrac{{{adj}}}{{{hyp}}}"
        sol = tex(r"\cos\theta = \dfrac{{\text{{Adj}}}}{{\text{{Hyp}}}} = \dfrac{{{adj}}}{{{hyp}}}",
                  adj=adj, hyp=hyp)
    else:
        ans = f"\\dfrac{{{opp}}}{{{adj}}}"
        sol = tex(r"\tan\theta = \dfrac{{\text{{Opp}}}}{{\text{{Adj}}}} = \dfrac{{{opp}}}{{{adj}}}",
                  opp=opp, adj=adj)

    d = Diagram("right_triangle",
                q_sides={"a": str(opp), "b": str(adj), "c": str(hyp)},
                s_sides={"a": str(opp), "b": str(adj), "c": str(hyp)},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])

    return Exercise("write_ratio",
        parts=[Part("a", question=f"Write $\\{ratio}\\,{theta}°$ as a fraction.",
                    answer=ans, solution=sol)],
        context="The diagram shows a right-angled triangle.",
        diagram=d)


def gen_identify_ratio():
    theta = random.choice(NICE_ANGLES)
    case  = random.choice(["opp_hyp", "adj_hyp", "opp_adj"])
    opp = _ns(); adj = _ns()
    hyp = _r2(math.sqrt(opp**2 + adj**2))

    if case == "opp_hyp":
        ctx = f"In a right triangle, $\\theta={theta}°$, opposite={opp} cm, hypotenuse={hyp} cm."
        ans = r"\text{Use }\sin\theta=\dfrac{\text{Opp}}{\text{Hyp}}"
        sol = tex(r"\text{{Opp and Hyp}} \Rightarrow \sin\theta = \dfrac{{{opp}}}{{{hyp}}}",
                  opp=opp, hyp=hyp)
        d = Diagram("right_triangle",
                    q_sides={"a": str(opp), "b": "", "c": str(hyp)},
                    s_sides={"a": str(opp), "b": "", "c": str(hyp)},
                    q_angles=["", f"{theta}°", ""],
                    s_angles=["", f"{theta}°", ""])
    elif case == "adj_hyp":
        ctx = f"In a right triangle, $\\theta={theta}°$, adjacent={adj} cm, hypotenuse={hyp} cm."
        ans = r"\text{Use }\cos\theta=\dfrac{\text{Adj}}{\text{Hyp}}"
        sol = tex(r"\text{{Adj and Hyp}} \Rightarrow \cos\theta = \dfrac{{{adj}}}{{{hyp}}}",
                  adj=adj, hyp=hyp)
        d = Diagram("right_triangle",
                    q_sides={"a": "", "b": str(adj), "c": str(hyp)},
                    s_sides={"a": "", "b": str(adj), "c": str(hyp)},
                    q_angles=["", f"{theta}°", ""],
                    s_angles=["", f"{theta}°", ""])
    else:
        ctx = f"In a right triangle, $\\theta={theta}°$, opposite={opp} cm, adjacent={adj} cm."
        ans = r"\text{Use }\tan\theta=\dfrac{\text{Opp}}{\text{Adj}}"
        sol = tex(r"\text{{Opp and Adj}} \Rightarrow \tan\theta = \dfrac{{{opp}}}{{{adj}}}",
                  opp=opp, adj=adj)
        d = Diagram("right_triangle",
                    q_sides={"a": str(opp), "b": str(adj), "c": ""},
                    s_sides={"a": str(opp), "b": str(adj), "c": ""},
                    q_angles=["", f"{theta}°", ""],
                    s_angles=["", f"{theta}°", ""])

    return Exercise("identify_ratio",
        parts=[Part("a", question="State the correct ratio and write the equation.",
                    answer=ans, solution=sol)],
        context=ctx, diagram=d)


# ══════════════════════════════════════════════════════════════════
# LT3 — FINDING SIDES
# ══════════════════════════════════════════════════════════════════

def gen_find_side_sin():
    theta = random.choice(NICE_ANGLES); hyp = _ns()
    opp = _r2(hyp * _sin(theta)); ans = _fmt(_r2(opp))
    d = Diagram("right_triangle",
                q_sides={"a": "x",   "b": "", "c": str(hyp)},
                s_sides={"a": ans,   "b": "", "c": str(hyp)},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\sin {theta}° = \dfrac{{x}}{{{hyp}}}",
              r"x = {hyp} \times \sin {theta}°",
              r"x = {ans} \text{{ cm}}",
              theta=theta, hyp=hyp, ans=ans)
    return Exercise("find_side_sin",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Hypotenuse = {hyp} cm, θ = {theta}°.", diagram=d)


def gen_find_side_cos():
    theta = random.choice(NICE_ANGLES); hyp = _ns()
    adj = _r2(hyp * _cos(theta)); ans = _fmt(_r2(adj))
    d = Diagram("right_triangle",
                q_sides={"a": "",    "b": "x",  "c": str(hyp)},
                s_sides={"a": "",    "b": ans,   "c": str(hyp)},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\cos {theta}° = \dfrac{{x}}{{{hyp}}}",
              r"x = {hyp} \times \cos {theta}°",
              r"x = {ans} \text{{ cm}}",
              theta=theta, hyp=hyp, ans=ans)
    return Exercise("find_side_cos",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Hypotenuse = {hyp} cm, θ = {theta}°.", diagram=d)


def gen_find_side_tan():
    theta = random.choice(NICE_ANGLES); adj = _ns()
    opp = _r2(adj * _tan(theta)); ans = _fmt(_r2(opp))
    d = Diagram("right_triangle",
                q_sides={"a": "x",   "b": str(adj), "c": ""},
                s_sides={"a": ans,   "b": str(adj), "c": ""},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\tan {theta}° = \dfrac{{x}}{{{adj}}}",
              r"x = {adj} \times \tan {theta}°",
              r"x = {ans} \text{{ cm}}",
              theta=theta, adj=adj, ans=ans)
    return Exercise("find_side_tan",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Adjacent = {adj} cm, θ = {theta}°.", diagram=d)


def gen_find_side_hyp_sin():
    theta = random.choice(NICE_ANGLES); opp = _ns()
    hyp = _r2(opp / _sin(theta)); ans = _fmt(_r2(hyp))
    d = Diagram("right_triangle",
                q_sides={"a": str(opp), "b": "", "c": "x"},
                s_sides={"a": str(opp), "b": "", "c": ans},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\sin {theta}° = \dfrac{{{opp}}}{{x}}",
              r"x = \dfrac{{{opp}}}{{\sin {theta}°}}",
              r"x = {ans} \text{{ cm}}",
              theta=theta, opp=opp, ans=ans)
    return Exercise("find_side_hyp_sin",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Opposite = {opp} cm, θ = {theta}°.", diagram=d)


def gen_find_side_hyp_cos():
    theta = random.choice(NICE_ANGLES); adj = _ns()
    hyp = _r2(adj / _cos(theta)); ans = _fmt(_r2(hyp))
    d = Diagram("right_triangle",
                q_sides={"a": "",       "b": str(adj), "c": "x"},
                s_sides={"a": "",       "b": str(adj), "c": ans},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\cos {theta}° = \dfrac{{{adj}}}{{x}}",
              r"x = \dfrac{{{adj}}}{{\cos {theta}°}}",
              r"x = {ans} \text{{ cm}}",
              theta=theta, adj=adj, ans=ans)
    return Exercise("find_side_hyp_cos",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Adjacent = {adj} cm, θ = {theta}°.", diagram=d)


def gen_find_side_hyp_tan():
    theta = random.choice(NICE_ANGLES); opp = _ns()
    adj = _r2(opp / _tan(theta)); ans = _fmt(_r2(adj))
    d = Diagram("right_triangle",
                q_sides={"a": str(opp), "b": "x",  "c": ""},
                s_sides={"a": str(opp), "b": ans,   "c": ""},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\tan {theta}° = \dfrac{{{opp}}}{{x}}",
              r"x = \dfrac{{{opp}}}{{\tan {theta}°}}",
              r"x = {ans} \text{{ cm}}",
              theta=theta, opp=opp, ans=ans)
    return Exercise("find_side_hyp_tan",
        parts=[Part("a", question="Find $x$.",
                    answer=f"x = {ans} cm", solution=sol)],
        context=f"Opposite = {opp} cm, θ = {theta}°.", diagram=d)


# ══════════════════════════════════════════════════════════════════
# LT4 — FINDING ANGLES
# ══════════════════════════════════════════════════════════════════

def gen_find_angle_sin():
    theta = random.choice(NICE_ANGLES); hyp = _ns()
    opp = _r2(hyp * _sin(theta)); ans = f"{_asin(opp/hyp)}°"
    d = Diagram("right_triangle",
                q_sides={"a": str(opp), "b": "", "c": str(hyp)},
                s_sides={"a": str(opp), "b": "", "c": str(hyp)},
                q_angles=["", "?", ""],
                s_angles=["", ans, ""])
    sol = tex(r"\sin\theta = \dfrac{{{opp}}}{{{hyp}}}",
              r"\theta = \sin^{{-1}}\!\left(\dfrac{{{opp}}}{{{hyp}}}\right)",
              r"\theta = {ans}",
              opp=opp, hyp=hyp, ans=ans)
    return Exercise("find_angle_sin",
        parts=[Part("a", question=r"Find angle $\theta$.",
                    answer=f"θ = {ans}", solution=sol)],
        context=f"Opposite = {opp} cm, hypotenuse = {hyp} cm.", diagram=d)


def gen_find_angle_cos():
    theta = random.choice(NICE_ANGLES); hyp = _ns()
    adj = _r2(hyp * _cos(theta)); ans = f"{_acos(adj/hyp)}°"
    d = Diagram("right_triangle",
                q_sides={"a": "",       "b": str(adj), "c": str(hyp)},
                s_sides={"a": "",       "b": str(adj), "c": str(hyp)},
                q_angles=["", "?", ""],
                s_angles=["", ans, ""])
    sol = tex(r"\cos\theta = \dfrac{{{adj}}}{{{hyp}}}",
              r"\theta = \cos^{{-1}}\!\left(\dfrac{{{adj}}}{{{hyp}}}\right)",
              r"\theta = {ans}",
              adj=adj, hyp=hyp, ans=ans)
    return Exercise("find_angle_cos",
        parts=[Part("a", question=r"Find angle $\theta$.",
                    answer=f"θ = {ans}", solution=sol)],
        context=f"Adjacent = {adj} cm, hypotenuse = {hyp} cm.", diagram=d)


def gen_find_angle_tan():
    theta = random.choice(NICE_ANGLES); adj = _ns()
    opp = _r2(adj * _tan(theta)); ans = f"{_atan(opp/adj)}°"
    d = Diagram("right_triangle",
                q_sides={"a": str(opp), "b": str(adj), "c": ""},
                s_sides={"a": str(opp), "b": str(adj), "c": ""},
                q_angles=["", "?", ""],
                s_angles=["", ans, ""])
    sol = tex(r"\tan\theta = \dfrac{{{opp}}}{{{adj}}}",
              r"\theta = \tan^{{-1}}\!\left(\dfrac{{{opp}}}{{{adj}}}\right)",
              r"\theta = {ans}",
              opp=opp, adj=adj, ans=ans)
    return Exercise("find_angle_tan",
        parts=[Part("a", question=r"Find angle $\theta$.",
                    answer=f"θ = {ans}", solution=sol)],
        context=f"Opposite = {opp} cm, adjacent = {adj} cm.", diagram=d)


# ══════════════════════════════════════════════════════════════════
# LT5 — APPLICATIONS
# ══════════════════════════════════════════════════════════════════

def gen_elevation_basic():
    theta = random.choice([25,30,35,40,45,50,55])
    dist  = random.choice([10,15,20,25,30,40,50])
    h = _r2(dist * _tan(theta)); ans = _fmt(_r2(h))
    d = Diagram("right_triangle",
                q_sides={"a": "h",  "b": str(dist), "c": ""},
                s_sides={"a": ans,  "b": str(dist), "c": ""},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\tan {theta}° = \dfrac{{h}}{{{dist}}}",
              r"h = {dist} \times \tan {theta}°",
              r"h = {ans} \text{{ m}}",
              theta=theta, dist=dist, ans=ans)
    return Exercise("elevation_basic",
        parts=[Part("a", question="Find the height of the tower.",
                    answer=f"h = {ans} m", solution=sol)],
        context=(f"A person stands {dist} m from a vertical tower. "
                 f"The angle of elevation to the top is {theta}°."),
        diagram=d)


def gen_depression_basic():
    theta = random.choice([25,30,35,40,45,50,55])
    h     = random.choice([10,15,20,25,30,40,50])
    dist  = _r2(h / _tan(theta)); ans = _fmt(_r2(dist))
    # theta_vertex=2 → angle at V2 (top-left) for depression
    d = Diagram("right_triangle",
                q_sides={"a": str(h), "b": "d",  "c": ""},
                s_sides={"a": str(h), "b": ans,   "c": ""},
                q_angles=["", "", f"{theta}°"],
                s_angles=["", "", f"{theta}°"])
    sol = tex(r"\tan {theta}° = \dfrac{{{h}}}{{d}}",
              r"d = \dfrac{{{h}}}{{\tan {theta}°}}",
              r"d = {ans} \text{{ m}}",
              theta=theta, h=h, ans=ans)
    return Exercise("depression_basic",
        parts=[Part("a", question="Find the horizontal distance from the cliff base to the boat.",
                    answer=f"d = {ans} m", solution=sol)],
        context=(f"An observer at the top of a {h} m cliff looks down at a boat "
                 f"with angle of depression {theta}°."),
        diagram=d)


def gen_elevation_word():
    theta = random.choice([25,30,35,40,45,50])
    h     = random.choice([10,15,20,30,40,50])
    dist  = _r2(h / _tan(theta)); ans = _fmt(_r2(dist))
    ctx = random.choice([
        f"A bird sits on top of a {h} m pole. From a point on the ground, the angle of elevation is {theta}°.",
        f"A tree of height {h} m is observed at an angle of elevation of {theta}° from the ground.",
    ])
    d = Diagram("right_triangle",
                q_sides={"a": str(h), "b": "d",  "c": ""},
                s_sides={"a": str(h), "b": ans,   "c": ""},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\tan {theta}° = \dfrac{{{h}}}{{d}}",
              r"d = \dfrac{{{h}}}{{\tan {theta}°}}",
              r"d = {ans} \text{{ m}}",
              theta=theta, h=h, ans=ans)
    return Exercise("elevation_word",
        parts=[
            Part("a", question="Draw and label a diagram.",
                 answer=r"\text{Right triangle: vertical height, horizontal distance, θ at observer}",
                 solution=r"\text{Vertical = height, horizontal = distance, }\theta\text{ at base}"),
            Part("b", question="Find the horizontal distance to 2 d.p.",
                 answer=f"d = {ans} m", solution=sol),
        ],
        context=ctx, diagram=d)


def gen_depression_word():
    theta = random.choice([25,30,35,40,45,50])
    h     = random.choice([15,20,30,40,50,60])
    dist  = _r2(h / _tan(theta)); ans = _fmt(_r2(dist))
    ctx = random.choice([
        f"A lighthouse keeper {h} m above sea level spots a ship at angle of depression {theta}°.",
        f"A drone hovers {h} m above ground. Angle of depression to a landmark is {theta}°.",
    ])
    d = Diagram("right_triangle",
                q_sides={"a": str(h), "b": "d",  "c": ""},
                s_sides={"a": str(h), "b": ans,   "c": ""},
                q_angles=["", "", f"{theta}°"],
                s_angles=["", "", f"{theta}°"])
    sol = tex(r"\text{{Depression angle}} = {theta}° \text{{ (alternate angles)}}",
              r"\tan {theta}° = \dfrac{{{h}}}{{d}}",
              r"d = \dfrac{{{h}}}{{\tan {theta}°}} = {ans} \text{{ m}}",
              theta=theta, h=h, ans=ans)
    return Exercise("depression_word",
        parts=[
            Part("a", question="Draw and label a diagram.",
                 answer=r"\text{Horizontal at observer level, angle of depression downward}",
                 solution=r"\text{Horizontal line at top; depression angle = interior angle}"),
            Part("b", question="Find the horizontal distance to 2 d.p.",
                 answer=f"d = {ans} m", solution=sol),
        ],
        context=ctx, diagram=d)


def gen_shadow_flagpole():
    shadow = round(random.uniform(5.0, 12.0), 2)
    theta  = random.choice([55, 60, 63, 65, 70])
    height = _r2(shadow * _tan(theta)); ans = _fmt(_r2(height))
    d = Diagram("right_triangle",
                q_sides={"a": "h",  "b": f"{shadow}m", "c": ""},
                s_sides={"a": ans,  "b": f"{shadow}m", "c": ""},
                q_angles=["", f"{theta}°", ""],
                s_angles=["", f"{theta}°", ""])
    sol = tex(r"\tan {theta}° = \dfrac{{h}}{{{shadow}}}",
              r"h = {shadow} \times \tan {theta}° = {ans} \text{{ m}}",
              theta=theta, shadow=shadow, ans=ans)
    return Exercise("shadow_flagpole",
        parts=[Part("a", question="Find the height of the flagpole.",
                    answer=f"h = {ans} m", solution=sol)],
        context=f"A flagpole casts a shadow of {shadow} m when the angle of elevation to the sun is {theta}°.",
        diagram=d)


def gen_hill_gradient():
    angle    = random.choice([12,15,18,20,22,25])
    dist     = random.choice([100,120,150,180,200])
    h        = _r2(dist * _sin(angle))
    target_h = random.choice([60,70,80,90,100])
    walked   = _r2(target_h / _sin(angle))
    sol_a = tex(r"h = {dist} \sin {angle}° = {h} \text{{ m}}",
                dist=dist, angle=angle, h=_fmt(_r2(h)))
    sol_b = tex(r"\sin {angle}° = \dfrac{{{t}}}{{d}}",
                r"d = \dfrac{{{t}}}{{\sin {angle}°}} = {w} \text{{ m}}",
                angle=angle, t=target_h, w=_fmt(_r2(walked)))
    return Exercise("hill_gradient",
        parts=[
            Part("a", question=f"If you walk {dist} m up the hill, what is your height above sea level?",
                 answer=f"h = {_fmt(_r2(h))} m", solution=sol_a),
            Part("b", question=f"If you climb to {target_h} m above sea level, how far have you walked?",
                 answer=f"d = {_fmt(_r2(walked))} m", solution=sol_b),
        ],
        context=f"A hill is inclined at {angle}° to the horizontal, base at sea level.")


def gen_train_gradient():
    rise  = round(random.uniform(4.0, 8.0), 1)
    track = random.choice([150,175,200,220,250])
    theta = _asin(rise / track); ans = f"{theta}°"
    sol = tex(r"\sin\theta = \dfrac{{{rise}}}{{{track}}}",
              r"\theta = \sin^{{-1}}\!\left(\dfrac{{{rise}}}{{{track}}}\right) = {ans}",
              rise=rise, track=track, ans=ans)
    return Exercise("train_gradient",
        parts=[Part("a", question="Find the angle of incline.",
                    answer=f"θ = {ans}", solution=sol)],
        context=f"A train climbs {rise} m for every {track} m of track.")


def gen_elevation_depression_pair():
    h   = random.choice([40,45,50,56,60,65])
    d   = random.choice([90,100,110,113,120])
    elev = _atan(h/d); ans = f"{elev}°"
    sol_a = tex(r"\tan\theta = \dfrac{{{h}}}{{{d}}}",
                r"\theta = \tan^{{-1}}\!\left(\dfrac{{{h}}}{{{d}}}\right) = {ans}",
                h=h, d=d, ans=ans)
    sol_b = tex(r"\text{{Depression angle}} = \text{{elevation angle}} = {ans}",
                r"\text{{(Alternate interior angles with horizontal)}}",
                ans=ans)
    return Exercise("elevation_depression_pair",
        parts=[
            Part("a", question="Find the angle of elevation from A to the top of the building.",
                 answer=f"θ = {ans}", solution=sol_a),
            Part("b", question="What is the angle of depression from the top to A?",
                 answer=f"θ = {ans}", solution=sol_b),
        ],
        context=f"A {h} m building. Point $A$ is {d} m from its base.")


def gen_kite_height():
    string_m  = random.choice([6,7,8,9,10])
    angle     = random.choice([55,60,63,65,70])
    handle_cm = random.choice([70,75,80,85,90])
    handle_m  = handle_cm / 100
    vert_m    = _r2(string_m * _sin(angle))
    total_m   = _r2(vert_m + handle_m); ans = _fmt(_r2(total_m))
    d = Diagram("right_triangle",
                q_sides={"a": "h",             "b": "", "c": str(string_m)},
                s_sides={"a": _fmt(_r2(vert_m)), "b": "", "c": str(string_m)},
                q_angles=["", f"{angle}°", ""],
                s_angles=["", f"{angle}°", ""])
    sol = tex(
        r"\text{{Vertical}} = {sm} \sin {angle}° = {vm} \text{{ m}}",
        r"\text{{Handle}} = {hcm} \text{{ cm}} = {hm} \text{{ m}}",
        r"\text{{Total}} = {vm} + {hm} = {ans} \text{{ m}}",
        sm=string_m, angle=angle, vm=_fmt(_r2(vert_m)),
        hcm=handle_cm, hm=handle_m, ans=ans)
    return Exercise("kite_height",
        parts=[Part("a", question="Calculate the height of the kite above the ground.",
                    answer=f"Height = {ans} m", solution=sol)],
        given=[f"\\text{{String}} = {string_m}\\text{{ m}}",
               f"\\text{{Angle}} = {angle}°",
               f"\\text{{Handle}} = {handle_cm}\\text{{ cm}}"],
        context=(f"The handle is held {handle_cm} cm above the ground. "
                 f"The string is {string_m} m long at {angle}° to the horizontal."),
        diagram=d)


# ══════════════════════════════════════════════════════════════════
# LT6 — MULTI-STEP
# ══════════════════════════════════════════════════════════════════

def gen_multi_step_two_triangles():
    theta1 = random.choice([30,35,40,45,50])
    theta2 = random.choice([25,30,35,40])
    d1     = random.choice([10,12,15,20])
    h      = _r2(d1 * _tan(theta1))
    d2     = _r2(h / _tan(theta2))
    sol_a = tex(r"h = {d1} \times \tan {t1}° = {h} \text{{ m}}",
                d1=d1, t1=theta1, h=_fmt(_r2(h)))
    sol_b = tex(r"d_B = \dfrac{{{h}}}{{\tan {t2}°}} = {d2} \text{{ m}}",
                h=_fmt(_r2(h)), t2=theta2, d2=_fmt(_r2(d2)))
    return Exercise("multi_step_two_triangles",
        parts=[
            Part("a", question="Find the height of the tower.",
                 answer=f"{_fmt(_r2(h))} m", solution=sol_a),
            Part("b", question="Find the horizontal distance from B to the tower.",
                 answer=f"{_fmt(_r2(d2))} m", solution=sol_b),
        ],
        context=(f"Two points A and B on opposite sides of a tower. "
                 f"From A: elevation {theta1}°, distance {d1} m. From B: elevation {theta2}°."))


def gen_multi_step_bearing():
    bearing  = random.choice([30,40,45,50,60,70])
    distance = random.choice([10,12,15,20,25])
    north = _r2(distance * _cos(bearing))
    east  = _r2(distance * _sin(bearing))
    sol_n = tex(r"N = {dist} \cos {b}° = {n} \text{{ km}}",
                dist=distance, b=bearing, n=_fmt(_r2(north)))
    sol_e = tex(r"E = {dist} \sin {b}° = {e} \text{{ km}}",
                dist=distance, b=bearing, e=_fmt(_r2(east)))
    return Exercise("multi_step_bearing",
        parts=[
            Part("a", question="How far north of port is the ship?",
                 answer=f"{_fmt(_r2(north))} km", solution=sol_n),
            Part("b", question="How far east of port is the ship?",
                 answer=f"{_fmt(_r2(east))} km", solution=sol_e),
        ],
        context=f"A ship sails {distance} km on bearing {bearing:03d}°.")


def gen_ladder_safety():
    h    = round(random.uniform(3.5, 6.5), 1)
    d    = round(random.uniform(0.8, 2.0), 1)
    theta = _atan(h/d); safe = 70.0 <= theta <= 80.0
    lad  = _fmt(_r2(math.sqrt(h**2 + d**2)))
    safety_str = "safe (70°–80°)" if safe else "NOT safe (outside 70°–80°)"
    diag = Diagram("right_triangle",
                   q_sides={"a": f"{h}m", "b": f"{d}m", "c": "L"},
                   s_sides={"a": f"{h}m", "b": f"{d}m", "c": f"{lad}m"},
                   q_angles=["", "θ", ""],
                   s_angles=["", f"{theta}°", ""])
    sol_a = tex(r"\tan\theta = \dfrac{{{h}}}{{{d}}}",
                r"\theta = \tan^{{-1}}\!\left(\dfrac{{{h}}}{{{d}}}\right) = {theta}°",
                r"{theta}° \text{{ is {safety}}}",
                h=h, d=d, theta=theta, safety=safety_str)
    sol_b = tex(r"L^2 = {h}^2 + {d}^2 = {sq}",
                r"L = \sqrt{{{sq}}} = {lad} \text{{ m}}",
                h=h, d=d, sq=_r2(h**2+d**2), lad=lad)
    return Exercise("ladder_safety",
        parts=[
            Part("a", question="Is the ladder safe? Show your working.",
                 answer=f"θ = {theta}° — {safety_str}", solution=sol_a),
            Part("b", question="Calculate the length of the ladder.",
                 answer=f"L = {lad} m", solution=sol_b),
        ],
        context=(f"A ladder leans against a wall. "
                 f"Wall height = {h} m, base distance = {d} m. "
                 f"Safe angle: 70°–80° to the ground."),
        diagram=diag)


def gen_ramp_angle():
    dist_m = round(random.uniform(1.5, 3.5), 1)
    h_cm   = random.choice([15,18,20,22,25,30])
    h_m    = h_cm / 100
    theta  = _atan(h_m / dist_m); ans = f"{theta}°"
    d = Diagram("right_triangle",
                q_sides={"a": f"{h_cm}cm", "b": f"{dist_m}m", "c": ""},
                s_sides={"a": f"{h_cm}cm", "b": f"{dist_m}m", "c": ""},
                q_angles=["", "y", ""],
                s_angles=["", ans, ""])
    sol = tex(r"\text{{Convert: }} {hcm} \text{{ cm}} = {hm} \text{{ m}}",
              r"\tan y = \dfrac{{{hm}}}{{{dist}}}",
              r"y = \tan^{{-1}}\!\left(\dfrac{{{hm}}}{{{dist}}}\right) = {ans}",
              hcm=h_cm, hm=h_m, dist=dist_m, ans=ans)
    return Exercise("ramp_angle",
        parts=[Part("a", question="Calculate the size of angle $y$.",
                    answer=f"y = {ans}", solution=sol)],
        context=f"A ramp: horizontal distance {dist_m} m, height {h_cm} cm.",
        diagram=d)


def gen_two_triangles_vertex():
    AB  = random.choice([8,9,10,11,12])
    BC  = random.choice([2,3,4])
    BCD = random.choice([55,60,65,70])
    BD  = _r2(BC * _tan(BCD))
    ABD = _asin(min(BD/AB, 0.999)); ans = f"{ABD}°"
    sol = tex(
        r"\triangle BCD: \quad BD = BC \times \tan {BCD}° = {BC} \times \tan {BCD}° = {BD} \text{{ cm}}",
        r"\triangle ABD: \quad \sin(x) = \dfrac{{{BD}}}{{{AB}}}",
        r"x = \sin^{{-1}}\!\left(\dfrac{{{BD}}}{{{AB}}}\right) = {ans}",
        BCD=BCD, BC=BC, BD=_fmt(_r2(BD)), AB=AB, ans=ans)
    return Exercise("two_triangles_vertex",
        parts=[Part("a", question="Calculate angle $ABD$ (marked $x$).",
                    answer=f"∠ABD = {ans}", solution=sol)],
        given=[f"AB={AB}\\text{{ cm}}", f"BC={BC}\\text{{ cm}}",
               f"\\angle BCD={BCD}°"],
        context="Two right-angled triangles share side BD.")


def gen_ratio_split_angle():
    AB  = random.choice([12,14,15,16,18])
    ABD = random.choice([60,65,70,72,75])
    r1, r2 = 5, 2
    DBC = round(ABD * r2 / r1, 1)
    BD  = _r2(AB * _sin(ABD))
    CD  = _r2(BD * _tan(DBC)); ans = _fmt(_r2(CD))
    sol = tex(
        r"\angle DBC = \dfrac{{2}}{{5}} \times {ABD}° = {DBC}°",
        r"BD = {AB} \sin {ABD}° = {BD} \text{{ cm}}",
        r"CD = BD \times \tan {DBC}° = {BD} \times \tan {DBC}° = {ans} \text{{ cm}}",
        ABD=ABD, DBC=DBC, AB=AB, BD=_fmt(_r2(BD)), ans=ans)
    return Exercise("ratio_split_angle",
        parts=[Part("a", question="Work out the length of $CD$.",
                    answer=f"CD = {ans} cm", solution=sol)],
        given=[f"AB={AB}\\text{{ cm}}",
               f"\\angle ABD={ABD}°",
               f"\\angle ABD:\\angle DBC={r1}:{r2}"],
        context="Right-angled triangles ABD and BCD share side BD.")


def gen_isosceles_split():
    equal = random.choice([25, 28, 30, 32, 35])
    base  = random.choice([10, 12, 14, 16, 18, 20])
    half  = base / 2

    # Pick 3 distinct vertex letters, assign by geometric role
    apex, bl, br = pick_verts(3)
    # apex = top,  bl = left base corner,  br = right base corner
    # Equal sides: bl-apex and br-apex  |  Base: bl-br

    BAC = _asin(half / equal)        # angle at each base corner
    ABC = round(180 - 2 * BAC, 1)   # angle at apex

    # Isosceles geometry: vertices=[bl, br, apex]
    #   V0=bl (left base)  V1=br (right base)  V2=apex
    # angle_values[V0, V1, V2] = [BAC, BAC, ABC]
    d = Diagram("isosceles",
                q_sides={"equal": str(equal), "base": str(base)},
                s_sides={"equal": str(equal), "base": str(base)},
                vertices=[bl, br, apex],
                show_vertices=True,
                s_angles=[f"{BAC}°", f"{BAC}°", f"{ABC}°"])

    sol_a = tex(
        r"\text{{Drop perpendicular from {apex} to midpoint M of {bl}{br}}}",
        r"{bl}M = \dfrac{{{base}}}{{2}} = {half} \text{{ cm}}",
        r"\sin(\angle {apex}{bl}{br}) = \dfrac{{{half}}}{{{equal}}}",
        r"\angle {apex}{bl}{br} = \sin^{{-1}}\!\left(\dfrac{{{half}}}{{{equal}}}\right) = {BAC}°",
        apex=apex, bl=bl, br=br, base=base, half=half, equal=equal, BAC=BAC)

    sol_b = tex(
        r"\angle {bl}{apex}{br} = 180° - 2 \times {BAC}° = {ABC}°",
        bl=bl, apex=apex, br=br, BAC=BAC, ABC=ABC)

    return Exercise("isosceles_split",
        parts=[
            Part("a", question=f"Work out angle ${apex}{bl}{br}$.",
                 answer=f"\\angle {apex}{bl}{br} = {BAC}°", solution=sol_a),
            Part("b", question=f"Work out angle ${bl}{apex}{br}$.",
                 answer=f"\\angle {bl}{apex}{br} = {ABC}°", solution=sol_b),
        ],
        context=(f"Isosceles triangle ${bl}{apex}{br}$: "
                 f"${bl}{apex} = {apex}{br} = {equal}$ cm, "
                 f"${bl}{br} = {base}$ cm."),
        diagram=d)


def gen_bearing_triangle():
    d_east  = random.choice([8,9,10,12,15])
    d_north = random.choice([6,7,8,9,10])
    direct  = _r2(math.sqrt(d_east**2 + d_north**2))
    ang     = _atan(d_east / d_north); bearing = round(ang)
    sol_a = tex(r"d^2 = {de}^2 + {dn}^2 = {sq}",
                r"d = \sqrt{{{sq}}} = {direct} \text{{ km}}",
                de=d_east, dn=d_north, sq=d_east**2+d_north**2,
                direct=_fmt(_r2(direct)))
    sol_b = tex(r"\tan\theta = \dfrac{{{de}}}{{{dn}}}",
                r"\theta = \tan^{{-1}}\!\left(\dfrac{{{de}}}{{{dn}}}\right) = {ang}°",
                r"\text{{Bearing}} = {b:03d}°",
                de=d_east, dn=d_north, ang=ang, b=bearing)
    return Exercise("bearing_triangle",
        parts=[
            Part("a", question="Find the direct distance.",
                 answer=f"d = {_fmt(_r2(direct))} km", solution=sol_a),
            Part("b", question="Calculate the bearing.",
                 answer=f"Bearing = {bearing:03d}°", solution=sol_b),
        ],
        context=f"A helicopter flies {d_east} km due east, then {d_north} km due north.")


def gen_cliff_lighthouse():
    h_cliff = random.choice([80,90,100,110,120])
    h_light = random.choice([20,25,30,35,40])
    theta   = random.choice([18,20,22,25])
    total   = h_cliff + h_light
    dist    = _r2(total / _tan(theta))
    ang_cliff = _atan(h_cliff / dist)
    sol_a = tex(r"\tan {theta}° = \dfrac{{{total}}}{{d}}",
                r"d = \dfrac{{{total}}}{{\tan {theta}°}} = {dist} \text{{ m}}",
                theta=theta, total=total, dist=_fmt(_r2(dist)))
    sol_b = tex(r"\tan\alpha = \dfrac{{{hc}}}{{{dist}}}",
                r"\alpha = \tan^{{-1}}\!\left(\dfrac{{{hc}}}{{{dist}}}\right) = {ang}°",
                hc=h_cliff, dist=_fmt(_r2(dist)), ang=ang_cliff)
    return Exercise("cliff_lighthouse",
        parts=[
            Part("a", question="Find the distance from the boat to the base of the cliff.",
                 answer=f"d = {_fmt(_r2(dist))} m", solution=sol_a),
            Part("b", question="Find the angle of elevation from the boat to the top of the cliff.",
                 answer=f"α = {ang_cliff}°", solution=sol_b),
        ],
        given=[f"\\text{{Cliff}} = {h_cliff}\\text{{ m}}",
               f"\\text{{Lighthouse}} = {h_light}\\text{{ m}}",
               f"\\text{{Elevation to lighthouse top}} = {theta}°"],
        context=(f"A boat approaches a {h_cliff} m cliff with a {h_light} m lighthouse on top. "
                 f"Angle of elevation to top of lighthouse is {theta}°."))


def gen_circle_chord_radius():
    theta  = random.choice([30,34,36,40,45,50])
    chord  = round(random.uniform(3.0, 8.0), 1)
    half   = chord / 2
    radius = _r2(half / _sin(theta)); ans = _fmt(_r2(radius))
    sol = tex(r"\text{{Half-chord}} = \dfrac{{{chord}}}{{2}} = {half} \text{{ cm}}",
              r"\sin {theta}° = \dfrac{{{half}}}{{r}}",
              r"r = \dfrac{{{half}}}{{\sin {theta}°}} = {ans} \text{{ cm}}",
              chord=chord, half=half, theta=theta, ans=ans)
    return Exercise("circle_chord_radius",
        parts=[Part("a", question="Find the radius of the circle.",
                    answer=f"r = {ans} cm", solution=sol)],
        given=[f"\\text{{Chord}} = {chord}\\text{{ cm}}",
               f"\\text{{Angle at centre}} = {theta}°"],
        context=f"A chord of {chord} cm subtends an angle of {theta}° at the centre.")


def gen_flagpole_two_elevations():
    d     = random.choice([150,180,200,220])
    alpha = random.choice([32,34,36,38])
    beta  = alpha + random.choice([2,3,4])
    h_bldg = _r2(d * _tan(alpha))
    h_top  = _r2(d * _tan(beta))
    h_flag = _r2(h_top - h_bldg); ans = _fmt(_r2(h_flag))
    sol = tex(r"h_1 = {d} \tan {a}° = {h1} \text{{ m}}",
              r"h_2 = {d} \tan {b}° = {h2} \text{{ m}}",
              r"\text{{Flagpole}} = {h2} - {h1} = {ans} \text{{ m}}",
              d=d, a=alpha, b=beta,
              h1=_fmt(_r2(h_bldg)), h2=_fmt(_r2(h_top)), ans=ans)
    return Exercise("flagpole_two_elevations",
        parts=[Part("a", question="Find the height of the flagpole.",
                    answer=f"h = {ans} m", solution=sol)],
        context=(f"From {d} m away: elevation to flagpole bottom = {alpha}°, "
                 f"to top = {beta}°."))


def gen_cliff_boat_closer():
    h    = random.choice([12,15,18,20])
    ang1 = round(random.uniform(2.0, 3.5), 1)
    ang2 = round(ang1 + random.uniform(1.0, 2.5), 1)
    d1   = _r2(h / _tan(ang1)); d2 = _r2(h / _tan(ang2))
    diff = _r2(d1 - d2); ans = _fmt(_r2(diff))
    sol = tex(r"d_1 = \dfrac{{{h}}}{{\tan {a1}°}} = {d1} \text{{ m}}",
              r"d_2 = \dfrac{{{h}}}{{\tan {a2}°}} = {d2} \text{{ m}}",
              r"\text{{Moved}} = {d1} - {d2} = {ans} \text{{ m}}",
              h=h, a1=ang1, a2=ang2,
              d1=_fmt(_r2(d1)), d2=_fmt(_r2(d2)), ans=ans)
    return Exercise("cliff_boat_closer",
        parts=[Part("a", question="How much closer must the boat move?",
                    answer=f"{ans} m", solution=sol)],
        context=(f"Depression from top of {h} m cliff: first {ang1}°, then {ang2}°. "
                 f"How far does the boat move?"))


def gen_helicopter_overhead():
    speed_kmh = random.choice([80,90,100,110,120])
    time_s    = random.choice([15,20,25,30])
    angle     = random.choice([55,60,65,70])
    dist_km   = _r2(speed_kmh * time_s / 3600)
    height_km = _r2(dist_km * _tan(angle))
    height_m  = _r2(height_km * 1000); ans = _fmt(_r2(height_m))
    sol = tex(
        r"\text{{Distance}} = {speed} \times \dfrac{{{t}}}{{3600}} = {dist} \text{{ km}}",
        r"h = {dist} \times \tan {angle}° = {hkm} \text{{ km}}",
        r"h = {ans} \text{{ m}}",
        speed=speed_kmh, t=time_s, dist=_fmt(_r2(dist_km)),
        angle=angle, hkm=_fmt(_r2(height_km)), ans=ans)
    return Exercise("helicopter_overhead",
        parts=[Part("a", question="Find the height of the helicopter.",
                    answer=f"h = {ans} m", solution=sol)],
        context=(f"Helicopter at {speed_kmh} km/h. "
                 f"Takes {time_s} s to go from overhead to elevation angle {angle}°."))


# ══════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    "label_sides":               gen_label_sides,
    "write_ratio":               gen_write_ratio,
    "identify_ratio":            gen_identify_ratio,
    "find_side_sin":             gen_find_side_sin,
    "find_side_cos":             gen_find_side_cos,
    "find_side_tan":             gen_find_side_tan,
    "find_side_hyp_sin":         gen_find_side_hyp_sin,
    "find_side_hyp_cos":         gen_find_side_hyp_cos,
    "find_side_hyp_tan":         gen_find_side_hyp_tan,
    "find_angle_sin":            gen_find_angle_sin,
    "find_angle_cos":            gen_find_angle_cos,
    "find_angle_tan":            gen_find_angle_tan,
    "elevation_basic":           gen_elevation_basic,
    "depression_basic":          gen_depression_basic,
    "elevation_word":            gen_elevation_word,
    "depression_word":           gen_depression_word,
    "shadow_flagpole":           gen_shadow_flagpole,
    "hill_gradient":             gen_hill_gradient,
    "train_gradient":            gen_train_gradient,
    "elevation_depression_pair": gen_elevation_depression_pair,
    "kite_height":               gen_kite_height,
    "multi_step_two_triangles":  gen_multi_step_two_triangles,
    "multi_step_bearing":        gen_multi_step_bearing,
    "ladder_safety":             gen_ladder_safety,
    "ramp_angle":                gen_ramp_angle,
    "two_triangles_vertex":      gen_two_triangles_vertex,
    "ratio_split_angle":         gen_ratio_split_angle,
    "isosceles_split":           gen_isosceles_split,
    "bearing_triangle":          gen_bearing_triangle,
    "cliff_lighthouse":          gen_cliff_lighthouse,
    "circle_chord_radius":       gen_circle_chord_radius,
    "flagpole_two_elevations":   gen_flagpole_two_elevations,
    "cliff_boat_closer":         gen_cliff_boat_closer,
    "helicopter_overhead":       gen_helicopter_overhead,
}


# ══════════════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════════════

def generate(types, seed=None, count=6, counts=None, show_solutions=False):
    if seed is not None:
        random.seed(seed)

    _counts = counts or {}
    exercises = []

    for ex_type in types:
        if ex_type not in REGISTRY:
            raise ValueError(
                f"Unknown type: '{ex_type}'. "
                f"Available: {sorted(REGISTRY.keys())}"
            )
        gen_fn = REGISTRY[ex_type]
        n      = _counts.get(ex_type, count)

        # Generate first exercise to detect layout
        first = gen_fn()
        # List-layout exercises (with context/diagram) generate once per slot
        is_list = (first.context or first.diagram_svg
                   or any(not p.expression for p in first.parts))
        if is_list and ex_type not in _counts:
            n = 1

        all_ex = [first] + [gen_fn() for _ in range(n - 1)]

        # Merge parts from multiple exercises into one
        merged = all_ex[0]
        if len(all_ex) > 1:
            labels = list("abcdefghijklmnopqrstuvwxyz")
            all_parts = []
            for ex in all_ex:
                for p in ex.parts:
                    p.label = labels[len(all_parts)]
                    all_parts.append(p)
            merged.parts = all_parts

        exercises.append(merged)

    return build_output(
        exercises, METADATA,
        show_solutions=show_solutions,
        worksheet_meta={
            "title":          "Trigonometry",
            "unit":           "Unit 1: Trigonometry",
            "date":           str(date.today()),
            "seed":           seed,
            "show_solutions": show_solutions,
        },
        unit_prefix="trig",
    )


def generate_session(types_json, seed=None, count=3, counts_json=None):
    types  = json.loads(types_json)
    counts = json.loads(counts_json) if counts_json else None
    return json.dumps(generate(types=types, seed=seed, count=count, counts=counts))


# ══════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate trigonometry exercises")
    parser.add_argument("--types",    nargs="+", default=["find_side_sin"])
    parser.add_argument("--seed",     type=int,  default=None)
    parser.add_argument("--count",    type=int,  default=3)
    parser.add_argument("--solutions",action="store_true")
    parser.add_argument("--list-types", action="store_true")
    args = parser.parse_args()

    if args.list_types:
        badges = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        for k in sorted(REGISTRY.keys()):
            m = METADATA.get(k, {})
            d = m.get("difficulty", "?")
            print(f"  {badges.get(d,'⚪')}  {k:<35} {m.get('subtopic','')}")
    else:
        result = generate(types=args.types, seed=args.seed,
                          count=args.count, show_solutions=args.solutions)
        print(f"Generated {len(result['_exercises_qmd'])} exercises.")
        for ex in result["_exercises_qmd"]:
            print(f"\n{'='*60}")
            print(f"Type: {ex['type']} | Difficulty: {ex['difficulty']}")
            print(ex["rendered"][:400])
