# Codex Design Notes

This file documents the work completed in the Codex session that resumed the
blog section after the earlier Claude session ended.

It is intentionally narrower than `architecture.md` and `decisions.md`:
- `architecture.md` explains how the site is structured overall
- `decisions.md` explains longer-lived site-wide design/build choices
- `codex_design.md` records what Codex changed, why, and what happened during
  implementation

---

## Session Goal

Resume and complete the blog / writing section implementation using the saved
plan:
- add a writing index page
- add a blog JSON data source
- add post-page styling and a reusable post template
- ensure navbar coverage includes `Writing`
- render the site and verify the generated output

---

## Starting Context

When this session began, the repository already contained partial in-progress
blog work:
- `blog.qmd` already existed
- `blog.json` already existed
- `posts/metrics-vs-meaning.qmd` already existed as the first real post
- navbar updates for `Writing` were already present in several files
- `_partials/case-study-template.html` had already been updated to include the
  `Writing` link for shared project-page nav

Because of that, the first decision was to continue from the current repo
state rather than recreate the blog feature from scratch.

---

## Docs Reviewed

Codex reviewed:
- `architecture.md`
- `decisions.md`

`design.md` was mentioned by name in the handoff request, but that file was not
present in the repo. The intended file was later clarified to be
`decisions.md`.

---

## Actions Taken

### 1. Audited the repo before editing

Codex checked:
- current git status
- existing blog files
- current CSS state
- shared navbar partial usage
- project-page structure

This was done to avoid overwriting work already present in the repository.

### 2. Compared implementation against the saved plan

The main mismatch found was on the blog index card design:
- the saved plan called for text-only writing cards
- the in-progress `blog.qmd` used a category-colored preview/header band

Codex treated that as design drift and aligned the page back to the original
writing-first direction.

### 3. Updated `blog.qmd`

Changes made:
- removed the blog-card preview/header band from rendered card HTML
- kept the shared `.p-card`, `.p-body`, `.p-meta`, `.p-tags`, and filter system
- kept client-side draft filtering via `draft: true`
- kept category filter button generation from `blog.json`
- added explicit category ordering for filters:
  - `Data Science`
  - `Marketing`
  - `Philosophy`
  - `Future`
- preserved click-to-open behavior for the whole card

Why:
- the writing section is meant to feel deliberate and text-led
- removing decorative preview blocks makes the cards feel closer to essays than
  portfolio objects
- explicit category order matches the original plan more closely than generic
  alphabetical sorting

### 4. Added `posts/post-template.qmd`

This file did not exist yet, so Codex created it as a reusable starter template
for future posts.

Included in the template:
- post navbar with `../` paths
- back link to `../blog.html`
- post meta row
- example title/subtitle
- starter markdown body inside `.post-body`

Why:
- the plan called for a reusable post starter, not just a single real post
- a template lowers the friction for future additions and keeps structure
  consistent across posts

### 5. Cleaned blog-specific CSS in `styles/custom.css`

The CSS already contained both:
- the planned `b-read-time` styling
- extra rules for the abandoned colored blog preview/header treatment

Codex removed the unused blog preview/header rules and kept only the actual
blog card addition:
- `.b-read-time`
- dark-mode accent override for `.b-read-time`

Why:
- the extra rules no longer matched the chosen markup
- keeping only the active styling reduces confusion for future edits

### 6. Updated `posts/metrics-vs-meaning.qmd`

Codex removed the inline `style="color:var(--accent)"` from the read-time
element in the post header.

Why:
- the shared stylesheet already handles `.b-read-time`
- keeping the color in CSS makes the post page consistent with the template and
  avoids one-off style overrides

### 7. Updated `_quarto.yml`

Codex added:

```yaml
- blog.json
```

to `project.resources`.

Why:
- `blog.qmd` fetches `blog.json` client-side
- before this change, Quarto copied `projects.json` into `docs/` but not
  `blog.json`
- without copying `blog.json`, the deployed/generated blog page would render
  the shell but fail to load post data

This was the most important build-level fix made in the session.

### 8. Rendered and verified output

Codex ran `quarto render` and verified generated output for:
- `docs/blog.html`
- `docs/blog.json`
- `docs/posts/metrics-vs-meaning.html`
- `docs/posts/post-template.html`
- `docs/styles/custom.css`

Verification included checking:
- Twain quote/banner content exists
- blog cards render using text-only markup
- `Read →` links remain present
- post page includes `All Writing`
- `blog.json` is copied to `docs/`
- CSS output includes the intended blog/post rules

---

## Files Added By Codex In This Session

- `codex_design.md`
- `posts/post-template.qmd`

---

## Files Modified By Codex In This Session

- `_quarto.yml`
- `blog.qmd`
- `posts/metrics-vs-meaning.qmd`
- `styles/custom.css`

Generated output after render:
- `docs/blog.html`
- `docs/blog.json`
- `docs/posts/metrics-vs-meaning.html`
- `docs/posts/post-template.html`
- `docs/styles/custom.css`
- other rendered `docs/*.html` files updated as part of the site-wide render

---

## Decisions Made During This Session

### Decision 1. Continue from the current repo state, not from the original checklist alone

Why:
- the repo already contained partial blog implementation
- rebuilding from scratch would risk overwriting useful work or creating
  duplicate structures

### Decision 2. Favor the saved plan over the in-progress visual deviation

Why:
- the in-progress blog card preview bands contradicted the documented design
  philosophy
- the text-only card treatment better supports the intended tone:
  deliberate writing over content volume

### Decision 3. Keep the existing shared systems whenever possible

Reused systems:
- navbar patterns
- `p-card` card system
- `cards-grid`
- `filter-bar`
- existing CSS variables

Why:
- this keeps the writing section visually native to the site
- it also reduces maintenance burden and avoids unnecessary new CSS

### Decision 4. Put behavior in shared CSS/config rather than inline page overrides

Examples:
- removed inline read-time color styling
- added `blog.json` to Quarto resources rather than working around missing data

Why:
- shared behavior is easier to maintain than local exceptions
- this follows the same philosophy already documented in `decisions.md`

---

## Quarto / Build Issues Encountered

During rendering, Quarto intermittently failed with `NotFound` errors involving
its own generated temp folders under `.quarto/`, for example:
- missing `index_files`
- missing `.quarto/quarto-session-temp...`

Observed behavior:
- the failures were not caused by the blog source files themselves
- rerunning after cleanup succeeded

Working workaround used in this session:
- remove `.quarto/quarto-session-temp*` directories
- rerun `quarto render`

This appears to be a temporary Quarto cache/session issue, not a structural
problem in the new blog implementation.

---

## Final State After Codex Work

At the end of the session:
- the blog index exists and uses `blog.json`
- the writing cards are text-only
- the first real post exists
- a reusable post template exists
- the writing data file is copied to `docs/`
- the site renders successfully after Quarto temp cleanup
- generated output includes blog pages under `docs/`

---

## Notes For Future Work

If the writing section is expanded later, the intended workflow is:
1. Duplicate `posts/post-template.qmd`
2. Write the post content
3. Add a matching entry in `blog.json`
4. Run `quarto render`

If `quarto render` throws another temp-session `NotFound` error, clear the
`.quarto/quarto-session-temp*` directories and retry before making source-code
changes.
