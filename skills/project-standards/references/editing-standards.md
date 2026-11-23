# Editing Standards

Make a targeted change to existing project standards or `AGENTS.md` routing: add, change, or remove a rule the user states, or correct a standard. Read `references/standards-contract.md` first; this procedure applies it. Paths such as `references/` are relative to the skill directory.

## When to use the setup workflow instead

Switch to `references/setup-workflow.md` when the task matches the first route in `SKILL.md`, because it needs the repository re-inspected or a repository-level decision revisited:

- the repository has no root `AGENTS.md` or standards tree yet;
- the change concerns an application that has no standards or routing yet, even when it is phrased as a single rule for that application;
- an application scope is removed, renamed, or moved, or routing no longer matches the repository's applications;
- existing standards must be brought up to date with the repository or the installed skill version, for example after the version check reports `repo-older` and the user accepts update mode;
- the documentation root, development-documentation language, commit-message language, or Claude Code support changes.

To add, replace, or remove an application's formatter, linter, or type checker, such as applying a toolchain profile to an existing application, or to switch its profile variant between `recommended` and `google`, follow `references/toolchains.md` for that application only, then update its Verification commands in `AGENTS.md` and the toolchain, variant, and Style rules in its `coding-style.md`. Switching the variant replaces the configuration generated from the previous variant's templates, and its Style rules, as Choosing the toolchain for each concern in `references/toolchains.md` describes; existing tooling that the user maintained stays.

To change a code-comment or testing policy, read the Code-comment policy or Testing policy decisions section of `references/setup-workflow.md` for the policy terms, then apply only the decision the user stated.

## Procedure

1. Classify the content. Apply the Standards Boundary: descriptive project state, change history, and source-of-truth documentation do not belong in standards. If the requested content is descriptive, do not add it to standards and do not write it anywhere else unasked. Tell the user why. If an authoritative source already records it, such as a manifest, configuration, or existing documentation, name that source instead of duplicating it. Otherwise, propose where it belongs in development documentation and wait for the user's decision.
2. Prefer enforcement. Apply the Enforcement Ladder: when a tool the application already configures has a built-in rule or option that enforces the request, offer to enable it in that tool's configuration instead of writing prose, and wait for the user's decision. With approval, enable it (when the file came from a toolchain profile template, say that a later variant switch regenerates it and the rule must then be re-applied), run the application's `verify` command, and report any failures in existing code without changing the code; standards then need no prose rule unless judgment remains. Otherwise continue with a written rule.
3. Find the owning document. Choose the narrowest correct scope: application-scoped unless the rule truly applies across all applications and technology stacks, and never the fixed baseline. Never edit the baseline itself: it is Fixed Content maintained by this skill and replaced on every setup run. When the user asks to relax, replace, or remove a baseline rule, record a Baseline Exception as the standards contract describes, in the `AGENTS.md` of the scope the user intends, and ask when that scope is unclear. When the user asks to add a rule to the baseline, place it in the narrowest appropriate non-baseline location instead. Choose the canonical catalog file that covers the concern, and locate it through the applicable `AGENTS.md` routing.
4. Check for conflicts. Compare the rule with enforced formatter, linter, build, test, compiler, and code-generation configuration and with existing rules in the same scope and in `common/`. Report a conflict with enforced configuration instead of silently overriding it.
5. Edit. Apply Editing Existing Standards and the Writing Rules: fold the rule into the section it governs, merge or remove the rules it overlaps or supersedes, and add no change notes. Prefer a section in an existing canonical file; create a new canonical file only when the concern justifies one. Record the rule with the scope and strength the user stated: precise wording is expected, but do not add requirements, enforcement, or assertions the user did not ask for. When the user's intent is ambiguous, ask.
6. Route. When a new standards file is created, or a rule changes whether a standard is mandatory, update the application's `AGENTS.md`: mandatory standards under Mandatory Instructions, others as scope-triggered routing.
7. Validate. Every referenced file exists; filenames belong to the canonical catalog; the rule is stated once, in en-US, and not hard-wrapped; the Fixed Content and version stamp are unchanged; each baseline exception quotes the replaced baseline rule verbatim; and no other application's standards changed.

Ask the user only when the owning scope or file is ambiguous, when the rule conflicts with enforced configuration or an existing explicit decision, or to offer enforcement in step 2.

## Report

Briefly report the `project-standards` version in use, the files changed, where each rule landed and why (tool configuration or a standard), and any conflict or open question.
