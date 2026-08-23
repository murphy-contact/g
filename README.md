# g

The Mulligan's Bar Golf Society Captain's Day draw sheet, served by GitHub Pages
at [mulligansbar.online](https://mulligansbar.online/).

- `index.html` — the whole thing: tee sheet, both sides, and the shots in every match
- `draw.html` — a redirect to `/`, so links shared before the restructure still work
- `draft.html` — staging copy for previewing a change before it goes live

Static HTML, no build step. Pages serves this repo from `main` at the root.
The page carries `noindex` so search engines skip it; the link still works for
anyone it is sent to.

The small print opens with an "As of ..." stamp that is refreshed on every push.

Changes are previewed at `/draft.html`, which carries a banner marking it as a
draft. Promoting strips the banner, so the approved page is what gets published.
