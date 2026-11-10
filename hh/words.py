"""Monta o timing.json a partir da transcrição com tempo por palavra (ElevenLabs Scribe, grátis no conector).
Uso: python3 -m hh.words videos/<pasta> [tempo]
  Lê <pasta>/words_raw.json (lista de {text, start, end}) e <pasta>/roteiro.txt (uma frase por linha).
  `tempo` (ex.: 1.05) = aceleração aplicada ao narr.mp3 com ffmpeg atempo; os tempos são divididos por ele.
Escreve start/end e "words" ([texto, início, fim]) em cada segmento: a legenda acende cada palavra na hora
exata e as cenas podem usar WT(i, "palavra") para sincronizar ações com a fala.
"""
import json, os, re, sys, unicodedata

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)

if __name__ == "__main__":
    d = sys.argv[1]; tempo = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    raw = json.load(open(os.path.join(d, "words_raw.json")))
    raw = raw["words"] if isinstance(raw, dict) else raw
    ws = [w for w in raw if w.get("type", "word") == "word" and not re.match(r"^\[.*|.*\]$", w["text"]) and norm(w["text"])]
    lines = [l.strip() for l in open(os.path.join(d, "roteiro.txt")) if l.strip()]
    segs = []; i = 0
    for line in lines:
        toks = line.split(); out = []
        for tk in toks:
            if not norm(tk): continue
            assert i < len(ws), f"faltou palavra na transcrição para {tk!r}"
            if norm(ws[i]["text"]) != norm(tk): print(f"aviso: roteiro {tk!r} x transcrição {ws[i]['text']!r}")
            out.append([tk, round(ws[i]["start"] / tempo, 3), round(ws[i]["end"] / tempo, 3)]); i += 1
        segs.append({"t": line, "d": round(out[-1][2] - out[0][1], 3), "start": out[0][1], "end": out[-1][2],
                     "chunks": [[out[0][1], out[-1][2]]], "words": out})
    assert i == len(ws), f"sobraram {len(ws) - i} palavras na transcrição"
    T = {"lead_in": 0, "segments": segs, "tail": 2.4}
    json.dump(T, open(os.path.join(d, "timing.json"), "w"), ensure_ascii=False, indent=1)
    for k, s in enumerate(segs): print(k, s["start"], s["end"], s["t"])
