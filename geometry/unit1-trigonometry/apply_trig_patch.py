#!/usr/bin/env python3
"""
Trigonometry.py patch — apply these two changes:

CHANGE 1: Add "string" to the imports line (line 1)
  FROM: import random, math, json
  TO:   import random, math, json, string

CHANGE 2: Replace gen_label_sides vertex selection (2 lines, ~line 225)
  FROM:
    verts=random.choice([("A","B","C"),("P","Q","R"),("X","Y","Z")])
    vA,vB,vC=verts
  TO:
    vA, vB, vC = random.sample(string.ascii_uppercase, 3)
    # vA=right-angle corner, vB=theta corner, vC=top corner

CHANGE 3: Replace entire gen_isosceles_split function (~line 420):
"""

NEW_GEN_ISOSCELES_SPLIT = '''
def gen_isosceles_split():
    equal = random.choice([25, 28, 30, 32, 35])
    base  = random.choice([10, 12, 14, 16, 18, 20])
    half  = base / 2

    # Pick 3 distinct random vertex letters, assign by geometric role
    apex, bl, br = random.sample(string.ascii_uppercase, 3)
    # apex = top vertex
    # bl   = left  base corner    equal sides: bl-apex and br-apex
    # br   = right base corner    base:        bl-br

    BAC = _asin_deg(half / equal)       # angle at each base corner
    ABC = round(180 - 2 * BAC, 1)      # angle at apex

    sol_a = steps(
        f"\\text{{Drop perpendicular from {apex} to midpoint }}M\\text{{ of {bl}{br}}}",
        f"{bl}M = \\dfrac{{{base}}}{{2}} = {half}\\text{{ cm}}",
        f"\\sin(\\angle {apex}{bl}{br}) = \\dfrac{{{half}}}{{{equal}}}",
        f"\\angle {apex}{bl}{br} = \\sin^{{-1}}\\!\\left("
        f"\\dfrac{{{half}}}{{{equal}}}\\right) = {BAC}°"
    )
    sol_b = steps(
        f"\\angle {bl}{apex}{br} = 180° - 2 \\times {BAC}° = {ABC}°"
    )

    # vertices=[bl, br, apex] matches isosceles geometry:
    #   V0=bl (left base), V1=br (right base), V2=apex
    # angle_values must match [V0, V1, V2]:
    #   V0,V1 = base corners → BAC°  each
    #   V2    = apex         → ABC°
    svg_q = SVG.figure("isosceles",
                       sides={"equal": str(equal), "base": str(base)},
                       vertices=[bl, br, apex],
                       show_angles=False, show_vertices=True)
    svg_s = SVG.figure("isosceles",
                       sides={"equal": str(equal), "base": str(base)},
                       vertices=[bl, br, apex],
                       show_angles=False, show_vertices=True,
                       angle_values=[f"{BAC}°", f"{BAC}°", f"{ABC}°"])

    return _ex("isosceles_split", parts=[
        make_part("a",
            question=f"Work out angle ${apex}{bl}{br}$.",
            answer_latex=f"\\angle {apex}{bl}{br} = {BAC}°",
            solution_latex=sol_a),
        make_part("b",
            question=f"Work out angle ${bl}{apex}{br}$.",
            answer_latex=f"\\angle {bl}{apex}{br} = {ABC}°",
            solution_latex=sol_b),
    ],
    context=(f"Isosceles triangle ${bl}{apex}{br}$: "
             f"${bl}{apex} = {apex}{br} = {equal}$ cm, "
             f"${bl}{br} = {base}$ cm."),
    diagram_svg=svg_q,
    solution_svg=svg_s)
'''

if __name__ == "__main__":
    import sys, re
    path = sys.argv[1] if len(sys.argv) > 1 else "Trigonometry.py"
    with open(path) as f:
        code = f.read()

    # Add string import
    code = code.replace(
        "import random, math, json",
        "import random, math, json, string",
        1
    )

    # Patch gen_label_sides
    code = code.replace(
        '    verts=random.choice([("A","B","C"),("P","Q","R"),("X","Y","Z")])\n    vA,vB,vC=verts',
        '    vA, vB, vC = random.sample(string.ascii_uppercase, 3)\n    # vA=right-angle corner, vB=theta corner, vC=top',
        1
    )

    # Replace gen_isosceles_split
    old_start = "def gen_isosceles_split():"
    old_end   = "        diagram_svg=svg_q,solution_svg=svg_s)"
    # Find the function boundaries
    i = code.find(old_start)
    j = code.find(old_end, i) + len(old_end)
    assert i >= 0 and j > i, "gen_isosceles_split not found"
    code = code[:i] + NEW_GEN_ISOSCELES_SPLIT.strip() + code[j:]

    with open(path, "w") as f:
        f.write(code)
    print(f"Patched {path} successfully.")
    print("  + string import added")
    print("  + gen_label_sides: random.sample")
    print("  + gen_isosceles_split: consistent vertices, correct angle_values")
