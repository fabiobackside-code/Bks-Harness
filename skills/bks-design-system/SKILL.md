---
name: bks-design-system
description: Writes and maintains a project's DESIGN.md (Google Labs format) so brand and interface tokens have one source across PWA, mobile and slides. Use when creating or changing a project's brand, or generating UI for a PWA (installable web app), a mobile app or a slide deck.
---

# Design System

Approach this like the brand steward of a small studio: the brand is written once, in
`DESIGN.md`, and every surface (web, PWA, mobile, slides) reads it instead of reinventing it.

## When to use

- Creating or changing a project's brand: colors, typography, shape, spacing, components.
- Generating UI for a PWA (installable web app), a mobile app or a slide deck.
- Checking that existing UI still matches the brand.

For a plain site or screen with no brand to keep, `frontend-design` alone is enough.

## Flow

1. Look for `DESIGN.md` in the project root. If it exists, it is the source; read it before any
   UI work. If not, write one. The Backside brand lives at
   `skills/bks-design-system/assets/backside/DESIGN.md`, with its six images beside it
   (`mark-*.png` for the horizontal signature, `symbol-*.png` for the symbol).
2. Write or edit the `DESIGN.md` following `references/design-md-format.md`.
3. Validate: `npx -p @google/design.md designmd lint DESIGN.md`. It must exit 0 with no error.
   The plain `npx @google/design.md` form can fail on Windows, so keep the `-p` form.
4. After a change, compare with the previous version: `designmd diff old/DESIGN.md DESIGN.md`.
5. Export tokens for the code: `designmd export --format css-tailwind|json-tailwind|dtcg DESIGN.md`.
6. Build for the target, reading the matching reference: `references/pwa.md`,
   `references/mobile.md` or `references/slides.md`.

Tested with the `@google/design.md` CLI version 0.4.0. The format is alpha: rerun `lint` after
upgrading the CLI.

## The rule

Art direction belongs to the taste skill (`design-taste-frontend`) and to `frontend-design`; the
brand belongs to `DESIGN.md`. When both are active, run the taste skill with `--keep palette,type`
so it never replaces the brand's colors or typefaces. Direction decides layout, rhythm and
composition inside the brand, never the brand itself.

## What NOT to do

- Don't invent a color or typeface that is not in `DESIGN.md`; extend `DESIGN.md` first.
- Don't edit the brand section of a third-party `DESIGN.md` to make a screen pass contrast;
  change the surface instead.
- Don't commit font files; load them from the foundry's CDN as the `DESIGN.md` says.
- Don't write the author's local paths into the file; use repo-relative paths.

## Output format

The `DESIGN.md` (or its diff), the `lint` result, and a short note on which brand rules the work
relied on.

## References

- Read `references/design-md-format.md` when writing or reviewing a `DESIGN.md`.
- Read `references/pwa.md` when the target is an installable web app.
- Read `references/mobile.md` when the target is a mobile app.
- Read `references/slides.md` when the target is a slide deck.
