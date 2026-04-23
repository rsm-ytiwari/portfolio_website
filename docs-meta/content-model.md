# Content Model

How content is organized, where it lives, and how to add more. The site has two maturing content sections (projects and deep-dive articles) both driven by JSON + a template-duplication workflow.

---

## Page types

| Page | File | Role |
|---|---|---|
| Home | [index.qmd](../index.qmd) | Hero + bento grid + featured projects grid + tools marquee |
| Projects index | [projects.qmd](../projects.qmd) | Full grid of all projects, category filter bar, stats |
| Project case study | `projects/<slug>.qmd` | Individual project write-up (banner + results + case body) |
| Deep Dives index | [blog.qmd](../blog.qmd) | Full grid of all articles, category filter bar |
| Article splash | `posts/<slug>-splash.qmd` | Full-viewport gate into an article |
| Article body | `posts/<slug>.qmd` | The article itself |
| About | [about.qmd](../about.qmd) | Bio, education, experience timeline, skills grid |
| Resume | [resume.qmd](../resume.qmd) | Embedded PDF + download button |

The navbar references: Home · Projects · Deep Dives · About · Resume.

---

## JSON-driven data layer

Two files act as the single source of truth for all card grids. Both are listed as `resources:` in [_quarto.yml](../_quarto.yml) so they're copied into `/docs/` at render and fetched client-side.

### [projects.json](../projects.json)

Array of objects; each renders as a `.p-card` on [projects.qmd](../projects.qmd) (all) and [index.qmd](../index.qmd) (where `featured: true`).

```json
{
  "id": "intuit-upsell",
  "number": "01",
  "year": "2026",
  "title": "Intuit QuickBooks Upsell Targeting",
  "summary": "...",
  "tags": ["Python", "XGBoost", "Scikit-learn", "GLM"],
  "category": ["ML", "Analytics"],
  "href": "projects/intuit.html",
  "featured": true,
  "image": ""
}
```

- `category` drives the filter pills automatically — add a new value, a new pill appears.
- `href` must point to the **rendered `.html`** path (not `.qmd`).
- `featured` controls homepage visibility.

### [blog.json](../blog.json)

Array of objects; each renders as a blog card on [blog.qmd](../blog.qmd) and (if `featured`) on the homepage.

```json
{
  "id": "ab-testing-protocol-matters",
  "number": "02",
  "date": "Apr 2026",
  "read_time": "10 min",
  "title": "...",
  "summary": "...",
  "tags": ["A/B Testing", "Statistics", "Frequentist Methods"],
  "category": ["Data Science"],
  "href": "posts/ab-testing-protocol-matters-splash.html",
  "featured": true,
  "draft": false
}
```

- `href` points to the **splash page**, not the article body — this is intentional (see "Splash pattern" below).
- `draft: true` hides the post from rendered grids.

---

## Splash page pattern (deep dives)

Every deep-dive article has **two files**:

1. `posts/<slug>-splash.qmd` — full-viewport gate with title, subtitle, meta, and a single "Read article" CTA. This is what blog cards link to.
2. `posts/<slug>.qmd` — the actual article body. The splash page's CTA links here.

**Why two files:** the splash page gives readers a visual pause and sets tone before the long-form text begins. It also keeps the JSON `href` consistent with "entry point URL" regardless of whether an article has a splash or not in the future. See [decisions.md](decisions.md) for the full rationale.

**Template files** (copy these):
- [posts/splash-template.qmd](../posts/splash-template.qmd)
- [posts/post-template.qmd](../posts/post-template.qmd)

---

## How to add content

### Add a new project case study

1. Duplicate [projects/new-project-template.qmd](../projects/new-project-template.qmd) → `projects/<slug>.qmd`.
2. Fill in the YAML front matter, banner text, meta, result cards, and case body sections.
3. Add an entry to [projects.json](../projects.json) pointing `href` to `projects/<slug>.html`.
4. If it should appear on the homepage, set `"featured": true` and remove `featured` from any project that's being demoted (homepage shows only `featured` entries).
5. Run `quarto render`.

The shared case-study navbar is in [_partials/case-study-template.html](../_partials/case-study-template.html) — included via `include-before-body` in the case study's front matter. Uses `../` paths because case studies render to `docs/projects/<slug>.html`.

### Add a new deep-dive article

1. Duplicate [posts/splash-template.qmd](../posts/splash-template.qmd) → `posts/<slug>-splash.qmd`.
2. Duplicate [posts/post-template.qmd](../posts/post-template.qmd) → `posts/<slug>.qmd`.
3. In the splash file, make the CTA `href` point to `<slug>.html`.
4. Add an entry to [blog.json](../blog.json) with `href: "posts/<slug>-splash.html"`.
5. Run `quarto render`.

Real examples to cross-reference:
- [posts/metrics-vs-meaning-splash.qmd](../posts/metrics-vs-meaning-splash.qmd) + [posts/metrics-vs-meaning.qmd](../posts/metrics-vs-meaning.qmd)
- [posts/ab-testing-protocol-matters-splash.qmd](../posts/ab-testing-protocol-matters-splash.qmd) + [posts/ab-testing-protocol-matters.qmd](../posts/ab-testing-protocol-matters.qmd)

### Add a new page entirely

1. Create `<name>.qmd` at the root with a YAML header matching any existing root page (e.g. `page-layout: custom`).
2. Copy the navbar block from any existing root `.qmd` (navbar is not a shared partial at the root level — see decision 10).
3. Add the page to the nav links in every `*.qmd` that should surface it (this is a known edge of the architecture — the navbar is copy-pasted across root pages).
4. Add to [_quarto.yml](../_quarto.yml) `render:` globs if it's not `*.qmd` at the root.

---

## Category taxonomies

Filter pills are generated from the `category` field in JSON — add a new value, a new pill appears.

**Projects** (as of 2026-04-22): `ML`, `Analytics`
**Deep dives** (as of 2026-04-22): `Data Science`, `Marketing`, `Philosophy`, `Future`

Projects can carry multiple categories (arrays); blog posts currently carry one each.

---

## Invariants to preserve

- Card grids are **always** JSON-driven. Do not hardcode cards in HTML — it breaks the featured/filter contracts and creates two-file drift.
- Project `href` values are the rendered `.html` path, not `.qmd`.
- Blog `href` values point to the **splash** file if one exists.
- The homepage bento grid cells are intentionally handwritten in [index.qmd](../index.qmd) (not JSON-driven). Keep them there — they are not a "card" type.
- `_partials/scripts.html` is auto-generated from [js/main.js](../js/main.js) on every render. Never edit it directly.

---

## When to update this doc

Append or edit here when you:
- Add a new page type or rename an existing one
- Change the JSON schema (new required fields, rename a key)
- Change the splash-page pattern (e.g. make splashes optional, add a second flavor)
- Add a new category taxonomy or retire one
- Add a new content invariant that future LLMs must respect
