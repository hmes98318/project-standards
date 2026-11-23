# Toolchains

Select and apply enforced tooling for each software application: formatter, linter, type checker, test framework, and the verification commands that run them. Read `references/standards-contract.md` first; its Enforcement Ladder explains why tooling comes before prose. Paths such as `toolchains/` are relative to the skill directory.

## Catalog

Each profile fixes the toolchain for one language in two variants: Recommended and Google Style Guide. A variant chooses a style authority and ships the configuration that enforces it, the import order, the test framework, and the prose style rules that tools cannot check. Applying the same variant gives every project the same tools, configuration, commands, and rules, so generated standards do not drift between runs and no style guide has to be researched during setup.

- `recommended` (Recommended) is the default. It follows the language's official conventions with the tooling most widely adopted for the language.
- `google` (Google Style Guide) follows the language's [Google Style Guide](https://google.github.io/styleguide/), enforced through the same kinds of tools. Each profile's Variants table links the guide it follows.

| Profile | Applies to | `recommended` formatting and linting | `google` formatting and linting | Type checker | Test framework |
| --- | --- | --- | --- | --- | --- |
| [`typescript`](../toolchains/typescript/profile.md) | TypeScript and JavaScript on Node.js package managers | Prettier defaults; ESLint with typescript-eslint and perfectionist | Prettier with `gts` options; ESLint with the Google TypeScript rules | `tsc` | Vitest |
| [`python`](../toolchains/python/profile.md) | Python | Ruff | Ruff at 80 columns with Google docstrings and imports | mypy | pytest |
| [`go`](../toolchains/go/profile.md) | Go modules | golangci-lint with `gofumpt` and `gci` | golangci-lint with Google revive and staticcheck rules | `go build` | `go test` |
| [`rust`](../toolchains/rust/profile.md) | Cargo packages and workspaces | rustfmt; Clippy `pedantic` | rustfmt with Google options; Clippy `pedantic` with `missing_docs`, `exhaustive_enums`, `exhaustive_structs`, and `undocumented_unsafe_blocks` | `cargo check` through Clippy | `cargo test` |
| [`java`](../toolchains/java/profile.md) | Java on Gradle or Maven | Palantir Java Format; Error Prone | google-java-format; Error Prone | `javac` | JUnit 6 with AssertJ or Truth |
| [`kotlin`](../toolchains/kotlin/profile.md) | Kotlin on Gradle | ktlint `ktlint_official` | ktlint `android_studio` (Android Kotlin style guide) | `kotlinc` | JUnit 6 with `kotlin.test` |
| [`csharp`](../toolchains/csharp/profile.md) | C# on the .NET SDK | `dotnet format` and analyzers, Microsoft conventions | `dotnet format` and analyzers, Google conventions | `dotnet build` | xUnit.net v3 |
| [`swift`](../toolchains/swift/profile.md) | Swift packages and Xcode projects | swift-format, four-space indentation | swift-format, Google rules | `swift build` or `xcodebuild` | Swift Testing |
| [`flutter`](../toolchains/flutter/profile.md) | Flutter apps and Dart packages | `dart format`; `flutter_lints` with strict analyzer modes | same as `recommended`: Effective Dart is Google's Dart guide | Dart analyzer | `flutter_test` |
| [`shell`](../toolchains/shell/profile.md) | Bash and POSIX shell scripts | shfmt; ShellCheck | shfmt; ShellCheck with Google checks | none | Bats |

Platform profiles extend a language profile with the platform's own checks:

| Profile | Extends | Applies to | Additions in both variants |
| --- | --- | --- | --- |
| [`android`](../toolchains/android/profile.md) | `kotlin` | Android apps and libraries | Android Lint with warnings as errors; Compose lint checks; JUnit 4 local tests and Compose UI tests |
| [`ios`](../toolchains/ios/profile.md) | `swift` | iOS apps in Xcode | warnings as errors and complete concurrency checking for the app's targets; `xcodebuild` commands; Swift Testing with XCTest for UI tests |

Apply a platform profile by applying the language profile it extends in the same variant, then the platform profile's additions. The platform profile's Commands replace the language profile's, and `coding-style.md` receives the Style rules of both.

A language without a profile follows the coding-style authority order in setup workflow step 4. Never improvise a profile or a variant for it.

## Profile format

Every `profile.md` has the same sections, in this order:

- **Detection** — the manifests and sources that select the profile.
- **Variants** — each variant's style authority and a summary of its toolchain.
- **Toolchain** — one row per variant and concern (formatter, linter, type checker, test framework, optional coverage, and task-runner commands when the profile has a template for them): the tool, its template, and the target path relative to the application directory. Rows for the test framework and coverage name the tool and its invocation and have no template; coverage applies only when the user asks for it. Templates live in the profile's `recommended/`, `google/`, or `shared/` directory; a row marked `both` applies to every variant. A target marked `(merge)` names a fragment to merge into that file instead of a file to copy.
- **Install** — the project's own development dependencies to add, each with the condition that requires it, including the test framework when the testing policy requires tests and the application has none. Tools that live outside the project are not installed (see Applying a profile).
- **Commands** — the `format`, `lint`, `typecheck`, `test`, and `verify` commands, where `verify` runs every check without modifying files.
- **Import order** — the import grouping and sorting each variant enforces, and which tool enforces it. A grouping rule that no tool enforces is a Style rule instead.
- **Style rules** — one list per variant of rules the tools cannot enforce, written to be copied verbatim into `coding-style.md`.
- **Adaptation points** — the only places where a template may be changed, and how.
- **Existing tooling** — which existing tools replace which concerns.
- **Standards notes** — what the application's `coding-style.md` records about the toolchain.

## Choosing the profiles

An application uses one profile for each language with source files in it, not only for its main language. For example, a Flutter app with release scripts uses the `flutter` and `shell` profiles, and a Node.js service with deployment scripts uses `typescript` and `shell`; the inspector's `toolchain_profiles` lists the candidates per directory. A secondary profile governs only its own files. Skip generated or vendored code, and code that a profile assigns to another one, such as the host folders of a Flutter app. Ask in the Toolchain decision only when it is unclear whether a few files of a language are part of the application.

## Choosing the variant

Each application whose language has a profile uses one variant, `recommended` unless the user chooses `google` (setup workflow step 3). A profile that has only a `recommended` variant, such as `flutter`, serves a `google` choice too, because its style authority is also Google's guide for that language (Effective Dart is listed in Google's style guide index); no report is needed. The variant decides the style authority recorded in `coding-style.md` and the Style rules copied there, even when existing tooling covers every concern. When existing tooling contradicts a Style rule of the chosen variant, keep the tooling, omit that rule, and report the conflict.

## Choosing the toolchain for each concern

Decide formatter, linter, type checker, and test framework separately for each application:

1. A tool the repository already enforces for the concern stays, together with its configuration. Never replace or reconfigure it as part of setup.
2. A tool the user names is used for the concern, unless it conflicts with enforced configuration; report the conflict.
3. Otherwise, when the user approved the profile (setup workflow step 3), the tool of the chosen variant covers the concern. The test framework is the one exception: the testing policy alone decides it, whether or not the profile was approved or asked about. Add the framework only when the testing policy requires tests and the application has no test framework yet; never add one to an application whose testing policy requires no tests.
4. Otherwise, the concern stays without enforced tooling. Record the selected coding-style authority in `coding-style.md` instead.

The profile's Existing tooling section says when an existing tool already covers a concern, for example Biome covering both formatting and linting. Configuration that `coding-style.md` records as generated from the application's previous variant (its `Variant:` line) is that variant's template, not existing tooling: switching the variant replaces those files with the new variant's templates, and re-applies, or reports as no longer applicable, any rule the user approved adding to them.

## Applying a profile

Apply the profile only to the concerns assigned to it under Choosing the toolchain for each concern:

1. Copy each template of the chosen variant, and each `shared/` template its rows use, to its target path in the application directory, byte for byte; template filenames omit leading dots, so always write the target name. Change only the profile's Adaptation points. Merge `(merge)` fragments into the existing file, keeping its other content, or create the file from the fragment when it does not exist.
2. Add the Install dependencies the application does not already declare, leaving declared ones and their version ranges unchanged, through the application's package manager or build tool, so that versions resolve to the latest stable releases and are pinned the way the ecosystem pins them, for example in a lockfile. Never type version numbers from memory. Resolve a `{{LATEST_STABLE_VERSION}}` placeholder in a template to the latest stable release on the tool's primary distribution source, such as the Gradle Plugin Portal or Maven Central.
3. Add the profile's commands to a task runner only when the profile's Toolchain table has a Commands row for it, as the TypeScript profile has for `package.json` scripts, using the names `format`, `lint`, `typecheck`, `test`, and `verify`. Keep existing scripts with those names when they already run the same check, and report a conflicting one instead of replacing it. Otherwise record the commands in `AGENTS.md` only. A `typecheck` command that the table marks as covered by `lint`, or as `none`, is omitted.
4. Add nothing the profile does not list. Report other gaps, such as installed dependencies missing from `.gitignore`, in the Completion Report.
5. Run `verify`. Do not change application source code to make it pass, and do not weaken, disable, or suppress any rule. Report the result: passing, or the failing checks with their finding counts and the command that applies automatic fixes, such as the formatter, so the user can decide.

Commands follow the tools actually used. Each Commands table assumes the profile's own tool for every concern. Where existing tooling covers a concern, replace that concern's part of `format`, `lint`, `typecheck`, and `verify` with the existing tool's own check, such as its `--check` or `--diff` mode, over the same paths, and keep the other concerns' parts. When no profile applies, assemble the same commands from the existing tools only, with one check per concern and none for a concern without enforced tooling. When an existing tool has no check mode that leaves files unmodified, leave it out of `verify` and report that.

Setup installs only the project's own development dependencies and the toolchain components that Install lists, such as `rustup component add`. It never installs SDKs, system packages, or global tools, never edits CI configuration, and creates no project or sample files. When a tool that a profile needs lies outside the project, such as golangci-lint, ShellCheck, shfmt, or `cargo-llvm-cov`, and is not installed, or a dependency cannot be installed, for example without network access, keep the configuration, list the missing tools and dependencies with their install commands in the Completion Report, and do not run `verify`.

## Recording the toolchain

- Record the commands in the application's `AGENTS.md` under Verification, because agents read `AGENTS.md` on every task and follow commands placed there more reliably than linked documents. Use the task-runner names when the commands were added to a task runner, and write one list item per command in this order and form:
  - `` `<format>` `` — applies formatting and automatic fixes.
  - `` `<verify>` `` — checks formatting, linting, and types without modifying files.
  - `` `<test>` `` — runs the tests. Include it only when the application has a test command.
- In `coding-style.md`, write these sections in this order, using exactly these headings and sentence forms so that every project records the toolchain the same way. Add project-specific naming or design conventions that need judgment after them, as further sections:
  - `## Style Authority`: `Variant: <Recommended or Google Style Guide>. Style authority: <the authority links of the profile's Variants row>.` For an application whose language has no profile, write only `Style authority: <the authority chosen in setup workflow step 4>.`
  - `## Toolchain`: one list item per concern for formatting, linting, and type checking, in the form `- <Concern>: <tool>, configured in \`<path>\`.`, or `- <Concern>: <tool>, with default settings.` when no file configures the tool, or `- <Concern>: none.` when the language has no tool for the concern or the user declined it. Then `- Testing: <test framework>.` or `- Testing: none.`, followed by the sentence `These tools and their configuration govern every concern listed above except testing.` Name the files and tools the application actually uses, including existing tooling kept under Choosing the toolchain for each concern.
  - `## Code Comments`: the selected code-comment policy, as the setup workflow's Code-comment policy section describes, followed by the documentation-comment sentence from the Standards notes of each profile, in profile order, each as its own paragraph.
  - `## Style Rules`: the variant's Style rules, copied verbatim, except rules omitted for a reported conflict with existing tooling or with the code-comment policy. The policy governs comment coverage: omit a rule that requires comments or documentation comments beyond what the policy requires, such as documenting every exported symbol under `Concise` or `None`, and keep rules about the form of the comments that exist. Style rules are language and platform coding practice, so they stay in `coding-style.md` even when they touch testing, security, UI, or performance, which other standards files own; do not copy them into those files.

  Do not restate rules the tools enforce, or the baseline's rules on suppressing checks.
- An application with several profiles (Choosing the profiles) records the primary profile, the one for its main language, first and each secondary profile after it. A platform profile and the language profile it extends count as one profile: its `Variant:` line names the platform profile, and its Style rules are the language profile's followed by the platform profile's. With more than one profile, write one `Variant:` and `Style authority:` sentence per profile in `## Style Authority`, one `### <profile>` subsection per profile in `## Toolchain` and in `## Style Rules`, with the closing sentence of `## Toolchain` written once after the last subsection, and in `AGENTS.md` the three command items of each profile in the same order, each description starting with `(<profile>)`.
- In update mode, when `coding-style.md` already exists, change only the toolchain content of these sections and fold what it already holds into them: keep every user-written rule as a further section, and leave the file untouched when the toolchain, variant, and code-comment policy are unchanged.
