---
name: project-standards
description: Inspect a repository and create or update durable, application-scoped development standards and agent instruction routing based on its project structure and user preferences.
metadata:
  version: "0.5.0"
---

# Project Standards

## Role

Inspect the repository and create or update its agent-facing development standards. `AGENTS.md` is the canonical instruction and routing layer, and application scope is the primary boundary for technology-specific rules, kept separate from repository-wide rules. When Claude Code support is enabled, thin `CLAUDE.md` adapters import the corresponding `AGENTS.md` instead of duplicating it. Single-application repositories, monorepos, and documentation-only repositories are supported.

## Language Policy

- Always write `AGENTS.md` and files under `<docs-root>/standards/` in en-US.
- Use the user's current language for setup questions and other interaction unless the user requests another. Translate question wording, explanations, and labels naturally, but leave literal values, file paths, identifiers, locale codes, command names, and technology names untranslated when translating would change their meaning. Treat English question wording in this skill as decision intent, not text to copy verbatim.
- Project development documentation outside the standards tree and Git commit messages default to en-US.

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

- Root `AGENTS.md` defines repository-wide routing, hard constraints, development-documentation rules, instruction precedence, and commit policy. Scoped `<application>/AGENTS.md` files route only the standards applicable to their application.
- `<docs-root>/standards/common/development-guidelines.md` is the fixed repository-wide engineering baseline and must exactly mirror `templates/common/development-guidelines.md` (see step 5). `common/` otherwise holds only rules that truly apply across all application scopes and technology stacks; a rule shared only because applications currently use the same implementation stays application-scoped.
- Language-, framework-, platform-, and tool-specific rules belong to the owning application scope. Match a standards directory name to its application directory name when practical.
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

## Canonical Standards Catalog

Application standards must use the canonical filenames below. Create only files that contain substantive rules for the application. Do not invent alternate filenames for concerns already covered by the catalog.

### Software applications

- `development.md` — application-specific engineering practices, framework and dependency usage rules, build/configuration practices, generated-code policies, and durable implementation constraints.
- `coding-style.md` — language and framework coding style, naming, formatting, comments, and code-structure conventions.
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

## Skill Version Check

Run this first in every task, before any documentation edit, whether the skill was invoked directly or through a repository's `AGENTS.md`:

```text
python <skill-dir>/scripts/update_skill.py --repo <repository-root>
```

`<skill-dir>` is the directory containing this `SKILL.md`; use `python3` or `py -3` where `python` is not Python 3. Pass only `--repo`, plus `--force` to skip the 24-hour lookup interval; the other flags are for testing. Never look up versions with a browser or web-fetch tool, which can return cached pages and cost far more tokens.

The script updates this skill automatically when a newer stable release exists, so never ask for confirmation. It prints one JSON object and never fails the task:

- Always tell the user the version in use by relaying `notice`, translated into the user's language, and `stamp_notice` when present. Do this for failures and cached results (`from_cache`) too, even if the same message was reported earlier.
- If `reread_skill` is true, re-read this `SKILL.md` and use the updated `templates/` and `scripts/` from disk.
- Any status other than `updated`, `current` or `ahead` (for example `check-failed`, `update-failed`, `managed`, `disabled`) means the skill could not be updated. Continue with the installed version.
- If `stamp_status` is `repo-older`, offer update mode. Never rewrite repository files because of the stamp alone.

## Workflow

Ordinary documentation edits follow the project's Development Documentation rules; use this workflow only to create or update project standards and agent routing.

### 1. Inspect the repository

Scan the current working directory. Use `scripts/inspect_project.py` when available, then inspect relevant files directly.

Identify:

- repository layout and likely application boundaries;
- languages, frameworks, manifests, package managers, build systems, linters, formatters, test frameworks, existing test suites, test commands, and CI configuration;
- testable behavior surfaces and integration boundaries for each software application, based on the responsibilities and external resources actually present in the repository;
- existing `AGENTS.md`, `CLAUDE.md`, `.claude/`, standards, and development documentation;
- whether existing `CLAUDE.md` files already import `@AGENTS.md` or contain user-maintained Claude-specific instructions;
- authoritative project documentation, specifications, schemas, configuration, design sources, and other sources of truth;
- whether the repository is documentation-only.

An application boundary is a product, service, deployable, or independently governed development scope. It is not merely a language, package, library, or module.

Treat detected patterns as evidence, not automatically as standards. Promote a pattern to a development rule only when it is enforced, documented, consistently intentional, or confirmed by the user.

### 2. Determine create or update mode

Use **update mode** when the repository already has an agent-routing or development-standards structure serving this purpose, such as applicable `AGENTS.md` files or a standards tree; otherwise use create mode. Do not assume existing files were generated by this skill.

In update mode, re-scan the repository, read the existing routing and standards, compare them with the detected applications, stacks, tooling, and sources of truth, and apply step 7. If the purpose or ownership of an existing document is ambiguous, ask before moving, merging, replacing, or removing it.

### 3. Resolve user decisions with one contextualized question batch

Infer as much as possible before asking: use repository evidence, existing standards and routing, authoritative documentation, and decisions already stated in the conversation. Do not ask for what the repository can establish reliably, and do not re-ask a decision already stated clearly.

Identify the unresolved decisions that materially affect the standards, routing, document ownership, or long-term rules. The standard categories below are a checklist, not a fixed questionnaire. Ask an additional repository-specific question only when the decision cannot be inferred reliably, different reasonable answers would materially change the result, and choosing a default risks encoding an incorrect long-term rule. Do not ask exploratory, speculative, or open-ended questions.

If nothing remains unresolved, skip the question batch and proceed with confirmed decisions, repository evidence, existing valid choices, and defaults. Otherwise present the decisions in one compact batch, using structured user-input tooling when available and a concise text format otherwise, and wait for the response before generating or updating standards.

Every question must be self-contained:

- a complete question, with one brief sentence on what the decision controls or why user input is needed;
- `Options: <values>` for finite choices when it makes the answer clearer;
- `Detected: <value>` when repository evidence helps the user decide;
- `Current: <value>` in update mode when an existing decision is explicit. Keep an explicit valid current value as the default unless the user asks to reconsider it or it no longer applies, and explain briefly if a proposed default differs;
- `Default: <value>` when a safe default applies; it is used when the user leaves the item unanswered. Do not invent a default to avoid asking for a material product or engineering-policy decision;
- `Required: Yes` when there is no safe default and explicit input is necessary.

Example text shape:

```text
Project Standards Setup

1. <Complete question?>
   <One-sentence explanation of what this decision affects.>
   Options: <value> / <value>
   Detected: <value>
   Default: <value>

2. <Complete question?>
   <One-sentence explanation of what this decision affects.>
   Current: <value>
   Default: <same current value unless a change is justified>

Reply with only the items you want to change.
Unanswered items will use their shown defaults. Items marked Required must be answered.
```

#### Code-comment policy

Apply this policy only to software application source code. Exclude development documentation and documentation-only repositories. Existing comment volume or generic "explain why" advice does not establish an explicit policy.

- `Full` — Document module responsibilities and relationships, important types, public interfaces, and nontrivial functions, including private helpers. Explain purpose and relevant inputs, outputs, side effects, and failures; explain business rules, edge cases, design decisions, and complex flows beside the implementation.
- `Concise` — Briefly document public entry-point purposes and relevant contracts; explain non-obvious rules locally. Add internal explanations where intent or behavior remains unclear.
- `None` — Add no optional explanatory comments or docstrings; maintain existing comments.
- `Custom` — Use the user's explicit coverage, detail, and exceptions.

Write the selected policy's name, concrete requirements, and the shared rules below in the application's `coding-style.md`. Route that standard through the applicable `AGENTS.md` as mandatory for source changes.

- Apply coverage to new or materially changed units and fill missing required explanations within those units.
- Use native documentation-comment syntax for contracts and nearby inline comments for implementation reasoning.
- Exclude generated and vendored code from manual additions. Meet license and tooling requirements for comments under every policy, including adding required notices, directives, or documentation comments.

#### Testing policy decisions

Automated-testing policy is an engineering-policy decision, not a fact inferable from the presence or absence of tests. Existing tests, frameworks, commands, coverage, and CI are evidence of current practice; they create future obligations only when an authoritative project rule makes that intent explicit.

For each software application with testable behavior that lacks an explicit, unambiguous testing policy:

- derive a compact set of candidate test surfaces from the application's actual responsibilities and integrations, at meaningful behavior or integration boundaries rather than per file, type, component, or endpoint (unless the repository governs testing at that granularity);
- ask only about surfaces that exist or are clearly relevant, grouping applications or surfaces that can share a policy, and present them as one compact item or matrix with repository-specific surface names and short explanations;
- ask about behavior, boundaries, and dependency realism rather than testing taxonomy. Infer unit, component, integration, contract, or end-to-end tests from the confirmed policy, architecture, and tooling, and ask about test types only when that distinction would materially change implementation or maintenance.

Potential surfaces, as discovery examples rather than a checklist: UI or component behavior, domain or business logic, service or API behavior, persistence and data access, external infrastructure or service integrations, background processing, and end-to-end flows.

Treat these as separate policy dimensions:

- **Requirement:** `Required` or `Not required`: whether changes to the surface carry an automated-test obligation.
- **Depth**, only when Required: `Targeted`, `Broad`, or `Custom`, unless repository-specific choices are clearer.
- **Dependency strategy**, only for integration boundaries where it materially affects the standard: `Shared/external real dependency`, `Ephemeral/local real dependency`, `Test double`, `Mixed`, or `Custom`, unless repository-specific choices are clearer.
- **Additional constraints:** ask only when another testing distinction materially affects implementation or maintenance and cannot be inferred reliably.

Depth terms:

- `Targeted` — require tests for newly added or materially changed behavior on that surface, regressions fixed by the change, and important failure, boundary, or edge behavior relevant to that change.
- `Broad` — require tests for the surface's significant supported behavior, including normal paths, important boundaries, failure handling, and applicable integration behavior, not only behavior touched by the current change.
- `Custom` — follow the explicit scope or depth defined by the user.

When a change affects a `Required` surface, add or update automated tests to the confirmed depth. A `Not required` surface has no standing obligation to add or update dedicated tests; this does not prohibit adding tests, require removing existing ones, permit skipping configured tests, prevent coverage by shared or higher-level tests, or disable build, lint, formatting, type-checking, static analysis, packaging, or other validation required elsewhere. Do not introduce numeric coverage targets, mandatory test types, exhaustive testing requirements, or stronger dependency realism than the confirmed policy requires.

When several surfaces need decisions and text input is used, present them compactly:

```text
Testing policy

Surface      Requirement                 Depth (if Required)           Dependency strategy (if relevant)
<surface>    Required / Not required     Targeted / Broad / Custom     <when relevant>
<surface>    Required / Not required     Targeted / Broad / Custom     <when relevant>
```

Ask for `Depth` only when `Requirement` is `Required`, and show `Dependency strategy` only for integration boundaries where it is relevant. Mark the testing-policy item `Required: Yes` when no safe default exists.

#### Standard decision categories

Use these categories only when they are unresolved:

1. Application scopes and names, only when detected boundaries are ambiguous.
2. Documentation root. Default: `docs/`. This remains required because project standards are always stored under `<docs-root>/standards/`.
3. Language for project development documentation outside `<docs-root>/standards/`. Default: `en-US`.
4. Git commit message language. Default: `en-US`.
5. Claude Code support:
   - if a `CLAUDE.md` already imports `@AGENTS.md`, keep support enabled without asking;
   - if Claude Code evidence exists but no adapter is active, ask whether to enable it. Options: `Yes` / `No`. Default: `Yes`;
   - otherwise, ask whether to generate Claude Code adapters. Options: `Yes` / `No`. Default: `No`.
6. Coding-style authority selection. Default to `Automatic` for all applications. When confirmation is needed, ask once at repository level and let the user specify only application-level overrides.
7. Code-comment policy for software applications. Ask when missing, ambiguous, or the user requests reconsideration. Options: `Full` / `Concise` / `None` / `Custom`. Default: the current explicit policy, otherwise `Full`. Use a shared policy with application overrides.
8. Testing policy for each software application with testable behavior: which detected surfaces are `Required` or `Not required`, the depth for required surfaces, and dependency strategy only where an integration boundary makes it material.
9. Repository-wide hard constraints or application-specific conventions, only when repository evidence indicates that a material rule exists but its intended policy cannot be determined reliably.
10. The authoritative project document, only when multiple conflicting candidates exist.
11. The preservation destination for source-of-truth content that must move out of the standards tree, only when destination or ownership is ambiguous.

In create mode, confirm the development-documentation language and Git commit message language unless the conversation already states them, and require an explicit testing-policy decision for every software application with testable behavior that has no authoritative or user-stated policy. Group applications when the same policy clearly applies, and do not derive testing obligations from repository conventions.

In update mode, do not re-ask explicit, unambiguous existing choices unless the user asks to reconsider them or repository changes make them inapplicable. Preserve an explicit testing policy too, and ask only about the surfaces or dimensions it does not cover, such as a materially new application responsibility or integration boundary, rather than reopening the whole policy.

After the user answers, ask at most one focused follow-up batch for newly revealed material ambiguity or missing required policy details. Resolve required testing-policy fields and any unspecified `Custom` comment requirements before proceeding; do not infer or default them. Otherwise, proceed without further setup questions.

### 4. Select coding-style authorities

For each application:

1. Respect formatter, linter, compiler, and code-generation configuration already enforced by the repository.
2. If the user specifies a coding-style authority, use it unless it conflicts with enforced project configuration; report the conflict instead of silently overriding it.
3. Prefer official framework guidance for framework-specific patterns when it directly applies to the application.
4. For language-level style not covered by higher-priority authorities, prefer a relevant [Google Style Guide](https://google.github.io/styleguide/) when one exists and directly applies to the language.
5. If no suitable Google guide exists, prefer the official language coding/style guide.
6. Verify version-sensitive or unclear behavior against primary documentation for the versions actually used by the project.

Do not copy entire external style guides into project standards. Reference the authority and record only project-relevant additions, exceptions, and high-value rules.

### 5. Generate the minimum useful standards set

Always create or maintain root `AGENTS.md`, `<docs-root>/standards/common/development-guidelines.md`, and the application standards selected from the canonical catalog that hold substantive rules.

Copy `templates/common/development-guidelines.md` verbatim to `<docs-root>/standards/common/development-guidelines.md`, replacing the target whenever it differs. Never summarize, rewrite, omit, reorder, or adapt it, or merge project-specific rules into it, whatever the repository evidence, user answers, or existing conventions; put such rules in the narrowest appropriate non-baseline location.

Use `templates/root/AGENTS.md`, `templates/root/scoped-AGENTS.md`, and `templates/root/CLAUDE.md` as structural templates. In both modes, root `AGENTS.md` must contain the Documentation Skill Prerequisite, Development Documentation, and Commits sections exactly as in the template with placeholders resolved, replacing any older wording even when nothing else in the file changes.

- Resolve `{{SKILL_VERSION}}` to the installed `metadata.version`, producing `<!-- project-standards: X.Y.Z -->` near the top of root `AGENTS.md`. In update mode, refresh the stamp only after the standards match the installed version.
- Resolve `{{DEVELOPMENT_DOCUMENTATION_CREATION_POLICY}}` to `- Do not create new project development documentation unless the current task explicitly requires it.` only for an explicit opt-out; otherwise remove the placeholder without adding a rule.

Generate application-specific standards only from durable normative requirements supported by enforced project configuration, authoritative documentation, established project conventions, selected style authorities, primary documentation, and user answers. State each rule once, as a precise, actionable statement under the topic it governs. Do not carry prewritten standards for a specific language, framework, platform, product domain, or project type beyond the technology-neutral baseline bundled with this skill.

For software applications, write `testing.md` from the confirmed testing policy rather than extrapolating from the current test suite. For each covered surface, record whether automated testing is `Required` or `Not required`; for required surfaces, the confirmed depth; dependency strategy only where it is part of the policy; and the change obligation that tells agents when tests must be added or updated. Include established test tooling and test-type conventions only where they help execute the policy. Preserve deliberate `Not required` decisions that materially constrain future changes; a policy in which every surface is `Not required` is itself substantive when it is meant to keep agents from introducing test requirements.

Do not hard-wrap prose in Markdown generated or updated by this skill unless repository-enforced tooling requires it.

### 6. Generate application-scoped routing

For each non-root application, create or maintain `<application>/AGENTS.md`. It should contain only:

- mandatory standards for that application;
- scope-triggered routing to additional canonical standards when needed.

Do not copy repository-wide hard constraints or instruction precedence into scoped files unless a local specialization is necessary. The root `AGENTS.md` remains authoritative for repository-wide rules.

When Claude Code support is enabled:

- create or maintain a root `CLAUDE.md` and a scoped `<application>/CLAUDE.md` next to each generated scoped `AGENTS.md`;
- use `@AGENTS.md` to import the corresponding file in the same directory;
- if a `CLAUDE.md` contains only `@AGENTS.md`, treat it as a thin adapter;
- if a `CLAUDE.md` contains user-maintained instructions, preserve them; add `@AGENTS.md` only when support is enabled and the import is missing;
- never replace a user-maintained `CLAUDE.md` with the thin adapter unless the user explicitly requests it.

### 7. Update safely

In update mode:

- read every affected standards, routing, and source-of-truth document before editing;
- preserve valid user-authored normative rules, project-specific decisions, and explicit existing choices, including the opt-out, testing classifications, depth, and dependency strategies;
- do not rewrite unchanged documents merely to match templates, or replace user customizations with generated defaults unless the user explicitly requests it. The exceptions are the fixed baseline and the template-defined root `AGENTS.md` sections, which always match the bundled content (step 5);
- edit each affected standard into its final state: fold the change into the relevant existing section, merge overlapping rules, and remove superseded or inapplicable ones, instead of appending new rules or change notes. Consolidate duplicated rules into the narrowest correct shared location, and never propagate one application's rules into another;
- update routing when applications are added, removed, renamed, or moved, and normalize application standards to the canonical catalog instead of keeping alternate filenames;
- remove change history, and descriptive project state that has an authoritative source elsewhere, from standards;
- relocate unique source-of-truth content as the Standards Boundary describes, without folding it into a canonical standard. When an opt-out applies and relocation needs a new document, ask the user before creating it.

### 8. Documentation-only repositories

When no software application is present and the repository is primarily documentation:

- treat the repository root, or the independently governed documentation product directory, as one application scope;
- use only the documentation-only canonical standards catalog, without unrelated software-specific standards;
- detect and align with the repository's existing documentation tooling and validation;
- keep standards limited to durable rules for documentation development.

### 9. Validate the generated architecture

Before completion, verify:

- root `AGENTS.md` and the required project standards exist, with the template's Documentation Skill Prerequisite, Development Documentation, and Commits sections and a version stamp equal to the installed skill version;
- the common baseline exactly matches `templates/common/development-guidelines.md` and contains no project-specific rules;
- every referenced file exists;
- application standards filenames belong to the canonical catalog unless the user extended it, and documentation-only repositories receive no unrelated software-specific standards;
- each scoped `AGENTS.md` routes only standards relevant to its application;
- standards contain durable normative rules, each stated once, rather than descriptive project state or incidental implementation patterns;
- source-of-truth documents, including design documentation separate from `ui.md`, remain outside the standards tree and are referenced rather than duplicated or absorbed;
- standards do not conflict with enforced formatter, linter, build, test, compiler, or code-generation configuration;
- root mandatory instructions contain no application-specific assumptions, common standards contain only rules every application shares, and no rule is duplicated across common and application documents without deliberate specialization;
- when Claude Code support is enabled, every intended `CLAUDE.md` imports the local `@AGENTS.md`, duplicates no `AGENTS.md` instructions, and loses no user-maintained content;
- each software application has its selected code-comment policy in `coding-style.md`, with mandatory routing for source changes;
- each `testing.md`, when present, matches the confirmed surfaces, depth, dependency strategy, and change obligations without strengthening them based on existing tests or tooling, and does not replace independently required build, lint, formatting, type-checking, static-analysis, or packaging validation;
- every `AGENTS.md` and standards file is in en-US, the development-documentation and commit-message languages match the selected values, and generated Markdown is not hard-wrapped unless enforced tooling requires it;
- an opt-out suppresses only the creation of new development documentation: standards and the Development Documentation rules stay in force, no new documents are created unless explicitly required, and no unique source-of-truth content is discarded;
- the final diff is focused and does not modify application source code unless the user explicitly requested it.

## Completion Report

Report concisely:

- the `project-standards` version in use, and the previous version if it was updated during this run;
- create or update mode;
- detected and confirmed application scopes and stacks;
- documentation root, development-documentation language and whether the user opted out of creating new development documentation, Git commit message language, and Claude Code support status;
- files created, updated, moved, or removed;
- selected coding-style authorities and, for software applications, code-comment policies;
- confirmed testing policy per software application, including `Required` and `Not required` surfaces, depth, and dependency strategy where relevant;
- source-of-truth content moved out of standards or awaiting a user decision;
- unresolved conflicts or assumptions.
