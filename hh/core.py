"""HyperHypothesis — núcleo do motor de motion graphics 2D (1080x1920, 30 fps).
Marca (cores, fontes, logo), personagens, utilidades, linha do tempo e legendas.
O vídeo ativo vem de HH_VIDEO (pasta com timing.json e meta.json); ver hh/render.py.
"""
import os, sys, json, math, random, subprocess
import cairocffi as cairo
from fontTools.ttLib import TTFont
from fontTools.pens.cairoPen import CairoPen

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.environ["HH_VIDEO"]
FONTS = os.path.join(REPO, "brand", "fonts")
OUT = os.path.join(VIDEO, "out"); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
PI = math.pi

def hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
VOID, ORBIT, LINE = hx("0A0C10"), hx("161B26"), hx("2A3140")
INK, MUTED = hx("F2EEE6"), hx("9AA1AE")
RED, BLUE, SOLAR = hx("FF5A1F"), hx("4DD6FF"), hx("FFC93C")

# ---------------------------------------------------------------- timing
T = json.load(open(os.path.join(VIDEO, "timing.json")))
META = json.load(open(os.path.join(VIDEO, "meta.json")))
SEG = []
OFF = 0.5 if "start" in T["segments"][0] else 0.0   # respiro antes da primeira fala
t = T["lead_in"]; SPEECH = []
for s in T["segments"]:
    st = s.get("start", t) + OFF; en = s.get("end", st + s["d"]) + (OFF if "end" in s else 0)
    SEG.append((st, en, s["t"])); SPEECH.append([(a + OFF, b + OFF) for a, b in s.get("chunks", [[st - OFF, en - OFF]])])
    t = en if "end" in s else t + s["d"]
TOTAL = SEG[-1][1] + T["tail"]
def S(i): return SEG[i][0]
def E(i): return SEG[i][1]

# ---------------------------------------------------------------- utils
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(lerp(a, b, k) for a, b in zip(c1, c2))
def prog(t, t0, d): return clamp((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def eo(k): return 1 - (1 - k) ** 3                         # ease out cubic
def eio(k): return 4*k**3 if k < .5 else 1 - (-2*k + 2)**3 / 2
def back(k):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2

class Font:
    def __init__(self, file, wght):
        self.f = TTFont(os.path.join(FONTS, file))
        self.gs = self.f.getGlyphSet(location={"wght": wght})
        self.cmap = self.f.getBestCmap(); self.upm = self.f["head"].unitsPerEm
    def gw(self, ch):
        g = self.cmap.get(ord(ch)); return self.gs[g].width if g else self.upm * .3
    def width(self, txt, size, track=0.0):
        return sum(self.gw(c) for c in txt) * size / self.upm + track * size * max(0, len(txt) - 1)
    def path(self, ctx, txt, size, x, y, track=0.0):
        s = size / self.upm; cx = 0.0
        for c in txt:
            g = self.cmap.get(ord(c))
            if g:
                ctx.save(); ctx.translate(x + cx, y); ctx.scale(s, -s)
                self.gs[g].draw(CairoPen(self.gs, ctx)); ctx.restore()
            cx += self.gw(c) * s + track * size

DISP = Font("Unbounded-Variable.ttf", 800)
BOLD = Font("Unbounded-Variable.ttf", 700)
LITE = Font("Unbounded-Variable.ttf", 300)
SANS = Font("Manrope-Variable.ttf", 600)
SANSB = Font("Manrope-Variable.ttf", 800)

NOW = 0.0          # tempo do frame atual (o render atualiza)
MIN_TEXT = 36      # px: menor texto permitido na tela (fora HUD e legenda)
LINT = {}          # (texto, tamanho) -> primeiro instante em que apareceu pequeno demais
TEXTS = []         # caixas de texto do frame atual: (x0, y0, x1, y1, texto)
_SKIP_LINT = [False]

def text(ctx, txt, font, size, x, y, col, a=1.0, align="c", track=0.0):
    if a <= 0: return 0
    w = font.width(txt, size, track)
    x0 = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    font.path(ctx, txt, size, x0, y, track)
    ctx.set_source_rgba(*col, a); ctx.fill()
    if a > .5 and not _SKIP_LINT[0] and txt.strip():
        eff = abs(ctx.user_to_device_distance(0, size)[1])
        if eff < MIN_TEXT - .5: LINT.setdefault((txt, round(eff)), round(NOW, 2))
        X0, Y0 = ctx.user_to_device(x0, y - size * .8); X1, Y1 = ctx.user_to_device(x0 + w, y + size * .2)
        TEXTS.append((X0, Y0, X1, Y1, txt))
    return w

def text_fit(ctx, txt, font, size, x, y, col, a=1.0, maxw=888, track=0.0):
    w = font.width(txt, size, track)
    if w > maxw: size *= maxw / w
    return text(ctx, txt, font, size, x, y, col, a, "c", track)

def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -PI/2, 0); ctx.arc(x + w - r, y + h - r, r, 0, PI/2)
    ctx.arc(x + r, y + h - r, r, PI/2, PI); ctx.arc(x + r, y + r, r, PI, 1.5*PI); ctx.close_path()

def fill(ctx, col, a=1.0): ctx.set_source_rgba(*col, a); ctx.fill()
def circle(ctx, x, y, r, col, a=1.0):
    ctx.new_sub_path(); ctx.arc(x, y, max(r, 0.01), 0, 2*PI); fill(ctx, col, a)

# ---------------------------------------------------------------- marca e personagens
def mark(ctx, ox, oy, k, a=1.0):
    ctx.move_to(ox + 2*k, oy + 57*k)
    for x, y in [(30, 52), (66, 52), (66, 68), (30, 68), (2, 63)]: ctx.line_to(ox + x*k, oy + y*k)
    ctx.close_path(); fill(ctx, RED, a)
    rrect(ctx, ox + 22*k, oy + 20*k, 18*k, 80*k, 4*k); rrect(ctx, ox + 60*k, oy + 20*k, 18*k, 80*k, 4*k); fill(ctx, INK, a)
    circle(ctx, ox + 100*k, oy + 60*k, 10*k, BLUE, a)

def person(ctx, x, y, s=1.0, body=INK, hair=None, a=1.0, hunch=0.0, arms=(.22, -.22), mood=None, look=0.0, blink=True):
    """'Você': cabeça círculo, corpo pílula, braços em pílula. (x,y) = pés.
    arms = (ângulo braço esquerdo, direito) em rad, 0 = para baixo, +/-2.6 = para cima.
    mood: None | "wow" (olhos grandes, boca O) | "happy" (sorriso) | "scared" (olhos grandes, boca reta).
    look: -1..1 desloca o olhar. Pisca sozinho a cada ~3,5 s."""
    if a <= 0 or s <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(hunch * 0.18); ctx.scale(s, s)
    for sx, ang in ((-1, arms[0]), (1, arms[1])):            # braços atrás do corpo
        ctx.save(); ctx.translate(sx * 26, -108); ctx.rotate(ang); rrect(ctx, -11, -6, 22, 84, 11); fill(ctx, body, a); ctx.restore()
    rrect(ctx, -34, -130, 68, 130, 34); fill(ctx, body, a)
    hy = -178 + hunch * 10
    circle(ctx, 0, hy, 40, body, a)
    if hair:
        ctx.new_sub_path(); ctx.arc(0, hy, 42, PI*1.05, PI*1.95); ctx.close_path(); fill(ctx, hair, a)
    big = mood in ("wow", "scared"); ex = look * 6
    closed = blink and ((NOW + x * .0031) % 3.5) < .11
    for sx in (-13, 13):
        if closed: rrect(ctx, sx + ex - 6, hy + 3, 12, 3, 1.5); fill(ctx, VOID, a)
        else: circle(ctx, sx + ex, hy + 4, 7.5 if big else 5.5, VOID, a)
    if mood == "wow": circle(ctx, ex, hy + 22, 7, VOID, a)
    elif mood == "scared": rrect(ctx, ex - 9, hy + 20, 18, 4, 2); fill(ctx, VOID, a)
    elif mood == "happy":
        ctx.set_line_width(4); ctx.new_sub_path(); ctx.arc(ex, hy + 12, 11, .3, PI - .3); ctx.set_source_rgba(*VOID, a); ctx.stroke()
    ctx.restore()

def ship(ctx, x, y, s=1.0, flame=0.0, a=1.0, hull=INK, tilt=0.0):
    if a <= 0: return
    ctx.save(); ctx.translate(x, y); ctx.rotate(tilt); ctx.scale(s, s)
    if flame > 0:
        L = 60 + 260 * flame
        ctx.move_to(-150, -26); ctx.line_to(-150 - L, -6); ctx.line_to(-150 - L, 6); ctx.line_to(-150, 26); ctx.close_path()
        fill(ctx, RED, a)
        ctx.move_to(-150, -12); ctx.line_to(-150 - L * .5, -3); ctx.line_to(-150 - L * .5, 3); ctx.line_to(-150, 12); ctx.close_path()
        fill(ctx, SOLAR, a)
    rrect(ctx, -140, -78, 70, 40, 8); rrect(ctx, -140, 38, 70, 40, 8); fill(ctx, RED, a)   # aletas
    rrect(ctx, -160, -48, 320, 96, 48); fill(ctx, hull, a)
    circle(ctx, 70, 0, 22, BLUE, a)
    ctx.restore()

# ---------------------------------------------------------------- fundo
random.seed(7)
BG = [(random.uniform(0, W), random.uniform(0, H), random.uniform(1.2, 3.0), random.uniform(.12, .5), random.uniform(0, 6)) for _ in range(110)]
def background(ctx, t, drift=0.0):
    ctx.set_source_rgb(*VOID); ctx.paint()
    for x, y, r, a, ph in BG:
        xx = (x - (drift + t * .012) * r * 60) % W           # parallax: estrelas maiores andam mais
        circle(ctx, xx, y, r, INK, a * (0.75 + 0.25 * math.sin(t * 1.3 + ph)))

def hud(ctx, t):
    _SKIP_LINT[0] = True
    mark(ctx, 84, 120, 0.42, 0.9)
    text(ctx, f"HIPÓTESE #{META['numero']:02d}", LITE, 30, 150, 158, MUTED, .95, "l", track=.08)
    _SKIP_LINT[0] = False

# ---------------------------------------------------------------- legendas
KEY = {w.lower() for w in META.get("highlight", [])}   # palavras da legenda em blueshift
NOCAP = set(META.get("nocap", []))               # segmentos sem legenda (texto grande na tela)
def chunks():
    out = []
    for i, (st, en, txt) in enumerate(SEG):
        if i in NOCAP: continue
        ws = txt.split(); groups = []; cur = []
        for w in ws:
            if cur and (len(cur) >= 3 or len(" ".join(cur + [w])) > 18): groups.append(cur); cur = []
            cur.append(w)
        if cur: groups.append(cur)
        # mapeia fração de caracteres -> tempo de fala real (pula as pausas internas)
        sp = SPEECH[i]; spd = sum(b - a for a, b in sp)
        def at(f):
            x = f * spd
            for a, b in sp:
                if x <= b - a: return a + x
                x -= b - a
            return sp[-1][1]
        tot = sum(len(" ".join(g)) + 1 for g in groups); acc = 0
        for gi, g in enumerate(groups):
            a = at(acc / tot); acc += len(" ".join(g)) + 1
            b = at(acc / tot) if gi < len(groups) - 1 else en + 0.25
            out.append((a, b, g))
    return out
CAPS = chunks()

def captions(ctx, t):
    for st, en, g in CAPS:
        if st <= t < en:
            k = prog(t, st, 0.12); sc = lerp(0.85, 1.0, back(k))
            size = 60 * sc; y = 1460
            words = [(w, BLUE if w.lower() in KEY else INK) for w in g]
            space = BOLD.width(" ", size)
            tw = sum(BOLD.width(w, size) for w, _ in words) + space * (len(words) - 1)
            if tw > 900: size *= 900 / tw; space *= 900 / tw; tw = 900
            # pílula de fundo para leitura
            rrect(ctx, 540 - tw / 2 - 28, y - size * 0.95, tw + 56, size * 1.35, 999); fill(ctx, VOID, 0.55 * k)
            # karaokê: a palavra acende quando é falada (tempo proporcional às letras)
            tot = sum(len(w) + 1 for w, _ in words); acc = 0; x = 540 - tw / 2
            _SKIP_LINT[0] = True
            for w, c in words:
                ws = st + (en - st) * acc / tot * .9; acc += len(w) + 1
                lit = .45 + .55 * prog(t, ws, .08)
                x += text(ctx, w, BOLD, size, x, y, c, k * lit, "l") + space
            _SKIP_LINT[0] = False
            return

