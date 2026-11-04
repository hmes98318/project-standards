# Project Standards

**English** · [繁體中文](docs/README_zh-TW.md)

`project-standards` is an [Agent Skill](https://agentskills.io/) for creating and managing a project's development standards and guidelines.

## Installation

### Skills CLI (`npx skills`)

```bash
npx skills@latest add hmes98318/project-standards
```

### Claude Code

```bash
/plugin marketplace add hmes98318/project-standards
/plugin install project-standards@project-standards
```

### Codex

```bash
codex plugin marketplace add hmes98318/project-standards
codex plugin add project-standards@project-standards
```

## Usage

In the repository where you want to create or update standards, ask the agent:

```text
Use project-standards SKILL to create or update the development standards for this repository.
```

The skill reads the repository first, then asks one compact batch of questions for decisions it cannot infer. Unanswered items use their shown defaults.

## What It Generates

```text
AGENTS.md                            # repository-wide rules and routing
CLAUDE.md                            # optional; imports AGENTS.md
<application>/AGENTS.md              # when the application is not the repository root
docs/standards/
  common/development-guidelines.md   # fixed repository-wide baseline
  <application>/                     # only the standards that application needs
```

Application standards use fixed filenames, and a file is created only when it has substantive rules to hold:

- **Software applications:** `development.md`, `coding-style.md`, `testing.md`, `security-privacy.md`, `data.md`, `ui.md`, `performance.md`
- **Documentation-only repositories:** `development.md`, `writing-style.md`, `testing.md`

## Principles

- **Application scope is the boundary.** Language-, framework-, and tooling-specific rules belong to the application that owns them, so applications in a monorepo do not leak rules into each other.
- **Standards hold durable rules, not project state.** Current architecture, module layout, deployment state, and design specifications stay in their own source-of-truth documents. Standards reference them instead of copying them.
- **Development documentation explains the system as it is.** Generated `AGENTS.md` rules direct agents to keep documentation a coherent technical explanation of the current design, revised in place instead of appended with change records.
- **`AGENTS.md` routes; standards carry the detail.** Root instructions stay short as the project grows.
- **Existing tooling wins.** Enforced formatter, linter, and compiler configuration comes first. Without one, the skill follows framework guidance, then the Google Style Guide, then the official language style guide.
- **Updates preserve valid decisions.** In a repository that already has standards, the skill re-scans, keeps valid user-written rules, and does not assume existing files came from this skill or rewrite documents that need no change.

## Settings

The skill asks only about settings it cannot infer from the repository.

| Setting | Default |
| --- | --- |
| Documentation root | `docs/` |
| Language of development documentation | `en-US` |
| Git commit message language | `en-US` |
| Claude Code `CLAUDE.md` adapters | `No` (kept if already in use) |
| Coding style | `Automatic` per application, overridable |
| [Code-comment policy](skills/project-standards/SKILL.md#code-comment-policy) | `Full` (or `Concise`, `None`, `Custom`) |
| Testing policy | none; asked for each software application unless already defined |

`AGENTS.md` and standards files are always written in `en-US`. New development documentation may be created by default; ask explicitly if you do not want any. That opt-out never disables the standards themselves or the rules for existing documentation.

## Staying Up to Date

Generated `AGENTS.md` files tell agents to load the skill before documentation edits. In each task, the skill checks for a newer stable release (looked up at most once every 24 hours), updates itself without asking, and tells you which version is in use. If the skill is not installed, the agent asks before installing it.

The check is a Python 3 script that uses only the standard library, and a failed check never blocks the task. Skills installed through a plugin or a git checkout are not replaced in place; update them with the plugin manager or `git`. Set `PROJECT_STANDARDS_NO_UPDATE` to any non-empty value to disable the check.

## License

[MIT](./LICENSE) License.
