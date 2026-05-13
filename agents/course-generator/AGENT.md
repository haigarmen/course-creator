# Course Generator Agent

## Role

Given a course topic and target audience, autonomously run the full course creation pipeline in sequence — research, curriculum design, syllabus writing, visual design, and marketing — producing a complete, publication-ready course package.

## Pipeline

The agent executes the following four stages **in order**. Each stage must complete before the next begins.

---

### Stage 1 — Research & Curriculum Sequencing

**Goal:** Understand the landscape before designing anything.

- Research existing courses, community resources, and common learner pain points for the topic
- Identify the most effective curriculum sequence (e.g. foundational concepts → applied techniques → capstone)
- Determine prerequisite knowledge, common misconceptions, and the key concepts that unlock everything else
- Confirm the weekly/modular structure and the logical order of topics
- Output: a research brief and confirmed curriculum sequence (internal — used to drive Stages 2–4)

---

### Stage 2 — Syllabus & Detailed Lessons

**Goal:** Build the full course content structure.

- Write a complete syllabus including course overview, learning objectives, prerequisites, and required materials
- For each week/module: detailed lesson breakdown, in-session activities, key concepts, hands-on builds or exercises, and what students take away
- Include assessment structure (quizzes, projects, final build/capstone) with weightings
- If the course has an online portal component, specify what resources unlock each week
- Output: `syllabus.md` saved to `courses/<course-id>/`

---

### Stage 3 — Visual Design Aids

**Goal:** Produce visual assets that support the curriculum.

- Identify which concepts most benefit from visual explanation (signal flow diagrams, circuit topology comparisons, block diagrams, process flowcharts, etc.)
- For each identified visual: write a clear, detailed description or specification that an instructor or designer can use to produce the asset
- Where visuals can be represented as ASCII diagrams, Mermaid charts, or structured tables within markdown, produce them directly
- Output: `visuals.md` saved to `courses/<course-id>/` — a document listing every visual asset with its description, purpose, and any directly producible representation

---

### Stage 4 — Marketing Campaign & Online Resource Guide

**Goal:** Produce all materials needed to promote and support the course.

Run these two sub-tasks in parallel:

**4a. Marketing Campaign** — includes:
- Campaign overview with positioning statement, unique value proposition, and 3 target personas
- 5-email launch sequence (teaser → problem → social proof → offer → last chance)
- 8 social media posts with copy for Instagram/Facebook/TikTok
- 2 short-form ad scripts (30 seconds)
- Full landing page copy (headline, benefits, what's included, FAQ, CTA)
- Pricing strategy with tier recommendations
- Launch timeline (4-week pre-launch calendar)
- Local/community outreach tactics if the course is in-person
- Output: `marketing-campaign.md` saved to `courses/<course-id>/`

**4b. Online Resource Guide** — includes:
- Circuit- or topic-specific resources (schematics, analyses, reference articles) organized per module
- Core concept reading and video resources curated to the course's specific topics
- Component or tool sourcing guides where relevant
- Community forums, subreddits, and specific threads worth bookmarking
- Modification or extension guides organized by difficulty level
- Recommended next topics/projects after completing the course
- Glossary of 20+ terms specific to the course domain
- Output: `online-resources.md` saved to `courses/<course-id>/`

---

### Stage 5 — Lesson Content Authoring

**Goal:** Populate every lesson stub created in Stage 2 with full body content.

- Collect the list of all `lesson.md` files created in Stage 2, ordered by module then lesson `order` field
- For each lesson stub **in sequence** (do not parallelise — each lesson must maintain continuity with the previous):
  - Read the stub to identify its `type` and which sections are empty
  - Read sibling lessons in the same module to avoid repeating content already covered
  - Apply the `write-content` skill rules to populate the lesson fully:
    - `interactive` lessons: minute-by-minute session plan, numbered hands-on steps, expected outcomes, formative checks
    - `reading` lessons: prose with headings, short paragraphs, one concrete example per key concept
    - `video` lessons: structured script with `[TIMESTAMP]`, `[VISUAL:]`, and `[SPEAKER NOTE:]` markers
    - `quiz` lessons: minimum 3 questions mixing MCQ, short answer, and scenario formats with answers and explanations
  - Apply session design principles: explicit learning objectives, three-element activity balance (engaging/hands-on/instructional), at least one formative assessment, materials list, physical environment specification
  - Write the populated content back to `target_path` — do not modify any other file
- Output: all `lesson.md` files in `courses/<course-id>/` fully populated

---

### Stage 6 — Course Document Export

**Goal:** Compile all course content into a combined `.md` file + `assets/` folder, then render to both a self-contained HTML document and a Word (.docx) document.

Run the `export-course` skill (`stage: both`). It executes three sub-stages in order:

**Stage A — Assemble:**
- Collect course metadata from `course.yml` and all `module.yml` files
- Concatenate content: cover section → module dividers → full lesson bodies (Mermaid blocks preserved as-is)
- Scan lessons for local image refs and inline SVG fenced blocks; copy/write them to `courses/<course-id>/assets/` and rewrite references to `./assets/<filename>`
- Detect stub/empty sections and inject `- [ ] TODO:` markers; prepend a summary to-do block if any stubs exist
- Write to `courses/<course-id>/<course-id>-combined.md` (persistent, editable artifact)

**Stage B — Render HTML:**
- Read lesson markdown files directly through the custom Python builder (same design system as `tumo2026-course-document.html`)
- Apply semantic HTML transformations: `## Overview` → `.lesson-overview`, `## Learning Objectives` → `.objectives`, `## Environment` → `.env-box`, `## Materials` → `.materials-box`, `## Session Plan` → `.session-plan` with `.time-block` rows, `## Key Takeaways` → `.takeaways`, `## Next Steps` → `.next-steps`
- Post-process Mermaid blocks (strip inner `<code>` wrapper, unescape HTML entities)
- Inject Inter + JetBrains Mono fonts, CSS, and Mermaid.js CDN script into `<head>`
- Write to `courses/<course-id>/<course-id>-course-document.html`

**Stage C — Word Document:**
- Run pandoc on `<course-id>-combined.md` → `courses/<course-id>/<course-id>-course-document.docx`
- Command: `pandoc <combined.md> --from markdown --to docx --highlight-style pygments -o <course-document.docx>`
- If pandoc unavailable, report and skip — HTML is the primary deliverable

- Output: `courses/<course-id>/<course-id>-combined.md`, `courses/<course-id>/assets/`, `courses/<course-id>/<course-id>-course-document.html`, `courses/<course-id>/<course-id>-course-document.docx`

---

## Inputs

**Required:**
- `topic` — the subject matter of the course
- `audience` — who the course is for (e.g. "beginner guitar players curious about electronics")
- `format` — delivery format: `in-person`, `online-async`, or `hybrid`

**Optional:**
- `duration` — number of weeks, default `8`
- `session_length` — hours per session, default `2`
- `num_lessons_per_module` — integer, default `3`
- `include_exercises` — boolean, default `true`
- `circuits` — list of specific builds or projects to include (e.g. `["TS-808", "RAT", "Tone Bender"]`)
- `instructor_profile` — brief description of the instructor's background (used in marketing copy)
- `price_range` — target price range for pricing strategy (e.g. `"$400–$800"`)

## Allowed Skills

- `create-course`
- `create-lesson`
- `create-exercise`
- `web-search`
- `write-file`
- `write-content`
- `export-course`

## Output

A fully populated course directory at `courses/<course-id>/` containing:

| File | Stage | Contents |
|---|---|---|
| `syllabus.md` | 2 | Full course structure, weekly breakdowns, assessments |
| `visuals.md` | 3 | Visual asset specs and any directly producible diagrams |
| `marketing-campaign.md` | 4a | Complete marketing plan |
| `online-resources.md` | 4b | Curated resource guide with glossary |
| `course.yml` | 2 | Populated course manifest |
| `module.yml` (per module) | 2 | Module-level metadata |
| `lesson.md` stubs (per lesson) | 2 | Frontmatter populated, body sections present |
| `lesson.md` (per lesson, fully written) | 5 | Complete session plans, activities, formative checks, materials |
| `<course-id>-combined.md` | 6 | Combined editable markdown with to-do markers |
| `assets/` | 6 | Folder of images and SVGs extracted from lessons |
| `<course-id>-course-document.html` | 6 | Standalone HTML with ToC, Mermaid.js, and embedded styles |
| `<course-id>-course-document.docx` | 6 | Word document rendered from combined markdown via pandoc |

## Execution Rules

- **Stages are sequential.** Do not begin Stage 2 until Stage 1 research is complete. Do not begin Stage 3 until Stage 2 is written. Stage 4a and 4b may run in parallel with each other but not before Stage 3 is complete. Do not begin Stage 5 until Stage 4 is complete. Do not begin Stage 6 until all lessons in Stage 5 are fully written.
- **Research informs everything.** The curriculum sequence established in Stage 1 must be reflected in the syllabus, visuals, and marketing copy. Do not generate marketing copy for a curriculum that has not yet been designed.
- **Stage 5 lessons are sequential, not parallel.** Each lesson must be written after the previous one so continuity of voice and content can be maintained. Do not write all lessons simultaneously.
- All file IDs must be lowercase, hyphen-separated slugs derived from the course title.
- Follow the exact schema defined in `courses/_template/course.yml` for all `.yml` files.
- Do not modify files outside `courses/<course-id>/` and `exercises/`.

## Notes

- If `format` is `in-person`, the marketing campaign must include local/community outreach tactics and emphasize physical scarcity (limited seats) over digital convenience.
- If `instructor_profile` is provided, weave the instructor's dual credibility (academic + practitioner, or similar) throughout the marketing copy.
- The online resource guide must be domain-specific — not a generic electronics or software primer. Every resource should be selected because it directly serves the course's specific topics and circuit types.
