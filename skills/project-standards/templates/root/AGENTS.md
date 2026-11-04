# AGENTS.md

<!-- project-standards: {{SKILL_VERSION}} -->

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

Before the first documentation edit in each task, including `AGENTS.md` and `{{STANDARDS_ROOT}}/`, load the installed `project-standards` skill and complete its "Skill Version Check" first. It updates the skill automatically, without asking.

If the skill is not installed, ask the user whether to install it, following the [installation instructions](https://github.com/hmes98318/project-standards#installation), and leave documentation edits pending until it is available.

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

Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for all commit messages: `<type>[(scope)][!]: <description>`.

Write commit messages in `{{COMMIT_MESSAGE_LANGUAGE}}` while keeping Conventional Commits types, scopes, and footer tokens in English.

A commit message records the intent of one change; the diff already shows what changed. Describe only the changes actually being committed (for example, as shown by `git diff --staged`), not the whole task or conversation.

- Type: choose by the primary intent: `feat` new capability, `fix` bug fix, `perf` performance improvement, `refactor` restructuring without behavior change, `style` formatting without logic change, `docs` documentation only, `test` tests only, `build` or `ci` build and pipeline, `chore` other maintenance, `revert` reverting an earlier commit. Use only these types unless repository tooling defines others.
- Scope: add only when it names the one affected application or module; omit it for repository-wide or multi-module changes.
- Description: imperative mood where the language has one, lowercase initial where the language has case, no trailing period, naming the concrete change and its effect, not vague wording such as "update code" or "various improvements". Keep the whole first line, including type and scope, within 72 characters.
- One commit, one logical change. When the pending changes mix unrelated concerns, stage and commit them separately.
- Body: omit it when the description is self-explanatory. Otherwise add one or two sentences on why the change was needed, a non-obvious decision, or an impact on behavior or compatibility. Take reasons from the task or conversation; never invent motivation, impact, or references such as issue numbers. Use bullets only for genuinely separate points, at most three.
- Do not list files, functions, or individual edits, and do not mention accompanying tests, documentation, or formatting unless they are the change. Do not restate the description, repeat a point in different words, or narrate the working process.
- Mark breaking changes with `!` after the type or scope and a `BREAKING CHANGE:` footer that states the impact.
