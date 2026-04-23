# File Map — "To change X, edit Y"

The fastest lookup in the docs. If you know what you want to change, this table tells you exactly which file to open. No prose.

For the reasoning behind these file choices, see [decisions.md](decisions.md) and [build-deploy.md](build-deploy.md).

---

## Global / site-wide

| To change… | Edit… |
|---|---|
| Site colors (entire palette) | [styles/custom.css](../styles/custom.css) → `:root` + `html.dark` blocks at the top |
| Accent color / gradient | [styles/custom.css](../styles/custom.css) → `--accent`, `--accent-alt`, `--accent-gradient` |
| Fonts (swap family) | [_partials/head-extras.html](../_partials/head-extras.html) (Google Fonts URL) + `font-family` rules in [styles/custom.css](../styles/custom.css) |
| Favicon | [assets/favicon.svg](../assets/favicon.svg) |
| Dark-mode default (initial theme) | [_partials/head-extras.html](../_partials/head-extras.html) — inline `<script>` adds `html.dark` before paint |
| Theme toggle behavior | [js/main.js](../js/main.js) → section `1. Theme Toggle` |
| Navbar links (site-wide) | Every `*.qmd` file's navbar block (copy-paste; all files must stay in sync) |
| Nav active-link detection | [js/main.js](../js/main.js) → section `4. Active Nav Link Detection` |
| Responsive / mobile breakpoints | [styles/custom.css](../styles/custom.css) → `@media (max-width: 768px)` block |

## Homepage — [index.qmd](../index.qmd)

| To change… | Edit… |
|---|---|
| Hero name | `index.qmd` → `.hero-name` block |
| Typewriter role line | [js/main.js](../js/main.js) → `TW_TEXT` constant |
| Hero bio paragraphs | `index.qmd` → `.hero-bio` blocks |
| Availability badge text | `index.qmd` → `.badge-text` span |
| Bento grid cells | `index.qmd` → `.bento` block (cells A–E) |
| Terminal bento content | `index.qmd` → `.terminal-cell` block |
| "Let's Talk" email | [js/main.js](../js/main.js) → `email` constant in Copy Email section |
| Tools marquee text | `index.qmd` → `.marquee-track` (duplicate text twice for seamless loop) |
| Featured projects (3 on homepage) | [projects.json](../projects.json) — set `"featured": true` on 3 entries |

## Projects — index & case studies

| To change… | Edit… |
|---|---|
| Projects page banner | [projects.qmd](../projects.qmd) → `.page-banner` block |
| Project card data (all cards) | [projects.json](../projects.json) — single source of truth |
| Category filter pills | [projects.json](../projects.json) — pills generated from `"category"` fields automatically |
| Add a new case study | 1) Duplicate [projects/new-project-template.qmd](../projects/new-project-template.qmd), 2) Add entry to [projects.json](../projects.json) |
| Case study shared navbar | [_partials/case-study-template.html](../_partials/case-study-template.html) (uses `../` paths) |
| Card hover shadows / glow | [styles/custom.css](../styles/custom.css) → `.p-card:hover` block |

## Deep Dives / Writing — [blog.qmd](../blog.qmd)

| To change… | Edit… |
|---|---|
| Blog page banner | [blog.qmd](../blog.qmd) → `.page-banner` block |
| Blog card data (all posts) | [blog.json](../blog.json) — single source of truth |
| Featured-post badge | [blog.json](../blog.json) — set `"featured": true` |
| Category filters | [blog.json](../blog.json) — pills generated from `"category"` fields |
| Add a new post | 1) Duplicate [posts/splash-template.qmd](../posts/splash-template.qmd) and [posts/post-template.qmd](../posts/post-template.qmd), 2) Add entry to [blog.json](../blog.json) pointing `href` to the `-splash.html` file |
| Article body typography | [styles/custom.css](../styles/custom.css) → `POST PAGE` block (`.post-body`, `.post-body p`, etc.) |
| Splash page styling | [styles/custom.css](../styles/custom.css) → `SPLASH PAGE` block |

## About — [about.qmd](../about.qmd)

| To change… | Edit… |
|---|---|
| About photo | Replace [assets/profile.jpg](../assets/profile.jpg) |
| About bio | `about.qmd` → `.about-bio` block |
| Education entries | `about.qmd` → `.edu-item` blocks |
| Experience timeline | `about.qmd` → `.timeline-item` blocks |
| Skills | `about.qmd` → `.skill-group` blocks |

## Resume — [resume.qmd](../resume.qmd)

| To change… | Edit… |
|---|---|
| Resume PDF | Replace [assets/resume.pdf](../assets/resume.pdf) — no other changes needed |
| Resume page copy (buttons, caption) | [resume.qmd](../resume.qmd) |

## Build & deploy

| To change… | Edit… |
|---|---|
| Render pipeline / pre-render hook | [sync-scripts.py](../sync-scripts.py) |
| Output directory | [_quarto.yml](../_quarto.yml) → `output-dir` |
| CSS/JS includes | [_quarto.yml](../_quarto.yml) → `format.html.css`, `include-in-header`, `include-after-body` |
| Which `.qmd` files render | [_quarto.yml](../_quarto.yml) → `project.render` globs |
| Static resources copied to `/docs` | [_quarto.yml](../_quarto.yml) → `project.resources` |
| What gets ignored from git | [.gitignore](../.gitignore) |

## Never-edit files

| File | Why |
|---|---|
| [_partials/scripts.html](../_partials/scripts.html) | Auto-generated by `sync-scripts.py` on every render. Edit [js/main.js](../js/main.js) instead. |
| [docs/](../docs/) | Build output. Regenerated by `quarto render`. Never hand-edit. |
| [.quarto/](../.quarto/) | Quarto's cache. Safe to delete; will regenerate. |
