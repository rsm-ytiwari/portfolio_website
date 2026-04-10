# Architecture

How the portfolio site is structured, how the build works,
and what to touch for each type of change.

---

## Directory layout

```
Portfolio_website/
│
├── _quarto.yml                  Site config (build settings, CSS, JS includes)
│
├── styles/
│   └── custom.css               Single stylesheet for the entire site
│
├── js/
│   └── main.js                  JS source of truth (edit here)
│
├── _partials/
│   ├── head-extras.html         Injected into <head>: Google Fonts + dark-mode init
│   └── scripts.html             Injected after <body>: full JS inline
│
├── assets/                      Static files copied verbatim to docs/assets/
│   ├── resume.pdf               ← ADD THIS: enables resume page
│   └── profile.jpg              ← ADD THIS: enables about page photo
│
├── index.qmd                    Homepage
├── projects.qmd                 All projects grid
├── resume.qmd                   PDF embed + download
├── about.qmd                    Bio, education, experience, skills
│
├── projects/                    Individual case studies (one file per project)
│   └── traway.qmd               Template — duplicate for every new project
│
├── docs/                        OUTPUT — GitHub Pages reads this folder
│   ├── index.html
│   ├── projects.html
│   ├── resume.html
│   ├── about.html
│   ├── projects/
│   │   └── traway.html
│   ├── styles/
│   │   └── custom.css           Copied from styles/custom.css
│   └── js/
│       └── main.js              Copied from js/main.js
│
├── index.html                   Original hand-coded design (reference only)
└── info.md                      Resume data (reference only, not rendered)
```

---

## Build pipeline

```
quarto render
      │
      ├── reads _quarto.yml
      │       ├── format.html.css        → copies styles/custom.css to docs/styles/
      │       ├── include-in-header      → injects _partials/head-extras.html into <head>
      │       ├── include-after-body     → injects _partials/scripts.html before </body>
      │       └── resources: [js/, assets/] → copies those dirs to docs/
      │
      ├── renders each .qmd file
      │       ├── reads YAML front matter (title, page-layout)
      │       ├── passes {=html} blocks through verbatim
      │       ├── adjusts relative CSS/asset paths per page depth
      │       └── writes output HTML to docs/
      │
      └── docs/ is ready for GitHub Pages
```

**Key Quarto behaviour to know:**
- `page-layout: custom` — Quarto injects no layout scaffolding; the page
  body is exactly what the `.qmd` file contains.
- CSS paths are **auto-adjusted per page depth**: `styles/custom.css` for
  root pages, `../styles/custom.css` for `projects/*.html`.
- `include-in-header` and `include-after-body` files are inserted verbatim,
  paths not adjusted — this is why the JS is inlined rather than sourced.

---

## Request → file map

| What you want to change | File(s) to edit |
|---|---|
| Site colors (entire palette) | `styles/custom.css` → top `:root` + `html.dark` blocks |
| Fonts | `_partials/head-extras.html` (CDN URL) + `body { font-family }` in CSS |
| Navbar links / social URLs | Every `.qmd` file near `EDIT NAV LINKS HERE` |
| Homepage bio | `index.qmd` → `EDIT BIO HERE` |
| Homepage bento cards | `index.qmd` → `EDIT BENTO HERE` |
| Typewriter role line | `js/main.js` → `TW_TEXT` (sync to `_partials/scripts.html`) |
| Tools marquee | `index.qmd` → `.marquee-track` (duplicate text twice for loop) |
| Featured projects (3 on homepage) | `index.qmd` → `EDIT PROJECTS HERE` |
| All projects (full grid) | `projects.qmd` → `EDIT PROJECTS HERE` |
| Projects page banner | `projects.qmd` → `EDIT BANNER HERE` |
| Resume PDF | Replace `assets/resume.pdf` — no other changes needed |
| About photo | Add `assets/profile.jpg`, uncomment `<img>` in `about.qmd` |
| About bio / education / experience / skills | `about.qmd` — each section is labeled |
| Add a new case study | Duplicate `projects/traway.qmd`, add card in `projects.qmd` + `index.qmd` |
| New page entirely | Create `newpage.qmd` with same YAML header as any existing page |

---

## CSS architecture

`styles/custom.css` is organized in order of specificity:

```
1. Reset
2. Color variables  ← ONLY place to change colors
3. Animations (keyframes)
4. Navbar
5. Hero
6. Bento grid
7. Tools strip
8. Project cards      ← shared between index + projects pages
9. Toast
10. Page banner       ← projects.qmd, resume.qmd
11. Resume page
12. About page
13. Case study page
14. Responsive (mobile breakpoints)
```

All colors are CSS custom properties. Light/dark variants are in `:root`
and `html.dark` respectively. No color value appears outside those two blocks.

---

## JS architecture

`js/main.js` (canonical) and `_partials/scripts.html` (inline copy) contain:

| Function | What it does | Elements required |
|---|---|---|
| Theme toggle | Toggles `html.dark`, swaps icon + label | `#theme-toggle`, `#theme-icon`, `#theme-label` |
| Typewriter | Animates the hero role line character by character | `#typewriter` |
| Copy email | Writes email to clipboard, shows toast | `#copy-btn`, `#toast` |
| Active nav | Adds `.active` to matching `.nav-link` based on URL | `.nav-link` elements |

All four functions are **defensive** — wrapped in `if (element)` checks so
they silently no-op on pages where their elements don't exist (e.g.
typewriter only runs on the homepage).

---

## Deployment

```bash
# One-time setup
git init                          # already done
git remote add origin <repo-url>  # if not already added

# Every update
quarto render                     # rebuilds docs/
git add .
git commit -m "update site"
git push

# Or use Quarto's publish command (handles push automatically)
quarto publish gh-pages
```

**GitHub Pages config required:**
Settings → Pages → Source: **Deploy from branch** →
Branch: `main` · Folder: `/docs`

The `docs/` folder is committed to `main` alongside your source files.
GitHub Pages reads it directly — no CI/CD pipeline needed.
