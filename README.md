# Course Creator

A content-agnostic course creator system. Define courses using manifests and templates; use agents and skills to generate, deliver, and grade course content.

## Structure

| Directory | Purpose |
|-----------|---------|
| `courses/` | Course definitions — manifests, modules, lessons |
| `exercises/` | Standalone and lesson-linked exercises |
| `agents/` | Agent system prompts for generation, grading, and tutoring |
| `skills/` | Claude Code skills for scaffolding workflows |

## Quickstart

| Task | Command |
|------|---------|
| Scaffold a new course | `/create-course` |
| Add a lesson to a module | `/create-lesson` |
| Add an exercise | `/create-exercise` |
| Validate a course | `/validate-course` |

## Templates

All templates live in `_template/` subdirectories co-located with their targets:

- Course template: `courses/_template/`
- Module template: `courses/_template/modules/_template/`
- Lesson template: `courses/_template/modules/_template/lessons/_template/`
- Exercise template: `exercises/_template/`

Copy templates — never edit them directly.

## Extending the System

- **New agent**: create `agents/<name>/AGENT.md` and register it in `agents/README.md`
- **New skill**: create `skills/<name>.md` and register it in `skills/README.md`
- **New course**: run `/create-course` or copy `courses/_template/` manually
