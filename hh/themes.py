"""Temas sazonais. Ative no meta.json do vídeo: "tema": "natal" (ou HH_THEME=natal para testar).
O que cada tema faz sozinho, sem mudar as cenas:
  natal: gorro de Papai Noel no personagem (person(..., hat=False) desliga), neve caindo na frente da cena,
         neve nas copas das árvores e nos telhados, pisca-pisca piscando, flocos no fundo.
Períodos sugeridos (a rotina semanal liga o tema sozinha pela data de publicação):
  natal: 01/12 a 26/12
Para criar um tema novo (halloween, carnaval, são joão, réveillon): adicione o nome em PERIODOS,
o efeito de tela em overlay(), e os detalhes nos desenhos (core.person, fx.tree, fx.building) com
`if _core.THEME == "<tema>"`.
"""
import math, random
from hh import core as _c

PERIODOS = {"natal": ((12, 1), (12, 26))}

def tema_da_data(mes, dia):
    for nome, ((m0, d0), (m1, d1)) in PERIODOS.items():
        if (m0, d0) <= (mes, dia) <= (m1, d1): return nome
    return None

_rnd = random.Random(42)
_FLAKES = [(_rnd.uniform(0, _c.W), _rnd.uniform(0, _c.H), _rnd.uniform(1.5, 6.5), _rnd.uniform(0, 6.28)) for _ in range(140)]

def overlay(ctx, t):
    """Efeito de tela do tema, desenhado por cima da cena e por baixo do HUD e da legenda."""
    if _c.THEME == "natal":
        for x, y, r, ph in _FLAKES:                     # flocos maiores caem mais rápido (profundidade)
            yy = (y + t * (40 + r * 22)) % (_c.H + 20) - 10
            xx = (x + math.sin(t * .9 + ph) * (10 + r * 3) + t * 8) % _c.W
            _c.circle(ctx, xx, yy, r, _c.INK, .35 + r * .07)
