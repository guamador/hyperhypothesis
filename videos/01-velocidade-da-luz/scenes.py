"""Cenas da Hipótese #01 — E se você viajasse na velocidade da luz?"""
import math, random
import cairocffi as cairo
from hh.core import *

# ---------------------------------------------------------------- cenas
def scene_intro(ctx, t):                         # segs 0-1
    background(ctx, t)
    k = back(prog(t, S(0) + .1, .5))
    leave = prog(t, E(1) - 0.9, 0.9)
    board = prog(t, E(1) - 1.4, 0.5)
    px = lerp(330, 640, eio(board))
    person(ctx, px, 1180, 1.25 * k * (1 - eo(board) * .7), a=1 - board)
    sx = 700 + 900 * eio(leave) ** 2
    ship(ctx, sx, 1100, 1.15 * back(prog(t, S(0) + .3, .5)), flame=eo(leave) if leave > 0 else 0.12 + .05 * math.sin(t * 20))
    if leave > 0:   # rastros de velocidade
        for j, (dy, ln) in enumerate([(-60, 260), (0, 420), (60, 300)]):
            x1 = sx - 200; rrect(ctx, x1 - ln * leave, 1100 + dy - 4, ln * leave, 8, 4); fill(ctx, RED, .8 - j * .15)
    lines = [("E SE VOCÊ", INK), ("VIAJASSE NA", INK), ("VELOCIDADE", INK), ("DA LUZ?", BLUE)]
    for j, (ln, c) in enumerate(lines):
        kk = prog(t, S(1) + j * .18, .35)
        if kk > 0:
            text_fit(ctx, ln, DISP, 92, 540, 470 + j * 112 + 30 * (1 - eo(kk)), c, eo(kk))

def scene_energy(ctx, t):                        # segs 2-4
    background(ctx, t)
    x0, x1, yb, yt = 170, 900, 1220, 430
    ka = eo(prog(t, S(2), .5))
    ctx.set_line_width(4); ctx.set_source_rgba(*MUTED, ka)
    ctx.move_to(x0, yt - 20); ctx.line_to(x0, yb); ctx.line_to(x0 + (x1 + 60 - x0) * ka, yb); ctx.stroke()
    text(ctx, "ENERGIA", BOLD, 30, x0, yt - 50, MUTED, ka, "l", .06)
    text(ctx, "VELOCIDADE", BOLD, 30, x0, yb + 60, MUTED, ka, "l", .06)
    kc = eo(prog(t, S(2) + .5, .5))
    ctx.set_dash([18, 14]); ctx.set_line_width(5); ctx.set_source_rgba(*RED, kc)
    ctx.move_to(x1, yb); ctx.line_to(x1, yb - (yb - yt + 30) * kc); ctx.stroke(); ctx.set_dash([])
    text(ctx, "c", DISP, 64, x1, yb + 70, RED, kc)
    text(ctx, "velocidade da luz", SANS, 28, x1, yb + 110, RED, kc)
    # curva E = (γ-1)mc²
    p = 0.0
    if t >= S(3): p = 0.90 * eio(prog(t, S(3), E(3) - S(3) - .1))
    if t >= S(4): p = 0.90 + 0.0985 * eio(prog(t, S(4), (E(4) - S(4)) * .8))
    if p > 0:
        def pt(v):
            g = 1 / math.sqrt(1 - v * v); y = clamp((g - 1) / 7.0, 0, 1.15)
            return x0 + (x1 - x0) * v, yb - (yb - yt) * y
        ctx.set_line_width(9); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*BLUE, 1)
        n = 140; ctx.move_to(*pt(0))
        for i in range(1, n + 1): ctx.line_to(*pt(p * i / n))
        ctx.stroke()
        px, py = pt(p); circle(ctx, px, py, 22, BLUE); circle(ctx, px, py, 9, VOID)
    kinf = back(prog(t, S(4) + (E(4) - S(4)) * .55, .45))
    if kinf > 0:
        sh = 6 * math.sin(t * 60) * (1 - prog(t, S(4) + (E(4) - S(4)) * .55, 1.0))
        text(ctx, "∞", SANSB, 300 * kinf, x1 - 140 + sh, 520, RED, 1)

def scene_99(ctx, t):                            # seg 5
    background(ctx, t, drift=t * .2)
    k = eo(prog(t, S(5) + .25, 1.1)); n = int(round(99 * k))
    text(ctx, f"{n}%", DISP, 230 * lerp(.9, 1, back(prog(t, S(5) + .25, .4))), 540, 920, BLUE, prog(t, S(5) + .2, .2))
    text(ctx, "DA VELOCIDADE DA LUZ", BOLD, 40, 540, 1010, MUTED, prog(t, S(5) + .5, .3), track=.04)
    rrect(ctx, 96, 1110, 888, 26, 13); fill(ctx, ORBIT)
    rrect(ctx, 96, 1110, max(26, 888 * .99 * k), 26, 13); fill(ctx, BLUE)
    circle(ctx, 96 + 888 * .99 * k, 1123, 20, RED)

def scene_mt(ctx, t):                            # segs 6-7
    background(ctx, t)
    up = eio(prog(t, S(7), .6))
    kp = back(prog(t, S(6) + .1, .5))
    person(ctx, 540, lerp(640, 470, up), .9 * kp * (1 - up), a=1 - up)
    text(ctx, "70 kg", BOLD, 44, 540, 720, MUTED, prog(t, S(6) + .4, .3) * (1 - up))
    kn = eo(prog(t, S(6) + (E(6) - S(6)) * .55, 1.3)); n = int(round(9200 * kn))
    num = f"{n:,}".replace(",", ".")
    ya = prog(t, S(6) + (E(6) - S(6)) * .55, .15)
    text(ctx, num, DISP, lerp(190, 120, up), 540, lerp(1010, 520, up), SOLAR, ya)
    text(ctx, "MEGATONS", BOLD, lerp(52, 38, up), 540, lerp(1090, 580, up), INK, ya, track=.08)
    if t >= S(7):
        cols, rows, sp, sx, sy = 20, 25, 40, 540 - 19 * 20, 700
        tot = cols * rows; shown = int(tot * eo(prog(t, S(7) + .3, (E(7) - S(7)) * .75)))
        for i in range(shown):
            r, c = divmod(i, cols)
            circle(ctx, sx + c * sp, sy + r * 21, 7, SOLAR if (i % 37) else RED)
        ka = prog(t, S(7) + .3, .3)
        text(ctx, "cada ponto = 1.000 bombas de Hiroshima", SANS, 30, 540, 1250, MUTED, ka)

def scene_strange(ctx, t):                       # seg 8
    background(ctx, t, drift=t * 2)
    for x, y, r, a, ph in BG[:40]:               # estrelas esticando
        ln = 40 + 300 * prog(t, S(8), E(8) - S(8)); rrect(ctx, (x * 3 + t * 900) % (W + 400) - 200, y, ln, 4, 2); fill(ctx, INK, a * .6)
    k = prog(t, S(8) + .7, .3)
    j = (math.sin(t * 47) * 10 + math.sin(t * 91) * 6) * (1 - prog(t, S(8) + 1.0, 1.2))
    for ln, y in [("A COISA FICA", 860), ("ESTRANHA", 990)]:
        sz = 96 if ln == "A COISA FICA" else 120
        text_fit(ctx, ln, DISP, sz, 540 - j, y, RED, .85 * k)
        text_fit(ctx, ln, DISP, sz, 540 + j, y, BLUE, .85 * k)
        text_fit(ctx, ln, DISP, sz, 540, y, INK, k)

random.seed(3)
SKY = []
for _ in range(900):
    cz = random.uniform(-1, 1); ph = random.uniform(0, 2 * PI)
    SKY.append((cz, ph, random.uniform(.6, 1.6), random.uniform(.4, 1)))
def scene_sky(ctx, t):                           # segs 9-11 — aberração + Doppler relativísticos
    ctx.set_source_rgb(*VOID); ctx.paint()
    b = 0.0
    if t >= S(9): b = 0.5 * eio(prog(t, S(9), E(9) - S(9)))
    if t >= S(10): b = 0.5 + 0.49 * eio(prog(t, S(10), (E(10) - S(10)) * .9))
    g = 1 / math.sqrt(1 - b * b)
    cx, cy, R = 540, 800, 410
    circle(ctx, cx, cy, R + 6, ORBIT)
    for cz, ph, m, a in SKY:
        c2 = (cz + b) / (1 + b * cz); th = math.acos(clamp(c2, -1, 1))
        D = g * (1 + b * cz)                      # fator Doppler
        if D < 0.25: continue
        r = th / PI * R
        x, y = cx + r * math.cos(ph), cy + r * math.sin(ph)
        col = mix(INK, BLUE, clamp((D - 1) / 2.5)) if D >= 1 else mix(INK, RED, clamp((1 - D) / .55))
        al = a * clamp((D - .25) / .4) * (1 if D >= 1 else .8)
        circle(ctx, x, y, m * (1.6 + 1.3 * min(D, 4) ** .5), col, al)
    ka = prog(t, S(9) + .2, .4)
    text(ctx, "FRENTE", BOLD, 26, cx, cy - 18, INK, .55 * ka * (1 - prog(t, S(10), .5)), track=.1)
    circle(ctx, cx, cy, 5, INK, .5 * ka * (1 - prog(t, S(10), .5)))
    kb = prog(t, S(11), .5)
    ctx.set_line_width(26); ctx.new_sub_path(); ctx.arc(cx, cy, R - 30, 0, 2 * PI)
    ctx.set_source_rgba(*RED, .18 * kb); ctx.stroke()
    text(ctx, "ATRÁS", BOLD, 30, cx, cy + R - 54, RED, kb, track=.1)
    text(ctx, f"v = {b:.2f}c".replace(".", ","), SANS, 40, cx, cy + R + 90, MUTED, ka)
    text(ctx, "visão de 360°: centro = frente, borda = atrás", SANS, 26, cx, cy + R + 136, MUTED, ka * .8)

random.seed(11)
HYD = [(random.uniform(0, 1), random.uniform(560, 1260), random.uniform(0, 1)) for _ in range(90)]
def scene_rad(ctx, t):                           # segs 12-14
    background(ctx, t)
    sx, sy = 430, 910
    fast = eio(prog(t, S(13), .8))
    danger = prog(t, S(14), .4)
    for u, y, ph in HYD:
        if fast <= 0:
            x = 120 + u * 860 + math.sin(t + ph * 6) * 6
            circle(ctx, x, y, 6, INK, .8 * prog(t, S(12), .4))
        else:
            v = 2.2 * fast
            x = W + 200 - ((u + t * v) % 1.3) * (W + 400)
            ln = 30 + 380 * fast
            if abs(y - sy) < 60 and x < sx + 170: continue
            rrect(ctx, x, y - 3, ln, 6, 3); fill(ctx, INK, .75)
    text(ctx, "~1 átomo de hidrogênio por cm³", SANS, 32, 540, 470, MUTED, prog(t, S(12) + .2, .3) * (1 - fast))
    hull = mix(INK, RED, danger * (0.6 + 0.4 * math.sin(t * 14)))
    ship(ctx, sx, sy, 1.0, flame=.5 + .1 * math.sin(t * 25), hull=hull)
    if fast > 0:
        random.seed(int(t * 30))
        for _ in range(int(14 * fast)):
            a = random.uniform(-1.3, 1.3); L = random.uniform(30, 110)
            x1 = sx + 165 + 10 * math.cos(a); y1 = sy + 40 * math.sin(a)
            ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_source_rgba(*(SOLAR if random.random() < .5 else RED), .9)
            ctx.move_to(x1, y1); ctx.line_to(x1 + L * math.cos(a), y1 + L * math.sin(a)); ctx.stroke()
        text(ctx, "RADIAÇÃO", DISP, 72, 540, 470, RED, prog(t, S(13) + .8, .3))
    if danger > 0:
        rr = 230 + 20 * math.sin(t * 8)
        ctx.set_line_width(10); ctx.new_sub_path(); ctx.arc(sx, sy, rr, 0, 2 * PI)
        ctx.set_source_rgba(*RED, .5 * danger); ctx.stroke()

def scene_trip(ctx, t):                          # segs 15-17
    background(ctx, t)
    y = 820; ax, bx = 150, 930
    ka = eo(prog(t, S(15), .5))
    circle(ctx, ax, y, 60 * ka, SOLAR); text(ctx, "SOL", BOLD, 30, ax, y + 110, MUTED, ka, track=.1)
    circle(ctx, bx, y, 30 * ka, RED); text(ctx, "PROXIMA", BOLD, 30, bx, y + 110, MUTED, ka, "r", .06)
    text(ctx, "CENTAURI", BOLD, 30, bx, y + 150, MUTED, ka, "r", .06)
    ctx.set_dash([10, 14]); ctx.set_line_width(4); ctx.set_source_rgba(*LINE, ka)
    ctx.move_to(ax + 70, y); ctx.line_to(bx - 40, y); ctx.stroke(); ctx.set_dash([])
    text(ctx, "4,24 anos-luz", SANS, 34, 540, y - 70, MUTED, ka)
    text(ctx, "99,99%", DISP, 120, 540, 520, BLUE, eo(prog(t, S(15) + (E(15) - S(15)) * .55, .4)))
    text(ctx, "DA VELOCIDADE DA LUZ", BOLD, 34, 540, 580, MUTED, eo(prog(t, S(15) + (E(15) - S(15)) * .55, .4)), track=.04)
    m = eio(prog(t, S(16), E(16) - S(16) + .3))
    ship(ctx, lerp(ax + 110, bx - 90, m), y, .38, flame=.4 if 0 < m < 1 else 0)
    kp = eo(prog(t, S(16) - .2, .4))
    rrect(ctx, 240, 1010, 600, 270, 16); fill(ctx, ORBIT, kp)
    d = int(round(22 * m))
    text(ctx, f"{d}", DISP, 150, 540, 1185, BLUE, kp)
    text(ctx, "DIAS NO SEU RELÓGIO", BOLD, 30, 540, 1245, INK, kp, track=.04)
    text(ctx, "γ ≈ 71: o tempo a bordo passa 71× mais devagar", SANS, 28, 540, 1340, MUTED, prog(t, S(17), .4))

def scene_return(ctx, t):                        # segs 18-20
    background(ctx, t)
    ka = eo(prog(t, S(18), .5))
    ctx.set_source_rgba(*LINE, ka); ctx.rectangle(540 - 2, 520, 4, 820); ctx.fill()
    text(ctx, "VOCÊ", BOLD, 40, 300, 560, BLUE, ka, track=.1)
    text(ctx, "TERRA", BOLD, 40, 780, 560, RED, ka, track=.1)
    step = eo(prog(t, S(18) + .1, .7))
    ship(ctx, 220, 1060, .45, a=ka)
    person(ctx, lerp(220, 320, step), 1060, 1.0 * back(prog(t, S(18) + .1, .5)))
    age = eio(prog(t, S(20) + .3, (E(20) - S(20)) * .8))
    circle(ctx, 780, 800, 70, BLUE, .25 * ka)
    person(ctx, 780, 1060, lerp(1.0, .93, age), body=mix(INK, MUTED, age * .4), hair=mix(RED, MUTED, age), a=ka, hunch=age)
    k1 = prog(t, S(19), .3); d = int(round(44 * eo(prog(t, S(19), .9))))
    text(ctx, f"{d}", DISP, 120, 300, 1230, BLUE, k1); text(ctx, "DIAS", BOLD, 34, 300, 1285, INK, k1, track=.06)
    k2 = prog(t, S(20), .3); y = 8.5 * eo(prog(t, S(20), 1.4))
    text(ctx, f"{y:.1f}".replace(".", ","), DISP, 120, 780, 1230, RED, k2); text(ctx, "ANOS", BOLD, 34, 780, 1285, INK, k2, track=.06)

def scene_end(ctx, t):                           # seg 21 + final
    background(ctx, t)
    k = eo(prog(t, S(21), .4))
    text(ctx, "VALERIA", DISP, 110, 540, 640, INK, k)
    text(ctx, "A PENA?", DISP, 110, 540, 770, BLUE, eo(prog(t, S(21) + .25, .4)))
    kl = back(prog(t, E(21) + .2, .6))
    if kl > 0:
        mark(ctx, 540 - 120 * kl, 900, 2 * kl, 1)
        text(ctx, "HYPER", DISP, 64, 540, 1230, INK, prog(t, E(21) + .4, .3))
        text(ctx, "HYPOTHESIS", LITE, 64, 540, 1310, INK, prog(t, E(21) + .5, .3))
        text(ctx, "@hyperhypothesis", SANS, 36, 540, 1390, MUTED, prog(t, E(21) + .8, .3))
        text(ctx, "Responde nos comentários.", SANS, 34, 540, 1470, BLUE, prog(t, E(21) + 1.1, .3))

SCENES = [(0, 1, scene_intro), (2, 4, scene_energy), (5, 5, scene_99), (6, 7, scene_mt), (8, 8, scene_strange),
          (9, 11, scene_sky), (12, 14, scene_rad), (15, 17, scene_trip), (18, 20, scene_return), (21, 21, scene_end)]

