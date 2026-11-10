# HyperHypothesis: fábrica de vídeos

Canal de animações curtas "E se...?" (TikTok @hyperhypothesis, YouTube Shorts @hyperhypothesis e Instagram Reels @hyper.hypothesis). Formato 1080×1920 a 30 fps, motion graphics 2D feito por código, narração do ElevenLabs.

O dono é o Gustavo. Tudo que vai para ele, inclusive mensagens e legendas, é escrito em **português do Brasil**.

## Estrutura

- `brand/`: identidade da marca. `BRAND.md` traz a personalidade, a voz, o estilo de animação e as regras de texto na tela; `tokens.json` traz as cores e a tipografia; também há as fontes e os logos. **Leia o `BRAND.md` antes de escrever qualquer roteiro.**
- `hh/core.py`: cores, fontes, texto em curvas, personagem `person` (braços, piscar, `mood`: wow/happy/scared), nave `ship`, `mark` (logo), fundo com parallax, HUD, legenda karaokê, `S(i)`/`E(i)` (início e fim da frase i), easings.
- `hh/fx.py`: peças da v2. **Use nas cenas com `from hh.fx import *`.**
  - `icon(ctx, nome, x, y, tamanho, cor, style="fill"|"duotone")`: 1.512 ícones Phosphor (MIT) em `brand/icons/`, sempre nas cores da marca;
  - `globe(...)`, `globe_line`, `globe_band`, `geo(lon, lat, ...)`: Terra com continentes reais (Natural Earth);
  - cenário: `building`, `skyline`, `tree`, `cloud`, `wave`;
  - efeitos: `arrow`, `trails`, `burst`, `debris`, `glitch_text`;
  - `counter()`: números no formato brasileiro.
- `hh/anim.py`: animação da v3. **Use nas cenas com `from hh.anim import *`**, que já traz `fx` e `core`.
  - `spring()`: mola com leve overshoot, para tudo que entra na tela;
  - `wobble()`: movimento secundário (balanço, flutuação, olhar);
  - partículas: `smoke`, `sparks`, `dust`, `trail_dust`, `spray`, `shockwave`, `speedlines`;
  - `pop_text` / `pop_text_fit`: título que entra letra a letra.
- **Motor v4** (nasceu no teste A/B da #03; o modelo de referência é `videos/03b-tunel-terra-fable/scenes.py`). Tudo é opcional e convive com a v3:
  - `hh/cam.py`: câmera virtual `Cam(cx, cy, z, rot, fx, fy)`. Desenhe o mundo em unidades próprias (km, m) entre `cam.apply(ctx)` e `cam.restore(ctx)`; `cam.pt(x, y)` converte mundo → tela. Serve para **plano-sequência**: seguir o personagem, afastar até o planeta inteiro, girar, sem corte. Na cena, ponha `ZOOM = 0.0` para desligar o push-in automático. Também traz `ramp`, `pulse`, `smooth`, `smoother`, `anticipate`, `lerp_log` (zoom).
  - `hh/hero.py`: personagem com cotovelos e joelhos, `POSES` (stand, crouch, leap, fall, dive, float, brake, reach, panic, dig), `mixpose(a, b, k)` para passar de uma pose a outra, `flutter()` para tremular na queda, cachecol redshift que voa contra a velocidade (`vel`), e moods extras (`effort`, `dizzy`, `calm`). Prefira `hero` a `person` em vídeos novos.
  - `hh/planet.py`: Terra em corte com as camadas reais (PREM), `earth(ctx, cam, t, ...)` com textura por nível de zoom, e `FALL`, a queda pelo túnel já integrada (posição, velocidade, tempo). Use a simulação para mover as coisas, em vez de inventar a curva: o número do HUD e o movimento saem da mesma conta.
  - **Sincronia por palavra:** depois de gerar a narração, transcreva o `narr.mp3` com `creative_transcribe_audio` (0 créditos), salve as palavras em `words_raw.json`, o roteiro em `roteiro.txt` (uma frase por linha) e rode `python3 -m hh.words videos/<pasta> [tempo]`. Isso gera o `timing.json` com o tempo de cada palavra (substitui o `hh.align`). Nas cenas, `WT(i, "palavra")` devolve o instante em que a palavra é dita: **todo evento visual e todo `CUE` deve cair na palavra certa**, não em `S(i) + chute`. A legenda karaokê passa a acender no tempo exato.
  - Se a narração passar de ~47 s, acelere com `ffmpeg -filter:a atempo=1.05` (até 1,06 não se nota) e passe o mesmo valor ao `hh.words`.
- Personagem `person(...)`: tem pernas, `run=t*3` (ciclo de corrida), `rot` (tombo), `squash` (achatar/esticar), `arms`, `mood` e `look`. Ele nunca fica parado: use sempre `wobble` nos braços e no olhar.
- `hh/audio.py`: trilha ambiente bem baixa, que abaixa mais com a fala, e efeitos em níveis fixos abaixo da narração (`LEVEL`).
  - gravados (Kenney, CC0): `impact`, `crash`, `boom`, `metal`, `glass`, `rumble`, `thruster`, `glitch`, `force`, `tick`;
  - sintetizados: `whoosh`, `wind`, `riser`, `pop`.
- `hh/themes.py`: temas sazonais. Com `"tema": "natal"` no `meta.json`, o vídeo ganha sozinho gorro de Papai Noel no personagem, neve caindo, neve nas árvores e telhados, e pisca-pisca. Para testar sem mudar o vídeo, use `HH_THEME=natal`. `themes.tema_da_data(mes, dia)` diz qual tema vale numa data.
- `brand/CREDITS.md`: licenças de tudo que veio de fora. Só use material livre para uso comercial e registre-o lá.
- `hh/render.py`: renderiza um vídeo. `python3 -m hh.render videos/<pasta> frames 10 20` gera frames de conferência; `... video` gera `out/video.mp4` (motion blur de 4 subquadros, ~4–5 min por vídeo); `... audio` refaz só o som de um vídeo já renderizado.
- `hh/align.py`: `python3 -m hh.align videos/<pasta>` alinha as frases do `timing.json` com o `narr.mp3` pelas pausas da fala.
- `videos/NN-slug/`: um vídeo por pasta, com estes arquivos:
  - `meta.json`: número, título, palavras destacadas na legenda e segmentos sem legenda;
  - `timing.json`: as frases do roteiro;
  - `narr.mp3`: a narração;
  - `scenes.py`: as cenas. A lista `SCENES` contém tuplas `(seg_inicial, seg_final, função)`. Também traz `CUES` (efeitos sonoros: `(lambda: S(6), "impact", 1.0)`) e `SHAKES` (tremor de câmera: `(lambda: S(8)+1.2, 18, .5)`). O vídeo 03 é o modelo de referência.
  - Automático em todo vídeo: push-in de câmera em cada cena, transição em cortina (feixe redshift) com whoosh, trilha ambiente que abaixa quando a narração fala, legenda karaokê e loudness em −14 LUFS.
- O calendário e o status de cada vídeo ficam no doc "HyperHypothesis — Planejamento de vídeos" (Claude Docs): https://claude.ai/artifact/VuhJp9Xwm7pHCVLa2nB7Yy

## Preparar o ambiente (sessão nova)

```
pip install --break-system-packages -q -r requirements.txt   # o ffmpeg já vem instalado
curl -sS -o /dev/null -w '%{http_code}' https://api.elevenlabs.io/v1/models   # precisa responder (≠ 000/403)
```

Se o ElevenLabs estiver bloqueado (000/403), **não gere narração**, porque o áudio não teria como ser baixado e os créditos seriam perdidos. Escreva só os roteiros, salve-os no repositório e avise o Gustavo do bloqueio.

## Regras fixas

- **Abertura (lição da #01: a maioria saía em 0:01):**
  - ação já no frame 0, com personagem ou objeto em movimento;
  - narração começando no segundo zero (`lead_in` 0, que é o padrão);
  - pergunta na tela em no máximo 2 linhas curtas;
  - nada de paredão de texto parado.
- **Roteiro (lições do teste A/B):**
  - o gancho coloca "você" numa ação ("...e pulasse?"), não num fato;
  - frases curtas, uma ideia por frase, e cada frase tem de pedir uma imagem;
  - um número-herói só, com frase própria ("38 minutos."), e no máximo 3 ou 4 números no vídeo;
  - uma virada perto do fim (uma consequência engraçada ou um perigo) antes da pergunta;
  - a pergunta final se responde com uma palavra ("Pra onde você cavaria?"), o que facilita comentar;
  - tags de emoção do ElevenLabs também gastam créditos: use poucas.
- **Duração de 35 a 50 s.** Roteiro com ~650–750 caracteres, que custa uns 690 créditos.
- **Final:** a última frase falada é "Segue pra próxima hipótese." A cena final usa `end_card(ctx, t, S(i), question=[...], next_title="E se ...?")`, com o botão + SEGUIR e o próximo tema do calendário. Não peça para seguir no meio do vídeo.

- **Som:** trilha e efeitos sempre abaixo da narração. Não aumente `music_gain` nem os níveis de `LEVEL`; o Gustavo achou alto na v2. Para mudar volume, use o ganho do `CUE` (0,3–1,0).
- **Texto mínimo de 36 px** na tela, fora o HUD e a legenda. O `qa` acusa o que estiver abaixo disso.
- Cores: só os tokens da marca (`brand/tokens.json`), mais o verde das árvores e campos (`#2E6B5E`) e o oceano e os continentes do globo (`fx.OCEAN_COL`, `fx.LAND_COL`).

- A narração começa **direto em "E se...?"**. O número da hipótese aparece só escrito (HUD e capa), nunca falado.
- A física tem que estar certa: confira cada número antes de narrar. Quando der, **calcule** (integração numérica, como em `hh/planet.py`) em vez de citar número de cabeça, e deixe contas e fontes no comentário do topo do `scenes.py`. Quando uma comparação não puder ser verificada, troque por uma que possa (ex.: bombas de Hiroshima, ~15 kt).
- **Narração:** voz Will (Deep Smooth and Affectionate), modelo `eleven_v4`, **uma versão só** (`generations_count: 1`). Roteiro de ~650–750 caracteres, cerca de 690 créditos. O plano tem 30 mil créditos por mês.
- Todo post vai com o rótulo de conteúdo de IA ligado (TikTok `isAigc`, YouTube `isAiGeneratedContent`, Instagram `isAiGenerated`).
- **Metricool:** marca HyperHypothesis (blogId 7873537), fuso America/Sao_Paulo. Nunca publique na marca saopaulohidro.

## Rotina semanal (tarefa agendada)

1. Leia o calendário no doc e pegue os próximos 4 vídeos ainda em status "Ideia".
2. Para cada um: escreva o roteiro seguindo o `BRAND.md`, crie a pasta `videos/NN-slug/` com `meta.json` e `timing.json`.
   - **Tema:** se `themes.tema_da_data()` da data de publicação devolver um tema, coloque `"tema"` no `meta.json`.
   - **Episódios temáticos:** confira também a seção da temporada no doc (ex.: "Temporada de Natal"). Os episódios de lá entram nas datas indicadas, junto com os do calendário principal.
   - Depois disso, siga no mesmo item: gere a narração (uma versão) e salve como `narr.mp3`.
3. Rode `python3 -m hh.align` e escreva o `scenes.py`, reaproveitando as peças do `fx` e partindo do **vídeo 03** como modelo (abertura, duração e tela final no padrão atual).
   - **Menos cortes:** quando a história é um trajeto (queda, viagem, zoom de escala), faça um plano-sequência com `hh/cam.py` e deixe a transição em cortina só para mudar de assunto. Use câmera lenta e plano aberto no momento-chave.
   - O `qa` só olha 1 frame a cada 2 s: confira também frames nos instantes de transição de câmera (`frames t1 t2 ...`), onde placas e rótulos mudam de tamanho.
   - **Cada cena precisa de ação**: um personagem ou objeto fazendo algo, com antecipação, impacto e reação (partículas, tremor, som). Títulos entram com `pop_text`, e números contam ou entram com `spring`.
   - **Cada cena precisa de cenário**, nada de forma solta no vazio: ícones, prédios, árvores, globo, partículas. Também precisa de movimento contínuo, um evento visual com som (`CUES`) e tremor nos impactos (`SHAKES`).
   - Rode `python3 -m hh.render videos/<pasta> qa` e **olhe a folha `out/qa_sheet.png`**. Corrija tudo que o relatório apontar: texto menor que 36 px, texto embaixo da legenda (faixa y 1370–1530) e tela vazia. Rode de novo até não sobrar nenhum aviso.
   - Renderize o vídeo e confira alguns frames do MP4 final.
4. Faça commit e push. O MP4 vai para `videos/NN-slug/out/video.mp4`, publicado com `git add -f` para o Metricool conseguir baixar por `https://raw.githubusercontent.com/guamador/hyperhypothesis/main/...`.
5. Agende no Metricool como **rascunho** (`draft: true`), na data e hora do calendário, com 3 posts separados:
   - TikTok: `isAigc` ligado e capa por `videoCoverMilliseconds` no frame do número-herói;
   - YouTube Short: `madeForKids` false, `isAiGeneratedContent` true e categoria `SCIENCE_TECHNOLOGY`;
   - Instagram Reel: `instagramData`: `{type: "REEL", showReelOnFeed: true, isAiGenerated: true}`, com 3 a 5 hashtags.
   Use como media a URL raw **fixada no SHA do commit**: `.../hyperhypothesis/<sha>/videos/...`. Assim o cache do GitHub nunca entrega uma versão antiga.
6. Atualize o status no doc para "Agendado" e mande uma mensagem curta ao Gustavo pedindo a aprovação dos rascunhos.
