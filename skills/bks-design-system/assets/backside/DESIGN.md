---
version: alpha
name: Backside devs
description: Identidade visual da Backside devs — duas cores de marca, Clash Display nos títulos e Satoshi no texto, mais uma extensão de interface para neutros e estados.
colors:
  backside-blue: "#99CCFF"
  devs-blue: "#336699"
  primary: "#336699"
  white: "#FFFFFF"
  ink: "#1B2633"
  ink-muted: "#4A5868"
  surface: "#FFFFFF"
  surface-alt: "#F4F7FA"
  line: "#D5DDE6"
  night: "#0B1624"
  night-alt: "#14233A"
  night-ink: "#E8EEF4"
  night-muted: "#A9B7C6"
  success: "#1B7A4B"
  warning: "#8A5300"
  error: "#B3261E"
  success-night: "#5FD08F"
  warning-night: "#F2B84B"
  error-night: "#FF8A80"
typography:
  display:
    fontFamily: Clash Display
    fontSize: 48px
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: -0.01em
  headline:
    fontFamily: Clash Display
    fontSize: 32px
    fontWeight: 600
    lineHeight: 1.2
  title:
    fontFamily: Clash Display
    fontSize: 22px
    fontWeight: 500
    lineHeight: 1.3
  body-lg:
    fontFamily: Satoshi
    fontSize: 18px
    fontWeight: 400
    lineHeight: 1.6
  body:
    fontFamily: Satoshi
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: Satoshi
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: 0.01em
  caption:
    fontFamily: Satoshi
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
rounded:
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.white}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 44px
  button-primary-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.white}"
  button-secondary:
    backgroundColor: "{colors.backside-blue}"
    textColor: "{colors.night}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 44px
  button-on-night:
    backgroundColor: "{colors.backside-blue}"
    textColor: "{colors.night}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 44px
  card:
    backgroundColor: "{colors.surface-alt}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
  card-night:
    backgroundColor: "{colors.night-alt}"
    textColor: "{colors.night-ink}"
    typography: "{typography.body}"
    rounded: "{rounded.lg}"
    padding: 24px
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: 12px
    height: 44px
  badge-success:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.success}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
  badge-warning:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.warning}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
  badge-error:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.error}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
  text-muted:
    backgroundColor: "{colors.surface-alt}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.caption}"
  text-muted-night:
    backgroundColor: "{colors.night}"
    textColor: "{colors.night-muted}"
    typography: "{typography.caption}"
  link:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.devs-blue}"
    typography: "{typography.body}"
  divider:
    backgroundColor: "{colors.line}"
    height: 1px
  badge-success-night:
    backgroundColor: "{colors.night}"
    textColor: "{colors.success-night}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
  badge-warning-night:
    backgroundColor: "{colors.night}"
    textColor: "{colors.warning-night}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
  badge-error-night:
    backgroundColor: "{colors.night}"
    textColor: "{colors.error-night}"
    typography: "{typography.caption}"
    rounded: "{rounded.full}"
    padding: 4px
---

# Backside devs

## Overview

Fonte: manual da marca e da identidade visual da Backside, edição de janeiro de 2022. A marca é
sóbria e técnica: duas cores, duas famílias tipográficas e uma assinatura com regras fixas de uso.

Os arquivos da marca ficam ao lado deste `DESIGN.md`, em `assets/backside/`:
`mark-original.png`, `mark-black.png` e `mark-white.png` (assinatura horizontal) e
`symbol-original.png`, `symbol-black.png` e `symbol-white.png` (símbolo isolado).

Tudo o que não está no manual — neutros, cores de estado, escala de espaço e componentes — é
extensão de interface. A extensão nunca altera a marca.

## Colors

Cores da marca, conforme o manual:

| Token | Hex | Pantone | CMYK (ciano, magenta, amarelo, preto) |
|---|---|---|---|
| `backside-blue` (Azul Backside) | `#99CCFF` | 2717C | 35, 10, 0, 0 |
| `devs-blue` (Azul devs) | `#336699` | 647C | 86, 60, 17, 2 |

Contraste, conforme a WCAG (as diretrizes de acessibilidade web) nível AA:

- `devs-blue` sobre branco: 6,0 para 1. Passa como texto e como fundo de botão com texto branco.
- `backside-blue` sobre branco: 1,69 para 1. Não passa como texto. No tema claro serve só como
  superfície ou destaque, com texto escuro `night` por cima (10,77 para 1).
- `backside-blue` sobre `night`: 10,77 para 1. No tema escuro pode ser texto, ícone e botão.

### Extensão de interface

Os tokens abaixo não vêm do manual. Foram propostos para telas e passam em AA (4,5 para 1) no
tema em que servem de texto.

| Token | Hex | Uso | Contraste |
|---|---|---|---|
| `ink` | `#1B2633` | texto principal, tema claro | 15,31 sobre `surface` |
| `ink-muted` | `#4A5868` | texto secundário, tema claro | 7,27 sobre `surface`; 6,77 sobre `surface-alt` |
| `surface` | `#FFFFFF` | fundo base, tema claro | — |
| `surface-alt` | `#F4F7FA` | cartões e faixas, tema claro | 14,24 com `ink` |
| `line` | `#D5DDE6` | divisores e bordas | decorativo, sem texto |
| `night` | `#0B1624` | fundo base, tema escuro | — |
| `night-alt` | `#14233A` | cartões, tema escuro | 7,72 com `night-muted` |
| `night-ink` | `#E8EEF4` | texto principal, tema escuro | 15,56 sobre `night` |
| `night-muted` | `#A9B7C6` | texto secundário, tema escuro | 8,90 sobre `night` |
| `success` | `#1B7A4B` | sucesso, tema claro | 5,34 sobre branco |
| `warning` | `#8A5300` | alerta, tema claro | 6,33 sobre branco |
| `error` | `#B3261E` | erro, tema claro | 6,54 sobre branco |
| `success-night` | `#5FD08F` | sucesso, tema escuro | 9,45 sobre `night` |
| `warning-night` | `#F2B84B` | alerta, tema escuro | 10,16 sobre `night` |
| `error-night` | `#FF8A80` | erro, tema escuro | 7,97 sobre `night` |

Tipografia, também extensão de interface e não regra da marca: Clash Display só em títulos de
22 px para cima; abaixo disso, Satoshi.

Estado nunca se comunica só por cor: acompanha ícone ou texto.

## Typography

Títulos e marca usam Clash Display Variable, de Extralight a Bold. O texto corrido usa Satoshi, de
Light a Black, com itálicos. As duas famílias são da Fontshare, de uso livre; os arquivos de fonte
não entram no repositório. Carregue pela rede de distribuição da Fontshare:

```html
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-display@200,300,400,500,600,700&f[]=satoshi@300,400,500,700,900&display=swap">
```

Pilha de reserva: `"Clash Display", system-ui, sans-serif` e `"Satoshi", system-ui, sans-serif`.

## Layout

Grade de 8 px, com passo de 4 px para ajustes finos. Largura de leitura máxima de 72 caracteres.
Em telas até 640 px, margem lateral de 16 px; acima, 24 px ou mais. Alvo de toque mínimo de 44 px.

## Elevation & Depth

Profundidade vem de camadas de superfície e de `line`, não de sombra pesada. No tema claro,
`surface-alt` sobre `surface`; no escuro, `night-alt` sobre `night`. Sombra, quando usada, é
difusa e de baixa opacidade, e nunca colorida com as cores da marca.

## Shapes

Raio de 8 px em controles, 16 px em cartões e painéis, 9999 px em selos. Cantos retos só em
tabelas e faixas de borda a borda. A assinatura nunca recebe raio, máscara nem moldura.

## Components

Os tokens de `components` cobrem botão, cartão, campo e selo de estado. Cada par de fundo e texto
passa em AA. O botão primário do tema claro usa `devs-blue` com texto branco; no tema escuro, o
botão usa `backside-blue` com texto `night`. O estado de foco usa contorno de 2 px em `devs-blue`
no tema claro e em `backside-blue` no escuro, com 2 px de distância.

## Do's and Don'ts

Faça:

- Use a assinatura horizontal como padrão. O símbolo isolado é permitido com cautela, onde o
  espaço não comporta a horizontal e a marca já é conhecida.
- Respeite o tamanho mínimo digital: 40 px de largura para a horizontal e 30 px para o símbolo.
- Respeite a área de proteção de 2X em volta da assinatura, sendo X a altura do "C" de Backside.
- Em fundo claro, de até 10% de saturação, use a versão positiva (`mark-original.png`).
- Em fundo escuro, use a versão monocromática (`mark-white.png`).
- Quando a marca precisar de uma cor só, use preto (`mark-black.png`, `symbol-black.png`) ou
  branco (`mark-white.png`, `symbol-white.png`). O símbolo isolado também pode ir em Azul
  Backside (`symbol-original.png`).
- Mantenha o contraste AA em todo texto, nos dois temas.

Não faça:

- Não troque a ordem das cores da assinatura.
- Não distorça, estique nem comprima a assinatura.
- Não rotacione a assinatura.
- Não redesenhe a assinatura com outra tipografia.
- Não use outras cores na marca, nem degradê, contorno ou sombra sobre ela.
- Não use `backside-blue` como texto sobre fundo claro.
- Não use `warning` ou `error` como cor de marca ou de destaque comercial.
- Não carregue fontes fora da Fontshare nem guarde arquivos de fonte no repositório.
