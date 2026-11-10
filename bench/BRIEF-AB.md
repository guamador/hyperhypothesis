# Teste A/B completo: Hipótese #03 (túnel pela Terra)

**Objetivo:** ver se outro modelo faz um vídeo **melhor no geral** sobre o mesmo tema: roteiro, narração, animação, som e texto do post. O lado A (`videos/03-tunel-terra/`, feito pelo Opus 5.5) já foi publicado e **não pode ser alterado**.

## Liberdade total em `videos/03b-tunel-terra-fable/`
- **Roteiro:** reescreva do zero se achar melhor (gancho, estrutura, frases, número-herói, final). A física tem de estar certa: confira cada número e deixe as contas e fontes num comentário no topo do `scenes.py`.
- **Narração:** se mudar o roteiro, gere **uma narração nova, uma versão só** (`generations_count: 1`), com a voz Will (Deep, Smooth and Affectionate, id `CstacWqMhJQlnfLPxRG4`, modelo `eleven_v4`). Ela custa ~690 créditos; não gere mais de uma vez. Baixe como `narr.mp3`, corte o silêncio inicial, refaça o `timing.json` e rode `python3 -m hh.align`.
- **Animação:**
  - reescreva o `scenes.py` como quiser;
  - crie peças novas em `hh/`, sem quebrar os vídeos 01–03: fluidez, física dos movimentos, câmera, composição, transições, personagem, cenário, sincronia com a fala, abertura.
- **Som:** ajuste `CUES`/`SHAKES` livremente. Os níveis gerais (`music_gain`, `LEVEL`) não sobem, porque o dono achou alto antes.
- **Post:** proponha título, legenda e hashtags para TikTok, Shorts e Reels em `videos/03b-tunel-terra-fable/post.md`. **Não agende nada.**

## O que não muda (regras da marca e do canal)
- `brand/BRAND.md` (personalidade, voz, cores, fontes) e as regras fixas do `CLAUDE.md`:
  - abertura com ação no frame 0;
  - 35–50 s;
  - final com "Segue pra próxima hipótese" e `end_card`;
  - texto ≥ 36 px;
  - faixa da legenda livre;
  - narração começando em "E se...?".
- O vídeo tem de passar no `python3 -m hh.render videos/03b-tunel-terra-fable qa` sem avisos.

## Entrega
1. `python3 -m hh.render videos/03b-tunel-terra-fable video`
2. `bash bench/ab_compare.sh`, que gera o lado a lado em `bench/ab_03.mp4`. Se as durações forem diferentes, o vídeo acaba no menor.
3. Commit e push de tudo.
4. Uma lista curta do que mudou e por quê, separada em roteiro, animação e som.
