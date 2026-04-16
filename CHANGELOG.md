# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
