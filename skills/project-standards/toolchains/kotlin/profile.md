# Kotlin Toolchain Profile

## Detection

A `build.gradle.kts` or `build.gradle` with `.kt` sources. Android modules use the [`android`](../android/profile.md) platform profile, which extends this one.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Kotlin coding conventions](https://kotlinlang.org/docs/coding-conventions.html) as extended by ktlint's `ktlint_official` code style | ktlint `ktlint_official` through Spotless, unused imports removed, Kotlin compiler warnings as errors, JUnit 6 with `kotlin.test` for tests |
| `google` | [Android Kotlin style guide](https://developer.android.com/kotlin/style-guide) | ktlint `android_studio` code style through Spotless, unused imports removed, Kotlin compiler warnings as errors, JUnit 6 with `kotlin.test` for tests |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| both | Formatter and linter | Spotless with ktlint, and Kotlin compiler warnings as errors | `shared/build.gradle.fragment.kts` | `build.gradle.kts` (merge) |
| `recommended` | ktlint code style | `.editorconfig` | `recommended/editorconfig` | `.editorconfig` (merge) |
| `google` | ktlint code style | `.editorconfig` | `google/editorconfig` | `.editorconfig` (merge) |
| both | Type checker | Kotlin compiler | none | none |
| both | Test framework | JUnit 6 (JUnit Jupiter) through `kotlin("test")` with `useJUnitPlatform()`, run by `gradle test`; `kotlinx-coroutines-test` and Turbine for coroutine and `Flow` code | none | none |
| both | Coverage (optional) | Kover: the `org.jetbrains.kotlinx.kover` plugin and `gradle koverHtmlReport` | none | none |

## Install

The Spotless plugin declared in the fragment. Replace `{{LATEST_STABLE_VERSION}}` with the latest stable release from the Gradle Plugin Portal. The fragment's top-level `kotlin { compilerOptions { ... } }` block configures the Kotlin Gradle plugin, not Spotless.

When the testing policy requires tests and none exists, add `testImplementation(platform("org.junit:junit-bom:..."))`, `testImplementation(kotlin("test"))`, `testRuntimeOnly("org.junit.platform:junit-platform-launcher")` and `tasks.test { useJUnitPlatform() }`; add `kotlinx-coroutines-test` and Turbine only when the code uses coroutines or `Flow`. Gradle runs JUnit 4 unless `useJUnitPlatform()` selects JUnit Jupiter.

## Commands

Use the Gradle wrapper (`./gradlew`) when the application has one.

| Command | Invocation |
| --- | --- |
| `format` | `gradle spotlessApply` |
| `lint` | `gradle spotlessCheck compileKotlin compileTestKotlin` |
| `typecheck` | covered by `lint` |
| `test` | `gradle test` |
| `verify` | `gradle spotlessCheck compileKotlin compileTestKotlin` |

`test` runs the application's existing test runner; `gradle test` applies when it uses JUnit on Gradle.

## Import order

Both variants forbid wildcard imports and remove unused ones.

- `recommended`: ktlint's `ktlint_official` layout: all imports sorted lexicographically, then `java`, `javax`, and `kotlin` imports, then import aliases.
- `google`: one ASCII-sorted list with no blank lines, as the Android Kotlin style guide requires.

## Style rules

### recommended

- Prefer `val` over `var`, and read-only collection types (`List`, `Map`) in public APIs.
- Use nullable types only where absence is meaningful; do not use `!!` except where a comment explains why the value cannot be null.
- Model closed sets of states with `sealed` classes or interfaces and handle them with exhaustive `when` expressions.
- Launch coroutines only in a scope owned by a lifecycle or component; do not create ad hoc `CoroutineScope(...)` instances.
- Use named arguments when a call passes several parameters of the same type or any `Boolean`.
- Prefer default parameter values to overloaded functions.
- Name files after their content; avoid meaningless words such as `Util` in file names, and do not create a file only to hold the extensions of one class.
- Test observable behavior through public APIs; do not test private functions or assert on call order unless the interaction is the behavior.
- Prefer real implementations, then hand-written fakes; use MockK only for boundaries you cannot fake.
- Keep unit tests deterministic: inject clocks and dispatchers, and never use real network, `Thread.sleep`, or `delay` as synchronization.
- Test `suspend` functions with `runTest` and `Flow`s with Turbine; do not use `runBlocking` in tests.
- Give each test one behavior and a name stating scenario and expected result; keep loops and conditionals out of test bodies.
- Place tests under `src/test/kotlin` in the production class's package, in a class named `<ClassUnderTest>Test`.

### google

- Name constants (`const val`, and top-level or `object` `val` properties holding deeply immutable data) in `UPPER_SNAKE_CASE` and all other properties in `lowerCamelCase`; treat acronyms as words (`XmlHttpRequest`).
- Order the declarations of a file and the members of a class in a logical order that a maintainer could explain; do not just append new declarations at the end.
- Write KDoc for every `public` type and every `public` or `protected` member except simple, obvious members and overrides; begin with a summary fragment, not a sentence.
- Keep each file focused on a single theme; put unrelated declarations in separate files and minimize public declarations per file.
- In test sources, separate the parts of a test function name with underscores (`pop_emptyStack`); never use backticked names with spaces.
- Test observable behavior through public APIs; do not test private functions or assert on call order unless the interaction is the behavior.
- Prefer real implementations, then hand-written fakes; use MockK only for boundaries you cannot fake.
- Keep unit tests deterministic: inject clocks and dispatchers, and never use real network, `Thread.sleep`, or `delay` as synchronization.
- Test `suspend` functions with `runTest` and `Flow`s with Turbine; do not use `runBlocking` in tests.
- Give each test one behavior and a name stating scenario and expected result; keep loops and conditionals out of test bodies.
- Place tests under `src/test/kotlin` in the production class's package, in a class named `<ClassUnderTest>Test`.

## Adaptation points

- Groovy build scripts (`build.gradle`): write the same configuration in Groovy syntax, and target `*.gradle` files in place of `kotlinGradle`.
- Multi-project builds: apply the fragment in each Kotlin subproject, or in the convention plugin the build already uses for shared configuration.
- Android modules: compile task names include the variant, for example `compileDebugKotlin`; use them in `lint` and `verify`.
- Kotlin Multiplatform modules: use the `compileKotlin<Target>` task of each target in `lint` and `verify`.
- An existing `.editorconfig`: add the fragment's `[*.{kt,kts}]` section, or its properties to an existing section for those files.
- Library modules: add `kotlin { explicitApi() }` so that public declarations need explicit visibility and types; `explicitApiWarning()` is the lenient form.
- `google` variant: Truth or Hamcrest assertions are acceptable when the application already uses them.

## Existing tooling

- An existing ktlint (through Spotless or the ktlint Gradle plugin) or ktfmt setup covers formatting.
- An existing detekt or ktlint setup covers linting. Android Lint covers Android-specific linting.
- An existing test framework or runner (JUnit 4, Kotest, TestNG) stays; add JUnit 6 only when none exists.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: ktlint through Spotless with the `.editorconfig` code style, and Kotlin compiler warnings as errors, for formatting and linting; the Kotlin compiler for type checking; and JUnit. Documentation-comment sentence: Documentation comments use KDoc `/** ... */` blocks.
