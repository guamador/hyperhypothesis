"""Cenas da Hipótese #05 — E se você saísse da nave sem traje?   (motor v4; modelos: 03b e 04)

FISIOLOGIA E FONTES (conferidas em 12/11/2026)
- Consciência no vácuo: ~10 a 15 s (animais: 9 a 12 s; um chimpanzé com EEG: ~11 s de consciência útil).
  Fonte: aerospaceweb.org, "Human Exposure to the Vacuum of Space"; oikofuge.com, "Human Exposure To Vacuum, Part 2".
- Prender a respiração na descompressão pode romper os pulmões (quase sempre fatal): a regra é soltar o ar.
- Ninguém explode: a pele e os tecidos seguram. A água dos tecidos vira vapor (ebulismo) e o corpo pode inchar
  até ~2 vezes o volume (cães chegaram a ~2x). Na tela: escala linear 1,25 ≈ volume 1,95x.
- Não congela na hora: o vácuo isola; a evaporação esfria só a boca e o nariz. Para inchar 2x, o corpo
  evapora ~3,5 g de água e esfria ~0,025 °C (oikofuge).
- A saliva ferve na língua: a 37 °C a água ferve abaixo de ~6,3 kPa (limite de Armstrong). O sangue não ferve
  porque a pressão nos vasos o mantém líquido.
- Sobrevivência: quase sempre se recupera com recompressão em até ~90 s; depois de ~2 min as mortes ficam frequentes.
- Jim LeBlanc, 1966 (NASA, Houston): o traje despressurizou numa câmara de vácuo; apagou em ~14-15 s; a câmara foi
  repressurizada em menos de 1 minuto; ficou só com dor nos ouvidos. Última lembrança: "a saliva na língua começando a ferver".
- O relógio da tela é comprimido: 15 s de verdade até o "apagão"; depois acelera (avanço rápido) até o resgate, em ~45 s.
"""
import math, random
import cairocffi as cairo
from hh.anim import *
from hh.cam import Cam, lerp_log, smooth, smoother, ramp, pulse, ease_out, ease_in
from hh.hero import hero, POSES, mixpose, flutter

ZOOM = 0.0

# ---------------------------------------------------------------- linha do tempo
T_OUT = 1.5                                              # sai pela escotilha: o relógio começa
T_EXH = WT(1, "solta")                                   # solta o ar
T_TEAR = WT(1, "rasgam.")
T_BOIL = WT(3, "ferver.")
T_SW0, T_SW1 = WT(4, "incha,") - .1, WT(4, "dobro.") + .3
T_O2 = WT(5, "sangue")
T_15 = WT(6, "15")
T_DARK = WT(7, "apagão.")                                 # 15 s no vácuo
T_R0, T_R1 = WT(8, "puxarem") + .2, WT(8, "dentro") + .75 # corda puxa de volta
T_DOOR = T_R1 + .05
T_SAFE = T_DOOR + .4
TAU_DARK, TAU_SAFE = 15.0, 45.0

def tau(t):
    """Segundos no vácuo. Tempo real até o apagão; depois, avanço rápido até o resgate."""
    if t < T_OUT: return 0.0
    if t < T_DARK: return TAU_DARK * (t - T_OUT) / (T_DARK - T_OUT)
    return lerp(TAU_DARK, TAU_SAFE, ramp(t, T_DARK, T_SAFE))

# ---------------------------------------------------------------- personagem: trajetória no mundo (px)
P_IN = (-70.0, 20.0)
def hero_state(t):
    """(x, y, rot, s, squash) do personagem no mundo."""
    k0 = ease_out(ramp(t, 0.0, 3.0), 2)
    x, y = lerp(P_IN[0], 240, k0), lerp(P_IN[1], -40, k0)
    d = max(0.0, t - 3.0); x += 11 * d; y -= 4 * d
    rot = .12 * math.sin(t * .9) + .05 * d + .18 * max(0.0, t - T_DARK)
    s = 1.0 + .25 * smoother(ramp(t, T_SW0, T_SW1)) * (1 - ramp(t, T_SAFE, T_SAFE + 1.0))
    sq = 1 + .05 * math.sin(t * 7) * ramp(t, T_SW0, T_SW1 + .5) * (1 - ramp(t, T_SW1 + .5, T_SW1 + 1.5))
    if t >= T_EXH - .1:                                                              # expira: o peito murcha um pouco
        sq *= 1 - .08 * pulse(t, T_EXH - .1, .25, .2, .5)
    kr = smoother(ramp(t, T_R0, T_R1))
    if kr > 0: x, y, rot = lerp(x, P_IN[0], kr), lerp(y, P_IN[1], kr), lerp(rot, 0, kr)
    return x, y, rot, s, sq

def head_pt(x, y, rot, s, lx=0.0, ly=-90.0):
    c, sn = math.cos(rot), math.sin(rot)
    return x + (lx * c - ly * sn) * s, y + (lx * sn + ly * c) * s

# ---------------------------------------------------------------- câmera
KEYS = [  # (t, z, alvo: "hero" | "head" | (x, y), fy)
    (0.0, .85, (-40, 0), 900), (S(1) - .2, .85, (-40, 0), 900), (S(1) + .5, 1.5, "hero", 860),
    (S(2), 1.5, "hero", 860), (S(2) + .5, 1.3, "hero", 860), (S(3) - .1, 1.3, "hero", 860), (S(3) + .5, 3.0, "head", 820),
    (WT(3, "ferver.") + .4, 3.0, "head", 820), (S(4) + .2, 1.35, "hero", 880), (S(5), 1.35, "hero", 880),
    (T_DARK, 1.6, "hero", 860), (S(8) - .05, 1.6, "hero", 860), (S(8) + .4, .82, (150, -40), 900), (99, .82, (150, -40), 900)]

def camera(t, hs):
    x, y, rot, s, _ = hs
    def tgt(k):
        _, z, a, fy = k
        if a == "hero": return x, y, z, fy
        if a == "head": hx_, hy_ = head_pt(x, y, rot, s, 0, -78); return hx_, hy_, z, fy
        return a[0], a[1], z, fy
    for i in range(len(KEYS) - 1):
        if KEYS[i][0] <= t < KEYS[i + 1][0]:
            a, b = tgt(KEYS[i]), tgt(KEYS[i + 1]); k = smoother(ramp(t, KEYS[i][0], KEYS[i + 1][0]))
            return Cam(lerp(a[0], b[0], k), lerp(a[1], b[1], k), lerp_log(a[2], b[2], k), 0, 540, lerp(a[3], b[3], k))
    a = tgt(KEYS[0]); return Cam(a[0], a[1], a[2], 0, 540, a[3])

# ---------------------------------------------------------------- cenário: Terra, nave, escotilha
def earth_bg(ctx, t, cam):
    px = -cam.cx * .04
    globe(ctx, 540 + px, 2780, 1560, lon0=-40 + t * .6, lat0=-8, grid=False, ring=True)
    for k, al in ((1.035, .16), (1.06, .08)):
        ctx.set_line_width(26); ctx.new_sub_path(); ctx.arc(540 + px, 2780, 1560 * k, PI, 2 * PI); ctx.set_source_rgba(*BLUE, al); ctx.stroke()

def door_open(t):
    return smoother(ramp(t, -.6, .5)) * (1 - smoother(ramp(t, T_DOOR, T_DOOR + .35)))

def ship(ctx, cam, t):
    """Módulo da nave em coordenadas do mundo: casco à esquerda, escotilha em x = 0."""
    cam.apply(ctx)
    rrect(ctx, -900, -820, 30, 560, 10); fill(ctx, MUTED)                          # mastro + painel solar
    for i in range(2):
        for j in range(5):
            rrect(ctx, -1180 + i * 330, -1300 + j * 96, 300, 84, 6); fill(ctx, hx("1F5E8A")); ctx.set_line_width(3)
            rrect(ctx, -1180 + i * 330, -1300 + j * 96, 300, 84, 6); ctx.set_source_rgba(*BLUE, .8); ctx.stroke()
    rrect(ctx, -1500, -270, 1500, 540, 60); fill(ctx, hx("2A2F3A"))
    rrect(ctx, -1500, -270, 1500, 540, 60); ctx.set_line_width(6); ctx.set_source_rgba(*LINE, 1); ctx.stroke()
    for xx in range(-1400, 0, 200):                                                  # placas e rebites
        ctx.move_to(xx, -260); ctx.line_to(xx, 260)
    ctx.move_to(-1490, -90); ctx.line_to(-10, -90); ctx.move_to(-1490, 150); ctx.line_to(-10, 150)
    ctx.set_line_width(3); ctx.set_source_rgba(*LINE, .8); ctx.stroke()
    for xx in range(-1350, 0, 100): circle(ctx, xx, -240, 5, MUTED); circle(ctx, xx, 240, 5, MUTED)
    rrect(ctx, -560, -60, 240, 90, 12); fill(ctx, RED, .85)                          # faixa de aviso
    for k in range(5): rrect(ctx, -545 + k * 46, -50, 22, 70, 4); fill(ctx, SOLAR, .9)
    # escotilha (abre para cima)
    rrect(ctx, -150, -150, 150, 300, 24); fill(ctx, VOID)
    rrect(ctx, -140, -140, 130, 280, 20); fill(ctx, hx("161A22"))
    k = door_open(t); dy = -330 * k
    rrect(ctx, -26, -150 + dy, 48, 300, 14); fill(ctx, MUTED)
    rrect(ctx, -26, -150 + dy, 48, 300, 14); ctx.set_line_width(4); ctx.set_source_rgba(*INK, .5); ctx.stroke()
    circle(ctx, -2, dy, 14, INK, .8)
    # sinal de alerta girando
    a0 = t * 5
    circle(ctx, -90, -300, 26, RED)
    for s_ in (-1, 1):
        ctx.move_to(-90, -300); ctx.arc(-90, -300, 220, a0 + s_ * 1.4 - .28, a0 + s_ * 1.4 + .28); ctx.close_path(); fill(ctx, RED, .16)
    cam.restore(ctx)

def porthole(ctx, cam, t, a):
    """Janelinha ao lado da escotilha: depois do resgate, mostra o personagem acordando."""
    x, y = cam.pt(-300, 20); r = 74 * cam.z
    circle(ctx, x, y, r * 1.18, MUTED); circle(ctx, x, y, r, hx("161A22"))
    if a > 0:
        ctx.save(); ctx.new_sub_path(); ctx.arc(x, y, r, 0, 2 * PI); ctx.clip()
        circle(ctx, x, y, r, SOLAR, .12 * a)
        hero(ctx, x, y + r * .55, r / 120, t, pose=mixpose(POSES["stand"], dict(arms=(2.6 + .3 * math.sin(t * 8), -.3), elbows=(.2, -.1), legs=(.08, -.08), knees=(0, 0)), a), mood="happy" if a > .5 else "calm", look=(.4, -.2), a=1)
        ctx.restore()
    ctx.set_line_width(max(3, 6 * cam.z)); ctx.new_sub_path(); ctx.arc(x, y, r, 0, 2 * PI); ctx.set_source_rgba(*INK, .5); ctx.stroke()

def air_jet(ctx, cam, t):
    """Ar escapando pela escotilha nos primeiros segundos (e entrando de volta quando fecha)."""
    k = 1 - ramp(t, 1.2, 3.2)
    if k <= 0: return
    rnd = random.Random(31)
    for i in range(46):
        ph = rnd.random(); sp = 500 + 600 * rnd.random(); u = (t * 1.3 + ph) % 1.0
        ang = rnd.uniform(-.55, .55); d = u * sp
        x, y = cam.pt(-20 + math.cos(ang) * d, 10 + math.sin(ang) * d)
        circle(ctx, x, y, (3 + 8 * u) * cam.z, INK, .5 * (1 - u) * k)

def lungs_card(ctx, t, x, y, a):
    """Painel com pulmões: inflam se você prende o ar e rasgam."""
    if a <= 0: return
    rrect(ctx, x - 150, y - 150, 300, 300, 40); fill(ctx, ORBIT, .95 * a)
    infl = 1 + .18 * smooth(ramp(t, WT(1, "prender,") - .1, T_TEAR))
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(x, y - 110); ctx.line_to(x, y - 30); ctx.set_source_rgba(*INK, a); ctx.stroke()
    for sx in (-1, 1):
        ctx.save(); ctx.translate(x + sx * 52, y + 20); ctx.scale(infl, infl)
        ctx.new_sub_path(); ctx.arc(0, -20, 42, PI, 2 * PI); ctx.line_to(42, 50); ctx.curve_to(42, 90, -42, 90, -42, 50); ctx.close_path(); fill(ctx, RED, .9 * a)
        ctx.restore()
    kt = ramp(t, T_TEAR, T_TEAR + .2)
    if kt > 0:
        ctx.set_line_width(7); ctx.move_to(x - 80, y - 10); ctx.line_to(x - 55, y + 20); ctx.line_to(x - 75, y + 45); ctx.line_to(x - 50, y + 70)
        ctx.set_source_rgba(*INK, a * kt); ctx.stroke()
        burst(ctx, x - 60, y + 25, clamp((t - T_TEAR) / .5), INK, n=8, r0=30, r1=90, w=5)
        icon(ctx, "x-circle", x + 100, y - 100, 80, RED, a * kt, "fill")

def o2_bar(ctx, t, a):
    if a <= 0: return
    lv = 1 - .85 * smooth(ramp(t, T_O2 - .2, T_15))
    rrect(ctx, 70, 450, 940, 150, 30); fill(ctx, ORBIT, .93 * a)
    icon(ctx, "brain", 150, 525, 80 * (1 + .08 * math.sin(t * 9) * (1 - lv)), RED if lv < .4 else INK, a, "fill")
    text(ctx, "OXIGÊNIO NO SANGUE", BOLD, 38, 230, 505, MUTED, a, "l", .04)
    rrect(ctx, 230, 530, 740, 36, 18); fill(ctx, VOID, a)
    rrect(ctx, 230, 530, 740 * lv, 36, 18); fill(ctx, mix(RED, BLUE, lv), a)

def vac_clock(ctx, t, a):
    if a <= 0: return
    rrect(ctx, 50, 205, 980, 180, 28); fill(ctx, ORBIT, .93 * a)
    ff = T_DARK < t < T_SAFE
    icon(ctx, "fast-forward" if ff else "timer", 124, 296, 72, RED if tau(t) >= 15 else SOLAR, a, "fill")
    ctx.save(); ctx.translate(184, 332); ks = 1 + .1 * pulse(t, T_DARK, .08, .1, .4); ctx.scale(ks, ks)
    text(ctx, fmt_clock(tau(t)), DISP, 100, 0, 0, RED if tau(t) >= 15 else SOLAR, a, "l"); ctx.restore()
    text(ctx, "NO", BOLD, 36, 996, 286, MUTED, a, "r", .04); text(ctx, "VÁCUO", BOLD, 36, 996, 340, INK, a, "r", .04)

def limit_bar(ctx, t, a):
    """Régua de 0 a 120 s com a zona perigosa depois de 90 s; o marcador mostra o tempo no vácuo."""
    if a <= 0: return
    x0, x1, y = 110, 970, 470; sx = lambda s_: x0 + (x1 - x0) * s_ / 120
    rrect(ctx, x0, y - 12, x1 - x0, 24, 12); fill(ctx, BLUE, .55 * a)
    rrect(ctx, sx(90), y - 12, x1 - sx(90), 24, 12); fill(ctx, RED, .85 * a)
    text(ctx, "1 MIN 30 S", BOLD, 36, sx(90), y + 66, RED, a)
    mx = sx(tau(t)); circle(ctx, mx, y, 22, INK, a); circle(ctx, mx, y, 10, VOID, a)

def bubbles(ctx, x, y, t, t0, k, sc=1.0, seed=3):
    """Bolhinhas de saliva fervendo saindo da boca."""
    if k <= 0: return
    rnd = random.Random(seed)
    for i in range(14):
        ph = rnd.random(); u = ((t - t0) * (1.2 + rnd.random()) + ph) % 1.0
        bx = x + (rnd.uniform(-14, 14) + 30 * u * math.sin(i * 2.1)) * sc; by = y - (6 + 70 * u) * sc
        r = (5 + 9 * rnd.random()) * sc * (1 - .3 * u)
        circle(ctx, bx, by, r, BLUE, .25 * k * (1 - u))
        ctx.set_line_width(max(2.5, 3.5 * sc)); ctx.new_sub_path(); ctx.arc(bx, by, r, 0, 2 * PI); ctx.set_source_rgba(*BLUE, .95 * k * (1 - u)); ctx.stroke()
        if u > .85: burst(ctx, bx, by, (u - .85) / .15, BLUE, n=5, r0=r, r1=r * 2.4, w=3)

# ---------------------------------------------------------------- cena 1: no vácuo (frases 0 a 8), um plano só
def scene_space(ctx, t):
    background(ctx, t)
    hs = hero_state(t); x, y, rot, s, sq = hs
    cam = camera(t, hs)
    earth_bg(ctx, t, cam)
    ship(ctx, cam, t)
    porthole(ctx, cam, t, ramp(t, T_SAFE + .2, T_SAFE + .7))
    air_jet(ctx, cam, t)
    # corda de resgate
    kr0 = ramp(t, T_R0 - .45, T_R0); hide = t > T_DOOR + .1
    hxs, hys = cam.pt(x, y)
    if kr0 > 0 and not hide:
        sx_, sy_ = cam.pt(-30, 30); ex_, ey_ = lerp(sx_, hxs, kr0), lerp(sy_, hys, kr0)
        ctx.set_line_width(7 * cam.z); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(sx_, sy_)
        ctx.curve_to(lerp(sx_, ex_, .4), lerp(sy_, ey_, .4) + 40 * cam.z * (1 - kr0), lerp(sx_, ex_, .7), ey_, ex_, ey_); ctx.set_source_rgba(*SOLAR, 1); ctx.stroke()
        icon(ctx, "hand-grabbing", ex_, ey_, 70 * cam.z, INK, 1, "fill")
    # personagem
    if t < T_DOOR + .05:
        dark = t >= T_DARK
        if t < T_OUT: pose, mood = mixpose(POSES["leap"], POSES["float"], ramp(t, .3, 1.6)), "wow"
        elif dark: pose, mood = POSES["float"], "calm"
        elif t < S(2): pose, mood = POSES["float"], ("effort" if WT(1, "prender,") - .1 < t < T_TEAR + .5 else "wow")
        elif t < S(3): pose, mood = POSES["panic"] if t < WT(2, "explode.") + .6 else POSES["float"], "scared"
        elif t < S(4): pose, mood = POSES["float"], "wow"
        elif t < S(5): pose, mood = mixpose(POSES["float"], POSES["panic"], .5), "scared"
        else: pose, mood = POSES["float"], "dizzy"
        pose = flutter(pose, t, .06 if not dark else .02, f=3)
        if s > 1.01:                                                                  # contorno do tamanho normal
            ctx.save(); ctx.set_dash([10, 8]); ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(hxs, hys - 30 * cam.z, 150 * cam.z, 0, 2 * PI)
            ctx.set_source_rgba(*BLUE, .6 * ramp(s, 1.02, 1.1)); ctx.stroke(); ctx.restore()
        hero(ctx, hxs, hys, s * cam.z, t, pose=pose, mood=mood, look=(wobble(t, .5, .5), -.2), rot=rot, squash=sq, vel=(0, 0))
        # bafo ao soltar o ar
        if T_EXH - .1 < t < T_EXH + 1.4:
            mx, my = cam.pt(*head_pt(x, y, rot, s, 0, -70))
            smoke(ctx, mx + 10, my, T_EXH - .05, t, n=10, col=INK, life=1.2, spread=60 * cam.z, rise=-20, r0=8 * cam.z, r1=40 * cam.z, a=.5, wind=260 * cam.z, seed=5)
        # saliva fervendo
        kb = ramp(t, T_BOIL - .7, T_BOIL - .3) * (1 - ramp(t, S(4) + .4, S(4) + .9))
        mx, my = cam.pt(*head_pt(x, y, rot, s, 0, -64))
        bubbles(ctx, mx, my, t, S(3), kb, sc=cam.z * .9)
    # vinheta do apagão (as pálpebras fecham e reabrem no resgate)
    kc = smoother(ramp(t, T_DARK - .05, T_DARK + .55)) * (1 - smoother(ramp(t, S(8) - .1, S(8) + .5)))
    if kc > 0:
        r = lerp(1400, 0, kc)
        ctx.save(); ctx.rectangle(-20, -20, W + 40, H + 40); ctx.new_sub_path(); ctx.arc(hxs, hys - 40, max(r, 1), 0, 2 * PI)
        ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.clip(); ctx.rectangle(-20, -20, W + 40, H + 40); fill(ctx, VOID, .97); ctx.restore()
    # textos
    a1 = 1 - ramp(t, S(1) - .1, S(1) + .2)
    pop_text_fit(ctx, "E SE VOCÊ SAÍSSE", DISP, 74, 540, 250, INK, t, 0.0, a=a1, stagger=.02, dur=.3)
    pop_text_fit(ctx, "DA NAVE SEM TRAJE?", DISP, 84, 540, 365, RED, t, WT(0, "sem") - .2, a=a1, stagger=.02)
    vac_clock(ctx, t, ramp(t, S(1) + .1, S(1) + .4) * (1 - ramp(t, E(8) + .2, E(8) + .5)))
    ka = 1 - ramp(t, S(2) - .1, S(2) + .2)
    chip(ctx, "SOLTA O AR", 540, 480, ramp(t, T_EXH - .1, T_EXH + .25) * ka, ic="wind", col=BLUE)
    lungs_card(ctx, t, 830, 700, ramp(t, WT(1, "prender,") - .25, WT(1, "prender,") + .1) * ka)
    kb_ = 1 - ramp(t, S(3) - .1, S(3) + .2)
    chip(ctx, "NÃO EXPLODE", 540, 480, ramp(t, WT(2, "explode.") - .1, WT(2, "explode.") + .25) * kb_, ic="bomb", col=INK)
    chip(ctx, "NEM CONGELA NA HORA", 540, 590, ramp(t, WT(2, "congela") - .1, WT(2, "congela") + .25) * kb_, ic="snowflake", col=BLUE)
    kc_ = 1 - ramp(t, S(4) - .1, S(4) + .2)
    chip(ctx, "SALIVA FERVENDO", 540, 480, ramp(t, WT(3, "saliva") - .1, WT(3, "saliva") + .25) * kc_, ic="drop", col=INK)
    chip(ctx, "ÁGUA FERVE NO VÁCUO", 540, 590, ramp(t, T_BOIL - .2, T_BOIL + .15) * kc_, ic="flame", col=SOLAR, size=38)
    kd_ = 1 - ramp(t, S(5) - .1, S(5) + .2)
    chip(ctx, "VOLUME: QUASE O DOBRO", 540, 480, ramp(t, WT(4, "dobro.") - .3, WT(4, "dobro.") + .05) * kd_, ic="arrows-out", col=SOLAR, size=38)
    chip(ctx, "A PELE SEGURA", 540, 590, ramp(t, WT(4, "pele") - .1, WT(4, "pele") + .25) * kd_, ic="check-circle", col=BLUE)
    o2_bar(ctx, t, ramp(t, S(5) - .05, S(5) + .3) * (1 - ramp(t, S(6) - .1, S(6) + .15)))
    pop_text_fit(ctx, "15 SEGUNDOS", DISP, 120, 540, 600, SOLAR, t, T_15 - .1, a=1 - ramp(t, T_DARK + .1, T_DARK + .4), stagger=.035)
    limit_bar(ctx, t, ramp(t, S(8) + .3, S(8) + .7) * (1 - ramp(t, E(8) + .2, E(8) + .5)))
    chip(ctx, "SOBREVIVE", 540, 640, ramp(t, WT(8, "sobreviver.") - .15, WT(8, "sobreviver.") + .2), ic="heartbeat", col=BLUE)

# ---------------------------------------------------------------- cena 2: 1966, câmara de vácuo da NASA (frases 9 e 10)
T_Y = WT(9, "1966,")
T_POP = WT(9, "passou")                                  # a mangueira do traje solta
T_FALL = T_POP + .7
T_REP = WT(9, "sobreviveu.") - .45                       # repressuriza
T_UP = WT(9, "sobreviveu.") + .05
T_FB = S(10)                                             # flashback: volta ao momento do vazamento
HX, HY = 540, 900                                        # personagem dentro da câmara (mundo do laboratório)

def pressure(t):
    if t >= T_FB: return .06
    return lerp(1.0, .03, ease_out(ramp(t, T_POP, T_POP + .9), 2)) if t < T_REP else lerp(.03, 1.0, smooth(ramp(t, T_REP, T_REP + 1.0)))

def lab_hero(ctx, t, tt):
    """Técnico de traje dentro da câmara. tt = tempo da história (congela no flashback)."""
    kf = smoother(ramp(tt, T_FALL, T_FALL + .5)) * (1 - smoother(ramp(tt, T_UP, T_UP + .6)))
    x, y = HX + 30 * kf, HY + 70 * kf
    rot = .9 * kf
    pose = mixpose(POSES["stand"], POSES["float"], kf)
    if T_POP < tt < T_FALL: pose = POSES["panic"]
    if tt > T_UP + .4: pose = mixpose(POSES["stand"], dict(arms=(2.7, -2.7), elbows=(.2, -.2), legs=(.1, -.1), knees=(0, 0)), smooth(ramp(tt, T_UP + .4, T_UP + .8)))
    mood = "calm" if kf > .6 else ("scared" if tt > T_POP else "happy")
    if tt > T_UP + .4: mood = "happy"
    if t >= T_FB: mood = "wow"
    rrect(ctx, x - 50, y - 60, 100, 110, 26); fill(ctx, MUTED)                     # mochila do traje (atrás)
    hero(ctx, x, y, 1.15, t, pose=flutter(pose, t, .03, f=4), mood=mood, look=(.2, 0), rot=rot, scarf=False)
    hx_, hy_ = head_pt(x, y, rot, 1.15, 0, -90)
    circle(ctx, hx_, hy_, 66, BLUE, .12); ctx.set_line_width(6); ctx.new_sub_path(); ctx.arc(hx_, hy_, 66, 0, 2 * PI); ctx.set_source_rgba(*INK, .75); ctx.stroke()
    ctx.set_line_width(5); ctx.new_sub_path(); ctx.arc(hx_, hy_, 54, -2.4, -1.5); ctx.set_source_rgba(*INK, .6); ctx.stroke()   # brilho do capacete
    return x, y, rot, hx_, hy_

def lab(ctx, t, cam):
    tt = T_POP + .35 + .05 * math.sin(t * 3) if t >= T_FB else t
    cam.apply(ctx)
    rrect(ctx, -400, -400, 1880, 2800, 0); fill(ctx, hx("161A22"))                # parede
    for xx in range(-300, 1500, 180): rrect(ctx, xx, 200, 8, 1100, 4); fill(ctx, LINE, .6)
    rrect(ctx, -400, 1300, 1880, 900, 0); fill(ctx, ORBIT)                          # piso
    rrect(ctx, -400, 1296, 1880, 10, 0); fill(ctx, LINE)
    # câmara de vácuo: cilindro em corte
    rrect(ctx, 200, 440, 680, 860, 120); fill(ctx, MUTED)
    rrect(ctx, 236, 476, 608, 788, 96); fill(ctx, VOID)
    p = pressure(tt)
    rrect(ctx, 236, 476, 608, 788, 96); fill(ctx, BLUE, .10 * p)
    for k in range(4): rrect(ctx, 200, 520 + k * 200, 680, 10, 5); fill(ctx, LINE, .9)
    # alarme
    al = 1.0 if (T_POP < tt < T_REP + .6) else 0.0
    circle(ctx, 540, 420, 28, RED if al else MUTED)
    if al:
        a0 = t * 7
        for s_ in (-1, 1): ctx.move_to(540, 420); ctx.arc(540, 420, 300, a0 + s_ * 1.4 - .3, a0 + s_ * 1.4 + .3); ctx.close_path(); fill(ctx, RED, .14)
    # manômetro
    gx, gy = 780, 1180
    circle(ctx, gx, gy, 58, INK); circle(ctx, gx, gy, 50, ORBIT)
    ang = PI * .8 + PI * 1.4 * p
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(gx, gy); ctx.line_to(gx + math.cos(ang) * 40, gy + math.sin(ang) * 40); ctx.set_source_rgba(*RED, 1); ctx.stroke()
    circle(ctx, gx, gy, 8, INK)
    x, y, rot, hx_, hy_ = lab_hero(ctx, t, tt)
    # mangueira do traje
    kp = ramp(tt, T_POP, T_POP + .25)
    hose_end = (x + 40, y - 10)
    ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(240, 760)
    if kp <= 0: ctx.curve_to(330, 820, 420, 760, hose_end[0] + 20, hose_end[1])
    else: ctx.curve_to(310, 840, 360, 900 + 60 * math.sin(t * 6) * kp, 380 + 30 * math.sin(t * 9), 980)
    ctx.set_source_rgba(*SOLAR, 1); ctx.stroke()
    if T_POP <= tt < T_POP + 1.3:
        spray(ctx, hose_end[0], hose_end[1], T_POP, tt, n=26, col=INK, speed=600, life=.8, g=0, seed=2, ang0=-1.2, ang1=.6)
        sparks(ctx, hose_end[0], hose_end[1], T_POP, tt, n=10, col=SOLAR, speed=500, life=.4, g=0, seed=7, ang0=-1.4, ang1=1.0)
    # técnicos do lado de fora
    for i, tx in enumerate((110, 975)):
        run = ramp(t, T_REP - .6, T_REP)
        hero(ctx, tx + (40 if i == 0 else -40) * run, 1190, .72, t, pose=POSES["panic"] if T_POP < tt < T_UP + .6 else POSES["stand"], mood="scared" if T_POP < tt < T_UP else "happy", look=(1 if i == 0 else -1, 0), scarf=False, body=MUTED)
    # bolhas de saliva (no flashback)
    kb = ramp(t, WT(10, "saliva") - .5, WT(10, "saliva") - .1)
    if kb > 0:
        mx, my = head_pt(x, y, rot, 1.15, 0, -66); bubbles(ctx, mx, my, t, T_FB, kb, sc=.6, seed=8)
    cam.restore(ctx)
    return hx_, hy_

def scene_lab(ctx, t):
    background(ctx, t)
    kz = smoother(ramp(t, T_FB + .2, WT(10, "lembra?") + .3))
    hx_, hy_ = head_pt(HX, HY, 0, 1.15, 0, -90)
    cam = Cam(lerp(540, hx_ + 10, kz), lerp(860 + 30 * ramp(t, S(9), S(10)), hy_ + 20, kz), lerp_log(1.0, 3.4, kz), 0, 540, lerp(860, 900, kz))
    lab(ctx, t, cam)
    if t >= T_FB:                                                                     # filtro de lembrança
        kf = ramp(t, T_FB, T_FB + .3)
        ctx.rectangle(0, 0, W, H); fill(ctx, ORBIT, .28 * kf)
        ctx.save(); ctx.rectangle(-20, -20, W + 40, H + 40); ctx.new_sub_path(); ctx.arc(540, 900, 640, 0, 2 * PI); ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.clip()
        ctx.rectangle(-20, -20, W + 40, H + 40); fill(ctx, VOID, .55 * kf); ctx.restore()
        chip(ctx, "ÚLTIMA LEMBRANÇA", 540, 330, ramp(t, T_FB + .1, T_FB + .45), ic="clock-counter-clockwise", col=MUTED)
        chip(ctx, "A SALIVA FERVENDO", 540, 1240, ramp(t, WT(10, "saliva") - .1, WT(10, "saliva") + .25), ic="drop", col=INK)
    else:
        ky = ramp(t, T_Y - .15, T_Y + .9); yr = int(round(lerp(2026, 1966, ease_out(ky, 3))))
        if ky > 0:
            ks = spring(ramp(t, T_Y - .15, T_Y + .35))
            ctx.save(); ctx.translate(540, 300); ctx.scale(max(ks, .4), max(ks, .4)); text(ctx, str(yr), DISP, 130, 0, 0, SOLAR, clamp(ky * 5)); ctx.restore()
        a_ = 1 - ramp(t, T_FB - .2, T_FB)
        chip(ctx, "TESTE DA NASA", 540, 390, ramp(t, WT(9, "NASA") - .1, WT(9, "NASA") + .25) * a_, ic="rocket", col=INK)
        chip(ctx, "SOBREVIVEU", 540, 1240, ramp(t, WT(9, "sobreviveu.") - .05, WT(9, "sobreviveu.") + .3) * a_, ic="check-circle", col=BLUE)

def scene_end(ctx, t):                                   # frases 11 e 12 + final
    end_card(ctx, t, S(11), question=["QUEM VOCÊ CHAMARIA", "PRA TE PUXAR?"], next_title="E se a Lua sumisse?")

SCENES = [(0, 8, scene_space), (9, 10, scene_lab), (11, 12, scene_end)]

CUES = [(lambda: 0.0, "wind", .7), (lambda: .05, "metal", .5), (lambda: .9, "whoosh", .5),
        (lambda: S(1) + .1, "whoosh", .5), (lambda: T_EXH - .05, "wind", .6), (lambda: WT(1, "prender,") - .2, "pop", .5), (lambda: T_TEAR, "glass", .55),
        (lambda: WT(2, "explode.") - .1, "riser", .45), (lambda: WT(2, "explode.") + .45, "pop", .4), (lambda: WT(2, "congela") - .1, "tick", .7),
        (lambda: S(3) + .05, "whoosh", .55), (lambda: T_BOIL - .5, "pop", .4), (lambda: T_BOIL, "pop", .45), (lambda: T_BOIL + .35, "pop", .35),
        (lambda: T_SW0, "riser", .6), (lambda: WT(4, "pele") - .1, "tick", .7), (lambda: T_O2, "tick", .6), (lambda: WT(5, "aguenta...") - .1, "riser", .8),
        (lambda: T_15 - .1, "impact", .8), (lambda: T_DARK, "force", .7), (lambda: T_DARK + .1, "rumble", .4),
        (lambda: T_R0 - .45, "whoosh", .8), (lambda: T_DOOR + .3, "metal", .9), (lambda: T_DOOR + .35, "wind", .5), (lambda: WT(8, "sobreviver.") - .1, "pop", .6),
        (lambda: T_Y - .1, "tick", .8), (lambda: WT(9, "NASA") - .1, "tick", .6), (lambda: T_POP, "glitch", .6), (lambda: T_POP + .02, "wind", .7),
        (lambda: T_REP, "thruster", .4), (lambda: WT(9, "sobreviveu.") - .05, "pop", .7),
        (lambda: T_FB, "whoosh", .5), (lambda: WT(10, "saliva") - .2, "pop", .35), (lambda: WT(10, "fervendo.") - .1, "pop", .3),
        (lambda: S(11) + 1.0, "pop", .7)]
SHAKES = [(lambda: T_TEAR, 5, .25), (lambda: T_15 - .1, 8, .35), (lambda: T_DOOR + .3, 8, .3), (lambda: T_POP, 7, .3)]
