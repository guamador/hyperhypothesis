"""Cenas da Hipótese #04 — E se o Sol virasse um buraco negro?   (motor v4; modelo: videos/03b-tunel-terra-fable)

FÍSICA E FONTES (conferidas em 10/11/2026)
- Raio de Schwarzschild do Sol: Rs = 2GM/c² = 2 · 6,674e-11 · 1,989e30 / (2,998e8)² = 2,95 km -> diâmetro 5,9 km ("bola de 6 km").
- Luz do Sol até a Terra: 1 UA / c = 1,496e11 m / 2,998e8 m/s = 499 s = 8 min 19 s em média (varia de ~8 min 10 s a
  ~8 min 27 s ao longo do ano). "8 minutos e 20 segundos" é o arredondamento usual; o relógio da tela vai até 08:20.
- Fora de uma massa esférica, a gravidade só depende da massa (teorema de Birkhoff): mesma massa -> mesma órbita.
  A mudança de gravidade também viaja à velocidade da luz; chega junto com o apagão e não muda nada.
- A Lua só reflete a luz do Sol: apaga de 1 a ~2,6 s depois (384.400 km / c = 1,28 s por trecho).
- As estrelas continuam no céu: a luz delas não vem do Sol.
- Sem luz: a fotossíntese para; a superfície esfria e os oceanos congelam por cima; o gelo isola a água de baixo, e a vida
  que sobra é a das fontes hidrotermais, que não depende do Sol (Caltech, "If the Sun ceased to exist right now...").
- O Sol não vira buraco negro: precisaria de ~20 vezes mais massa (NASA, "Why the Sun won't become a black hole", 2019).
- Everest: 8.849 m (medição China–Nepal, 2020). Na tela, a bola de 6 km e o Everest estão na mesma escala.
- Fora de escala (de propósito): tamanho do Sol, do buraco negro e da Terra no plano da órbita.
"""
import math, random
import cairocffi as cairo
from hh.anim import *
from hh import fx as _fx
from hh.cam import Cam, lerp_log, smooth, smoother, ramp, pulse, ease_out, ease_in
from hh.hero import hero, POSES, mixpose, flutter

GREEN = hx("2E6B5E")
SAND = mix(SOLAR, VOID, .45)
SEA1 = hx("0B7399")
ZOOM = 0.0                                              # a câmera é das cenas

# ---------------------------------------------------------------- linha do tempo (sincronizada com a fala)
T_P1 = (WT(0, "e", nth=1) - .22, WT(0, "e", nth=1) + .25)     # chicote praia -> Sol
T_COL0 = WT(0, "virasse") - .05                                # o Sol incha (antecipação)...
T_COL1 = WT(0, "buraco") + .10                                 # ...e colapsa: vira buraco negro
T_ZOOM0, T_ZOOM1 = WT(1, "encolhe") - .1, WT(1, "6") - .1      # zoom até a bola de 6 km
T_EV = WT(1, "bola") - .15                                     # Everest entra para dar escala
T_P2 = (S(2) - .32, S(2) + .08)                                # volta para a praia
T_P3 = (S(3) - .32, S(3) + .08)                                # sobe para a órbita
T_IN0, T_IN1 = S(5) - .15, S(6) + .35                          # "Até que...": aproxima da Terra
T_OFF = WT(7, "Apaga")                                         # a frente de escuridão chega: apaga
T_P4 = (T_OFF - .42, T_OFF - .10)                              # desce para a praia logo antes
T_MOON = WT(8, "some") + .05
TAU_END = 500.0                                                # s: 08:20 no relógio

def tau(t):
    """Tempo real desde o colapso (s). Linear: 500 s de verdade em ~20 s de vídeo."""
    return TAU_END * clamp((t - T_COL1) / (T_OFF - T_COL1))

PANS = [(T_P1, "B", "S"), (T_P2, "S", "B"), (T_P3, "B", "S"), (T_P4, "S", "B")]
DPAN = H * 1.15
def pan_state(t):
    """(deslocamento da praia, deslocamento do espaço, intensidade do chicote). Câmera sobe = o mundo desce."""
    cur = "B"
    for (a, b), fr, to in PANS:
        if t < a: break
        if t < b:
            k = smoother((t - a) / (b - a)); m = math.sin(PI * k)
            if fr == "B": return DPAN * k, -DPAN * (1 - k), m
            return DPAN * (1 - k), -DPAN * k, m
        cur = to
    return (0.0, -DPAN * 1.3, 0.0) if cur == "B" else (DPAN * 1.3, 0.0, 0.0)

def vlines(ctx, t, m):
    """Riscos verticais do chicote de câmera."""
    if m < .05: return
    rnd = random.Random(11)
    for i in range(24):
        x = rnd.uniform(20, W - 20); L = (200 + 500 * rnd.random()) * m; y = (rnd.random() * H + t * 4000 * (.6 + rnd.random())) % (H + 600) - 300
        rrect(ctx, x - 3, y, 6, L, 3); fill(ctx, INK, .22 * m)

# ---------------------------------------------------------------- praia
SUN_X, SUN_Y = 840, 640
MOON_X, MOON_Y = 200, 600
_rs = random.Random(7)
NSTARS = [(_rs.uniform(30, W - 30), _rs.uniform(190, 960), _rs.uniform(2.2, 4.6), _rs.uniform(0, 6)) for _ in range(70)]
LIE = dict(arms=(2.75, -2.75), elbows=(1.25, -1.25), legs=(.12, -.05), knees=(-.2, .35))   # deitado, mãos atrás da cabeça
COLD = dict(arms=(.75, -.75), elbows=(-2.1, 2.1), legs=(.06, -.06), knees=(.05, -.05))     # braços cruzados de frio

def sky_sun(ctx, x, y, t, a=1.0, r=96):
    if a <= 0: return
    for rr, al in ((r * 2.0, .05), (r * 1.6, .09), (r * 1.28, .15)): circle(ctx, x, y, rr + 6 * math.sin(t * 2 + rr), SOLAR, al * a)
    ctx.save(); ctx.translate(x, y); ctx.rotate(t * .25)
    for j in range(12):
        ctx.save(); ctx.rotate(j * PI / 6); rrect(ctx, r * 1.24, -7, r * (.46 + .12 * math.sin(t * 3 + j)), 14, 7); fill(ctx, SOLAR, .85 * a); ctx.restore()
    ctx.restore(); circle(ctx, x, y, r, SOLAR, a)

def moon(ctx, x, y, r, a):
    if a <= 0: return
    circle(ctx, x, y, r * 1.25, INK, .06 * a); circle(ctx, x, y, r, INK, .92 * a)
    for dx, dy, rr in ((-.3, -.2, .22), (.28, .1, .16), (-.05, .4, .12), (.36, -.36, .1)): circle(ctx, x + dx * r, y + dy * r, rr * r, MUTED, .55 * a)

def umbrella(ctx, x, y, t, a=1.0, kd=0.0):
    lean = .22 + wobble(t, .035, .9)
    tx, ty = x + math.sin(lean) * 360, y - math.cos(lean) * 360
    ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(x, y); ctx.line_to(tx, ty); ctx.set_source_rgba(*mix(MUTED, VOID, .5 * kd), a); ctx.stroke()
    ctx.save(); ctx.translate(tx, ty); ctx.rotate(lean); ctx.scale(1, .55)
    for j in range(6):
        a0 = PI + j * PI / 6; ctx.move_to(0, 0); ctx.arc(0, 0, 230, a0, a0 + PI / 6); ctx.close_path()
        fill(ctx, mix(RED if j % 2 == 0 else INK, VOID, .55 * kd), a)
    ctx.restore()

def ball(ctx, x, ground, t, a=1.0, damp=1.0):
    h = abs(math.sin(t * 3.2)) * damp; y = ground - 45 - 190 * h; sq = 1 - .2 * clamp(1 - h * 6) * damp
    ctx.save(); ctx.translate(x, y + 45 * (1 - sq)); ctx.scale(1 / math.sqrt(sq), sq); ctx.rotate(t * 2.2 * damp)
    for j in range(6):
        ctx.move_to(0, 0); ctx.arc(0, 0, 45, j * PI / 3, (j + 1) * PI / 3); ctx.close_path(); fill(ctx, (RED, INK, BLUE)[j % 3], a)
    circle(ctx, 0, 0, 9, INK, a); ctx.restore()

def shades(ctx, x, y, s, rot, a=1.0):
    """Óculos escuros na cabeça do hero (mesmo sistema local: cabeça em (0, -90))."""
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    for sx in (-1, 1): rrect(ctx, sx * 15 - 13, -97, 26, 17, 7); fill(ctx, VOID, a)
    rrect(ctx, -5, -93, 10, 4, 2); fill(ctx, VOID, a); ctx.restore()

def beach(ctx, t, off, kd=0.0, sun=True, moon_a=.35, who="lie"):
    """Praia em coordenadas de tela, deslocada `off` px na vertical. kd = 0 dia, 1 escuro."""
    if abs(off) > H * 1.1: return
    ctx.save(); ctx.translate(0, off)
    for x, y, r, ph in NSTARS: circle(ctx, x, y, r, INK, kd * (.55 + .45 * math.sin(t * 2.1 + ph)))     # estrelas aparecem no escuro
    if sun: sky_sun(ctx, SUN_X, SUN_Y, t, 1 - kd)
    moon(ctx, MOON_X, MOON_Y, 62, moon_a)
    for k in range(2): cloud(ctx, 380 + k * 420 + 40 * math.sin(t * .3 + k * 2), 430 + k * 150, .7, MUTED, .35 * (1 - .7 * kd))
    wave(ctx, t, 985, 12, 260, mix(SEA1, VOID, .6 * kd), 1, speed=.5, bottom=1170)
    wave(ctx, t, 1018, 9, 200, mix(BLUE, VOID, .65 * kd), .9, speed=.8, bottom=1170, phase=1.3)
    wave(ctx, t, 1084, 6, 150, INK, .45 * (1 - .6 * kd), speed=1.1, bottom=1100, phase=.6)        # espuma
    rrect(ctx, -20, 1104, W + 40, H, 0); fill(ctx, mix(SAND, VOID, .62 * kd))
    for i, (cx_, cy_) in enumerate(((150, 1330), (900, 1335), (470, 1320))):
        icon(ctx, "star", cx_, cy_, 58, mix(RED if i == 0 else SOLAR if i == 1 else INK, VOID, .55 * kd), .9, "fill", rot=.3 * i)
    rnd = random.Random(3)
    for _ in range(26): circle(ctx, rnd.uniform(0, W), rnd.uniform(1130, 1360), rnd.uniform(3, 6), mix(SOLAR, VOID, .3 + .6 * kd), .5)
    icon(ctx, "tree-palm", 140, 870, 470, mix(GREEN, VOID, .5 * kd), 1, "fill", rot=wobble(t, .03, .7))
    umbrella(ctx, 420, 1186, t, 1, kd)
    rrect(ctx, 540, 1234, 460, 46, 14); fill(ctx, mix(BLUE, VOID, .55 * kd))
    for sx in (600, 920): rrect(ctx, sx, 1234, 26, 46, 0); fill(ctx, mix(INK, VOID, .55 * kd))
    ball(ctx, 260, 1300, t, 1, damp=1.0 if t < T_OFF or who == "relax" else math.exp(-3 * (t - T_OFF)))
    # personagem
    hx0, hy0 = 760, 1190
    if who == "lie" and t >= T_OFF:                                                   # apagou: levanta assustado
        ku = spring(ramp(t, T_OFF + .06, T_OFF + .5)); kc = clamp(ku)
        x, y = lerp(hx0, 735, kc), lerp(hy0, 1092, kc) + wobble(t, 4, 3.0)
        pose = flutter(mixpose(LIE, POSES["panic"], kc), t, .05, f=6)
        mood = "wow" if t > T_MOON else "scared"
        look = (-.8, -1) if t < T_MOON + .9 else (wobble(t, .8, .6), -1)
        hero(ctx, x, y, 1.2, t, pose=pose, mood=mood, look=look, rot=lerp(PI / 2, -.12, kc))
        g = ramp(t, T_OFF + .06, T_OFF + .45)                                         # óculos caem na toalha
        gx, gy = lerp(hx0 + 104, 850, g), lerp(hy0 - 14, 1250, g * g)
        ctx.save(); ctx.translate(gx, gy); ctx.rotate(g * 2.2)
        for sx in (-1, 1): rrect(ctx, sx * 15 - 13, -8, 26, 17, 7); fill(ctx, VOID, 1)
        ctx.restore()
    else:
        thumbs = who == "relax" or S(2) - .1 < t < S(3) + .2
        k = smooth(ramp(t, S(2) + .2, S(2) + .55)) * (1 - smooth(ramp(t, S(3) - .1, S(3) + .2))) if who == "lie" else smooth(ramp(t, S(11) + .2, S(11) + .6))
        arm = mixpose(LIE, dict(arms=(PI / 2 + .25 * math.sin(t * 7), -2.75), elbows=(.15, -1.25), legs=LIE["legs"], knees=LIE["knees"]), k)
        arm["knees"] = (-.25 + .3 * math.sin(t * 3.4), .35)                         # balança o pé
        hands = hero(ctx, hx0, hy0 + wobble(t, 2, .8), 1.2, t, pose=arm, mood="happy", look=(.3, -.5), rot=PI / 2)
        shades(ctx, hx0, hy0 + wobble(t, 2, .8), 1.2, PI / 2)
        if thumbs and k > .05: icon(ctx, "thumbs-up", hands[0][0], hands[0][1] - 26, 74 * k, INK, 1, "fill")
    ctx.restore()

# ---------------------------------------------------------------- espaço 1: o Sol de perto e o colapso
RS_W, RBH_W = 70.0, 3.5                                  # mundo: raio do Sol (fora de escala) e da bola de 6 km
KM = 2 * RBH_W / 6.0                                     # unidades do mundo por km (para o Everest)
_rg = random.Random(5)
GRAN = [(_rg.uniform(0, 2 * PI), math.sqrt(_rg.random()) * .86, _rg.uniform(.05, .11)) for _ in range(34)]
PART = [(_rg.uniform(0, 2 * PI), _rg.uniform(1.3, 2.6), _rg.uniform(0, .25)) for _ in range(64)]

def sun_r(t):
    if t < T_COL0: return RS_W * (1 + .015 * math.sin(t * 5))
    if t < T_COL0 + .2: return RS_W * (1 + .09 * smooth(ramp(t, T_COL0, T_COL0 + .2)))
    return lerp(RS_W * 1.09, RBH_W, ease_in(ramp(t, T_COL0 + .2, T_COL1), 3))

def sun_cam(t, off):
    k0 = ramp(t, T_P1[1], T_ZOOM0); kz = smoother(ramp(t, T_ZOOM0, T_ZOOM1))
    z = lerp_log(lerp(4.0, 4.25, k0), 48.0, kz)
    return Cam(5.5 * kz, 0.0, z, 0, 540, 900 + off)

def draw_bh(ctx, x, y, r, t, a=1.0):
    """Buraco negro sem disco (não há matéria caindo): horizonte escuro, anel de fótons e lente."""
    for k, al in ((2.6, .07), (2.0, .10)):
        ctx.set_line_width(max(1.5, r * .06)); ctx.new_sub_path(); ctx.arc(x, y, r * k, 0, 2 * PI); ctx.set_source_rgba(*INK, al * a); ctx.stroke()
    for j in range(3):                                                               # arcos de lente girando
        a0 = t * (.6 + .25 * j) + j * 2.1
        ctx.set_line_width(max(2, r * .08)); ctx.new_sub_path(); ctx.arc(x, y, r * (1.62 + .12 * j), a0, a0 + 1.7); ctx.set_source_rgba(*BLUE, .45 * a); ctx.stroke()
    ctx.set_line_width(max(2.5, r * .13)); ctx.new_sub_path(); ctx.arc(x, y, r * 1.5, 0, 2 * PI); ctx.set_source_rgba(*BLUE, .9 * a); ctx.stroke()
    circle(ctx, x, y, r * 1.08, VOID, a); circle(ctx, x, y, r, VOID, a)

def sun_view(ctx, t, off):
    if abs(off) > H * 1.1: return
    cam = sun_cam(t, off); x, y = cam.pt(0, 0); z = cam.z
    if t < T_COL1:
        r = sun_r(t) * z; kc = ramp(t, T_COL0 + .2, T_COL1)
        for rr, al in ((1.55, .05), (1.3, .09), (1.14, .16)): circle(ctx, x, y, r * rr * (1 + .02 * math.sin(t * 3 + rr)), SOLAR, al * (1 - kc))
        ctx.save(); ctx.translate(x, y); ctx.rotate(t * .12)
        for j in range(5):                                                           # proeminências na borda
            a0 = j * 1.26 + .3 * math.sin(t * .8 + j); hh_ = r * (.12 + .05 * math.sin(t * 1.7 + j * 2))
            ctx.set_line_width(max(3, r * .035)); ctx.new_sub_path(); ctx.arc(r * math.cos(a0), r * math.sin(a0), hh_, a0 - PI / 2, a0 + PI / 2)
            ctx.set_source_rgba(*RED, .8 * (1 - kc)); ctx.stroke()
        ctx.restore()
        circle(ctx, x, y, r, mix(SOLAR, RED, kc), 1)
        for ang, fr, sz in GRAN:
            a2 = ang + t * .05
            circle(ctx, x + math.cos(a2) * fr * r, y + math.sin(a2) * fr * r, sz * r * (1 + .25 * math.sin(t * 2.3 + ang * 5)), mix(hx("FF8A3D"), RED, kc), .45)
        if kc > 0:                                                                   # matéria sendo sugada para o centro
            for ang, r0, d in PART:
                kk = ease_in(ramp(t, T_COL0 + .2 + d * .5, T_COL1), 2)
                if 0 < kk < 1:
                    rr = lerp(r0 * RS_W, 0, kk) * z; px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr
                    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(px, py)
                    ctx.line_to(px + math.cos(ang) * 60 * kk, py + math.sin(ang) * 60 * kk); ctx.set_source_rgba(*SOLAR, .9); ctx.stroke()
        return
    rb = RBH_W * z
    ke = ramp(t, T_EV, T_EV + .5)
    if ke > 0:                                                                       # Everest na mesma escala
        g = RBH_W
        prof = [(4.2, g), (7.2, g - 5.2), (8.6, g - 4.6), (11.5, g - 8.849 * KM), (13.9, g - 6.3), (15.5, g - 7.0), (20.0, g)]
        ctx.move_to(*cam.pt(*prof[0]))
        for p in prof[1:]: ctx.line_to(*cam.pt(*p))
        ctx.close_path(); fill(ctx, MUTED, ke)
        sh = [(11.5, g - 8.849 * KM), (13.9, g - 6.3), (15.5, g - 7.0), (20.0, g), (12.1, g)]
        ctx.move_to(*cam.pt(*sh[0]))
        for p in sh[1:]: ctx.line_to(*cam.pt(*p))
        ctx.close_path(); fill(ctx, ORBIT, .55 * ke)
        pk = (11.5, g - 8.849 * KM)
        cap = [(10.2, pk[1] + 2.0), pk, (12.8, pk[1] + 2.2), (12.0, pk[1] + 1.6), (11.5, pk[1] + 2.3), (10.9, pk[1] + 1.5)]
        ctx.move_to(*cam.pt(*cap[0]))
        for p in cap[1:]: ctx.line_to(*cam.pt(*p))
        ctx.close_path(); fill(ctx, INK, ke)
        gx0, gy0 = cam.pt(-30, g); ctx.rectangle(-20, gy0, W + 40, H); fill(ctx, ORBIT, ke)
        ctx.rectangle(-20, gy0, W + 40, 8); fill(ctx, LINE, ke)
        px_, py_ = cam.pt(*pk)
        if z > 30: chip(ctx, "EVEREST", px_, py_ - 70, ramp(t, T_EV + .2, T_EV + .6), ic="mountains", col=INK, size=38)
    kg = ramp(t, T_COL1 + .2, T_COL1 + .7) * (1 - ramp(t, T_ZOOM0, T_ZOOM0 + .4))
    if kg > 0:                                                                       # onde ficava a borda do Sol
        ctx.set_dash([14, 12], t * 20); ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(x, y, RS_W * z, 0, 2 * PI)
        ctx.set_source_rgba(*MUTED, .7 * kg); ctx.stroke(); ctx.set_dash([])
        chip(ctx, "ERA O TAMANHO DO SOL", 540, y - RS_W * z - 70, kg, col=MUTED, size=36)
    draw_bh(ctx, x, y, max(rb, 44), t)
    if t < T_COL1 + .35: circle(ctx, x, y, 90 * (1 - ramp(t, T_COL1, T_COL1 + .35)), INK, 1 - ramp(t, T_COL1, T_COL1 + .35))   # clarão
    shockwave(ctx, x, y, T_COL1, t, r1=560, life=.8, col=BLUE, w=9)
    sparks(ctx, x, y, T_COL1, t, n=22, col=BLUE, speed=900, life=.6, g=0, seed=4, ang0=-PI, ang1=PI)
    k6 = spring(ramp(t, WT(1, "6") - .15, WT(1, "6") + .35))
    if k6 > 0 and z > 30:                                                            # cota de 6 km
        y0 = y + rb + 54; x1, x2 = x - rb, x - rb + 2 * rb * clamp(k6)
        ctx.set_line_width(5); ctx.move_to(x1, y0); ctx.line_to(x2, y0); ctx.set_source_rgba(*SOLAR, 1); ctx.stroke()
        for xx in (x1, x2): rrect(ctx, xx - 3, y0 - 18, 6, 36, 3); fill(ctx, SOLAR, clamp(k6))
        ks6 = max(k6, 37 / 68); ctx.save(); ctx.translate(x, y0 + 92); ctx.scale(ks6, ks6); text(ctx, "6 km", DISP, 68, 0, 0, SOLAR, clamp(k6 * 4)); ctx.restore()
    kz = ramp(t, T_ZOOM0, T_ZOOM1)
    if 0 < kz and t < T_EV + .4:                                                      # mergulho de zoom + diâmetro encolhendo
        rnd = random.Random(13); m = math.sin(PI * kz)
        ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(40):
            ang = rnd.uniform(0, 2 * PI); r0 = rb * 1.8 + ((rnd.random() * 900 - t * 1400) % 900); L = 80 + 160 * rnd.random()
            ctx.move_to(x + math.cos(ang) * r0, y + math.sin(ang) * r0); ctx.line_to(x + math.cos(ang) * (r0 + L * m), y + math.sin(ang) * (r0 + L * m))
        ctx.set_source_rgba(*INK, .25 * m); ctx.stroke()
        ad = 1 - ramp(t, T_EV, T_EV + .4)
        d = lerp_log(1391400.0, 6.0, smoother(kz))
        text(ctx, "DIÂMETRO", BOLD, 38, 540, 1180 + off, MUTED, ad, track=.06)
        text(ctx, counter(round(d)) + " km", DISP, 84, 540, 1290 + off, SOLAR, ad)
    off_m = 1 - ramp(t, T_ZOOM0 - .2, T_ZOOM0 + .1)
    chip(ctx, "MESMA MASSA", 540, 1250 + off, ramp(t, WT(1, "mesma") - .1, WT(1, "mesma") + .35) * off_m, ic="scales", col=SOLAR)

# ---------------------------------------------------------------- espaço 2: a órbita e a frente de escuridão
RO, EA, ER = 430.0, .88, 46.0
EX, EY = RO * math.cos(EA), RO * math.sin(EA)
V_FRONT = RO / (T_OFF - T_COL1)                          # mundo/s: luz (e escuridão) a 'c' na escala do vídeo

def orbit_cam(t, off):
    k0 = smoother(ramp(t, T_P3[0], T_P3[1] + 1.0)); ki = smoother(ramp(t, T_IN0, T_IN1))
    z = lerp_log(lerp(1.35, 1.0, k0), 2.3, ki)
    return Cam(EX * .8 * ki, EY * .8 * ki, z, 0, 540, 780 + 140 * ki + off)

def orbit_view(ctx, t, off):
    if abs(off) > H * 1.1: return
    cam = orbit_cam(t, off); z = cam.z; bx, by = cam.pt(0, 0)
    rf = (RO - ER) * tau(t) / TAU_END                    # a frente só encosta na Terra quando o relógio bate 08:20
    rfp = rf * z
    # luz que já estava a caminho: preenche tudo fora da frente e corre para fora junto com ela
    ctx.save(); ctx.rectangle(-50, -50, W + 100, H + 100); ctx.new_sub_path(); ctx.arc(bx, by, rfp, 0, 2 * PI)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); ctx.clip()
    ctx.rectangle(-50, -50, W + 100, H + 100); fill(ctx, SOLAR, .08)
    ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for j in range(60):
        ang = j * 2 * PI / 60 + .03 * math.sin(j * 7.0)
        for m in range(9):
            d = ((j * 37) % 110) + m * 110
            r1 = rf + d; r2 = r1 + 16
            ctx.move_to(bx + math.cos(ang) * r1 * z, by + math.sin(ang) * r1 * z); ctx.line_to(bx + math.cos(ang) * r2 * z, by + math.sin(ang) * r2 * z)
    ctx.set_source_rgba(*SOLAR, .55); ctx.stroke()
    ctx.restore()
    # órbita (e a "fantasma" do seg. 4: igualzinha)
    ctx.set_line_width(3); ctx.new_sub_path(); ctx.arc(bx, by, RO * z, 0, 2 * PI); ctx.set_source_rgba(*LINE, .9); ctx.stroke()
    ko = ramp(t, WT(4, "órbita") - .1, WT(4, "órbita") + .3) * (1 - ramp(t, S(5) - .1, S(5) + .3))
    if ko > 0:
        ctx.set_dash([22, 16], -t * 60); ctx.set_line_width(7); ctx.new_sub_path(); ctx.arc(bx, by, RO * z, 0, 2 * PI)
        ctx.set_source_rgba(*BLUE, .9 * ko); ctx.stroke(); ctx.set_dash([])
    # Terra (lado dia virado para o buraco negro)
    ex, ey = cam.pt(EX, EY); er = ER * z
    globe(ctx, ex, ey, er, lon0=-60 + t * 4, lat0=-12)
    ctx.save(); ctx.new_sub_path(); ctx.arc(ex, ey, er, 0, 2 * PI); ctx.clip(); ctx.translate(ex, ey); ctx.rotate(EA)
    ctx.rectangle(er * .05, -er, er * 1.2, 2 * er); fill(ctx, VOID, .4); ctx.restore()
    ctx.set_line_width(max(4, er * .1)); ctx.new_sub_path(); ctx.arc(ex, ey, er * 1.02, EA + PI - 1.3, EA + PI + 1.3); ctx.set_source_rgba(*SOLAR, .9); ctx.stroke()   # borda iluminada
    circle(ctx, ex, ey, er * 1.35, SOLAR, .10)
    # escuridão
    if rfp > 1:
        circle(ctx, bx, by, rfp, VOID, .88)
        ctx.set_line_width(18); ctx.new_sub_path(); ctx.arc(bx, by, rfp, 0, 2 * PI); ctx.set_source_rgba(*SOLAR, .14); ctx.stroke()
        ctx.set_line_width(5); ctx.new_sub_path(); ctx.arc(bx, by, rfp, 0, 2 * PI); ctx.set_source_rgba(*SOLAR, .9); ctx.stroke()
    ctx.set_dash([6, 10]); ctx.set_line_width(3); ctx.new_sub_path(); ctx.arc(bx, by, 40 * z, 0, 2 * PI); ctx.set_source_rgba(*MUTED, .5); ctx.stroke(); ctx.set_dash([])   # onde era o Sol
    draw_bh(ctx, bx, by, 9 * math.sqrt(z), t)
    # etiquetas
    kz = 1 - ramp(t, T_IN0 - .2, T_IN0 + .2)
    du = (-.72, -.69)
    if rfp > 200:
        cx_ = clamp(bx + du[0] * (rfp - 40), 230, 850); cy_ = clamp(by + du[1] * (rfp - 40), 470 + off, 1290 + off)
        chip(ctx, "ESCURIDÃO", cx_, cy_, ramp(t, S(3) + 1.6, S(3) + 2.0) * kz, ic="moon", col=INK, size=38)
    chip(ctx, "LUZ A CAMINHO", 740, ey + er + 110, ramp(t, WT(3, "caminho") - .1, WT(3, "caminho") + .3) * (1 - ramp(t, S(4) - .1, S(4) + .2)), ic="sun", col=SOLAR, size=38)
    kg = spring(ramp(t, WT(4, "não") - .1, WT(4, "não") + .4)) * kz
    if kg > 0:
        dx, dy = -math.cos(EA), -math.sin(EA); s0 = er + 14; L = 150 * clamp(kg)
        arrow(ctx, ex + dx * s0, ey + dy * s0, ex + dx * (s0 + L), ey + dy * (s0 + L), RED, clamp(kg), w=12, head=34)
        chip(ctx, "MESMA GRAVIDADE", 700, ey + er + 110, ramp(t, WT(4, "não") - .1, WT(4, "não") + .35) * kz, ic="arrow-down-left", col=RED, size=38)
    chip(ctx, "ÓRBITA IGUAL", 300, by + 360, ko * kz, ic="check-circle", col=BLUE, size=38)
    pop_text_fit(ctx, "8 MIN 20 S", DISP, 140, 540, 640 + off, SOLAR, t, WT(6, "8") - .12, a=1 - ramp(t, T_P4[0] - .1, T_P4[0] + .1), stagger=.04)

def clock_hud(ctx, t, a):
    if a <= 0: return
    late = t >= T_OFF
    rrect(ctx, 50, 205, 980, 180, 28); fill(ctx, ORBIT, .93 * a)
    icon(ctx, "timer", 124, 296, 72, RED if late else SOLAR, a, "fill")
    ks = 1 + .08 * pulse(t, T_OFF, .08, .1, .4)
    ctx.save(); ctx.translate(184, 332); ctx.scale(ks, ks); text(ctx, fmt_clock(tau(t)), DISP, 100, 0, 0, RED if late else SOLAR, a, "l"); ctx.restore()
    text(ctx, "DESDE O", BOLD, 36, 996, 286, MUTED, a, "r", .04)
    text(ctx, "COLAPSO", BOLD, 36, 996, 340, INK, a, "r", .04)

# ---------------------------------------------------------------- cena 1: praia <-> espaço, um chicote de câmera por mudança (frases 0 a 8)
def scene_take(ctx, t):
    background(ctx, t)
    ob, os_, m = pan_state(t)
    kd = 1.0 if t >= T_OFF else 0.0
    ma = .35 if t < T_OFF else (1 - ramp(t, T_MOON, T_MOON + .18))
    beach(ctx, t, ob, kd=kd, moon_a=ma)
    if t < T_P3[0]: sun_view(ctx, t, os_)
    else: orbit_view(ctx, t, os_)
    vlines(ctx, t, m)
    if T_OFF <= t < T_OFF + .9:                                                      # o Sol some de uma vez: fica o contorno
        ka = 1 - ramp(t, T_OFF, T_OFF + .9); ctx.set_line_width(5); ctx.new_sub_path(); ctx.arc(SUN_X, SUN_Y + ob, 96, 0, 2 * PI); ctx.set_source_rgba(*SOLAR, .7 * ka); ctx.stroke()
    if T_MOON <= t < T_MOON + .5: burst(ctx, MOON_X, MOON_Y + ob, (t - T_MOON) / .5, INK, n=10, r0=70, r1=140, w=5)
    chip(ctx, "AS ESTRELAS FICAM", 540, 800 + ob, ramp(t, WT(8, "depois.") - .1, WT(8, "depois.") + .3), ic="sparkle", col=INK, size=38)
    # títulos da pergunta (2 linhas por vez)
    a1 = 1 - ramp(t, T_P1[0] - .1, T_P1[0] + .15)
    pop_text_fit(ctx, "E SE VOCÊ ESTIVESSE", DISP, 70, 540, 250, INK, t, 0.0, a=a1, stagger=.02, dur=.3)
    pop_text_fit(ctx, "TOMANDO SOL...", DISP, 100, 540, 368, SOLAR, t, WT(0, "tomando") - .2, a=a1, stagger=.025)
    a2 = 1 - ramp(t, S(1) + .2, S(1) + .5)
    pop_text_fit(ctx, "...E O SOL VIRASSE", DISP, 70, 540, 250, INK, t, T_P1[0] + .1, a=a2, stagger=.02, dur=.3)
    pop_text_fit(ctx, "UM BURACO NEGRO?", DISP, 92, 540, 365, BLUE, t, WT(0, "buraco") - .2, a=a2, stagger=.025)
    clock_hud(ctx, t, ramp(t, S(3) - .1, S(3) + .3) * (1 - ramp(t, T_OFF + 1.2, T_OFF + 1.6)))

# ---------------------------------------------------------------- cena 2: sem luz, o mar congela e a vida desce (frases 9 e 10)
FLOOR, SHORE = 2300.0, 360
T_LEAF = WT(9, "para,") - .1
T_ICE0, T_ICE1 = WT(9, "congelar") - .25, WT(9, "cima.") + .7
T_DOWN0, T_DOWN1 = WT(10, "vida") - .3, WT(10, "fundo") + .55
_rw = random.Random(9)
WORMS = [(x, _rw.uniform(40, 95), _rw.uniform(0, 6)) for x in list(range(590, 665, 13)) + list(range(790, 870, 13))]
FISH = [(260, .55, 0.0, 80), (190, -.42, 2.0, 66), (330, .33, 4.1, 72)]

def vent(ctx, x, top, w0, w1, t, a=1.0, seed=0):
    ctx.move_to(x - w0 / 2, FLOOR + 10)
    n = 7
    for i in range(1, n + 1):
        u = i / n; ctx.line_to(x - lerp(w0, w1, u) / 2 + (8 if i % 2 else -6), FLOOR + 10 - (FLOOR + 10 - top) * u)
    for i in range(n, -1, -1):
        u = i / n; ctx.line_to(x + lerp(w0, w1, u) / 2 + (-7 if i % 2 else 6), FLOOR + 10 - (FLOOR + 10 - top) * u)
    ctx.close_path(); fill(ctx, MUTED, a)
    ctx.set_line_width(4)
    for i in range(3):
        yy = lerp(FLOOR, top, .25 + .22 * i); ctx.move_to(x - 14, yy); ctx.line_to(x + 6, yy - 20); ctx.line_to(x + 16, yy - 8)
    ctx.set_source_rgba(*RED, (.6 + .3 * math.sin(t * 4 + seed)) * a); ctx.stroke()
    circle(ctx, x, top - 4, 120 + 10 * math.sin(t * 3), RED, .10 * a); circle(ctx, x, top - 4, 58 + 6 * math.sin(t * 5), SOLAR, .24 * a)
    for k in range(7):                                                               # fumaça preta contínua
        t0 = (math.floor(t / .32) - k) * .32
        smoke(ctx, x, top - 10, t0, t, n=3, col=MUTED, life=2.4, spread=80, rise=620, r0=22, r1=110, a=.75, seed=(int(t0 * 31) + seed) % 97, wind=25)

def scene_freeze(ctx, t):
    background(ctx, t)
    kdn = smoother(ramp(t, T_DOWN0, T_DOWN1)); cy = lerp(0, FLOOR - 220, kdn) + wobble(t, 5, .4)
    dy = 1080 - cy
    kp = ease_out(ramp(t, T_LEAF - .3, T_LEAF + 1.2), 2)                              # plantas morrendo
    ki = ramp(t, T_ICE0, T_ICE1)                                                       # gelo
    ctx.save(); ctx.translate(0, dy)
    # neve no ar
    ks = ramp(t, S(9) + .5, S(9) + 1.5); rnd = random.Random(21)
    for i in range(36):
        sp = .6 + rnd.random(); x = rnd.uniform(0, W) + 30 * math.sin(t * 1.1 + i); y = -1000 + ((rnd.random() * 1000 + t * 120 * sp) % 1000)
        icon(ctx, "snowflake", x, y, 26 + 18 * rnd.random(), INK, .7 * ks, "fill", rot=t * sp)
    # mar
    ctx.rectangle(SHORE - 20, -20, W - SHORE + 40, FLOOR + 60); fill(ctx, _fx.OCEAN_COL)
    for y0, al in ((500, .22), (1200, .25), (1800, .25)): ctx.rectangle(SHORE - 20, y0, W - SHORE + 40, FLOOR + 60 - y0); fill(ctx, VOID, al)
    amp = 10 * (1 - ki)
    wave(ctx, t, -6, amp, 220, SEA1, 1, speed=.5, x0=SHORE - 20, x1=W + 20, bottom=40)
    wave(ctx, t, 16, amp * .8, 170, BLUE, .7, speed=.8, x0=SHORE - 20, x1=W + 20, bottom=40, phase=1.3)
    if ki > 0:                                                                         # gelo cresce da praia para o mar e engrossa
        wi = (W - SHORE + 30) * ease_out(ki, 2); th = 16 + 64 * ki
        rrect(ctx, SHORE - 20, -16, wi, th, 10); fill(ctx, mix(INK, BLUE, .22), .93)
        ctx.set_line_width(3); rnd = random.Random(2)
        for _ in range(9):
            x0 = SHORE + rnd.random() * (W - SHORE)
            if x0 < SHORE - 20 + wi - 20:
                ctx.move_to(x0, -14); ctx.line_to(x0 + rnd.uniform(-30, 30), -14 + th * .5); ctx.line_to(x0 + rnd.uniform(-40, 40), -16 + th)
        ctx.set_source_rgba(*LINE, .7); ctx.stroke()
        ex_ = SHORE - 20 + wi
        if ki < 1: sparks(ctx, ex_, -10, t - .1, t + .001, n=5, col=INK, speed=240, life=.3, seed=int(t * 30))
    rnd = random.Random(17)                                                            # neve marinha e águas-vivas na descida
    for i in range(70):
        x = rnd.uniform(SHORE, W); y = 120 + ((rnd.random() * (FLOOR - 200) + t * 25) % (FLOOR - 200))
        circle(ctx, x + 6 * math.sin(t + i), y, rnd.uniform(2, 4), INK, .3)
    for i, (jx, jy) in enumerate(((560, 820), (880, 1200), (640, 1580))):
        jy += 30 * math.sin(t * 1.4 + i * 2); pu = 1 + .12 * math.sin(t * 3 + i)
        ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(5):
            tx0 = jx - 40 + k * 20; ctx.move_to(tx0, jy)
            for u in range(1, 6): ctx.line_to(tx0 + 10 * math.sin(t * 3 + u + k), jy + u * 26)
        ctx.set_source_rgba(*BLUE, .55); ctx.stroke()
        ctx.save(); ctx.translate(jx, jy); ctx.scale(pu, 1 / pu); ctx.new_sub_path(); ctx.arc(0, 0, 58, PI, 2 * PI); ctx.close_path(); fill(ctx, BLUE, .7); ctx.restore()
        circle(ctx, jx, jy - 20, 60, BLUE, .08)
    # bolhas e peixes
    rnd = random.Random(4)
    for i in range(16):
        x = 520 + rnd.uniform(-160, 420) + 14 * math.sin(t * 2 + i); y = FLOOR - 280 - ((rnd.random() * 2000 + t * 110 * (.7 + rnd.random())) % 2000)
        if y > 90:
            ctx.set_line_width(3); ctx.new_sub_path(); ctx.arc(x, y, 7 + 6 * rnd.random(), 0, 2 * PI); ctx.set_source_rgba(*INK, .35); ctx.stroke()
    for rr, w, ph, sz in FISH:
        ang = ph + w * t; x = 730 + rr * 1.35 * math.cos(ang); y = FLOOR - 470 + rr * .7 * math.sin(ang)
        x = clamp(x, SHORE + 50, W - 40); icon(ctx, "fish", x, y, sz, BLUE, .95, "fill", flip=(w * math.sin(ang) > 0))
    for i in range(4):                                                                # cardume sob o gelo
        x = (SHORE + 80 + ((i * 170 + t * 60) % (W - SHORE - 40))); y = 160 + 60 * i + 14 * math.sin(t * 2 + i)
        icon(ctx, "fish-simple", x, y, 56, INK, .5, "fill")
    # fundo do mar, fontes e vermes
    ctx.move_to(SHORE - 20, FLOOR + 30)
    for i in range(13): ctx.line_to(SHORE + i * 60, FLOOR + 18 * math.sin(i * 1.7))
    ctx.line_to(W + 20, FLOOR); ctx.line_to(W + 20, FLOOR + 900); ctx.line_to(SHORE - 20, FLOOR + 900); ctx.close_path(); fill(ctx, ORBIT)
    vent(ctx, 720, FLOOR - 400, 190, 64, t, seed=1); vent(ctx, 950, FLOOR - 210, 120, 46, t, seed=5)
    for x, h, ph in WORMS:
        lean = .18 * math.sin(t * 1.6 + ph); tx, ty = x + math.sin(lean) * h, FLOOR + 4 - math.cos(lean) * h
        ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(x, FLOOR + 6); ctx.line_to(tx, ty); ctx.set_source_rgba(*INK, .9); ctx.stroke()
        circle(ctx, tx, ty, 10, RED, 1)
    for i, x0 in enumerate((560, 850)):
        icon(ctx, "shrimp", x0 + 40 * math.sin(t * .7 + i * 2), FLOOR - 24, 64, RED, 1, "fill", flip=i == 1)
    # terra firme: penhasco, grama, árvore e planta morrendo, personagem com frio
    ctx.move_to(-20, -46); ctx.line_to(SHORE - 10, -46); ctx.line_to(SHORE + 20, 200); ctx.line_to(SHORE - 30, 700); ctx.line_to(SHORE + 10, FLOOR + 900); ctx.line_to(-20, FLOOR + 900); ctx.close_path(); fill(ctx, ORBIT)
    rrect(ctx, -20, -58, SHORE + 10, 22, 10); fill(ctx, mix(GREEN, MUTED, kp))
    leaf = mix(GREEN, MUTED, kp)
    tree(ctx, 95, -46, 1.6, col=leaf, lean=wobble(t, .05) - .1 * kp)
    icon(ctx, "plant", 330, -100, 100, leaf, 1, "fill", rot=.55 * kp)
    rnd = random.Random(8)
    for i in range(9):                                                                # folhas caindo
        t0 = T_LEAF + i * .17; u = ramp(t, t0, t0 + 1.5)
        if 0 < u < 1:
            x = 90 + rnd.uniform(-90, 90) + 50 * math.sin(u * 7 + i); y = lerp(-300 + rnd.uniform(-40, 40), -60, u)
            icon(ctx, "leaf", x, y, 40, mix(GREEN, MUTED, u), 1 - ramp(u, .85, 1), "fill", rot=u * 5 + i)
    sh = 3.5 * math.sin(t * 42) * ramp(t, S(9) + .4, S(9) + 1.2)
    hero(ctx, 236 + sh, -162, 1.25, t, pose=flutter(COLD, t, .03, f=30), mood="scared", look=(.8, .2 + wobble(t, .2)), squash=.97)
    t0b = math.floor(t / 1.3) * 1.3                                                    # bafo de frio
    smoke(ctx, 270, -250, t0b, t, n=4, col=INK, life=1.1, spread=26, rise=50, r0=6, r1=24, a=.35, wind=60, seed=int(t0b * 10) % 50)
    ctx.restore()
    # etiquetas (tela)
    af = 1 - ramp(t, T_DOWN0 - .2, T_DOWN0 + .2)
    chip(ctx, "SEM FOTOSSÍNTESE", 500, 330, ramp(t, WT(9, "fotossíntese") - .1, WT(9, "fotossíntese") + .3) * af, ic="leaf", col=MUTED)
    chip(ctx, "OCEANO CONGELANDO", 560, 520, ramp(t, T_ICE0, T_ICE0 + .4) * af, ic="snowflake", col=BLUE)
    lvl = lerp(.78, .1, ease_out(ramp(t, S(9) + .3, E(9)), 2)); ct = mix(RED, BLUE, ramp(t, S(9) + .3, E(9)))
    if af > 0:
        ctx.set_line_width(5); rrect(ctx, 942, 610, 36, 300, 18); ctx.set_source_rgba(*INK, af); ctx.stroke()
        rrect(ctx, 951, 610 + 300 * (1 - lvl), 18, 300 * lvl + 10, 9); fill(ctx, ct, af); circle(ctx, 960, 935, 34, ct, af)
        for i in range(5): rrect(ctx, 990, 640 + i * 55, 22, 5, 2); fill(ctx, MUTED, af)
    ad = ramp(t, T_DOWN1 - .5, T_DOWN1)
    chip(ctx, "VIDA SEM SOL", 330, 430, ramp(t, WT(10, "mar,") - .2, WT(10, "mar,") + .2) * ad, ic="fish", col=BLUE)
    chip(ctx, "FONTES QUENTES", 330, 570, ramp(t, WT(10, "fontes") - .1, WT(10, "fontes") + .3) * ad, ic="flame", col=SOLAR)

# ---------------------------------------------------------------- cena 3: relaxa, o Sol é leve demais (frase 11)
def balance(ctx, t, t0, ttilt):
    k = spring(ramp(t, t0, t0 + .7))
    if k <= 0: return
    px, py = 540, lerp(-320, 430, k)
    th = .21 * spring(ramp(t, ttilt, ttilt + .8)) + wobble(t, .012, 1.2)
    ctx.set_line_width(8); ctx.move_to(px, -40); ctx.line_to(px, py); ctx.set_source_rgba(*MUTED, 1); ctx.stroke()
    c, s = math.cos(th), math.sin(th); L = 330
    ends = [(px - L * c, py - L * s), (px + L * c, py + L * s)]
    ctx.save(); ctx.translate(px, py); ctx.rotate(th); rrect(ctx, -L - 10, -10, 2 * L + 20, 20, 10); fill(ctx, INK); ctx.restore()
    circle(ctx, px, py, 22, SOLAR); circle(ctx, px, py, 9, VOID)
    for j, (ex, ey) in enumerate(ends):
        bx, by = ex, ey + 170
        ctx.set_line_width(4); ctx.move_to(ex, ey); ctx.line_to(bx - 105, by); ctx.move_to(ex, ey); ctx.line_to(bx + 105, by); ctx.set_source_rgba(*MUTED, 1); ctx.stroke()
        rrect(ctx, bx - 120, by - 4, 240, 20, 10); fill(ctx, INK)
        if j == 0:
            sky_sun(ctx, bx, by - 64, t, 1, r=56)
            text(ctx, "SOL", BOLD, 40, bx, by + 74, INK)
        else:
            for n in range(20):
                cx, cy = bx - 76 + (n % 5) * 38, by - 20 - (n // 5) * 37
                circle(ctx, cx, cy, 16, SOLAR); circle(ctx, cx, cy, 22, SOLAR, .14)
            text(ctx, "UNS 20 SÓIS", BOLD, 40, bx, by + 74, SOLAR)

def scene_relax(ctx, t):
    background(ctx, t)
    beach(ctx, t, 0, kd=0.0, sun=False, moon_a=0.0, who="relax")
    pop_text_fit(ctx, "RELAXA", DISP, 104, 540, 260, BLUE, t, WT(11, "relaxa:") - .1, stagger=.04)
    balance(ctx, t, WT(11, "Sol") - .35, WT(11, "demais") - .05)
    chip(ctx, "LEVE DEMAIS", 300, 770, ramp(t, WT(11, "leve") - .1, WT(11, "leve") + .3), ic="feather", col=RED)

def scene_end(ctx, t):                                   # frases 12 e 13 + final
    end_card(ctx, t, S(12), question=["O QUE VOCÊ FARIA", "NOS ÚLTIMOS 8 MIN?"], next_title="E se você ficasse no espaço sem traje?")

SCENES = [(0, 8, scene_take), (9, 10, scene_freeze), (11, 11, scene_relax), (12, 13, scene_end)]

CUES = [(lambda: math.pi / 3.2, "pop", .35), (lambda: 2 * math.pi / 3.2, "pop", .3),
        (lambda: T_P1[0] - .05, "whoosh", .9), (lambda: T_COL0 - .55, "riser", .7), (lambda: T_COL1 - .08, "force", .9), (lambda: T_COL1, "boom", .6),
        (lambda: WT(1, "mesma") - .1, "tick", .8), (lambda: T_ZOOM0, "whoosh", .6), (lambda: T_EV + .2, "pop", .6), (lambda: WT(1, "6") - .15, "tick", .9),
        (lambda: T_P2[0] - .05, "whoosh", .9), (lambda: S(2) + .25, "pop", .5), (lambda: T_P3[0] - .05, "whoosh", .9), (lambda: S(3) + .3, "wind", .45),
        (lambda: WT(3, "caminho") - .1, "tick", .7), (lambda: WT(4, "não") - .1, "tick", .7), (lambda: WT(4, "órbita") - .1, "pop", .7),
        (lambda: S(5) - .35, "riser", .9), (lambda: WT(6, "8") - .12, "impact", .7), (lambda: WT(6, "20") - .05, "tick", .6),
        (lambda: T_P4[0] - .05, "whoosh", .9), (lambda: T_OFF, "impact", 1.0), (lambda: T_OFF + .02, "glitch", .4),
        (lambda: T_MOON, "tick", .9), (lambda: WT(8, "depois.") - .1, "pop", .5),
        (lambda: S(9) + .2, "wind", .6), (lambda: WT(9, "fotossíntese") - .1, "tick", .7), (lambda: T_ICE0, "glass", .7), (lambda: T_ICE0 + 1.1, "glass", .45),
        (lambda: T_DOWN0, "whoosh", .7), (lambda: WT(10, "fontes") - .25, "rumble", .5),
        (lambda: WT(11, "relaxa:") - .1, "pop", .6), (lambda: WT(11, "Sol") - .3, "whoosh", .5), (lambda: WT(11, "demais") - .05, "metal", .7),
        (lambda: S(12) + 1.0, "pop", .7)]
SHAKES = [(lambda: T_COL1, 12, .45), (lambda: WT(6, "8") - .12, 6, .3), (lambda: T_OFF, 10, .4), (lambda: WT(11, "demais") - .05, 5, .25)]
