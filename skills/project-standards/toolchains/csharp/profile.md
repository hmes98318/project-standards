# C# Toolchain Profile

## Detection

A `.csproj` or `.sln` with `.cs` sources.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Microsoft C# coding conventions](https://learn.microsoft.com/dotnet/csharp/fundamentals/coding-style/coding-conventions) | 4-space indentation, Allman braces, file-scoped namespaces, `_camelCase` private and internal fields (static ones too, unlike the `s_` prefix of the Microsoft page), `PascalCase` constants, `var` only when the type is apparent |
| `google` | [Google C# Style Guide](https://google.github.io/styleguide/csharpguide.html) | 2-space indentation, K&R braces, block-scoped namespaces, `_camelCase` for all non-public fields and properties, Google modifier order |

Both variants enforce code style in the build through .NET analyzers at `latest-recommended`, `EnforceCodeStyleInBuild`, warnings as errors except NuGet vulnerability warnings, and nullable reference types.

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter and code style | `dotnet format` and IDE analyzers | `recommended/editorconfig` | `.editorconfig` (merge) |
| `google` | Formatter and code style | `dotnet format` and IDE analyzers | `google/editorconfig` | `.editorconfig` (merge) |
| both | Linter and type checker | .NET analyzers and the C# compiler | `shared/Directory.Build.props` | `Directory.Build.props` (merge) |
| both | Test framework | xUnit.net v3 on Microsoft.Testing.Platform, run by `dotnet test` | none | none |
| both | Coverage (optional) | Microsoft code coverage extension: `dotnet test --coverage --coverage-output-format cobertura` | none | none |

## Install

Setup installs no SDK. The profile expects the .NET 10 SDK (LTS) or newer, and an older SDK is reported: .NET 9 and .NET 8 reached end of support on 2026-11-10, and SDKs from .NET 9 on read the severities written next to option values in `.editorconfig` during builds. `GenerateDocumentationFile` is enabled so that unused `using` directives (IDE0005) are reported in builds; CS1591 is suppressed so that documentation comments stay governed by the code-comment policy.

When the testing policy requires tests and none exists, setup creates no test project: report that the user must create one with `dotnet new xunit3` (template package `xunit.v3.templates`), which configures Microsoft Testing Platform in the project and in `global.json`. Coverage needs the `Microsoft.Testing.Extensions.CodeCoverage` package in the test project, only when the user asks for coverage.

## Commands

| Command | Invocation |
| --- | --- |
| `format` | `dotnet format` |
| `lint` | `dotnet build` |
| `typecheck` | covered by `lint` |
| `test` | `dotnet test` |
| `verify` | `dotnet format --verify-no-changes && dotnet build` |

In Microsoft Testing Platform mode, `dotnet test` takes a solution or project through `--solution` or `--project` instead of a bare path.

## Import order

`using` directives go at the top of the file, outside the namespace, sorted alphabetically with `System` namespaces first and no blank lines between groups. Unused directives are reported.

## Style rules

### recommended

- Suffix asynchronous methods with `Async`, except test methods.
- Use `async` and `await` end to end; do not block on tasks with `.Result` or `.Wait()`.
- Accept a `CancellationToken` as the last parameter of public asynchronous methods that do I/O.
- Do not catch `Exception` except at a boundary that logs or translates the error; never swallow exceptions.
- Prefer `record` types for immutable data.
- Name tests `Method_Scenario_ExpectedBehavior`, in a `<Class>Tests` class inside a separate `<Project>.Tests` project.
- Write straight-line tests with one Act each and no `if`, `for`, `while`, or `switch`; use the framework's parameterized-test feature for repeated cases.
- Keep unit tests free of the network, file system, database, real clock, and `Thread.Sleep`; inject `TimeProvider` and use fakes.
- Test behavior through the public API; do not test private methods or assert on call interactions unless the call is the behavior.

### google

- Treat acronyms as words (`MyRpc`); name files and directories in `PascalCase`, each file after its main class, with one core class per file.
- Order class members: nested types, enums, delegates, and events; static, const, and readonly fields; fields and properties; constructors and finalizers; methods; within each group order public, internal, protected internal, protected, then private.
- Wrap lines at 100 columns.
- Name an argument, or replace it with an `enum` or a named constant, when its meaning is not obvious, as with `bool`, `null`, and numeric literals.
- Declare parameters with the narrowest collection interface that suffices, such as `IReadOnlyCollection<T>`; use `IEnumerable<T>` only when iterating once; return `IList<T>` rather than `List<T>` when giving ownership to the caller.
- Use `var` when the type is obvious or the variable is short-lived; write the type for basic types and when it helps the reader.
- Add an extension method only for a type whose source you cannot change, and only for general core functionality.
- Indent continuation lines by 4 spaces, aligning wrapped arguments with the first argument when they fit.
- Make a variable or field `const` whenever possible, and use named constants instead of magic numbers.
- Keep namespaces at most two levels deep; the folder layout does not need to match the namespace.
- Name tests `Method_Scenario_ExpectedBehavior`, in a `<Class>Tests` class inside a separate `<Project>.Tests` project.
- Write straight-line tests with one Act each and no `if`, `for`, `while`, or `switch`; use the framework's parameterized-test feature for repeated cases.
- Keep unit tests free of the network, file system, database, real clock, and `Thread.Sleep`; inject `TimeProvider` and use fakes.
- Prefer real implementations, then fakes, then mocks; use a mocking library only where no real or fake implementation can run in-process.
- Test behavior through the public API; do not test private methods or assert on call interactions unless the call is the behavior.

## Adaptation points

- An existing `Directory.Build.props`: merge the `PropertyGroup` properties into it.
- A solution whose projects are in different directories: place `Directory.Build.props` and `.editorconfig` in the directory that contains all of them.
- Projects that cannot enable nullable reference types in one change: remove `<Nullable>` and report it in the Completion Report.
- A .NET SDK older than 9: keep the template; the `dotnet_diagnostic.<rule>.severity` entries still enforce the main rules.
- An SDK upgrade that reports new analyzer findings: set `AnalysisLevel` to the previous SDK's version with the `-recommended` suffix, for example `10-recommended`, until the findings are fixed.
- A directory that holds more than one solution or project: pass the solution to `dotnet format` and `dotnet build`, and `--solution` or `--project` to `dotnet test`.

## Existing tooling

- An existing `.editorconfig` covers formatting and code-style severity. Keep it.
- StyleCop.Analyzers, Roslynator, Meziantou.Analyzer, SonarAnalyzer, or an explicit `AnalysisLevel` or `AnalysisMode` covers linting.
- An existing NUnit, MSTest, xUnit.net v2, or TUnit setup covers the test framework. Keep it and its runner mode; `dotnet test` stays the `test` command.
- An existing `coverlet.collector`, `coverlet.msbuild`, or `Microsoft.Testing.Extensions.CodeCoverage` reference covers coverage. Keep it, and do not combine `coverlet.collector` with a Microsoft Testing Platform runner.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: `dotnet format` with `.editorconfig` for formatting, the .NET analyzers configured in `Directory.Build.props` and `.editorconfig` for linting, the C# compiler for type checking, and xUnit.net or the existing test framework. Documentation-comment sentence: Documentation comments use XML documentation comments (`///`).
