# Usage

The skill is used by asking the agent, inside the target repository, to create or update its standards:

```text
Use project-standards SKILL to create or update the development standards for this repository.
```

The skill first reads the repository: its manifests and source layout, any existing standards and `AGENTS.md` files, and the formatter, linter, and compiler configuration in use. It then asks one compact batch of questions about the decisions it cannot infer from that evidence. Items left unanswered take the defaults shown with each question.

## Creating and Updating Standards

A repository without standards is set up in create mode, which writes the structure described in [Generated Files](generated-files.md). In a repository that already has standards the skill works in update mode. It re-scans the repository, keeps valid rules and explicit earlier decisions, and neither assumes that existing files came from the skill nor rewrites documents that need no change. Existing standards usually record choices a team made deliberately, so an update that regenerated them would discard that work.

## Changing Individual Rules

A single rule is changed by asking for it directly, for example "add a rule to the web app's testing standard that ...". The skill places the rule in the standard that owns the topic without repeating the setup questions, and switches to the full workflow only when the change requires it, such as adding an application. When a tool the application already configures can enforce the rule, the skill offers to enable it in that tool instead of writing prose, as [Design Principles](design-principles.md#tooling-before-prose) explains.

## Settings

The skill asks only about settings it cannot infer from the repository.

| Setting | Default |
| --- | --- |
| Documentation root | `docs/` |
| Language of development documentation | `en-US` |
| Git commit message language | `en-US` |
| Claude Code `CLAUDE.md` adapters | `No` (kept if already in use) |
| Toolchain profile | `Apply` in create mode, `Skip` in update mode |
| Coding style | `Recommended` where a toolchain profile exists, otherwise `Automatic`; overridable per application |
| [Code-comment policy](../skills/project-standards/references/setup-workflow.md#code-comment-policy) | `Full` (or `Concise`, `None`, `Custom`) |
| Testing policy | none; asked for each software application unless already defined |

`AGENTS.md` and the standards files are always written in `en-US`; the language setting applies to other development documentation. New development documentation may be created by default. An explicit request not to create it suppresses only new documents: it never disables the standards themselves or the rules for maintaining existing documentation.

## Keeping the Skill Current

Generated `AGENTS.md` files tell agents to load the skill before editing documentation, so standards are always changed under the current rules. In each task the skill checks for a newer stable release, looking it up at most once every 24 hours, updates itself without asking, and reports which version is in use. If the skill is not installed, the agent asks before installing it. The root `AGENTS.md` carries a version stamp; when it is older than the installed skill, the skill offers to run update mode and never rewrites files because of the stamp alone.

The check is a Python 3 script that uses only the standard library, and a failed check never blocks the task. A skill installed through a plugin or a git checkout is not replaced in place and must be updated with the plugin manager or `git`. Setting `PROJECT_STANDARDS_NO_UPDATE` to any non-empty value disables the check.
