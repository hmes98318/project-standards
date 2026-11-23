# Android Toolchain Profile

## Detection

An Android Gradle module with an `AndroidManifest.xml`, applying `com.android.application` or `com.android.library`, with Kotlin sources. This platform profile extends the [`kotlin`](../kotlin/profile.md) profile: apply that profile in the same variant first, then this profile's additions, and use this profile's Commands instead of the Kotlin ones.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Guide to app architecture](https://developer.android.com/topic/architecture), [Recommendations for Android architecture](https://developer.android.com/topic/architecture/recommendations), and the Kotlin `recommended` variant | the Kotlin `recommended` toolchain, Android Lint with warnings as errors, and Slack's Compose lint checks for Compose apps |
| `google` | [Android Kotlin style guide](https://developer.android.com/kotlin/style-guide), [Compose API guidelines](https://android.googlesource.com/platform/frameworks/support/+/androidx-main/compose/docs/compose-api-guidelines.md), and [Recommendations for Android architecture](https://developer.android.com/topic/architecture/recommendations) | the Kotlin `google` toolchain (ktlint `android_studio`), Android Lint with warnings as errors, and the Compose lint checks bundled with the Compose libraries |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| both | Kotlin formatting, linting, and compiler warnings | the `kotlin` profile in the same variant | see that profile | see that profile |
| both | Android linter | Android Lint, warnings as errors, dependencies checked | `shared/lint.gradle.fragment.kts` | each Android module's `build.gradle.kts` (merge) |
| both | ktlint for Compose | `.editorconfig` setting that exempts `@Composable` functions from ktlint's function naming | `shared/editorconfig` | `.editorconfig` (merge) |
| both | Spotless targets | Kotlin sources under Android source sets, which Spotless does not detect | `shared/spotless.gradle.fragment.kts` | each Android module's `build.gradle.kts` (merge) |
| `recommended` | Compose linter | Slack compose-lints, run by Android Lint | `recommended/compose-lint.gradle.fragment.kts` | each Android module's `build.gradle.kts` (merge) |
| both | Type checker | Kotlin compiler | none | none |
| both | Test framework | JUnit 4 local tests run by `./gradlew testDebugUnitTest`; `kotlinx-coroutines-test` and Turbine for coroutine and `Flow` code; Compose UI tests with `ui-test-junit4` in `src/androidTest` | none | none |
| both | Coverage (optional) | Kover for local tests: the `org.jetbrains.kotlinx.kover` plugin and `./gradlew koverHtmlReport` | none | none |

## Install

The Kotlin profile's dependencies, plus for `recommended` Compose apps the `compose-lint-checks` dependency declared in the fragment. Replace `{{LATEST_STABLE_VERSION}}` with the latest stable release from Maven Central. With Android Gradle Plugin 9 or newer, Kotlin support is built in: do not apply `org.jetbrains.kotlin.android`, and configure compiler options in the top-level `kotlin { compilerOptions { ... } }` block, not `android { kotlinOptions { ... } }`.

When the testing policy requires tests and none exists, add `testImplementation("junit:junit:...")`, plus `kotlinx-coroutines-test` and Turbine when the module uses coroutines or `Flow`. Do not apply the Kotlin profile's JUnit Platform setup (`useJUnitPlatform()`) to Android modules: Android local tests and AndroidX Test run on JUnit 4. Compose UI tests need `androidTestImplementation` `androidx.compose.ui:ui-test-junit4` and `debugImplementation` `androidx.compose.ui:ui-test-manifest`.

## Commands

Use the Gradle wrapper (`./gradlew`). Replace `Debug` with the application's development build variant when it differs.

| Command | Invocation |
| --- | --- |
| `format` | `./gradlew spotlessApply` |
| `lint` | `./gradlew spotlessCheck lintDebug` |
| `typecheck` | `./gradlew compileDebugKotlin` |
| `test` | `./gradlew testDebugUnitTest` |
| `verify` | `./gradlew spotlessCheck lintDebug` |

Android Lint compiles the variant it checks, so `verify` also type-checks. Instrumented tests (`connectedDebugAndroidTest`) and Compose UI tests need a device or emulator and are not part of these commands. `test` runs the application's existing test runner.

## Import order

Imports follow the Kotlin profile's Import order for the same variant.

## Style rules

### recommended

- Follow unidirectional data flow: UI state flows down from a state holder, and events flow up as lambdas or function calls.
- Expose screen state from a `ViewModel` as a `StateFlow` of an immutable UI state type in a single `uiState` property; a `ViewModel` never holds an `Activity`, `Context`, `Resources`, `View`, or `Fragment`.
- Keep data access in repositories in the data layer; UI code never calls network or database APIs directly.
- Do not send events from the `ViewModel` to the UI; process the event in the `ViewModel` and update the UI state.
- Collect UI state in composables with `collectAsStateWithLifecycle`.
- Hoist state: stateless composables take a value and an `onValueChange`-style callback, and only the screen-level composable obtains the `ViewModel`.
- Name resources in `snake_case` with a type prefix, such as `activity_main.xml`, `item_order.xml`, and `ic_search.xml`; put user-visible text in string resources.
- Test a `ViewModel` and a repository on the JVM with fakes and `runTest`; use Robolectric only for code that needs Android classes.
- Find Compose UI nodes in tests by semantics (text, content description, or test tag), not by layout structure.

### google

- Follow unidirectional data flow: UI state flows down from a state holder, and events flow up as lambdas or function calls.
- Expose screen state from a `ViewModel` as a `StateFlow` of an immutable UI state type in a single `uiState` property; a `ViewModel` never holds an `Activity`, `Context`, `Resources`, `View`, or `Fragment`.
- Keep data access in repositories in the data layer; UI code never calls network or database APIs directly.
- Do not send events from the `ViewModel` to the UI; process the event in the `ViewModel` and update the UI state.
- Collect UI state in composables with `collectAsStateWithLifecycle`.
- Name `@Composable` functions that emit UI in `PascalCase` as nouns, and give each a `modifier: Modifier = Modifier` parameter as its first optional parameter, passed to the root node it emits.
- Hoist state: stateless composables take a value and an `onValueChange`-style callback, and only the screen-level composable obtains the `ViewModel`.
- Name resources in `snake_case` with a type prefix, such as `activity_main.xml`, `item_order.xml`, and `ic_search.xml`; put user-visible text in string resources.
- Test a `ViewModel` and a repository on the JVM with fakes and `runTest`; use Robolectric only for code that needs Android classes.
- Find Compose UI nodes in tests by semantics (text, content description, or test tag), not by layout structure.

## Adaptation points

- Modules without Jetpack Compose: omit the compose-lints fragment.
- Spotless on Android: keep an existing `target` in the `kotlin` block; otherwise merge the `shared/spotless.gradle.fragment.kts` target into it.
- Robolectric, only when a test needs Android classes: add `testOptions { unitTests { isIncludeAndroidResources = true } }` and the `org.robolectric:robolectric` test dependency. MockK or Mockito only for boundaries that cannot be faked.
- Library modules: keep `checkDependencies = true` only in the application module, which then checks its library dependencies.
- Adopting in an existing app with many Lint findings: report the findings. Create a Lint baseline (`baseline = file("lint-baseline.xml")` and `./gradlew lintDebug -Dlint.baselines.continue=true`) only when the user approves it.
- Android Gradle Plugin older than 9: keep the `org.jetbrains.kotlin.android` plugin the module already applies; the Kotlin profile's `kotlin { compilerOptions { ... } }` block works unchanged.

## Existing tooling

- An existing `android { lint { ... } }` block or `lint.xml` covers Android linting.
- An existing ktlint, ktfmt, or detekt setup covers the concerns the Kotlin profile lists.
- An existing test framework or runner (JUnit 4, Robolectric, Kotest) stays.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: the Kotlin profile's, plus Android Lint, configured in the module build files, for linting, and JUnit. The Style rules are the Kotlin profile's followed by this profile's for the variant. The documentation-comment sentence is the Kotlin profile's.
