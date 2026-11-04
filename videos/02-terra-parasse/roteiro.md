# Hipótese #02: E se a Terra parasse de girar por 1 segundo?

Status: **roteiro pronto, narração NÃO gerada** (o ElevenLabs estava bloqueado na execução automática de 04/11/2026).

- Voz: Will - Deep Smooth and Affectionate · modelo `eleven_v4` · `generations_count: 1`
- Número-herói: **1.670 km/h** no equador
- O número da hipótese não é falado (aparece só no HUD e na capa)

## Narração (texto para o ElevenLabs)

```
[curious] E se a Terra parasse de girar... por um segundo só?
Parece pouco. Você nem sente o planeta girar.
Mas ele gira. E você gira junto.
[pause] Agora, o chão para. Você não.
A gravidade te puxa pra baixo. Não pro lado.
Então você continua indo para o leste...
[dramatic] a 1.670 quilômetros por hora. No equador.
Quase o dobro da velocidade de um avião.
Em um segundo, você anda quase meio quilômetro. Até bater em alguma coisa.
O ar vai junto: um vento supersônico em dois terços do planeta.
Os oceanos avançam sobre as costas.
Prédios? A base para. O topo, não.
[serious] E o pior: um segundo depois, a Terra volta a girar.
Tudo o que parou leva o tranco de novo.
Nos polos, quase nada acontece.
Em São Paulo, você seria lançado a 1.530 quilômetros por hora.
[curious] Onde você queria estar nesse segundo?
```

Tamanho: 838 caracteres com as tags (abaixo do limite de ~1.100).

### Estrutura

| Bloco | Frases |
|---|---|
| Gancho | 1 |
| Barreira | 2–3 (você não sente a rotação) |
| Virada | 4–6 (o chão para, você não) |
| Número-herói | 7–9 (1.670 km/h, 465 m em 1 s) |
| Consequências | 10–14 (ar, oceanos, prédios, a volta da rotação) |
| Consequência pessoal + pergunta | 15–17 |

## Conferência da física

| Afirmação | Conta | Resultado |
|---|---|---|
| 1.670 km/h no equador | 2π × 6.378 km ÷ 23 h 56 min (dia sideral) | 1.674 km/h = 465 m/s |
| São Paulo, 1.530 km/h | 1.674 × cos 23,55° | 1.535 km/h |
| Polos, quase nada | v × cos 90° | 0 km/h |
| Quase o dobro de um avião | avião comercial em cruzeiro ~900 km/h | 1,86× |
| Quase meio quilômetro em 1 s | 465 m/s × 1 s | 465 m (≈ 4,4 campos de futebol) |
| Vento supersônico em 2/3 do planeta | som ≈ 340 m/s → cos φ > 0,73 → \|φ\| < 43°; fração da área = sen 43° | 68% da superfície |
| "A gravidade puxa pra baixo, não pro lado" | o que não está preso só é segurado pelo atrito, que não freia 465 m/s em 1 s | correto |
| Prédios: a base para, o topo não | fundação presa à crosta; o resto segue por inércia (desaceleração equivalente a ~47 g se o chão parasse em 1 s) | correto, qualitativo |
| "Um segundo depois, volta a girar" | leitura literal de "parasse por 1 segundo": o que foi freado por colisões recebe o chão de volta a 465 m/s | correto, qualitativo |

## Cenas sugeridas (para o scenes.py)

1. Terra em `ink` girando, seta `blueshift` no equador; HUD "Hipótese #02".
2. "Você" em pé sobre a curva do planeta, com seta de rotação.
3. Chão congela (linha do solo fica `redshift`), "Você" desliza para a direita com rastro `redshift` para trás.
4. Número-herói **1.670 km/h** em 160px `solar`, rótulo "no equador"; avião ao lado com "~900 km/h".
5. Régua de 465 m sobre campos de futebol estilizados.
6. Globo com faixa ±43° destacada em `blueshift` ("vento supersônico"), oceano empurrando a costa.
7. Prédio: base fixa, topo inclinando.
8. Barra de latitude: polos 0 · São Paulo 1.530 · equador 1.670.
9. Pergunta final + logo `hh-stacked-dark`.

## Legenda sugerida (TikTok / Shorts)

> E se a Terra parasse de girar por 1 segundo? 🌍 No equador, o chão anda a 1.670 km/h, e você vai junto. Se ele para, você não. Onde você queria estar nesse segundo?
>
> #ciencia #fisica #ese #curiosidades #espaco #animacao #terra #rotacaodaterra #inercia
