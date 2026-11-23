---
name: project-standards
description: Inspect a repository and create or update durable, application-scoped development standards and agent instruction routing. Also load before editing AGENTS.md, files under the standards tree, or development documentation in a repository whose AGENTS.md requires project-standards.
metadata:
  version: "0.5.0"
---

# Project Standards

## Role

Create, update, and maintain the repository's agent-facing development standards and agent routing. `AGENTS.md` is the canonical instruction and routing layer, and application scope is the primary boundary for technology-specific rules, kept separate from repository-wide rules. When Claude Code support is enabled, thin `CLAUDE.md` adapters import the corresponding `AGENTS.md` instead of duplicating it. Single-application repositories, monorepos, and documentation-only repositories are supported.

## Language Policy

- Always write `AGENTS.md` and files under `<docs-root>/standards/` in en-US.
- Use the user's current language for setup questions and other interaction unless the user requests another. Translate question wording, explanations, and labels naturally, but leave literal values, file paths, identifiers, locale codes, command names, and technology names untranslated when translating would change their meaning. Treat English question wording in this skill as decision intent, not text to copy verbatim.
- Project development documentation outside the standards tree and Git commit messages default to en-US.

## Skill Version Check

Run this first in every task, before any documentation edit, whether the skill was invoked directly or through a repository's `AGENTS.md`:

```text
python <skill-dir>/scripts/update_skill.py --repo <repository-root>
```

`<skill-dir>` is the directory containing this `SKILL.md`; use `python3` or `py -3` where `python` is not Python 3. Pass only `--repo`, plus `--force` to skip the 24-hour lookup interval; the other flags are for testing. Never look up versions with a browser or web-fetch tool, which can return cached pages and cost far more tokens.

The script updates this skill automatically when a newer stable release exists, so never ask for confirmation. It prints one JSON object and never fails the task:

- Always tell the user the version in use by relaying `notice`, translated into the user's language, and `stamp_notice` when present. Do this for failures and cached results (`from_cache`) too, even if the same message was reported earlier.
- If `reread_skill` is true, re-read this `SKILL.md` and use the updated `references/`, `templates/`, and `scripts/` from disk.
- Any status other than `updated`, `current` or `ahead` (for example `check-failed`, `update-failed`, `managed`, `disabled`) means the skill could not be updated. Continue with the installed version.
- If `stamp_status` is `repo-older`, offer to run the setup workflow in update mode. Never rewrite repository files because of the stamp alone.

## Task Routing

Run the Skill Version Check first, then follow the first route below that matches the task, and read only the references it names. Paths such as `references/`, `templates/`, and `scripts/` are relative to the skill directory.

- **Create or update project standards and agent routing** — set up standards in a repository that has none; cover an application that has no standards or routing yet, even when the request is phrased as a single rule for it; remove, rename, or move application scopes; bring existing standards up to date with the repository or the installed skill version; or change repository-level settings: read `references/standards-contract.md`, then follow `references/setup-workflow.md` to completion.
- **Edit an existing standard, `AGENTS.md` routing, or an application's toolchain** — add, change, or remove specific rules, or a formatter, linter, or type checker, in a repository that already has standards: read `references/standards-contract.md`, then follow `references/editing-standards.md`. It says when to switch to the setup workflow.
- **Edit other development documentation** — documentation outside `AGENTS.md` files and the standards tree: no further reference is needed. Follow the Development Documentation section of the repository's root `AGENTS.md`.

When unsure whether a task edits standards or other documentation, read `references/standards-contract.md`: its Standards Boundary decides.
