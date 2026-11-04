"""Som da v2, todo sintetizado (sem créditos e sem direitos autorais).
- trilha: pad sci-fi em lá menor com pulso suave, que abaixa sozinho quando a narração fala
- efeitos: whoosh, impact, boom, rumble, riser, tick, pop, wind, glitch
mix(narr_path, total, cues, out_wav, offset): cues = [(tempo_s, nome, ganho)]
"""
import subprocess, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)

def _t(d): return np.arange(int(d * SR)) / SR
def _env(n, a, r):                       # ataque/release lineares em s
    e = np.ones(n); na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e
def _lp(x, k):                           # passa-baixa de um polo (k pode ser vetor 0..1)
    if np.isscalar(k):
        from scipy.signal import lfilter
        return lfilter([k], [1, k - 1], x)
    y = np.empty_like(x); acc = 0.0; k = np.broadcast_to(k, x.shape)
    for i in range(len(x)): acc += k[i] * (x[i] - acc); y[i] = acc
    return y
def _norm(x, g=1.0): m = np.max(np.abs(x)) or 1; return x / m * g

def whoosh(d=.45):
    n = int(d * SR); k = np.concatenate([np.linspace(.02, .35, n // 2), np.linspace(.35, .02, n - n // 2)])
    return _norm(_lp(rng.standard_normal(n), k) * np.hanning(n), .8)
def wind(d=3.0):
    n = int(d * SR); k = .04 + .03 * np.sin(_t(d) * 2 * np.pi * .7)
    return _norm(_lp(rng.standard_normal(n), k) * _env(n, .6, .8), .6)
def impact(d=.9):
    t = _t(d); f = 40 + 110 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6)
    hit = _lp(rng.standard_normal(len(t)), .25) * np.exp(-t * 35)
    return _norm(body + .5 * hit, .95)
def boom(d=2.2):
    t = _t(d); f = 30 + 60 * np.exp(-t * 6)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    rum = _lp(rng.standard_normal(len(t)), .03) * np.exp(-t * 1.5)
    return _norm(body + 1.2 * rum, 1.0)
def rumble(d=2.0):
    n = int(d * SR); return _norm(_lp(rng.standard_normal(n), .012) * _env(n, .3, .8), .9)
def riser(d=1.2):
    t = _t(d); f = 200 + 900 * (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .25
    noise = _lp(rng.standard_normal(len(t)), np.linspace(.02, .4, len(t))) * .6
    return _norm((tone + noise) * (t / d) ** 1.5 * _env(len(t), 0, .03), .7)
def tick(d=.06):
    t = _t(d); return _norm(np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 90), .5)
def pop(d=.18):
    t = _t(d); f = 500 + 500 * (t / d)
    return _norm(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25), .6)
def glitch(d=.5):
    n = int(d * SR); x = rng.standard_normal(n)
    gate = (np.floor(_t(d) * 40) % 3 == 0).astype(float)
    x = np.round(x * 4) / 4 * gate
    return _norm(_lp(x, .5), .5)

SFX = {"whoosh": whoosh, "wind": wind, "impact": impact, "boom": boom, "rumble": rumble,
       "riser": riser, "tick": tick, "pop": pop, "glitch": glitch}

def music(total):
    """Pad em lá menor (A1 E2 A2 C3 E3) com leve desafinação, LFO lento e pulso de 80 bpm."""
    t = _t(total); x = np.zeros_like(t)
    for f, g in [(55, .5), (82.41, .35), (110, .35), (130.81, .25), (164.81, .18)]:
        for det in (-.25, .25):
            x += g * np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    x *= .75 + .25 * np.sin(2 * np.pi * t / 9)
    beat = 60 / 80; ph = (t % beat) / beat
    x += .35 * np.sin(2 * np.pi * 55 * t) * np.exp(-ph * 9)               # pulso grave
    x = _lp(x, .08)
    n = len(x); fade = _env(n, 1.5, 2.0)
    return _norm(x * fade, 1.0)

def _read(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64) / 32768

def mix(narr_path, total, cues, out_wav, offset=0.0, music_gain=.16, duck_to=.07):
    n = int(total * SR); out = np.zeros(n)
    narr = np.zeros(n)
    if narr_path:
        v = _read(narr_path); s = int(offset * SR); m = min(len(v), n - s); narr[s:s + m] = v[:m]
    # envelope da fala -> ducking da trilha
    win = int(.05 * SR); en = np.sqrt(np.convolve(narr ** 2, np.ones(win) / win, "same"))
    speech = (en > .02).astype(float)
    k = 1 - np.exp(-1 / (.25 * SR)); g = np.empty(n); acc = 0.0
    for i in range(0, n, 64):                                   # suavização em blocos (rápido)
        acc += (speech[i] - acc) * (1 - (1 - k) ** 64); g[i:i + 64] = acc
    out += music(total) * (music_gain - (music_gain - duck_to) * g)
    for tt, name, gain in cues:
        s = SFX[name](); i = int(tt * SR)
        if i >= n: continue
        m = min(len(s), n - i); out[i:i + m] += s[:m] * gain * .5
    out += narr
    peak = np.max(np.abs(out)) or 1
    if peak > .98: out *= .98 / peak
    with wave.open(out_wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    return out_wav
