# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.6.0] - 2026-05-13

### Added
- **Stage C — Word Document** added to `/export-course` skill (v3.0.0): pandoc converts `<course-id>-combined.md` → `<course-id>-course-document.docx`; `stage: docx` re-runs Stage C independently; skill description, overview, and output section updated
- **Course version in outputs**: `version` field from `course.yml` is now embedded in the HTML cover metadata grid and the combined markdown cover table, so every exported document carries its own version number
- **`/export-course` added to Quickstart** in `README.md`

### Changed
- `skills/build_course_html.py` rewritten as a fully generic builder — reads all course structure from `course.yml`, `module.yml`, and `lesson.md` frontmatter; no hardcoded course data; CLI usage: `python3 build_course_html.py <path/to/course>`; runs all three stages (A, B, C) in sequence
- `skills/build_tumo2026_html.py` deleted — superseded by the generic builder
- `course-generator` agent Stage 6 updated to describe all three sub-stages (A, B, C) and list `<course-id>-course-document.docx` in the output table
- `README.md` overhauled: added version, Course Generator Pipeline table (6 stages), Export Pipeline section, build script usage, and accent/version field guidance
- `accent` and `accent2` fields added to `courses/tumo2026/course.yml` (`#e05a00` / `#5a00e0`) and `courses/guitar-pedal-course-2/course.yml` (`#c0392b` / `#8e44ad`) — colors now documented in manifests rather than being implicit script defaults

## [0.5.2] - 2026-04-16

### Fixed
- `/export-course` skill Stage B: documented two rendering bugs found and fixed during `guitar-pedal-course-2` export:
  1. **Unclosed final time-block** — the closing `</div></div>` for the last `.time-block` in a session plan was never written, causing all subsequent content (takeaways, next-steps, following modules) to render inside the flex row as broken vertical columns. Fix: always append closing tags after the time-block loop, not only before subsequent blocks.
  2. **Bold-label + list collapsing** — pandoc collapses `**Label:**\n- item` (no blank line) into a single paragraph with inline ` - ` separators. Fix: pre-process markdown before pandoc, inserting a blank line between any bold-text line and a directly following list item (`(\*\*[^*]+\*\*:?)\n([-*])` → `\1\n\n\2`).
- `skills/build_course_html.py` updated with both fixes

## [0.5.1] - 2026-04-16

### Changed
- `/export-course` skill Stage B rewritten to describe the custom Python HTML builder approach (replacing pandoc flat output + CSS injection). Stage B now documents the shared visual design system, per-course accent color convention, full semantic component mapping (`lesson-overview`, `objectives`, `env-box`, `materials-box`, `session-plan`, `time-block`, `takeaways`, `next-steps`), and the document-level structure (cover, TOC, module headers, lesson headers). Reference implementation saved at `skills/build_course_html.py`.
- `guitar-pedal-course-2` HTML rebuilt using the new builder — now matches `tumo2026` document style with dark module headers, semantic section boxes, time-stamped session blocks, dark code backgrounds, and accent-colored list markers. Accent color set to `#c0392b` (deep red).

## [0.5.0] - 2026-04-16

### Changed
- `/export-course` skill rewritten as v2.0.0 with a two-stage pipeline (Assemble → Render):
  - **Stage A** writes a persistent `<course-id>-combined.md` directly into the course directory (no longer a throwaway `/tmp/` file) and creates a sibling `assets/` folder containing all local images and SVGs extracted from lessons (references rewritten to `./assets/<filename>`)
  - **Stage A** detects stub/placeholder sections (empty bodies, TBD headings) and injects `- [ ] TODO:` markers plus a summary to-do block at the top of the document
  - Mermaid fenced blocks are now preserved as-is in the combined `.md` (no longer converted to blockquotes or tables) — Mermaid.js renders them in the HTML output
  - **Stage B** is now the only render target: pandoc → `.html` (Python fallback if unavailable); `.docx` output removed
  - HTML post-processing and `<head>` injection unchanged; added task-list checkbox CSS for `- [ ]` items; added `img` max-width rule for assets
  - New `stage` input (`assemble` | `render` | `both`) lets users re-render from an edited `.md` without re-assembling
- `course-generator` agent Stage 6 updated to match new two-stage export pipeline; output table updated to list `combined.md`, `assets/`, and `.html` as separate artifacts

## [0.4.1] - 2026-04-16

### Fixed
- `/export-course` skill (v1.1.0): HTML export now includes a mandatory pandoc post-processing step to fix Mermaid diagram rendering. Pandoc HTML-escapes code block contents (`-->` → `--&gt;`, `"` → `&quot;`, etc.) and wraps Mermaid blocks in a redundant `<code>` tag — both of which cause Mermaid.js to report "Syntax error in text". The fix: strip the inner `<code>`/`</code>` wrapper and unescape all HTML entities in every `<pre class="mermaid">` block before writing the final file. A direct Python fallback path (no pandoc) is also documented, specifying that Mermaid block contents must never be HTML-escaped.

## [0.4.0] - 2026-04-16

### Added
- `/export-course` skill: compiles all lesson content for a course into a single combined document; produces `.docx` via pandoc with auto-generated ToC, or falls back to a self-contained `.html` file with embedded Mermaid.js if pandoc is unavailable
- `course-generator` agent Stage 5: after marketing/resources, iterate over every lesson stub in module order and apply `write-content` rules to populate full body content sequentially
- `course-generator` agent Stage 6: compile all populated lessons into a combined course document using the `export-course` skill; output lands at `courses/<course-id>/<course-id>-course-document.docx`

### Changed
- `course-generator` agent execution rules updated: Stage 5 must complete before Stage 6; Stage 5 lessons are written sequentially (not in parallel) to maintain continuity of voice
- `course-generator` allowed skills expanded to include `write-content` and `export-course`
- `course-generator` output table updated to include fully-written lesson files (Stage 5) and the combined course document (Stage 6)
- `agents/README.md` pipeline description updated to reflect the full 6-stage pipeline
- `skills/README.md` updated to register `/export-course`
- `CLAUDE.md` key workflows table and pipeline section updated

## [0.3.0] - 2026-04-16

### Changed
- `/write-content` skill enhanced with a session design principles step (step 5): learning objectives tied to course goals, minute-by-minute session structure, mandatory formative assessment activities, activity balance requirements (engaging/hands-on/instructional), later-phase variety guidelines, materials list output, and physical environment specification per session

## [0.2.0] - 2026-04-16

### Changed
- `course-generator` agent upgraded from a scaffold-only generator to a full 4-stage autonomous pipeline: research & curriculum sequencing → syllabus & detailed lessons → visual design aids → marketing campaign & online resource guide (parallel)
- `course-generator` inputs expanded: added `format`, `circuits`, `instructor_profile`, and `price_range`; agent now requires `format` as a required input alongside `topic` and `audience`
- `agents/README.md` updated to reflect the course-generator's new pipeline role and expanded `AGENT.md` section schema
- `skills/README.md` updated to register previously undocumented skills: `/create-visual`, `/web-research`, `/write-content`
- Root `README.md` Quickstart table updated to surface the full pipeline workflow and all available skills

## [0.1.0] - 2026-04-09

### Added
- Initial project setup with agents, courses, exercises, and skills structure
- Version field added to all skills
- Tags, repository, and compatibility metadata added to all skills
- MIT License

### Changed
- Repository renamed from `Agentic-Skills-Workshop` to `course-creator`
- Updated repository URLs to reflect rename
- Updated README title to match repository rename
