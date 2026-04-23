# CLAUDE.md

**Entry point for any LLM working on this site.** Read this file first. Load supporting docs in `docs-meta/` only as the task requires.

---

## What this project is

Yash Tiwari's personal portfolio site — a custom-designed Quarto static site showcasing data/analytics/ML case studies and long-form "Deep Dive" articles on data science, decision-making, and applied AI. Dark-first dual theme, zero framework dependencies, deployed to GitHub Pages from the `/docs` folder. Hand-authored design system (no Bootstrap, no Quarto defaults). Currently ships 3 project case studies and 2 published articles, with templates and a JSON-driven content model ready for more.

---

## Tech stack at a glance

- **Quarto** static site generator (`theme: none`, `minimal: true` — strips Bootstrap and Quarto scaffolding)
- **Plain CSS** with custom properties — one file: [styles/custom.css](styles/custom.css)
- **Vanilla JS** — one file: [js/main.js](js/main.js). No framework, no bundler.
- **Google Fonts** — Geist, Instrument Serif, JetBrains Mono
- **GitHub Pages** on `main` branch, `/docs` folder. No CI/CD. Manual `quarto render` + `git push`.
- Pre-render hook: [sync-scripts.py](sync-scripts.py) auto-generates `_partials/scripts.html` from [js/main.js](js/main.js)

---

## Directory map (high level)

```
Portfolio_website/
├── CLAUDE.md                 ← You are here. Entry point.
├── docs-meta/                ← LLM-facing supporting docs (this is doc, not build output)
│   ├── design-system.md      ← Colors, typography, components, theming
│   ├── content-model.md      ← JSON data, page types, splash pattern, how to add content
│   ├── build-deploy.md       ← Render pipeline, _quarto.yml, GH Pages
│   ├── file-map.md           ← "To change X, edit Y" lookup table
│   ├── decisions.md          ← Append-only decision log (1-line index + full new entries)
│   └── _archive/             ← Original docs preserved (architecture.md, decisions.md, codex_design.md)
│
├── _quarto.yml               ← Site config
├── sync-scripts.py           ← Pre-render hook
├── _partials/
│   ├── head-extras.html      ← <head>: fonts + dark-mode init
│   ├── scripts.html          ← AUTO-GENERATED — never edit
│   └── case-study-template.html ← Shared navbar for case studies
│
├── styles/custom.css         ← All styling
├── js/main.js                ← All behavior (source of truth)
│
├── index.qmd                 ← Homepage
├── projects.qmd              ← Projects index
├── blog.qmd                  ← Deep Dives index
├── about.qmd                 ← About
├── resume.qmd                ← Resume
│
├── projects.json             ← Project card data (single source of truth)
├── blog.json                 ← Blog card data (single source of truth)
│
├── projects/                 ← Individual case studies
│   ├── new-project-template.qmd
│   └── <slug>.qmd
│
├── posts/                    ← Deep-dive articles + splashes
│   ├── post-template.qmd
│   ├── splash-template.qmd
│   ├── <slug>-splash.qmd
│   └── <slug>.qmd
│
├── assets/                   ← resume.pdf, profile.jpg, favicon.svg
├── docs/                     ← BUILD OUTPUT. GH Pages reads this. Never hand-edit.
└── others/                   ← Excluded from render (scratch)
```

For a complete "to change X, edit Y" table, see [docs-meta/file-map.md](docs-meta/file-map.md).

---

## Load-order guide — which doc to open for which task

| If the task involves… | Load this doc |
|---|---|
| Fast lookup of which file controls what | [docs-meta/file-map.md](docs-meta/file-map.md) |
| Colors, typography, components, theming, cursor effects | [docs-meta/design-system.md](docs-meta/design-system.md) |
| Adding a post, project, or page — or understanding the JSON schema | [docs-meta/content-model.md](docs-meta/content-model.md) |
| `_quarto.yml`, render pipeline, `sync-scripts.py`, deploy, gotchas | [docs-meta/build-deploy.md](docs-meta/build-deploy.md) |
| "Why was X done this way?" — past tradeoffs | [docs-meta/decisions.md](docs-meta/decisions.md) (index) or [docs-meta/_archive/decisions.md](docs-meta/_archive/decisions.md) (full prose, entries 1–45) |

For most tasks, CLAUDE.md + one supporting doc is enough. Don't load all four unless you're doing a site-wide refactor.

---

## Update protocol — keep these docs honest

**After you make a change, update the relevant doc in the same commit.** If you skip this, the docs drift and the next LLM to work on this site has to rediscover everything.

| If you changed… | Update… |
|---|---|
| CSS variables, color tokens, typography, or added a new component class | [docs-meta/design-system.md](docs-meta/design-system.md) |
| JSON schema, page types, splash pattern, or how to add content | [docs-meta/content-model.md](docs-meta/content-model.md) |
| [_quarto.yml](_quarto.yml), [sync-scripts.py](sync-scripts.py), render pipeline, or deploy flow | [docs-meta/build-deploy.md](docs-meta/build-deploy.md) |
| Which file controls what (new or moved file) | [docs-meta/file-map.md](docs-meta/file-map.md) + this file's directory map |
| Made a non-obvious tradeoff (rejected an alternative, went against the obvious choice) | Append a new entry to [docs-meta/decisions.md](docs-meta/decisions.md) |
| Added a major new content section or page type | [docs-meta/content-model.md](docs-meta/content-model.md) + this file's "What this project is" and directory map |

**One-off tweaks (a padding adjustment, a copy change, a new card in JSON) do NOT require a doc update.** Docs describe structure, invariants, and reasoning — not every line of content. Update docs when the *shape* of the site changes.

---

## Guardrails — things to never do

- **Never edit [_partials/scripts.html](_partials/scripts.html).** It's auto-generated by [sync-scripts.py](sync-scripts.py) on every render, and is gitignored. Edit [js/main.js](js/main.js) instead; `quarto render` re-syncs.
- **Never edit files inside [docs/](docs/).** It's the build output; changes will be overwritten.
- **Never hardcode project or blog cards in HTML.** They're JSON-driven ([projects.json](projects.json), [blog.json](blog.json)). Hardcoding breaks featured/filter contracts and creates two-file drift.
- **Never add Bootstrap or Quarto default styles back.** `theme: none` + `minimal: true` is deliberate. The design system assumes nothing else is in the cascade.
- **Never commit without re-rendering.** `quarto render` must run before `git push` if any `.qmd`, CSS, JS, JSON, or config changed. GitHub Pages serves `/docs` as-is.
- **Never push the `others/` folder's contents as site content.** It's excluded from render for a reason (scratch/homework).

---

## Common workflows (fastest paths)

- **Change site colors:** Edit [styles/custom.css](styles/custom.css) `:root` and `html.dark` blocks at the top. Nothing else.
- **Add a project:** Duplicate [projects/new-project-template.qmd](projects/new-project-template.qmd), add entry to [projects.json](projects.json). See [docs-meta/content-model.md](docs-meta/content-model.md).
- **Add a deep dive:** Duplicate [posts/splash-template.qmd](posts/splash-template.qmd) + [posts/post-template.qmd](posts/post-template.qmd), add entry to [blog.json](blog.json) pointing `href` at the splash's `.html`. See [docs-meta/content-model.md](docs-meta/content-model.md).
- **Change homepage bento content:** Edit [index.qmd](index.qmd) — it's handwritten, not JSON-driven.
- **Change nav links:** Edit the navbar block in every root `*.qmd` (navbar is copy-pasted across root pages by design — see [docs-meta/decisions.md](docs-meta/decisions.md) entry 10).
- **Swap the resume PDF:** Replace [assets/resume.pdf](assets/resume.pdf). Nothing else.
- **Render + deploy:** `quarto render && git add . && git commit && git push`.

---

## One more thing — build before you commit

The `/docs` folder is part of the repo. If you change source files but don't re-render, the live site won't reflect your changes. Always: edit → `quarto render` → commit (both source and rebuilt `/docs`) → push.
