# AGENTS.md

## Mandatory Instructions

Before making changes, read and follow:

- `{{COMMON_DEVELOPMENT_GUIDELINES_PATH}}`

Treat it as mandatory repository-wide guidance.

For application-specific changes, also follow the closest applicable `AGENTS.md`:

{{APPLICATION_ROUTING}}

## Hard Constraints

{{HARD_CONSTRAINTS}}

## Documentation Skill Prerequisite

Use [project-standards](https://github.com/hmes98318/project-standards) for development-documentation rules.

Before the first documentation edit in each task, including `AGENTS.md` and `{{STANDARDS_ROOT}}/`:

1. Fetch the [latest release version file (`version.txt`)](https://github.com/hmes98318/project-standards/releases/latest/download/version.txt) and compare its value with the installed `SKILL.md`'s `metadata.version`, trimming whitespace.
2. If the skill or version is missing, or the versions differ, automatically install or update `skills/project-standards/` from the latest stable release, including templates and scripts.
3. Confirm the installed version matches, then read and apply `SKILL.md`.

If any step fails, report the blocker and leave documentation edits pending.

## Development Documentation

{{DEVELOPMENT_DOCUMENTATION_CREATION_POLICY}}
- Store development documentation under `{{DOCS_ROOT}}/`.
- Review relevant documentation before development.
- For new features or changes to documented architecture, design, or behavior, update the relevant documentation first, then implement according to it.
- Prefer updating existing documentation over creating duplicate or conflicting documents.
- Keep documentation concise and consistent with implementation; explain the project without requiring readers to inspect source code.
- Write project development documentation in `{{DEVELOPMENT_DOCUMENTATION_LANGUAGE}}`.
- Keep all `AGENTS.md` files and files under `{{STANDARDS_ROOT}}/` in en-US.

## Instruction Precedence

Follow instructions in this order:

1. Explicit task requirements.
2. The closest applicable `AGENTS.md`.
3. This root `AGENTS.md`.
4. Documents referenced by the applicable `AGENTS.md`.
5. Existing implementation patterns that do not conflict with the above.

Scoped `AGENTS.md` files may specialize local rules but must not weaken repository-wide hard constraints or the Documentation Skill Prerequisite.

## Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all commit messages.

Write commit messages in `{{COMMIT_MESSAGE_LANGUAGE}}` while keeping Conventional Commits types and scopes in English.
