# DESIGN.md format

Summary of the Google Labs `design.md` spec (alpha). Authority: `designmd spec` prints the spec of
the installed CLI.

## Structure

A file is YAML front matter (between `---` lines) plus markdown prose. The tokens are normative;
the prose explains how to apply them. Fenced `yaml` blocks inside a section are merged into the
same token tree.

## Top-level keys

| Key | Required | Content |
|---|---|---|
| `version` | no | `alpha` |
| `name` | yes | design system name |
| `description` | no | one sentence |
| `omitted` | no | sections left out on purpose, with an optional reason |
| `colors` | no | token name to color |
| `typography` | no | token name to typography object |
| `rounded` | no | scale level to dimension |
| `spacing` | no | scale level to dimension or number |
| `components` | no | component name to property map |

## Token types

- Color: any CSS color; six-digit hex recommended, quoted (`"#336699"`).
- Dimension: number plus `px`, `em` or `rem`.
- Typography: `fontFamily`, `fontSize`, `fontWeight`, `lineHeight` (dimension or unitless),
  `letterSpacing`, `fontFeature`, `fontVariation`.
- Reference: `"{colors.primary}"`, a path into the tree. Outside `components` it must point to a
  primitive; inside `components` it may point to a composite such as a typography token.
- Component properties: `backgroundColor`, `textColor`, `typography`, `rounded`, `padding`,
  `size`, `height`, `width`. Variants are separate keys (`button-primary-hover`).

## Section order

`##` headings, in this order, any of them optional: Overview, Colors, Typography, Layout,
Elevation & Depth, Shapes, Components, Do's and Don'ts. A `#` title is allowed and ignored.

## What is an error and what is a warning

| Condition | Result |
|---|---|
| Duplicate section heading | error, file rejected |
| Duplicate top-level key | error, file rejected |
| Reference that does not resolve | error |
| Unknown section, color name or typography name | accepted |
| Unknown component property | warning |
| Missing section not listed in `omitted` | warning |
| No `primary` color | warning |
| Token defined but never used by a component | warning |
| Component text and background pair below WCAG AA contrast | warning |

`lint` exits 0 when there is no error; keep warnings at zero too.

## CLI

```
npx -p @google/design.md designmd lint DESIGN.md
npx -p @google/design.md designmd diff old/DESIGN.md DESIGN.md
npx -p @google/design.md designmd export --format css-tailwind DESIGN.md
npx -p @google/design.md designmd export --format json-tailwind DESIGN.md
npx -p @google/design.md designmd export --format dtcg DESIGN.md
```

The `export` formats also include `css-vars` (CSS custom properties).
