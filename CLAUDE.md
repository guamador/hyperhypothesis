# HyperHypothesis: fábrica de vídeos

Canal de animações curtas "E se...?" (TikTok @hyperhypothesis, YouTube Shorts e Instagram Reels). Formato 1080×1920 a 30 fps, motion graphics 2D feito por código, narração do ElevenLabs.

O dono é o Gustavo. Tudo que vai para ele, inclusive mensagens e legendas, é escrito em **português do Brasil**.

## Estrutura

- `brand/`: identidade da marca. `BRAND.md` traz a personalidade, a voz, o estilo de animação e as regras de texto na tela; `tokens.json` traz as cores e a tipografia; também há as fontes e os logos. **Leia o `BRAND.md` antes de escrever qualquer roteiro.**
- `hh/core.py`: cores, fontes, texto em curvas, personagem `person`, nave `ship`, `mark` (logo), fundo, HUD, legendas, `S(i)`/`E(i)` (início e fim da frase i), easings.
- `hh/render.py`: renderiza um vídeo. `python3 -m hh.render videos/<pasta> frames 10 20` gera frames de conferência; `... video` gera `out/video.mp4`.
- `hh/align.py`: `python3 -m hh.align videos/<pasta>` alinha as frases do `timing.json` com o `narr.mp3` pelas pausas da fala.
- `videos/NN-slug/`: um vídeo por pasta, com estes arquivos:
  - `meta.json`: número, título, palavras destacadas na legenda e segmentos sem legenda;
  - `timing.json`: as frases do roteiro;
  - `narr.mp3`: a narração;
  - `scenes.py`: as cenas. A lista `SCENES` contém tuplas `(seg_inicial, seg_final, função)`.
- O calendário e o status de cada vídeo ficam no doc "HyperHypothesis — Planejamento de vídeos" (Claude Docs): https://claude.ai/artifact/VuhJp9Xwm7pHCVLa2nB7Yy

## Regras fixas

- A narração começa **direto em "E se...?"**. O número da hipótese aparece só escrito (HUD e capa), nunca falado.
- A física tem que estar certa: confira cada número antes de narrar. Quando uma comparação não puder ser verificada, troque por uma que possa (ex.: bombas de Hiroshima, ~15 kt).
- **Narração:** voz Will (Deep Smooth and Affectionate), modelo `eleven_v4`, **uma versão só** (`generations_count: 1`). Roteiro de no máximo ~1.100 caracteres, cerca de 1.190 créditos. O plano tem 30 mil créditos por mês.
- Todo post vai com o rótulo de conteúdo de IA ligado (TikTok `isAigc`, YouTube `isAiGeneratedContent`, Instagram `isAiGenerated`).
- **Metricool:** marca HyperHypothesis (blogId 7873537), fuso America/Sao_Paulo. Nunca publique na marca saopaulohidro.

## Rotina semanal (tarefa agendada)

1. Leia o calendário no doc e pegue os próximos 4 vídeos ainda em status "Ideia".
2. Para cada um: escreva o roteiro seguindo o `BRAND.md`, crie a pasta `videos/NN-slug/` com `meta.json` e `timing.json`, gere a narração (uma versão) e salve como `narr.mp3`.
3. Rode `python3 -m hh.align` e escreva o `scenes.py`, reaproveitando as peças do `core` e copiando ideias dos vídeos anteriores. Confira os frames, renderize e confira de novo.
4. Faça commit e push. O MP4 vai para `videos/NN-slug/out/video.mp4`, publicado com `git add -f` para o Metricool conseguir baixar por `https://raw.githubusercontent.com/guamador/hyperhypothesis/main/...`.
5. Agende no Metricool como **rascunho** (`draft: true`), na data e hora do calendário: TikTok + YouTube Short (+ Instagram Reel, se estiver conectado).
6. Atualize o status no doc para "Agendado" e mande uma mensagem curta ao Gustavo pedindo a aprovação dos rascunhos.
