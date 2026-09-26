# AGENTS.md

## Mandatory Instructions

Before making changes, read and follow:

- `{{COMMON_DEVELOPMENT_GUIDELINES_PATH}}`

Treat it as mandatory repository-wide guidance.

For application-specific changes, also follow the closest applicable `AGENTS.md`:

{{APPLICATION_ROUTING}}

## Hard Constraints

{{HARD_CONSTRAINTS}}

## Development Documentation

{{DEVELOPMENT_DOCUMENTATION_CREATION_POLICY}}
- Store development documentation under `{{DOCS_ROOT}}/`.
- Review relevant documentation before development.
- For new features or changes to documented architecture, design, or behavior, update the relevant documentation first, then implement according to it.
- Prefer updating existing documentation over creating duplicate or conflicting documents.
- Keep documentation consistent with the current implementation, concise, and focused on information needed for development and maintenance.
- Write project development documentation in `{{DEVELOPMENT_DOCUMENTATION_LANGUAGE}}`.
- Keep all `AGENTS.md` files and files under `{{STANDARDS_ROOT}}/` in en-US.

## Instruction Precedence

Follow instructions in this order:

1. Explicit task requirements.
2. The closest applicable `AGENTS.md`.
3. This root `AGENTS.md`.
4. Documents referenced by the applicable `AGENTS.md`.
5. Existing implementation patterns that do not conflict with the above.

Scoped `AGENTS.md` files may specialize local rules but must not weaken repository-wide hard constraints.

## Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all commit messages.

Write commit messages in `{{COMMIT_MESSAGE_LANGUAGE}}` while keeping Conventional Commits types and scopes in English.
