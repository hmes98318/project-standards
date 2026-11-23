# Project Standards

**English** · [繁體中文](docs/README_zh-TW.md)

`project-standards` is an [Agent Skill](https://agentskills.io/) that creates and maintains a repository's development standards and the `AGENTS.md` files that route coding agents to them.

It reads the repository, asks only about decisions it cannot infer, and writes standards scoped to each application, so the applications of a monorepo do not inherit each other's rules. For languages with a bundled toolchain profile it can also set up the formatter, linter, type checker, and test framework, so that tools rather than prose enforce the rules.

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

## Documentation

- [Usage](docs/usage.md): creating, updating, and editing standards, the settings the skill asks about, and how the skill stays current.
- [Generated files](docs/generated-files.md): the files the skill writes and what each one holds.
- [Toolchain profiles](docs/toolchain-profiles.md): the bundled formatter, linter, type checker, and test framework setups.
- [Design principles](docs/design-principles.md): why the standards are structured the way they are.

## License

[MIT](./LICENSE) License.
