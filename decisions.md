# Design & Build Decisions

Decisions made during the conversion of `index.html` → Quarto website.
Each entry explains *what* was chosen and *why*, so future changes can be
evaluated against the original reasoning.

---

## 1. Output directory: `docs/` not `_site/`

**Decision:** `output-dir: docs` in `_quarto.yml`.

**Why:** GitHub Pages supports two deployment modes on `main` branch —
root (`/`) or `/docs`. Using `docs/` keeps source files and rendered output
on the same branch, avoids a separate `gh-pages` branch, and makes the
repo easier to audit. Quarto's default `_site/` would require configuring
Pages to read from a non-standard path.

---

## 2. `theme: none` + `minimal: true` — zero Quarto defaults

**Decision:** Both flags set in `_quarto.yml` under `format.html`.

**Why:** The design is 100% custom (CSS variables, bespoke components). Any
Bootstrap or Quarto default CSS would conflict with or override the custom
styles. `theme: none` strips Bootstrap; `minimal: true` strips Quarto's own
scaffold elements (TOC container, margin sidebar, etc.).

---

## 3. CSS in one file, not inline

**Decision:** All styles live in `styles/custom.css`, referenced globally.

**Why:** A single file means one place to change colors (the `:root` and
`html.dark` blocks at the top), one place to add new component styles, and
zero `<style>` tags scattered across `.qmd` files. Quarto copies the file
to `docs/styles/custom.css` and auto-adjusts relative paths for pages in
subdirectories (e.g. `../styles/custom.css` for `projects/traway.html`).

---

## 4. JS inlined in `_partials/scripts.html`, not sourced with `<script src>`

**Decision:** The JS block in `_partials/scripts.html` is an inline
`<script>` tag containing the full code, not `<script src="js/main.js">`.

**Why:** `include-after-body` inserts the file verbatim at the end of every
page's `<body>`. A `<script src="...">` tag with a relative path breaks on
pages in subdirectories — `projects/traway.html` would need `../js/main.js`
while top-level pages need `js/main.js`. Inlining the JS sidesteps this
entirely and works at any depth without per-page overrides.

`js/main.js` is kept as the **source of truth** for editing. After making
changes there, paste the updated code into `_partials/scripts.html`.

---

## 5. Dark mode default via inline `<script>` in `<head>`

**Decision:** `_partials/head-extras.html` contains:
```html
<script>document.documentElement.classList.add('dark');</script>
```

**Why:** The original `index.html` uses `<html class="dark">` to start in
dark mode. Quarto controls the `<html>` tag and won't let us set a class
on it from a `.qmd` file. An inline script in the `<head>` fires before the
first paint, so the `html.dark` class is present before any CSS renders.
This prevents a flash of light-mode content on page load.

---

## 6. Active nav link detected by JS, not hardcoded

**Decision:** No `.active` class in the navbar HTML. JS in `scripts.html`
reads `window.location.pathname`, extracts the filename, and adds `.active`
to the matching `.nav-link` at runtime.

**Why:** All pages share the same navbar HTML. If the active class were
hardcoded, the navbar would need to be different in every file — making
future link changes a multi-file edit. JS detection means the navbar is
truly a copy-paste component: identical in every page, zero maintenance.

---

## 7. `render: ["*.qmd"]` to exclude `info.md`

**Decision:** Added to `project` block in `_quarto.yml`.

**Why:** Without this, Quarto renders every `.md` file in the project,
including `info.md` (the raw resume data file), producing an unwanted
`docs/info.html`. The glob restricts rendering to `.qmd` files only.

---

## 8. Subdirectory pages use `../` nav paths

**Decision:** `projects/traway.qmd` has navbar hrefs like `../index.html`,
while top-level pages use plain `index.html`.

**Why:** All links in rendered HTML are relative to the page's own output
location. `docs/projects/traway.html` needs to go up one level to reach
`docs/index.html`. This is the only file-structure difference between
top-level pages and case study pages — noted prominently in the template
comment at the top of `traway.qmd`.

---

## 9. Case study pages live in `projects/` subfolder

**Decision:** Individual project write-ups are `projects/*.qmd`, not
`*.qmd` at root.

**Why:** Keeps the root clean (4 top-level pages: index, projects, resume,
about). Project case studies are a distinct content type and naturally nest
under the projects section. Adding a new case study = one new file in
`projects/`, one new card in `projects.qmd`.

---

## 10. No Quarto navbar (`navbar: false`)

**Decision:** Quarto's built-in navbar is disabled. Each page has its own
navbar HTML block.

**Why:** Quarto's navbar injects Bootstrap-dependent HTML and its own CSS
classes. Since we use `theme: none`, this would be unstyled. The custom
navbar is a plain `<header>` with flexbox — more predictable, easier to
style, and already pixel-matched to the original design.

---

## 11. Light mode overrides in a dedicated block, not mixed into base rules

**Decision:** All light-mode-specific corrections live in a clearly labelled
`/* LIGHT MODE OVERRIDES */` block appended at the end of `custom.css`,
scoped entirely to `html:not(.dark)`.

**Why:** The base rules use CSS custom properties that work in both modes.
Light mode needs targeted corrections (contrast fixes, card separation,
border weight) that would be lost or confusing if merged into the base rules.
A separate block makes it trivial to audit what differs between modes and
prevents accidental dark-mode regressions when editing light-mode fixes.

---

## 12. `.t-dim` and `.blink-cursor` overridden globally, not scoped to light mode

**Decision:** `.t-dim { color: #888 }` applies in both modes. `.blink-cursor`
is split into `html.dark` (#C8FF3E) and `html:not(.dark)` (#2D9E4E).

**Why:** `.t-dim`'s original value (`#555`) fails contrast on the terminal
cell's always-dark background (`#0D0D0C`) in both modes — the terminal is
never re-coloured for light mode, so the fix is unconditional. The cursor
uses a mode-aware split because `#C8FF3E` (neon lime) is appropriate inside
the dark terminal on a dark page, but reads as too aggressive when the rest
of the UI is light. `#2D9E4E` (muted green) keeps terminal semantics without
dominating the light layout.

---

## 13. Card "Read more" pinned via flexbox column on `.p-card`, not fixed height

**Decision:** `.p-card` is `display: flex; flex-direction: column`. `.p-body`
gets `flex: 1`. Tags get `margin-top: auto` to push "Read more" to the
card bottom.

**Why:** The original approach used `height: calc(100% - 176px)` on `.p-body`
to subtract the fixed preview image height. This broke when cards had
different amounts of text — short descriptions left a gap, long ones
overflowed. The flexbox approach lets the card stretch naturally and always
pins "Read more" at the bottom regardless of content length.

---

## 14. Cell E targeted by `.cell-contact` class, not `:has()` or `:last-child`

**Decision:** The "Let's Talk" bento cell has `class="cell cell-contact"`.
The CSS rule is `.cell-contact { align-self: start; }`.

**Why:** Two alternatives were rejected:
- `:last-child` — fragile; breaks if bento cell order ever changes.
- `.cell:has(.copy-btn)` — `:has()` has incomplete support in older
  WebKit/Firefox versions and is unreliable as a targeting strategy for
  layout-critical rules.

An explicit class is unambiguous, zero-specificity-conflict, and survives
any future reordering of the bento grid.

---

## 15. `h1.hero-name` Quarto reset added alongside base `.hero-name` rule

**Decision:** A separate `h1.hero-name` block resets margin, padding, border,
and `text-shadow` at the end of `custom.css`.

**Why:** Even with `theme: none`, Quarto injects a minimal stylesheet that
sets `h1` styles (including potential `text-shadow` or margin resets that
interact with custom values). Adding the override at the end of the file
ensures it wins the cascade without requiring `!important` on the base rule.
The base `.hero-name` rule is kept as-is; this block only handles the
Quarto-injected `<h1>` element context.

---

## 16. Bio split into two `<p>` tags with inline `margin-bottom`

**Decision:** The single hero bio paragraph was split into two `<p
class="hero-bio">` tags. `margin-bottom` was removed from the CSS class and
applied inline on each paragraph (`20px` after the first, `44px` after the
second).

**Why:** The two sentences serve different rhetorical purposes — proof
(ranked #1, two startups) and philosophy (how I work). Separating them
creates a visual beat that lets each land. The gap between paragraphs is
intentionally smaller (20px) than the gap to the CTA buttons (44px) to
preserve the original rhythm. Inline margin rather than a modifier class
keeps the HTML self-documenting without adding a new CSS rule for a
one-off spacing value.

---

## 17. Cell D restructured as a philosophy cell with `.c-quote` + `.c-building-sub`

**Decision:** Cell D was rewritten from a "Currently Building" info cell into
a "Philosophy" cell. The quote `"You are what you don't automate."` was
promoted to the headline using a new `.c-quote` class. The "Currently
Building" label was demoted to a sub-label using a new `.c-building-sub`
class (9px, 70% opacity) beneath a divider.

**Why:** The original layout buried the quote as a footnote in `.c-t3`.
The quote is the most memorable thing in the bento grid — making it the
lead creates a stronger identity statement. `.c-building-sub` is intentionally
smaller and dimmer than `.c-label` to signal hierarchy: philosophy first,
tooling detail second. Two new utility classes rather than inline styles
keep the values reusable and the HTML readable.

---

## 18. `.cell-available` accent top border to signal priority

**Decision:** The availability cell receives `class="cell cell-available"`.
In dark mode this adds a `rgba(200,255,62,0.3)` lime top border; in light
mode a `rgba(13,13,12,0.2)` dark border. No other cell has this treatment.

**Why:** The availability dates are the most recruiter-relevant data point
in the bento grid. A subtle top border creates a visual anchor that draws
the eye without breaking the grid's visual uniformity. The lime colour in
dark mode ties to the accent system; the neutral dark in light mode avoids
lime feeling aggressive on a warm background.

---

## 19. Liquid glass scoped to navbar, pills, bento cells, and copy button — terminal explicitly excluded

**Decision:** The liquid glass system uses `backdrop-filter` + semi-transparent
backgrounds on `.navbar`, `.badge`, `.theme-pill`, `.cell:not(.terminal-cell)`,
and `.copy-btn`. The terminal cell is excluded via `:not(.terminal-cell)`.

**Why:** Liquid glass works by blurring the content beneath a frosted surface.
The terminal cell has a hardcoded `#0D0D0C` background and is semantically
opaque — it represents a code environment, not a UI panel. Applying glass to
it would undermine that metaphor and blur the dot grid behind it in a way
that reads as broken rather than refined. The `:not()` exclusion is
deliberate and documented so future cell types default to glass unless
explicitly opted out.

---

## 20. Light mode glass cells use `box-shadow` outline, not `border`

**Decision:** Light mode glass cells set `border: 1px solid transparent` with
`background-clip: padding-box`, then use a `box-shadow: 0 0 0 1px
rgba(255,255,255,0.7)` to simulate the border stroke.

**Why:** CSS `border` is drawn inside the element's box and clips the
`background`. When `background-clip: padding-box` is set (required to prevent
the semi-transparent background from bleeding behind a coloured border), a
standard `border` would sit in the padding area and cover the background edge.
Using `box-shadow` for the stroke keeps the visual border outside the padding
box, preserving the glass background all the way to the edge. This is a
well-known technique for gradient or semi-transparent border effects without
`border-image`.

---

## 21. Dark mode primary CTA inverted to glass; light mode gets shadow only

**Decision:** In dark mode, `.btn-primary` switches from a solid fill
(`var(--text)` / `#F0EEE8`) to a frosted glass treatment:
`rgba(240,238,232,0.12)` background with `backdrop-filter: blur(12px)`.
In light mode, the solid fill is kept; only a subtle `box-shadow` is added.

**Why:** On a dark background the solid fill button reads as the heaviest
element on the page — too dominant next to the ghost button. The glass
treatment reduces its visual weight while retaining its hierarchy as the
primary action. On a light background the solid fill already has sufficient
contrast and the glass treatment would make the text colour unpredictable
across different underlying content. The asymmetric handling reflects that
glass is most effective as a dark-mode pattern.

---

## 22. Light mode blob — higher opacity, larger size, `mix-blend-mode: multiply`

**Decision:** `html:not(.dark) .hero-inner::after` updated: core opacity 0.13→0.28,
mid-stop 0.06→0.14, blur 24→32px, dimensions 600→640px, offset -100/-80→-120/-100px.
`mix-blend-mode: multiply` and `z-index: 0` added.

**Why:** The original light-mode blob was too faint to compete with the warm page
background — visible only on close inspection and providing no compositional weight.
Raising opacity and increasing blur spread make it perceptible as an ambient colour
field. `mix-blend-mode: multiply` darkens where the blob overlaps page content,
which is correct behaviour on a light background (multiply darkens, screen lightens —
the opposite of dark mode where no blend mode is needed because the additive glow
reads naturally against a dark canvas). `z-index: 0` is explicit to ensure the blob
sits behind text content regardless of stacking context changes.

---

## 23. Cursor-reactive blob — global listener, MAX_DRIFT cap, idle return

**Decision:** The blob IIFE was rewritten from a `heroInner`-scoped `mousemove`
listener to a `document`-level listener. STRENGTH raised 0.20→0.35, LERP 0.06→0.09,
convergence threshold 0.1→0.05. A `MAX_DRIFT = 120px` clamp prevents the blob from
drifting off-screen. A 3-second idle timer and a `document.mouseleave` handler both
call `resetTarget()` to smoothly return the blob to origin.

**Why:** The original implementation only responded when the cursor was inside
`.hero-inner`. On a typical screen the hero occupies ~50% of the viewport — moving
the cursor to the nav or bento grid froze the blob mid-drift. The global listener
means every cursor movement influences the blob, giving a persistent ambient
responsiveness. `MAX_DRIFT` prevents extreme positions when the cursor is at a
screen edge far from the blob's anchor point; 120px keeps the effect dramatic
without the blob disappearing behind other elements. The idle timer and
`mouseleave` reset prevent stale drift when the user leaves the window or goes
idle — both return to origin via the same lerp loop so the transition is smooth.

---

## 24. `.hero-wrap` full-viewport width; constraints moved to `.hero-inner`

**Decision:** `.hero-wrap` lost `max-width`, `margin: 0 auto`, and horizontal
padding. Those three properties moved to `.hero-inner`. The `::before` pseudo-element
(dot grid) now spans edge-to-edge with `inset: -20px`, unrestricted by any container
width. Mobile breakpoint updated: `.hero-wrap { padding: 64px 0 0 }`, `.hero-inner
{ padding: 0 24px }`.

**Why:** The dot grid was clipped to the 1280px content box, creating a hard visible
edge on wide viewports where the page background continued beyond the grid. Separating
layout concerns — `.hero-wrap` owns only position and top padding; `.hero-inner` owns
the content column — lets the `::before` texture cover the full viewport while the
text and bento stay centered. The mobile fix moves padding to `.hero-inner` so the
grid still bleeds to screen edges on small screens while content stays inset.

---

## 25. Dot grid: cursor spotlight + dreamy grid parallax (two-layer system)

**Decision:** The dot grid `::before` `background` property now layers two
`radial-gradient` calls in a single shorthand. Layer 1 (top): a large soft circle
at `var(--mouse-x, -500px) var(--mouse-y, -500px)` — 280px radius in dark, 240px
in light — illuminates dots near the cursor. Layer 2: the repeating dot pattern,
shifted by `var(--grid-x) var(--grid-y)`. The JS IIFE was rewritten to set
`--mouse-x`/`--mouse-y` with zero lerp (direct, instantaneous) and `--grid-x`/
`--grid-y` with `LERP_GRID=0.035`, `MAX_SHIFT=4px`. Touch devices excluded via
`(hover: none)` media query. `mouseleave` sets spotlight to `-500px` to hide it
instantly.

**Why:** Two separate interaction qualities serve two separate purposes. The
spotlight must feel *alive* — any lerp delay between cursor and lit dots reads as
lag and breaks the illusion. Grid parallax must feel *ambient* — instant response
would make the grid jitter distractingly. Setting them through separate CSS variables
means each effect is independently tunable without coupling the animation loops.
`-500px` as the off-screen default ensures the spotlight never appears on page load
or on touch devices where no cursor position is available.

---

## 26. Light mode blob → monochromatic depth vignette

**Decision:** The light mode `html:not(.dark) .hero-inner::after` was changed from
a coloured blob (first indigo/purple, then amber-rose) to a pure monochromatic
depth vignette: `rgba(13,13,12,0.05)` at the ellipse centre, fading to transparent,
with `blur(48px)`. Fixed anchor at `62% 35%` rather than cursor-reactive. No colour.

**Why:** Every coloured blob tested against the warm off-white page background
created a palette conflict — the blob colour had to either dominate (too loud) or be
so faint it was invisible. The Apple-style approach: use only luminosity to create
depth. A very subtle dark shadow behind the bento grid separates it from the page
without introducing a competing hue. The fixed anchor point (`62% 35%`) places the
deepest shadow roughly behind the bento grid's upper-right quadrant, reinforcing
the grid's elevation without requiring cursor tracking in light mode.

---

## 27. Light mode blob — settled on indigo at 20% opacity

**Decision:** After iterating through amber-rose and monochromatic depth vignette,
the light mode blob was set to indigo: `rgba(79,70,229,0.20)` at the core, fading
through `rgba(99,102,241,0.09)` and `rgba(139,92,246,0.02)`. `blur(20px)`,
`560×560px`, `top: -80px; right: -60px` — matching the dark mode blob's geometry.
`mix-blend-mode: normal`.

**Why:** The monochromatic vignette was invisible against the warm off-white
background at any opacity that didn't muddy the page. Amber-rose created palette
conflict with the page's warm neutrals. Indigo provides warm-cool tension that
mirrors dark mode's lime-on-black — the same compositional logic, different palette.
At 20% it reads as colour without competing with text or glass cells. `blur(20px)`
(vs. dark mode's 16px) keeps the edge softer on the lighter canvas.
`mix-blend-mode: normal` prevents the indigo from bleeding into cell backgrounds
through multiply or screen compositing.

---

## 28. Sticky navbar — `position: relative` override removed

**Decision:** The liquid glass system block contained `.navbar { position: relative; }`.
This was removed. The base `.navbar` rule's `position: sticky; top: 0` now applies
in both dark and light modes.

**Why:** The glass system block was added after the base navbar rule and unintentionally
overrode `position: sticky` with `position: relative`, making the navbar scroll away
with the page. The fix is a deletion, not an addition — the base rule already had the
correct sticky declaration. The glass block only needed to override visual properties
(background, backdrop-filter, border); layout properties should never be set in a
theme override block.

---

## 29. `projects.json` as single source of truth for project cards

**Decision:** All project metadata (title, summary, tags, year, href, featured flag,
image path) lives in `projects.json` at the project root. `projects.qmd` and
`index.qmd` fetch this file at runtime and render cards via a vanilla JS template
literal. `_quarto.yml` adds `projects.json` to `resources` so it is copied to
`docs/projects.json` on every render. To add a project: edit the JSON, create a
case-study `.qmd`, run `quarto render`. No HTML to touch.

**Why:** The previous hardcoded approach required updating card HTML in two separate
files (`index.qmd` and `projects.qmd`) for every project change, with no guarantee
the two stayed in sync. A single JSON source eliminates the duplication. The `featured`
boolean lets the homepage and the full grid share one dataset without separate
maintenance. Vanilla `fetch()` with no dependencies keeps the approach consistent
with the rest of the site's zero-dependency JS philosophy.

---

## 30. Whole card clickable via delegated click handler

**Decision:** After cards are injected into the DOM, each `.p-card` gets a click
listener that navigates to `link.href` — unless `e.target.closest('a')` is truthy,
in which case the event is left to the anchor's default behaviour. `.p-card` already
had `cursor: pointer` in CSS; no CSS change was needed.

**Why:** Users expect the entire card to be clickable, not just the "Read more" text.
The guard `e.target.closest('a')` prevents double-navigation when the "Read more"
link itself is clicked — without it, both the card listener and the anchor's default
would fire, causing two navigations. Using `getAttribute('href') !== '#'` checks the
raw attribute (not the resolved absolute URL) to correctly detect disabled/placeholder
links without string-comparing full URLs.

---

## 31. Case study template: `include-before-body` for navbar only

**Decision:** `_partials/case-study-template.html` contains the shared navbar with
`../` paths. It is used via `include-before-body: ../_partials/case-study-template.html`
in each case study's front matter. The banner, result cards, and case body are
authored directly in each `.qmd` as `{=html}` blocks interleaved with markdown.
`projects/new-project-template.qmd` is the copy-and-fill starter file.

**Why:** Quarto's `include-before-body` inserts files verbatim — Pandoc's `$variable$`
template substitution does not run in raw includes. Attempting to inject YAML metadata
via `$project_tag$` etc. in the include would produce literal dollar-sign strings in
the output. The working pattern is: the partial owns only the truly static, shared
structure (navbar); page-specific data is authored inline with clear EDIT HERE markers.
This is identical to how every other page in the site already works — it just formalises
the navbar as a shared partial to avoid drift across case study pages.

---

## 32. Traway bridge page instead of direct external link

**Decision:** `projects/traway-bridge.qmd` is a lightweight portfolio page that
introduces the Traway analysis and links out to `traway.live`. The project card in
`projects.json` points to `projects/traway-bridge.html`. The direct `https://traway.live`
href (briefly set in the JSON) was removed.

**Why:** Linking a project card directly to an external URL breaks the expected UX
pattern — clicking a card in a portfolio should land on a page within the portfolio,
not jump off-site without warning. The bridge page gives context (banner, metadata,
stat cards), presents the external analysis as a deliberate handoff, and keeps the
navigation model consistent. It also lets the Traway entry carry the standard
case-study design (case-banner, result-grid) without hosting the full analysis inline.
