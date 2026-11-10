"""Terra em corte (v4), em km, para usar com hh.cam.Cam: camadas do modelo PREM, texturas com nível de
detalhe (aparecem quando a câmera chega perto) e a física da queda por um túnel que passa pelo centro.

Mundo: origem no centro da Terra; y cresce para baixo na tela (entrada do túnel em y = -R, saída em y = +R).

Física (PREM, Dziewonski & Anderson 1981), integrada numericamente na importação:
    FALL.pos(tau)  -> y em km no instante tau (s) depois de soltar em y = -R (movimento periódico)
    FALL.vel(tau)  -> velocidade em km/s (positiva no sentido +y)
    FALL.T_ONE     -> tempo de uma travessia (≈ 38,1 min) ; FALL.V_MAX -> velocidade no centro (≈ 9,92 km/s)
    FALL.g(r)      -> gravidade a r km do centro (m/s²): ≈ 0 no centro, ≈ 10,7 na fronteira do núcleo
"""
import math, random
import numpy as np
import cairocffi as cairo
from hh.core import INK, VOID, RED, BLUE, SOLAR, MUTED, LINE, PI, hx, circle, fill, rrect, clamp, lerp, mix

R = 6371.0
R_OUTER, R_INNER, CRUST = 3480.0, 1221.5, 35.0
C_CRUST, C_MANTLE, C_MANTLE2, C_OUTER, C_OUTER2, C_INNER = hx("3B475A"), hx("5A2412"), hx("7A2E12"), hx("B5400F"), hx("D9591A"), SOLAR

def _rho(r):
    x = r / R
    if r < 1221.5: return 13.0885 - 8.8381 * x * x
    if r < 3480: return 12.5815 - 1.2638 * x - 3.6426 * x * x - 5.5281 * x ** 3
    if r < 5701: return 7.9565 - 6.4761 * x + 5.5283 * x * x - 3.0807 * x ** 3
    if r < 5771: return 5.3197 - 1.4836 * x
    if r < 5971: return 11.2494 - 8.0298 * x
    if r < 6151: return 7.1089 - 3.8045 * x
    if r < 6346.6: return 2.6910 + 0.6924 * x
    if r < 6356: return 2.9
    if r < 6368: return 2.6
    return 1.02

class _Fall:
    def __init__(self, n=6371):
        r = np.linspace(0, R, n + 1); dr = (r[1] - r[0]) * 1e3
        rho = np.array([_rho(x) for x in r]) * 1e3
        m = np.cumsum(4 * np.pi * (r * 1e3) ** 2 * rho * dr)
        self._r = r; self._g = np.where(r > 0, 6.674e-11 * m / np.maximum(r * 1e3, 1) ** 2, 0.0)
        phi = np.cumsum(self._g[::-1] * dr)[::-1]                 # ∫_r^R g dr
        v = np.sqrt(2 * phi)                                      # m/s em cada r
        # tempo desde a superfície até cada r (indo para dentro)
        vm = (v[:-1] + v[1:]) / 2; dt = np.empty(n); dt[:] = dr / np.maximum(vm, 1e-9)
        dt[-1] = math.sqrt(2 * dr / self._g[-1])                  # primeiro passo: parte do repouso
        t_in = np.concatenate([[0], np.cumsum(dt[::-1])])         # t_in[k] = tempo até r = R - k*dr
        self._t = t_in; self._depth_r = r[::-1]; self._v = v[::-1]
        self.T_HALF = float(t_in[-1]); self.T_ONE = 2 * self.T_HALF; self.V_MAX = float(v[0]) / 1e3
    def g(self, r): return float(np.interp(abs(r), self._r, self._g))
    def _half(self, tau):                                         # 0..T_HALF: da borda ao centro
        return float(np.interp(tau, self._t, self._depth_r)), float(np.interp(tau, self._t, self._v)) / 1e3
    def state(self, tau):
        """(y km, v km/s) para qualquer tau >= 0. y = -R no início, +R depois de T_ONE, e volta."""
        T = self.T_ONE; k = int(tau // T); u = tau - k * T
        if u <= self.T_HALF: r, v = self._half(u); y = -r
        else: r, v = self._half(T - u); y = r
        return (y, v) if k % 2 == 0 else (-y, -v)
    def pos(self, tau): return self.state(tau)[0]
    def vel(self, tau): return self.state(tau)[1]

FALL = _Fall()

def _h(*k):
    """Hash determinístico -> Random (texturas estáveis entre frames)."""
    return random.Random(hash(k) & 0xffffffff)

def earth(ctx, cam, t, tunnel_px=0.0, shield=1.0, detail=None, a=1.0, tun_y1=None, rings=1.0):
    """Desenha a Terra em corte sob a câmera. tunnel_px = largura do túnel NA TELA (px); 0 = sem túnel.
    detail: 0..1 força o nível de detalhe das texturas (None = automático pelo zoom).
    tun_y1: até onde o túnel já foi cavado (km; None = atravessa tudo). rings: opacidade dos anéis de referência."""
    z = cam.z; det = detail if detail is not None else clamp((z - .35) / .9)
    vr = cam.view_radius(); y0, y1 = cam.cy - vr, cam.cy + vr; x0, x1 = cam.cx - vr, cam.cx + vr
    cam.apply(ctx)
    circle(ctx, 0, 0, R + cam.px(10) + 60, BLUE, .10 * a)                       # atmosfera chapada
    circle(ctx, 0, 0, R, C_CRUST, a)
    circle(ctx, 0, 0, R - CRUST, C_MANTLE, a)
    # ---- manto: bolhas de convecção (detalhe) e arcos grandes (visão de longe)
    ctx.save(); ctx.new_sub_path(); ctx.arc(0, 0, R - CRUST, 0, 2 * PI); ctx.clip()
    if det > 0:
        cell = 170.0
        for gy in range(int(math.floor(y0 / cell)), int(math.floor(y1 / cell)) + 1):
            for gx in range(int(math.floor(max(x0, -900) / cell)), int(math.floor(min(x1, 900) / cell)) + 1):
                rnd = _h("m", gx, gy)
                for _ in range(2):
                    bx = (gx + rnd.random()) * cell; by = (gy + rnd.random()) * cell; br = rnd.uniform(22, 70)
                    by += 12 * math.sin(t * .6 + rnd.random() * 6)
                    ctx.save(); ctx.translate(bx, by); ctx.scale(1, rnd.uniform(.5, .9)); ctx.new_sub_path(); ctx.arc(0, 0, br, 0, 2 * PI); ctx.restore()
                    dark = rnd.random() < .3; fill(ctx, VOID if dark else C_MANTLE2, (.16 if dark else .55) * det * a)
    far = 1 - det
    if far > 0:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for k in range(7):
            rr = R_OUTER + (R - CRUST - R_OUTER) * (.14 + k * .125); a0 = t * (.10 + .02 * k) * (1 if k % 2 else -1) + k * 2.1
            ctx.set_line_width(cam.px(7)); ctx.new_sub_path(); ctx.arc(0, 0, rr, a0, a0 + .9 + .2 * (k % 3))
            ctx.set_source_rgba(*RED, .32 * far * a); ctx.stroke()
    ctx.restore()
    # ---- núcleo externo (líquido): faixas onduladas
    circle(ctx, 0, 0, R_OUTER, C_OUTER, a)
    ctx.save(); ctx.new_sub_path(); ctx.arc(0, 0, R_OUTER, 0, 2 * PI); ctx.clip()
    if det > 0:
        step = 130.0
        for gy in range(int(math.floor(max(y0, -R_OUTER) / step)), int(math.floor(min(y1, R_OUTER) / step)) + 1):
            rnd = _h("o", gy); yy = gy * step; amp = rnd.uniform(14, 34); wl = rnd.uniform(260, 420); ph = rnd.random() * 6 + t * rnd.uniform(.8, 1.6) * (1 if gy % 2 else -1)
            th = rnd.uniform(16, 38); xa, xb = max(x0, -1000), min(x1, 1000)
            ctx.new_path(); n = 36
            for i in range(n + 1):
                xx = xa + (xb - xa) * i / n; (ctx.move_to if i == 0 else ctx.line_to)(xx, yy + amp * math.sin(xx / wl * 2 * PI + ph))
            for i in range(n, -1, -1):
                xx = xa + (xb - xa) * i / n; ctx.line_to(xx, yy + th + amp * math.sin(xx / wl * 2 * PI + ph + .5))
            ctx.close_path(); fill(ctx, C_OUTER2, .55 * det * a)
    if far > 0:
        for k in range(4):
            rr = R_INNER + (R_OUTER - R_INNER) * (.2 + k * .22); a0 = -t * (.2 + .05 * k) + k * 1.7
            ctx.set_line_width(cam.px(6)); ctx.new_sub_path(); ctx.arc(0, 0, rr, a0, a0 + 1.3); ctx.set_source_rgba(*C_OUTER2, .7 * far * a); ctx.stroke()
    ctx.restore()
    # ---- núcleo interno (sólido): facetas
    circle(ctx, 0, 0, R_INNER, C_INNER, a)
    if det > 0:
        ctx.save(); ctx.new_sub_path(); ctx.arc(0, 0, R_INNER, 0, 2 * PI); ctx.clip(); cell = 210.0
        for gy in range(int(math.floor(max(y0, -R_INNER) / cell)), int(math.floor(min(y1, R_INNER) / cell)) + 1):
            for gx in range(int(math.floor(max(x0, -900) / cell)), int(math.floor(min(x1, 900) / cell)) + 1):
                rnd = _h("i", gx, gy); px_, py_ = (gx + rnd.random()) * cell, (gy + rnd.random()) * cell; rr = rnd.uniform(50, 120); a0 = rnd.random() * 6
                ctx.new_path()
                for j in range(3): ctx.line_to(px_ + rr * math.cos(a0 + j * 2.1), py_ + rr * math.sin(a0 + j * 2.1))
                ctx.close_path(); fill(ctx, INK if rnd.random() < .5 else C_OUTER2, (.30 if rnd.random() < .5 else .22) * det * a)
        ctx.restore()
    # ---- túnel (largura constante na tela)
    if tunnel_px > 0:
        w = cam.px(tunnel_px)
        ye = R + cam.px(4) if tun_y1 is None else min(tun_y1, R + cam.px(4))
        ctx.rectangle(-w / 2, -R - cam.px(4), w, ye + R + cam.px(4)); fill(ctx, VOID, a)
        lw = cam.px(max(3.0, tunnel_px * .045))
        for sx in (-1, 1):                                                      # blindagem blueshift
            ctx.rectangle(sx * w / 2 - lw / 2, -R, lw, min(ye, R) + R); fill(ctx, mix(MUTED, BLUE, shield), a)
        if det > 0 and rings > 0:                                                             # anéis de referência: dão a sensação de velocidade
            step = 120.0
            for gy in range(int(math.floor(max(y0, -R) / step)), int(math.floor(min(y1, R) / step)) + 1):
                yy = gy * step
                for sx in (-1, 1):
                    ctx.rectangle(sx * w / 2 - (cam.px(26) if sx > 0 else 0), yy, cam.px(26), cam.px(7)); fill(ctx, BLUE, .75 * det * rings * a)
    cam.restore(ctx)

def layer_at(y):
    r = abs(y)
    if r > R - CRUST: return "crosta"
    if r > R_OUTER: return "manto"
    if r > R_INNER: return "núcleo externo"
    return "núcleo interno"
