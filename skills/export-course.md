---
name: export-course
description: Compile all lesson content into a combined .md file (with to-do markers and a sibling assets/ folder), then render to both a standalone .html document and a .docx Word document.
version: "3.0.0"
tags: [export, documentation, publishing, pandoc, html, docx, markdown, assets]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

## Overview

The export pipeline has three explicit stages that produce three persistent artifacts:

1. **Stage A — Assemble:** Build `<course_id>-combined.md` + `assets/` folder inside the course directory.
2. **Stage B — Render HTML:** Convert lesson files → `<course_id>-course-document.html` (custom Python builder with semantic CSS).
3. **Stage C — Word Document:** Convert `<course_id>-combined.md` → `<course_id>-course-document.docx` via pandoc.

Running `/export-course` always executes all three stages in sequence (A → B → C). The `.md` file is kept as a first-class editable artifact — users can open it, tweak content, then re-run just Stage B or C with `stage: render` or `stage: docx`.

---

## Inputs

- `course_id` — id of the course to export (e.g. `tumo2026`)
- `course_path` — path to the course directory (default: `courses/<course_id>/`)
- `stage` — `assemble` | `render` | `docx` | `both` (default: `both`; `both` runs all three stages A + B + C)

---

## Stage A — Assemble

### A1. Read course manifest

Read `<course_path>/course.yml` and extract: `title`, `subtitle`, `description`, `estimated_hours`, `tags`, `tools`, `format`, `final_output`.

### A2. Collect modules and lessons

Scan `<course_path>/modules/` for directories containing a `module.yml`. Read each `module.yml` for `title`, `description`, and `order`. Sort by `order`.

For each module, scan its `lessons/` subdirectory for directories containing a `lesson.md`. Read each `lesson.md` frontmatter for `title` and `order`. Sort by `order`.

### A3. Create the assets folder

Create `<course_path>/assets/` if it does not already exist.

Scan every lesson body for:
- Markdown image references: `![alt](path)` — any path that is not an `http(s)://` URL
- Inline SVG blocks: ` ```svg ... ``` ` fenced code blocks or raw `<svg>...</svg>` content

For each local image or SVG file found:
- Copy the file to `<course_path>/assets/<filename>` (preserve the original filename; overwrite if already present)
- Rewrite the reference in the lesson body used for the combined doc to `./assets/<filename>`

For inline SVG blocks (` ```svg ... ``` `):
- Extract the SVG source, write it to `<course_path>/assets/<lesson_id>-<sequential_number>.svg`
- Replace the fenced block in the combined content with `![<lesson_id> diagram <n>](./assets/<lesson_id>-<sequential_number>.svg)`

Log every file copied/written as a bullet list at the end of Stage A output.

### A4. Build combined content

Assemble the combined markdown in this order:

**Cover section:**
```
# <course title>

<subtitle>  
*Exported: <YYYY-MM-DD>*

---

| | |
|---|---|
| **Duration** | <estimated_hours> hours |
| **Disciplines** | <tags joined with ", "> |
| **Tools** | <tools> |
| **Format** | <format> |
| **Final Output** | <final_output> |
```

**For each module (in order):**
```
---

## Module N — <module title>

<module description>

---
```

**For each lesson in the module (in order):**
- The lesson heading: `# <lesson title>`
- The full lesson body content, with these two transformations only:
  1. Local image/SVG paths already rewritten to `./assets/...` per step A3
  2. Mermaid fenced blocks preserved as-is — do NOT convert to text or tables

**Closing line:**
```
---

*End of course handbook. <course title>.*
```

### A5. Inject to-do markers

After assembling the content, scan for incomplete or placeholder sections and inject `- [ ] TODO:` items immediately below them. Criteria for a placeholder section:

- A heading immediately followed by another heading (no body content between them)
- A heading followed only by a line matching: `TBD`, `TODO`, `Coming soon`, `*placeholder*`, `<!-- TODO ...-->`, or an empty blockquote `>`
- A lesson whose body is only the frontmatter delimiter (`---`) with nothing below

For each detected stub, append directly after the heading:

```markdown
> **To Do**
> - [ ] TODO: add content for this section
```

Also prepend a summary block just below the cover table if any stubs were found:

```markdown
> **Document To-Do List** — <N> incomplete section(s) found
> - [ ] <Lesson/Section title> in Module N
> - [ ] ...
```

If no stubs are found, omit this block entirely.

### A6. Write the combined markdown file

Write the assembled content to `<course_path>/<course_id>-combined.md`.

Report:
- Path to the `.md` file
- Path to the `assets/` folder and count of files copied/created
- Count of to-do items injected (or "No incomplete sections found")

---

## Stage B — Render

Reads lesson markdown files directly (not the combined `.md`). Produces `<course_path>/<course_id>-course-document.html` using a **custom Python builder** that generates the established course document style.

### Visual design system

All course HTML documents follow a shared design system first established in `tumo2026-course-document.html`. Key properties:

- CSS variables: `--black #0f0f0f`, `--ink #1a1a1a`, `--accent` (course-specific color), `--accent2` (secondary, purple), `--bg-alt #f7f7f7`, `--page-w 740px`
- Inter + JetBrains Mono fonts via Google Fonts
- Dark code blocks: `background: #1a1a2e; color: #e8e8f0`
- Black table headers: `background: var(--black); color: #fff`
- Accent-colored list markers: `li::marker { color: var(--accent) }`
- Full-bleed dark module headers: `.module-header { background: var(--black) }`

**Per-course accent color** — choose a color that fits the subject:
- `tumo2026`: `#e05a00` (orange — experimental/energy)
- `guitar-pedal-course-2`: `#c0392b` (deep red — dirt/grit)
- New courses: select a distinctive hue; avoid the existing two

### Semantic HTML structure

Generate structured HTML — not pandoc's flat output. Each section of a lesson maps to a specific component:

| Markdown section heading | HTML component |
|---|---|
| `## Overview` | `<div class="lesson-overview">` — left-bordered grey aside |
| `## Learning Objectives` | `<div class="objectives">` — blue box with checkbox list |
| `## Environment` | `<div class="env-box">` — green left-bordered box |
| `## Materials` | `<div class="materials-box">` — amber box |
| `## Session Plan` | `<div class="session-plan">` wrapper; `### HH:MM–HH:MM — Title` → `.time-block` with `.time-stamp` + `.time-content` |
| `## Key Takeaways` | `<div class="takeaways">` — black box with accent heading |
| `## Next Steps` | `<div class="next-steps">` — grey box |
| Mermaid fenced blocks | `<div class="mermaid">` — Mermaid.js renders in-browser |
| All other `##` sections | bare `<h2>` + body |

### Document-level structure (in order)

1. **`<div class="cover">`** — full-height cover with `.cover-label`, `<h1>`, `.subtitle`, and `.cover-meta` grid (6 cells: Format, Duration, Total Hours, Prerequisites, Disciplines, Final Output)
2. **`<div class="toc">`** — custom `<ol>` with `.toc-module` and `.toc-lessons` lists; lesson type badges
3. **Per module:** `<div class="module-header">` with `.module-number` label, `<h2>`, `.module-desc`
4. **Per lesson:** `<div class="lesson-header">` with `.type-badge`, `<h3>`, `.lesson-meta`; then processed lesson body

### Markdown pre-processing (before pandoc)

Apply these fixes to the markdown source of every lesson body **before** passing it to pandoc:

1. **Bold-label + list separation** — pandoc will collapse `**Label:**\n- item` into a single paragraph with inline ` - ` separators unless there is a blank line between them. Insert a blank line whenever a bold-text line (`**...**` or `**...**:`) is immediately followed by a list item (`-` or `*`):
   ```
   regex: (\*\*[^*]+\*\*:?)\n([-*])
   replace: \1\n\n\2
   ```

### Build process

Use pandoc for per-section markdown→HTML fragment conversion (`--from markdown --to html --highlight-style=pygments`), then apply the semantic transformations above in Python.

**Build script:** `course-creator/skills/build_course_html.py`

This is the single generic builder for all courses. It reads course structure dynamically from `course.yml`, `module.yml`, and `lesson.md` frontmatter — no hardcoded course data.

Usage:
```bash
python3 course-creator/skills/build_course_html.py courses/<course-id>
```

The script lives in `course-creator/skills/` — never inside the course directory itself.

**Mermaid fix:** strip inner `<code>` wrapper and unescape HTML entities in all mermaid blocks; use `<div class="mermaid">` not `<pre>`.

### Session plan time-block pattern

`### 0:00–0:20 — Title` → split at the `—` separator, output:
```html
<div class="time-block">
  <div class="time-stamp">0:00–0:20</div>
  <div class="time-content"><strong>Title</strong>
    ... body content ...
  </div>
</div>
```

**Critical:** the closing `</div></div>` for each time-block is written **before** the opening of the next time-block. The final time-block in a session is never followed by another time-block, so its closing tags must be appended explicitly after the loop — not left open. Unclosed time-block divs cause all subsequent content (takeaways, next-steps, following modules) to be rendered inside the flex row, producing broken vertical column layouts.

---

## Stage C — Word Document

Reads `<course_path>/<course_id>-combined.md` (produced in Stage A) and uses pandoc to render a `.docx` Word document. The combined markdown is the source because it already has the correct linear order, cover section, and module dividers baked in.

### C1. Run pandoc

```bash
pandoc "<course_path>/<course_id>-combined.md" \
  --from markdown \
  --to docx \
  --highlight-style pygments \
  -o "<course_path>/<course_id>-course-document.docx"
```

If pandoc is unavailable, report the error clearly and skip this stage — the HTML document is the primary deliverable.

### C2. Post-generation check

Verify the `.docx` file was created and is non-zero bytes. Report file size. If pandoc failed (non-zero exit code), display stderr and suggest running `brew install pandoc` or equivalent.

### C3. Output

Report:
- Path to `<course_id>-course-document.docx` and file size

---

## Output

Return:
- Path to `<course_id>-combined.md`
- Path to `assets/` folder and file count
- Path to `<course_id>-course-document.html` and file size
- Path to `<course_id>-course-document.docx` and file size
- One-line summary: module count, lesson count, asset count, to-do item count
