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
