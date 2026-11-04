"""Cenas da Hipótese #02 — E se a Terra parasse de girar por 1 segundo? (motor v2)"""
import math, random
import cairocffi as cairo
from hh.fx import *

GREEN = hx("2E6B5E")                       # copa das árvores (mesma do fx.tree)


def mid(i, f): return S(i) + (E(i) - S(i)) * f          # instante a uma fração da frase i


# ---------------------------------------------------------------- peças locais
def spin_arrow(ctx, cx, cy, R, a=1.0, col=BLUE):
    """Seta curva por cima do globo, de oeste para leste (→)."""
    if a <= 0: return
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    a0, a1 = PI * 1.24, PI * 1.76
    ctx.new_sub_path(); ctx.arc(cx, cy, R + 70, a0, a1); ctx.set_source_rgba(*col, a); ctx.stroke()
    ex, ey = cx + (R + 70) * math.cos(a1), cy + (R + 70) * math.sin(a1)
    ctx.save(); ctx.translate(ex, ey); ctx.rotate(a1 + PI / 2)
    ctx.move_to(26, 0); ctx.line_to(-16, -24); ctx.line_to(-16, 24); ctx.close_path(); fill(ctx, col, a); ctx.restore()


def street(ctx, y, off, a=1.0, stopped=False, seed=5):
    """Rua com casas, árvores e postes que andam com `off` (px)."""
    rnd = random.Random(seed)
    items = []
    for i in range(10):
        kind = ("house", "tree", "lamp", "buildings", "tree")[i % 5]
        items.append((i * 230 + rnd.randint(-30, 30), kind))
    span = 10 * 230
    for x0, kind in items:
        x = (x0 + off) % span - 200
        if x < -260 or x > W + 260: continue
        if kind == "tree": tree(ctx, x, y, 1.1, a=a)
        elif kind == "lamp":
            rrect(ctx, x - 5, y - 210, 10, 210, 5); fill(ctx, MUTED, a)
            rrect(ctx, x - 5, y - 214, 60, 12, 6); fill(ctx, MUTED, a); circle(ctx, x + 52, y - 196, 12, SOLAR, a * .9)
        elif kind == "house": icon(ctx, "house", x, y - 92, 200, SOLAR, a, "duotone")
        else: icon(ctx, "buildings", x, y - 120, 250, MUTED, a, "duotone")
    rrect(ctx, -20, y, W + 40, 18, 9); fill(ctx, RED if stopped else LINE, a)       # calçada
    rrect(ctx, -20, y + 18, W + 40, 120, 0); fill(ctx, ORBIT, a)                       # asfalto
    for i in range(-1, 14):                                                            # faixas
        x = (i * 140 + off) % (W + 140) - 70
        rrect(ctx, x, y + 70, 70, 12, 6); fill(ctx, MUTED, a * .6)


# ---------------------------------------------------------------- cenas
def scene_intro(ctx, t):                           # seg 0 (sem legenda)
    background(ctx, t)
    cx, cy, R = 540, 1200, 330
    kg = back(prog(t, S(0), .6))
    tl = mid(0, .6)
    lon0 = -20 - (min(t, tl) * 55)                  # gira de oeste p/ leste e TRAVA em tl
    globe(ctx, cx, cy, R * kg, lon0=lon0, lat0=18)
    globe_line(ctx, 0, lon0, 18, R * kg, cx, cy, BLUE, .9 * kg)
    stop = prog(t, tl, .15)
    spin_arrow(ctx, cx, cy, R * kg, a=kg * (1 - stop), col=BLUE)
    spin_arrow(ctx, cx, cy, R * kg, a=kg * stop, col=RED)
    if stop > 0:
        icon(ctx, "lock-simple", cx + R * .78, cy - R * .78, 120 * back(prog(t, tl, .35)), RED, 1, "fill")
    for j, (ln, sz) in enumerate([("E SE A TERRA", 88), ("PARASSE", 104), ("DE GIRAR...", 104)]):
        kk = prog(t, S(0) + j * .18, .35)
        if kk > 0: text_fit(ctx, ln, DISP, sz, 540, 380 + j * 118 + 30 * (1 - eo(kk)), INK, eo(kk))
    k2 = prog(t, mid(0, .55), .35)
    if k2 > 0: text_fit(ctx, "POR 1 SEGUNDO?", DISP, 84, 540, 740 + 30 * (1 - eo(k2)), BLUE, eo(k2))


def scene_spin(ctx, t):                            # segs 1-2
    background(ctx, t)
    cx, cy, R = 540, 2950, 1800                      # um pedaço enorme do planeta embaixo; topo em y=1150
    k = eo(prog(t, S(1), .5))
    icon(ctx, "sun", 860, 560, 170, SOLAR, k, "duotone")
    for c in (0, 1, 2):                              # nuvens no céu, devagar
        cloud(ctx, (180 + c * 380 + t * 25) % (W + 300) - 150, 820 - c * 90, .8 - c * .15, MUTED, .45 * k)
    circle(ctx, cx, cy, R, ORBIT, k)
    circle(ctx, cx, cy, R - 70, hx("111A28"), k)
    rot = t * .045                                   # paisagem girando junto
    for i in range(28):
        ang = -PI / 2 + ((i / 28) * 2 * PI + rot) % (2 * PI) - PI
        if abs(ang + PI / 2) > .55: continue
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        ctx.save(); ctx.translate(x, y); ctx.rotate(ang + PI / 2)
        kind = i % 4
        if kind == 0: tree(ctx, 0, 0, .9, a=k)
        elif kind == 1: icon(ctx, "house", 0, -70, 150, SOLAR, k, "duotone")
        elif kind == 2: building(ctx, -55, 0, 110, 260, a=k, seed=i)
        else: tree(ctx, 0, 0, .7, a=k)
        ctx.restore()
    yb = cy - R
    person(ctx, 540, yb, 1.15 * back(prog(t, S(1) + .2, .5)), mood="happy" if t < S(2) else None)
    text(ctx, "você não sente nada", SANS, 44, 540, 430, MUTED, eo(prog(t, S(1) + .3, .4)) * (1 - prog(t, S(2), .3)))
    kg = prog(t, S(2), .4)
    if kg > 0:
        arrow(ctx, 250, yb + 90, 250 + 440 * eo(kg), yb + 90, BLUE, kg, w=14, head=42)
        arrow(ctx, 660, yb - 330, 660 + 240 * eo(kg), yb - 330, BLUE, kg, w=14, head=42)
        text(ctx, "VOCÊ", BOLD, 40, 660, yb - 370, BLUE, kg, "l", .08)
        wl = text(ctx, "CHÃO", BOLD, 40, 250, yb + 170, BLUE, kg, "l", .08)
        text(ctx, "· 1.670 km/h", BOLD, 40, 250 + wl + 16, yb + 170, MUTED, kg, "l", .02)
        text(ctx, "JUNTOS", DISP, 96, 540, 420, BLUE, eo(prog(t, mid(2, .5), .3)))


def scene_stop(ctx, t):                            # segs 3-5
    background(ctx, t)
    gy = 1150; ts = S(3) + .7
    stopped = t >= ts
    off = (ts if stopped else t) * 420
    flash = 1 - prog(t, ts, .35) if stopped else 0
    street(ctx, gy, off, stopped=stopped)
    if flash > 0: ctx.rectangle(0, 0, W, H); fill(ctx, RED, .18 * flash)
    text(ctx, "O CHÃO PARA.", DISP, 86, 540, 460, RED, prog(t, S(3), .25))
    text(ctx, "VOCÊ NÃO.", DISP, 86, 540, 580, BLUE, prog(t, mid(3, .55), .25))
    slide = 0.0
    if stopped: slide = (t - ts) * 60
    if t >= S(5): slide += (t - S(5)) ** 2 * 90
    px = 380 + slide
    arms = (2.4, -2.4) if stopped else (.22, -.22)
    if px < W + 200:
        person(ctx, px, gy, 1.15, arms=arms, mood="wow" if stopped else None, hunch=-.5 if stopped else 0)
        if stopped: trails(ctx, px, gy - 20, clamp(prog(t, ts, .4) + prog(t, S(5), 1)), .9)
    if S(4) <= t < S(5):
        kg = eo(prog(t, S(4), .4)); ks = eo(prog(t, mid(4, .5), .4))
        arrow(ctx, px + 140, gy - 480, px + 140, gy - 480 + 280 * kg, BLUE, kg, w=14, head=40)
        text(ctx, "gravidade", SANS, 40, px + 170, gy - 340, BLUE, kg, "l")
        ctx.set_dash([18, 14]); ctx.set_line_width(7); ctx.set_source_rgba(*MUTED, ks)
        ctx.move_to(px - 340, gy - 320); ctx.line_to(px - 90, gy - 320); ctx.stroke(); ctx.set_dash([])
        text(ctx, "pro lado: nada", SANS, 40, px - 215, gy - 360, MUTED, ks)
    if t >= S(5):
        kl = eo(prog(t, S(5) + .2, .4))
        text(ctx, "LESTE", DISP, 80, 540, 800, INK, kl)
        arrow(ctx, 340, 870, 340 + 400 * kl, 870, INK, kl, w=14, head=42)


def scene_hero(ctx, t):                            # segs 6 (sem legenda) - 7
    background(ctx, t, drift=t * .3)
    up = eio(prog(t, S(7), .6))
    kn = eo(prog(t, S(6), 1.1)); ya = prog(t, S(6), .12)
    sc = lerp(.9, 1, back(prog(t, S(6), .4)))
    text(ctx, counter(1670 * kn), DISP, lerp(200, 120, up) * sc, 540, lerp(780, 500, up), SOLAR, ya)
    text(ctx, "KM/H", BOLD, lerp(60, 42, up), 540, lerp(870, 565, up), INK, ya, track=.08)
    ke = prog(t, mid(6, .55), .3)
    text(ctx, "NO EQUADOR", BOLD, lerp(44, 38, up), 540, lerp(940, 620, up), BLUE, ke, track=.06)
    if up < 1:                                       # globo com o equador acendendo
        cx, cy, R = 540, 1380, 300
        lon0 = -40 - t * 20; a = (1 - up) * eo(prog(t, S(6), .5))
        globe(ctx, cx, cy, R, lon0=lon0, lat0=20, a=a)
        globe_line(ctx, 0, lon0, 20, R, cx, cy, SOLAR, a * ke, w=9)
        text(ctx, "465 metros por segundo", SANS, 40, 540, 1020, MUTED, ke * (1 - up))
    if t >= S(7):
        x0, wmax = 120, 760
        k1 = eo(prog(t, S(7) + .1, .6)); k2 = eo(prog(t, S(7) + .4, .9))
        for y, lab, v, col, k, ic in ((820, "AVIÃO", 900, MUTED, k1, "airplane-tilt"), (1040, "VOCÊ", 1670, SOLAR, k2, None)):
            text(ctx, lab, BOLD, 40, x0, y - 26, col, k, "l", .08)
            L = wmax * v / 1670 * k
            rrect(ctx, x0, y, max(1, L), 64, 16); fill(ctx, col, k)
            if ic: icon(ctx, ic, x0 + L + 60, y + 32, 96, INK, k, "fill", rot=.75)
            else: person(ctx, x0 + L + 40, y + 60, .42, a=k, arms=(2.3, -2.3), mood="wow")
            text(ctx, f"{counter(v)} km/h", SANS, 40, x0 + 20, y + 120, MUTED if col == MUTED else SOLAR, k, "l")
        text(ctx, "QUASE O DOBRO", DISP, 72, 540, 1300, BLUE, eo(prog(t, mid(7, .55), .3)))


def scene_meio(ctx, t):                            # seg 8
    background(ctx, t)
    y = 1080; x0, x1 = 60, 900
    ka = eo(prog(t, S(8), .4))
    fw = (x1 - x0) * 105 / 465                       # 4,4 campos de 105 m = 465 m
    for i in range(5):
        w = fw if i < 4 else (x1 - x0) - 4 * fw; xx = x0 + i * fw
        rrect(ctx, xx + 4, y - 150, w - 8, 150, 10); fill(ctx, GREEN, ka * .85)
        ctx.set_line_width(4); ctx.set_source_rgba(*INK, ka * .5)
        rrect(ctx, xx + 16, y - 138, w - 32, 126, 4); ctx.stroke()
        if i < 4:
            ctx.move_to(xx + fw / 2, y - 138); ctx.line_to(xx + fw / 2, y - 12); ctx.stroke()
            ctx.new_sub_path(); ctx.arc(xx + fw / 2, y - 75, 24, 0, 2 * PI); ctx.stroke()
    text(ctx, "4,4 campos de futebol", SANS, 40, 480, y + 70, MUTED, ka)
    m = eio(prog(t, S(8) + .2, (E(8) - S(8)) * .55)); th = S(8) + .2 + (E(8) - S(8)) * .55
    hit = prog(t, th, .45)
    building(ctx, x1 + 10, y, 150, 520, col=ORBIT, a=ka, seed=8)
    px = lerp(x0 + 30, x1 - 50, m)
    if t >= th:
        sq = 1 - .3 * math.sin(PI * min(1, hit * 2))
        ctx.save(); ctx.translate(px, y); ctx.scale(sq, 1); person(ctx, 0, 0, .75, mood="scared", arms=(1.2, -1.2)); ctx.restore()
        burst(ctx, x1, y - 220, hit, SOLAR, n=12, r0=30, r1=160, w=8)
        debris(ctx, x1 + 20, y - 300, prog(t, th, 1.2), n=16, col=MUTED)
    else:
        person(ctx, px, y, .75, hunch=-.5, arms=(2.4, -2.4), mood="wow")
        if 0 < m < 1: trails(ctx, px, y - 60, .7, .9)
    text(ctx, f"{int(round(465 * m))} m", DISP, 150, 540, 600, BLUE, prog(t, S(8) + .1, .2))
    text(ctx, "EM 1 SEGUNDO", BOLD, 40, 540, 675, INK, prog(t, S(8) + .1, .2), track=.08)


def scene_air(ctx, t):                             # segs 9-10
    background(ctx, t)
    if t < S(10):
        cx, cy, R = 540, 860, 330
        kb = eo(prog(t, S(9) + .3, .6)); lon0 = 10
        globe(ctx, cx, cy, R, lon0=lon0, lat0=12)
        globe_band(ctx, 42, lon0, 12, R, cx, cy, BLUE, .30 * kb)
        if kb > 0:                                  # rajadas e nuvens para o leste
            for i in range(14):
                yy = cy + (i / 13 - .5) * 2 * R * .62
                u = (t * 1.4 + i * .37) % 1
                xx = -100 + (W + 200) * u
                rrect(ctx, xx - 140, yy - 4, 140, 8, 4); fill(ctx, INK, .6 * kb * math.sin(PI * u))
            for c in range(3):
                u = (t * .9 + c * .33) % 1
                cloud(ctx, -150 + (W + 300) * u, cy - 120 + c * 120, .55, INK, .55 * kb * math.sin(PI * u))
        text(ctx, "VENTO", DISP, 84, 540, 360, BLUE, kb)
        text(ctx, "SUPERSÔNICO", DISP, 84, 540, 460, BLUE, kb)
        text(ctx, "2/3 da superfície do planeta", SANS, 40, 540, cy + R + 85, MUTED, kb)
        text(ctx, "Mach 1,4 no equador", SANS, 40, 540, cy + R + 140, MUTED, kb)
    else:
        k = eo(prog(t, S(10) + .05, .4)); gy = 1250
        adv = eio(prog(t, S(10) + .3, (E(10) - S(10)) * .9))
        skyline(ctx, gy - 60, seed=12, a=k, x0=560, hmin=180, hmax=380)
        for i, x in enumerate((600, 760, 930)): tree(ctx, x, gy - 60, .9, a=k, lean=adv * 1.2)
        rrect(ctx, 540, gy - 60, 560, 200, 0); fill(ctx, ORBIT, k)                     # costa
        front = 540 + 360 * adv
        for j, (col, al, amp, yo) in enumerate(((hx("0B7399"), .95, 26, 40), (BLUE, .9, 20, 70))):
            ctx.save(); ctx.rectangle(-20, 0, front + 40 - j * 60, H); ctx.clip()
            wave(ctx, t, gy - 60 + yo - 200 * adv * (1 - j * .4), amp, 220, col, al * k, speed=1.2 + j * .4, bottom=gy + 140)
            ctx.restore()
        burst(ctx, front, gy - 160 - 150 * adv, (t * 1.3) % 1, INK, n=8, r0=20, r1=90, w=7, a=.8 * adv)
        arrow(ctx, 140, 620, 140 + 360 * k, 620, BLUE, k, w=14, head=42)
        icon(ctx, "waves", 830, 610, 120, BLUE, k, "duotone")
        text(ctx, "~465 m em 1 segundo", SANS, 44, 540, 540, MUTED, k)


def scene_building(ctx, t):                        # seg 11
    background(ctx, t)
    gy = 1260
    rrect(ctx, -20, gy, W + 40, 18, 9); fill(ctx, RED)
    k = back(prog(t, S(11), .5))
    sh = eio(prog(t, mid(11, .45), .9))
    for i, (x, w, h, sk) in enumerate(((20, 150, 380, 120), (390, 300, 620 * k, 260), (760, 170, 460, 170), (950, 140, 300, 90))):
        building(ctx, x, gy, w, h, col=ORBIT if i != 1 else hx("1C2433"), a=1, seed=20 + i, skew=sk * sh, lit=.5)
    if sh > 0:
        trails(ctx, 390 + 260 * sh, gy - 520, sh * .8, .9)
        debris(ctx, 600 + 200 * sh, gy - 560, prog(t, mid(11, .45), 1.4), n=18, col=MUTED, seed=4)
    text(ctx, "A BASE PARA.", DISP, 76, 540, 430, RED, prog(t, S(11) + .1, .3))
    text(ctx, "O TOPO, NÃO.", DISP, 76, 540, 540, BLUE, prog(t, mid(11, .45), .3))


def scene_restart(ctx, t):                         # segs 12 - 13 (sem legenda)
    background(ctx, t)
    cx, cy, R = 540, 1020, 300
    tr = mid(12, .5)
    lon0 = 20 - max(0, t - tr) * 55
    globe(ctx, cx, cy, R, lon0=lon0, lat0=15)
    globe_line(ctx, 0, lon0, 15, R, cx, cy, BLUE, .9)
    spin_arrow(ctx, cx, cy, R, a=eo(prog(t, tr, .4)), col=BLUE)
    text(ctx, "+1 s", DISP, 130, 540, 470, SOLAR, prog(t, S(12), .3))
    icon(ctx, "timer", 760, 430, 110, SOLAR, prog(t, S(12), .3), "duotone")
    text(ctx, "A TERRA VOLTA A GIRAR", BOLD, 44, 540, 560, INK, prog(t, mid(12, .4), .3), track=.03)
    if t >= S(13):
        k = prog(t, S(13) + .2, .2)
        text(ctx, "TUDO LEVA O", BOLD, 48, 540, 1440, INK, k, track=.04)
        glitch_text(ctx, "TRANCO", DISP, 160, 540, 1610, k, t, amp=16)
        text(ctx, "DE NOVO", BOLD, 48, 540, 1700, INK, k, track=.04)


def scene_lat(ctx, t):                             # segs 14-15
    background(ctx, t)
    cx, cy, R = 330, 880, 270
    lon0, lat0 = -52, 12
    globe(ctx, cx, cy, R, lon0=lon0, lat0=lat0, a=eo(prog(t, S(14), .4)))
    globe_line(ctx, 0, lon0, lat0, R, cx, cy, SOLAR, .8 * eo(prog(t, S(15), .4)), w=6)
    rows = [((-52, 90), "POLO", 0, MUTED, 600, S(14) + .3),
            ((-52, 0), "EQUADOR", 1670, SOLAR, 860, S(15)),
            ((-46.6, -23.5), "SÃO PAULO", 1530, BLUE, 1120, S(15) + .6)]
    x0 = 660
    for (lon, lat), name, v, col, ly, tk in rows:
        k = eo(prog(t, tk, .6))
        if k <= 0: continue
        xx, yy, _ = geo(lon, lat, lon0, lat0, R, cx, cy)
        if lat == 90: yy = cy - R * math.cos(math.radians(lat0)); xx = cx
        circle(ctx, xx, yy, 16, col, k); circle(ctx, xx, yy, 7, VOID, k)
        ctx.set_dash([8, 10]); ctx.set_line_width(4); ctx.set_source_rgba(*col, .7 * k)
        ctx.move_to(xx + 20, yy); ctx.line_to(x0 - 50, yy); ctx.line_to(x0 - 20, ly - 10); ctx.stroke(); ctx.set_dash([])
        text(ctx, name, BOLD, 38, x0, ly - 40, col, k, "l", .06)
        lab = counter(v * k)
        text(ctx, lab, DISP, 80, x0, ly + 48, col, k, "l")
        text(ctx, "km/h", SANS, 38, x0 + DISP.width(lab, 80) + 14, ly + 48, MUTED, k, "l")
    if t >= S(15) + .6:
        xx, yy, _ = geo(-46.6, -23.5, lon0, lat0, R, cx, cy)
        person(ctx, xx - 6, yy - 14, .34 * back(prog(t, S(15) + .8, .5)), mood="wow", arms=(2.4, -2.4))
        text(ctx, "VOCÊ, AQUI", BOLD, 38, x0, 1250, BLUE, prog(t, S(15) + 1.4, .4), "l", .08)


def scene_end(ctx, t):                             # seg 16 + final (sem legenda)
    background(ctx, t)
    k = eo(prog(t, S(16), .4))
    text(ctx, "ONDE VOCÊ", DISP, 100, 540, 520, INK, k)
    text(ctx, "QUERIA ESTAR", DISP, 92, 540, 640, INK, eo(prog(t, S(16) + .2, .4)))
    text(ctx, "NESSE SEGUNDO?", DISP, 84, 540, 760, BLUE, eo(prog(t, S(16) + .4, .4)))
    kl = back(prog(t, E(16) + .2, .6))
    globe(ctx, 540, 1700, 260, lon0=-50 - t * 20, lat0=20, a=.5 * k * (1 - prog(t, E(16), .4)))
    if kl > 0:
        mark(ctx, 540 - 120 * kl, 900, 2 * kl, 1)
        text(ctx, "HYPER", DISP, 64, 540, 1230, INK, prog(t, E(16) + .4, .3))
        text(ctx, "HYPOTHESIS", LITE, 64, 540, 1310, INK, prog(t, E(16) + .5, .3))
        text(ctx, "@hyperhypothesis", SANS, 40, 540, 1400, MUTED, prog(t, E(16) + .8, .3))
        text(ctx, "Responde nos comentários.", SANS, 40, 540, 1480, BLUE, prog(t, E(16) + 1.1, .3))


SCENES = [(0, 0, scene_intro), (1, 2, scene_spin), (3, 5, scene_stop), (6, 7, scene_hero), (8, 8, scene_meio),
          (9, 10, scene_air), (11, 11, scene_building), (12, 13, scene_restart), (14, 15, scene_lat), (16, 16, scene_end)]

_th8 = lambda: S(8) + .2 + (E(8) - S(8)) * .55
CUES = [(0.3, "rumble", .5), (lambda: mid(0, .6), "impact", 1.0),
        (lambda: S(3) + .7, "impact", .9), (lambda: S(5) + .1, "whoosh", .8),
        (lambda: S(6) - .9, "riser", .6), (lambda: S(6), "impact", .8),
        (_th8, "boom", .9), (lambda: S(9) + .3, "wind", .8), (lambda: S(10) + .2, "rumble", .8),
        (lambda: mid(11, .45), "impact", .8), (lambda: mid(12, .5) - 1.0, "riser", .5),
        (lambda: S(13) + .2, "boom", 1.0), (lambda: S(13) + .2, "glitch", .6),
        (lambda: S(14) + .3, "tick", .8), (lambda: S(15), "tick", .8), (lambda: S(15) + .6, "tick", .8),
        (lambda: S(15) + .8, "pop", .6), (lambda: E(16) + .2, "pop", .8)]
SHAKES = [(lambda: mid(0, .6), 16, .5), (lambda: S(3) + .7, 14, .45), (_th8, 22, .6),
          (lambda: mid(11, .45), 12, .5), (lambda: S(13) + .2, 26, .9)]
