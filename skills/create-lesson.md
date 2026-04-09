---
name: create-lesson
description: Add a new lesson stub to a specific module within an existing course.
version: "1.0.0"
tags: [education, lesson, content-authoring, module]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Ask the user for:
   - `course_id` — the course to add the lesson to
   - `module_id` — the module to add the lesson to
   - `title` — the lesson title
   - `order` — the lesson's position within the module
   - `type` — lesson type: `reading`, `video`, `interactive`, or `quiz` (default: `reading`)

2. Derive a slug from the title (lowercase, hyphens, no special characters).

3. Copy `courses/_template/modules/_template/lessons/_template/lesson.md` to
   `courses/<course_id>/modules/<module_path>/lessons/<NN>-<slug>/lesson.md`.

4. Populate the frontmatter: `id` (slug), `title`, `module` (module_id), `order`, `type`.

5. Append the new lesson entry to `module.yml` under the `lessons` list.

6. Confirm the created path to the user.
