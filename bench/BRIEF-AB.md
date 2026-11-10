# Teste A/B de animação — Hipótese #03 (túnel pela Terra)

**Objetivo:** ver se outro modelo melhora a qualidade da ANIMAÇÃO, com tudo o mais igual.

**Regras do teste**
- Trabalhe só em `videos/03b-tunel-terra-fable/`. Ela é uma cópia da #03 com a mesma narração, o mesmo `timing.json` e o mesmo `meta.json`. Não gere narração e não gaste créditos.
- Reescreva **apenas o `scenes.py`** e, se precisar, adicione peças novas em `hh/` (sem quebrar os vídeos 01–03).
- Mantenha o roteiro, os tempos (`S(i)`/`E(i)`), a marca (`brand/BRAND.md`), as cores, o texto mínimo de 36 px e a faixa da legenda livre.
- O vídeo tem de passar no `python3 -m hh.render videos/03b-tunel-terra-fable qa` sem avisos.

**O que melhorar, com liberdade total:**
- fluidez e física dos movimentos (antecipação, follow-through, arcos, peso);
- composição e leitura de cada cena;
- câmera;
- transições entre ideias;
- riqueza de detalhes e cenário;
- personagem mais expressivo;
- sincronia entre a ação e a narração;
- abertura mais forte nos primeiros 2 s.

**Entrega**
1. `python3 -m hh.render videos/03b-tunel-terra-fable video`
2. `bash bench/ab_compare.sh` gera o lado a lado em `bench/ab_03.mp4`.
3. Uma lista curta do que mudou e por quê.
