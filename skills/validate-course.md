---
name: validate-course
description: Validate a course manifest and directory structure for completeness and consistency.
version: "1.0.0"
tags: [education, validation, course, quality]
repository: https://github.com/haigarmen/agentic-skills-workshop
compatibility: [claude-code, claude]
---

1. Ask the user for the `course_id` to validate.

2. Read `courses/<course_id>/course.yml`. Fail immediately if the file does not exist.

3. For each entry in the `modules` list:
   - Verify the `path` directory exists under `courses/<course_id>/`
   - Verify `module.yml` is present in that directory
   - For each lesson listed in `module.yml`, verify the `lesson.md` file exists at the given path

4. Check that all `id` fields are unique within their scope (course-level, module-level, lesson-level).

5. For each `lesson.md`, verify that all required frontmatter keys are present:
   `id`, `title`, `module`, `order`, `type`, `estimated_minutes`

6. Report:
   - **Pass / Fail** summary
   - List of missing files (if any)
   - List of frontmatter issues (if any)
   - List of duplicate IDs (if any)
