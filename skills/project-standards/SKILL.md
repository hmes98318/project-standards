---
name: project-standards
description: Inspect a repository and create or update durable, application-scoped development standards and agent instruction routing based on its project structure and user preferences.
---

# Project Standards

## Role

Inspect the repository and create or update its agent-facing development standards.

Use `AGENTS.md` as the canonical instruction and routing layer. Use application scope as the primary boundary for technology-specific rules, keeping repository-wide rules separate from application-specific rules.

When Claude Code support is enabled, use thin `CLAUDE.md` adapters that import the corresponding `AGENTS.md` instead of duplicating instructions.

Support single-application repositories, monorepos, and documentation-only repositories.

## Language Policy

- Always write `AGENTS.md` and files under `<docs-root>/standards/` in en-US.
- Use the language the user is currently using for setup questions and other user-facing interaction unless the user explicitly requests another language.
- Translate question wording, explanations, and interface labels naturally. Do not translate literal values, file paths, identifiers, locale codes, command names, or technology names when doing so would change their meaning.
- Treat English question wording in this skill as decision intent, not text to copy verbatim to the user.
- Project development documentation outside the standards tree defaults to `en-US`.
- Git commit messages default to `en-US`.

## Output Architecture

Use application scope as the primary boundary for development standards.

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

Rules:

- Root `AGENTS.md` defines repository-wide routing, hard constraints, development-documentation policy, instruction precedence, and commit policy.
- Scoped `<application>/AGENTS.md` files route only the standards applicable to their application.
- When Claude Code support is enabled, create a `CLAUDE.md` next to each generated `AGENTS.md` that imports the local `@AGENTS.md`.
- `common/` contains only rules that truly apply across application scopes and technology stacks.
- Language-, framework-, platform-, and tool-specific rules belong to the owning application scope.
- Match a standards directory name to its application directory name when practical.
- Create only the application scopes and standards required by the repository and current requirements.

## Standards Boundary

Files under `<docs-root>/standards/` contain durable, normative development rules. They prescribe how contributors should develop, review, test, secure, and maintain the project; they do not describe the project's current implementation state.

Do not put the following in standards:

- inventories or snapshots of current project structure, capabilities, dependencies, integrations, or other implementation state;
- descriptions of current architecture, topology, configuration values, environments, deployment state, or generated output;
- product, domain, feature, operational, design source-of-truth, reference, or other descriptive project documentation;
- facts copied from source code, configuration, specifications, or existing documentation when referencing the authoritative source is sufficient.

A repository fact belongs in standards only when it expresses a durable rule that should govern future development. Configuration-enforced behavior may be referenced or summarized when it defines contributor requirements.

Keep descriptive and source-of-truth project documentation outside the standards tree. Preserve existing authoritative documentation locations when practical. Standards may reference those sources without duplicating their current contents.

Do not merge non-standard source-of-truth documentation into the nearest canonical standard merely because the subjects are related. This includes design source-of-truth documentation, which must remain separate from `ui.md`; `ui.md` may reference the authoritative design source without absorbing its content.

If authoritative content exists only inside the standards tree but is not itself a development standard, preserve it outside the standards tree before removing or replacing the original file. Preserve an existing suitable location when one exists; when design documentation must move and no suitable location exists, use `<docs-root>/design/` by default. Ask the user when the destination or ownership is ambiguous.

Repository inspection provides context for selecting and writing standards; detected project state is not itself standards content.

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

Rules:

- Keep descriptive and source-of-truth project documentation outside the standards tree, regardless of its subject area.
- Prefer adding a concise section to an existing canonical standard over creating a separate document when the concern does not justify its own file.
- Create a new standards filename only when the user explicitly extends the catalog.

## Workflow

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

Use **update mode** when the repository already contains an agent-routing or development-standards structure serving this purpose, including existing applicable `AGENTS.md` files or a standards tree.

In update mode:

- re-scan the repository;
- read and understand the existing routing and standards before editing;
- compare detected applications, stacks, tooling, and sources of truth with current routing and standards;
- preserve valid user-authored normative rules and project-specific decisions;
- identify descriptive or source-of-truth content that does not belong under `standards/`;
- preserve separate source-of-truth documents instead of folding them into canonical standards;
- do not assume existing files were generated by this skill;
- do not replace unchanged documents merely to match current templates.

If the purpose or ownership of an existing document is ambiguous, ask before moving, merging, replacing, or removing it.

### 3. Resolve user decisions with one contextualized question batch

Infer as much as possible before asking the user. Use repository evidence, existing standards and routing, authoritative project documentation, and decisions already stated in the current conversation. Do not ask the user for information the repository can provide reliably.

Before asking questions, identify unresolved decisions that materially affect the generated standards, routing, document ownership, or long-term project rules. The standard decision categories below are a checklist, not a fixed or exhaustive questionnaire.

Ask an additional repository-specific question only when all of the following are true:

- the decision cannot be inferred reliably from available evidence;
- different reasonable answers would materially change the resulting standards, routing, ownership, or policy; and
- choosing a default without confirmation risks encoding an incorrect long-term rule.

Do not ask exploratory, speculative, preference, or open-ended fishing questions that do not materially affect the output. Do not ask the user to supply information that repository evidence can establish, and do not re-ask a decision already stated clearly in the current conversation.

If no unresolved decisions remain, do not ask a setup question batch. Proceed using confirmed decisions, reliable repository evidence, existing valid choices, and applicable defaults.

When one or more unresolved decisions remain, present them in one compact batch whenever possible. When structured user-input tooling is available, use it. Otherwise, use a concise text format and wait for the user's response before generating or updating standards.

Every question must be self-contained:

- ask a complete question rather than a bare label;
- add one brief sentence explaining what the decision controls or why user input is needed;
- show `Options: <values>` for finite-choice decisions when doing so makes the answer clearer or less ambiguous;
- show `Detected: <value>` when repository evidence helps the user decide;
- show `Current: <value>` in update mode when an existing decision is explicit;
- show `Default: <value>` when a safe default applies;
- show `Required: Yes` when the decision has no safe default and explicit user input is necessary;
- do not invent a default merely to avoid asking for a material product or engineering-policy decision;
- in update mode, preserve an explicit valid current value as the default unless the user asks to reconsider it or the value is no longer applicable;
- if a proposed default differs from an explicit current value, briefly explain why;
- use the shown default when the user leaves the item unanswered;
- use the user's current language for the question, explanation, and labels, while preserving literal technical values where appropriate.

The exact wording and labels should be localized naturally. Do not copy the English examples below verbatim unless English is the appropriate user-facing language.

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

#### Testing policy decisions

Automated-testing policy is an engineering-policy decision, not a fact that can be inferred from the mere presence or absence of existing tests. Existing test files, frameworks, commands, coverage, and CI are evidence about current tooling and practice, but they define future automated-testing obligations only when an authoritative project rule already makes that intent explicit.

For each software application with testable behavior that does not already have an explicit, unambiguous testing policy:

- derive a compact set of candidate test surfaces from the application's actual responsibilities and integrations rather than from a fixed questionnaire;
- ask only about surfaces that actually exist or are clearly relevant to the application;
- group applications or surfaces when the same policy can reasonably apply instead of asking repetitive questions;
- when several surfaces need decisions, present them as one compact testing-policy item or matrix rather than many unrelated top-level questions;
- use repository-specific surface names and short explanations so the user can tell what code or behavior each choice governs;
- define surfaces at meaningful behavior or integration boundaries; do not create a separate policy row for every file, type, component, endpoint, or implementation unit unless the repository explicitly governs testing at that granularity.

Treat the following as separate policy dimensions rather than combining them into one scale:

- **Requirement:** `Required` or `Not required`. This decides whether changes to the surface carry an automated-test obligation.
- **Depth:** when testing is required, use `Targeted`, `Broad`, or `Custom` unless repository-specific choices are clearer.
- **Dependency strategy:** only for integration boundaries where the choice materially affects the standard, use `Shared/external real dependency`, `Ephemeral/local real dependency`, `Test double`, `Mixed`, or `Custom` unless repository-specific choices are clearer.
- **Additional constraints:** ask only when another testing distinction materially affects implementation or maintenance and cannot be inferred reliably.

Interpret the default depth terms consistently:

- `Targeted` — require tests for newly added or materially changed behavior on that surface, regressions fixed by the change, and important failure, boundary, or edge behavior relevant to that change.
- `Broad` — require tests for the surface's significant supported behavior, including normal paths, important boundaries, failure handling, and applicable integration behavior, not only behavior touched by the current change.
- `Custom` — follow the explicit scope or depth defined by the user.

When a change affects a surface marked `Required`, add or update automated tests according to that surface's confirmed depth. A surface marked `Not required` has no standing obligation to add or update dedicated automated tests. It does not prohibit adding tests, require removing existing tests, permit configured tests to be skipped, or prevent the surface from being covered by shared or higher-level tests. It also does not disable build, lint, formatting, type-checking, static analysis, packaging, or other validation required elsewhere.

Prefer asking about behavior, boundaries, and dependency realism over asking the user to choose testing taxonomy. Infer suitable unit, component, integration, contract, or end-to-end test types from the confirmed policy, repository architecture, and established tooling. Ask about specific test types only when that distinction itself would materially change implementation or maintenance.

Do not introduce numeric coverage targets, mandatory test types, exhaustive testing requirements, or stronger dependency realism than the confirmed policy requires.

Potential test surfaces include UI or component behavior, domain or business logic, service or API behavior, persistence and data access, external infrastructure or service integrations, background processing, and end-to-end flows. Treat these as discovery examples, not as a required checklist.

When several surfaces require user decisions and text input is used, present them compactly, for example:

```text
Testing policy

Surface      Requirement                 Depth (if Required)           Dependency strategy (if relevant)
<surface>    Required / Not required     Targeted / Broad / Custom     <when relevant>
<surface>    Required / Not required     Targeted / Broad / Custom     <when relevant>
```

Ask for `Depth` only when `Requirement` is `Required`. Show `Dependency strategy` only for integration boundaries where it is relevant. Mark the testing-policy item `Required: Yes` when no safe default exists.

#### Standard decision categories

Use these standard decision categories only when they are unresolved:

1. Application scopes and names, only when detected boundaries are ambiguous.
2. Documentation root. Default: `docs/`.
3. Language for project development documentation outside `<docs-root>/standards/`. Default: `en-US`.
4. Git commit message language. Default: `en-US`.
5. Claude Code support:
   - if a `CLAUDE.md` already imports `@AGENTS.md`, keep support enabled without asking;
   - if Claude Code evidence exists but no adapter is active, ask whether to enable it. Options: `Yes` / `No`. Default: `Yes`;
   - otherwise, ask whether to generate Claude Code adapters. Options: `Yes` / `No`. Default: `No`.
6. Coding-style authority selection. Default to `Automatic` for all applications. When confirmation is needed, ask once at repository level and let the user specify only application-level overrides.
7. Testing policy for each software application with testable behavior, including which detected surfaces are `Required` or `Not required`, the depth for required surfaces, and dependency strategy only where an integration boundary makes it material. Do not infer this policy solely from current test coverage.
8. Repository-wide hard constraints or application-specific conventions, only when repository evidence indicates that a material rule exists but its intended policy cannot be determined reliably.
9. The authoritative project document, only when multiple conflicting candidates exist.
10. The preservation destination for source-of-truth content that must move out of the standards tree, only when destination or ownership is ambiguous.

In create mode, confirm the development-documentation language and Git commit message language unless the user already stated them in the current conversation. For every software application with testable behavior and no authoritative or user-stated testing policy, require an explicit testing-policy decision. Group applications when the same policy clearly applies, and do not silently derive automated-testing obligations from repository conventions.

In update mode, do not re-ask those language decisions when the current values are explicit and unambiguous. Preserve explicit valid existing choices as current defaults unless the user asks to reconsider them or repository changes make them inapplicable. Apply the same rule to all other existing decisions. Preserve an explicit testing policy as well, but ask when it is missing, ambiguous, or no longer classifies a materially new application responsibility or integration boundary. Ask only about the uncovered surfaces or dimensions rather than reopening the entire testing policy.

After the user answers, ask at most one focused follow-up batch only when the answers introduce or reveal a new material ambiguity that could not reasonably have been identified before the initial batch. If a required testing-policy field remains unanswered, do not infer or default it; use that focused follow-up only for the missing required decisions and do not proceed until they are resolved. Otherwise, proceed without further setup questions.

Do not ask which language to use for `AGENTS.md` or `<docs-root>/standards/**`; they are always en-US.

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

Always create or maintain:

- root `AGENTS.md`;
- `<docs-root>/standards/common/development-guidelines.md`;
- application-specific standards selected only from the canonical catalog and only when they contain substantive rules.

Use the bundled files only as technology-neutral templates:

- `templates/common/development-guidelines.md`
- `templates/root/AGENTS.md`
- `templates/root/scoped-AGENTS.md`
- `templates/root/CLAUDE.md`

Generate standards only from durable normative requirements supported by enforced project configuration, authoritative documentation, established project conventions, selected style authorities, primary documentation, and user answers. Keep descriptive and source-of-truth project documentation outside the standards tree and reference it when needed.

For software applications, write `testing.md` from the confirmed testing policy rather than extrapolating from the current test suite. For each covered surface, record whether automated testing is `Required` or `Not required`; for required surfaces, record the confirmed depth; record dependency strategy only for integration boundaries where it is part of the policy; and state the change obligation that tells agents when tests must be added or updated. Include established test tooling and test-type conventions only where they help execute the confirmed policy.

Keep automated-testing policy separate from broader validation. Build, lint, formatting, type-checking, static analysis, packaging, and similar checks are governed by repository tooling and development guidelines even when a surface is `Not required` for automated testing.

Preserve deliberate `Not required` decisions when they materially constrain future changes; an explicit policy in which all discovered surfaces are `Not required` is itself substantive when it is intended to prevent agents from introducing automated-test requirements. Do not require tests for every component, layer, service, or code path unless the confirmed policy says so, and do not invent coverage percentages, test taxonomies, dependency realism, or stronger testing obligations than the user selected.

When writing Markdown generated or updated by this skill, do not hard-wrap prose to a fixed column width unless repository-enforced tooling explicitly requires it.

This skill must not carry prewritten standards for a specific language, framework, platform, product domain, or project type.

### 6. Generate application-scoped routing

For each non-root application, create or maintain `<application>/AGENTS.md`.

It should contain only:

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
- preserve valid user-authored normative rules and project-specific decisions;
- update routing when applications are added, removed, renamed, or moved;
- normalize application standards to the canonical catalog instead of preserving alternate standards filenames;
- do not normalize non-standard source-of-truth documents into canonical standards;
- remove rules that no longer apply to the owning application;
- preserve explicit `Required` and `Not required` testing classifications, depth, and dependency strategies; when a materially new application responsibility or integration boundary is not covered by the existing testing policy, ask only about the uncovered policy dimensions instead of automatically extending the policy;
- remove duplicated descriptive project state from standards when an authoritative source already exists elsewhere;
- if unique descriptive or source-of-truth content exists only inside standards, preserve it outside the standards tree before removing the original; use an existing appropriate documentation location, or `<docs-root>/design/` as the fallback for design documentation, and ask the user when the destination is ambiguous;
- when moving source-of-truth documentation, preserve its content and update references instead of merging it into a canonical standard;
- never propagate one application's rules into another application;
- consolidate duplicated rules into the narrowest correct shared location;
- do not rewrite unchanged documents merely to match templates;
- do not replace user customizations with generated defaults unless the user explicitly requests it.

If a rule appears common only because multiple applications currently use the same implementation, keep it application-scoped unless it is truly repository-wide.

### 8. Documentation-only repositories

When no software application is present and the repository is primarily documentation:

- treat the repository root, or the independently governed documentation product directory, as one application scope;
- use only the documentation-only canonical standards catalog;
- detect and align with the repository's existing documentation tooling and validation;
- keep standards limited to durable rules relevant to documentation development;
- keep descriptive and source-of-truth documentation outside the standards tree;
- do not invent software-specific standards unrelated to the repository.

The user-selected development-documentation language still applies to normal project documentation. `AGENTS.md` and `<docs-root>/standards/**` remain en-US.

### 9. Validate the generated architecture

Before completion, verify:

- every referenced file exists;
- every application standards filename belongs to the canonical catalog unless the user explicitly extended it;
- every scoped `AGENTS.md` routes only standards relevant to that application;
- standards contain durable normative rules rather than descriptive project state or incidental implementation patterns;
- source-of-truth project documents remain outside the standards tree and standards reference them instead of duplicating or absorbing them;
- design source-of-truth documentation remains separate from `ui.md`; when relocation is necessary and no suitable location exists, `<docs-root>/design/` is used as the fallback;
- when Claude Code support is enabled, every intended `CLAUDE.md` imports the local `@AGENTS.md`;
- no `CLAUDE.md` duplicates canonical `AGENTS.md` instructions or loses user-maintained content;
- root mandatory instructions contain no application-specific language, framework, platform, or product assumptions;
- common standards contain no application-specific requirements unless every application truly shares them;
- no rule is duplicated in common and application-specific documents without deliberate specialization;
- standards do not conflict with enforced formatter, linter, build, test, compiler, or code-generation configuration;
- each software application's `testing.md`, when present, matches the confirmed `Required` and `Not required` surfaces, depth, dependency strategy where relevant, and change obligations, and does not silently strengthen or broaden the testing policy based only on existing tests or tooling;
- automated-testing policy does not disable or replace independently required build, lint, formatting, type-checking, static-analysis, packaging, or other validation;
- Markdown generated or updated by this skill is not hard-wrapped to a fixed column width unless enforced repository tooling requires it;
- documentation-only repositories do not receive unrelated software-specific standards;
- every `AGENTS.md` and standards file is written in en-US;
- development-documentation and commit-message language rules match the user's selected values;
- the final diff is focused and does not modify application source code unless the user explicitly requested it.

## Completion Report

Report concisely:

- create or update mode;
- detected and confirmed application scopes and stacks;
- documentation root;
- development-documentation language;
- Git commit message language;
- Claude Code support status;
- files created, updated, moved, or removed;
- coding-style authorities selected per application;
- confirmed testing policy per software application, including `Required` and `Not required` surfaces, depth, and dependency strategy where relevant;
- source-of-truth content moved out of standards or awaiting a user decision;
- unresolved conflicts or assumptions.
