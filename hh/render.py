"""Renderiza um vídeo do HyperHypothesis.
Uso:
  python3 -m hh.render videos/<pasta> frames t1 t2 ...   -> PNGs de conferência em <pasta>/out/
  python3 -m hh.render videos/<pasta> video              -> <pasta>/out/video.mp4 (com narr.mp3 se existir)
"""
import os, sys, importlib.util, subprocess
VDIR = os.path.abspath(sys.argv[1]); os.environ["HH_VIDEO"] = VDIR
from hh.core import *  # noqa: E402

spec = importlib.util.spec_from_file_location("scenes", os.path.join(VDIR, "scenes.py"))
SC = importlib.util.module_from_spec(spec); spec.loader.exec_module(SC)
SCENES = SC.SCENES
LAST = len(SEG) - 1

def frame(ctx, t):
    for idx, (a, b, fn) in enumerate(SCENES):
        st = 0 if idx == 0 else S(a)
        en = TOTAL + 1 if idx == len(SCENES) - 1 else S(SCENES[idx + 1][0])
        if st <= t < en:
            ctx.push_group(); fn(ctx, t); ctx.pop_group_to_source()
            ctx.paint_with_alpha(clamp((t - st) / 0.18) if idx else 1.0)
            fo = clamp((t - (en - 0.12)) / 0.12) if idx < len(SCENES) - 1 else clamp((t - (TOTAL - .6)) / .6)
            if fo > 0: ctx.set_source_rgba(*VOID, fo); ctx.paint()
            break
    if t < E(LAST): hud(ctx, t)
    captions(ctx, t)

def surface_at(t):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); ctx = cairo.Context(surf)
    ctx.set_antialias(cairo.ANTIALIAS_BEST); frame(ctx, t); return surf

if __name__ == "__main__":
    mode = sys.argv[2]
    if mode == "frames":
        for ts in sys.argv[3:]:
            surface_at(float(ts)).write_to_png(os.path.join(OUT, f"f_{float(ts):05.1f}.png"))
        print("total", round(TOTAL, 2))
    else:
        audio = os.path.join(VDIR, "narr.mp3")
        outp = os.path.join(OUT, "video.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        if os.path.exists(audio):
            cmd += ["-i", audio, "-filter_complex", "[1:a]adelay=%d|%d,apad[a]" % (OFF * 1000, OFF * 1000),
                    "-map", "0:v", "-map", "[a]", "-shortest", "-c:a", "aac", "-b:a", "192k"]
        cmd += ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", outp]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = int(TOTAL * FPS)
        for i in range(n):
            p.stdin.write(bytes(surface_at(i / FPS).get_data()))
            if i % 300 == 0: print(f"{i}/{n}", flush=True)
        p.stdin.close(); p.wait(); print("ok", outp, round(TOTAL, 2))
