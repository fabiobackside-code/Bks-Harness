# PWA (installable web app)

Tokens come from `DESIGN.md`; this file covers what the brand file does not.

## Manifest

`manifest.webmanifest`, linked with `<link rel="manifest">`:

- `name`, `short_name` (up to 12 characters), `start_url`, `scope`, `display: "standalone"`.
- `theme_color`: the brand primary. `background_color`: the base surface of the light theme.
- `lang` and `dir`.
- `icons`: 192 px and 512 px PNG, plus a `purpose: "maskable"` 512 px version.

## Icons from the symbol

- Build from the brand symbol image, never from the horizontal signature.
- Respect the minimum size and the protection area written in `DESIGN.md`.
- Maskable icon: the symbol inside the central 80% (safe zone) on a solid brand surface, because
  the system crops it; no shadow or outline.
- Apple touch icon: 180 px, opaque background.

## Offline

- A service worker precaches the app shell (HTML, CSS, JS, fonts in use, icons).
- Static assets: cache first. Data: network first with cache fallback, or stale-while-revalidate.
- Version the cache name and delete old caches on `activate`.
- Offer an explicit offline page and show connection state in the UI; never fail silently.
- Fonts load from the CDN named in `DESIGN.md`: cache them in the worker so the brand survives
  offline.

## Installation

- Serve over HTTPS.
- Chrome installs when there is a manifest with icons and a service worker; capture
  `beforeinstallprompt` and show an install button at a moment the user chose, not on load.
- iOS has no install prompt: explain "Share, then Add to Home Screen" in the UI when relevant.
- Update flow: when a new worker is waiting, show "new version available" and reload on consent.

## Checks

- Lighthouse PWA audit passes; the app opens offline after the first visit.
- Safe-area insets respected (see `references/mobile.md`).
- Contrast AA in both themes, using the pairs defined in `DESIGN.md`.
