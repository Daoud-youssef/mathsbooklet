"""
Mensuration.py
==============
Single source of truth for ALL Unit 3 Mensuration exercises.
Follows the exact same architecture as Indices.py.
"""

import math
import random
import json
from datetime import date

# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

PART_LABELS = list("abcdefghijklmnopqrstuvwxyz")
ri = random.randint

def _fmt_num(x):
    if isinstance(x, float) and x == int(x):
        x = int(x)
    if isinstance(x, int):
        return f"{x:,}".replace(",", "{,}") if x >= 10_000 else str(x)
    return str(round(x, 6)).rstrip("0").rstrip(".")

def _u(unit):
    """Render a unit string as valid LaTeX. e.g. 'cm^2' → '\\text{cm}^2'"""
    if "^" in unit:
        base, exp = unit.split("^", 1)
        return f"\\text{{{base}}}^{{{exp}}}"
    return f"\\text{{{unit}}}"

def _part(question_latex, answer_latex, solution_latex,
          answer_plain="", is_word=False, is_wide=False):
    return {
        "question_latex": question_latex,
        "answer_latex":   answer_latex,
        "answer":         answer_plain or answer_latex,
        "solution_latex": solution_latex,
        "is_word":        is_word,
        "is_wide":        is_wide,
    }

# ══════════════════════════════════════════════════════════════════
# SVG DRAWING ENGINE
# Volume exercises: svg attached per PART (actual numbers)
# SA exercises:     svg attached per EXERCISE (letter labels)
# ══════════════════════════════════════════════════════════════════

def _svg_wrap(content, vw, vh):
    return (f'<svg width="{int(vw)}" height="{int(vh)}" '
            f'viewBox="0 0 {int(vw)} {int(vh)}" '
            f'style="display:block;margin:8px auto;font-family:serif;" '
            f'xmlns="http://www.w3.org/2000/svg">{content}</svg>')

def _lbl(x, y, text, color="black", size=12, anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-family="serif" font-style="italic">{text}</text>')

def _arrow(x1, y1, x2, y2, color="#333", dash=""):
    dash_attr = f'stroke-dasharray="{dash}"' if dash else ""
    mid_x = (x1+x2)/2; mid_y = (y1+y2)/2
    dx = x2-x1; dy = y2-y1; L = math.sqrt(dx*dx+dy*dy) or 1
    ux = dx/L; uy = dy/L; s = 6
    a1x = x2-s*ux+s*0.4*uy; a1y = y2-s*uy-s*0.4*ux
    a2x = x2-s*ux-s*0.4*uy; a2y = y2-s*uy+s*0.4*ux
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="1.5" {dash_attr}/>'
            f'<polygon points="{x2:.1f},{y2:.1f} {a1x:.1f},{a1y:.1f} {a2x:.1f},{a2y:.1f}" '
            f'fill="{color}"/>')

# ─── 3D ISOMETRIC CUBOID ──────────────────────────────────────────
def svg_rect_prism(l, w, h, lbl_l=None, lbl_w=None, lbl_h=None):
    lbl_l = lbl_l if lbl_l is not None else str(l)
    lbl_w = lbl_w if lbl_w is not None else str(w)
    lbl_h = lbl_h if lbl_h is not None else str(h)
    S = 13; Lp = min(l,10)*S; Wp = min(w,8)*S; Hp = min(h,8)*S
    ox = Wp*0.5; oy = Wp*0.35; pad = 32
    vw = Lp+ox+pad*2; vh = Hp+oy+pad*2
    x0 = pad; y0 = pad+oy
    # three faces
    front  = (f'<polygon points="{x0},{y0} {x0+Lp},{y0} {x0+Lp},{y0+Hp} {x0},{y0+Hp}" '
              f'fill="#ddeeff" stroke="#2255aa" stroke-width="1.5"/>')
    top    = (f'<polygon points="{x0},{y0} {x0+ox},{y0-oy} {x0+Lp+ox},{y0-oy} {x0+Lp},{y0}" '
              f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    right  = (f'<polygon points="{x0+Lp},{y0} {x0+Lp+ox},{y0-oy} '
              f'{x0+Lp+ox},{y0+Hp-oy} {x0+Lp},{y0+Hp}" '
              f'fill="#99ccee" stroke="#2255aa" stroke-width="1.5"/>')
    # dashed hidden edges
    dash = (f'<line x1="{x0}" y1="{y0+Hp}" x2="{x0+ox}" y2="{y0+Hp-oy}" '
            f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>'
            f'<line x1="{x0+ox}" y1="{y0-oy}" x2="{x0+ox}" y2="{y0+Hp-oy}" '
            f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>'
            f'<line x1="{x0+ox}" y1="{y0+Hp-oy}" x2="{x0+Lp+ox}" y2="{y0+Hp-oy}" '
            f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # labels
    lb_l = _lbl(x0+Lp/2, y0+Hp+16, lbl_l, "#c0392b", 12)
    lb_h = _lbl(x0-14,   y0+Hp/2,  lbl_h, "#27ae60", 12, "end")
    lb_w = _lbl(x0+Lp+ox/2+10, y0-oy/2-5, lbl_w, "#8e44ad", 11)
    return _svg_wrap(front+top+right+dash+lb_l+lb_h+lb_w, vw, vh)

# ─── 3D TRIANGULAR PRISM (right-angled cross-section, isometric) ──
def svg_triangular_prism(b, ht, l, lbl_b=None, lbl_h=None, lbl_l=None,
                         lbl_s1=None, lbl_s2=None):
    lbl_b = lbl_b or str(b); lbl_h = lbl_h or str(ht); lbl_l = lbl_l or str(l)
    S = 13; Bp = min(b,9)*S; Hp = min(ht,8)*S; Lp = min(l,10)*S
    ox = Lp*0.45; oy = Lp*0.3; pad = 38
    vw = Bp+ox+pad*2; vh = Hp+oy+pad*2
    x0 = pad; y0 = pad+oy
    # Front right-angled triangle: bottom-left, bottom-right, top-left
    f0x,f0y = x0,       y0+Hp
    f1x,f1y = x0+Bp,    y0+Hp
    f2x,f2y = x0,       y0
    # Back triangle
    b0x,b0y = f0x+ox, f0y-oy
    b1x,b1y = f1x+ox, f1y-oy
    b2x,b2y = f2x+ox, f2y-oy
    # Faces
    front  = (f'<polygon points="{f0x},{f0y} {f1x},{f1y} {f2x},{f2y}" '
              f'fill="#e8f5e9" stroke="#27ae60" stroke-width="1.5"/>')
    back_d = (f'<polygon points="{b0x},{b0y} {b1x},{b1y} {b2x},{b2y}" '
              f'fill="#c8e6c9" stroke="#27ae60" stroke-width="1" stroke-dasharray="4"/>')
    # Bottom rectangle (f0→f1→b1→b0)
    bot = (f'<polygon points="{f0x},{f0y} {f1x},{f1y} {b1x},{b1y} {b0x},{b0y}" '
           f'fill="#ddf5dd" stroke="#27ae60" stroke-width="1.5"/>')
    # Top-left rectangle (f0→f2→b2→b0)
    side= (f'<polygon points="{f0x},{f0y} {f2x},{f2y} {b2x},{b2y} {b0x},{b0y}" '
           f'fill="#b8e0b8" stroke="#27ae60" stroke-width="1.5"/>')
    # Slant rect (f1→f2→b2→b1)
    slant=(f'<polygon points="{f1x},{f1y} {f2x},{f2y} {b2x},{b2y} {b1x},{b1y}" '
           f'fill="#a0d4a0" stroke="#27ae60" stroke-width="1.5"/>')
    # Right-angle mark on front face
    rm = (f'<polyline points="{f0x+8},{f0y} {f0x+8},{f0y-8} {f0x},{f0y-8}" '
          f'fill="none" stroke="#27ae60" stroke-width="1"/>')
    lb_b = _lbl((f0x+f1x)/2, f0y+16, lbl_b, "#c0392b", 12)
    lb_h = _lbl(f0x-14,      (f0y+f2y)/2, lbl_h, "#27ae60", 12, "end")
    lb_l = _lbl((f1x+b1x)/2+12, (f1y+b1y)/2, lbl_l, "#8e44ad", 11)
    return _svg_wrap(back_d+bot+side+slant+front+rm+lb_b+lb_h+lb_l, vw, vh)

# ─── 3D TRAPEZOIDAL PRISM ─────────────────────────────────────────
def svg_trapezoidal_prism(a, b, ht, l, lbl_a=None, lbl_b=None,
                          lbl_h=None, lbl_l=None):
    lbl_a=lbl_a or str(a); lbl_b=lbl_b or str(b)
    lbl_h=lbl_h or str(ht); lbl_l=lbl_l or str(l)
    S=13; Ap=min(a,6)*S; Bp=min(b,9)*S; Hp=min(ht,7)*S; Lp=min(l,10)*S
    off=(Bp-Ap)/2; ox=Lp*0.45; oy=Lp*0.3; pad=38
    vw=Bp+ox+pad*2; vh=Hp+oy+pad*2
    x0=pad; y0=pad+oy
    # Front trapezoid corners
    f=[(x0,y0+Hp),(x0+Bp,y0+Hp),(x0+Bp-off,y0),(x0+off,y0)]
    # Back trapezoid corners
    bk=[(fx+ox,fy-oy) for fx,fy in f]
    def poly(pts,fill,stroke,sw=1.5,dash=""):
        s=f'stroke-dasharray="{dash}"' if dash else ""
        return (f'<polygon points="{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {s}/>')
    back_d = poly(bk,"#ffe0b2","#e67e22",1,"4")
    # Connecting faces
    bot  = poly([f[0],f[1],bk[1],bk[0]],"#fff3e0","#e67e22")
    right= poly([f[1],f[2],bk[2],bk[1]],"#ffd8a0","#e67e22")
    top_ = poly([f[2],f[3],bk[3],bk[2]],"#ffe5b4","#e67e22")
    front= poly(f,"#fff8e1","#e67e22")
    lb_b = _lbl((f[0][0]+f[1][0])/2, f[0][1]+16, lbl_b,"#c0392b",12)
    lb_a = _lbl((f[2][0]+f[3][0])/2, f[2][1]-13, lbl_a,"#2980b9",12)
    lb_h = _lbl(f[0][0]-14, (f[0][1]+f[2][1])/2, lbl_h,"#27ae60",12,"end")
    lb_l = _lbl((f[1][0]+bk[1][0])/2+12,(f[1][1]+bk[1][1])/2, lbl_l,"#8e44ad",11)
    return _svg_wrap(back_d+bot+right+top_+front+lb_b+lb_a+lb_h+lb_l, vw, vh)

# ─── 3D PARALLELOGRAM PRISM ───────────────────────────────────────
def svg_parallelogram_prism(b, ht, l, lbl_b=None, lbl_h=None, lbl_l=None):
    lbl_b=lbl_b or str(b); lbl_h=lbl_h or str(ht); lbl_l=lbl_l or str(l)
    S=13; Bp=min(b,9)*S; Hp=min(ht,7)*S; Lp=min(l,10)*S
    sk=Hp*0.4; ox=Lp*0.45; oy=Lp*0.3; pad=38
    vw=Bp+sk+ox+pad*2; vh=Hp+oy+pad*2
    x0=pad; y0=pad+oy
    f=[(x0+sk,y0),(x0+sk+Bp,y0),(x0+Bp,y0+Hp),(x0,y0+Hp)]
    bk=[(fx+ox,fy-oy) for fx,fy in f]
    def poly(pts,fill,stroke,sw=1.5,dash=""):
        s=f'stroke-dasharray="{dash}"' if dash else ""
        return (f'<polygon points="{" ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {s}/>')
    back_d=poly(bk,"#e1bee7","#8e44ad",1,"4")
    bot=poly([f[2],f[3],bk[3],bk[2]],"#f3e5f5","#8e44ad")
    top_=poly([f[0],f[1],bk[1],bk[0]],"#e8d5f5","#8e44ad")
    side=poly([f[1],f[2],bk[2],bk[1]],"#d5b8e8","#8e44ad")
    front=poly(f,"#f8eeff","#8e44ad")
    lb_b=_lbl((f[2][0]+f[3][0])/2,f[3][1]+16,lbl_b,"#c0392b",12)
    lb_h=_lbl(f[3][0]-14,(f[0][1]+f[3][1])/2,lbl_h,"#27ae60",12,"end")
    lb_l=_lbl((f[2][0]+bk[2][0])/2+12,(f[2][1]+bk[2][1])/2,lbl_l,"#8e44ad",11)
    return _svg_wrap(back_d+bot+top_+side+front+lb_b+lb_h+lb_l, vw, vh)

# ─── UPRIGHT CYLINDER (proper body fill) ─────────────────────────
def svg_cylinder(r, h, show_radius=True, lbl_r=None, lbl_h=None):
    rv = lbl_r if lbl_r is not None else str(r)
    hv = lbl_h if lbl_h is not None else str(h)
    S=14; R=min(r,8)*S; H=min(h,11)*S; ry=R*0.28; pad=36
    vw=R*2+pad*2; vh=H+ry*2+pad*2
    cx=vw/2; top_cy=pad+ry; bot_cy=top_cy+H
    # Body fill (rectangle between sides)
    body_fill=(f'<rect x="{cx-R:.1f}" y="{top_cy:.1f}" width="{R*2:.1f}" height="{H:.1f}" '
               f'fill="#ddeeff" stroke="none"/>')
    # Bottom ellipse halves
    bot_vis =(f'<path d="M {cx-R:.1f},{bot_cy:.1f} A {R:.1f},{ry:.1f} 0 0 0 {cx+R:.1f},{bot_cy:.1f}" '
              f'fill="none" stroke="#2255aa" stroke-width="1.5"/>')
    bot_dash=(f'<path d="M {cx-R:.1f},{bot_cy:.1f} A {R:.1f},{ry:.1f} 0 0 1 {cx+R:.1f},{bot_cy:.1f}" '
              f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Sides
    sides=(f'<line x1="{cx-R:.1f}" y1="{top_cy:.1f}" x2="{cx-R:.1f}" y2="{bot_cy:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>'
           f'<line x1="{cx+R:.1f}" y1="{top_cy:.1f}" x2="{cx+R:.1f}" y2="{bot_cy:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>')
    # Top ellipse
    top_el=(f'<ellipse cx="{cx:.1f}" cy="{top_cy:.1f}" rx="{R:.1f}" ry="{ry:.1f}" '
            f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    # Dimension line
    if show_radius:
        dim=(f'<line x1="{cx:.1f}" y1="{top_cy:.1f}" x2="{cx+R:.1f}" y2="{top_cy:.1f}" '
             f'stroke="#c0392b" stroke-width="1.5"/>')
        lb_r=_lbl(cx+R/2, top_cy-14, rv, "#c0392b",12)
    else:
        dim=(f'<line x1="{cx-R:.1f}" y1="{top_cy:.1f}" x2="{cx+R:.1f}" y2="{top_cy:.1f}" '
             f'stroke="#c0392b" stroke-width="1.5" stroke-dasharray="5"/>')
        lb_r=_lbl(cx, top_cy-14, rv, "#c0392b",12)
    lb_h=_lbl(cx+R+20, top_cy+H/2, hv, "#27ae60",12)
    return _svg_wrap(body_fill+bot_vis+bot_dash+sides+top_el+dim+lb_r+lb_h, vw, vh)

# ─── HALF-CYLINDER (proper 3D bowl shape) ────────────────────────
def svg_half_cylinder(r, h, lbl_r=None, lbl_h=None):
    rv=lbl_r or str(r); hv=lbl_h or str(h)
    S=14; R=min(r,8)*S; H=min(h,11)*S; ry=R*0.3; pad=36
    vw=R*2+pad*2; vh=H+R+ry+pad*2
    cx=vw/2; flat_y=pad+R; bot_y=flat_y+H
    # Flat rectangular face (bottom)
    rect=(f'<rect x="{cx-R:.1f}" y="{flat_y:.1f}" width="{R*2:.1f}" height="{H:.1f}" '
          f'fill="#ddeeff" stroke="#2255aa" stroke-width="1.5"/>')
    # Back dashed semi-ellipse
    back=(f'<path d="M {cx-R:.1f},{bot_y:.1f} A {R:.1f},{ry:.1f} 0 0 1 {cx+R:.1f},{bot_y:.1f}" '
          f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Front semi-ellipse at bottom
    front_bot=(f'<path d="M {cx-R:.1f},{bot_y:.1f} A {R:.1f},{ry:.1f} 0 0 0 {cx+R:.1f},{bot_y:.1f}" '
               f'fill="none" stroke="#2255aa" stroke-width="1.5"/>')
    # Front curved top half (semi-circle facing front)
    semi=(f'<path d="M {cx-R:.1f},{flat_y:.1f} A {R:.1f},{R:.1f} 0 0 1 {cx+R:.1f},{flat_y:.1f}" '
          f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    # Flat diameter line at top
    diam=(f'<line x1="{cx-R:.1f}" y1="{flat_y:.1f}" x2="{cx+R:.1f}" y2="{flat_y:.1f}" '
          f'stroke="#2255aa" stroke-width="1.5"/>')
    lb_r=_lbl(cx+R/2, flat_y-R/2-8, rv, "#c0392b",12)
    lb_h=_lbl(cx+R+20, flat_y+H/2,  hv, "#27ae60",12)
    return _svg_wrap(rect+back+front_bot+semi+diam+lb_r+lb_h, vw, vh)

# ─── QUARTER-CYLINDER ─────────────────────────────────────────────
def svg_quarter_cylinder(r, h, lbl_r=None, lbl_h=None):
    rv=lbl_r or str(r); hv=lbl_h or str(h)
    S=14; R=min(r,8)*S; H=min(h,11)*S; pad=38
    vw=R+pad*2+20; vh=H+R+pad*2
    x0=pad; y0=pad+R
    # Front quarter circle
    qf=(f'<path d="M {x0},{y0} L {x0+R},{y0} A {R},{R} 0 0 1 {x0},{y0-R} Z" '
        f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    # Back quarter (dashed)
    qb=(f'<path d="M {x0},{y0+H} L {x0+R},{y0+H} A {R},{R} 0 0 1 {x0},{y0+H-R}" '
        f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Rectangular flat faces
    flat1=(f'<polygon points="{x0},{y0} {x0+R},{y0} {x0+R},{y0+H} {x0},{y0+H}" '
           f'fill="#ddeeff" stroke="#2255aa" stroke-width="1.5"/>')
    flat2=(f'<polygon points="{x0},{y0} {x0},{y0-R} {x0},{y0-R+H} {x0},{y0+H}" '
           f'fill="#ddeeff" stroke="#2255aa" stroke-width="1"/>')
    # Vertical edge at apex of curve
    ve=(f'<line x1="{x0}" y1="{y0-R}" x2="{x0}" y2="{y0-R+H}" '
        f'stroke="#2255aa" stroke-width="1.5"/>')
    lb_r=_lbl(x0+R/2, y0+14, rv, "#c0392b",12)
    lb_h=_lbl(x0+R+16, y0+H/2, hv, "#27ae60",12)
    return _svg_wrap(flat1+flat2+qb+ve+qf+lb_r+lb_h, vw, vh)

# ─── SECTOR CYLINDER ──────────────────────────────────────────────
def svg_sector_cylinder(r, h, theta, lbl_r=None, lbl_h=None, lbl_t=None):
    rv=lbl_r or str(r); hv=lbl_h or str(h)
    tv=lbl_t or f"{theta}°"
    S=14; R=min(r,8)*S; H=min(h,11)*S; pad=42
    vw=R*2+pad*2; vh=H+R*2+pad*2
    cx=vw/2; cy_top=pad+R; cy_bot=cy_top+H
    t=math.radians(theta)
    x1=cx+R; y1=cy_top
    x2=cx+R*math.cos(t); y2=cy_top-R*math.sin(t)
    lg=1 if theta>180 else 0
    # Top sector
    top_s=(f'<path d="M {cx:.1f},{cy_top:.1f} L {x1:.1f},{y1:.1f} '
           f'A {R:.1f},{R:.1f} 0 {lg},0 {x2:.1f},{y2:.1f} Z" '
           f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    # Bottom sector (dashed)
    y1b=cy_bot; y2b=cy_bot-R*math.sin(t)
    bot_s=(f'<path d="M {cx:.1f},{cy_bot:.1f} L {x1:.1f},{y1b:.1f} '
           f'A {R:.1f},{R:.1f} 0 {lg},0 {x2:.1f},{y2b:.1f} Z" '
           f'fill="#99ccee" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Curved side face (rectangle bent — approx with polygon)
    edges=(f'<line x1="{cx:.1f}" y1="{cy_top:.1f}" x2="{cx:.1f}" y2="{cy_bot:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>'
           f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" y2="{y1b:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>'
           f'<line x1="{x2:.1f}" y1="{y2:.1f}" x2="{x2:.1f}" y2="{y2b:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>')
    lb_r=_lbl(cx+R/2, cy_top+14, rv, "#c0392b",12)
    lb_t=_lbl(cx+12,  cy_top-14, tv, "#8e44ad",12)
    lb_h=_lbl(cx+R+20, cy_top+H/2, hv, "#27ae60",12)
    return _svg_wrap(bot_s+edges+top_s+lb_r+lb_t+lb_h, vw, vh)

# ─── RECTANGULAR PYRAMID ──────────────────────────────────────────
def svg_pyramid_rect(l, w, h, lbl_l=None, lbl_w=None, lbl_h=None):
    lbl_l=lbl_l or str(l); lbl_w=lbl_w or str(w); lbl_h=lbl_h or str(h)
    S=13; Lp=min(l,9)*S; Wp=min(w,7)*S; Hp=min(h,10)*S
    ox=Wp*0.5; oy=Wp*0.35; pad=42
    vw=Lp+ox+pad*2; vh=Hp+oy+pad*2
    # Base corners
    b0=(pad,          pad+oy+Hp)
    b1=(pad+Lp,       pad+oy+Hp)
    b2=(pad+Lp+ox,    pad+Hp)
    b3=(pad+ox,       pad+Hp)
    apex=(pad+Lp/2+ox/2, pad)
    def li(p,q,dash=""):
        da=f'stroke-dasharray="{dash}"' if dash else ""
        return (f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
                f'stroke="#c8860a" stroke-width="1.5" {da}/>')
    base=(f'<polygon points="{b0[0]},{b0[1]} {b1[0]},{b1[1]} {b2[0]},{b2[1]} {b3[0]},{b3[1]}" '
          f'fill="#fff9c4" stroke="#c8860a" stroke-width="1.5"/>')
    e1=li(b0,apex); e2=li(b1,apex); e3=li(b2,apex)
    e4=li(b3,apex,"4")
    # Base hidden edges
    hid=li(b0,b3,"4")+li(b3,b2,"4")
    # Height indicator
    mid_base=((b0[0]+b2[0])/2,(b0[1]+b2[1])/2)
    hl=(f'<line x1="{apex[0]:.1f}" y1="{apex[1]:.1f}" x2="{apex[0]:.1f}" y2="{mid_base[1]:.1f}" '
        f'stroke="#27ae60" stroke-width="1" stroke-dasharray="3"/>')
    lb_l=_lbl((b0[0]+b1[0])/2, b0[1]+16, lbl_l, "#c0392b",12)
    lb_w=_lbl((b2[0]+b3[0])/2+14,(b2[1]+b3[1])/2, lbl_w, "#8e44ad",11)
    lb_h=_lbl(apex[0]+14,(apex[1]+mid_base[1])/2, lbl_h, "#27ae60",12)
    return _svg_wrap(base+hid+e1+e2+e3+e4+hl+lb_l+lb_w+lb_h, vw, vh)

def svg_pyramid_square(s, h, lbl_s=None, lbl_h=None):
    return svg_pyramid_rect(s, s, h, lbl_l=lbl_s or str(s),
                            lbl_w=lbl_s or str(s), lbl_h=lbl_h or str(h))

# ─── CONE ─────────────────────────────────────────────────────────
def svg_cone(r, h, show_slant=False, lbl_r=None, lbl_h=None, lbl_sl=None):
    rv=lbl_r or str(r); hv=lbl_h or str(h)
    S=14; R=min(r,7)*S; H=min(h,11)*S; ry=R*0.28; pad=42
    vw=R*2+pad*2; vh=H+ry*2+pad*2
    cx=vw/2; bot_cy=pad+H+ry; top_y=pad
    # Base ellipse
    bot_el=(f'<ellipse cx="{cx:.1f}" cy="{bot_cy:.1f}" rx="{R:.1f}" ry="{ry:.1f}" '
            f'fill="#ffe0b2" stroke="#c85000" stroke-width="1.5"/>')
    # Slant sides
    sl=(f'<line x1="{cx-R:.1f}" y1="{bot_cy:.1f}" x2="{cx:.1f}" y2="{top_y:.1f}" '
        f'stroke="#c85000" stroke-width="1.5"/>'
        f'<line x1="{cx+R:.1f}" y1="{bot_cy:.1f}" x2="{cx:.1f}" y2="{top_y:.1f}" '
        f'stroke="#c85000" stroke-width="1.5"/>')
    # Height line (dashed)
    hl=(f'<line x1="{cx:.1f}" y1="{top_y:.1f}" x2="{cx:.1f}" y2="{bot_cy:.1f}" '
        f'stroke="#27ae60" stroke-width="1" stroke-dasharray="3"/>')
    # Radius
    rl=(f'<line x1="{cx:.1f}" y1="{bot_cy:.1f}" x2="{cx+R:.1f}" y2="{bot_cy:.1f}" '
        f'stroke="#c0392b" stroke-width="1.5" stroke-dasharray="4"/>')
    lb_r=_lbl(cx+R/2, bot_cy+14, rv, "#c0392b",12)
    lb_h=_lbl(cx+10,  top_y+H/2, hv, "#27ae60",12)
    extra=""
    if show_slant:
        slv=lbl_sl or ""
        slant_line=(f'<line x1="{cx+R:.1f}" y1="{bot_cy:.1f}" x2="{cx:.1f}" y2="{top_y:.1f}" '
                    f'stroke="#e74c3c" stroke-width="2" stroke-dasharray="6"/>')
        lb_sl=_lbl(cx+R/2+16, (bot_cy+top_y)/2, slv, "#e74c3c",12)
        extra=slant_line+lb_sl
    return _svg_wrap(sl+hl+rl+extra+bot_el+lb_r+lb_h, vw, vh)

# ─── SPHERE ───────────────────────────────────────────────────────
def svg_sphere(r, show_diameter=False, lbl_r=None):
    rv=lbl_r if lbl_r is not None else str(r if not show_diameter else r*2)
    S=14; R=min(r,8)*S; pad=30
    vw=vh=R*2+pad*2; cx=cy=vw/2
    circle=(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" '
            f'fill="#fce4ec" stroke="#c0392b" stroke-width="1.5"/>')
    # Equator (dashed ellipse)
    eq=(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{R:.1f}" ry="{R*0.28:.1f}" '
        f'fill="none" stroke="#c0392b" stroke-width="1" stroke-dasharray="5"/>')
    if show_diameter:
        dl=(f'<line x1="{cx-R:.1f}" y1="{cy:.1f}" x2="{cx+R:.1f}" y2="{cy:.1f}" '
            f'stroke="#c0392b" stroke-width="1.5" stroke-dasharray="5"/>')
        arr=(_arrow(cx-R,cy,cx+R,cy,"#c0392b","5"))
        lb_r=_lbl(cx, cy-14, rv, "#c0392b",12)
        return _svg_wrap(circle+eq+arr+lb_r, vw, vh)
    else:
        rl=(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx+R:.1f}" y2="{cy:.1f}" '
            f'stroke="#c0392b" stroke-width="1.5"/>')
        lb_r=_lbl(cx+R/2, cy-14, rv, "#c0392b",12)
        return _svg_wrap(circle+eq+rl+lb_r, vw, vh)

# ─── HEMISPHERE ───────────────────────────────────────────────────
def svg_hemisphere(r, lbl_r=None):
    rv=lbl_r or str(r)
    S=14; R=min(r,8)*S; ry=R*0.32; pad=32
    vw=R*2+pad*2; vh=R+ry+pad*2+10
    cx=vw/2; cy=pad+R
    # Bowl arc (upper hemisphere)
    arc=(f'<path d="M {cx-R:.1f},{cy:.1f} A {R:.1f},{R:.1f} 0 0 1 {cx+R:.1f},{cy:.1f}" '
         f'fill="#fce4ec" stroke="#c0392b" stroke-width="1.5"/>')
    # Flat rim ellipse
    el=(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{R:.1f}" ry="{ry:.1f}" '
        f'fill="#f8bbd0" stroke="#c0392b" stroke-width="1.5"/>')
    # Radius arrow
    rl=_arrow(cx, cy, cx+R, cy, "#c0392b","5")
    lb_r=_lbl(cx+R/2, cy-14, rv, "#c0392b",12)
    return _svg_wrap(arc+el+rl+lb_r, vw, vh)

# ─── 3D L-SHAPED PRISM (two joined isometric cuboids) ─────────────
def svg_l_prism(a1, b1, a2, b2, l,
                lbl_a1=None,lbl_b1=None,lbl_a2=None,lbl_b2=None,lbl_l=None):
    la1=lbl_a1 or str(a1); lb_1=lbl_b1 or str(b1)
    la2=lbl_a2 or str(a2); lb_2=lbl_b2 or str(b2)
    ll=lbl_l   or str(l)
    S=12
    A1p=min(a1,10)*S; B1p=min(b1,8)*S
    A2p=min(a2,8)*S;  B2p=min(b2,6)*S
    Lp=min(l,10)*S
    ox=Lp*0.45; oy=Lp*0.3; pad=40
    # Total canvas
    vw=A1p+ox+pad*2; vh=B1p+oy+pad*2+20
    # Bottom-front-left anchor
    x0=pad; y0=pad+oy

    def cube(fx,fy,W,H,fill_f,fill_t,fill_r):
        # Front face
        f=(f'<polygon points="{fx},{fy} {fx+W},{fy} {fx+W},{fy+H} {fx},{fy+H}" '
           f'fill="{fill_f}" stroke="#2255aa" stroke-width="1.5"/>')
        # Top face
        t=(f'<polygon points="{fx},{fy} {fx+ox},{fy-oy} {fx+W+ox},{fy-oy} {fx+W},{fy}" '
           f'fill="{fill_t}" stroke="#2255aa" stroke-width="1.5"/>')
        # Right face
        r=(f'<polygon points="{fx+W},{fy} {fx+W+ox},{fy-oy} {fx+W+ox},{fy+H-oy} {fx+W},{fy+H}" '
           f'fill="{fill_r}" stroke="#2255aa" stroke-width="1.5"/>')
        return f+t+r

    # Tall left block
    tall=cube(x0, y0, A1p, B1p, "#ddeeff","#bbddff","#99ccee")
    # Short right block sitting at the bottom (flush bottom)
    short_y = y0 + (B1p - B2p)  # aligned at bottom
    short=cube(x0+A1p, short_y, A2p, B2p, "#cceedd","#aaeecc","#88ddbb")

    # Dashed hidden edges for tall block
    dash=(f'<line x1="{x0}" y1="{y0+B1p}" x2="{x0+ox}" y2="{y0+B1p-oy}" '
          f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>'
          f'<line x1="{x0+ox}" y1="{y0-oy}" x2="{x0+ox}" y2="{y0+B1p-oy}" '
          f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>'
          f'<line x1="{x0+ox}" y1="{y0+B1p-oy}" x2="{x0+A1p+ox}" y2="{y0+B1p-oy}" '
          f'stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')

    # Labels
    lb_a1=_lbl(x0+A1p/2, y0+B1p+16, la1, "#c0392b",12)
    lb_b1=_lbl(x0-14, y0+B1p/2, lb_1, "#27ae60",12,"end")
    lb_a2=_lbl(x0+A1p+A2p/2, short_y+B2p+16, la2, "#c0392b",11)
    lb_b2=_lbl(x0+A1p+A2p+ox/2+14, short_y+(B2p-oy)/2, lb_2, "#27ae60",11)
    lb_l =_lbl(x0+A1p+ox/2+12, y0-oy/2-6, ll, "#8e44ad",11)

    return _svg_wrap(tall+short+dash+lb_a1+lb_b1+lb_a2+lb_b2+lb_l, vw, vh)

# ─── COMPOSITE: PRISM + HALF-CYLINDER (house) ────────────────────
def svg_house_prism(l, w, h, r, lbl_l=None, lbl_w=None, lbl_h=None, lbl_r=None):
    ll=lbl_l or str(l); lw=lbl_w or str(w)
    lh=lbl_h or str(h); lr=lbl_r or str(r)
    S=12; Lp=min(l,10)*S; Wp=min(w,8)*S; Hp=min(h,7)*S
    Rp=Wp/2  # half-cylinder radius = half width
    ox=Wp*0.45; oy=Wp*0.32; pad=40
    vw=Lp+ox+pad*2; vh=Hp+Rp+oy+pad*2

    x0=pad; y0=pad+oy+Rp   # front-face top-left of rect section

    # ── Rectangular prism (3 faces) ──────────────────────────────
    front_rect=(f'<polygon points="{x0},{y0} {x0+Lp},{y0} {x0+Lp},{y0+Hp} {x0},{y0+Hp}" '
                f'fill="#ddeeff" stroke="#2255aa" stroke-width="1.5"/>')
    top_rect  =(f'<polygon points="{x0},{y0} {x0+ox},{y0-oy} {x0+Lp+ox},{y0-oy} {x0+Lp},{y0}" '
                f'fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    right_rect=(f'<polygon points="{x0+Lp},{y0} {x0+Lp+ox},{y0-oy} '
                f'{x0+Lp+ox},{y0+Hp-oy} {x0+Lp},{y0+Hp}" '
                f'fill="#99ccee" stroke="#2255aa" stroke-width="1.5"/>')

    # ── Half-cylinder roof ────────────────────────────────────────
    # Front semi-circle sits on top of rect front face
    cx_f = x0 + Lp/2; cy_f = y0
    front_arc=(f'<path d="M {x0},{cy_f} A {Lp/2},{Rp} 0 0 1 {x0+Lp},{cy_f} Z" '
               f'fill="#c8e6f5" stroke="#2255aa" stroke-width="1.5"/>')
    # Back semi-circle (offset, dashed)
    cx_b = cx_f+ox; cy_b = cy_f-oy
    back_arc=(f'<path d="M {x0+ox},{cy_b} A {Lp/2},{Rp} 0 0 1 {x0+Lp+ox},{cy_b}" '
              f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Ridge line at top (front apex to back apex)
    ridge=(f'<line x1="{cx_f:.1f}" y1="{cy_f-Rp:.1f}" x2="{cx_b:.1f}" y2="{cy_b-Rp:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>')
    # Curved surface sides connecting front arc top to back arc top
    side_l=(f'<line x1="{x0:.1f}" y1="{cy_f:.1f}" x2="{x0+ox:.1f}" y2="{cy_b:.1f}" '
            f'stroke="#2255aa" stroke-width="1.5"/>')
    side_r=(f'<line x1="{x0+Lp:.1f}" y1="{cy_f:.1f}" x2="{x0+Lp+ox:.1f}" y2="{cy_b:.1f}" '
            f'stroke="#2255aa" stroke-width="1.5"/>')

    # Labels
    lb_l=_lbl(x0+Lp/2,    y0+Hp+16, ll, "#c0392b", 12)
    lb_w=_lbl(x0-14,       y0+Hp/2,  lw, "#8e44ad", 12, "end")
    lb_h=_lbl(x0+Lp+ox+16, y0+Hp/2,  lh, "#27ae60", 12)
    lb_r=_lbl(cx_f+Lp/4,   cy_f-Rp/2, lr, "#c0392b", 11)

    return _svg_wrap(
        front_rect+top_rect+right_rect+back_arc+side_l+side_r+ridge+front_arc+lb_l+lb_w+lb_h+lb_r,
        vw, vh
    )

# ─── COMPOSITE: CONE + HEMISPHERE ────────────────────────────────
def svg_cone_hemisphere(r, h_cone, lbl_r=None, lbl_h=None):
    rv=lbl_r or str(r); hv=lbl_h or str(h_cone)
    S=13; R=min(r,7)*S; Hc=min(h_cone,9)*S; ry=R*0.28; pad=36
    vw=R*2+pad*2; vh=Hc+R+ry+pad*2
    cx=vw/2; hemi_cy=pad+Hc+R; apex_y=pad
    # Hemisphere bowl
    hemi=(f'<path d="M {cx-R:.1f},{hemi_cy:.1f} A {R:.1f},{R:.1f} 0 0 0 {cx+R:.1f},{hemi_cy:.1f} Z" '
          f'fill="#fce4ec" stroke="#c0392b" stroke-width="1.5"/>')
    hemi_el=(f'<ellipse cx="{cx:.1f}" cy="{hemi_cy:.1f}" rx="{R:.1f}" ry="{ry:.1f}" '
             f'fill="#f8bbd0" stroke="#c0392b" stroke-width="1.5"/>')
    # Cone above
    cone_sl=(f'<line x1="{cx-R:.1f}" y1="{hemi_cy:.1f}" x2="{cx:.1f}" y2="{apex_y:.1f}" '
             f'stroke="#e67e22" stroke-width="1.5"/>'
             f'<line x1="{cx+R:.1f}" y1="{hemi_cy:.1f}" x2="{cx:.1f}" y2="{apex_y:.1f}" '
             f'stroke="#e67e22" stroke-width="1.5"/>')
    hl=(f'<line x1="{cx:.1f}" y1="{apex_y:.1f}" x2="{cx:.1f}" y2="{hemi_cy:.1f}" '
        f'stroke="#27ae60" stroke-width="1" stroke-dasharray="3"/>')
    lb_r=_lbl(cx+R/2, hemi_cy+16, rv, "#c0392b",12)
    lb_h=_lbl(cx+12,  apex_y+Hc/2, hv, "#27ae60",12)
    return _svg_wrap(hemi_el+hemi+cone_sl+hl+lb_r+lb_h, vw, vh)

# ─── CYLINDER + CONE (upright, cone on top like image 16) ─────────
def svg_cylinder_cone(r, h_cyl, h_cone, lbl_r=None, lbl_hc=None, lbl_hcone=None):
    rv=lbl_r or str(r); hcv=lbl_hc or str(h_cyl); hconv=lbl_hcone or str(h_cone)
    S=13; R=min(r,7)*S; Hcy=min(h_cyl,10)*S; Hco=min(h_cone,8)*S
    ry=R*0.28; pad=40
    vw=R*2+pad*2; vh=Hcy+Hco+ry*2+pad*2
    cx=vw/2
    cyl_top=pad+Hco; cyl_bot=cyl_top+Hcy
    cone_apex=pad
    # Cylinder body
    body_fill=(f'<rect x="{cx-R:.1f}" y="{cyl_top:.1f}" width="{R*2:.1f}" height="{Hcy:.1f}" '
               f'fill="#ddeeff" stroke="none"/>')
    bot_vis=(f'<path d="M {cx-R:.1f},{cyl_bot:.1f} A {R:.1f},{ry:.1f} 0 0 0 {cx+R:.1f},{cyl_bot:.1f}" '
             f'fill="none" stroke="#2255aa" stroke-width="1.5"/>')
    bot_dash=(f'<path d="M {cx-R:.1f},{cyl_bot:.1f} A {R:.1f},{ry:.1f} 0 0 1 {cx+R:.1f},{cyl_bot:.1f}" '
              f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    sides=(f'<line x1="{cx-R:.1f}" y1="{cyl_top:.1f}" x2="{cx-R:.1f}" y2="{cyl_bot:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>'
           f'<line x1="{cx+R:.1f}" y1="{cyl_top:.1f}" x2="{cx+R:.1f}" y2="{cyl_bot:.1f}" '
           f'stroke="#2255aa" stroke-width="1.5"/>')
    # Dashed ellipse at join
    join_el=(f'<ellipse cx="{cx:.1f}" cy="{cyl_top:.1f}" rx="{R:.1f}" ry="{ry:.1f}" '
             f'fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="5"/>')
    # Cone on top
    cone_sl=(f'<line x1="{cx-R:.1f}" y1="{cyl_top:.1f}" x2="{cx:.1f}" y2="{cone_apex:.1f}" '
             f'stroke="#c85000" stroke-width="1.5"/>'
             f'<line x1="{cx+R:.1f}" y1="{cyl_top:.1f}" x2="{cx:.1f}" y2="{cone_apex:.1f}" '
             f'stroke="#c85000" stroke-width="1.5"/>')
    # Diameter arrow at base
    diam_line=(f'<line x1="{cx-R:.1f}" y1="{cyl_bot+ry+8:.1f}" '
               f'x2="{cx+R:.1f}" y2="{cyl_bot+ry+8:.1f}" '
               f'stroke="#c0392b" stroke-width="1.5" stroke-dasharray="5"/>')
    lb_r=_lbl(cx, cyl_bot+ry+22, rv, "#c0392b",12)
    lb_hc=_lbl(cx-R-18, cyl_top+Hcy/2, hcv, "#27ae60",12,"end")
    lb_hco=_lbl(cx+R+18, cone_apex+Hco/2, hconv, "#e67e22",12)
    return _svg_wrap(body_fill+bot_vis+bot_dash+sides+join_el+cone_sl+diam_line+lb_r+lb_hc+lb_hco, vw, vh)

# ─── T-SHAPED COMPOSITE CUBOIDS ──────────────────────────────────
def svg_t_cuboids(l_base,w_base,h_base,l_top,w_top,h_top,
                  ll_b=None,lw_b=None,lh_b=None,
                  ll_t=None,lw_t=None,lh_t=None):
    lb=ll_b or str(l_base); wb=lw_b or str(w_base); hb=lh_b or str(h_base)
    lt=ll_t or str(l_top);  wt=lw_t or str(w_top);  ht=lh_t or str(h_top)
    S=11
    Lb=min(l_base,12)*S; Wb=min(w_base,9)*S; Hb=min(h_base,5)*S
    Lt=min(l_top,8)*S;   Wt=min(w_top,6)*S;  Ht=min(h_top,8)*S
    ox=Wb*0.45; oy=Wb*0.32; pad=40
    vw=Lb+ox+pad*2; vh=Hb+Ht+oy+pad*2+10
    x0=pad; y_base=pad+oy+Ht   # base block top-left

    def block(fx,fy,W,H,ff,ft,fr,dash=False):
        sw="1" if dash else "1.5"; da='stroke-dasharray="4"' if dash else ""
        f=(f'<polygon points="{fx},{fy} {fx+W},{fy} {fx+W},{fy+H} {fx},{fy+H}" '
           f'fill="{ff}" stroke="#8a6000" stroke-width="{sw}" {da}/>')
        t=(f'<polygon points="{fx},{fy} {fx+ox},{fy-oy} {fx+W+ox},{fy-oy} {fx+W},{fy}" '
           f'fill="{ft}" stroke="#8a6000" stroke-width="{sw}" {da}/>')
        r=(f'<polygon points="{fx+W},{fy} {fx+W+ox},{fy-oy} {fx+W+ox},{fy+H-oy} {fx+W},{fy+H}" '
           f'fill="{fr}" stroke="#8a6000" stroke-width="{sw}" {da}/>')
        return f+t+r

    base=block(x0, y_base, Lb, Hb, "#fff3cd","#ffe082","#ffd54f")
    top_x=x0+(Lb-Lt)/2; top_y=y_base-Ht
    top_b=block(top_x, top_y, Lt, Ht, "#ffe0b2","#ffcc80","#ffb74d")

    lb_l=_lbl(x0+Lb/2, y_base+Hb+18, lb, "#c0392b",11)
    lb_w=_lbl(x0+Lb+ox/2+12, y_base-oy/2, wb, "#8e44ad",10)
    lb_h=_lbl(x0-14, y_base+Hb/2, hb, "#27ae60",11,"end")
    lb_lt=_lbl(top_x+Lt/2, top_y-14, lt, "#c0392b",11)
    lb_wt=_lbl(top_x+Lt+ox/2+12, top_y-oy/2, wt, "#8e44ad",10)
    lb_ht=_lbl(top_x-14, top_y+Ht/2, ht, "#27ae60",11,"end")

    return _svg_wrap(base+top_b+lb_l+lb_w+lb_h+lb_lt+lb_wt+lb_ht, vw, vh)

# ─── SA LABEL VERSIONS (letter labels, called by SA generators) ───
def svg_rect_prism_sa():
    return svg_rect_prism(5,3,4, lbl_l="l", lbl_w="w", lbl_h="h")

def svg_triangular_prism_sa():
    return svg_triangular_prism(4,3,7, lbl_b="b", lbl_h="h", lbl_l="l",
                                lbl_s1="s₁", lbl_s2="s₂")

def svg_trapezoidal_prism_sa():
    return svg_trapezoidal_prism(2,5,3,7, lbl_a="a", lbl_b="b",
                                 lbl_h="h", lbl_l="l")

def svg_cylinder_sa():
    return svg_cylinder(4,8, show_radius=True, lbl_r="r", lbl_h="h")

def svg_cylinder_open_sa():
    return svg_cylinder(4,8, show_radius=True, lbl_r="r", lbl_h="h")

def svg_half_cylinder_sa():
    return svg_half_cylinder(4,8, lbl_r="r", lbl_h="l")

def svg_sphere_sa():
    return svg_sphere(5, show_diameter=False, lbl_r="r")

def svg_sphere_diameter_sa():
    return svg_sphere(5, show_diameter=True, lbl_r="d")

def svg_hemisphere_sa():
    return svg_hemisphere(5, lbl_r="r")

def svg_cone_sa():
    return svg_cone(4,8, show_slant=True, lbl_r="r", lbl_h="h", lbl_sl="l")

def svg_cone_slant_sa():
    return svg_cone(4,8, show_slant=True, lbl_r="r", lbl_h="h", lbl_sl="l")

def svg_l_prism_sa():
    return svg_l_prism(5,6,3,2,8, lbl_a1="a", lbl_b1="b",
                       lbl_a2="c", lbl_b2="d", lbl_l="l")

def svg_cylinder_cone_sa():
    return svg_cylinder_cone(4,8,5, lbl_r="d", lbl_hc="h", lbl_hcone="l")

def svg_t_cuboids_sa():
    return svg_t_cuboids(6,4,2,3,2,5,
                         ll_b="l\u2081",lw_b="w\u2081",lh_b="h\u2081",
                         ll_t="l\u2082",lw_t="w\u2082",lh_t="h\u2082")
def svg_hollow_pipe(r_outer, r_inner, h, lbl_R=None, lbl_r=None, lbl_h=None):
    lR = lbl_R or str(r_outer)
    lr = lbl_r or str(r_inner)
    lh = lbl_h or str(h)
    S=14; Ro=min(r_outer,8)*S; Ri=min(r_inner,6)*S
    ry_o=Ro*0.28; ry_i=Ri*0.28; H=min(h,10)*S; pad=40
    vw=Ro*2+pad*2; vh=H+ry_o*2+pad*2
    cx=vw/2; top_cy=pad+ry_o; bot_cy=top_cy+H

    # Outer body fill (two rects left and right of inner hole)
    body=(f'<rect x="{cx-Ro:.1f}" y="{top_cy:.1f}" width="{Ro*2:.1f}" height="{H:.1f}" fill="#ddeeff" stroke="none"/>')
    # Inner body cutout (white)
    inner_mask=(f'<rect x="{cx-Ri:.1f}" y="{top_cy:.1f}" width="{Ri*2:.1f}" height="{H:.1f}" fill="white" stroke="none"/>')
    # Outer side lines
    sides=(f'<line x1="{cx-Ro:.1f}" y1="{top_cy:.1f}" x2="{cx-Ro:.1f}" y2="{bot_cy:.1f}" stroke="#2255aa" stroke-width="1.5"/>'
           f'<line x1="{cx+Ro:.1f}" y1="{top_cy:.1f}" x2="{cx+Ro:.1f}" y2="{bot_cy:.1f}" stroke="#2255aa" stroke-width="1.5"/>')
    # Inner side lines (dashed)
    inner_sides=(f'<line x1="{cx-Ri:.1f}" y1="{top_cy:.1f}" x2="{cx-Ri:.1f}" y2="{bot_cy:.1f}" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>'
                 f'<line x1="{cx+Ri:.1f}" y1="{top_cy:.1f}" x2="{cx+Ri:.1f}" y2="{bot_cy:.1f}" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Bottom outer ellipse visible arc
    bot_o_vis=(f'<path d="M {cx-Ro:.1f},{bot_cy:.1f} A {Ro:.1f},{ry_o:.1f} 0 0 0 {cx+Ro:.1f},{bot_cy:.1f}" fill="none" stroke="#2255aa" stroke-width="1.5"/>')
    bot_o_dash=(f'<path d="M {cx-Ro:.1f},{bot_cy:.1f} A {Ro:.1f},{ry_o:.1f} 0 0 1 {cx+Ro:.1f},{bot_cy:.1f}" fill="none" stroke="#2255aa" stroke-width="1" stroke-dasharray="4"/>')
    # Bottom inner ellipse
    bot_i=(f'<ellipse cx="{cx:.1f}" cy="{bot_cy:.1f}" rx="{Ri:.1f}" ry="{ry_i:.1f}" fill="white" stroke="#2255aa" stroke-width="1"/>')
    # Top: outer ellipse filled (annulus ring)
    top_o=(f'<ellipse cx="{cx:.1f}" cy="{top_cy:.1f}" rx="{Ro:.1f}" ry="{ry_o:.1f}" fill="#bbddff" stroke="#2255aa" stroke-width="1.5"/>')
    # Top: inner ellipse (hole, white)
    top_i=(f'<ellipse cx="{cx:.1f}" cy="{top_cy:.1f}" rx="{Ri:.1f}" ry="{ry_i:.1f}" fill="white" stroke="#2255aa" stroke-width="1.5"/>')
    # Labels
    lb_R=_lbl(cx+Ro/2+Ri/2, top_cy-14, lR, "#c0392b", 12)   # outer radius
    lb_r=_lbl(cx+Ri/2,       top_cy+10, lr, "#e67e22", 11)   # inner radius
    lb_h=_lbl(cx+Ro+20,      top_cy+H/2, lh, "#27ae60", 12)

    return _svg_wrap(body+inner_mask+sides+inner_sides+bot_o_vis+bot_o_dash+bot_i+top_o+top_i+lb_R+lb_r+lb_h, vw, vh)
# ══════════════════════════════════════════════════════════════════
# LT1 — VOLUME: RIGHT PRISMS
# ══════════════════════════════════════════════════════════════════

def gen_prism_rectangle():
    l=ri(3,14); w=ri(2,9); h=ri(2,8)
    vol=l*w*h
    q=f"\\text{{Cuboid: }}l={l}\\text{{ cm}},\\ w={w}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\text{{ cm}}^3"
    sol=f"V={l}\\times{w}\\times{h}={vol}\\text{{ cm}}^3"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_rect_prism(l,w,h); return p

def gen_prism_given_area():
    A=ri(8,50); h=ri(3,14); vol=A*h
    q=f"\\text{{Prism: }}A={A}\\,{_u('cm^2')},\\ l={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V={A}\\times{h}={vol}\\,{_u('cm^3')}"
    return _part(q,a,sol,f"{vol} cm^3")

def gen_prism_triangle():
    b=ri(3,10); ht=ri(3,8); l=ri(5,14)
    A=round(0.5*b*ht,1); vol=round(A*l,1)
    q=f"\\text{{Triangular prism: }}b={b},\\ h={ht},\\ l={l}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"A=\\tfrac{{1}}{{2}}\\times{b}\\times{ht}={A}\\quad V={A}\\times{l}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_triangular_prism(b,ht,l); return p

def gen_prism_trapezoid():
    a=ri(2,5); b=a+ri(2,5); ht=ri(2,5); s1=ri(3,7); s2=ri(3,7); l=ri(5,12)
    A=0.5*(a+b)*ht; vol=round(A*l,1)
    q=f"\\text{{Trapezoidal prism: }}a={a},\\ b={b},\\ h={ht},\\ l={l}\\text{{ cm}}"
    a_ans=f"{vol}\\,{_u('cm^3')}"
    sol=f"A=\\tfrac{{1}}{{2}}({a}+{b})\\times{ht}={A}\\quad V={A}\\times{l}={vol}\\,{_u('cm^3')}"
    p=_part(q,a_ans,sol,f"{vol} cm^3"); p["svg"]=svg_trapezoidal_prism(a,b,ht,l); return p

def gen_prism_parallelogram():
    b=ri(4,10); ht=ri(3,8); l=ri(5,14)
    A=b*ht; vol=A*l
    q=f"\\text{{Parallelogram prism: }}b={b},\\ h={ht},\\ l={l}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"A={b}\\times{ht}={A}\\quad V={A}\\times{l}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_parallelogram_prism(b,ht,l); return p

# ══════════════════════════════════════════════════════════════════
# LT2 — VOLUME: CYLINDERS
# ══════════════════════════════════════════════════════════════════

def gen_cylinder_radius():
    r=ri(2,10); h=ri(3,15); vol=round(math.pi*r**2*h,1)
    q=f"\\text{{Cylinder: }}r={r}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_cylinder(r,h,True); return p

def gen_cylinder_diameter():
    d=ri(4,18); r=d/2; h=ri(3,14); vol=round(math.pi*r**2*h,1)
    q=f"\\text{{Cylinder: }}d={d}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"r={d}\\div2={r}\\quad V=\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_cylinder(r,h,False); return p

def gen_cylinder_mixed_units():
    r=round(random.uniform(0.5,3.5),1); h=round(random.uniform(1.0,8.0),1)
    vol=round(math.pi*r**2*h,1)
    q=f"\\text{{Cylinder: }}r={r}\\text{{ m}},\\ h={h}\\text{{ m}}"
    a=f"{vol}\\,{_u('m^3')}"
    sol=f"V=\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('m^3')}"
    return _part(q,a,sol,f"{vol} m^3")

# ══════════════════════════════════════════════════════════════════
# LT3 — VOLUME: CYLINDRICAL PORTIONS
# ══════════════════════════════════════════════════════════════════

def gen_half_cylinder():
    r=ri(2,9); h=ri(4,16); vol=round(0.5*math.pi*r**2*h,1)
    q=f"\\text{{Half-cylinder: }}r={r}\\text{{ cm}},\\ l={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{2}}\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_half_cylinder(r,h); return p

def gen_quarter_cylinder():
    r=ri(2,9); h=ri(4,16); vol=round(0.25*math.pi*r**2*h,1)
    q=f"\\text{{Quarter-cylinder: }}r={r}\\text{{ cm}},\\ l={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{4}}\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_quarter_cylinder(r,h); return p

def gen_sector_cylinder():
    r=ri(3,10); h=ri(4,14)
    theta=random.choice([60,90,120,150,240,270,300])
    vol=round((theta/360)*math.pi*r**2*h,1)
    q=f"\\text{{Sector cylinder: }}r={r},\\ l={h}\\text{{ cm}},\\ \\theta={theta}^\\circ"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\dfrac{{{theta}}}{{360}}\\times\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_sector_cylinder(r,h,theta); return p

# ══════════════════════════════════════════════════════════════════
# LT4 — FIND MISSING DIMENSION
# ══════════════════════════════════════════════════════════════════

def gen_find_missing_prism():
    w=ri(2,8); h=ri(2,7); l=ri(3,12); vol=l*w*h
    q=f"\\text{{Cuboid: }}V={vol}\\,{_u('cm^3')},\\ w={w},\\ h={h}\\text{{ cm. Find }}l."
    a=f"l={l}\\text{{ cm}}"
    sol=f"l=\\dfrac{{{vol}}}{{{w}\\times{h}}}={l}\\text{{ cm}}"
    return _part(q,a,sol,f"l={l} cm",is_wide=True)

def gen_find_missing_cylinder():
    r=ri(2,8); h=ri(3,12); vol=round(math.pi*r**2*h,1)
    if random.choice([True,False]):
        q=f"\\text{{Cylinder: }}V={vol}\\,{_u('cm^3')},\\ r={r}\\text{{ cm. Find }}h."
        a=f"h={h}\\text{{ cm}}"
        sol=f"h=\\dfrac{{{vol}}}{{\\pi\\times{r}^2}}\\approx{h}\\text{{ cm}}"
    else:
        q=f"\\text{{Cylinder: }}V={vol}\\,{_u('cm^3')},\\ h={h}\\text{{ cm. Find }}r."
        a=f"r={r}\\text{{ cm}}"
        sol=f"r=\\sqrt{{\\dfrac{{{vol}}}{{\\pi\\times{h}}}}}\\approx{r}\\text{{ cm}}"
    return _part(q,a,sol,is_wide=True)

def gen_find_missing_tri_prism():
    """Triangular prism — find the height of the cross-section."""
    b=ri(4,10); l=ri(6,12); x=ri(3,9)
    vol=round(0.5*b*x*l,1)
    q=(f"\\text{{Triangular prism: }}V={vol}\\,{_u('cm^3')},"
       f"\\ b={b}\\text{{ cm}},\\ l={l}\\text{{ cm. Find }}x.")
    a=f"x={x}\\text{{ cm}}"
    sol=(f"\\tfrac{{1}}{{2}}\\times{b}\\times x\\times{l}={vol}"
         f"\\Rightarrow x=\\dfrac{{2\\times{vol}}}{{{b}\\times{l}}}={x}\\text{{ cm}}")
    return _part(q,a,sol,f"x={x} cm",is_wide=True)

# ══════════════════════════════════════════════════════════════════
# LT5 — REAL-WORLD CONTEXT
# ══════════════════════════════════════════════════════════════════

def gen_context_tank():
    r=round(random.uniform(0.5,2.5),1); h=round(random.uniform(1.0,5.0),1)
    vol_m3=round(math.pi*r**2*h,2); litres=int(round(vol_m3*1000,0))
    q=(f"\\text{{Cylindrical tank: }}r={r}\\text{{ m}},\\ h={h}\\text{{ m.}}"
       f"\\ \\text{{How many litres?}}")
    a=f"{_fmt_num(litres)}\\text{{ L}}"
    sol=f"V\\approx{vol_m3}\\,{_u('m^3')}\\times1000={_fmt_num(litres)}\\text{{ L}}"
    return _part(q,a,sol,is_wide=True)

def gen_context_shed():
    b=ri(3,7); ht=ri(2,5); l=ri(6,14); vol=round(0.5*b*ht*l,1)
    q=(f"\\text{{Triangular prism roof: }}"
       f"b={b}\\text{{ m}},\\ h={ht}\\text{{ m}},\\ l={l}\\text{{ m. Find volume.}}")
    a=f"{vol}\\,{_u('m^3')}"
    sol=f"V=\\tfrac{{1}}{{2}}\\times{b}\\times{ht}\\times{l}={vol}\\,{_u('m^3')}"
    return _part(q,a,sol,is_wide=True)

# ══════════════════════════════════════════════════════════════════
# LT6 — COMPOSITE SOLIDS (VOLUME)
# ══════════════════════════════════════════════════════════════════

def gen_composite_prism_cylinder():
    l=ri(6,14); w=ri(4,9); h=ri(3,8); r=w/2
    vp=l*w*h; vh2=round(0.5*math.pi*r**2*l,1); vol=round(vp+vh2,1)
    q=(f"\\text{{Prism+half-cyl: }}l={l},w={w},h={h}\\text{{ cm}}"
       f",\\ r={r}\\text{{ cm}}")
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V_{{\\text{{prism}}}}={vp}+V_{{\\text{{half-cyl}}}}\\approx{vh2}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,is_wide=True); p["svg"]=svg_house_prism(l,w,h,r); return p

def gen_composite_two_prisms():
    a1=ri(4,10); b1=ri(3,6); a2=ri(2,4); b2=ri(2,4); l=ri(6,14)
    A=a1*b1+a2*b2; vol=A*l
    q=(f"\\text{{L-prism: }}({a1}\\times{b1})"
       f"\\text{{ and }}({a2}\\times{b2})\\text{{ cm}},\\ l={l}\\text{{ cm}}")
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"A={a1*b1}+{a2*b2}={A}\\quad V={A}\\times{l}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,is_wide=True); p["svg"]=svg_l_prism(a1,b1,a2,b2,l); return p

def gen_composite_l_prism():
    return gen_composite_two_prisms()

def gen_composite_cylinder_subtract():
    l=ri(6,14); w=ri(4,10); h=ri(3,8); r=ri(1,min(w,h)//2)
    vb=l*w*h; vh2=round(math.pi*r**2*l,1); vol=round(vb-vh2,1)
    q=(f"\\text{{Box}}(l={l},w={w},h={h}\\text{{ cm)}}"
       f"\\text{{, hole }}r={r}\\text{{ cm}}")
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V={vb}-{vh2}={vol}\\,{_u('cm^3')}"
    return _part(q,a,sol,is_wide=True)

def gen_composite_tunnel():
    ro=ri(4,9); ri2=ri(1,ro-2); h=ri(6,20)
    vo=round(math.pi*ro**2*h,1); vi=round(math.pi*ri2**2*h,1)
    vol=round(vo-vi,1)
    q=f"\\text{{Hollow pipe: }}R={ro},\\ r={ri2},\\ l={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\pi({ro}^2-{ri2}^2)\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,is_wide=True)   # ← assign to p
    p["svg"]=svg_hollow_pipe(ro,ri2,h)  # ← correct name + correct variables
    return p
  

def gen_composite_t_cuboids():
    """Two cuboids stacked (T-shape) — find volume."""
    lb=ri(5,12); wb=ri(4,9); hb=ri(2,5)
    lt=ri(2,lb-1); wt=ri(2,wb-1); ht=ri(4,10)
    vol=lb*wb*hb+lt*wt*ht
    q=(f"\\text{{T-shape: base }}({lb}\\times{wb}\\times{hb})"
       f"\\text{{ cm, top }}({lt}\\times{wt}\\times{ht})\\text{{ cm.}}"
       f"\\ \\text{{Find total volume.}}")
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V={lb}\\times{wb}\\times{hb}+{lt}\\times{wt}\\times{ht}={lb*wb*hb}+{lt*wt*ht}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,is_wide=True)
    p["svg"]=svg_t_cuboids(lb,wb,hb,lt,wt,ht)
    return p

# ══════════════════════════════════════════════════════════════════
# LT7 — SURFACE AREA: CUBOIDS & PRISMS
# ══════════════════════════════════════════════════════════════════

def gen_sa_cuboid():
    l=ri(3,12); w=ri(2,8); h=ri(2,7)
    lw=l*w; lh=l*h; wh=w*h; SA=2*(lw+lh+wh)
    q=f"\\text{{Cuboid: }}l={l},\\ w={w},\\ h={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"SA=2({lw}+{lh}+{wh})={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_rect_prism_sa(); return p

def gen_sa_triangular_prism():
    b=ri(3,8); ht=ri(3,7); s1=ri(4,9); s2=ri(4,9); l=ri(5,14)
    A_tri=round(0.5*b*ht,1); SA=round(2*A_tri+b*l+s1*l+s2*l,1)
    q=f"\\text{{Tri-prism: }}b={b},\\ h={ht},\\ s_1={s1},\\ s_2={s2},\\ l={l}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\times{A_tri}+({b}+{s1}+{s2})\\times{l}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_triangular_prism_sa(); return p

def gen_sa_trapezoidal_prism():
    a=ri(2,5); b=a+ri(2,5); ht=ri(2,5); s1=ri(3,7); s2=ri(3,7); l=ri(5,12)
    A_trap=0.5*(a+b)*ht; SA=round(2*A_trap+(a+b+s1+s2)*l,1)
    q=f"\\text{{Trap-prism: }}a={a},\\ b={b},\\ h={ht},\\ s_1={s1},\\ s_2={s2},\\ l={l}\\text{{ cm}}"
    a_ans=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\times\\tfrac{{1}}{{2}}({a}+{b})\\times{ht}+({a}+{b}+{s1}+{s2})\\times{l}={SA}\\,{_u('cm^2')}"
    p=_part(q,a_ans,sol,f"{SA} cm^2"); p["ex_svg"]=svg_trapezoidal_prism_sa(); return p

def gen_sa_open_box():
    l=ri(4,12); w=ri(3,8); h=ri(2,6)
    SA=l*w+2*l*h+2*w*h
    q=f"\\text{{Open box: }}l={l},\\ w={w},\\ h={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"lw+2lh+2wh={l*w}+{2*l*h}+{2*w*h}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_rect_prism_sa(); return p

def gen_sa_l_prism():
    """SA of L-shaped prism — image 9 style."""
    a=ri(4,10); b=ri(5,10); c=ri(2,5); d=ri(2,4); l=ri(6,14)
    # L cross-section: big rect minus corner rect
    A_cross=a*b - (a-c)*(b-d)
    # Faces: 2 L-ends + all outer rectangular faces
    perim=a+b+c+(b-d)+( a-c)+d   # perimeter of L
    SA=round(2*A_cross+perim*l,1)
    q=(f"\\text{{L-prism: outer }}a={a},b={b},"
       f"\\text{{ notch }}c={c},d={d},\\ l={l}\\text{{ cm}}")
    ans=f"{SA}\\,{_u('cm^2')}"
    sol=(f"A_{{\\text{{cross}}}}={a}\\times{b}-({a-c})\\times({b-d})={A_cross}\\,{_u('cm^2')}"
         f"\\quad SA=2\\times{A_cross}+{perim}\\times{l}={SA}\\,{_u('cm^2')}")
    p=_part(q,ans,sol,f"{SA} cm^2",is_wide=True)
    p["ex_svg"]=svg_l_prism_sa()
    return p

# ══════════════════════════════════════════════════════════════════
# LT8 — SURFACE AREA: CYLINDERS
# ══════════════════════════════════════════════════════════════════

def gen_sa_cylinder_closed():
    r=ri(2,10); h=ri(3,15)
    curved=round(2*math.pi*r*h,1); ends=round(2*math.pi*r**2,1); SA=round(curved+ends,1)
    q=f"\\text{{Closed cylinder: }}r={r}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\pi rh+2\\pi r^2\\approx{curved}+{ends}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_cylinder_sa(); return p

def gen_sa_cylinder_open():
    r=ri(2,9); h=ri(4,14)
    curved=round(2*math.pi*r*h,1); one_end=round(math.pi*r**2,1); SA=round(curved+one_end,1)
    q=f"\\text{{Open-top cylinder: }}r={r}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\pi rh+\\pi r^2\\approx{curved}+{one_end}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_cylinder_open_sa(); return p

def gen_sa_cylinder_tube():
    r=ri(2,8); h=ri(5,20); SA=round(2*math.pi*r*h,1)
    q=f"\\text{{Open tube: }}r={r}\\text{{ cm}},\\ l={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\pi rh\\approx{SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_cylinder_sa(); return p

def gen_sa_half_cylinder():
    r=ri(2,7); h=ri(5,15)
    curved=round(math.pi*r*h,1); rect=round(2*r*h,1)
    semis=round(math.pi*r**2,1); SA=round(curved+rect+semis,1)
    q=f"\\text{{Half-cylinder: }}r={r}\\text{{ cm}},\\ l={h}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"\\pi rh+2rh+\\pi r^2\\approx{curved}+{rect}+{semis}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_half_cylinder_sa(); return p

# ══════════════════════════════════════════════════════════════════
# LT9 — SURFACE AREA: COMPOSITE
# ══════════════════════════════════════════════════════════════════

def gen_sa_composite_prism_halfcyl():
    l=ri(6,14); w=ri(4,8); h_wall=ri(3,7); r=w/2
    A_end=round(w*h_wall+0.5*math.pi*r**2,1)
    long_side=round(l*h_wall,1); half_curved=round(math.pi*r*l,1); bottom=l*w
    SA=round(2*A_end+2*long_side+half_curved+bottom,1)
    q=f"\\text{{House prism: }}l={l},\\ w={w},\\ h_{{\\text{{wall}}}}={h_wall},\\ r={r}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\times A_{{\\text{{end}}}}+2\\times\\text{{side}}+\\text{{half-cyl}}+\\text{{base}}\\approx{SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,is_wide=True); p["ex_svg"]=svg_house_prism(l,w,h_wall,r); return p

def gen_sa_composite_subtract():
    l=ri(6,12); w=ri(4,9); h=ri(3,7); r=ri(1,min(l,w)//3)
    full_SA=2*(l*w+l*h+w*h); hole=round(math.pi*r**2,1); SA=round(full_SA-hole,1)
    q=f"\\text{{Cuboid}}(l={l},w={w},h={h}\\text{{ cm) with hole }}r={r}\\text{{ cm}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"{full_SA}-\\pi r^2\\approx{full_SA}-{hole}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,is_wide=True); p["ex_svg"]=svg_rect_prism_sa(); return p

def gen_sa_cylinder_cone():
    """Cylinder + cone composite SA (image 16 style)."""
    r=ri(3,8); h_cyl=ri(6,14); h_cone=ri(4,10)
    sl=round(math.sqrt(r**2+h_cone**2),2)
    curved=round(2*math.pi*r*h_cyl,1); base=round(math.pi*r**2,1)
    cone_lat=round(math.pi*r*sl,1); SA=round(curved+base+cone_lat,1)
    q=(f"\\text{{Cylinder+cone: }}d={r*2}\\text{{ cm}},"
       f"\\ h_{{\\text{{cyl}}}}={h_cyl},\\ h_{{\\text{{cone}}}}={h_cone}\\text{{ cm}}")
    a=f"{SA}\\,{_u('cm^2')}"
    sol=(f"2\\pi rh+\\pi r^2+\\pi rl\\approx{curved}+{base}+{cone_lat}={SA}\\,{_u('cm^2')}")
    p=_part(q,a,sol,is_wide=True)
    p["ex_svg"]=svg_cylinder_cone_sa()
    return p

# ══════════════════════════════════════════════════════════════════
# LT10 — UNIT CONVERSIONS
# ══════════════════════════════════════════════════════════════════

def gen_convert_length():
    options=[
        (lambda: round(random.uniform(1.5,9.9),1),"cm","mm",10),
        (lambda: ri(10,90),"mm","cm",0.1),
        (lambda: round(random.uniform(1.0,9.5),1),"m","cm",100),
        (lambda: ri(100,950),"cm","m",0.01),
        (lambda: round(random.uniform(1.5,9.5),1),"km","m",1000),
        (lambda: ri(2000,9000),"m","km",0.001),
        (lambda: round(random.uniform(0.5,4.0),1),"m","mm",1000),
        (lambda: ri(1000,5000),"mm","m",0.001),
    ]
    val_fn,fu,tu,fac=random.choice(options); val=val_fn()
    ans=round(val*fac,6)
    if ans==int(ans): ans=int(ans)
    q=f"{val}\\,{_u(fu)} = \\square\\,{_u(tu)}"
    a=f"{_fmt_num(ans)}\\,{_u(tu)}"
    sol=f"{val}\\times{fac}={_fmt_num(ans)}\\,{_u(tu)}"
    return _part(q,a,sol,str(ans))

def gen_convert_area():
    options=[
        (lambda: round(random.uniform(1.5,9.9),1),"cm^2","mm^2",100),
        (lambda: ri(100,900),"mm^2","cm^2",0.01),
        (lambda: round(random.uniform(2.0,8.5),1),"m^2","cm^2",10000),
        (lambda: ri(10000,90000),"cm^2","m^2",0.0001),
        (lambda: round(random.uniform(1.5,6.5),1),"km^2","m^2",1000000),
        (lambda: ri(1000000,9000000),"m^2","km^2",0.000001),
    ]
    val_fn,fu,tu,fac=random.choice(options); val=val_fn()
    ans=round(val*fac,6)
    if ans==int(ans): ans=int(ans)
    q=f"{val}\\,{_u(fu)} = \\square\\,{_u(tu)}"
    a=f"{_fmt_num(ans)}\\,{_u(tu)}"
    sol=f"{val}\\times{fac}={_fmt_num(ans)}\\,{_u(tu)}"
    return _part(q,a,sol,str(ans))

def gen_convert_volume():
    options=[
        (lambda: round(random.uniform(1.5,9.9),1),"cm^3","mm^3",1000),
        (lambda: ri(1000,9000),"mm^3","cm^3",0.001),
        (lambda: round(random.uniform(1.0,5.5),1),"m^3","cm^3",1000000),
        (lambda: ri(1000000,9000000),"cm^3","m^3",0.000001),
        (lambda: round(random.uniform(1.0,8.0),1),"m^3","L",1000),
        (lambda: ri(1000,9000),"L","m^3",0.001),
        (lambda: ri(50,900),"cm^3","mL",1),
    ]
    val_fn,fu,tu,fac=random.choice(options); val=val_fn()
    ans=round(val*fac,6)
    if ans==int(ans): ans=int(ans)
    q=f"{val}\\,{_u(fu)} = \\square\\,{_u(tu)}"
    a=f"{_fmt_num(ans)}\\,{_u(tu)}"
    sol=f"{val}\\times{fac}={_fmt_num(ans)}\\,{_u(tu)}"
    return _part(q,a,sol,str(ans))

def gen_convert_mixed():
    return random.choice([gen_convert_length,gen_convert_area,gen_convert_volume])()

# ══════════════════════════════════════════════════════════════════
# LT11 — PYRAMIDS, CONES, SPHERES
# ══════════════════════════════════════════════════════════════════

def gen_pyramid_rect():
    l=ri(3,12); w=ri(3,10); h=ri(4,14)
    vol=round((1/3)*l*w*h,1)
    q=f"\\text{{Rect pyramid: }}l={l},\\ w={w},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{3}}\\times{l}\\times{w}\\times{h}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_pyramid_rect(l,w,h); return p

def gen_pyramid_square():
    s=ri(3,10); h=ri(4,14); vol=round((1/3)*s**2*h,1)
    q=f"\\text{{Square pyramid: }}s={s}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{3}}\\times{s}^2\\times{h}={vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_pyramid_square(s,h); return p

def gen_pyramid_given_area():
    A=ri(8,50); h=ri(4,14); vol=round((1/3)*A*h,1)
    q=f"\\text{{Pyramid: }}A={A}\\,{_u('cm^2')},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{3}}\\times{A}\\times{h}={vol}\\,{_u('cm^3')}"
    return _part(q,a,sol,f"{vol} cm^3")

def gen_pyramid_missing():
    A=ri(8,40); h=ri(4,12); vol=round((1/3)*A*h,1)
    q=f"\\text{{Pyramid: }}V={vol}\\,{_u('cm^3')},\\ A={A}\\,{_u('cm^2')}\\text{{. Find }}h."
    a=f"h={h}\\text{{ cm}}"
    sol=f"h=\\dfrac{{3\\times{vol}}}{{{A}}}={h}\\text{{ cm}}"
    return _part(q,a,sol,is_wide=True)

def gen_cone_radius():
    r=ri(2,10); h=ri(4,16); vol=round((1/3)*math.pi*r**2*h,1)
    q=f"\\text{{Cone: }}r={r}\\text{{ cm}},\\ h={h}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{1}}{{3}}\\pi\\times{r}^2\\times{h}\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_cone(r,h); return p

def gen_cone_pythagoras():
    r=ri(3,8); h=ri(4,14)
    sl=round(math.sqrt(r**2+h**2),3); vol=round((1/3)*math.pi*r**2*h,1)
    q=f"\\text{{Cone: }}r={r}\\text{{ cm}},\\ l={sl}\\text{{ cm. Find volume.}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=(f"h=\\sqrt{{{sl}^2-{r}^2}}\\approx{h}\\text{{ cm}}"
         f"\\quad V\\approx{vol}\\,{_u('cm^3')}")
    p=_part(q,a,sol,f"{vol} cm^3",is_wide=True)
    p["svg"]=svg_cone(r,h,show_slant=True,lbl_sl=str(sl))
    return p

def gen_sphere_radius():
    r=ri(2,10); vol=round((4/3)*math.pi*r**3,1)
    q=f"\\text{{Sphere: }}r={r}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{4}}{{3}}\\pi\\times{r}^3\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_sphere(r); return p

def gen_sphere_diameter():
    d=ri(4,18); r=d/2; vol=round((4/3)*math.pi*r**3,1)
    q=f"\\text{{Sphere: }}d={d}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"r={d}\\div2={r}\\quad V=\\tfrac{{4}}{{3}}\\pi\\times{r}^3\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_sphere(r,show_diameter=True,lbl_r=str(d)); return p

def gen_hemisphere():
    r=ri(3,10); vol=round((2/3)*math.pi*r**3,1)
    q=f"\\text{{Hemisphere: }}r={r}\\text{{ cm}}"
    a=f"{vol}\\,{_u('cm^3')}"
    sol=f"V=\\tfrac{{2}}{{3}}\\pi\\times{r}^3\\approx{vol}\\,{_u('cm^3')}"
    p=_part(q,a,sol,f"{vol} cm^3"); p["svg"]=svg_hemisphere(r); return p

def gen_composite_cone_hemisphere():
    r=ri(3,7); h_cone=ri(5,15)
    v_hemi=round((2/3)*math.pi*r**3,1); v_cone=round((1/3)*math.pi*r**2*h_cone,1)
    vol=round(v_hemi+v_cone,1)
    q=(f"\\text{{Hemisphere}}(r={r})+\\text{{Cone}}"
       f"(r={r},h={h_cone})\\text{{ cm}}")
    a=f"{vol}\\,{_u('cm^3')}"
    sol=(f"V_{{\\text{{hemi}}}}\\approx{v_hemi}"
         f"+V_{{\\text{{cone}}}}\\approx{v_cone}={vol}\\,{_u('cm^3')}")
    p=_part(q,a,sol,is_wide=True); p["svg"]=svg_cone_hemisphere(r,h_cone); return p

# ─── NEW: SA exercises from images ────────────────────────────────

def gen_sa_sphere():
    r=ri(2,10); SA=round(4*math.pi*r**2,1)
    q=f"\\text{{Sphere: }}r={r}\\text{{ cm. Find surface area.}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"SA=4\\pi r^2=4\\pi\\times{r}^2\\approx{SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_sphere_sa(); return p

def gen_sa_sphere_diameter():
    """SA from diameter (images 1, 10)."""
    d=ri(4,20); r=d/2; SA=round(4*math.pi*r**2,1)
    q=f"\\text{{Sphere: diameter }}d={d}\\text{{ cm. Find surface area.}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"r={d}\\div2={r}\\quad SA=4\\pi\\times{r}^2\\approx{SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_sphere_diameter_sa(); return p

def gen_sa_hemisphere():
    """Total SA of hemisphere including flat circle (image 2)."""
    r=ri(3,12)
    curved=round(2*math.pi*r**2,1); flat=round(math.pi*r**2,1)
    SA=round(curved+flat,1)
    q=f"\\text{{Hemisphere: }}r={r}\\text{{ cm. Find total surface area.}}"
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"2\\pi r^2+\\pi r^2=3\\pi r^2\\approx{curved}+{flat}={SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2"); p["ex_svg"]=svg_hemisphere_sa(); return p

def gen_sa_cone():
    r=ri(3,9); h=ri(4,14)
    sl=round(math.sqrt(r**2+h**2),2); SA=round(math.pi*r**2+math.pi*r*sl,1)
    q=(f"\\text{{Cone: }}r={r}\\text{{ cm}},\\ h={h}\\text{{ cm.}}"
       f"\\ \\text{{Find total SA.}}")
    a=f"{SA}\\,{_u('cm^2')}"
    sol=(f"l=\\sqrt{{{r}^2+{h}^2}}\\approx{sl}\\text{{ cm}}"
         f"\\quad SA=\\pi r^2+\\pi rl\\approx{SA}\\,{_u('cm^2')}")
    p=_part(q,a,sol,f"{SA} cm^2",is_wide=True); p["ex_svg"]=svg_cone_sa(); return p

def gen_sa_cone_slant():
    """SA of cone with slant height given directly (image 15)."""
    r=ri(3,9)
    sl=ri(5,15)
    # ensure slant > r
    sl=max(sl,r+1)
    SA=round(math.pi*r**2+math.pi*r*sl,1)
    q=(f"\\text{{Cone: base radius }}r={r}\\text{{ cm}},"
       f"\\ \\text{{slant height }}l={sl}\\text{{ cm.}}"
       f"\\ \\text{{Find total SA.}}")
    a=f"{SA}\\,{_u('cm^2')}"
    sol=f"SA=\\pi r^2+\\pi rl=\\pi\\times{r}^2+\\pi\\times{r}\\times{sl}\\approx{SA}\\,{_u('cm^2')}"
    p=_part(q,a,sol,f"{SA} cm^2",is_wide=True)
    p["ex_svg"]=svg_cone(r,int(round(math.sqrt(sl**2-r**2))),
                         show_slant=True,lbl_r=str(r),
                         lbl_h="h",lbl_sl=str(sl))
    return p

def gen_similar_cylinders():
    """Similar cylinders — find volume using scale factor (image 3)."""
    l1=ri(3,8); l2=l1+ri(1,5)
    v1=ri(40,200)
    v2=round(v1*(l2/l1)**3,1)
    q=(f"\\text{{Similar cylinders A and B: }}"
       f"l_A={l1}\\text{{ cm}},\\ l_B={l2}\\text{{ cm}}."
       f"\\ V_A={v1}\\,{_u('cm^3')}."
       f"\\ \\text{{Find }}V_B.")
    a=f"{v2}\\,{_u('cm^3')}"
    sf=round(l2/l1,4)
    sol=(f"\\text{{Scale factor }}=\\dfrac{{{l2}}}{{{l1}}}={sf}"
         f"\\quad V_B={v1}\\times{sf}^3\\approx{v2}\\,{_u('cm^3')}")
    return _part(q,a,sol,f"{v2} cm^3",is_wide=True)

# ══════════════════════════════════════════════════════════════════
# LT12 — ALGEBRAIC VOLUME
# ══════════════════════════════════════════════════════════════════

def gen_algebraic_prism_triangle():
    k=ri(2,8)
    q=(f"\\text{{Tri-prism: base}}=2x,\\ h=x,"
       f"\\ \\text{{length}}=(x+{k})\\text{{ cm.}}"
       f"\\ \\text{{Find }}V.")
    a=f"V=x^3+{k}x^2"
    sol=f"V=\\tfrac{{1}}{{2}}\\times2x\\times x\\times(x+{k})=x^3+{k}x^2"
    return _part(q,a,sol,is_wide=True)

def gen_algebraic_prism_rectangle():
    a=ri(2,5); b=ri(2,4); c=ri(3,8); coef=a*b*c
    q=(f"\\text{{Rect prism: }}l={a}x,\\ w={b}x,\\ h={c}\\text{{ cm.}}"
       f"\\ \\text{{Express }}V.")
    a_ans=f"V={coef}x^2\\,{_u('cm^3')}"
    sol=f"V={a}x\\times{b}x\\times{c}={coef}x^2\\,{_u('cm^3')}"
    return _part(q,a_ans,sol,is_wide=True)

def gen_algebraic_cylinder():
    a=ri(1,3); b=ri(2,5); coef=a**2*b
    q=(f"\\text{{Cylinder: }}r={a}x\\text{{ cm}},\\ h={b}x\\text{{ cm.}}"
       f"\\ \\text{{Express }}V.")
    a_ans=f"V={coef}\\pi x^3\\,{_u('cm^3')}"
    sol=f"V=\\pi({a}x)^2\\times{b}x={coef}\\pi x^3\\,{_u('cm^3')}"
    return _part(q,a_ans,sol,is_wide=True)

def gen_algebraic_find_x():
    x_val=ri(2,5); coef=ri(2,6); vol=coef*x_val**3
    q=(f"\\text{{Prism: }}V={vol}\\,{_u('cm^3')},"
       f"\\ l=x,\\ w=x,\\ h={coef}x.\\ \\text{{Find }}x.")
    a=f"x={x_val}\\text{{ cm}}"
    sol=(f"{coef}x^3={vol}"
         f"\\Rightarrow x=\\sqrt[3]{{{vol//coef}}}={x_val}\\text{{ cm}}")
    return _part(q,a,sol,is_wide=True)

# ══════════════════════════════════════════════════════════════════
# REGISTRY
# ══════════════════════════════════════════════════════════════════

REGISTRY = {
    "prism_rectangle":      gen_prism_rectangle,
    "prism_given_area":     gen_prism_given_area,
    "prism_triangle":       gen_prism_triangle,
    "prism_trapezoid":      gen_prism_trapezoid,
    "prism_parallelogram":  gen_prism_parallelogram,
    "cylinder_radius":      gen_cylinder_radius,
    "cylinder_diameter":    gen_cylinder_diameter,
    "cylinder_mixed_units": gen_cylinder_mixed_units,
    "half_cylinder":        gen_half_cylinder,
    "quarter_cylinder":     gen_quarter_cylinder,
    "sector_cylinder":      gen_sector_cylinder,
    "find_missing_prism":    gen_find_missing_prism,
    "find_missing_cylinder": gen_find_missing_cylinder,
    "find_missing_tri_prism":gen_find_missing_tri_prism,
    "context_tank":         gen_context_tank,
    "context_shed":         gen_context_shed,
    "composite_prism_cylinder":    gen_composite_prism_cylinder,
    "composite_two_prisms":        gen_composite_two_prisms,
    "composite_l_prism":           gen_composite_l_prism,
    "composite_cylinder_subtract": gen_composite_cylinder_subtract,
    "composite_tunnel":            gen_composite_tunnel,
    "composite_t_cuboids":         gen_composite_t_cuboids,
    "sa_cuboid":            gen_sa_cuboid,
    "sa_triangular_prism":  gen_sa_triangular_prism,
    "sa_trapezoidal_prism": gen_sa_trapezoidal_prism,
    "sa_open_box":          gen_sa_open_box,
    "sa_l_prism":           gen_sa_l_prism,
    "sa_cylinder_closed":   gen_sa_cylinder_closed,
    "sa_cylinder_open":     gen_sa_cylinder_open,
    "sa_cylinder_tube":     gen_sa_cylinder_tube,
    "sa_half_cylinder":     gen_sa_half_cylinder,
    "sa_composite_prism_halfcyl": gen_sa_composite_prism_halfcyl,
    "sa_composite_subtract":      gen_sa_composite_subtract,
    "sa_cylinder_cone":           gen_sa_cylinder_cone,
    "convert_length":       gen_convert_length,
    "convert_area":         gen_convert_area,
    "convert_volume":       gen_convert_volume,
    "convert_mixed":        gen_convert_mixed,
    "pyramid_rect":              gen_pyramid_rect,
    "pyramid_square":            gen_pyramid_square,
    "pyramid_given_area":        gen_pyramid_given_area,
    "pyramid_missing":           gen_pyramid_missing,
    "cone_radius":               gen_cone_radius,
    "cone_pythagoras":           gen_cone_pythagoras,
    "sphere_radius":             gen_sphere_radius,
    "sphere_diameter":           gen_sphere_diameter,
    "hemisphere":                gen_hemisphere,
    "composite_cone_hemisphere": gen_composite_cone_hemisphere,
    "sa_sphere":                 gen_sa_sphere,
    "sa_sphere_diameter":        gen_sa_sphere_diameter,
    "sa_hemisphere":             gen_sa_hemisphere,
    "sa_cone":                   gen_sa_cone,
    "sa_cone_slant":             gen_sa_cone_slant,
    "similar_cylinders":         gen_similar_cylinders,
    "algebraic_prism_triangle":  gen_algebraic_prism_triangle,
    "algebraic_prism_rectangle": gen_algebraic_prism_rectangle,
    "algebraic_cylinder":        gen_algebraic_cylinder,
    "algebraic_find_x":          gen_algebraic_find_x,
}

# ══════════════════════════════════════════════════════════════════
# METADATA
# ══════════════════════════════════════════════════════════════════

METADATA = {
    "prism_rectangle":     {"subtopic":"Volume of Rectangular Prism","difficulty":"easy","bloom":"remember","lt":["LT1"],"prerequisites":[],"skills":["volume_formula_prism","multiplication_of_integers","unit_recognition"],"strategy":["1. V = l × w × h."],"common_errors":["Adding instead of multiplying."],"remediation":None,"instruction":"Find the volume of each solid.","flint_prompt":"Multiply all three dimensions."},
    "prism_given_area":    {"subtopic":"Volume from Cross-Section Area","difficulty":"easy","bloom":"understand","lt":["LT1"],"prerequisites":["prism_rectangle"],"skills":["volume_formula_prism","area_identification"],"strategy":["1. V = A × l."],"common_errors":["Confusing area and volume units."],"remediation":"prism_rectangle","instruction":"Find the volume. The cross-section area is given.","flint_prompt":"If we know the area, what is the one remaining step?"},
    "prism_triangle":      {"subtopic":"Volume of Triangular Prism","difficulty":"easy","bloom":"apply","lt":["LT1"],"prerequisites":["prism_given_area"],"skills":["area_triangle","volume_formula_prism","multi_step_calculation"],"strategy":["1. A = ½bh.","2. V = A × l."],"common_errors":["Forgetting the ½."],"remediation":"prism_given_area","instruction":"Find the volume of each triangular prism.","flint_prompt":"What is the cross-section shape?"},
    "prism_trapezoid":     {"subtopic":"Volume of Trapezoidal Prism","difficulty":"medium","bloom":"apply","lt":["LT1"],"prerequisites":["prism_triangle"],"skills":["area_trapezoid","volume_formula_prism","multi_step_calculation"],"strategy":["1. A = ½(a+b)h.","2. V = A × l."],"common_errors":["Using a or b alone."],"remediation":"prism_triangle","instruction":"Find the volume of each trapezoidal prism.","flint_prompt":"What formula combines a and b?"},
    "prism_parallelogram": {"subtopic":"Volume of Parallelogram Prism","difficulty":"medium","bloom":"apply","lt":["LT1"],"prerequisites":["prism_rectangle"],"skills":["area_parallelogram","volume_formula_prism"],"strategy":["1. A = b×h_perp.","2. V = A × l."],"common_errors":["Using slant height."],"remediation":"prism_rectangle","instruction":"Find the volume of each parallelogram prism.","flint_prompt":"Which height is perpendicular?"},
    "cylinder_radius":     {"subtopic":"Volume of Cylinder (radius)","difficulty":"easy","bloom":"apply","lt":["LT2"],"prerequisites":["prism_given_area"],"skills":["cylinder_formula","squaring_numbers","use_of_pi"],"strategy":["1. V = πr²h."],"common_errors":["Using diameter instead of radius."],"remediation":"prism_given_area","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"What is the area of the circular base?"},
    "cylinder_diameter":   {"subtopic":"Volume of Cylinder (diameter)","difficulty":"medium","bloom":"apply","lt":["LT2"],"prerequisites":["cylinder_radius"],"skills":["cylinder_formula","diameter_to_radius","use_of_pi"],"strategy":["1. r = d/2.","2. V = πr²h."],"common_errors":["Using d in formula directly."],"remediation":"cylinder_radius","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"What must we do with the diameter first?"},
    "cylinder_mixed_units":{"subtopic":"Volume of Cylinder (metres)","difficulty":"medium","bloom":"apply","lt":["LT2"],"prerequisites":["cylinder_radius"],"skills":["cylinder_formula","unit_recognition","decimal_calculation"],"strategy":["1. V = πr²h."],"common_errors":["Unit confusion."],"remediation":"cylinder_radius","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"Are all dimensions in the same unit?"},
    "half_cylinder":       {"subtopic":"Volume of Half-Cylinder","difficulty":"medium","bloom":"apply","lt":["LT3"],"prerequisites":["cylinder_radius"],"skills":["cylinder_formula","fraction_of_solid","use_of_pi"],"strategy":["1. V = ½πr²h."],"common_errors":["Using full cylinder formula."],"remediation":"cylinder_radius","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"Where does the ½ appear?"},
    "quarter_cylinder":    {"subtopic":"Volume of Quarter-Cylinder","difficulty":"medium","bloom":"apply","lt":["LT3"],"prerequisites":["half_cylinder"],"skills":["cylinder_formula","fraction_of_solid","use_of_pi"],"strategy":["1. V = ¼πr²h."],"common_errors":["Using ½ instead of ¼."],"remediation":"half_cylinder","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"What fraction of a full circle?"},
    "sector_cylinder":     {"subtopic":"Volume of Cylindrical Sector","difficulty":"hard","bloom":"analyse","lt":["LT3"],"prerequisites":["quarter_cylinder"],"skills":["cylinder_formula","sector_fraction","use_of_pi","proportional_reasoning"],"strategy":["1. V = (θ/360)πr²h."],"common_errors":["Not dividing by 360."],"remediation":"quarter_cylinder","instruction":"Find the volume. Round to 1 decimal place.","flint_prompt":"What fraction of a full circle does the sector represent?"},
    "find_missing_prism":  {"subtopic":"Find Missing Prism Dimension","difficulty":"medium","bloom":"apply","lt":["LT4"],"prerequisites":["prism_rectangle"],"skills":["rearranging_formula","division_of_integers","algebraic_reasoning"],"strategy":["1. Divide V by the two known dimensions."],"common_errors":["Multiplying instead of dividing."],"remediation":"prism_rectangle","instruction":"Find the missing dimension.","flint_prompt":"How do you isolate l in V = lwh?"},
    "find_missing_cylinder":{"subtopic":"Find Missing Cylinder Dimension","difficulty":"hard","bloom":"analyse","lt":["LT4"],"prerequisites":["cylinder_radius","find_missing_prism"],"skills":["rearranging_formula","square_root","use_of_pi","algebraic_reasoning"],"strategy":["1. h = V/(πr²).","2. r = √(V/(πh))."],"common_errors":["Forgetting square root for r."],"remediation":"find_missing_prism","instruction":"Find the missing dimension. Round to 1 d.p.","flint_prompt":"Which dimension is unknown?"},
    "find_missing_tri_prism":{"subtopic":"Find Missing Height — Triangular Prism","difficulty":"medium","bloom":"apply","lt":["LT4"],"prerequisites":["prism_triangle"],"skills":["rearranging_formula","division_of_integers"],"strategy":["1. V = ½bxl → x = 2V/(bl)."],"common_errors":["Forgetting the ½."],"remediation":"prism_triangle","instruction":"Find the value of x.","flint_prompt":"Rearrange V = ½bxl for x."},
    "context_tank":        {"subtopic":"Real-World: Water Tank","difficulty":"medium","bloom":"apply","lt":["LT5"],"prerequisites":["cylinder_radius"],"skills":["cylinder_formula","unit_conversion_m3_to_litres","real_world_application"],"strategy":["1. V = πr²h in m³.","2. ×1000 for litres."],"common_errors":["Forgetting conversion."],"remediation":"cylinder_radius","instruction":"Solve the word problem. Show all working.","flint_prompt":"How many litres in 1 m³?"},
    "context_shed":        {"subtopic":"Real-World: Shed Roof","difficulty":"medium","bloom":"apply","lt":["LT5"],"prerequisites":["prism_triangle"],"skills":["prism_formula","real_world_application"],"strategy":["1. V = ½bhl."],"common_errors":["Using rectangular prism formula."],"remediation":"prism_triangle","instruction":"Solve the word problem. Show all working.","flint_prompt":"What 3D shape is the roof?"},
    "composite_prism_cylinder":    {"subtopic":"Composite: Prism + Half-Cylinder","difficulty":"hard","bloom":"analyse","lt":["LT6"],"prerequisites":["prism_rectangle","half_cylinder"],"skills":["composite_volume","multi_step_calculation","combining_shapes"],"strategy":["1. Split.","2. Calculate each.","3. Add."],"common_errors":["Double-counting overlap."],"remediation":"half_cylinder","instruction":"Find the total volume.","flint_prompt":"How many shapes?"},
    "composite_two_prisms":        {"subtopic":"Composite: L-Prism","difficulty":"hard","bloom":"analyse","lt":["LT6"],"prerequisites":["prism_rectangle"],"skills":["composite_volume","decomposing_shapes","multi_step_calculation"],"strategy":["1. Split into two rectangles.","2. Add volumes."],"common_errors":["Wrong decomposition."],"remediation":"prism_rectangle","instruction":"Find the total volume.","flint_prompt":"How would you cut this L-shape?"},
    "composite_l_prism":           {"subtopic":"Composite: L-Shaped Prism","difficulty":"medium","bloom":"apply","lt":["LT6"],"prerequisites":["prism_rectangle"],"skills":["composite_volume","area_l_shape","multi_step_calculation"],"strategy":["1. A = sum of rectangles.","2. V = A × l."],"common_errors":["Wrong dimensions."],"remediation":"prism_rectangle","instruction":"Find the volume of the L-shaped prism.","flint_prompt":"How many rectangles in the cross-section?"},
    "composite_cylinder_subtract": {"subtopic":"Composite: Subtract Cylinder","difficulty":"hard","bloom":"analyse","lt":["LT6"],"prerequisites":["prism_rectangle","cylinder_radius"],"skills":["composite_volume","subtraction_of_volumes","use_of_pi"],"strategy":["1. V_prism − V_hole."],"common_errors":["Adding instead of subtracting."],"remediation":"composite_prism_cylinder","instruction":"Find the volume of the solid.","flint_prompt":"Do we add or subtract the hole?"},
    "composite_tunnel":            {"subtopic":"Composite: Hollow Cylinder","difficulty":"hard","bloom":"analyse","lt":["LT6"],"prerequisites":["cylinder_radius"],"skills":["composite_volume","subtraction_of_volumes","use_of_pi"],"strategy":["1. V = π(R²−r²)h."],"common_errors":["Forgetting to subtract inner."],"remediation":"cylinder_radius","instruction":"Find the volume of material.","flint_prompt":"What do we subtract?"},
    "composite_t_cuboids":         {"subtopic":"Composite: T-Shape Cuboids","difficulty":"hard","bloom":"analyse","lt":["LT6"],"prerequisites":["prism_rectangle"],"skills":["composite_volume","decomposing_shapes","multi_step_calculation"],"strategy":["1. V_base + V_top."],"common_errors":["Overlapping region."],"remediation":"prism_rectangle","instruction":"Find the total volume of the compound solid.","flint_prompt":"How many cuboids?"},
    "sa_cuboid":           {"subtopic":"Surface Area of a Cuboid","difficulty":"easy","bloom":"remember","lt":["LT7"],"prerequisites":[],"skills":["sa_formula_cuboid","counting_faces","multiplication_of_integers"],"strategy":["1. SA = 2(lw+lh+wh)."],"common_errors":["Missing a face pair."],"remediation":None,"instruction":"Find the total surface area.","flint_prompt":"How many pairs of faces?"},
    "sa_triangular_prism": {"subtopic":"Surface Area of a Triangular Prism","difficulty":"medium","bloom":"apply","lt":["LT7"],"prerequisites":["sa_cuboid"],"skills":["area_triangle","sa_formula_prism","counting_faces"],"strategy":["1. 2×A_tri + 3 rect faces."],"common_errors":["Forgetting the ½."],"remediation":"sa_cuboid","instruction":"Find the total surface area.","flint_prompt":"How many faces?"},
    "sa_trapezoidal_prism":{"subtopic":"Surface Area of a Trapezoidal Prism","difficulty":"medium","bloom":"apply","lt":["LT7"],"prerequisites":["sa_triangular_prism"],"skills":["area_trapezoid","sa_formula_prism","counting_faces"],"strategy":["1. 2×A_trap + perimeter×l."],"common_errors":["Wrong perimeter."],"remediation":"sa_triangular_prism","instruction":"Find the total surface area.","flint_prompt":"Trapezoid area formula?"},
    "sa_open_box":         {"subtopic":"Surface Area of Open-Top Box","difficulty":"easy","bloom":"understand","lt":["LT7"],"prerequisites":["sa_cuboid"],"skills":["sa_formula_cuboid","counting_faces","omit_one_face"],"strategy":["1. lw+2lh+2wh."],"common_errors":["Including both top and bottom."],"remediation":"sa_cuboid","instruction":"Find the surface area (no lid).","flint_prompt":"Which face is missing?"},
    "sa_l_prism":          {"subtopic":"Surface Area of L-Shaped Prism","difficulty":"hard","bloom":"analyse","lt":["LT7"],"prerequisites":["sa_cuboid"],"skills":["area_l_shape","sa_formula_prism","multi_step_calculation"],"strategy":["1. SA = 2×A_cross + perimeter×l."],"common_errors":["Wrong perimeter."],"remediation":"sa_cuboid","instruction":"Find the total surface area of the L-prism.","flint_prompt":"Work out the perimeter of the L cross-section first."},
    "sa_cylinder_closed":  {"subtopic":"Surface Area of Closed Cylinder","difficulty":"medium","bloom":"apply","lt":["LT8"],"prerequisites":["sa_cuboid"],"skills":["sa_formula_cylinder","use_of_pi","curved_surface_area"],"strategy":["1. SA = 2πrh + 2πr²."],"common_errors":["Using diameter."],"remediation":None,"instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"Unroll the curved surface — what shape is it?"},
    "sa_cylinder_open":    {"subtopic":"Surface Area: Open-Top Cylinder","difficulty":"medium","bloom":"apply","lt":["LT8"],"prerequisites":["sa_cylinder_closed"],"skills":["sa_formula_cylinder","use_of_pi","omit_one_face"],"strategy":["1. 2πrh + πr²."],"common_errors":["Including both ends."],"remediation":"sa_cylinder_closed","instruction":"Find the surface area (no lid). Round to 1 d.p.","flint_prompt":"How many circular faces?"},
    "sa_cylinder_tube":    {"subtopic":"Surface Area: Open Tube","difficulty":"easy","bloom":"remember","lt":["LT8"],"prerequisites":["sa_cylinder_closed"],"skills":["curved_surface_area","use_of_pi"],"strategy":["1. 2πrh only."],"common_errors":["Adding circular ends."],"remediation":"sa_cylinder_closed","instruction":"Find the curved surface area. Round to 1 d.p.","flint_prompt":"No ends — what remains?"},
    "sa_half_cylinder":    {"subtopic":"Surface Area of Half-Cylinder","difficulty":"hard","bloom":"analyse","lt":["LT8"],"prerequisites":["sa_cylinder_closed"],"skills":["fraction_of_solid","curved_surface_area","area_rectangle","area_semicircle"],"strategy":["1. πrh + 2rh + πr²."],"common_errors":["Using 2πrh for curved part."],"remediation":"sa_cylinder_closed","instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"List every face on a half-cylinder."},
    "sa_composite_prism_halfcyl": {"subtopic":"SA: Prism + Half-Cylinder","difficulty":"hard","bloom":"analyse","lt":["LT9"],"prerequisites":["sa_cuboid","sa_half_cylinder"],"skills":["composite_sa","multi_step_calculation","combining_shapes"],"strategy":["1. List all visible faces.","2. Sum areas."],"common_errors":["Counting internal join."],"remediation":"sa_half_cylinder","instruction":"Find the total surface area.","flint_prompt":"Which faces are outside?"},
    "sa_composite_subtract":      {"subtopic":"SA: Cuboid with Hole","difficulty":"hard","bloom":"analyse","lt":["LT9"],"prerequisites":["sa_cuboid","sa_cylinder_closed"],"skills":["composite_sa","subtraction_of_areas","use_of_pi"],"strategy":["1. SA_cuboid − circle."],"common_errors":["Not subtracting circle."],"remediation":"sa_cuboid","instruction":"Find the total outer surface area.","flint_prompt":"Does the hole add any new surface?"},
    "sa_cylinder_cone":           {"subtopic":"SA: Cylinder + Cone","difficulty":"hard","bloom":"analyse","lt":["LT9"],"prerequisites":["sa_cylinder_closed","sa_cone"],"skills":["composite_sa","cone_sa_formula","curved_surface_area"],"strategy":["1. Curved cylinder + base + cone lateral."],"common_errors":["Counting join face twice."],"remediation":"sa_cylinder_closed","instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"Which faces are visible from outside?"},
    "convert_length":      {"subtopic":"Converting Units of Length","difficulty":"easy","bloom":"remember","lt":["LT10"],"prerequisites":[],"skills":["unit_conversion_length","multiply_by_powers_of_10"],"strategy":["×10:cm↔mm, ×100:m↔cm, ×1000:km↔m."],"common_errors":["Wrong factor."],"remediation":None,"instruction":"Convert the measurement.","flint_prompt":"Smaller or larger unit — multiply or divide?"},
    "convert_area":        {"subtopic":"Converting Units of Area","difficulty":"medium","bloom":"understand","lt":["LT10"],"prerequisites":["convert_length"],"skills":["unit_conversion_area","squaring_conversion_factors"],"strategy":["1. Square the length factor."],"common_errors":["Using length factor for area."],"remediation":"convert_length","instruction":"Convert the measurement.","flint_prompt":"Why do we square the factor for area?"},
    "convert_volume":      {"subtopic":"Converting Units of Volume","difficulty":"medium","bloom":"understand","lt":["LT10"],"prerequisites":["convert_area"],"skills":["unit_conversion_volume","cubing_conversion_factors"],"strategy":["1. Cube the length factor."],"common_errors":["Using area factor for volume."],"remediation":"convert_area","instruction":"Convert the measurement.","flint_prompt":"Why cube the factor for volume?"},
    "convert_mixed":       {"subtopic":"Mixed Unit Conversions","difficulty":"medium","bloom":"apply","lt":["LT10"],"prerequisites":["convert_length","convert_area","convert_volume"],"skills":["unit_conversion_length","unit_conversion_area","unit_conversion_volume"],"strategy":["1. Identify type.","2. Apply factor."],"common_errors":["Wrong power."],"remediation":"convert_volume","instruction":"Convert the measurement.","flint_prompt":"Length, area, or volume?"},
    "pyramid_rect":        {"subtopic":"Volume of Rectangular Pyramid","difficulty":"easy","bloom":"remember","lt":["LT11"],"prerequisites":["prism_rectangle"],"skills":["pyramid_formula","one_third_factor"],"strategy":["1. V = ⅓lwh."],"common_errors":["Forgetting ⅓."],"remediation":"prism_rectangle","instruction":"Find the volume. Round to 1 d.p. where needed.","flint_prompt":"Pyramid vs prism — what changes?"},
    "pyramid_square":      {"subtopic":"Volume of Square Pyramid","difficulty":"easy","bloom":"remember","lt":["LT11"],"prerequisites":["pyramid_rect"],"skills":["pyramid_formula","squaring_numbers","one_third_factor"],"strategy":["1. V = ⅓s²h."],"common_errors":["Not squaring s."],"remediation":"pyramid_rect","instruction":"Find the volume.","flint_prompt":"What is the base area?"},
    "pyramid_given_area":  {"subtopic":"Volume of Pyramid (area given)","difficulty":"easy","bloom":"understand","lt":["LT11"],"prerequisites":["pyramid_rect"],"skills":["pyramid_formula","one_third_factor"],"strategy":["1. V = ⅓Ah."],"common_errors":["Missing ⅓."],"remediation":"pyramid_rect","instruction":"Find the volume.","flint_prompt":"V = ⅓Ah — what is A?"},
    "pyramid_missing":     {"subtopic":"Find Missing Pyramid Dimension","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["pyramid_given_area"],"skills":["rearranging_formula","pyramid_formula"],"strategy":["1. h = 3V/A."],"common_errors":["Forgetting ×3."],"remediation":"pyramid_given_area","instruction":"Find the missing dimension.","flint_prompt":"Rearrange V = ⅓Ah for h."},
    "cone_radius":         {"subtopic":"Volume of a Cone","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["cylinder_radius","pyramid_rect"],"skills":["cone_formula","use_of_pi","one_third_factor"],"strategy":["1. V = ⅓πr²h."],"common_errors":["Missing ⅓."],"remediation":"pyramid_given_area","instruction":"Find the volume. Round to 3 s.f.","flint_prompt":"Cone vs cylinder — what factor?"},
    "cone_pythagoras":     {"subtopic":"Cone Volume using Pythagoras","difficulty":"hard","bloom":"analyse","lt":["LT11"],"prerequisites":["cone_radius"],"skills":["cone_formula","pythagoras_theorem"],"strategy":["1. h=√(l²−r²).","2. V=⅓πr²h."],"common_errors":["Using slant in formula."],"remediation":"cone_radius","instruction":"Find the volume. Round to 3 s.f.","flint_prompt":"Which side is the hypotenuse?"},
    "sphere_radius":       {"subtopic":"Volume of a Sphere","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["cylinder_radius"],"skills":["sphere_formula","use_of_pi","cubing_numbers"],"strategy":["1. V = 4/3 πr³."],"common_errors":["Squaring r."],"remediation":"cylinder_radius","instruction":"Find the volume. Round to 3 s.f.","flint_prompt":"What is r³?"},
    "sphere_diameter":     {"subtopic":"Sphere Volume (diameter given)","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sphere_radius"],"skills":["sphere_formula","diameter_to_radius"],"strategy":["1. r=d/2.","2. V=4/3 πr³."],"common_errors":["Using d directly."],"remediation":"sphere_radius","instruction":"Find the volume. Round to 1 d.p.","flint_prompt":"What must you do first?"},
    "hemisphere":          {"subtopic":"Volume of a Hemisphere","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sphere_radius"],"skills":["sphere_formula","fraction_of_solid"],"strategy":["1. V = 2/3 πr³."],"common_errors":["Using 4/3."],"remediation":"sphere_radius","instruction":"Find the volume. Round to 1 d.p.","flint_prompt":"Hemisphere = half sphere — how does formula change?"},
    "composite_cone_hemisphere": {"subtopic":"Composite: Cone + Hemisphere","difficulty":"hard","bloom":"analyse","lt":["LT11"],"prerequisites":["hemisphere","cone_radius"],"skills":["composite_volume","cone_formula","sphere_formula"],"strategy":["1. V_hemi + V_cone."],"common_errors":["Mixing fractions."],"remediation":"hemisphere","instruction":"Find the total volume. Round to 3 s.f.","flint_prompt":"What formula applies to each part?"},
    "sa_sphere":           {"subtopic":"Surface Area of a Sphere","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sa_cylinder_closed"],"skills":["sphere_sa_formula","use_of_pi"],"strategy":["1. SA = 4πr²."],"common_errors":["Using 2πr²."],"remediation":"sa_cylinder_closed","instruction":"Find the surface area. Round to 1 d.p.","flint_prompt":"Sphere SA formula?"},
    "sa_sphere_diameter":  {"subtopic":"Surface Area of Sphere (diameter given)","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sa_sphere"],"skills":["sphere_sa_formula","diameter_to_radius","use_of_pi"],"strategy":["1. r=d/2.","2. SA=4πr²."],"common_errors":["Using d in formula directly."],"remediation":"sa_sphere","instruction":"Find the surface area. Round to 1 d.p.","flint_prompt":"Find r first."},
    "sa_hemisphere":       {"subtopic":"Surface Area of a Hemisphere","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sa_sphere"],"skills":["sphere_sa_formula","fraction_of_solid","area_circle"],"strategy":["1. SA = 2πr² + πr² = 3πr²."],"common_errors":["Forgetting the flat circular base."],"remediation":"sa_sphere","instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"A hemisphere has two parts — curved surface and flat base."},
    "sa_cone":             {"subtopic":"Surface Area of a Cone","difficulty":"hard","bloom":"analyse","lt":["LT11"],"prerequisites":["sa_cylinder_closed","cone_pythagoras"],"skills":["cone_sa_formula","pythagoras_theorem"],"strategy":["1. l=√(r²+h²).","2. SA=πr²+πrl."],"common_errors":["Using h instead of l."],"remediation":"cone_radius","instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"Two parts to cone surface — what are they?"},
    "sa_cone_slant":       {"subtopic":"SA of Cone (slant height given)","difficulty":"medium","bloom":"apply","lt":["LT11"],"prerequisites":["sa_cone"],"skills":["cone_sa_formula","use_of_pi"],"strategy":["1. SA = πr² + πrl (l given directly)."],"common_errors":["Computing l from h when l is already given."],"remediation":"sa_cone","instruction":"Find the total surface area. Round to 1 d.p.","flint_prompt":"l is already given — no Pythagoras needed."},
    "similar_cylinders":   {"subtopic":"Similar Cylinders — Find Volume","difficulty":"hard","bloom":"analyse","lt":["LT11"],"prerequisites":["cylinder_radius"],"skills":["similar_solids","scale_factor","cubing_scale_factor"],"strategy":["1. SF = l_B/l_A.","2. V_B = V_A × SF³."],"common_errors":["Using SF² instead of SF³."],"remediation":"cylinder_radius","instruction":"Use the scale factor to find the volume.","flint_prompt":"Volume scale factor = (length scale factor)³."},
    "algebraic_prism_triangle":  {"subtopic":"Algebraic Volume — Triangular Prism","difficulty":"hard","bloom":"create","lt":["LT12"],"prerequisites":["prism_triangle"],"skills":["expanding_brackets","volume_formula_prism"],"strategy":["1. V=½×base×h×length.","2. Expand."],"common_errors":["Forgetting ½."],"remediation":"prism_triangle","instruction":"Find V in terms of x. Simplify.","flint_prompt":"Substitute and expand step by step."},
    "algebraic_prism_rectangle": {"subtopic":"Algebraic Volume — Rectangular Prism","difficulty":"hard","bloom":"apply","lt":["LT12"],"prerequisites":["prism_rectangle"],"skills":["algebraic_expressions","index_laws"],"strategy":["1. V=l×w×h algebraically."],"common_errors":["Adding powers."],"remediation":"prism_rectangle","instruction":"Express V in terms of x.","flint_prompt":"ax × bx = ?"},
    "algebraic_cylinder":        {"subtopic":"Algebraic Volume — Cylinder","difficulty":"hard","bloom":"apply","lt":["LT12"],"prerequisites":["cylinder_radius"],"skills":["algebraic_expressions","cylinder_formula"],"strategy":["1. V=πr²h with expressions."],"common_errors":["(ax)²≠ax²."],"remediation":"cylinder_radius","instruction":"Express V in terms of x. Leave π in answer.","flint_prompt":"(2x)² = ?"},
    "algebraic_find_x":          {"subtopic":"Solve for x given Volume","difficulty":"hard","bloom":"analyse","lt":["LT12"],"prerequisites":["algebraic_prism_rectangle"],"skills":["cube_root","rearranging_formula"],"strategy":["1. Isolate x³.","2. Cube root."],"common_errors":["Square root instead of cube root."],"remediation":"algebraic_prism_rectangle","instruction":"Find the value of x.","flint_prompt":"Isolate x³ first."},
}

DIFFICULTY = {k: v["difficulty"] for k, v in METADATA.items()}
SUBTOPIC   = {k: v["subtopic"]   for k, v in METADATA.items()}


def clean_skills(skills):
    return [s.replace("_", " ").capitalize() for s in skills]


def generate(types, seed=None, count=6, show_solutions=False):
    if seed is not None:
        random.seed(seed)
    exercises = []
    for i, ex_type in enumerate(types, 1):
        if ex_type not in REGISTRY:
            raise ValueError(f"Unknown type: '{ex_type}'. Available: {sorted(REGISTRY.keys())}")
        gen   = REGISTRY[ex_type]
        parts = [gen() for _ in range(count)]
        # Extract exercise-level SVG (SA diagrams) from first part if present
        ex_svg = None
        for p in parts:
            if "ex_svg" in p:
                ex_svg = p.pop("ex_svg")
                break
        # Strip ex_svg from all parts (already extracted)
        for p in parts:
            p.pop("ex_svg", None)
        for j, p in enumerate(parts):
            p["label"] = PART_LABELS[j]
            if not show_solutions:
                p.pop("solution_latex", None)
        m = METADATA.get(ex_type, {})
        ex = {
            "number":      i,
            "title":       m.get("subtopic", ex_type),
            "instruction": m.get("instruction", "Find the answer."),
            "parts":       parts,
            "meta": {
                "type":          ex_type,
                "subtopic":      m.get("subtopic", ""),
                "topic":         "Mensuration",
                "unit":          "Unit 3: Mensuration",
                "curriculum":    "MYP5",
                "difficulty":    m.get("difficulty", "medium"),
                "bloom":         m.get("bloom", "apply"),
                "lt":            m.get("lt", []),
                "prerequisites": m.get("prerequisites", []),
                "skills":        clean_skills(m.get("skills", ["Mensuration"])),
                "strategy":      m.get("strategy", []),
                "common_errors": m.get("common_errors", []),
                "remediation":   m.get("remediation", None),
                "flint_prompt":  m.get("flint_prompt", ""),
            }
        }
        if ex_svg:
            ex["ex_svg"] = ex_svg
        exercises.append(ex)

    return {
        "worksheet": {
            "title":          "Unit 3: Mensuration",
            "unit":           "Unit 3: Mensuration",
            "topic":          "Mensuration",
            "date":           str(date.today()),
            "total_parts":    len(types) * count,
            "seed":           seed,
            "show_solutions": show_solutions,
        },
        "exercises": exercises,
    }


def generate_session(types_json, seed=None, count=6):
    types = json.loads(types_json)
    return json.dumps(generate(types=types, seed=seed, count=count))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate Mensuration exercises")
    parser.add_argument("--types", nargs="+", default=["prism_rectangle"])
    parser.add_argument("--seed",           type=int,  default=None)
    parser.add_argument("--count",          type=int,  default=6)
    parser.add_argument("--show-solutions", action="store_true")
    parser.add_argument("--pretty",         action="store_true")
    parser.add_argument("--list-types",     action="store_true")
    args = parser.parse_args()
    if args.list_types:
        print("\nAvailable exercise types:\n")
        for k in sorted(REGISTRY.keys()):
            diff  = DIFFICULTY.get(k, "?")
            badge = {"easy":"🟢","medium":"🟡","hard":"🔴"}.get(diff,"⚪")
            print(f"  {badge}  {k:<38} {SUBTOPIC.get(k,'')}")
        print()
    else:
        result = generate(types=args.types, seed=args.seed,
                          count=args.count, show_solutions=args.show_solutions)
        print(json.dumps(result, ensure_ascii=False,
                         indent=2 if args.pretty else None))
