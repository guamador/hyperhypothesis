"""Renderiza um vídeo do HyperHypothesis (motor v2).
Uso:
  python3 -m hh.render videos/<pasta> frames t1 t2 ...   -> PNGs de conferência em <pasta>/out/
  python3 -m hh.render videos/<pasta> qa                 -> folha de conferência + relatório (texto pequeno,
                                                            texto sob a legenda, tela vazia)
  python3 -m hh.render videos/<pasta> video              -> <pasta>/out/video.mp4 (narração + trilha + efeitos)

No scenes.py do vídeo:
  SCENES = [(seg_inicial, seg_final, função), ...]        obrigatório
  CUES   = [(lambda: S(6), "impact", 1.0), ...]           efeitos sonoros (hh/audio.py: SFX)
  SHAKES = [(lambda: S(8) + 1.2, 18, .5), ...]            tremor de câmera: (tempo, amplitude px, duração s)
  ZOOM   = 0.035                                          push-in de câmera por cena (opcional; 0 desliga)
Automático: whoosh + transição em cortina (feixe redshift) entre cenas, trilha ambiente com ducking,
legenda karaokê, aviso de texto menor que MIN_TEXT.
"""
import os, sys, math, importlib.util, subprocess
VDIR = os.path.abspath(sys.argv[1]); os.environ["HH_VIDEO"] = VDIR
from hh import core  # noqa: E402
from hh.core import *  # noqa: E402,F403
from hh import audio  # noqa: E402

spec = importlib.util.spec_from_file_location("scenes", os.path.join(VDIR, "scenes.py"))
SC = importlib.util.module_from_spec(spec); spec.loader.exec_module(SC)
SCENES = SC.SCENES
CUES = [(f() if callable(f) else f, n, g) for f, n, g in getattr(SC, "CUES", [])]
SHAKES = [(f() if callable(f) else f, amp, d) for f, amp, d in getattr(SC, "SHAKES", [])]
ZOOM = getattr(SC, "ZOOM", 0.035)
WIPE = 0.32
LAST = len(SEG) - 1

def bounds(idx):
    a = SCENES[idx][0]
    st = 0 if idx == 0 else S(a)
    en = TOTAL + 1 if idx == len(SCENES) - 1 else S(SCENES[idx + 1][0])
    return st, en

def shake_at(t):
    dx = dy = 0.0
    for t0, amp, d in SHAKES:
        if t0 <= t < t0 + d:
            k = 1 - (t - t0) / d
            dx += amp * k * math.sin(t * 73); dy += amp * k * math.sin(t * 59 + 1)
    return dx, dy

def draw_scene(ctx, idx, t):
    st, en = bounds(idx)
    z = 1 + ZOOM * eio(clamp((t - st) / max(.5, en - st)))
    dx, dy = shake_at(t)
    ctx.save(); ctx.translate(540 + dx, 960 + dy); ctx.scale(z, z); ctx.translate(-540, -960)
    SCENES[idx][2](ctx, t)
    ctx.restore()

def frame(ctx, t):
    core.NOW = t; core.TEXTS.clear()
    idx = next(i for i in range(len(SCENES)) if bounds(i)[0] <= t < bounds(i)[1])
    st, en = bounds(idx)
    if idx > 0 and t < st + WIPE:                       # cortina: feixe redshift da esquerda p/ direita
        p = eio((t - st) / WIPE); xw = p * (W + 120) - 60
        ctx.save(); ctx.rectangle(xw, 0, W, H); ctx.clip(); draw_scene(ctx, idx - 1, t); ctx.restore()
        core.TEXTS.clear()
        ctx.save(); ctx.rectangle(0, 0, max(0, xw), H); ctx.clip(); draw_scene(ctx, idx, t); ctx.restore()
        rrect(ctx, xw - 22, 0, 22, H, 0); fill(ctx, RED)
        for j, (yy, ln) in enumerate([(380, 300), (900, 460), (1500, 340)]):
            rrect(ctx, xw - 22 - ln * (1 - p) - 40, yy, ln * (1 - p), 14, 7); fill(ctx, RED, .8)
        circle(ctx, xw + 26, 960, 16, BLUE)
    else:
        draw_scene(ctx, idx, t)
    if idx == len(SCENES) - 1:
        fo = clamp((t - (TOTAL - .6)) / .6)
        if fo > 0: ctx.set_source_rgba(*VOID, fo); ctx.paint()
    if t < E(LAST): hud(ctx, t)
    captions(ctx, t)

def surface_at(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST); frame(ctx, t); return surf

def lint_report():
    if core.LINT:
        print(f"AVISO: {len(core.LINT)} texto(s) menores que {MIN_TEXT}px:")
        for (txt, sz), t in sorted(core.LINT.items(), key=lambda x: x[1]): print(f"  t={t:6.2f}s  {sz:>3}px  {txt!r}")
    else: print(f"OK: nenhum texto menor que {MIN_TEXT}px")

def qa():
    """Folha de conferência (1 frame a cada 2 s) + checagens automáticas."""
    import numpy as np
    times = [round(x * 2.0 + 1.0, 2) for x in range(int(TOTAL // 2))]
    thumbs = []; issues = []
    capzone = (1370, 1530)
    for tt in times:
        s = surface_at(tt); buf = np.frombuffer(bytes(s.get_data()), np.uint8).reshape(H, W, 4)
        cap_on = any(a <= tt < b for a, b, _ in CAPS)
        for x0, y0, x1, y1, txt in core.TEXTS:
            if cap_on and y1 > capzone[0] and y0 < capzone[1]:
                issues.append(f"t={tt:5.1f}s texto {txt!r} embaixo da legenda")
        lum = buf[200:1350, :, :3].astype(int).sum(axis=2)
        busy = (abs(lum - lum.mean()) > 60).mean()
        if busy < .015: issues.append(f"t={tt:5.1f}s tela quase vazia ({busy:.1%} ocupada)")
        thumbs.append(buf[:, :, [2, 1, 0]][::5, ::5].copy())
    cols = 8; rows = math.ceil(len(thumbs) / cols); th, tw = thumbs[0].shape[:2]
    sheet = np.full((rows * th, cols * tw, 3), 40, np.uint8)
    for i, im in enumerate(thumbs): r, c = divmod(i, cols); sheet[r*th:(r+1)*th, c*tw:(c+1)*tw] = im
    out = os.path.join(OUT, "qa_sheet.ppm")
    with open(out, "wb") as f: f.write(f"P6 {sheet.shape[1]} {sheet.shape[0]} 255\n".encode()); f.write(sheet.tobytes())
    png = out.replace(".ppm", ".png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", out, png]); os.remove(out)
    print("folha:", png, f"({len(times)} frames, 1 a cada 2 s, começando em 1 s)")
    lint_report()
    print(f"{len(issues)} problema(s) de layout:" if issues else "OK: layout sem sobreposição com a legenda nem tela vazia")
    for i in issues: print("  " + i)

if __name__ == "__main__":
    mode = sys.argv[2]
    if mode == "frames":
        for ts in sys.argv[3:]:
            surface_at(float(ts)).write_to_png(os.path.join(OUT, f"f_{float(ts):05.1f}.png"))
        print("total", round(TOTAL, 2)); lint_report()
    elif mode == "qa":
        qa()
    else:
        narr = os.path.join(VDIR, "narr.mp3")
        cues = list(CUES) + [(bounds(i)[0] - .12, "whoosh", .7) for i in range(1, len(SCENES))]
        wav = os.path.join(OUT, "mix.wav")
        audio.mix(narr if os.path.exists(narr) else None, TOTAL, cues, wav, offset=OFF)
        outp = os.path.join(OUT, "video.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-i", wav, "-map", "0:v", "-map", "1:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",
               "-c:a", "aac", "-b:a", "192k", "-shortest",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(TOTAL * FPS)
        for i in range(n):
            p.stdin.write(bytes(surface_at(i / FPS).get_data()))
            if i % 300 == 0: print(f"{i}/{n}", flush=True)
        p.stdin.close(); p.wait(); os.remove(wav)
        print("ok", outp, round(TOTAL, 2)); lint_report()
