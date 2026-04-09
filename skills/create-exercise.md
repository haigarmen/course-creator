---
name: create-exercise
description: Add a new exercise from the template, optionally linking it to a lesson.
version: "1.0.0"
tags: [education, exercise, content-authoring, practice]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Ask the user for:
   - `id` — a lowercase, hyphen-separated slug (e.g. `build-a-calculator`)
   - `title` — the human-readable exercise title
   - `difficulty` — `beginner`, `intermediate`, or `advanced` (default: `beginner`)
   - `linked_lesson` — the lesson id this exercise accompanies (optional)

2. Copy `exercises/_template/` to `exercises/<id>/`.

3. Populate the frontmatter in `exercises/<id>/exercise.md`:
   - `id`, `title`, `difficulty`
   - `linked_lesson` (leave blank if not provided)

4. If `linked_lesson` was provided:
   - Locate the corresponding `module.yml`
   - Append the exercise reference to its `exercises` list

5. Confirm the created path to the user.
