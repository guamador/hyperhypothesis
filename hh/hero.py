"""Personagem 'Você' v4: mesmo desenho da marca (cabeça círculo, corpo pílula, ink), com rig melhor:
braços e pernas com cotovelo/joelho, poses que se misturam, cachecol redshift que fica para trás
(mostra a direção e a velocidade do movimento), olhar, piscada e expressões.

    hero(ctx, x, y, s, t, pose=POSES["fall"], vel=(0, 900), mood="wow", look=(0, 1), rot=0, squash=1)

(x, y) = centro do corpo. `pose` é um dict de ângulos; use mixpose(p1, p2, k) para transições e
flutter(pose, t, amp) para dar vida. `vel` em px/s na tela: orienta o cachecol e o esticamento.
"""
import math, random
import cairocffi as cairo
from hh import core as _c
from hh.core import INK, VOID, RED, BLUE, SOLAR, MUTED, PI, rrect, fill, circle, clamp, lerp

# ângulos em rad. Braço/perna apontam para baixo em 0; + abre para a esquerda da tela, - para a direita.
# arms/legs = (esq, dir); elbows/knees = dobra extra do segmento de baixo.
POSES = {
    "stand":  dict(arms=(.20, -.20), elbows=(.05, -.05), legs=(.08, -.08), knees=(0, 0)),
    "crouch": dict(arms=(-.7, .7), elbows=(-.5, .5), legs=(.75, -.75), knees=(-1.4, 1.4)),
    "leap":   dict(arms=(2.7, -2.7), elbows=(.2, -.2), legs=(.25, -.25), knees=(-.3, .3)),
    "fall":   dict(arms=(2.45, -2.45), elbows=(.45, -.45), legs=(.42, -.42), knees=(-.7, .7)),   # pés primeiro, membros para cima
    "dive":   dict(arms=(2.95, -2.95), elbows=(.05, -.05), legs=(.10, -.10), knees=(0, 0)),       # super-homem, subindo
    "float":  dict(arms=(1.35, -1.35), elbows=(.7, -.7), legs=(.55, -.55), knees=(-.8, .8)),
    "brake":  dict(arms=(1.7, -1.7), elbows=(-.6, .6), legs=(.3, -.3), knees=(-.2, .2)),
    "reach":  dict(arms=(.5, -2.75), elbows=(.2, -.05), legs=(.2, -.35), knees=(-.2, .5)),
    "panic":  dict(arms=(2.2, -2.2), elbows=(-.9, .9), legs=(.5, -.5), knees=(-.9, .9)),
    "dig":    dict(arms=(-.9, -.35), elbows=(-.6, -.9), legs=(.35, -.25), knees=(-.3, .2)),
}

def mixpose(a, b, k):
    k = clamp(k)
    return {key: tuple(lerp(x, y, k) for x, y in zip(a[key], b[key])) for key in a}

def flutter(p, t, amp=.12, f=9.0, seed=0.0):
    """Tremulação dos membros (vento/queda): pequenas oscilações defasadas."""
    def w(i): return amp * math.sin(t * f + seed + i * 1.9) + amp * .5 * math.sin(t * f * 1.7 + i)
    return dict(arms=(p["arms"][0] + w(0), p["arms"][1] + w(1)), elbows=(p["elbows"][0] + w(2) * 1.4, p["elbows"][1] + w(3) * 1.4),
                legs=(p["legs"][0] + w(4) * .7, p["legs"][1] + w(5) * .7), knees=(p["knees"][0] + w(6), p["knees"][1] + w(7)))

def _limb(ctx, x, y, a1, a2, l1, l2, w, col, al):
    """Membro de dois segmentos com juntas redondas. Retorna a ponta (mão/pé)."""
    ex, ey = x - math.sin(a1) * l1, y + math.cos(a1) * l1
    hx_, hy_ = ex - math.sin(a1 + a2) * l2, ey + math.cos(a1 + a2) * l2
    ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x, y); ctx.line_to(ex, ey); ctx.line_to(hx_, hy_); ctx.set_source_rgba(*col, al); ctx.stroke()
    return hx_, hy_

def _scarf(ctx, t, ang, speed, al, length=120):
    """Cachecol redshift preso no pescoço, voando na direção `ang` (rad, no sistema local) com ondulação."""
    amp = 5 + 9 * clamp(speed / 900); f = 7 + 9 * clamp(speed / 1500)
    L = length * (.55 + .45 * clamp(speed / 500))
    n = 9; pts = []
    for i in range(n + 1):
        u = i / n; d = L * u; off = math.sin(t * f - u * 5.5) * amp * u
        pts.append((math.cos(ang) * d - math.sin(ang) * off, math.sin(ang) * d + math.cos(ang) * off, 13 * (1 - .55 * u)))
    ctx.new_path()
    for i, (x, y, w) in enumerate(pts):
        nx, ny = -math.sin(ang), math.cos(ang); (ctx.move_to if i == 0 else ctx.line_to)(x + nx * w, y + ny * w)
    for x, y, w in reversed(pts):
        nx, ny = -math.sin(ang), math.cos(ang); ctx.line_to(x - nx * w, y - ny * w)
    ctx.close_path(); fill(ctx, RED, al)

def hero(ctx, x, y, s=1.0, t=0.0, pose=None, vel=(0.0, 0.0), mood=None, look=(0.0, 0.0), rot=0.0, squash=1.0,
         a=1.0, body=INK, scarf=True, blink=True, hat=True):
    """Desenha o personagem com o CENTRO DO CORPO em (x, y). Ver o docstring do módulo.
    mood: None | "happy" | "wow" | "scared" | "effort" | "dizzy" | "calm" """
    if a <= 0 or s <= 0: return
    p = pose or POSES["stand"]
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
    if squash != 1.0: ctx.scale(1 / math.sqrt(squash), squash)
    # sistema local: corpo de (-34,-45) a (34,45); cabeça em (0,-88)
    spd = math.hypot(*vel)
    if scarf:
        if spd > 30: va = math.atan2(-vel[1], -vel[0]) - rot            # para trás do movimento
        else: va = PI / 2 - rot + .35 * math.sin(t * 1.7)                 # parado: cai com a gravidade da tela
        ctx.save(); ctx.translate(0, -50); _scarf(ctx, t, va, spd, a); ctx.restore()
    for sx, i in ((-1, 0), (1, 1)):                                       # pernas
        _limb(ctx, sx * 15, 32, p["legs"][i], p["knees"][i], 30, 30, 22, body, a)
    hands = []
    for sx, i in ((-1, 0), (1, 1)):                                       # braços
        hands.append(_limb(ctx, sx * 27, -24, p["arms"][i], p["elbows"][i], 38, 38, 21, body, a))
    rrect(ctx, -34, -46, 68, 92, 34); fill(ctx, body, a)
    if scarf: rrect(ctx, -30, -58, 60, 20, 10); fill(ctx, RED, a)         # volta do cachecol no pescoço
    hy = -90
    circle(ctx, 0, hy, 40, body, a)
    if _c.THEME == "natal" and hat:
        ctx.move_to(-38, hy - 30); ctx.curve_to(-20, hy - 92, 30, hy - 118, 62, hy - 84); ctx.curve_to(38, hy - 82, 20, hy - 60, 38, hy - 30)
        ctx.close_path(); fill(ctx, RED, a); rrect(ctx, -46, hy - 44, 92, 24, 12); fill(ctx, INK, a); circle(ctx, 62, hy - 84, 13, INK, a)
        rrect(ctx, -46, hy - 44, 92, 24, 12); ctx.set_line_width(3); ctx.set_source_rgba(*VOID, .25 * a); ctx.stroke()
    ex, ey = clamp(look[0], -1, 1) * 7, clamp(look[1], -1, 1) * 6
    big = mood in ("wow", "scared")
    closed = blink and ((t + x * .0031) % 3.7) < .1 and mood not in ("wow", "scared", "dizzy")
    for sx in (-13, 13):
        cx_, cy_ = sx + ex, hy + 3 + ey
        if mood == "effort":                                              # olhos apertados: > <
            ctx.set_line_width(4.5); ctx.set_line_cap(cairo.LINE_CAP_ROUND); d = 6 * (1 if sx < 0 else -1)
            ctx.move_to(cx_ - d, cy_ - 5); ctx.line_to(cx_ + d, cy_); ctx.line_to(cx_ - d, cy_ + 5); ctx.set_source_rgba(*VOID, a); ctx.stroke()
        elif mood == "dizzy":                                             # espiral simples
            ctx.set_line_width(3.5); ctx.new_sub_path(); ctx.arc(cx_, cy_, 6.5, t * 9, t * 9 + 4.6); ctx.set_source_rgba(*VOID, a); ctx.stroke()
        elif closed or mood == "calm":
            rrect(ctx, cx_ - 6, cy_ - 1.5, 12, 3.4, 1.7); fill(ctx, VOID, a)
        else:
            circle(ctx, cx_, cy_, 8 if big else 5.6, VOID, a)
            if big: circle(ctx, cx_ + 2.2, cy_ - 2.4, 2.2, body, a)        # brilho: olho arregalado
    mx, my = ex * .7, hy + 21 + ey * .6
    if mood == "wow": circle(ctx, mx, my, 7.5, VOID, a)
    elif mood == "scared":
        ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(mx - 10, my)
        for i in range(1, 5): ctx.line_to(mx - 10 + i * 5, my + (3 if i % 2 else -3))
        ctx.set_source_rgba(*VOID, a); ctx.stroke()
    elif mood == "happy":
        ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.new_sub_path(); ctx.arc(mx, my - 9, 11, .35, PI - .35)
        ctx.set_source_rgba(*VOID, a); ctx.stroke()
    elif mood == "effort": rrect(ctx, mx - 8, my - 3, 16, 7, 3); fill(ctx, VOID, a)
    elif mood == "dizzy":
        ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(mx, my + 6, 8, PI + .5, 2 * PI - .5); ctx.set_source_rgba(*VOID, a); ctx.stroke()
    ctx.restore()
    c, sn = math.cos(rot), math.sin(rot)
    return [(x + (hx_ * c - hy_ * sn) * s, y + (hx_ * sn + hy_ * c) * s) for hx_, hy_ in hands]   # mãos na tela
