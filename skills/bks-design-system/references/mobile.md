# Mobile

Tokens come from `DESIGN.md`. Pick the platform guideline that matches the target and map the
brand tokens onto it; never replace the brand.

## Material 3 (Android)

- Map the brand to the color roles: primary, on-primary, surface, on-surface, error. Keep the
  brand values; derive tonal variants only for states.
- Type scale roles (display, headline, title, body, label) map one to one to the `typography`
  tokens of the `DESIGN.md`.
- Shape scale from the `rounded` tokens. Elevation by tonal surface, not heavy shadow.
- Touch target at least 48 dp.
- Dynamic color is off for branded apps unless the brand allows it.

## Apple Human Interface Guidelines (iOS)

- Touch target at least 44 pt.
- Respect Dynamic Type: sizes scale with the system setting; test the largest accessibility size.
- Use system navigation patterns (tab bar, navigation stack, sheets); the brand lives in color,
  type and imagery, not in reinvented navigation.
- Support light and dark appearance with the two themes of the `DESIGN.md`.
- App icon from the symbol, full bleed, no transparency, no rounded corners drawn by hand.

## Touch and spacing

- Space between adjacent targets at least 8 dp or pt.
- Primary action within thumb reach, in the lower half of the screen.
- Visible focus for keyboard and switch users; do not rely on hover.
- Every gesture has a visible alternative.

## Safe area

- Keep content and controls inside the safe area (notch, status bar, home indicator, rounded
  corners). Backgrounds may bleed under them.
- On the web, use `env(safe-area-inset-*)` and `viewport-fit=cover`.
- Test portrait and landscape, a small phone (360 dp or 375 pt wide) and a large one.

## Checks

- Contrast AA for every text and background pair, in both themes.
- Text scales to 200% without clipping.
- States covered: loading, empty, error, offline.
