#!/usr/bin/env python3
"""
Stop hook: auto-sync docs-meta/ when source files change.
Runs at the end of every Claude Code session.

Logic:
  1. Read changed source files from git status (excludes docs/ and docs-meta/).
  2. Map each file to the doc that describes it.
  3. For each doc that needs updating, invoke `claude -p --bare` with a
     targeted prompt. --bare skips hooks so there is no recursion.
  4. If nothing changed, exit 0 immediately.
"""
import json
import os
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Exact filename → doc that describes it
EXACT = {
    "styles/custom.css":  "docs-meta/design-system.md",
    "js/main.js":         "docs-meta/design-system.md",
    "projects.json":      "docs-meta/content-model.md",
    "blog.json":          "docs-meta/content-model.md",
    "_quarto.yml":        "docs-meta/build-deploy.md",
    "sync-scripts.py":    "docs-meta/build-deploy.md",
}

# Path prefix → doc
PREFIX = [
    ("_partials/",  "docs-meta/build-deploy.md"),
    ("posts/",      "docs-meta/content-model.md"),
    ("projects/",   "docs-meta/content-model.md"),
]

# Any .qmd change may affect the file map
QMD_DOC = "docs-meta/file-map.md"

# Dirs to exclude from source-file detection
SKIP_PREFIXES = ("docs/", "docs-meta/", ".claude/", ".quarto/")


def changed_source_files():
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=PROJECT,
    )
    files = []
    for line in r.stdout.splitlines():
        if len(line) > 3:
            f = line[3:].strip()
            if not any(f.startswith(p) for p in SKIP_PREFIXES) and f != "CLAUDE.md":
                files.append(f)
    return files


def map_to_docs(changed):
    needed = {}  # doc_path → set of source files
    for f in changed:
        if f in EXACT:
            needed.setdefault(EXACT[f], set()).add(f)
        for prefix, doc in PREFIX:
            if f.startswith(prefix):
                needed.setdefault(doc, set()).add(f)
                break
        if f.endswith(".qmd"):
            needed.setdefault(QMD_DOC, set()).add(f)
    return needed


def invoke_claude(doc_path, source_files):
    claude = subprocess.run(
        ["which", "claude"], capture_output=True, text=True
    ).stdout.strip()
    if not claude:
        return  # claude not in PATH — skip silently

    sources = ", ".join(sorted(source_files))
    prompt = (
        f"Portfolio website maintenance. Project root: {PROJECT}. "
        f"Source files changed since last commit: {sources}. "
        f"Task: (1) read {PROJECT}/{doc_path}; "
        f"(2) read the changed source files listed above; "
        f"(3) update {doc_path} only where structural facts — file paths, "
        f"component names, build steps, invariants, scope warnings — are now "
        f"wrong or missing. Preserve the doc's existing tone and style. "
        f"Do not add prose sections. If nothing structural changed, make no edits."
    )
    subprocess.run(
        [claude, "-p", prompt, "--bare", "--allowedTools", "Read,Edit"],
        cwd=PROJECT,
        timeout=180,
        capture_output=True,
    )


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}

    # stop_hook_active is set by Claude Code when a stop hook is already running.
    # Belt-and-suspenders guard; the git-status filter is the primary recursion guard.
    if data.get("stop_hook_active"):
        return

    changed = changed_source_files()
    if not changed:
        return

    for doc, files in map_to_docs(changed).items():
        invoke_claude(doc, files)


if __name__ == "__main__":
    main()
