# Swift Toolchain Profile

## Detection

A `Package.swift`, `.xcodeproj`, or `.xcworkspace` with `.swift` sources. iOS apps use the [`ios`](../ios/profile.md) platform profile, which extends this one.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/) | swift-format default rules with four-space indentation, plus `NeverForceUnwrap`, `NeverUseForceTry`, and `UseEarlyExits` |
| `google` | [Google Swift Style Guide](https://google.github.io/swift/) | swift-format default rules (two-space indentation, 100 columns), plus the force-unwrap, force-try, implicitly-unwrapped-optional, leading-underscore, documentation, early-exit, and `for`-`where` rules the guide requires |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter and linter | swift-format, lint in strict mode | `recommended/swift-format.json` | `.swift-format` |
| `google` | Formatter and linter | swift-format, lint in strict mode | `google/swift-format.json` | `.swift-format` |
| both | Type checker | Swift compiler | none | none |
| both | Compiler warnings | `.treatAllWarnings(as: .error)` in each first-party target's `swiftSettings`, for `swift-tools-version` 6.2 or newer only | none | `Package.swift`, edited by hand |
| both | Test framework | Swift Testing (included in the toolchain) run with `swift test`; XCTest only for UI and performance tests | none | none |
| both | Coverage (optional) | `swift test --enable-code-coverage` | none | none |

Each template lists every swift-format rule, because a `rules` object replaces the defaults instead of merging with them. The templates were generated from the Swift 6.4 toolchain's `swift format dump-configuration`.

## Install

Nothing beyond Swift 6 or newer, which includes swift-format as `swift format`, Swift Testing, and XCTest. Swift Testing needs no installation, so setup adds no test dependency.

Swift packages with `swift-tools-version` 6.2 or newer: add `swiftSettings: [.treatAllWarnings(as: .error)]` to each first-party target in `Package.swift` by hand (the Compiler warnings row). Do not use `-Xswiftc -warnings-as-errors` instead, because it applies to every Swift compiler invocation, including dependencies.

## Commands

Replace `Sources Tests` with the application's Swift source directories.

| Command | Invocation |
| --- | --- |
| `format` | `swift format --in-place --recursive Sources Tests` |
| `lint` | `swift format lint --strict --recursive Sources Tests` |
| `typecheck` | `swift build` for packages; `xcodebuild build -scheme <scheme>` for Xcode projects |
| `test` | `swift test --parallel` for packages; `xcodebuild test -scheme <scheme> -destination <destination>` for Xcode projects |
| `verify` | `swift format lint --strict --recursive Sources Tests && swift build` |

## Import order

Both variants sort imports with the `OrderedImports` rule into groups separated by one blank line, each sorted lexicographically: module imports, then declaration imports (`import struct Module.Type`), then `@_implementationOnly` imports, then `@testable` imports.

## Style rules

### recommended

- Follow the Swift API Design Guidelines: name methods by their side effects, use argument labels that read as grammatical phrases at the call site, and name Boolean properties as assertions (`isEmpty`).
- Do not silence concurrency diagnostics with `@unchecked Sendable` or `nonisolated(unsafe)`; fix the isolation instead, or comment why the code is safe.
- Use `async`/`await` and structured concurrency rather than completion handlers for new asynchronous APIs.
- Prefer value types (`struct`, `enum`) unless reference semantics or identity are required.
- Use `guard` to exit early on invalid input instead of nesting the main path.
- Write new tests with Swift Testing (`@Test`, `#expect`, `#require`); keep XCTest only for UI, performance, and Objective-C exception tests and for existing suites.
- Keep tests deterministic and independent: no real network, wall-clock time, or shared mutable state; inject clients and clocks as protocols.
- Prefer real objects or hand-written fakes over stubs and mocks, and assert on resulting state rather than on call sequences.

### google

- Name according to the Swift API Design Guidelines. Name global constants in `lowerCamelCase`, without `k` or `g` prefixes.
- Use throwing functions for operations with more than one failure reason, and `Optional` results only for one obvious failure; never return sentinel values such as -1.
- Use `guard` to exit early on invalid input instead of nesting the main path.
- Do not silence concurrency diagnostics with `@unchecked Sendable` or `nonisolated(unsafe)`; fix the isolation instead, or comment why the code is safe.
- Document each parameter, return value, and thrown error with `Parameter(s)`, `Returns`, and `Throws` tags, in that order, each with a non-empty description; omit a tag only when the summary already says it.
- Nest types that belong to one type, such as its error enum, inside it, and use a caseless `enum` as a namespace for constants and static helpers.
- Name delegate methods with the source object as the unlabeled first argument and the source type as the base name, for example `scrollViewDidBeginScrolling(_:)`.
- Import exactly the modules a file uses, without relying on transitive imports, and import `@testable` modules only in test sources.
- Write new tests with Swift Testing (`@Test`, `#expect`, `#require`); keep XCTest only for UI, performance, and Objective-C exception tests and for existing suites.
- Keep tests deterministic and independent: no real network, wall-clock time, or shared mutable state; inject clients and clocks as protocols.
- Prefer real objects or hand-written fakes over stubs and mocks, and assert on resulting state rather than on call sequences.

## Adaptation points

- Xcode projects: replace `swift build` with the `xcodebuild build` command for the application's main scheme, and set the source directories to the project's Swift source groups.
- An application whose existing sources consistently use the other indentation width: set `indentation.spaces` and `tabWidth` to match.
- A swift-format older than the template's that rejects an unknown rule: remove that rule from `rules`.
- `google` with the `None` code-comment policy: set `AllPublicDeclarationsHaveDocumentation`, `BeginDocumentationCommentWithOneLineSummary`, and `ValidateDocumentationComments` to `false`, and drop the documentation Style rule.
- `google` is stricter than the guide on force unwraps, force casts, `try!`, and implicitly unwrapped optionals: `NeverForceUnwrap`, `NeverUseForceTry`, and `NeverUseImplicitlyUnwrappedOptionals` reject them even where the guide allows a commented exception (test code and `@IBOutlet` are exempt). An application that needs the exception sets `NeverForceUnwrap` and `NeverUseForceTry` to `false` and adds the Style rule "Explain in a comment why a force unwrap, force cast, or `try!` cannot fail."
- `google`: `AllPublicDeclarationsHaveDocumentation` also flags public implementations of protocol requirements, which the guide exempts; document them or set the rule to `false`.

## Existing tooling

- SwiftLint (`.swiftlint.yml`) covers linting; SwiftFormat (`.swiftformat`) covers formatting. Keep them, and add swift-format for no concern they cover.
- An existing test framework or runner stays: XCTest suites, Quick, and Nimble. Write new tests with Swift Testing.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: swift-format (`.swift-format`) for formatting and linting, the Swift compiler for type checking, and Swift Testing with `swift test`. Documentation-comment sentence: Documentation comments use `///` Markdown comments.
