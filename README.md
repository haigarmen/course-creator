# Course Creator

**v0.6.0** — A content-agnostic course creation system. Define courses using YAML manifests and markdown templates; use agents and skills to generate, deliver, export, and grade course content.

## Structure

| Directory | Purpose |
|-----------|---------|
| `courses/` | Course definitions — manifests, modules, lessons, and exported documents |
| `exercises/` | Standalone and lesson-linked exercises |
| `agents/` | Agent system prompts for autonomous multi-step pipelines |
| `skills/` | Claude Code skills for user-invoked workflows |

## Quickstart

| Task | Command |
|------|---------|
| Generate a complete course (research → syllabus → visuals → marketing → lessons → export) | Run the `course-generator` agent |
| Scaffold a new course directory | `/create-course` |
| Add a lesson to a module | `/create-lesson` |
| Add an exercise | `/create-exercise` |
| Validate a course for missing files or broken references | `/validate-course` |
| Generate a visual asset spec or diagram | `/create-visual` |
| Research a topic | `/web-research` |
| Write full lesson content into stubs | `/write-content` |
| Compile all lessons to HTML + Word document | `/export-course` |

## Course Generator Pipeline

The `course-generator` agent runs six sequential stages:

| Stage | Goal | Output |
|-------|------|--------|
| 1 — Research | Landscape analysis, curriculum sequencing, pain points | Research brief |
| 2 — Syllabus & Lessons | Full course structure, module YAML, lesson stubs | `syllabus.md`, `course.yml`, `module.yml`, `lesson.md` stubs |
| 3 — Visual Design | Visual asset specs and directly producible diagrams | `visuals.md` |
| 4a — Marketing | Email sequence, social posts, landing page, pricing | `marketing-campaign.md` |
| 4b — Resources | Curated readings, tools, glossary (runs parallel with 4a) | `online-resources.md` |
| 5 — Content Authoring | Populate every lesson stub in sequence | Fully written `lesson.md` files |
| 6 — Export | Assemble + render HTML + render Word doc | `combined.md`, `assets/`, `.html`, `.docx` |

## Export Pipeline

`/export-course` runs three stages — all three always execute in order:

```
Stage A — Assemble    →  <course-id>-combined.md  +  assets/
Stage B — Render HTML →  <course-id>-course-document.html
Stage C — Word Doc    →  <course-id>-course-document.docx
```

All three artifacts land in `courses/<course-id>/`. The `.md` is kept as an editable artifact — re-run `stage: render` or `stage: docx` after manual edits.

**Build script:** `skills/build_course_html.py` — a single generic builder that reads all course structure from `course.yml`, `module.yml`, and `lesson.md` frontmatter. No hardcoded course data.

```bash
python3 skills/build_course_html.py ../../courses/<course-id>
```

Per-course accent colors are set via `accent` and `accent2` fields in `course.yml`. Course version numbers (from the `version` field in `course.yml`) are embedded in the HTML cover and combined markdown.

## Templates

All templates live in `_template/` subdirectories co-located with their targets:

- Course: `courses/_template/`
- Module: `courses/_template/modules/_template/`
- Lesson: `courses/_template/modules/_template/lessons/_template/`
- Exercise: `exercises/_template/`

Copy templates — never edit them directly.

## Extending the System

- **New agent**: create `agents/<name>/AGENT.md` and register it in `agents/README.md`
- **New skill**: create `skills/<name>.md` and register it in `skills/README.md` and the Quickstart table above
- **New course**: run `/create-course` or copy `courses/_template/` manually; set `accent` and `accent2` in `course.yml`
