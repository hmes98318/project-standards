# Standards Contract

Shared definitions for every task that creates or edits project standards or agent routing. Paths such as `templates/` are relative to the skill directory.

## Development Documentation Creation Policy

Project standards (`AGENTS.md` files and `<docs-root>/standards/`) are mandatory and unaffected by any documentation setting. Project development documentation outside the standards tree is governed by the Development Documentation section of the generated root `AGENTS.md`, which defines how it is written and maintained.

Creating new development documentation is allowed by default. Only an explicit opt-out suppresses it, either requested by the user in the current conversation or found as an existing repository decision in update mode. Never infer an opt-out from missing documentation, repository history, code-only conventions, or missing tooling, and never ask whether to opt out. Under an opt-out, create no new development documentation unless the current task explicitly requires it.

The opt-out applies only to creating new documents. It does not disable the Development Documentation rules (including reading and updating existing documentation), permit deleting existing documentation, or apply to standards and `CLAUDE.md` adapters. It also does not permit discarding unique source-of-truth content during standards cleanup; if preserving that content requires a new document, ask the user.

## Output Architecture

```text
AGENTS.md
CLAUDE.md                               # optional; imports @AGENTS.md
<application>/AGENTS.md                 # only when the application is not the repository root
<application>/CLAUDE.md                 # optional; imports @AGENTS.md
<docs-root>/standards/
  common/
    development-guidelines.md
  <application-name>/
    ...only the canonical standards required by that application...
```

- Root `AGENTS.md` defines repository-wide routing, hard constraints, repository-wide baseline exceptions, development-documentation rules, instruction precedence, commit policy, and the verification commands of an application at the repository root. Scoped `<application>/AGENTS.md` files route only the standards applicable to their application and hold that application's baseline exceptions and verification commands.
- `<docs-root>/standards/common/development-guidelines.md` is the fixed repository-wide engineering baseline and must exactly mirror `templates/common/development-guidelines.md` (see Fixed Content). `common/` otherwise holds only rules that truly apply across all application scopes and technology stacks; a rule shared only because applications currently use the same implementation stays application-scoped.
- Language-, framework-, platform-, and tool-specific rules belong to the owning application scope. Match a standards directory name to its application directory name when practical.
- Toolchain configuration, such as formatter, linter, and type-checker configuration files, lives in the application directory where the tools read it, not in the standards tree.
- Create only the application scopes and standards the repository and current requirements need.

## Standards Boundary

Files under `<docs-root>/standards/` contain durable, normative development rules: how contributors should develop, review, test, secure, and maintain the project. They do not describe the project's current state. Do not put in them:

- inventories or snapshots of current structure, capabilities, dependencies, integrations, or other implementation state, and descriptions of current architecture, topology, configuration values, environments, deployment state, or generated output;
- change history, task progress, or per-change notes;
- product, domain, feature, operational, design, reference, or other descriptive project documentation;
- facts copied from code, configuration, specifications, or existing documentation when referencing the authoritative source is enough.

A repository fact belongs in standards only when it expresses a durable rule that governs future development; enforced configuration may be referenced or summarized when it defines contributor requirements. Detected project state informs which standards to write; it is not standards content.

Descriptive and source-of-truth documentation stays outside the standards tree, including in documentation-only repositories, where the documentation itself is the product rather than a standard. Preserve existing authoritative locations when practical, reference them from standards instead of duplicating them, and do not merge them into the nearest canonical standard because the subjects are related. In particular, design source-of-truth documentation stays separate from `ui.md`, which may reference it without absorbing it.

If authoritative content that is not itself a development standard exists only inside the standards tree, preserve it outside before removing or replacing the original file: in an existing suitable location, or in `<docs-root>/design/` for design documentation when none exists. Move the content intact and update references. Change history is not authoritative content: remove it instead of relocating it. Ask the user when the destination or ownership is ambiguous.

## Enforcement Ladder

Agents reliably follow a rule that fails a check, and often skip prose they are only told to read. Place each development rule at the highest level that can hold it:

1. **Tooling** — the formatter, linter, type checker, compiler settings, and tests run by the application's verification commands. A rule a configured tool enforces lives in that tool's configuration, selected as `references/toolchains.md` describes.
2. **`AGENTS.md`** — the verification commands and the few instructions every change in the scope needs, because agents read it on every task.
3. **Standards** — rules that need judgment, such as the code-comment policy, the testing policy, and design conventions no tool checks.

Standards never restate a rule that configured tooling enforces; they name the tool and its configuration instead.

## Canonical Standards Catalog

Application standards must use the canonical filenames below. Create only files that contain substantive rules for the application. Do not invent alternate filenames for concerns already covered by the catalog.

### Software applications

- `development.md` — application-specific engineering practices, framework and dependency usage rules, build/configuration practices, generated-code policies, and durable implementation constraints.
- `coding-style.md` — the formatting, linting, and type-checking toolchain and its configuration files, coding-style authorities, the code-comment policy, naming and code-structure conventions that tooling does not enforce, and the Style rules of an applied toolchain profile, which stay here even where they touch topics that other files own.
- `testing.md` — automated-testing policy, test-surface requirements, testing depth, change obligations, integration dependency strategy, test-writing rules, and test-tooling conventions.
- `security-privacy.md` — security, authentication, authorization, secrets, sensitive data, privacy, permissions, and related safeguards.
- `data.md` — networking, persistence, caching, serialization, migrations, and data-access conventions.
- `ui.md` — UI implementation rules, accessibility, localization implementation, responsive behavior, platform UI conventions, and requirements for following authoritative design documentation.
- `performance.md` — performance, resource usage, profiling, responsiveness, and performance-sensitive implementation rules.

### Documentation-only repositories

- `development.md` — documentation-development workflow and tooling rules.
- `writing-style.md` — writing, structure, terminology, formatting, and documentation-style conventions.
- `testing.md` — linting, link checking, documentation builds, and other validation rules.

Prefer adding a concise section to an existing canonical standard over creating a separate document when the concern does not justify its own file. Create a new standards filename only when the user explicitly extends the catalog.

## Fixed Content

Two pieces of content always match the bundled templates:

- `<docs-root>/standards/common/development-guidelines.md` is a verbatim copy of `templates/common/development-guidelines.md`. Never summarize, rewrite, omit, reorder, or adapt it, or merge project-specific rules into it, whatever the repository evidence, user answers, or existing conventions; put such rules in the narrowest appropriate non-baseline location, and record any replacement of a baseline rule as a Baseline Exception.
- Root `AGENTS.md` contains the Documentation Skill Prerequisite, Development Documentation, and Commits sections exactly as in `templates/root/AGENTS.md` with placeholders resolved, plus the `<!-- project-standards: X.Y.Z -->` version stamp.

The setup workflow brings both, and the stamp, to the installed version (setup workflow step 5). Other edits leave them and the stamp unchanged.

## Baseline Exceptions

Every baseline rule applies to every scope unless a recorded baseline exception replaces it. Projects deviate from the baseline only through these exceptions, never by editing the baseline or by writing a conflicting rule into a standards file.

- Record an exception only when the user explicitly asks to relax or replace a baseline rule. Never infer one from repository evidence, existing code, or conflicting conventions.
- Record it in the Baseline Exceptions section of the `AGENTS.md` for the narrowest scope the user intends: root `AGENTS.md` for the whole repository, otherwise the application's `AGENTS.md`. Ask when the intended scope is unclear.
- Write each exception as one list item on a single line: `- Replaces "<baseline rule, quoted verbatim>": <rule that applies instead>` followed by a one-sentence reason when the user gives one. State the replacement as a precise, actionable rule.
- An exception replaces only the quoted rule within its scope; every other baseline rule still applies. Because an `AGENTS.md` outranks the documents it references in Instruction Precedence, a recorded exception takes precedence over the baseline within its scope.
- Open the section with one sentence stating that each exception replaces the quoted rule of the common development guidelines for this scope. Omit the section when there are no exceptions.

## Writing Rules

- State each rule once, as a precise, actionable statement under the topic it governs.
- Do not hard-wrap prose in Markdown generated or updated by this skill unless repository-enforced tooling requires it.

## Editing Existing Standards

Whenever existing standards, routing, or source-of-truth documents change:

- read every affected standards, routing, and source-of-truth document before editing;
- preserve valid user-authored normative rules, project-specific decisions, and explicit existing choices, including the opt-out, baseline exceptions, testing classifications, depth, and dependency strategies;
- do not rewrite unchanged documents merely to match templates, or replace user customizations with generated defaults unless the user explicitly requests it. The only exception is the Fixed Content, which the setup workflow always brings to the bundled content;
- edit each affected standard into its final state: fold the change into the relevant existing section, merge overlapping rules, and remove superseded or inapplicable ones, instead of appending new rules or change notes. Consolidate duplicated rules into the narrowest correct shared location, and never propagate one application's rules into another;
- remove change history, and descriptive project state that has an authoritative source elsewhere, from standards;
- relocate unique source-of-truth content as the Standards Boundary describes, without folding it into a canonical standard. When an opt-out applies and relocation needs a new document, ask the user before creating it.
