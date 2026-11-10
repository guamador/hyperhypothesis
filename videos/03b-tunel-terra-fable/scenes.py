"""Cenas da Hipótese #03 (versão B do teste A/B) — E se você cavasse um buraco até o outro lado do mundo?
Motor v4: câmera virtual (hh/cam.py), Terra em corte com física PREM (hh/planet.py), personagem com rig (hh/hero.py),
sincronia por palavra (WT) e legenda com tempo exato.

FÍSICA E FONTES (conferidas em 10/11/2026)
- Queda por um túnel reto pelo centro, sem ar e sem atrito, integrando a gravidade do modelo PREM
  (Dziewonski & Anderson, 1981; densidade real por camada). Resultado do hh/planet.py:
    travessia = 38,0 min (com malha mais fina: 38,1 min; Klotz 2015, Am. J. Phys. 83, 231, dá 38 min 11 s)
    até o centro = 19 min ; velocidade no centro = 9,92 km/s = 35.700 km/h ; ida e volta = 76 min
  (Com densidade uniforme, o resultado clássico seria 42 min e 28.400 km/h; a Terra real é mais densa no centro.)
- No centro, a gravidade resultante é zero: a massa em volta puxa igualmente em todas as direções.
- Depois do centro a gravidade aponta para trás e freia; sem perdas, a velocidade chega a zero exatamente na saída.
- Temperatura do núcleo interno: ~5.000–6.000 °C. Com ar, o atrito limitaria a velocidade; por isso "sem ar".
- Antípoda de São Paulo (23,55° S, 46,63° O) = 23,55° N, 133,37° L: Mar das Filipinas, a ~650 km de Okinawa
  (Naha) e ~330 km de Minamidaito, ilhas do Japão.
- De avião: não há voo direto São Paulo–Tóquio; o itinerário mais rápido leva 25 h 10 min (momondo.com.br, nov/2026).
- Câmera lenta no centro: recurso de montagem. A travessia real do centro dura segundos; o vídeo avisa na tela.
"""
import math, random
import cairocffi as cairo
from hh.anim import *
from hh import fx as _fx
from hh.cam import Cam, lerp_log, smooth, smoother, ramp, pulse, ease_out, ease_in
from hh.hero import hero, POSES, mixpose, flutter
from hh.planet import earth, FALL, R, R_OUTER, R_INNER, C_MANTLE, C_MANTLE2, C_OUTER, C_INNER, C_CRUST

GREEN = hx("2E6B5E")
ZOOM = 0.0                                              # a câmera é das cenas (hh/cam.py)

# ---------------------------------------------------------------- linha do tempo (sincronizada com a fala)
T_WHIP0, T_WIDE0, T_WIDE1, T_BACK = 1.50, 2.05, 3.10, 3.55      # afasta até o planeta e volta
T_CROUCH, T_JUMP = WT(0, "pulasse?") - .42, WT(0, "pulasse?") - .08
T_DROP = T_JUMP + .5                                    # entra no buraco: começa a queda (tau = 0)
T_SLOW0 = WT(3, "35") + .25                             # chega ao centro junto com "35 mil"
T_OUT0, T_OUT1 = T_SLOW0 + .5, T_SLOW0 + 2.3            # câmera afasta até o planeta inteiro
T_ROT0, T_ROT1 = WT(4, "bem") - .2, WT(5, "tempo.") + .3  # o planeta gira meia-volta em torno dele
T_IN0, T_IN1 = S(6) - .35, S(6) + .55                   # câmera volta a seguir
T_SLOW1 = S(6) + .15
T_STOP = WT(7, "para.") + .30                           # velocidade zero na saída
Y_SLOW = 300.0                                          # km: trecho em câmera lenta de cada lado do centro

def _solve(y):                                          # tau em que a queda passa por y (< 0)
    a, b = 0.0, FALL.T_HALF
    for _ in range(40):
        m = (a + b) / 2
        if FALL.pos(m) < y: a = m
        else: b = m
    return a
TAU_A = _solve(-Y_SLOW); TAU_B = FALL.T_ONE - TAU_A

def state(t):
    """(y km, v km/s, tau s) do personagem no instante t do vídeo."""
    if t < T_DROP: return -R, 0.0, 0.0
    if t < T_SLOW0:
        tau = TAU_A * (t - T_DROP) / (T_SLOW0 - T_DROP); y, v = FALL.state(tau); return y, v, tau
    if t < T_SLOW1:
        u = (t - T_SLOW0) / (T_SLOW1 - T_SLOW0); c = 2 * u - 1
        y = Y_SLOW * math.copysign(abs(c) ** 7, c); tau = FALL.T_HALF + y / FALL.V_MAX
        return y, FALL.vel(tau), tau
    if t < T_STOP:
        tau = TAU_B + (FALL.T_ONE - TAU_B) * (t - T_SLOW1) / (T_STOP - T_SLOW1); y, v = FALL.state(tau); return y, v, tau
    return R, 0.0, FALL.T_ONE

Z_NEAR, Z_FAST, Z_WIDE = 3.0, 1.7, 0.063
def wide_u(t):
    """0 = câmera perto, 1 = planeta inteiro."""
    return max(smoother(ramp(t, T_WHIP0, T_WIDE0)) * (1 - smoother(ramp(t, T_WIDE1, T_BACK))),
               smoother(ramp(t, T_OUT0, T_OUT1)) * (1 - smoother(ramp(t, T_IN0, T_IN1))))

def camera(t):
    y, v, _ = state(t); sp = abs(v) / FALL.V_MAX
    zn = lerp(Z_NEAR, Z_FAST, sp ** 1.2)
    wu = wide_u(t); z = lerp_log(zn, Z_WIDE, wu)
    rot = PI * smoother(ramp(t, T_ROT0, T_ROT1))
    # foco: no chão antes do pulo, no personagem durante a viagem, na borda da saída no fim
    k_in = smooth(ramp(t, T_DROP, T_DROP + .9)); k_out = smooth(ramp(t, T_STOP - 1.6, T_STOP - .1))
    cy = y; fy = lerp(1000, 760, k_in); fy = lerp(fy, 1000, k_out)
    cy = lerp(cy, 0.0, wu); fy = lerp(fy, 880, wu)
    return Cam(0.0, cy, z, rot, 540, fy), y, v, wu

def near_k(z): return clamp((math.log(z) - math.log(Z_WIDE)) / (math.log(1.6) - math.log(Z_WIDE)))

# ---------------------------------------------------------------- cenários das duas bocas do túnel
def _anchor(ctx, cam, wy, flip):
    x, y = cam.pt(0, wy); s = cam.z / Z_NEAR
    ctx.save(); ctx.translate(x, y); ctx.rotate(cam.rot - (PI if flip else 0)); ctx.scale(s, s)
    return s

def surface_sp(ctx, cam, t, pile=1.0, sign=1.0):
    """Entrada (São Paulo): grama, árvores, placa, monte de terra. Coordenadas locais: (0,0) = boca do túnel."""
    s = _anchor(ctx, cam, -R, False)
    if s < .03 or not -1500 < cam.pt(0, -R)[1] < H + 1500: ctx.restore(); return
    a = clamp((s - .03) / .12)
    icon(ctx, "sun", 420, -400, 130, SOLAR, a, "duotone", rot=t * .2)
    for k in range(2): cloud(ctx, -380 + k * 560 + 30 * math.sin(t * .4 + k), -330 - k * 60, .6, MUTED, .4 * a)
    for sx in (-1, 1):
        rrect(ctx, sx * 2000 if sx < 0 else 120, -4, 1880, 34, 0); fill(ctx, GREEN, a)
    tree(ctx, -470, 0, 1.25, a=a, lean=wobble(t, .06)); tree(ctx, 470, 0, 1.0, a=a, lean=wobble(t, .06, seed=2))
    sa = sign * a * clamp((s - .93) / .05)                                             # placa: só em escala legível (>= 36 px)
    rrect(ctx, 304, -150, 12, 150, 4); fill(ctx, MUTED, sa)
    rrect(ctx, 150, -250, 320, 110, 18); fill(ctx, ORBIT, sa)
    text(ctx, "SÃO PAULO", BOLD, 40, 310, -182, INK, sa)
    if pile > 0:                                                                       # monte de terra cavada
        ctx.save(); ctx.translate(-400, 0); ctx.scale(1, .62 * (.5 + .5 * pile)); ctx.new_sub_path(); ctx.arc(0, 0, 130, PI, 2 * PI); ctx.close_path()
        fill(ctx, C_MANTLE2, a); ctx.restore()
    for sx in (-1, 1): rrect(ctx, sx * 152 - 32, -14, 64, 28, 14); fill(ctx, RED, a)       # borda do buraco
    ctx.restore()

def surface_exit(ctx, cam, t, a=1.0):
    """Saída (Mar das Filipinas): mar, plataforma em volta da boca, placa, sol e gaivotas."""
    s = _anchor(ctx, cam, R, True)
    if s < .03 or not -1500 < cam.pt(0, R)[1] < H + 1500: ctx.restore(); return
    a *= clamp((s - .03) / .12)
    icon(ctx, "sun", -390, -560, 150, SOLAR, a, "duotone", rot=t * .2)
    for k in range(3): cloud(ctx, -360 + k * 380 + 30 * math.sin(t * .4 + k), -700 + (k % 2) * 100, .7, MUTED, .45 * a)
    for b in range(3):
        bx = ((t * 70 + b * 260) % 1500) - 750; by = -430 - b * 60 + wobble(t, 12, 1, b)
        icon(ctx, "bird", bx, by, 58, MUTED, .8 * a, "fill")
    for sx in (-1, 1):                                                                 # mar dos dois lados
        ctx.save(); ctx.rectangle(-2000 if sx < 0 else 150, -80, 1850, 200); ctx.clip()
        wave(ctx, t, -6, 13, 210, hx("0B7399"), a, speed=.5, x0=-2000, x1=2000, bottom=110)
        wave(ctx, t, 22, 10, 170, BLUE, .9 * a, speed=.8, x0=-2000, x1=2000, bottom=110, phase=1.3)
        ctx.restore()
    for sx in (-1, 1):                                                                 # plataforma
        rrect(ctx, sx * 205 - 85, -40, 170, 64, 14); fill(ctx, MUTED, a)
        rrect(ctx, sx * 205 - 85, -40, 170, 18, 9); fill(ctx, RED, a)
    sa = a * clamp((s - .93) / .05)                                                    # placa: só em escala legível (>= 36 px)
    rrect(ctx, 254, -210, 12, 172, 4); fill(ctx, MUTED, sa)
    rrect(ctx, 150, -330, 370, 150, 18); fill(ctx, ORBIT, sa)
    text(ctx, "OKINAWA", BOLD, 40, 335, -268, INK, sa); text(ctx, "650 km →", SANSB, 40, 335, -212, SOLAR, sa)
    ctx.restore()

# ---------------------------------------------------------------- HUD da viagem
def fmt_clock(tau): m, s = divmod(int(round(tau)), 60); return f"{m:02d}:{s:02d}"

def minimap(ctx, cx, cy, r, y, a=1.0):
    circle(ctx, cx, cy, r + 5, VOID, a); circle(ctx, cx, cy, r, C_CRUST, a); circle(ctx, cx, cy, r * .985, C_MANTLE2, a)
    circle(ctx, cx, cy, r * R_OUTER / R, C_OUTER, a); circle(ctx, cx, cy, r * R_INNER / R, C_INNER, a)
    ctx.rectangle(cx - 4, cy - r, 8, 2 * r); fill(ctx, VOID, a)
    circle(ctx, cx, cy + y / R * r, 11, INK, a); circle(ctx, cx, cy + y / R * r, 6, BLUE, a)

def trip_hud(ctx, t, y, v, tau, a, slow=0.0):
    if a <= 0: return
    rrect(ctx, 50, 205, 980, 250, 28); fill(ctx, ORBIT, .93 * a)
    kmh = abs(v) * 3600; col = mix(SOLAR, RED, clamp((kmh - 20000) / 16000))
    wn = text(ctx, counter(round(kmh / 10) * 10 if kmh > 300 else kmh), DISP, 96, 92, 322, col, a, "l")
    text(ctx, "km/h", SANSB, 44, 92 + wn + 18, 322, INK, a, "l")
    icon(ctx, "timer", 122, 396, 60, INK, a, "fill")
    wc = text(ctx, fmt_clock(tau), BOLD, 52, 166, 414, INK, a, "l")
    r = abs(y); name, lc = (("MANTO", RED) if r > R_OUTER else ("NÚCLEO EXTERNO", hx("FF8A3D")) if r > R_INNER else ("NÚCLEO INTERNO", SOLAR))
    if r > R - 35: name, lc = "CROSTA", MUTED
    text(ctx, name, BOLD, 36, 166 + wc + 30, 412, lc, a, "l", .03)
    minimap(ctx, 932, 330, 84, y, a)
    if slow > 0:
        rrect(ctx, 640, 470, 390, 64, 32); fill(ctx, VOID, .8 * slow * a)
        text(ctx, "CÂMERA LENTA", BOLD, 36, 835, 515, BLUE, slow * a, track=.04)

def chip(ctx, txt, x, y, k, ic=None, col=INK, font=None, size=40):
    """Etiqueta em pílula que entra com mola. k = progresso 0..1 (>1 mantém)."""
    if k <= 0: return
    font = font or BOLD; s = max(spring(clamp(k)), 37 / size); al = clamp(k * 5); w = font.width(txt, size) + (86 if ic else 56)
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    rrect(ctx, -w / 2, -42, w, 84, 42); fill(ctx, VOID, .86 * al)
    ctx.set_line_width(3); rrect(ctx, -w / 2, -42, w, 84, 42); ctx.set_source_rgba(*col, .9 * al); ctx.stroke()
    if ic: icon(ctx, ic, -w / 2 + 46, 0, 50, col, al, "fill")
    text(ctx, txt, font, size, (30 if ic else 0), 14, col, al)
    ctx.restore()

def streaks(ctx, cam, t, y, v, tun_px):
    """Riscos de velocidade dentro do túnel (no espaço da tela), contra o sentido do movimento."""
    sp = abs(v) / FALL.V_MAX
    if sp < .12 or cam.z < .8: return
    sgn = math.cos(cam.rot); rnd = random.Random(4); scroll = y * 2.4 * sgn
    ctx.save(); ctx.rectangle(540 - tun_px / 2 + 8, 0, tun_px - 16, H); ctx.clip()
    for i in range(16):
        x = 540 + (rnd.random() - .5) * (tun_px - 40); L = (90 + 420 * rnd.random()) * sp; ph = rnd.random() * (H + 600)
        yy = (ph - scroll * (1.5 + rnd.random())) % (H + 600) - 300
        rrect(ctx, x - 2.5, yy, 5, L, 2.5); fill(ctx, INK, .30 * sp)
    ctx.restore()

def shovel(ctx, hands, ang, a=1.0):
    mx, my = (hands[0][0] + hands[1][0]) / 2, (hands[0][1] + hands[1][1]) / 2
    dx, dy = math.cos(ang), math.sin(ang)
    ctx.set_line_width(11); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(mx - dx * 60, my - dy * 60); ctx.line_to(mx + dx * 120, my + dy * 120); ctx.set_source_rgba(*MUTED, a); ctx.stroke()
    ctx.save(); ctx.translate(mx + dx * 120, my + dy * 120); ctx.rotate(ang); rrect(ctx, 0, -30, 62, 60, 14); fill(ctx, BLUE, a); ctx.restore()

# ---------------------------------------------------------------- cena 1: plano-sequência (frases 0 a 7)
DIG = .46                                                # s por pá de terra

def scene_take(ctx, t):
    cam, y, v, wu = camera(t); _, _, tau = state(t)
    sp = abs(v) / FALL.V_MAX; nk = near_k(cam.z)
    background(ctx, t)
    tun = lerp(26, 240, nk)
    dig_y = lerp(-R + 260, R, ease_in(ramp(t, T_WIDE0 - .1, T_WIDE1 - .25), 1.6))       # o túnel "fura" o planeta no plano aberto
    earth(ctx, cam, t, tunnel_px=tun, tun_y1=None if t > T_WIDE1 else dig_y, rings=1 - clamp((sp - .35) / .4))
    if cam.rot < .5: surface_sp(ctx, cam, t, pile=clamp(t / 1.4), sign=1 - ramp(t, T_WHIP0 - .1, T_WHIP0 + .1))   # a placa sai antes do título "...E PULASSE?"
    if cam.rot > PI - .5: surface_exit(ctx, cam, t)
    streaks(ctx, cam, t, y, v, tun)
    gx, gy = cam.pt(0, -R)

    # ---- plano aberto da abertura: a ponta da escavação e os rótulos
    if T_WHIP0 < t < T_BACK:
        hx_, hy_ = cam.pt(0, min(dig_y, R))
        if t < T_WIDE1 - .2: circle(ctx, hx_, hy_, 13, BLUE, wu); sparks(ctx, hx_, hy_, t - .05, t + .001, n=6, col=SOLAR, speed=260, life=.3, seed=int(t * 30))
        ex, ey = cam.pt(0, R)
        shockwave(ctx, ex, ey, T_WIDE1 - .25, t, r1=190, life=.5, col=SOLAR, w=10)
        sparks(ctx, ex, ey, T_WIDE1 - .25, t, n=20, col=SOLAR, speed=620, life=.6, seed=5, ang0=0, ang1=PI)
        pop_text(ctx, "?", DISP, 120, 540, ey + 150, SOLAR, t, T_WIDE1 - .2, a=wu)
        text(ctx, "SÃO PAULO", BOLD, 36, 590, gy - 14, INK, wu * ramp(t, T_WIDE0 - .2, T_WIDE0), "l")

    # ---- personagem
    hs = lerp(.42, 1.0, nk)
    if t < T_DROP:                                                                     # cavando, agachando, pulando
        px, py = gx - 330 * (cam.z / Z_NEAR), gy - 92 * hs
        if t < T_WHIP0 + .25:
            ph = (t / DIG) % 1; k = smooth(ph / .45) if ph < .45 else 1 - smooth((ph - .45) / .55)   # 0 = pá no chão, 1 = pá no alto
            down = dict(arms=(-.95, -.55), elbows=(-.35, -.7), legs=(.3, -.3), knees=(-.35, .25))
            up = dict(arms=(1.75, 2.25), elbows=(.5, .35), legs=(.15, -.2), knees=(-.1, .1))
            hands = hero(ctx, px + 40 * (1 - k) * hs, py + 6 * (1 - k), hs, t, pose=mixpose(down, up, k), rot=lerp(.30, -.22, k),
                         mood="effort", look=(lerp(.8, -.6, k), lerp(.7, -.4, k)), vel=(lerp(120, -260, k), 0), squash=lerp(.94, 1.04, k))
            shovel(ctx, hands, lerp(.95, -2.25, k), a=clamp(nk * 3 - 1.5))
            for n in range(5):                                                         # torrões de terra a cada pá
                t0 = n * DIG + DIG * .62
                spray(ctx, px - 60, py - 150, t0, t, n=9, col=C_MANTLE2, speed=820, life=.75, g=2100, seed=n, ang0=-PI * .86, ang1=-PI * .62)
                spray(ctx, px - 60, py - 150, t0, t, n=5, col=GREEN, speed=700, life=.7, g=2100, seed=n + 9, ang0=-PI * .9, ang1=-PI * .6)
        elif t < T_CROUCH:
            hero(ctx, px, py, hs, t, pose=POSES["stand"], mood="happy", look=(.9, .5 + wobble(t, .2)))
        elif t < T_JUMP:                                                               # antecipação: agacha
            k = smooth(ramp(t, T_CROUCH, T_JUMP))
            hero(ctx, px, py + 34 * k, hs, t, pose=mixpose(POSES["stand"], POSES["crouch"], k), mood="happy", look=(1, .6), squash=1 - .16 * k)
        else:                                                                          # salto em arco para dentro do buraco
            u = (t - T_JUMP) / (T_DROP - T_JUMP); x = lerp(px, 540, ease_out(u, 2)); arc = -230 * 4 * u * (1 - u) * .62
            yy = py + arc + 92 * u * u * 1.05
            hero(ctx, x, yy, hs, t, pose=mixpose(POSES["leap"], POSES["fall"], smooth(u)), mood="wow", look=(.3, 1),
                 rot=lerp(.25, 0, u), vel=(300, lerp(-700, 600, u)), squash=1.1)
            dust(ctx, px, gy, T_JUMP, t, n=7, col=MUTED, dirx=-1, seed=3, size=.8)
    else:
        hx_, hy_ = cam.pt(0, y)
        k_out = smooth(ramp(t, T_STOP - 1.3, T_STOP))
        hy_ -= 150 * k_out * hs                                                        # no fim, sobe um pouco acima da borda
        hx_ += wobble(t, 10 * nk, .9)
        sgn = math.cos(cam.rot)                                                        # +1 descendo na tela, -1 subindo
        vel = (0, sgn * sp * 1500)
        if t < T_SLOW0 + .4:                                                           # queda livre
            pose = flutter(POSES["fall"], t, .10 + .10 * sp); mood = "wow"; look = (wobble(t, .3), 1); rot = wobble(t, .07, 1.1); sq = 1 + .10 * sp
        elif t < T_IN0:                                                                # flutuando no centro
            k = smooth(ramp(t, T_SLOW0 + .4, T_SLOW0 + 1.6))
            pose = flutter(mixpose(POSES["fall"], POSES["float"], k), t, .16, f=1.6); mood = "calm" if t > T_OUT1 + 2.8 else "happy"
            look = (math.cos(t * .9) * .7, math.sin(t * .7) * .6); rot = wobble(t, .22, .35); sq = 1.0
            vel = (70 * math.cos(t * .8), 70 * math.sin(t * .8))
            hy_ += wobble(t, 9, .5, 3)
        else:                                                                          # subindo: mergulho -> freio -> em pé
            k1 = smooth(ramp(t, T_IN0, T_IN1)); k2 = smooth(ramp(t, T_STOP - 2.4, T_STOP - .7)); k3 = smooth(ramp(t, T_STOP - .7, T_STOP + .15))
            pose = mixpose(mixpose(mixpose(POSES["float"], POSES["dive"], k1), POSES["brake"], k2), POSES["stand"], k3)
            pose = flutter(pose, t, .05 + .08 * sp); mood = "happy" if t > T_STOP - .5 else ("effort" if sp < .45 else "wow")
            look = (wobble(t, .3), -1 + 1.2 * k3); rot = wobble(t, .05, 1.1); sq = 1 + .10 * sp * (1 - k2)
            if t > T_STOP: hy_ += 7 * math.sin((t - T_STOP) * 2.6); look = (math.sin((t - T_STOP) * 2.2) * .9, -.2)
        hero(ctx, hx_, hy_, hs, t, pose=pose, vel=vel, mood=mood, look=look, rot=rot, squash=sq)
        if T_STOP <= t: burst(ctx, hx_, hy_ + 60, (t - T_STOP) / .5, INK, n=10, r0=70, r1=170, w=6)
        # gravidade puxando para todos os lados (plano aberto)
        ta = WT(5, "puxa") - .15
        if wu > .6 and t > ta:
            n = 10; kout = 1 - ramp(t, T_IN0 - .25, T_IN0 + .1)
            for j in range(n):
                k = spring(ramp(t, ta + j * .07, ta + j * .07 + .5)); ang = j * 2 * PI / n + .3
                r0, r1 = 92, 92 + (230 + 26 * math.sin(t * 5 - j * 1.3)) * k
                arrow(ctx, hx_ + r0 * math.cos(ang), hy_ + r0 * math.sin(ang), hx_ + r1 * math.cos(ang), hy_ + r1 * math.sin(ang), BLUE, clamp(k) * kout * wu, w=11, head=32)
        # freio da gravidade na subida
        tg = WT(6, "gravidade") - .1
        if t > tg and t < T_STOP + .2 and wu < .3:
            k = spring(ramp(t, tg, tg + .5)) * (1 - ramp(t, T_STOP - .5, T_STOP + .1)); L = (70 + 170 * sp) * k
            arrow(ctx, hx_ + 150, hy_ - 30, hx_ + 150, hy_ - 30 + L, RED, clamp(k), w=14, head=40)
            chip(ctx, "GRAVIDADE", hx_ + 290, hy_ + 215, ramp(t, tg, tg + .45) * (1 - ramp(t, T_STOP - .6, T_STOP - .2)), col=RED, size=36)

    # ---- títulos da abertura (um por trecho da pergunta)
    a1 = 1 - ramp(t, T_WHIP0 - .1, T_WHIP0 + .2)
    pop_text_fit(ctx, "E SE VOCÊ CAVASSE", DISP, 76, 540, 330, INK, t, 0.0, a=a1, stagger=.02, dur=.3)
    pop_text_fit(ctx, "UM BURACO", DISP, 96, 540, 440, BLUE, t, WT(0, "um") - .25, a=a1, stagger=.025)
    a2 = 1 - ramp(t, T_WIDE1 + .05, T_WIDE1 + .3)
    pop_text_fit(ctx, "ATÉ O OUTRO LADO", DISP, 78, 540, 280, INK, t, WT(0, "até") - .1, a=a2, stagger=.02)
    pop_text_fit(ctx, "DO MUNDO...", DISP, 78, 540, 372, BLUE, t, WT(0, "mundo...") - .25, a=a2, stagger=.02)
    a3 = 1 - ramp(t, S(1) + .2, S(1) + .6)
    pop_text_fit(ctx, "...E PULASSE?", DISP, 100, 540, 400, SOLAR, t, WT(0, "e", nth=1) - .05, a=a3, stagger=.025)

    # ---- HUD da viagem, etiquetas e números
    ah = ramp(t, S(1) + .3, S(1) + .8) * (1 - wu) * (1 if t < T_OUT0 or t > T_IN0 else 0)
    trip_hud(ctx, t, y, v, tau, ah, slow=ramp(t, T_SLOW0 + .1, T_SLOW0 + .5) * (1 - ramp(t, T_OUT0, T_OUT0 + .4)))
    off = 1 - ramp(t, S(2) - .25, S(2))
    chip(ctx, "SEM AR", 300, 1150, ramp(t, WT(1, "sem") - .1, WT(1, "sem") + .4) * off, ic="wind", col=BLUE)
    chip(ctx, "À PROVA DE CALOR", 660, 1260, ramp(t, WT(1, "prova") - .1, WT(1, "prova") + .4) * off, ic="shield-check", col=SOLAR, size=38)
    chip(ctx, "19 MIN ATÉ O CENTRO", 540, 1200, ramp(t, WT(2, "19") - .1, WT(2, "19") + .4) * (1 - ramp(t, S(3) - .1, S(3) + .2)), ic="timer", col=INK, size=38)
    if T_OUT0 < t < T_IN1:                                                             # plano aberto no centro
        kw = wu * (1 - ramp(t, T_IN0 - .2, T_IN0 + .1))
        tn = WT(4, "nada.") - .12
        pop_text(ctx, "PESO: 0", DISP, 124, 540, 282, SOLAR, t, tn, a=kw, stagger=.04)
        text(ctx, "no centro, a gravidade se cancela", SANS, 40, 540, 346, INK, kw * ramp(t, S(5) + .2, S(5) + .7))
        text(ctx, "CÂMERA LENTA", BOLD, 36, 1020, 168, BLUE, kw * (.6 + .4 * math.sin(t * 5) ** 2), "r", .04)
        for wy_, lab, col in ((-R, "SÃO PAULO", INK), (R, "SAÍDA", SOLAR)):                 # as duas bocas, girando com o planeta
            px_, py_ = cam.pt(0, wy_); ux, uy = px_ - 540, py_ - cam.fy; d = math.hypot(ux, uy) or 1
            lw_ = BOLD.width(lab, 36) * .5; circle(ctx, px_, py_, 14, col, kw); text(ctx, lab, BOLD, 36, clamp(px_ + ux / d * 46 + (ux / d) * lw_, lw_ + 40, W - lw_ - 40), py_ + uy / d * 46 + 13, col, kw * ramp(t, T_OUT1 - .4, T_OUT1))
    if t > T_STOP - .05:                                                               # chegou: velocidade zero
        chip(ctx, "0 km/h", 250, 700, ramp(t, T_STOP, T_STOP + .45), col=SOLAR, font=DISP, size=44)


# ---------------------------------------------------------------- cena 2: 38 minutos no mapa (frases 8 a 10)
SP = (-46.63, -23.55); AN = (133.37, 23.55)
_JP = [r for r in _fx._LAND if 129 <= sum(p[0] for p in r) / len(r) <= 146 and 30 <= sum(p[1] for p in r) / len(r) <= 46]

def scene_map(ctx, t):
    background(ctx, t)
    k38 = spring(ramp(t, S(8), S(8) + .7))
    ctx.save(); ctx.translate(540, 400); ctx.scale(lerp(.5, 1, k38), lerp(.5, 1, k38))
    n = int(round(38 * ease_out(ramp(t, S(8), S(8) + .7), 2)))
    wn = DISP.width(str(n), 230); wm = BOLD.width("MIN", 76)
    text(ctx, str(n), DISP, 230, -(wn + 24 + wm) / 2, 60, SOLAR, clamp(k38 * 2), "l"); text(ctx, "MIN", BOLD, 76, -(wn + 24 + wm) / 2 + wn + 24, 60, INK, clamp(k38 * 2), "l")
    ctx.restore()
    cx, cy, Rg = 540, 830, 290
    kr = smoother(ramp(t, WT(9, "até") - .2, WT(9, "mar,") + .1))
    lon0 = lerp(SP[0], AN[0], kr) - 14 * math.sin(PI * kr); lat0 = lerp(SP[1], AN[1], kr)
    globe(ctx, cx, cy, Rg, lon0=lon0, lat0=lat0)
    tj = WT(9, "Japão.") - .15; kj = ramp(t, tj, tj + .3)
    if kj > 0:                                                                         # Japão em destaque
        ctx.save(); ctx.new_sub_path(); ctx.arc(cx, cy, Rg, 0, 2 * PI); ctx.clip()
        for ring in _JP:
            pts = [geo(lo, la, lon0, lat0, Rg, cx, cy) for lo, la in ring]
            if all(p[2] for p in pts):
                ctx.move_to(pts[0][0], pts[0][1]); [ctx.line_to(p[0], p[1]) for p in pts[1:]]; ctx.close_path()
        fill(ctx, INK, kj); ctx.restore()
        jx, jy, _ = geo(138, 37, lon0, lat0, Rg, cx, cy)
        chip(ctx, "JAPÃO", jx + 150, jy - 60, ramp(t, tj, tj + .45), col=INK, size=38)
    for (lo, la), col, lab, ka, side in ((SP, BLUE, "SÃO PAULO", 1 - ramp(t, WT(9, "até"), WT(9, "até") + .5), 1), (AN, SOLAR, "SAÍDA", ramp(t, WT(9, "mar,") - .1, WT(9, "mar,") + .2), -1)):
        x, y, vis = geo(lo, la, lon0, lat0, Rg, cx, cy)
        if vis and ka > 0:
            pk = ((t * 1.2) % 1); ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(x, y, 18 + 34 * pk, 0, 2 * PI); ctx.set_source_rgba(*col, ka * (1 - pk)); ctx.stroke()
            circle(ctx, x, y, 18, col, ka); circle(ctx, x, y, 8, VOID, ka)
            text(ctx, lab, BOLD, 38, x, y + 74, col, ka, track=.04)
    # comparação: túnel x avião
    ta = S(10) - .1; x0 = 110
    k1 = ease_out(ramp(t, ta, ta + .4)); k2 = ease_out(ramp(t, ta + .25, ta + 1.5), 2)
    if k1 > 0:
        text(ctx, "TÚNEL", BOLD, 38, x0, 1196, SOLAR, k1, "l", .05); rrect(ctx, x0 + 230, 1164, max(8, 22 * k1), 40, 12); fill(ctx, SOLAR, k1)
        text(ctx, "38 min", SANSB, 40, x0 + 275, 1198, SOLAR, k1, "l")
        text(ctx, "AVIÃO", BOLD, 38, x0, 1296, MUTED, k1, "l", .05); L = 22 + (22 * 1510 / 38 - 22) * k2
        ctx.save(); ctx.rectangle(x0 + 230, 1250, 640, 70); ctx.clip(); rrect(ctx, x0 + 230, 1264, L, 40, 12); fill(ctx, MUTED, k1); ctx.restore()
        px = min(x0 + 230 + L, x0 + 850)
        icon(ctx, "airplane-tilt", px + 44, 1284 + wobble(t, 4, 2), 84, INK, k1, "fill", rot=.78)
        text(ctx, "25 h", SANSB, 40, x0 + 250, 1298, VOID, ramp(t, ta + .9, ta + 1.2), "l")


# ---------------------------------------------------------------- cena 3: a borda (frases 11 e 12)
def scene_edge(ctx, t):
    cam = Cam(0.0, R, Z_NEAR, PI, 540, 1000)
    background(ctx, t)
    earth(ctx, cam, t, tunnel_px=240)
    surface_exit(ctx, cam, t)
    hx0, hy0 = 540, 1000 - 150
    tr = S(11) + .25; tm = WT(11, "borda.") + .05; tf = WT(12, "cai") - .12
    kreach = smooth(ramp(t, tr, tr + .5)); kslip = smooth(ramp(t, tm, tm + .45))
    sink = 26 * ease_in(ramp(t, tr, tf), 2)                                            # já começa a descer devagar
    if t < tf:
        pose = mixpose(mixpose(POSES["stand"], POSES["reach"], kreach), POSES["panic"], kslip)
        pose = flutter(pose, t, .03 + .22 * kslip, f=17)
        mood = "happy" if t < tr + .2 else ("effort" if t < tm else "scared")
        hands = hero(ctx, hx0 + 30 * kreach * (1 - kslip), hy0 + sink + 6 * math.sin(t * 2.6), 1.0, t, pose=pose, mood=mood,
                     look=(lerp(0, 1, kreach) * (1 - kslip), lerp(-.2, -.5, kreach) + kslip * 1.2), rot=.16 * kreach * (1 - kslip), vel=(0, 40))
        if kslip > 0 and t < tm + .5:                                                   # a mão escapa
            for j in range(3):
                kk = ramp(t, tm + j * .08, tm + j * .08 + .3); ang = -1.0 + j * .5
                if 0 < kk < 1:
                    ctx.set_line_width(6); ctx.set_line_cap(cairo.LINE_CAP_ROUND); x1, y1 = 700 + 30 * math.cos(ang), 880 + 30 * math.sin(ang)
                    ctx.move_to(x1 + 16 * kk * math.cos(ang), y1 + 16 * kk * math.sin(ang)); ctx.line_to(x1 + (16 + 34) * kk * math.cos(ang), y1 + 50 * kk * math.sin(ang))
                    ctx.set_source_rgba(*SOLAR, 1 - kk); ctx.stroke()
        if t > tm + .15:                                                               # gota de suor
            kd = ((t - tm) * 1.6) % 1; circle(ctx, hx0 - 52, hy0 + sink - 120 + 60 * kd, 7 * (1 - kd * .5), BLUE, 1 - kd)
    else:                                                                              # cai de volta: acelera a partir do repouso
        d = t - tf; yy = hy0 + sink + 2600 * d * d
        if yy < H + 300:
            hero(ctx, hx0, yy, 1.0, t, pose=flutter(POSES["fall"], t, .2, f=14), mood="scared", look=(0, -1), vel=(0, 5200 * d), squash=1 + .12 * clamp(d * 2))
        # o vai e vem pelo planeta
        ko = spring(ramp(t, tf + .5, tf + 1.1))
        if ko > 0:
            cx, cy, r = 540, 470, 150 * ko
            w = 2 * PI / 1.5; yb = R * math.cos(w * (t - tf - .5))                      # ciclo de 76 min acelerado para 1,5 s
            minimap(ctx, cx, cy, r, yb, clamp(ko))
            chip(ctx, "IDA E VOLTA: 76 MIN", 540, 250, ramp(t, tf + .9, tf + 1.35), ic="timer", col=SOLAR, size=38)


def scene_end(ctx, t):                                   # frases 13 e 14 + final
    end_card(ctx, t, S(13), question=["PRA ONDE", "VOCÊ CAVARIA?"], next_title="E se o Sol virasse um buraco negro?")


SCENES = [(0, 7, scene_take), (8, 10, scene_map), (11, 12, scene_edge), (13, 14, scene_end)]

_tf = lambda: WT(12, "cai") - .12
CUES = [(DIG * .62, "tick", .9), (DIG * 1.62, "tick", .9), (DIG * 2.62, "tick", .9),
        (T_WHIP0 - .05, "whoosh", .9), (T_WIDE1 - .25, "pop", .9), (T_WIDE1 + .05, "whoosh", .8),
        (T_JUMP, "pop", .6), (T_DROP, "whoosh", 1.0), (T_DROP + .6, "rumble", .7), (T_DROP + 3.4, "rumble", .8), (T_DROP + 6.0, "thruster", .7),
        (T_SLOW0 - 1.25, "riser", .8), (T_SLOW0, "boom", .7), (T_OUT0, "force", .7),
        (lambda: WT(4, "nada.") - .12, "impact", .6), (lambda: WT(5, "puxa") - .1, "tick", .8), (lambda: WT(5, "todos"), "tick", .7),
        (T_IN0, "whoosh", .9), (lambda: WT(6, "gravidade"), "tick", .7), (T_STOP, "pop", .9),
        (lambda: S(8), "impact", .8), (lambda: WT(9, "mar,"), "pop", .7), (lambda: WT(9, "Japão.") - .1, "tick", .9), (lambda: S(10) + .1, "whoosh", .6),
        (lambda: WT(11, "borda.") + .05, "tick", 1.0), (_tf, "whoosh", 1.0), (lambda: _tf() + .55, "pop", .6),
        (lambda: S(13) + 1.0, "force", .6), (lambda: S(13) + 1.6, "pop", .7)]
SHAKES = [(T_WIDE1 - .25, 8, .3), (T_SLOW0, 12, .5), (lambda: S(8), 9, .35)]
