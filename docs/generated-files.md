# Generated Files

The skill writes agent routing at the repository root and the standards under the documentation root, `docs/` by default:

```text
AGENTS.md                            # repository-wide rules and routing
CLAUDE.md                            # optional; imports AGENTS.md
<application>/AGENTS.md              # when the application is not the repository root
docs/standards/
  common/development-guidelines.md   # fixed repository-wide baseline
  <application>/                     # only the standards that application needs
<application>/<tool configs>         # formatter, linter, and type-checker configuration
```

## Agent Routing

`AGENTS.md` is the canonical instruction layer, because agents read it on every task. The root file holds the repository-wide hard constraints, the development-documentation rules, instruction precedence, and the commit policy, and it routes the agent to the standards that apply. It also lists the commands that verify a change when the repository root is itself the application. When an application is not the repository root, its own `AGENTS.md` routes only the standards of that application and holds that application's verification commands and baseline exceptions. Keeping the files short lets them stay readable as the project grows, with the detail in the standards they point to.

With Claude Code support enabled, each `CLAUDE.md` is a thin adapter that imports the `AGENTS.md` beside it instead of repeating its content, so the instructions exist once.

## Fixed Baseline

`common/development-guidelines.md` is the repository-wide engineering baseline. It is always identical to the copy bundled with the skill and is replaced on every setup run, which keeps the baseline comparable across repositories. To relax or replace one of its rules, ask for an exception. The skill records it in the `AGENTS.md` of the repository or of one application, where it takes precedence over the baseline for that scope; the baseline file itself is never edited.

## Application Standards

Each application gets only the standards that hold substantive rules, under fixed filenames so that routing and later edits can find the document that owns a topic. A concern that does not justify its own file is added to an existing one instead.

For software applications:

- `development.md`: engineering practices, framework and dependency rules, build and configuration practices, and implementation constraints.
- `coding-style.md`: the formatting, linting, and type-checking toolchain, the style authority, the code-comment policy, and the conventions tools cannot enforce.
- `testing.md`: the testing policy, including the required surfaces, depth, change obligations, and test-writing rules.
- `security-privacy.md`: security, authentication, secrets, sensitive data, and privacy safeguards.
- `data.md`: networking, persistence, caching, serialization, and migrations.
- `ui.md`: UI implementation rules, accessibility, and localization.
- `performance.md`: performance, resource usage, and responsiveness rules.

For documentation-only repositories:

- `development.md`: the documentation workflow and tooling.
- `writing-style.md`: writing, structure, terminology, and formatting conventions.
- `testing.md`: linting, link checking, documentation builds, and other validation.

Standards contain durable rules only. Descriptions of the current architecture, change history, and other project documentation stay in their own source-of-truth documents, which the standards reference instead of copying.
