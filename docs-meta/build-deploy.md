# Build & Deploy

How source files become the live site. Quarto renders `.qmd` → HTML into `/docs/`, GitHub Pages serves `/docs/` on the `main` branch. No CI/CD, no Actions, no build server — `quarto render` on the author's machine is the entire pipeline.

---

## Tech stack

| Layer | Tool | Notes |
|---|---|---|
| Site generator | **Quarto** | `theme: none`, `minimal: true` — zero Bootstrap / zero Quarto scaffolding |
| Styling | Plain CSS with custom properties | Single file: [styles/custom.css](../styles/custom.css) |
| Behavior | Vanilla JS | Single file: [js/main.js](../js/main.js). No framework, no build step. |
| Fonts | Google Fonts (CDN) | Geist, Instrument Serif, JetBrains Mono — see [_partials/head-extras.html](../_partials/head-extras.html) |
| Hosting | GitHub Pages | Serves `/docs` folder on `main` branch |
| CI/CD | **None** | Manual `quarto render` + `git push` |

---

## The render pipeline

```
quarto render
      │
      ├── Pre-render hook: sync-scripts.py
      │       └─ reads js/main.js → wraps in <script> → writes _partials/scripts.html
      │
      ├── Reads _quarto.yml:
      │       ├─ format.html.css     → copies styles/custom.css to docs/styles/
      │       ├─ include-in-header   → injects _partials/head-extras.html into <head>
      │       ├─ include-after-body  → injects _partials/scripts.html before </body>
      │       └─ resources: [js/, assets/, projects.json, blog.json] → copied verbatim to docs/
      │
      ├── Renders each .qmd matching the render: globs:
      │       ├─ "*.qmd"           (root pages)
      │       ├─ "posts/*.qmd"     (articles + splashes)
      │       ├─ "projects/*.qmd"  (case studies)
      │       └─ "!others/**"      (excluded — scratch/homework)
      │
      └── docs/ is ready for GitHub Pages
```

### [_quarto.yml](../_quarto.yml) key settings

```yaml
project:
  type: website
  output-dir: docs              # ← GH Pages reads this folder
  pre-render: sync-scripts.py   # ← auto-generates _partials/scripts.html
  resources:                    # ← static files copied to docs/ verbatim
    - js/
    - assets/
    - projects.json
    - blog.json
  render:
    - "*.qmd"
    - "posts/*.qmd"
    - "projects/*.qmd"
    - "!others/**"              # ← exclude scratch

website:
  navbar: false                 # ← custom nav per page (no Quarto nav)
  sidebar: false

format:
  html:
    theme: none                 # ← strip Bootstrap
    minimal: true               # ← strip Quarto scaffold
    css: styles/custom.css
    include-in-header: _partials/head-extras.html
    include-after-body: _partials/scripts.html
    toc: false
    anchor-sections: false
    smooth-scroll: false
    html-math-method: plain
```

---

## The pre-render hook: [sync-scripts.py](../sync-scripts.py)

18 lines of Python. Reads [js/main.js](../js/main.js), wraps it in a `<script>` tag with a "do not edit" comment, writes to `_partials/scripts.html`. Runs automatically before every render.

**Why inline JS instead of `<script src="js/main.js">`:** Quarto adjusts relative CSS paths per page depth (e.g. root pages link to `styles/custom.css`, `projects/<slug>.html` links to `../styles/custom.css`). But `include-after-body` files are inserted verbatim — paths are **not** adjusted. A `<script src="js/main.js">` tag breaks on nested pages because the path stays `js/main.js` even from `projects/<slug>.html`. Inlining the JS sidesteps this entirely. Full rationale in [decisions.md](decisions.md) entry 4.

**Single source of truth:** [js/main.js](../js/main.js). `_partials/scripts.html` is **gitignored** and regenerated on every render. Do not edit it directly.

---

## Local development

```bash
# Live preview (hot reload on edit)
quarto preview

# One-off build
quarto render

# Render a single file
quarto render posts/metrics-vs-meaning.qmd
```

`quarto preview` is the fastest feedback loop — it rebuilds on file save and refreshes the browser. No `npm run dev` equivalent needed.

---

## Deploy

```bash
quarto render          # regenerates docs/
git add .              # includes the rebuilt docs/
git commit -m "..."
git push               # GitHub Pages picks it up
```

Alternative (one command): `quarto publish gh-pages` — but the current workflow is manual render + push, with `docs/` committed to `main`.

**GitHub Pages config:** Settings → Pages → Source: *Deploy from branch* → Branch: `main`, Folder: `/docs`.

---

## Gotchas

- **`docs/` must be committed.** GitHub Pages reads from the repo, not a build artifact. The rebuilt `docs/` is part of every site-changing commit.
- **Never edit `_partials/scripts.html`.** It's auto-generated and gitignored. Edits will be erased on the next render. Edit [js/main.js](../js/main.js) instead.
- **Never edit files inside `docs/`.** It's the output directory. Edits will be overwritten on the next render.
- **The render globs must include any new folder of `.qmd` files.** If you add `essays/` as a new content type, update `_quarto.yml` `render:` to include `"essays/*.qmd"`.
- **`resources:` must include any static file that should ship to the published site.** Quarto copies only what's listed (plus what's referenced from CSS/HTML). New JSON data files or asset folders need to be added.
- **`others/` is excluded.** It's the scratch/homework folder — anything there is intentionally not rendered and not pushed.
- **Path depth matters.** A case study at `projects/<slug>.qmd` renders to `docs/projects/<slug>.html` — all its intra-site links need `../`. Only case studies and posts live in subdirectories.

---

## [.gitignore](../.gitignore) — what's kept out of git

```
/.quarto/                        # Quarto's own cache
**/*.quarto_ipynb                # Jupyter intermediates
_partials/scripts.html           # auto-generated from js/main.js
.DS_Store, Thumbs.db             # OS cruft
*.swp, *.swo, *~, .idea/         # editor cruft
.env, .env.local                 # secrets (none currently used)
node_modules/                    # no Node deps currently, kept defensively
.devcontainer/                   # RSM-generated, not portable
others/                          # scratch/homework
```

---

## When to update this doc

Append or edit here when you:
- Change anything in [_quarto.yml](../_quarto.yml) that affects the build (resources, render globs, format settings)
- Change the pre-render pipeline (new hook, [sync-scripts.py](../sync-scripts.py) rewrite)
- Move to CI/CD or Quarto publish instead of manual render + push
- Add or remove a major static resource path
- Change the hosting target (away from GitHub Pages)
