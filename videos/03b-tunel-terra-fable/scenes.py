"""Cenas da Hipótese #03 — E se você caísse num túnel que atravessa a Terra? (motor v3, regras de abertura v4)
Física (modelo de densidade uniforme para a forma do movimento; tempos da Terra real):
  movimento harmônico: x = R cos φ, v = vmax sen φ; vmax ≈ √(gR) ≈ 7,9 km/s ≈ 28.400 km/h (Terra real: um pouco mais)
  ida em ~38 min com a densidade real (Klotz, 2015); ida e volta ≈ 76 min
  núcleo externo a 0,546 R, núcleo interno a 0,19 R; antípoda de São Paulo ≈ 23,5° N, 133,4° L (Oceano Pacífico)
"""
import math, random
import cairocffi as cairo
from hh.anim import *

MANTLE, OUTER, INNER = hx("5A2412"), hx("B5400F"), SOLAR      # tons de redshift (camadas quentes)
GREEN = hx("2E6B5E")


def mid(i, f): return S(i) + (E(i) - S(i)) * f


def section(ctx, cx, cy, R, t, a=1.0, labels=0.0, glow=0.0):
    """Corte da Terra em camadas com o túnel vertical passando pelo centro."""
    circle(ctx, cx, cy, R * 1.04, BLUE, .10 * a)
    circle(ctx, cx, cy, R, LAND_COL, a)                                   # crosta
    circle(ctx, cx, cy, R * .985, MANTLE, a)                              # manto
    circle(ctx, cx, cy, R * .546, OUTER, a)                               # núcleo externo
    circle(ctx, cx, cy, R * .19 * (1 + .04 * math.sin(t * 5) * glow), INNER, a)   # núcleo interno
    for k in range(3):                                                    # convecção do manto (arcos lentos)
        ctx.set_line_width(5); ctx.new_sub_path()
        ctx.arc(cx, cy, R * (.65 + k * .1), t * .3 + k * 2.1, t * .3 + k * 2.1 + .9)
        ctx.set_source_rgba(*RED, .35 * a); ctx.stroke()
    ctx.rectangle(cx - 34, cy - R - 10, 68, 2 * R + 20); fill(ctx, VOID, a)       # túnel
    ctx.set_line_width(5); ctx.set_source_rgba(*INK, .7 * a)
    ctx.move_to(cx - 34, cy - R); ctx.line_to(cx - 34, cy + R); ctx.move_to(cx + 34, cy - R); ctx.line_to(cx + 34, cy + R); ctx.stroke()
    if labels > 0:
        for txt, yy, col in (("crosta", cy - R + 40, INK), ("manto", cy - R * .75, INK), ("núcleo", cy - R * .33, VOID)):
            text(ctx, txt, BOLD, 36, cx + 70, yy, col, labels, "l", .04)


def faller(ctx, x, y, t, s=.5, flip=False, mood="wow"):
    """Personagem caindo de pé com braços para cima, girando de leve."""
    person(ctx, x, y, s, mood=mood, arms=(2.6 + wobble(t, .3, 4), -2.6 - wobble(t, .3, 4.4, 1)),
           legspread=.25 + wobble(t, .1, 5), rot=PI if flip else wobble(t, .12, 1.3))


# ---------------------------------------------------------------- cenas
def scene_hook(ctx, t):                            # seg 0 (sem legenda) — ação desde o frame 0
    background(ctx, t)
    gy = 1080
    icon(ctx, "sun", 930, 250, 110, SOLAR, 1, "duotone")
    for c in range(2): cloud(ctx, (200 + c * 500 + t * 30) % (W + 300) - 150, 300 + c * 60, .6, MUTED, .45)
    rrect(ctx, -20, gy, W + 40, H - gy + 20, 0); fill(ctx, MANTLE)               # chão em corte
    rrect(ctx, -20, gy, W + 40, 60, 0); fill(ctx, GREEN)
    ctx.rectangle(-20, gy + 60, W + 40, 120); fill(ctx, LAND_COL)
    tree(ctx, 120, gy, 1.1, lean=wobble(t, .06)); tree(ctx, 960, gy, .9, lean=wobble(t, .06, seed=2))
    icon(ctx, "house", 820, gy - 90, 190, SOLAR, 1, "duotone")
    ctx.rectangle(470, gy, 140, H - gy + 20); fill(ctx, VOID)                    # boca do túnel
    rrect(ctx, 450, gy - 12, 180, 24, 12); fill(ctx, RED)
    tj = 1.15                                                                  # pulo: agacha, salta, cai no buraco
    if t < tj:
        k = prog(t, 0, tj); x = lerp(250, 540, eio(k)); y = gy - 200 * math.sin(PI * k) * (k > .25)
        sq = .82 if k < .25 else 1.08
        person(ctx, x, y, .95, mood="happy" if k < .3 else "wow", arms=(2.4, -2.4) if k > .25 else (.6, -.6), squash=sq,
               run=None if k > .25 else t * 4)
    else:
        y = gy + (t - tj) ** 2 * 2400
        if y < H + 200: faller(ctx, 540, y, t, .95)
        dust(ctx, 540, gy, tj, t, n=10, col=MUTED, dirx=1, seed=3); dust(ctx, 540, gy, tj, t, n=10, col=MUTED, dirx=-1, seed=4)
    pop_text_fit(ctx, "UM TÚNEL QUE", DISP, 84, 540, 430, INK, t, .05, stagger=.02)
    pop_text_fit(ctx, "ATRAVESSA A TERRA?", DISP, 84, 540, 540, BLUE, t, .3, stagger=.02)


def fall_phase(t):
    """φ de 0 (topo) a π (outro lado) ao longo das frases 1–6."""
    if t < S(1): return 0.0
    if t < E(2): return (PI / 2) * eio(prog(t, S(1), E(2) - S(1)))           # até o centro no fim da frase 2
    if t < S(5): return PI / 2
    return PI / 2 + (PI / 2) * eio(prog(t, S(5), mid(6, .55) - S(5)))       # chega do outro lado no meio da frase 6


def scene_fall(ctx, t):                            # segs 1-2: cai acelerando até o centro
    background(ctx, t)
    cx, cy, R = 540, 850, 410
    section(ctx, cx, cy, R, t, labels=eo(prog(t, S(1) + .2, .5)) * (1 - prog(t, S(2), .4)))
    phi = fall_phase(t); y = cy - R * math.cos(phi); v = math.sin(phi)
    for j in range(4):                                                       # rastros redshift acima (atrás)
        L = 40 + 260 * v
        rrect(ctx, cx - 30 + j * 20 - 6, y - 120 - L, 12, L, 6); fill(ctx, RED, .8 * v * (1 - j * .18))
    faller(ctx, cx, y + 40, t, .5)
    speedlines_v = clamp(v)
    if speedlines_v > .3:
        rnd = random.Random(5)
        for _ in range(16):
            xx = rnd.uniform(80, 1000); L = rnd.uniform(80, 260); u = (rnd.random() + t * 2.5) % 1
            rrect(ctx, xx, H - (H + L) * u, 5, L, 3); fill(ctx, INK, .25 * speedlines_v * math.sin(PI * u))
    kv = prog(t, S(2), .3)
    text(ctx, counter(28400 * v), DISP, 110, 540, 300, SOLAR, max(kv, .0))
    text(ctx, "KM/H", BOLD, 40, 540, 360, INK, kv, track=.08)


def scene_core(ctx, t):                            # segs 3-4: calor do núcleo + túnel blindado e sem ar
    background(ctx, t)
    cx, cy = 540, 1000
    k = spring(prog(t, S(3), .7))
    circle(ctx, cx, cy, 760 * k, OUTER); circle(ctx, cx, cy, 300 * k, INNER)
    for j in range(3): shockwave(ctx, cx, cy, S(3) + j * .5 + ((t - S(3)) // 1.5) * 1.5, t, r1=520, life=1.2, col=SOLAR, w=8, a=.5)
    sparks(ctx, cx, cy - 300, S(3) + .2, t, n=20, col=SOLAR, speed=700, life=1.0, seed=31)
    smoke(ctx, cx, cy - 280, S(3), t, n=12, col=RED, life=2.2, spread=260, rise=260, a=.35, seed=32)
    ctx.rectangle(cx - 34, 0, 68, H); fill(ctx, VOID)
    sh = eo(prog(t, S(4), .5))
    if sh > 0:                                                               # blindagem: paredes azuis
        rrect(ctx, cx - 50, 0, 16, H, 8); rrect(ctx, cx + 34, 0, 16, H, 8); fill(ctx, BLUE, sh)
    faller(ctx, cx, cy + 40 + wobble(t, 20, 1.5), t, .5)
    ctx.save(); ctx.translate(150, 520); ctx.rotate(wobble(t, .1, 3))
    icon(ctx, "thermometer-hot", 0, 0, 170 * spring(prog(t, S(3) + .2, .6)), INK, 1, "duotone", col2=RED); ctx.restore()
    pop_text(ctx, "5.000+ °C", DISP, 96, 620, 560, SOLAR, t, S(3) + .3)
    if sh > 0:
        icon(ctx, "shield-check", 820, 1230, 150 * spring(prog(t, S(4), .6)), BLUE, 1, "duotone")
        icon(ctx, "wind", 260, 1230, 130 * spring(prog(t, mid(4, .5), .6)), MUTED, 1, "duotone")
        ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*RED, prog(t, mid(4, .5), .3))
        ctx.move_to(195, 1165); ctx.line_to(325, 1295); ctx.stroke()
        text(ctx, "BLINDADO", BOLD, 40, 820, 1340, BLUE, sh, track=.06)
        text(ctx, "SEM AR", BOLD, 40, 260, 1340, MUTED, prog(t, mid(4, .5), .3), track=.06)


def scene_rise(ctx, t):                            # segs 5-6: freia depois do centro e chega parado em 38 min
    background(ctx, t)
    cx, cy, R = 540, 850, 410
    section(ctx, cx, cy, R, t)
    phi = fall_phase(t); y = cy - R * math.cos(phi); v = math.sin(phi)
    for j in range(4):                                                       # agora sobe: rastros embaixo
        L = 40 + 260 * v
        rrect(ctx, cx - 30 + j * 20 - 6, y + 60, 12, L, 6); fill(ctx, RED, .8 * v * (1 - j * .18))
    faller(ctx, cx, y + 40, t, .5)
    kg = eo(prog(t, S(5) + .3, .5)) * (1 - prog(t, S(6), .4))
    if kg > 0:                                                               # gravidade puxando de volta ao centro
        arrow(ctx, cx + 90, y, cx + 90, y - (y - cy) * .55, BLUE, kg, w=12, head=36)
        text(ctx, "gravidade", SANS, 40, cx + 120, (y + cy) / 2 + 60, BLUE, kg, "l")
    text(ctx, counter(28400 * v), DISP, 96, 540, 300, SOLAR, 1 - prog(t, S(6), .5))
    text(ctx, "KM/H", BOLD, 36, 540, 352, INK, 1 - prog(t, S(6), .5), track=.08)
    arrive = mid(6, .55)
    if t >= S(6):
        km = eo(prog(t, S(6), arrive - S(6)))
        ka = prog(t, S(6), .3)
        rrect(ctx, 290, 190, 500, 190, 24); fill(ctx, ORBIT, ka)
        icon(ctx, "timer", 380, 285, 100, SOLAR, ka, "duotone")
        text(ctx, f"{int(round(38 * km))}", DISP, 110, 560, 325, SOLAR, ka)
        text(ctx, "MIN", BOLD, 40, 690, 325, INK, ka, "l", .06)
        if t >= arrive:
            pop_text(ctx, "PARADO.", DISP, 72, 810, 1250, BLUE, t, arrive)
            burst(ctx, cx, cy + R, prog(t, arrive, .5), INK, n=10, r0=40, r1=140, w=7)


def scene_anti(ctx, t):                            # seg 7: de São Paulo ao Oceano Pacífico
    background(ctx, t)
    cx, cy, R = 540, 900, 400
    k = prog(t, S(7) + .2, (E(7) - S(7)) * .7)
    lon0 = lerp(-46.6, 133.4, eio(k)); lat0 = lerp(-23.5, 23.5, eio(k))
    globe(ctx, cx, cy, R, lon0=lon0, lat0=lat0)
    for (lon, lat), col, lab, kk in (((-46.6, -23.5), BLUE, "SÃO PAULO", 1 - k), ((133.4, 23.5), SOLAR, "OCEANO PACÍFICO", k)):
        x, y, vis = geo(lon, lat, lon0, lat0, R, cx, cy)
        if vis and kk > .05:
            circle(ctx, x, y, 18, col, kk); circle(ctx, x, y, 8, VOID, kk)
            text(ctx, lab, BOLD, 40, x, y - 50, col, kk, track=.06)
    if k >= 1:                                                               # ele sai da água
        ta = S(7) + .2 + (E(7) - S(7)) * .7
        y = cy - 40 * spring(prog(t, ta, .6))
        faller(ctx, cx, y, t, .4, mood="happy")
        spray(ctx, cx, cy, ta, t, n=26, col=BLUE, speed=650, seed=7)
        spray(ctx, cx, cy, ta + .05, t, n=18, col=INK, speed=500, seed=8)
    text(ctx, "o outro lado do planeta", SANS, 44, 540, 1440 - 120, MUTED, eo(prog(t, S(7), .4)))


def scene_loop(ctx, t):                            # segs 8-9: cai de volta, ida e volta pra sempre
    background(ctx, t)
    cx, cy, R = 540, 850, 410
    section(ctx, cx, cy, R, t)
    tb = S(8) + (E(8) - S(8)) * .45
    if t < tb:
        y = cy - R + 10 * math.sin(t * 3); faller(ctx, cx, y + 40, t, .5, mood="scared")
        pop_text(ctx, "E SE NINGUÉM TE SEGURAR?", BOLD, 48, 540, 330, INK, t, S(8))
    else:
        w = 2 * PI / 2.4                                                     # ciclo acelerado (76 min em 2,4 s)
        phi = w * (t - tb); y = cy - R * math.cos(phi)
        for g in range(1, 6):                                                # fantasmas do caminho
            yy = cy - R * math.cos(phi - g * .18); faller(ctx, cx, yy + 40, t, .5);
        ctx.save(); ctx.rectangle(0, 0, W, H); fill(ctx, VOID, .25); ctx.restore()
        faller(ctx, cx, y + 40, t, .5)
        pop_text(ctx, "IDA E VOLTA", DISP, 84, 540, 300, BLUE, t, S(9))
        text(ctx, "76 minutos por ciclo, sem parar", SANS, 40, 540, 370, MUTED, prog(t, S(9) + .3, .4))


def scene_end(ctx, t):                             # segs 10-11 + final (sem legenda)
    end_card(ctx, t, S(10), question=["PRA ONDE", "VOCÊ CAVARIA?"], next_title="E se o Sol virasse um buraco negro?")


SCENES = [(0, 0, scene_hook), (1, 2, scene_fall), (3, 4, scene_core), (5, 6, scene_rise), (7, 7, scene_anti),
          (8, 9, scene_loop), (10, 11, scene_end)]

CUES = [(0.25, "whoosh", .7), (1.15, "whoosh", 1.0), (lambda: S(1), "wind", .8), (lambda: E(2) - 1.0, "riser", .6),
        (lambda: E(2) - .05, "impact", .9), (lambda: S(3), "rumble", .9), (lambda: S(4), "force", .7),
        (lambda: S(6), "tick", .7), (lambda: mid(6, .55), "pop", .8),
        (lambda: S(7) + .2 + (E(7) - S(7)) * .7, "crash", .5), (lambda: S(8) + (E(8) - S(8)) * .45, "whoosh", .9),
        (lambda: S(10) + 1.0, "force", .6), (lambda: S(10) + 1.6, "pop", .7)]
SHAKES = [(lambda: E(2) - .05, 14, .5), (lambda: S(3), 10, .8), (lambda: S(7) + .2 + (E(7) - S(7)) * .7, 10, .4)]
