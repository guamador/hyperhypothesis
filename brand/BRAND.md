# HyperHypothesis

**E se fosse possível? A física responde.**

Canal de animações curtas (TikTok, Reels, Shorts) sobre cenários improváveis levados a sério: o que *realmente* aconteceria, com números de verdade. Handle: **@hyperhypothesis**.

---

## 1. A ideia por trás da marca

**Hyper** é velocidade, extremo, levar uma ideia ao limite. **Hypothesis** é o "e se...?" de todo vídeo. Juntos: *pegar uma hipótese absurda e acelerá-la até as últimas consequências.*

### O símbolo

Um **H em movimento**, da esquerda para a direita:

- **Feixe laranja atrás (`redshift`):** a luz de quem se afasta fica avermelhada.
- **Ponto azul à frente (`blueshift`):** a luz de quem se aproxima fica azulada. É também o ponto de um "?", o destino da hipótese.

É o efeito Doppler relativístico, exatamente o que você veria a quase a velocidade da luz. O logo é fisicamente correto, e isso é a marca inteira em uma imagem: **visual simples, ciência certa**.

---

## 2. Personalidade

**Arquétipo:** o Explorador rigoroso. Curioso como uma criança, preciso como um engenheiro.

| Somos | Não somos |
|---|---|
| Curiosos, empolgados com o absurdo | Sensacionalistas ("os cientistas estão APAVORADOS") |
| Precisos, com números que dá pra conferir | Professorais ou chatos |
| Bem-humorados de forma seca | Palhaços ou memeiros |
| Confiantes ao dizer "isso mataria você" | Alarmistas ou mórbidos |
| Honestos quando é especulação | Donos da verdade |

**Três palavras:** *curioso, preciso, épico.*

---

## 3. Voz e tom (roteiro e narração)

- **Segunda pessoa, sempre.** "Você entra na nave...", nunca "Uma pessoa entra...". O espectador é o protagonista.
- **Frases curtas.** Uma ideia por frase, máximo de ~12 palavras. A narração precisa respirar com os cortes.
- **Número concreto > adjetivo.** Em vez de "uma energia enorme", diga "9 mil megatons". Todo vídeo tem pelo menos um número-herói.
- **Escala humana.** Traduza o número em algo sentível: "mais que todas as bombas nucleares do mundo juntas".
- **Virada no meio.** Por volta da metade, quebre a intuição: "Mas aí a coisa fica estranha."
- **Final com consequência pessoal**, não com resumo: "Seus amigos envelheceram. Você, quase nada."
- **Proibido:** "Você não vai acreditar", "Fique até o final", clickbait falso, física errada pra ficar mais bonito.

### Estrutura fixa de todo vídeo (45–60 s)

1. **Gancho (0–3 s):** o vídeo abre direto com a pergunta "E se...?", já na primeira palavra da narração, com a imagem mais forte. Nada antes dela: sem "Hipótese número X", sem vinheta, sem apresentação.
2. **Barreira (3–12 s):** por que é impossível, ou o primeiro problema.
3. **Virada (12–35 s):** o que a física realmente diz, a parte contraintuitiva.
4. **Número-herói (35–45 s):** o dado que impressiona, grande na tela.
5. **Consequência (45–60 s):** o que isso significa pra *você*, e uma pergunta final que puxa comentários.

### Narração (ElevenLabs)

- **Voz fixa do canal:** grave, ritmo médio, tom de documentário curioso. Nada de voz de propaganda.
- **Idioma:** PT-BR. Ajuste: *stability* ~40%, *similarity* ~75%, *style* baixo.
- **Abertura:** a primeira frase falada é sempre o "E se...?". O número da hipótese não é narrado.

---

## 4. Estilo de animação: motion graphics 2D

Um estilo **próprio**, inspirado no mundo do logo: geometria simples, cores chapadas, fundo de espaço escuro.

**Regras visuais**

- **Fundo:** sempre `void` (escuro), com poucas estrelas como pontos de `ink` em opacidade baixa.
- **Formas:** círculos, retângulos de canto `radius-sm`, pílulas. Nada de textura, gradiente realista ou sombra.
- **Cores com significado (código Doppler):**
  - `redshift` = passado, perigo, energia, o que fica pra trás
  - `blueshift` = futuro, descoberta, a resposta
  - `solar` = luz, estrelas, explosões
  - `ink` = personagens e objetos neutros
- **Personagem padrão, o "Você":** um boneco geométrico (cabeça círculo, corpo pílula) em `ink`, sem rosto detalhado, só dois pontos de olho. É o espectador em cena.
- **Movimento:** rastros de velocidade sempre em `redshift` pra trás, nunca na frente. Entradas rápidas com leve *overshoot*. Câmera quase sempre estática, quem se move são os objetos.
- **Máximo de 3 cores de destaque por cena.**

### Bloco de estilo para IA (cole no fim de todo prompt)

> `flat 2D motion graphics, geometric shapes, solid flat colors, no gradients, no textures, deep space background #0A0C10, accent colors orange #FF5A1F, cyan #4DD6FF, yellow #FFC93C, off-white #F2EEE6, minimal clean vector style, simple geometric character with round head and pill body, vertical 9:16`

---

## 5. Texto na tela

- **Legenda:** `Unbounded` 700, 64px, caixa alta só no gancho. 2 a 4 palavras por vez, centralizada, **acima** de `safe-bottom` (420px do fundo).
- **Palavra-chave da frase** em `blueshift`; o resto em `ink`.
- **Número-herói:** `Unbounded` 700, 160px, em `blueshift` ou `solar`, com a unidade embaixo em `rotulo` (`ink-muted`).
- **Fórmulas e dados técnicos** (γ, c, anos-luz): `JetBrains Mono`, só como detalhe, nunca no lugar da explicação.
- **Margens:** `safe-x` (96px) dos lados. Nada importante no canto superior direito nem embaixo, onde ficam os botões do TikTok.

---

## 6. Logo: uso correto

| Versão | Quando usar |
|---|---|
| `hh-avatar` | Foto de perfil (TikTok, Instagram, YouTube) |
| `hh-wordmark-dark` | Banners e capas sobre fundo escuro |
| `hh-wordmark-light` | Fundos claros |
| `hh-stacked-dark` | Tela final 9:16 e capa de destaque |
| `hh-mark-dark` / `-light` | Marca d'água no canto (opacidade 60%) e ícones pequenos |

**Não faça:** mudar as cores do feixe e do ponto, inverter a direção (o movimento é sempre →), girar, esticar, colocar sombra ou gradiente, ou trocar a fonte do nome.

---

## 7. Perfil

**Bio (até 80 caracteres):**
> E se fosse possível? 🚀 A física responde em 60s. Animações científicas.

**Série principal:** *Hipótese #01, #02...*, sempre numerada no canto superior esquerdo do vídeo e na capa.

**Hashtags base:** `#ciencia #fisica #ese #curiosidades #espaco #animacao`, mais 2–3 específicas do tema.

**Capa do vídeo (thumbnail):** fundo `void`, um único objeto central, a pergunta em `titulo-capa` com no máximo 5 palavras e o número da hipótese em `blueshift`.
