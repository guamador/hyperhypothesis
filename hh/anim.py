"""Animação da v3: partículas com física, molas, texto cinético.
Tudo é determinístico (estado calculado a partir de t - t0 e de uma semente), porque cada frame é
renderizado de forma independente. Uso nas cenas: `from hh.anim import *` (já traz fx e core).
"""
import math, random
from hh.fx import *  # noqa: F401,F403
from hh import core as _c

# ---------------------------------------------------------------- easings extras
def spring(k, freq=3.2, damp=5.0):
    """Mola amortecida 0 -> 1 com pequeno 'overshoot' (bom para pop-ins)."""
    if k <= 0: return 0.0
    if k >= 1: return 1.0
    return 1 - math.exp(-damp * k) * math.cos(2 * PI * freq * k)

def wobble(t, amp=1.0, f=1.3, seed=0):
    """Ruído suave (soma de senos) para movimento secundário: flutuar, balançar."""
    return amp * (math.sin(t * f * 2.1 + seed) * .6 + math.sin(t * f * 3.7 + seed * 1.7) * .4)

# ---------------------------------------------------------------- partículas
def smoke(ctx, x, y, t0, t, n=10, col=MUTED, life=1.6, spread=120, rise=160, r0=18, r1=70, a=.55, seed=0, wind=0.0):
    """Baforadas de fumaça que sobem, crescem e somem."""
    dt = t - t0
    if dt < 0: return
    rnd = random.Random(seed)
    for _ in range(n):
        d = rnd.uniform(0, life * .35); L = life * rnd.uniform(.7, 1.1); k = (dt - d) / L
        if not 0 <= k <= 1: rnd.random(); rnd.random(); continue
        ang = rnd.uniform(-PI, 0); sp = rnd.uniform(.3, 1) * spread
        px = x + math.cos(ang) * sp * eo(k) + wind * dt * 60
        py = y + math.sin(ang) * sp * .5 * eo(k) - rise * k
        circle(ctx, px, py, lerp(r0, r1, eo(k)) * rnd.uniform(.7, 1.2), col, a * (1 - k) ** 1.4)

def sparks(ctx, x, y, t0, t, n=18, col=SOLAR, speed=900, life=.7, g=1800, w=5, a=1.0, seed=0, ang0=-PI, ang1=0):
    """Faíscas com gravidade, desenhadas como traços na direção do movimento."""
    dt = t - t0
    if dt < 0 or dt > life * 1.3: return
    rnd = random.Random(seed); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    for _ in range(n):
        ang = rnd.uniform(ang0, ang1); v = rnd.uniform(.35, 1) * speed; L = life * rnd.uniform(.6, 1.2)
        if dt > L: continue
        vx, vy = math.cos(ang) * v, math.sin(ang) * v
        px, py = x + vx * dt, y + vy * dt + .5 * g * dt * dt
        tx, ty = vx, vy + g * dt; m = math.hypot(tx, ty) or 1
        tail = 28 * (1 - dt / L) + 6
        ctx.move_to(px, py); ctx.line_to(px - tx / m * tail, py - ty / m * tail)
        ctx.set_source_rgba(*col, a * (1 - dt / L)); ctx.stroke()

def dust(ctx, x, y, t0, t, n=8, col=MUTED, life=1.0, dirx=-1, a=.5, seed=0, size=1.0):
    """Poeira rente ao chão (atrás de quem desliza: dirx=-1 solta para a esquerda)."""
    dt = t - t0
    if dt < 0: return
    rnd = random.Random(seed)
    for _ in range(n):
        d = rnd.uniform(0, life * .4); L = life * rnd.uniform(.6, 1); k = (dt - d) / L
        if not 0 <= k <= 1: rnd.random(); rnd.random(); continue
        px = x + dirx * rnd.uniform(40, 220) * eo(k); py = y - rnd.uniform(0, 40) * eo(k)
        circle(ctx, px, py, (14 + 40 * eo(k)) * size * rnd.uniform(.7, 1.2), col, a * (1 - k))

def trail_dust(ctx, x, y, t, rate=14, life=.8, col=MUTED, a=.45, size=1.0, seed=0):
    """Poeira contínua atrás de algo que desliza: emite `rate` baforadas por segundo a partir de (x, y)."""
    for i in range(int(rate * life) + 1):
        k = ((t * rate + i) % (rate * life)) / (rate * life)
        rnd = random.Random(seed + int(t * rate) - i)
        px = x - 30 - 160 * eo(k) * rnd.uniform(.6, 1.2); py = y - 30 * eo(k) * rnd.uniform(.3, 1)
        circle(ctx, px, py, (12 + 34 * k) * size, col, a * (1 - k))

def spray(ctx, x, y, t0, t, n=22, col=INK, speed=700, life=.9, g=1600, a=.9, seed=0, ang0=-PI * .9, ang1=-PI * .15):
    """Borrifos (gotas) para ondas e respingos."""
    dt = t - t0
    if dt < 0 or dt > life * 1.3: return
    rnd = random.Random(seed)
    for _ in range(n):
        ang = rnd.uniform(ang0, ang1); v = rnd.uniform(.3, 1) * speed; L = life * rnd.uniform(.6, 1.1)
        if dt > L: continue
        px = x + math.cos(ang) * v * dt; py = y + math.sin(ang) * v * dt + .5 * g * dt * dt
        circle(ctx, px, py, rnd.uniform(4, 11) * (1 - .5 * dt / L), col, a * (1 - dt / L))

def shockwave(ctx, x, y, t0, t, r1=420, life=.6, col=INK, w=10, a=.8):
    """Anel de choque que se expande."""
    k = (t - t0) / life
    if not 0 < k < 1: return
    ctx.set_line_width(w * (1 - k) + 1); ctx.new_sub_path(); ctx.arc(x, y, r1 * eo(k), 0, 2 * PI)
    ctx.set_source_rgba(*col, a * (1 - k)); ctx.stroke()

def speedlines(ctx, t, a=1.0, n=26, col=INK, y0=200, y1=1350, speed=3.0, seed=1):
    """Linhas de velocidade atravessando a tela (sensação de movimento rápido para a direita)."""
    rnd = random.Random(seed)
    for _ in range(n):
        y = rnd.uniform(y0, y1); L = rnd.uniform(80, 320); ph = rnd.random(); v = rnd.uniform(.7, 1.3) * speed
        u = (ph + t * v) % 1
        rrect(ctx, -L + (W + 2 * L) * u - L, y, L, rnd.choice((4, 6, 8)), 3); fill(ctx, col, a * .35 * math.sin(PI * u))

# ---------------------------------------------------------------- texto cinético
def pop_text(ctx, txt, font, size, x, y, col, t, t0, stagger=.035, dur=.45, a=1.0, align="c", track=0.0):
    """Texto que entra letra a letra com mola (escala + subida)."""
    if t < t0 or a <= 0: return
    w = font.width(txt, size, track)
    xx = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    eff = abs(ctx.user_to_device_distance(0, size)[1])
    if eff < _c.MIN_TEXT - .5: _c.LINT.setdefault((txt, round(eff)), round(_c.NOW, 2))
    X0, Y0 = ctx.user_to_device(xx, y - size * .8); X1, Y1 = ctx.user_to_device(xx + w, y + size * .2)
    _c.TEXTS.append((X0, Y0, X1, Y1, txt)); _c._SKIP_LINT[0] = True
    for i, ch in enumerate(txt):
        k = clamp((t - t0 - i * stagger) / dur); cw = font.width(ch, size)
        if k > 0 and ch != " ":
            s = spring(k); ctx.save(); ctx.translate(xx + cw / 2, y - size * .35)
            ctx.scale(max(.01, s), max(.01, s)); ctx.translate(0, 40 * (1 - eo(k)))
            text(ctx, ch, font, size, 0, size * .35, col, a * clamp(k * 3))
            ctx.restore()
        xx += cw + track * size
    _c._SKIP_LINT[0] = False

def pop_text_fit(ctx, txt, font, size, x, y, col, t, t0, maxw=888, **kw):
    w = font.width(txt, size)
    if w > maxw: size *= maxw / w
    pop_text(ctx, txt, font, size, x, y, col, t, t0, **kw)
