# Design Principles

The skill is built around a few decisions that shape every file it writes.

## Application Scope

Language-, framework-, and tooling-specific rules belong to the application that owns them. The skill treats the application as the primary boundary, and only rules that apply to every application and technology stack live in the repository-wide baseline. In a monorepo this keeps a rule written for one application from leaking into another.

## Tooling Before Prose

Agents reliably follow a rule that fails a check and often skip prose they are only told to read. The skill therefore places each rule at the highest level that can hold it. A rule that a formatter, linter, type checker, compiler setting, or test can enforce lives in that tool's configuration. `AGENTS.md` carries the commands that run those checks and the few instructions every change in its scope needs. Standards keep only the rules that need judgment, such as the code-comment policy, the testing policy, and design conventions no tool checks, and they name a tool instead of restating what it enforces. When a rule request could be enforced by a tool the application already configures, the skill offers to enable it there.

## Durable Rules, Not Project State

Standards state how contributors should develop, review, test, and secure the project, and they stay valid as the code changes. Current architecture, module layout, deployment state, and design specifications change with the project, so they stay in their own source-of-truth documents and standards reference them. Descriptions of the current state would otherwise drift out of date inside files that agents treat as rules.

## Routing and Detail

`AGENTS.md` routes and the standards carry the detail. Root instructions stay short, and an agent reads only the standards that apply to the code it changes.

## Existing Tooling First

Enforced formatter, linter, and compiler configuration in the repository always wins. Where none exists, the skill applies a bundled toolchain profile when the language has one, and otherwise follows framework guidance, then the Google Style Guide, then the language's official style guide.

## Fixed Baseline with Recorded Exceptions

The common baseline is not edited per project. A project that needs a different rule records an exception at the narrowest scope it applies to, so every deviation is explicit and visible next to the code it concerns, and the baseline itself stays identical across repositories.

## Documentation Describes the System as It Is

Generated `AGENTS.md` rules direct agents to keep development documentation a coherent technical explanation of the current design, revised in place and reviewed before development, rather than a log of changes appended over time.
