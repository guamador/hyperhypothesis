"""Gera conceitos de logo e banners do HyperHypothesis.
Uso: python3 -m brand.tools.brandkit <pasta_saida> [logo]
  logo = "h" (atual, padrão) | "doppler" | "pergunta" | "orbita"
"""
import os, sys, math, random
os.environ.setdefault("HH_VIDEO", os.path.join(os.path.dirname(__file__), "..", "..", "videos", "02-terra-parasse"))
from hh.fx import *  # noqa: E402,F403

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "out_brand"; os.makedirs(OUTDIR, exist_ok=True)
LOGO = sys.argv[2] if len(sys.argv) > 2 else "h"

# ---------------------------------------------------------------- símbolos (centrados em 0,0, raio útil ~100)
def sym_h(ctx, k=1.0):
    """Atual: H em movimento, feixe redshift atrás, ponto blueshift à frente."""
    mark(ctx, -60 * k, -60 * k, k)

def sym_doppler(ctx, k=1.0):
    """Ondas Doppler: frentes de onda de uma fonte em movimento para a direita.
    Comprimidas e azuis à frente, espaçadas e vermelhas atrás. A fonte é o ponto blueshift."""
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.save(); ctx.translate(53 * k, 0)              # centraliza o desenho (as ondas ficam para trás)
    v = .55                                          # velocidade da fonte (fração da onda)
    for i, r in enumerate((96, 72, 48, 24)):
        cx = -v * r                                  # cada frente nasceu quando a fonte estava mais atrás
        ctx.set_line_width(12 * k)
        ctx.new_sub_path(); ctx.arc((cx) * k, 0, r * k, PI / 2, 3 * PI / 2)
        ctx.set_source_rgba(*RED, 1); ctx.stroke()
        ctx.new_sub_path(); ctx.arc((cx) * k, 0, r * k, -PI / 2, PI / 2)
        ctx.set_source_rgba(*BLUE, 1); ctx.stroke()
    circle(ctx, 0, 0, 14 * k, INK)
    ctx.restore()

def sym_pergunta(ctx, k=1.0):
    """Interrogação em velocidade: o gancho do '?' em ink com rastros redshift atrás e o ponto blueshift."""
    ctx.save(); ctx.scale(k, k); ctx.translate(14, 0)
    for j, (y, L) in enumerate(((-58, 70), (-28, 100), (2, 60))):
        rrect(ctx, -118 - L * .2, y - 7, L, 14, 7); fill(ctx, RED, 1 - j * .2)
    ctx.set_line_width(30); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.new_sub_path(); ctx.arc(0, -42, 42, PI * 1.05, PI * 2.25)
    ctx.line_to(0, 22); ctx.set_source_rgba(*INK, 1); ctx.stroke()
    circle(ctx, 0, 74, 18, BLUE)
    ctx.restore()

def sym_orbita(ctx, k=1.0):
    """Órbita: H sólido dentro de uma órbita inclinada; planeta blueshift com cauda redshift.
    A metade de trás da órbita passa atrás do H e a da frente por cima (profundidade)."""
    ctx.save(); ctx.scale(k, k)
    tilt, ry = -.35, .40
    def ell(a0, a1, w, col, al=1.0):
        ctx.save(); ctx.rotate(tilt); ctx.scale(1, ry); ctx.new_sub_path(); ctx.arc(0, 0, 112, a0, a1); ctx.restore()
        ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgba(*col, al); ctx.stroke()
    ell(PI, 2 * PI, 9, MUTED, .8)                                 # metade de trás
    rrect(ctx, -46, -56, 28, 112, 7); rrect(ctx, 18, -56, 28, 112, 7); rrect(ctx, -20, -11, 40, 22, 3); fill(ctx, INK)
    ell(0, PI, 9, MUTED, .8)                                      # metade da frente
    pa = -.35                                                     # posição do planeta (ângulo na elipse)
    for j in range(8):                                            # cauda redshift atrás do planeta
        ell(pa - .1 - j * .1, pa - j * .1, 16 - j * 1.6, RED, 1 - j * .11)
    x, y = 112 * math.cos(pa), 112 * ry * math.sin(pa)
    circle(ctx, x * math.cos(tilt) - y * math.sin(tilt), x * math.sin(tilt) + y * math.cos(tilt), 20, BLUE)
    ctx.restore()

SYMS = {"h": sym_h, "doppler": sym_doppler, "pergunta": sym_pergunta, "orbita": sym_orbita}

# ---------------------------------------------------------------- utilidades
def new(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.set_antialias(cairo.ANTIALIAS_BEST); return s, c

def stars(ctx, w, h, n, seed=1, a=1.0):
    rnd = random.Random(seed)
    for _ in range(n): circle(ctx, rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(1.2, 3.4), INK, rnd.uniform(.1, .5) * a)

def wordmark(ctx, x, y, size, align="l"):
    """HYPER (800) + HYPOTHESIS (300), linha de base em y. Retorna a largura."""
    w1 = DISP.width("HYPER", size); w2 = LITE.width("HYPOTHESIS", size); gap = size * .08; w = w1 + gap + w2
    x0 = x - w / 2 if align == "c" else x
    text(ctx, "HYPER", DISP, size, x0, y, INK, 1, "l"); text(ctx, "HYPOTHESIS", LITE, size, x0 + w1 + gap, y, INK, 1, "l")
    return w

def lockup(ctx, sym, cx, cy, sz, word=60):
    """Símbolo + wordmark lado a lado, centrados em (cx, cy)."""
    ww = DISP.width("HYPER", word) + word * .08 + LITE.width("HYPOTHESIS", word); total = sz * 2.1 + 40 + ww
    x0 = cx - total / 2
    ctx.save(); ctx.translate(x0 + sz * 1.05, cy); sym(ctx, sz / 100); ctx.restore()
    wordmark(ctx, x0 + sz * 2.1 + 40, cy + word * .36, word)

# ---------------------------------------------------------------- 1) folha de conceitos
def concepts():
    names = [("doppler", "A · ONDAS DOPPLER", "Frentes de onda de uma fonte em movimento: azul à frente, vermelho atrás."),
             ("pergunta", "B · INTERROGAÇÃO VELOZ", "O \"?\" da hipótese em alta velocidade, com rastros vermelhos."),
             ("orbita", "C · ÓRBITA", "O H no centro, com um planeta azul em órbita e a cauda vermelha.")]
    W_, H_ = 2400, 1500
    s, c = new(W_, H_); c.set_source_rgb(*VOID); c.paint(); stars(c, W_, H_, 160, 3, .6)
    text(c, "NOVOS CONCEITOS DE LOGO", BOLD, 54, 120, 140, INK, 1, "l", .06)
    text(c, "Atual: H com feixe e ponto. Escolha A, B ou C para os perfis e banners.", SANS, 34, 120, 200, MUTED, 1, "l")
    for i, (key, title, desc) in enumerate(names):
        x = 120 + i * 740; y = 300
        rrect(c, x, y, 680, 1100, 24); fill(c, ORBIT)
        circle(c, x + 340, y + 330, 230, VOID)                      # simulação do recorte circular de perfil
        c.save(); c.translate(x + 340, y + 330); SYMS[key](c, 1.55); c.restore()
        c.save(); c.translate(x + 340, y + 700); c.scale(.62, .62); lockup(c, SYMS[key], 0, 0, 70, 60); c.restore()
        text(c, title, BOLD, 32, x + 50, y + 860, BLUE, 1, "l", .02)
        words = desc.split(); line = ""; ly = y + 925
        for w in words:
            if SANS.width(line + " " + w, 32) > 590: text(c, line.strip(), SANS, 32, x + 50, ly, MUTED, 1, "l"); line = ""; ly += 44
            line += " " + w
        text(c, line.strip(), SANS, 32, x + 50, ly, MUTED, 1, "l")
    p = os.path.join(OUTDIR, "logo-conceitos.png"); s.write_to_png(p); return p

def avatars():
    out = []
    for key, fn in SYMS.items():
        s, c = new(1024, 1024); circle(c, 512, 512, 512, VOID)
        c.save(); c.translate(512, 512); fn(c, 3.4 if key != "h" else 3.4); c.restore()
        p = os.path.join(OUTDIR, f"avatar-{key}.png"); s.write_to_png(p); out.append(p)
    return out

# ---------------------------------------------------------------- 2) banners
def banner(w, h, safe, name, sym):
    """safe = (x, y, w, h) da área que aparece em todos os aparelhos."""
    s, c = new(w, h); c.set_source_rgb(*VOID); c.paint(); stars(c, w, h, int(w * h / 9000), 5)
    sx, sy, sw, sh = safe; cy = sy + sh / 2
    sc = sh / 423                                                  # escala relativa à área segura do YouTube
    # cenário fora/ao redor da área segura: globo à esquerda, céu relativístico à direita, rastros
    R = h * .62
    globe(c, -R * .25, h + R * .12, R, lon0=-50, lat0=18)
    globe_line(c, 0, -50, 18, R, -R * .25, h + R * .12, BLUE, .8, w=8 * sc)
    rnd = random.Random(9)
    for i in range(60):                                            # estrelas comprimidas à frente (aberração)
        ang = rnd.uniform(0, 2 * PI); rr = abs(rnd.gauss(0, 1)) * h * .16
        circle(c, w * .9 + rr * math.cos(ang), h * .32 + rr * math.sin(ang), rnd.uniform(2, 5) * sc, BLUE if rr < h * .1 else INK, .8)
    for j, (yy, L) in enumerate(((cy - sh * .32, w * .22), (cy + sh * .05, w * .3), (cy + sh * .4, w * .18))):
        rrect(c, sx - L - 60 * sc, yy, L, 16 * sc, 8 * sc); fill(c, RED, .85 - j * .2)
    # conteúdo dentro da área segura: símbolo + nome ocupando ~88% da largura segura
    SW = {"h": (1.12, .1), "doppler": (2.0, 0), "pergunta": (2.1, -.1), "orbita": (2.5, 0)}   # largura (×sz/100*100), desvio
    key = next(k for k, f in SYMS.items() if f is sym); fw, off = SW[key]
    word = 118 * sc
    def widths(word):
        sz = word * 1.15; ww = DISP.width("HYPER", word) + word * .08 + LITE.width("HYPOTHESIS", word)
        return sz, ww, fw * sz + 36 * sc + ww
    sz, ww, total = widths(word)
    if total > sw * .88: word *= sw * .88 / total; sz, ww, total = widths(word)
    x0 = sx + (sw - total) / 2; ty = cy - sh * .12
    c.save(); c.translate(x0 + fw * sz / 2 + off * sz, ty); sym(c, sz / 100); c.restore()
    wordmark(c, x0 + fw * sz + 36 * sc, ty + word * .36, word)
    text(c, "E se fosse possível? A física responde.", SANS, 46 * sc, sx + sw / 2, cy + sh * .27, BLUE, 1)
    text(c, "NOVOS VÍDEOS  SEG · QUA · SEX · SÁB", BOLD, 30 * sc, sx + sw / 2, cy + sh * .43, MUTED, 1, track=.08)
    p = os.path.join(OUTDIR, name); s.write_to_png(p)
    # prévia com a área segura marcada (só para conferência)
    c.set_line_width(4); c.set_dash([20, 14]); c.rectangle(*safe); c.set_source_rgba(*SOLAR, .9); c.stroke()
    s.write_to_png(p.replace(".png", "-guia.png"))
    return p

if __name__ == "__main__":
    sym = SYMS[LOGO]
    print(concepts()); [print(a) for a in avatars()]
    # YouTube: 2560×1440; área segura (todos os aparelhos) 1546×423 no centro
    print(banner(2560, 1440, ((2560 - 1546) / 2, (1440 - 423) / 2, 1546, 423), f"banner-youtube-{LOGO}.png", sym))
    # Facebook: 1640×924 (celular mostra tudo); computador corta para a faixa central 1640×624.
    # Área segura: faixa do computador, sem os cantos onde a foto de perfil e os botões ficam.
    print(banner(1640, 924, (260, 150 + 60, 1120, 504 - 60), f"capa-facebook-{LOGO}.png", sym))
