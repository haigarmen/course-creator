---
name: create-course
description: Scaffold a new course directory from the _template. Prompts for course id, title, and number of modules.
version: "1.0.0"
tags: [education, course, scaffold, content-authoring]
repository: https://github.com/haigarmen/course-creator
compatibility: [claude-code, claude]
---

1. Ask the user for:
   - `id` — a lowercase, hyphen-separated slug (e.g. `intro-to-python`)
   - `title` — the human-readable course title
   - `num_modules` — how many modules to create (default: 2)

2. Copy `courses/_template/` to `courses/<id>/`.

3. Open `courses/<id>/course.yml` and populate:
   - `id`, `title`
   - The `modules` list with `num_modules` placeholder entries, numbered `01` through `NN`
   - Leave all other fields as-is for the author to fill in

4. For each module, copy `courses/_template/modules/_template/` to
   `courses/<id>/modules/<NN>-module-<NN>/` and update `module.yml` with `order` set to the module number.

5. Confirm the list of created paths to the user.
