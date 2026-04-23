# Design & Build Decisions

Append-only log of non-obvious tradeoffs. Each entry answers three questions:
**what was decided, why, when it might be worth revisiting.**

- **Pre-2026-04-15 decisions** (entries 1–45) live in the [archive](_archive/decisions.md) with full prose. This file indexes them as one-liners so an LLM can scan them fast and only deep-dive when needed.
- **New decisions** (2026-04-15 onward) are written directly in this file with full prose. Append at the bottom.

When you make a non-obvious tradeoff, add an entry here before moving on. A "non-obvious tradeoff" is any choice a future reader (or future LLM) would question without the reasoning.

---

## Index — archived decisions 1–45

Full text in [_archive/decisions.md](_archive/decisions.md#1-output-directory-docs-not-_site).

### Build & project layout
1. Output directory `docs/` not `_site/` — GitHub Pages reads `/docs` on main, no gh-pages branch needed.
2. `theme: none` + `minimal: true` — strips Bootstrap and Quarto scaffolding; design is 100% custom.
3. All CSS in one file (`styles/custom.css`) — one place for colors, one place for components.
4. JS inlined via `_partials/scripts.html` (not `<script src>`) — solves relative-path problem on nested pages.
5. Dark mode default via inline `<script>` in `<head>` — fires before first paint, prevents flash.
6. Active nav link detected by JS, not hardcoded — same navbar HTML in every page.
7. `render: ["*.qmd"]` glob — excludes `info.md` from being rendered to HTML.
8. Subdirectory pages use `../` nav paths — only structural difference between root and `projects/` pages.
9. Case studies live in `projects/` subfolder — keeps root to 4 top-level pages.
10. No Quarto navbar (`navbar: false`) — custom `<header>` avoids Bootstrap dependency.

### Light mode & contrast
11. Light-mode overrides in a dedicated `html:not(.dark)` block at end of CSS — audit-friendly, no dark-mode regressions.
12. `.t-dim` (#888) and `.blink-cursor` global, not light-scoped — terminal is always dark, fix is unconditional.
38. Accent changed `#2563EB` → `#3B82F6` — meets WCAG AA on dark background (5.1:1).

### Bento grid & cells
13. `.p-card` "Read more" pinned via flexbox column, not fixed height — handles variable description length.
14. Cell E targeted by `.cell-contact` class, not `:has()` — explicit > fragile pseudo-class support.
15. `h1.hero-name` reset block added — defeats Quarto's injected h1 styles without `!important`.
16. Bio split into two `<p>` tags with inline `margin-bottom` — intentional rhetorical beat.
17. Cell D = philosophy cell with `.c-quote` + `.c-building-sub` — promotes the memorable line.
18. `.cell-available` accent top border — draws the eye to recruiter-relevant info.
19. Liquid glass scoped away from `.terminal-cell` — terminal is semantically opaque (code env, not UI panel).
20. Light-mode glass cells use `box-shadow` outline, not `border` — works with `background-clip: padding-box`.
21. Dark `.btn-primary` = glass; light = solid + shadow — asymmetric handling, glass is a dark-mode pattern.

### Hero effects
22. Light-mode blob — opacity 0.28, `mix-blend-mode: multiply`, blur 32px — visible without palette conflict.
23. Cursor blob: global listener, `MAX_DRIFT=120px`, 3s idle reset — ambient, never freezes mid-drift.
24. `.hero-wrap` full-viewport width; constraints on `.hero-inner` — lets dot grid bleed edge-to-edge.
25. Dot grid = cursor spotlight (no lerp) + grid parallax (lerp 0.035) — two separate effects for two qualities.
26. Light-mode blob rewritten → monochromatic depth vignette (superseded by #27).
27. Light-mode blob settled on indigo at 20% — mirrors dark's warm-cool tension on a warm canvas.
28. Sticky navbar fix — glass-system block was overriding `position: sticky` with `relative`.
39. Blob gradients: `radial-gradient(circle at 50% 50%, ...)` everywhere — spherical, not rectangular sweep.

### Projects page & cards
29. `projects.json` = single source of truth for project cards — one file, no HTML-in-two-places duplication.
30. Whole card clickable via delegated click handler — guard with `e.target.closest('a')` to prevent double-nav.
31. Case study template: `include-before-body` for navbar only — inline `{=html}` for data; Pandoc `$vars$` don't work in raw includes.
32. Traway uses a bridge page, not a direct external link — keeps clicks inside the portfolio.
33. Banner-to-grid spacing: `.page-banner ~ .projects-section { padding-top: 0 }` — sibling selector, doesn't touch the homepage case.
34. `.p-desc` clamp raised to 3 lines + `min-height: 60px` — ensures impact metric is visible; even row heights.
35. `.p-card:focus-visible` + `this.blur()` on click — keyboard accessibility preserved, no stuck focus ring.
36. Category filter bar generated from JSON — add a category = set `"category": "..."` in JSON, button appears.
40. Card borders: subtle 1px base + refined blue/violet shadow layering on hover — rejects `border-image` (conflicts with `border-radius`).
41. Bento cell hover: `box-shadow` glow layers only, no border lines — shadows don't bleed onto neighbors.
42. Project card hover shadows: pronounced blue+violet layered glow — gradient effect without `border-image`.
43. Filter button borders at `rgba(240,238,232,0.25)` — readable at 2.5× the previous subtle border.
44. Badge (`Open to Opportunities`) gets hover scale + green glow — ties to pulsing dot's semantics.

### Build automation
37. `sync-scripts.py` pre-render hook — `js/main.js` is SoT; `_partials/scripts.html` is auto-generated and gitignored.
45. CSS cleanup — removed old `.cell` duplicates and `transition: all`; explicit property transitions throughout.

---

## New decisions

Append here. Format:

```
## N. Short title

**Decision:** What was chosen.
**Why:** The reasoning, including what was rejected and why.
**When to revisit:** The condition or signal that would make this worth re-examining.
```

---

## 46. LLM-facing docs split into CLAUDE.md + docs-meta/

**Decision:** Introduced [CLAUDE.md](../CLAUDE.md) at the repo root as the single entry point for any LLM working on the site, with supporting docs in `docs-meta/` (design system, content model, build & deploy, file map, this decisions log). Originals (`architecture.md`, `decisions.md`, `codex_design.md`) moved to `docs-meta/_archive/` via `git mv` to preserve history.

**Why:** Before this change, three sibling markdown files sat at the repo root with no index and no rule for which to load first or which to update after a change. An LLM arriving cold had to scan all three to orient, and updates drifted because nobody knew which file owned what. A single entry point + split-by-concern supporting docs means the LLM loads only what the task needs, and a "what to update when" protocol in CLAUDE.md tells it which doc to refresh. `docs-meta/` (not `docs/`) because Quarto's build output already owns `/docs` — naming collision would be a real footgun.

**When to revisit:** If the site grows a second audience (a human wiki, a public contributor's guide), the CLAUDE.md + docs-meta split may no longer serve both audiences well — consider a separate README.md for humans while keeping CLAUDE.md LLM-focused.
