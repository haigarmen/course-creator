---
name: create-visual
description: Produce a diagram, schematic, or visual asset for a lesson or course, in Mermaid, SVG, or ASCII, matched to the course's visual language.
version: "1.0.0"
tags: [education, design, diagram, visual, content-authoring]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Accept inputs:
   - `course_id` — course this visual belongs to
   - `visual_type` — `diagram`, `schematic`, `flowchart`, `sequence`, `comparison`, `infographic`, or `illustration`
   - `concept` — what to visualise, in plain language
   - `visual_language_profile` — abstraction level, labelling style, and visual weight derived from `course.yml`
   - `format` — `mermaid`, `svg`, or `ascii`
   - `lesson_context` (optional) — relevant excerpt or summary from the target `lesson.md`
   - `research` (optional) — domain facts to draw from

2. Derive a `concept-slug` from the concept string (lowercase, hyphens).

3. Produce the visual in the requested format:

   **Mermaid**
   - Open with a `%%` comment: `%% concept: <concept> | course: <course_id>`
   - Choose the diagram type that best fits `visual_type` (flowchart, sequenceDiagram, classDiagram, erDiagram, block-beta, quadrantChart)
   - Label every node — no unlabelled elements
   - Use consistent arrow/edge styles throughout
   - Output as a fenced ` ```mermaid ` code block

   **SVG**
   - Self-contained: inline all styles, no `<image>` tags referencing external files
   - Normalise to an `800×500` viewBox (or `800×800` for square layouts)
   - Include a `<title>` element with the concept name for accessibility
   - Use `<g>` groups with descriptive `id` attributes for each logical section

   **ASCII**
   - Use `+`, `-`, `|`, `>`, `<`, `^`, `v` and Unicode box-drawing characters (`─`, `│`, `┌`, `┐`, `└`, `┘`, `├`, `┤`, `┬`, `┴`, `┼`)
   - Align all columns to a grid; pad labels uniformly
   - Wrap in a fenced ` ```text ` code block

4. Validate the output:
   - Every element depicted must correspond to a concept mentioned in `lesson_context` or `research`
   - No element is left unlabelled
   - Arrow directions are semantically correct (e.g. data flow arrows point in the direction data travels)

5. Derive suggested alt-text: one sentence describing what the visual shows and what relationship or process it illustrates.

6. Return:
   - The visual output (fenced code block or SVG)
   - Format used
   - One-line description of what is depicted
   - Suggested alt-text
