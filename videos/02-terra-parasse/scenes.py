"""Cenas da Hipótese #02 — E se a Terra parasse de girar por 1 segundo?"""
import math, random
import cairocffi as cairo
from hh.core import *


# ---------------------------------------------------------------- peças
def globe(ctx, cx, cy, R, rot, a=1.0, band=0.0, eq=1.0):
    """Terra vista de lado: disco, latitudes (retas) e meridianos girando com `rot` (rad)."""
    if a <= 0: return
    circle(ctx, cx, cy, R, ORBIT, a)
    if band > 0:                                   # faixa |lat| < 43° (vento supersônico)
        h = R * math.sin(math.radians(43))
        ctx.save(); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.clip()
        ctx.rectangle(cx - R, cy - h, 2 * R, 2 * h); fill(ctx, BLUE, .28 * band * a)
        ctx.restore()
    ctx.set_line_width(3)
    for lat in (-60, -30, 30, 60):
        y = cy - R * math.sin(math.radians(lat)); w = R * math.cos(math.radians(lat))
        ctx.move_to(cx - w, y); ctx.line_to(cx + w, y); ctx.set_source_rgba(*LINE, a); ctx.stroke()
    for j in range(8):                             # meridianos: só a metade da frente
        lam = rot + j * PI / 4
        s = math.sin(lam)
        if math.cos(lam) < 0: continue
        ctx.move_to(cx, cy - R)
        for i in range(1, 41):
            phi = -PI / 2 + PI * i / 40
            ctx.line_to(cx + R * math.cos(phi) * s, cy + R * math.sin(phi))
        ctx.set_source_rgba(*LINE, a); ctx.stroke()
    if eq > 0:
        ctx.set_line_width(6); ctx.move_to(cx - R, cy); ctx.line_to(cx + R, cy)
        ctx.set_source_rgba(*BLUE, a * eq); ctx.stroke()
    ctx.set_line_width(5); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.set_source_rgba(*MUTED, .5 * a); ctx.stroke()


def arrow(ctx, x1, y1, x2, y2, col, a=1.0, w=10, head=34):
    if a <= 0: return
    ang = math.atan2(y2 - y1, x2 - x1); L = math.hypot(x2 - x1, y2 - y1)
    if L < 2: return
    ctx.save(); ctx.translate(x1, y1); ctx.rotate(ang)
    hl = min(head, L * .6)
    rrect(ctx, 0, -w / 2, L - hl * .8, w, w / 2); fill(ctx, col, a)
    ctx.move_to(L, 0); ctx.line_to(L - hl, -hl * .62); ctx.line_to(L - hl, hl * .62); ctx.close_path(); fill(ctx, col, a)
    ctx.restore()


def spin_arrow(ctx, cx, cy, R, t, a=1.0, col=BLUE):
    """Seta curva por cima do globo, de oeste para leste (→)."""
    if a <= 0: return
    ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    a0, a1 = PI * 1.22, PI * 1.78
    ctx.new_sub_path(); ctx.arc(cx, cy, R + 60, a0, a1); ctx.set_source_rgba(*col, a); ctx.stroke()
    ex, ey = cx + (R + 60) * math.cos(a1), cy + (R + 60) * math.sin(a1)
    tang = a1 + PI / 2
    ctx.save(); ctx.translate(ex, ey); ctx.rotate(tang)
    ctx.move_to(22, 0); ctx.line_to(-14, -20); ctx.line_to(-14, 20); ctx.close_path(); fill(ctx, col, a); ctx.restore()


def ground(ctx, y, off, col=LINE, a=1.0):
    """Chão com marcas que andam (off em px)."""
    rrect(ctx, 0, y, W, 14, 7); fill(ctx, col, a)
    for i in range(-1, 14):
        x = (i * 96 + off) % (W + 96) - 48
        rrect(ctx, x, y + 34, 48, 10, 5); fill(ctx, col, a * .7)


def trails(ctx, x, y, k, a=1.0):
    """Rastros de velocidade em redshift, sempre atrás (à esquerda)."""
    for j, (dy, ln) in enumerate([(-150, 220), (-90, 360), (-30, 260)]):
        L = ln * k; rrect(ctx, x - 70 - L, y + dy - 5, L, 10, 5); fill(ctx, RED, a * (.85 - j * .15))


# ---------------------------------------------------------------- cenas
def scene_intro(ctx, t):                           # seg 0
    background(ctx, t)
    cx, cy, R = 540, 1180, 300
    kg = back(prog(t, S(0), .6))
    stop = prog(t, S(0) + (E(0) - S(0)) * .6, .5)  # "por um segundo só" -> a Terra trava
    rot = t * 1.6 * (1 - eo(stop)) + (S(0) + (E(0) - S(0)) * .6) * 1.6 * eo(stop)
    jit = 8 * math.sin(t * 60) * (stop * (1 - prog(t, S(0) + (E(0) - S(0)) * .6 + .5, .6)))
    globe(ctx, cx + jit, cy, R * kg, rot)
    spin_arrow(ctx, cx + jit, cy, R * kg, t, a=kg * (1 - stop), col=BLUE)
    spin_arrow(ctx, cx + jit, cy, R * kg, t, a=kg * stop, col=RED)
    lines = [("E SE A TERRA", INK, 88), ("PARASSE", INK, 104), ("DE GIRAR...", INK, 104)]
    for j, (ln, c, sz) in enumerate(lines):
        kk = prog(t, S(0) + j * .18, .35)
        if kk > 0: text_fit(ctx, ln, DISP, sz, 540, 400 + j * 118 + 30 * (1 - eo(kk)), c, eo(kk))
    k2 = prog(t, S(0) + (E(0) - S(0)) * .55, .35)
    if k2 > 0: text_fit(ctx, "POR 1 SEGUNDO?", DISP, 84, 540, 760 + 30 * (1 - eo(k2)), BLUE, eo(k2))


def scene_spin(ctx, t):                            # segs 1-2
    background(ctx, t)
    cx, cy, R = 540, 2550, 1700                    # um pedaço enorme do planeta embaixo
    rot = t * .35
    k = eo(prog(t, S(1), .5))
    ctx.save(); ctx.translate(0, 0)
    circle(ctx, cx, cy, R, ORBIT, k)
    ctx.set_line_width(5); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.set_source_rgba(*MUTED, .5 * k); ctx.stroke()
    for i in range(36):                            # marcas na superfície girando
        ang = -PI / 2 + ((i / 36) * 2 * PI + rot) % (2 * PI) - PI
        x, y = cx + (R - 40) * math.cos(ang), cy + (R - 40) * math.sin(ang)
        circle(ctx, x, y, 9, LINE, k)
    ctx.restore()
    yb = cy - R                                    # topo do planeta
    kp = back(prog(t, S(1) + .2, .5))
    person(ctx, 540, yb + 4, 1.15 * kp)
    kt = eo(prog(t, S(1) + .3, .4))
    text(ctx, "você não sente nada", SANS, 40, 540, 560, MUTED, kt * (1 - prog(t, S(2), .3)))
    kg = prog(t, S(2), .4)
    if kg > 0:
        # setas: chão e você andando juntos para o leste
        arrow(ctx, 330, yb + 70, 330 + 420 * eo(kg), yb + 70, BLUE, kg)
        arrow(ctx, 640, yb - 330, 640 + 220 * eo(kg), yb - 330, BLUE, kg)
        text(ctx, "VOCÊ", BOLD, 30, 640, yb - 290, BLUE, kg, "l", .08)
        text(ctx, "CHÃO", BOLD, 30, 330, yb + 140, BLUE, kg, "l", .08)
        text(ctx, "JUNTOS", DISP, 90, 540, 420, BLUE, eo(prog(t, S(2) + (E(2) - S(2)) * .5, .3)))


def scene_stop(ctx, t):                            # segs 3-5
    background(ctx, t)
    gy = 1180
    stop = t >= S(3) + .7
    off = (S(3) + .7) * 220 if stop else t * 220
    ground(ctx, gy, off, col=RED if stop else LINE)
    kt = prog(t, S(3), .25)
    text(ctx, "O CHÃO PARA.", DISP, 86, 540, 520, RED, kt)
    text(ctx, "VOCÊ NÃO.", DISP, 86, 540, 640, BLUE, prog(t, S(3) + (E(3) - S(3)) * .55, .25))
    # você: parado até o chão travar, depois desliza para o leste
    slide = 0.0
    if stop: slide = (t - (S(3) + .7)) * 70
    if t >= S(5): slide += (t - S(5)) ** 2 * 70
    px = 380 + slide
    if t < S(4):
        person(ctx, px, gy, 1.1)
        if stop: trails(ctx, px, gy, prog(t, S(3) + .7, .4), .9)
    elif t < S(5):
        person(ctx, px, gy, 1.1)
        trails(ctx, px, gy, 1, .9)
        kg = eo(prog(t, S(4), .4)); ks = eo(prog(t, S(4) + (E(4) - S(4)) * .5, .4))
        arrow(ctx, px + 120, gy - 420, px + 120, gy - 420 + 260 * kg, BLUE, kg)
        text(ctx, "gravidade", SANS, 34, px + 150, gy - 300, BLUE, kg, "l")
        # para o lado: nada segura
        ctx.set_dash([16, 14]); ctx.set_line_width(6); ctx.set_source_rgba(*MUTED, ks)
        ctx.move_to(px - 330, gy - 300); ctx.line_to(px - 90, gy - 300); ctx.stroke(); ctx.set_dash([])
        text(ctx, "pro lado: nada", SANS, 34, px - 210, gy - 340, MUTED, ks)
    else:
        if px < W + 200:
            person(ctx, px, gy, 1.1, hunch=-.6)
            trails(ctx, px, gy, 1 + prog(t, S(5), 1), 1)
        kl = eo(prog(t, S(5) + .2, .4))
        text(ctx, "LESTE", DISP, 72, 540, 900, INK, kl)
        arrow(ctx, 380, 980, 380 + 320 * kl, 980, INK, kl, w=12)


def scene_hero(ctx, t):                            # segs 6-7
    background(ctx, t, drift=t * .3)
    up = eio(prog(t, S(7), .6))
    kn = eo(prog(t, S(6), 1.1)); n = int(round(1670 * kn))
    num = f"{n:,}".replace(",", ".")
    ya = prog(t, S(6), .12)
    sc = lerp(.9, 1, back(prog(t, S(6), .4)))
    text(ctx, num, DISP, lerp(190, 120, up) * sc, 540, lerp(900, 560, up), SOLAR, ya)
    text(ctx, "KM/H", BOLD, lerp(56, 40, up), 540, lerp(990, 625, up), INK, ya, track=.08)
    ke = prog(t, S(6) + (E(6) - S(6)) * .55, .3)
    text(ctx, "no equador", SANS, lerp(40, 32, up), 540, lerp(1050, 675, up), MUTED, ke)
    text(ctx, "465 m/s · 2π × 6.378 km ÷ 23 h 56 min", SANS, 28, 540, 1120, MUTED, ke * (1 - up))
    if t >= S(7):
        x0, wmax = 140, 800
        k1 = eo(prog(t, S(7) + .1, .6)); k2 = eo(prog(t, S(7) + .4, .9))
        # avião ~900 km/h
        y1 = 860
        text(ctx, "AVIÃO", BOLD, 30, x0, y1 - 24, MUTED, k1, "l", .08)
        rrect(ctx, x0, y1, wmax * 900 / 1670 * k1, 56, 14); fill(ctx, MUTED, k1)
        text(ctx, "~900 km/h", SANS, 34, x0 + wmax * 900 / 1670 * k1 + 20, y1 + 40, MUTED, k1, "l")
        y2 = 1030
        text(ctx, "VOCÊ", BOLD, 30, x0, y2 - 24, SOLAR, k2, "l", .08)
        rrect(ctx, x0, y2, wmax * k2, 56, 14); fill(ctx, SOLAR, k2)
        person(ctx, x0 + wmax * k2, y2 - 6, .32, a=k2)
        text(ctx, "QUASE O DOBRO", DISP, 64, 540, 1250, BLUE, eo(prog(t, S(7) + (E(7) - S(7)) * .55, .3)))


def scene_meio(ctx, t):                            # seg 8
    background(ctx, t)
    y = 1000; x0, x1 = 96, 984
    ka = eo(prog(t, S(8), .4))
    # 4,4 campos de futebol (105 m) = 465 m
    fw = (x1 - x0) * 105 / 465
    for i in range(5):
        w = fw if i < 4 else (x1 - x0) - 4 * fw
        xx = x0 + i * fw
        rrect(ctx, xx + 4, y - 120, w - 8, 120, 10); fill(ctx, ORBIT, ka)
        ctx.set_line_width(3); ctx.set_source_rgba(*LINE, ka)
        if i < 4:
            ctx.move_to(xx + fw / 2, y - 120); ctx.line_to(xx + fw / 2, y); ctx.stroke()
            ctx.new_sub_path(); ctx.arc(xx + fw / 2, y - 60, 22, 0, 2 * PI); ctx.stroke()
    text(ctx, "4,4 campos de futebol", SANS, 32, 540, y + 70, MUTED, ka)
    m = eio(prog(t, S(8) + .2, (E(8) - S(8)) * .55))
    px = lerp(x0 + 30, x1 - 60, m)
    hit = prog(t, S(8) + .2 + (E(8) - S(8)) * .55, .2)
    # parede no fim
    rrect(ctx, x1 - 30, y - 330, 34, 330, 6); fill(ctx, INK, ka)
    if hit > 0:
        sq = 1 - .25 * math.sin(PI * hit)
        ctx.save(); ctx.translate(px, y); ctx.scale(sq, 1); person(ctx, 0, 0, .7); ctx.restore()
        for j in range(8):
            ang = -PI + j * PI / 7
            L = 70 * hit
            ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*SOLAR, 1 - hit * .6)
            ctx.move_to(x1 - 40 + 40 * math.cos(ang), y - 180 + 40 * math.sin(ang))
            ctx.line_to(x1 - 40 + (40 + L) * math.cos(ang), y - 180 + (40 + L) * math.sin(ang)); ctx.stroke()
    else:
        person(ctx, px, y, .7, hunch=-.5)
        if 0 < m < 1: trails(ctx, px, y - 40, .6, .9)
    d = int(round(465 * m))
    text(ctx, f"{d} m", DISP, 150, 540, 640, BLUE, prog(t, S(8) + .1, .2))
    text(ctx, "EM 1 SEGUNDO", BOLD, 36, 540, 710, INK, prog(t, S(8) + .1, .2), track=.08)


def scene_air(ctx, t):                             # segs 9-10
    background(ctx, t)
    cx, cy, R = 540, 900, 330
    kb = eo(prog(t, S(9) + .3, .6))
    sea = t >= S(10)
    ka = 1 - eo(prog(t, S(10), .3))
    if ka > 0:
        globe(ctx, cx, cy, R, 1.0, a=ka, band=kb)
        if kb > 0:
            random.seed(int(t * 20) % 1000)
            for i in range(16):                    # rajadas de vento para o leste, rastro atrás
                yy = cy + (i / 15 - .5) * 2 * R * math.sin(math.radians(43)) * .92
                ww = math.sqrt(max(0, R * R - (yy - cy) ** 2))
                u = ((t * 1.6 + i * .37) % 1)
                xx = cx - ww + 2 * ww * u
                rrect(ctx, xx - 90, yy - 3, 90, 6, 3); fill(ctx, INK, .55 * kb * ka * math.sin(PI * u))
        text(ctx, "VENTO", DISP, 80, 540, 380, BLUE, kb * ka)
        text(ctx, "SUPERSÔNICO", DISP, 80, 540, 480, BLUE, kb * ka)
        text(ctx, "68% da superfície (até ~43° de latitude)", SANS, 32, 540, cy + R + 80, MUTED, kb * ka)
        text(ctx, "Mach 1,4 no equador", SANS, 32, 540, cy + R + 130, MUTED, kb * ka)
    if sea:
        k = eo(prog(t, S(10) + .1, .4))
        gy = 1000
        # terra (direita) e oceano (esquerda) avançando para o leste
        rrect(ctx, 560, gy - 60, 620, 360, 10); fill(ctx, ORBIT, k)
        ctx.move_to(560, gy - 60); ctx.line_to(1080, gy - 60); ctx.set_line_width(4); ctx.set_source_rgba(*LINE, k); ctx.stroke()
        adv = eio(prog(t, S(10) + .3, (E(10) - S(10)) * .9))
        front = 560 + 330 * adv
        ctx.move_to(-20, gy)
        ctx.line_to(front - 120, gy)
        ctx.curve_to(front - 40, gy - 40 - 160 * adv, front + 20, gy - 160 * adv, front + 60, gy - 120 * adv)
        ctx.curve_to(front + 40, gy - 40, front + 10, gy + 20, front, gy + 40)
        ctx.line_to(front, gy + 300); ctx.line_to(-20, gy + 300); ctx.close_path(); fill(ctx, BLUE, .85 * k)
        text(ctx, "OCEANO", BOLD, 34, 240, gy + 120, VOID, k, track=.08)
        text(ctx, "COSTA", BOLD, 34, 860, gy + 120, MUTED, k, track=.08)
        arrow(ctx, 200, 640, 200 + 300 * k, 640, BLUE, k)
        text(ctx, "~465 m em 1 s", SANS, 36, 540, 580, MUTED, k)


def scene_building(ctx, t):                        # seg 11
    background(ctx, t)
    gy = 1260
    ground(ctx, gy, 0, col=RED)
    k = back(prog(t, S(11), .5))
    sh = eio(prog(t, S(11) + (E(11) - S(11)) * .45, .9))
    # prédio em fatias: a base fica, cada andar de cima vai mais para o leste
    n, hh_, bw = 9, 70, 240
    for i in range(n):
        f = (i / (n - 1)) ** 1.6
        x = 540 - bw / 2 + 170 * sh * f
        y = gy - (i + 1) * hh_ * k
        rrect(ctx, x, y, bw, hh_ * k - 6, 6); fill(ctx, INK, 1)
        for wx in range(3):
            rrect(ctx, x + 30 + wx * 70, y + 18 * k, 40, 26 * k, 4); fill(ctx, VOID, 1)
    if sh > 0: trails(ctx, 540 - bw / 2 + 170 * sh + 50, gy - n * hh_ + 160, sh * .8, .9)
    kb = prog(t, S(11) + .1, .3); kt = prog(t, S(11) + (E(11) - S(11)) * .45, .3)
    text(ctx, "A BASE PARA.", DISP, 72, 540, 450, RED, kb)
    text(ctx, "O TOPO, NÃO.", DISP, 72, 540, 560, BLUE, kt)


def scene_restart(ctx, t):                         # segs 12-13
    background(ctx, t)
    cx, cy, R = 540, 1050, 300
    st = prog(t, S(12) + (E(12) - S(12)) * .5, .4)
    rot = 1.0 + max(0, t - (S(12) + (E(12) - S(12)) * .5)) * 1.6
    globe(ctx, cx, cy, R, rot, a=1)
    spin_arrow(ctx, cx, cy, R, t, a=eo(st), col=BLUE)
    k1 = prog(t, S(12), .3)
    text(ctx, "+1 s", DISP, 120, 540, 500, SOLAR, k1)
    text(ctx, "A TERRA VOLTA A GIRAR", BOLD, 40, 540, 580, INK, prog(t, S(12) + (E(12) - S(12)) * .4, .3), track=.03)
    if t >= S(13):
        k = prog(t, S(13) + .2, .2)
        j = (math.sin(t * 47) * 14 + math.sin(t * 91) * 8) * (1 - prog(t, S(13) + .5, 1.2))
        text(ctx, "TUDO LEVA O", BOLD, 44, 540, 1440, INK, k, track=.04)
        for dx, c, al in ((-j, RED, .85), (j, BLUE, .85), (0, INK, 1)):
            text_fit(ctx, "TRANCO", DISP, 150, 540 + dx, 1600, c, al * k)
        text(ctx, "DE NOVO", BOLD, 44, 540, 1680, INK, k, track=.04)


def scene_lat(ctx, t):                             # segs 14-15
    background(ctx, t)
    cx, cy, R = 330, 900, 250
    globe(ctx, cx, cy, R, t * .8, a=eo(prog(t, S(14), .4)))
    #       lat     nome         km/h  cor    y do rótulo
    rows = [(90, "POLO", 0, MUTED, 640), (0, "EQUADOR", 1670, SOLAR, 860), (-23.55, "SÃO PAULO", 1530, BLUE, 1100)]
    x0 = 640
    for idx, (lat, name, v, col, ly) in enumerate(rows):
        tk = S(14) if idx == 0 else S(15) + (idx - 1) * .6
        k = eo(prog(t, tk, .6))
        if k <= 0: continue
        yy = cy - R * math.sin(math.radians(lat))
        xx = cx + R * math.cos(math.radians(lat)) * .25
        circle(ctx, xx, yy, 14, col, k)
        ctx.set_dash([8, 10]); ctx.set_line_width(3); ctx.set_source_rgba(*col, .6 * k)
        ctx.move_to(xx + 18, yy); ctx.line_to(x0 - 60, yy); ctx.line_to(x0 - 20, ly + 10); ctx.stroke(); ctx.set_dash([])
        text(ctx, name, BOLD, 28, x0, ly - 30, col, k, "l", .06)
        lab = f"{int(round(v * k)):,}".replace(",", ".")
        text(ctx, lab, DISP, 72, x0, ly + 46, col, k, "l")
        text(ctx, "km/h", SANS, 28, x0 + DISP.width(lab, 72) + 14, ly + 46, MUTED, k, "l")
    if t >= S(15):
        kp = back(prog(t, S(15) + .2, .5))
        yy = cy + R * math.sin(math.radians(23.55)); xx = cx + R * math.cos(math.radians(23.55)) * .25
        person(ctx, xx, yy - 18, .28 * kp)
        text(ctx, "VOCÊ, AQUI", BOLD, 26, x0, 1200, BLUE, prog(t, S(15) + 1.2, .4), "l", .08)


def scene_end(ctx, t):                             # seg 16 + final
    background(ctx, t)
    k = eo(prog(t, S(16), .4))
    text(ctx, "ONDE VOCÊ", DISP, 100, 540, 600, INK, k)
    text(ctx, "QUERIA ESTAR", DISP, 92, 540, 720, INK, eo(prog(t, S(16) + .2, .4)))
    text(ctx, "NESSE SEGUNDO?", DISP, 84, 540, 840, BLUE, eo(prog(t, S(16) + .4, .4)))
    kl = back(prog(t, E(16) + .2, .6))
    if kl > 0:
        mark(ctx, 540 - 120 * kl, 960, 2 * kl, 1)
        text(ctx, "HYPER", DISP, 64, 540, 1290, INK, prog(t, E(16) + .4, .3))
        text(ctx, "HYPOTHESIS", LITE, 64, 540, 1370, INK, prog(t, E(16) + .5, .3))
        text(ctx, "@hyperhypothesis", SANS, 36, 540, 1450, MUTED, prog(t, E(16) + .8, .3))
        text(ctx, "Responde nos comentários.", SANS, 34, 540, 1530, BLUE, prog(t, E(16) + 1.1, .3))


SCENES = [(0, 0, scene_intro), (1, 2, scene_spin), (3, 5, scene_stop), (6, 7, scene_hero), (8, 8, scene_meio),
          (9, 10, scene_air), (11, 11, scene_building), (12, 13, scene_restart), (14, 15, scene_lat), (16, 16, scene_end)]
