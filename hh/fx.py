"""Peças visuais da v2: ícones SVG (Phosphor, MIT), globo com continentes, cenário e efeitos.
Uso nas cenas: `from hh.fx import *` (já traz tudo do core).
"""
import os, re, json, math, random, functools
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier, Arc, Close
from hh.core import *  # noqa: F401,F403
from hh import core as _core

ICONS = os.path.join(REPO, "brand", "icons")

# ---------------------------------------------------------------- ícones SVG
_EL = re.compile(r"<(path|circle|rect|ellipse)\b([^>]*)/?>")
_AT = re.compile(r'([a-zA-Z-]+)="([^"]*)"')

@functools.lru_cache(maxsize=None)
def _icon_ops(name, style):
    """Lê o SVG uma vez e converte em comandos de cairo no espaço 256×256. Retorna [(camada, ops)]."""
    fn = os.path.join(ICONS, style, f"{name}-{style}.svg" if style != "regular" else f"{name}.svg")
    if not os.path.exists(fn):
        raise FileNotFoundError(f"ícone não existe: {name} ({style}). Veja brand/icons/{style}/")
    src = open(fn).read(); layers = []
    for tag, attrs in _EL.findall(src):
        A = dict(_AT.findall(attrs)); layer = 2 if float(A.get("opacity", "1")) < 1 else 1
        ops = []
        if tag == "path":
            for seg in parse_path(A["d"]):
                if isinstance(seg, Move): ops.append(("M", seg.end.real, seg.end.imag))
                elif isinstance(seg, Line): ops.append(("L", seg.end.real, seg.end.imag))
                elif isinstance(seg, CubicBezier):
                    ops.append(("C", seg.control1.real, seg.control1.imag, seg.control2.real, seg.control2.imag, seg.end.real, seg.end.imag))
                elif isinstance(seg, QuadraticBezier):
                    s0, c, e = seg.start, seg.control, seg.end
                    c1 = s0 + 2 / 3 * (c - s0); c2 = e + 2 / 3 * (c - e)
                    ops.append(("C", c1.real, c1.imag, c2.real, c2.imag, e.real, e.imag))
                elif isinstance(seg, Arc):
                    n = max(4, int(seg.length() / 6))
                    for i in range(1, n + 1):
                        p = seg.point(i / n); ops.append(("L", p.real, p.imag))
                elif isinstance(seg, Close): ops.append(("Z",))
        elif tag in ("circle", "ellipse"):
            cx, cy = float(A.get("cx", 0)), float(A.get("cy", 0))
            rx = float(A.get("r", A.get("rx", 0))); ry = float(A.get("r", A.get("ry", rx)))
            ops.append(("E", cx, cy, rx, ry))
        elif tag == "rect":
            ops.append(("R", float(A.get("x", 0)), float(A.get("y", 0)), float(A["width"]), float(A["height"]), float(A.get("rx", 0))))
        if ops: layers.append((layer, ops))
    return layers

def icon(ctx, name, x, y, size, col=INK, a=1.0, style="fill", col2=None, rot=0.0, flip=False):
    """Desenha o ícone Phosphor `name` centrado em (x, y) com `size` px.
    style: "fill" (chapado) ou "duotone" (camada de fundo em col2, padrão = col a 35%)."""
    if a <= 0 or size <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); s = size / 256; ctx.scale(-s if flip else s, s); ctx.translate(-128, -128)
    for layer, ops in _icon_ops(name, style):
        ctx.new_path()
        for op in ops:
            k = op[0]
            if k == "M": ctx.move_to(op[1], op[2])
            elif k == "L": ctx.line_to(op[1], op[2])
            elif k == "C": ctx.curve_to(*op[1:])
            elif k == "Z": ctx.close_path()
            elif k == "E":
                ctx.save(); ctx.translate(op[1], op[2]); ctx.scale(op[3], op[4]); ctx.new_sub_path(); ctx.arc(0, 0, 1, 0, 2 * PI); ctx.restore()
            elif k == "R": rrect(ctx, op[1], op[2], op[3], op[4], op[5])
        if layer == 2: ctx.set_source_rgba(*(col2 or col), a * (1 if col2 else .35))
        else: ctx.set_source_rgba(*col, a)
        ctx.fill()
    ctx.restore()

# ---------------------------------------------------------------- globo com continentes
_LAND = json.load(open(os.path.join(REPO, "brand", "data", "land.json")))["rings"]
LAND_COL = hx("3B475A")      # continentes: mais claro que orbit, contraste 1,9:1 sobre o oceano
OCEAN_COL = hx("12233A")

def geo(lon, lat, lon0, lat0, R, cx, cy):
    """Projeção ortográfica. Retorna (x, y, visível)."""
    l, p, l0, p0 = map(math.radians, (lon, lat, lon0, lat0))
    cosc = math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)
    x = R * math.cos(p) * math.sin(l - l0)
    y = R * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
    return cx + x, cy - y, cosc >= 0

def globe(ctx, cx, cy, R, lon0=0.0, lat0=15.0, a=1.0, grid=True, night=0.0, ring=True):
    """Terra em projeção ortográfica. lon0 = longitude no centro (aumente com o tempo para girar
    de oeste para leste: lon0 = base - t*vel). lat0 = inclinação vista de cima."""
    if a <= 0 or R <= 0: return
    if ring:
        circle(ctx, cx, cy, R * 1.06, BLUE, .10 * a); circle(ctx, cx, cy, R * 1.03, BLUE, .12 * a)  # atmosfera chapada
    circle(ctx, cx, cy, R, OCEAN_COL, a)
    ctx.save(); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.clip()
    for ring_ in _LAND:
        pts = []; anyv = False
        for lon, lat in ring_:
            x, y, v = geo(lon, lat, lon0, lat0, R, cx, cy)
            if not v:                                   # ponto atrás: empurra para a borda (limbo)
                dx, dy = x - cx, y - cy; d = math.hypot(dx, dy) or 1
                x, y = cx + dx / d * R, cy + dy / d * R
            else: anyv = True
            pts.append((x, y))
        if not anyv: continue
        ctx.move_to(*pts[0])
        for p in pts[1:]: ctx.line_to(*p)
        ctx.close_path()
    ctx.set_source_rgba(*LAND_COL, a); ctx.fill()
    if grid:
        ctx.set_line_width(2)
        for lat in (-60, -30, 0, 30, 60):
            first = True
            for i in range(0, 361, 6):
                x, y, v = geo(i - 180, lat, lon0, lat0, R, cx, cy)
                if v:
                    (ctx.move_to if first else ctx.line_to)(x, y); first = False
                else: first = True
            ctx.set_source_rgba(*LINE, .55 * a); ctx.stroke()
        for lon in range(-180, 180, 30):
            first = True
            for i in range(-90, 91, 6):
                x, y, v = geo(lon, i, lon0, lat0, R, cx, cy)
                if v:
                    (ctx.move_to if first else ctx.line_to)(x, y); first = False
                else: first = True
            ctx.set_source_rgba(*LINE, .45 * a); ctx.stroke()
    if night > 0:                                       # lado noturno: metade direita escurecida (chapado)
        ctx.rectangle(cx + R * .15, cy - R, R, 2 * R); fill(ctx, VOID, .35 * night * a)
    ctx.restore()
    ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.set_source_rgba(*MUTED, .45 * a); ctx.stroke()

def globe_line(ctx, lat, lon0, lat0, R, cx, cy, col, a=1.0, w=6):
    """Desenha um paralelo (ex.: equador) só na face visível."""
    ctx.set_line_width(w); first = True
    for i in range(0, 361, 3):
        x, y, v = geo(i - 180, lat, lon0, lat0, R, cx, cy)
        if v: (ctx.move_to if first else ctx.line_to)(x, y); first = False
        else: first = True
    ctx.set_source_rgba(*col, a); ctx.stroke()

def globe_band(ctx, lat_max, lon0, lat0, R, cx, cy, col, a=.3):
    """Faixa |lat| < lat_max pintada sobre o globo (ex.: região de vento supersônico)."""
    ctx.save(); ctx.new_sub_path(); ctx.arc(cx, cy, R, 0, 2 * PI); ctx.clip()
    top = [geo(i - 180, lat_max, lon0, lat0, R, cx, cy) for i in range(0, 361, 3)]
    bot = [geo(i - 180, -lat_max, lon0, lat0, R, cx, cy) for i in range(360, -1, -3)]
    pts = [(x, y) for x, y, v in top if v] + [(x, y) for x, y, v in bot if v]
    if pts:
        ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; ctx.close_path(); fill(ctx, col, a)
    ctx.restore()

# ---------------------------------------------------------------- cenário
def cloud(ctx, x, y, s=1.0, col=INK, a=1.0):
    """Nuvem chapada feita de pílulas e círculos."""
    if a <= 0: return
    rrect(ctx, x - 90 * s, y - 22 * s, 180 * s, 44 * s, 22 * s); fill(ctx, col, a)
    circle(ctx, x - 30 * s, y - 26 * s, 34 * s, col, a); circle(ctx, x + 22 * s, y - 34 * s, 42 * s, col, a)

def tree(ctx, x, y, s=1.0, col=None, a=1.0, lean=0.0):
    """Árvore chapada (pés em x, y). lean inclina a copa (vento)."""
    col = col or hx("2E6B5E")
    rrect(ctx, x - 7 * s, y - 70 * s, 14 * s, 70 * s, 5 * s); fill(ctx, MUTED, a)
    circle(ctx, x + lean * 30 * s, y - 100 * s, 46 * s, col, a); circle(ctx, x - 22 * s + lean * 24 * s, y - 78 * s, 30 * s, col, a)
    if _core.THEME == "natal":                               # neve na copa + pisca-pisca
        ctx.save(); ctx.new_sub_path(); ctx.arc(x + lean * 30 * s, y - 100 * s, 46 * s, PI * 1.08, PI * 1.92)
        ctx.arc_negative(x + lean * 30 * s, y - 112 * s, 40 * s, PI * 1.9, PI * 1.1); ctx.close_path(); fill(ctx, INK, a * .95); ctx.restore()
        for j in range(6):
            ang = PI * (.15 + j * .14); cx_ = x + lean * 30 * s + 40 * s * math.cos(ang); cy_ = y - 92 * s + 34 * s * math.sin(ang) * .6
            on = int(_core.NOW * 3 + j) % 2 == 0
            circle(ctx, cx_, cy_, 5.5 * s, (RED, SOLAR, BLUE)[j % 3], a * (1 if on else .35))

def building(ctx, x, y, w, h, col=ORBIT, win=MUTED, a=1.0, lit=.6, seed=0, skew=0.0):
    """Prédio com janelas (base em x..x+w, chão em y). skew desloca o topo para a direita (px)."""
    if a <= 0: return
    rnd = random.Random(seed)
    floors = max(1, int(h // 46)); cols = max(1, int((w - 24) // 34))
    for f in range(floors):
        fy = y - (f + 1) * (h / floors); dx = skew * ((f + 1) / floors) ** 1.6
        rrect(ctx, x + dx, fy, w, h / floors + 1, 3); fill(ctx, col, a)
        for c in range(cols):
            on = rnd.random() < lit
            rrect(ctx, x + dx + 14 + c * 34, fy + 12, 18, h / floors - 22, 3); fill(ctx, SOLAR if on else win, a * (.85 if on else .35))

    if _core.THEME == "natal":                               # neve no telhado + pisca-pisca na fachada
        top = y - h; rrect(ctx, x + skew - 6, top - 12, w + 12, 20, 10); fill(ctx, INK, a * .95)
        n = max(3, int(w // 22))
        for j in range(n):
            px = x + skew * .98 + 10 + j * (w - 20) / max(1, n - 1); py = top + 18 + 8 * math.sin(j * 1.3)
            on = int(_core.NOW * 3 + j) % 2 == 0
            circle(ctx, px, py, 5, (RED, SOLAR, BLUE, INK)[j % 4], a * (1 if on else .3))

def skyline(ctx, y, seed=1, a=1.0, x0=-20, x1=W + 20, hmin=160, hmax=420, col=ORBIT):
    rnd = random.Random(seed); x = x0
    while x < x1:
        w = rnd.randint(90, 170); h = rnd.randint(hmin, hmax)
        building(ctx, x, y, w, h, col=col, a=a, seed=rnd.randint(0, 999)); x += w + rnd.randint(6, 18)

def wave(ctx, t, y, amp, length, col, a=1.0, speed=1.0, x0=-20, x1=W + 20, bottom=H + 20, phase=0.0):
    """Faixa de oceano com crista senoidal que anda para a direita."""
    ctx.move_to(x0, bottom); ctx.line_to(x0, y)
    for x in range(int(x0), int(x1) + 1, 12):
        ctx.line_to(x, y + amp * math.sin((x / length - t * speed) * 2 * PI + phase))
    ctx.line_to(x1, bottom); ctx.close_path(); fill(ctx, col, a)

def arrow(ctx, x1, y1, x2, y2, col, a=1.0, w=10, head=34):
    if a <= 0: return
    ang = math.atan2(y2 - y1, x2 - x1); L = math.hypot(x2 - x1, y2 - y1)
    if L < 2: return
    ctx.save(); ctx.translate(x1, y1); ctx.rotate(ang); hl = min(head, L * .6)
    rrect(ctx, 0, -w / 2, L - hl * .8, w, w / 2); fill(ctx, col, a)
    ctx.move_to(L, 0); ctx.line_to(L - hl, -hl * .62); ctx.line_to(L - hl, hl * .62); ctx.close_path(); fill(ctx, col, a)
    ctx.restore()

def trails(ctx, x, y, k, a=1.0, spread=(-150, -90, -30), lens=(220, 360, 260)):
    """Rastros de velocidade em redshift, sempre atrás (à esquerda) de x."""
    for j, (dy, ln) in enumerate(zip(spread, lens)):
        L = ln * k; rrect(ctx, x - 70 - L, y + dy - 5, L, 10, 5); fill(ctx, RED, a * (.85 - j * .15))

def burst(ctx, x, y, k, col=SOLAR, n=10, r0=30, r1=110, w=7, a=1.0, seed=0):
    """Estouro radial de traços (impacto). k de 0 a 1."""
    if k <= 0 or k >= 1: return
    rnd = random.Random(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(w)
    for j in range(n):
        ang = j * 2 * PI / n + rnd.uniform(-.2, .2); rr = lerp(r0, r1, eo(k)); L = (1 - k) * 50
        ctx.move_to(x + rr * math.cos(ang), y + rr * math.sin(ang))
        ctx.line_to(x + (rr + L) * math.cos(ang), y + (rr + L) * math.sin(ang))
        ctx.set_source_rgba(*col, a * (1 - k)); ctx.stroke()

def debris(ctx, x, y, k, n=14, col=MUTED, a=1.0, seed=3, spread=260):
    """Pedaços voando para a direita/cima com gravidade."""
    rnd = random.Random(seed)
    for _ in range(n):
        vx, vy = rnd.uniform(.3, 1) * spread, -rnd.uniform(.4, 1) * spread * 1.2
        px, py = x + vx * k, y + vy * k + 900 * k * k; sz = rnd.uniform(8, 20)
        ctx.save(); ctx.translate(px, py); ctx.rotate(k * rnd.uniform(-6, 6)); rrect(ctx, -sz / 2, -sz / 2, sz, sz * .7, 3)
        fill(ctx, col, a * (1 - k * .6)); ctx.restore()

def glitch_text(ctx, txt, font, size, x, y, k, t, amp=12):
    """Texto com separação redshift/blueshift que estabiliza (k: entrada)."""
    j = (math.sin(t * 47) * amp + math.sin(t * 91) * amp * .6) * (1 - clamp(k * 1.5))
    text_fit(ctx, txt, font, size, x - j, y, RED, .85 * k); text_fit(ctx, txt, font, size, x + j, y, BLUE, .85 * k)
    text_fit(ctx, txt, font, size, x, y, INK, k)

def counter(v, dec=0):
    """Formata número no padrão brasileiro: 1.670 / 8,5."""
    s = f"{v:,.{dec}f}"; return s.replace(",", "X").replace(".", ",").replace("X", ".")
