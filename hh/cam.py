"""Câmera virtual 2D (v4): um mundo contínuo em unidades próprias (ex.: km), visto por uma câmera com
posição, zoom e rotação. Permite plano-sequência: seguir o personagem, afastar até o planeta inteiro, girar.

    cam = Cam(cx, cy, z, rot, fx=540, fy=800)   # (cx, cy) do mundo aparece no ponto (fx, fy) da tela
    cam.apply(ctx) ... desenha em coordenadas do mundo ... cam.restore(ctx)
    x, y = cam.pt(wx, wy)                        # mundo -> tela (para desenhar algo em escala de tela, sempre "em pé")
    cam.px(n)                                    # n pixels de tela convertidos para unidades do mundo (larguras de traço)

Easings e utilidades de tempo extras ficam aqui também.
"""
import math

PI = math.pi

class Cam:
    def __init__(self, cx=0.0, cy=0.0, z=1.0, rot=0.0, fx=540.0, fy=960.0):
        self.cx, self.cy, self.z, self.rot, self.fx, self.fy = cx, cy, z, rot, fx, fy
    def apply(self, ctx):
        ctx.save(); ctx.translate(self.fx, self.fy); ctx.rotate(self.rot); ctx.scale(self.z, self.z); ctx.translate(-self.cx, -self.cy)
    def restore(self, ctx): ctx.restore()
    def pt(self, x, y):
        dx, dy = (x - self.cx) * self.z, (y - self.cy) * self.z
        c, s = math.cos(self.rot), math.sin(self.rot)
        return self.fx + dx * c - dy * s, self.fy + dx * s + dy * c
    def px(self, n): return n / self.z
    def view_radius(self, w=1080, h=1920):
        """Raio (em unidades do mundo) que cobre a tela inteira a partir do foco."""
        return math.hypot(max(self.fx, w - self.fx), max(self.fy, h - self.fy)) / self.z

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, k): return a + (b - a) * k
def lerp_log(a, b, k):
    """Interpola zoom em escala logarítmica (zoom parece constante ao olho)."""
    return math.exp(lerp(math.log(a), math.log(b), k))
def smooth(k): k = clamp(k); return k * k * (3 - 2 * k)
def smoother(k): k = clamp(k); return k * k * k * (k * (6 * k - 15) + 10)
def ease_in(k, p=2.0): return clamp(k) ** p
def ease_out(k, p=3.0): return 1 - (1 - clamp(k)) ** p
def anticipate(k):
    """Recua um pouco antes de avançar (antecipação) e chega suave: 0 -> 1."""
    k = clamp(k)
    if k < .3: return -0.12 * math.sin(PI * k / .3)
    return 1 - (1 - (k - .3) / .7) ** 3
def ramp(t, t0, t1): return clamp((t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)
def pulse(t, t0, up=.15, hold=.0, down=.4):
    """0 -> 1 -> 0: sobe em `up`, segura `hold`, desce em `down`."""
    if t < t0: return 0.0
    d = t - t0
    if d < up: return d / up
    if d < up + hold: return 1.0
    return clamp(1 - (d - up - hold) / down)
