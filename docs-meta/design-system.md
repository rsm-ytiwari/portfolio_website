# Design System

Visual foundations and component inventory. This doc mirrors the CSS — **if it disagrees with [styles/custom.css](../styles/custom.css), the CSS wins.** Keep this in sync when you change tokens, add components, or alter the theming model.

---

## Design philosophy

- **Zero Bootstrap, zero Quarto defaults.** `theme: none` + `minimal: true` in [_quarto.yml](../_quarto.yml). Every pixel is authored.
- **Dark-first, light as a refined variant.** Dark mode is the default (set pre-paint in [_partials/head-extras.html](../_partials/head-extras.html) via inline `<script>`); light mode adds targeted overrides in a single `html:not(.dark)` block at the end of the CSS.
- **Liquid glass aesthetic** on `.navbar`, `.badge`, `.theme-pill`, `.cell:not(.terminal-cell)`, `.copy-btn`, `.btn-primary` (dark). Terminal is explicitly opaque — it represents a code environment, not a UI panel.
- **Gradient = identity.** Blue→violet (`#3B82F6 → #A78BFA`) appears in accents, hover shadows, splash buttons, project card glow. Layered `box-shadow` fakes gradient borders without `border-image` (which conflicts with `border-radius`).
- **Zero JS dependencies.** Vanilla `fetch()` for JSON data, vanilla `mousemove` listeners for the cursor effects.

---

## Color tokens

Defined at the top of [styles/custom.css](../styles/custom.css). **All color edits happen here and nowhere else.**

### Dark mode (default) — `html.dark`

```
--bg:             #0D0D0C   /* page background */
--bg-sec:         #161614   /* secondary / striped bg */
--card-bg:        #161614   /* card / cell background */
--text:           #F0EEE8   /* primary text */
--text-muted:     #888580   /* secondary / supporting text */
--accent:         #3B82F6   /* brand blue (WCAG AA on --bg at 5.1:1) */
--accent-alt:     #A78BFA   /* brand violet (gradient right stop) */
--accent-gradient: linear-gradient(135deg, #3B82F6 0%, #A78BFA 100%)
--accent-fg:      #0D0D0C   /* text color on accent background */
--border:         rgba(240,238,232,0.08)
--nav-bg:         rgba(13,13,12,0.85)
```

### Light mode — `:root` + `html:not(.dark)` overrides

```
--bg:             #F4F2ED   /* warm off-white */
--bg-sec:         #ECEAE3
--card-bg:        #FAFAF8
--text:           #0D0D0C
--text-muted:     #5A5754   /* WCAG AA override — #6B6963 failed */
--accent:         #0D0D0C   /* light-mode accent is just black text */
--accent-fg:      #F4F2ED
--border:         rgba(13,13,12,0.1)
--nav-bg:         rgba(244,242,237,0.85)
```

**Key contrast decisions** — see [decisions.md](decisions.md) entries 11, 12, 38 for rationale:
- Dark-mode accent raised from `#2563EB` → `#3B82F6` for WCAG AA (5.1:1 on `#0D0D0C`).
- Light-mode `--text-muted` darkened to `#5A5754` for WCAG AA (4.8:1 on `#F4F2ED`).
- `.t-dim` terminal text fixed globally at `#888` (terminal is always dark regardless of page theme).

---

## Typography

Fonts loaded via Google Fonts in [_partials/head-extras.html](../_partials/head-extras.html).

| Role | Family | Weights | Where |
|---|---|---|---|
| UI / body | **Geist** | 300–800 | Default `body { font-family: 'Geist', sans-serif }` |
| Display / serif accent | **Instrument Serif** *italic* | 1 | `.hero-name`, `.case-title`, `.banner-title`, `.post-title`, `.nav-logo`, `.result-num` |
| Terminal / mono | **JetBrains Mono** | 400 | `.terminal-cell`, `.post-body code` |

### Size scale (selected)

- Hero name: `clamp(80px, 9.5vw, 112px)` (mobile drops to `clamp(48px, 11vw, 72px)`)
- Banner titles: `clamp(40px, 5vw, 64px)`
- Case titles: `clamp(36px, 4.5vw, 60px)`
- Post titles: `clamp(32px, 4vw, 52px)`
- Post body: `16px / line-height 1.85` (desktop), `15px / 1.8` (mobile)
- Section labels (uppercase/tracked): `10–11px, letter-spacing 0.1em–0.12em`

---

## Components

All components live in [styles/custom.css](../styles/custom.css). Sections are clearly delimited with `══` comment banners. Add new components at the end, above the responsive block.

### Layout

| Class | Purpose | Notes |
|---|---|---|
| `.hero-wrap` / `.hero-inner` | Homepage hero | `.hero-wrap` is full-viewport width; `.hero-inner` holds max-width & padding. Dot grid (`.hero-wrap::before`) bleeds edge-to-edge. |
| `.bento` / `.cell` | Homepage bento grid | 2-column grid, glass treatment on `.cell:not(.terminal-cell)`. `.cell-full`, `.cell-available`, `.cell-contact` are variants. |
| `.projects-section` / `.cards-grid` | Project listings | 3-column grid, `.page-banner ~ .projects-section { padding-top: 0 }` removes banner-to-grid gap. |
| `.page-banner` | Projects/blog header | `.banner-label`, `.banner-title`, `.banner-sub` are the three children. |
| `.case-banner` / `.case-body` / `.case-section` | Case study pages | Shared navbar via `_partials/case-study-template.html`. |
| `.post-banner` / `.post-body` | Deep-dive article pages | `.post-body` max-width 760px, line-height 1.85, serif-feel readable typography. |
| `.splash-container` / `.splash-content` | Article splash pages | Full-viewport gate before entering the article body. |

### UI atoms

| Class | Purpose |
|---|---|
| `.navbar` / `.nav-logo` / `.nav-links` / `.nav-link` / `.nav-icon` / `.theme-pill` | Sticky top nav with glass + specular top edge |
| `.badge` / `.badge-dot` / `.badge-text` | Availability pill with pulsing green dot (hover scale + glow) |
| `.btn-primary` / `.btn-ghost` | CTA buttons (primary = glass in dark, solid in light; ghost = outlined) |
| `.copy-btn` / `.toast` | Email copy + bottom-right notification |
| `.p-card` / `.p-preview` / `.p-body` / `.p-meta` / `.p-title` / `.p-desc` / `.p-tags` / `.p-more` | Project/blog cards (flexbox column; "Read more" pinned to bottom) |
| `.b-card-featured` / `.b-featured-badge` / `.b-read-time` | Blog card variants |
| `.filter-bar` / `.filter-btn` | Category filter pills on projects & blog pages |
| `.tools-strip` / `.marquee-wrap` / `.marquee-track` | Scrolling tools marquee under the hero |
| `.scroll-hint` / `.scroll-chev` | Animated scroll prompt |
| `.result-grid` / `.result-card` / `.result-num` | Case-study stat cards (gradient-clipped number) |
| `.timeline` / `.timeline-item` / `.timeline-role` / `.timeline-bullets` | About page experience timeline |
| `.skill-group` / `.skill-tag` | About page skills grid |
| `.splash-title` / `.splash-subtitle` / `.splash-button` | Article splash page |

### Keyframe animations

| Name | Used on | Duration |
|---|---|---|
| `pulse-dot` | `.badge-dot`, `.dot-green` | 2s infinite |
| `blink` | `.blink-cursor` (terminal cursor) | 1s step-end infinite |
| `bounce-scroll` | `.scroll-chev` | 1.5s infinite |
| `marquee` | `.marquee-track` | 28s linear infinite |

---

## Theming mechanism

1. **Pre-paint default:** [_partials/head-extras.html](../_partials/head-extras.html) contains `<script>document.documentElement.classList.add('dark');</script>` — runs before any CSS applies, prevents flash of light mode.
2. **Toggle:** [js/main.js](../js/main.js) section 1 toggles `html.dark` on click; swaps `#theme-icon` (sun/moon SVG) and `#theme-label` ("Dark"/"Light"). No localStorage persistence currently.
3. **Scoping:**
   - Dark styles use `html.dark` prefix (or are unprefixed because dark is the default).
   - Light-mode corrections live in a dedicated `html:not(.dark)` block at the end of the CSS (see decision 11). This block handles contrast fixes, card separation, glass effects, blob re-coloring.
4. **What's not themed:** The terminal cell (`.terminal-cell` — always `#0D0D0C`), the pulsing availability dot color (`#4ADE80`).

---

## Cursor effects (hero pages)

Three layered effects driven by [js/main.js](../js/main.js) sections 5–6. Touch devices (`hover: none`) are fully excluded from the grid/spotlight effect.

1. **Blob parallax** (`--blob-x`, `--blob-y`) — `.hero-inner::after` follows cursor at 35% strength, LERP 0.09, `MAX_DRIFT=120px`, returns to origin after 3s idle. Global `mousemove` listener so the blob responds anywhere on the page, not just over the hero.
2. **Grid parallax** (`--grid-x`, `--grid-y`) — very slow LERP (0.035), `MAX_SHIFT=4px` — subtle drift of the dot pattern.
3. **Spotlight** (`--mouse-x`, `--mouse-y`) — direct cursor tracking, no lerp (any delay reads as lag). Sets radial gradient at cursor position, lighting nearby dots. Hides to `-500px` off-screen on `mouseleave`.

On non-homepage pages, the same system attaches to `document.body` for an ambient version (reduced opacity).

---

## Responsive strategy

Single breakpoint at `@media (max-width: 768px)` at the end of [styles/custom.css](../styles/custom.css). Mobile collapses multi-column grids to 1 column, reduces padding from 64px → 24px, and hides `.nav-links` (no hamburger — site targets desktop recruiters primarily).

---

## When to update this doc

Append or edit here when you:
- Add, rename, or remove a color token
- Change the font family or typography scale
- Add a new component class that isn't a one-off
- Change the theming mechanism (e.g. add localStorage persistence, add a third mode)
- Change the cursor-effect system (new interactions, new parallax layers)

For one-off tweaks to an existing component (hover color, padding adjustment), do not update this doc — the CSS is the source of truth and this doc only covers structure.
