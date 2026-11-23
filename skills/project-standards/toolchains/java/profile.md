# Java Toolchain Profile

## Detection

A `build.gradle`, `build.gradle.kts`, or `pom.xml` with `.java` sources. A project that mixes Java and Kotlin sources uses this profile for Java and the `kotlin` profile for Kotlin.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Java Language Specification, Naming Conventions](https://docs.oracle.com/javase/specs/jls/se26/html/jls-6.html#jls-6.1) for naming; layout by Palantir Java Format | Palantir Java Format (4-space indentation, 120 columns) through Spotless, Error Prone, `javac` warnings as errors, JUnit 6 and AssertJ for tests |
| `google` | [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) | google-java-format (2-space indentation, 100 columns) through Spotless, Error Prone with the Google Style checks as errors, `javac` warnings as errors, JUnit 6 and Truth for tests |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter and linter | Spotless with Palantir Java Format, wildcard and module imports forbidden, Error Prone, `javac -Xlint:all -Werror` | `recommended/build.gradle.fragment.kts` (Gradle) or `recommended/pom.fragment.xml` (Maven) | `build.gradle.kts` (merge) or `pom.xml` (merge) |
| `google` | Formatter and linter | Spotless with google-java-format, wildcard and module imports forbidden, Error Prone with the Google Style checks as errors, `javac -Xlint:all -Werror` | `google/build.gradle.fragment.kts` (Gradle) or `google/pom.fragment.xml` (Maven) | `build.gradle.kts` (merge) or `pom.xml` (merge) |
| both, Maven only | Error Prone JVM flags | Maven JVM configuration | `shared/mvn/jvm.config` | `.mvn/jvm.config` |
| both | Type checker | Java compiler | none | none |
| both | Test framework | JUnit 6 (JUnit Jupiter) on the JUnit Platform, run by `gradle test` or `mvn test`; AssertJ for `recommended`, Truth for `google` | none | none |
| both | Coverage (optional) | JaCoCo: the Gradle `jacoco` plugin with `gradle test jacocoTestReport`, or `jacoco-maven-plugin` with `mvn test jacoco:report` | none | none |

## Install

The plugins and the `error_prone_core` dependency declared in the fragment. Replace each `{{LATEST_STABLE_VERSION}}` with the latest stable release from the Gradle Plugin Portal or Maven Central. Error Prone and Palantir Java Format must run on JDK 21 or newer; they can still compile and format code for older Java releases through `--release`.

When the testing policy requires tests and none exists, add the JUnit BOM `org.junit:junit-bom`, `org.junit.jupiter:junit-jupiter` and, for Gradle, `org.junit.platform:junit-platform-launcher` as `testRuntimeOnly` with `tasks.test { useJUnitPlatform() }`, plus `org.assertj:assertj-core` for `recommended` or `com.google.truth:truth` for `google`. Maven needs Surefire 3 or newer. JUnit 6 requires Java 17 at runtime.

## Commands

Use the Gradle or Maven wrapper (`./gradlew`, `./mvnw`) when the application has one.

| Command | Gradle | Maven |
| --- | --- | --- |
| `format` | `gradle spotlessApply` | `mvn spotless:apply` |
| `lint` | `gradle compileJava compileTestJava` | `mvn test-compile` |
| `typecheck` | covered by `lint` | covered by `lint` |
| `test` | `gradle test` | `mvn test` |
| `verify` | `gradle spotlessCheck compileJava compileTestJava` | `mvn spotless:check test-compile` |

`test` runs the application's existing test runner; the commands above apply when it uses JUnit on Gradle or Maven.

## Import order

Both formatters write all static imports in one block, then all non-static imports in one block, separated by one blank line and sorted in ASCII order, with no other blank lines. They remove unused imports. Spotless fails on wildcard imports and module imports (`forbidWildcardImports()`, `forbidModuleImports()`); the fragments enable both.

## Style rules

### recommended

- Name classes and interfaces as nouns in `UpperCamelCase`, methods as verbs in `lowerCamelCase`, and constants (`static final` deeply immutable fields) in `UPPER_SNAKE_CASE`.
- Do not catch `Exception` or `Throwable` except at a boundary that logs or translates the error; never swallow an exception silently.
- Prefer immutable objects and `final` fields; return unmodifiable collections from public APIs.
- Use `Optional` only as a return type for possibly absent values; never for fields or parameters.
- Make classes `final` unless they are designed and documented for extension.
- Test observable behavior through public APIs; do not test private methods or assert on call order unless the interaction is the behavior.
- Prefer real implementations, then hand-written fakes; use Mockito only for boundaries you cannot fake.
- Keep unit tests deterministic: no real network, clock, sleeps, or randomness without an injected fake or a fixed seed.
- Give each test one behavior and a name stating scenario and expected result; keep loops and conditionals out of test bodies and use `@ParameterizedTest` for repeated inputs.
- Place tests under `src/test/java` in the production class's package, in a class named `<ClassUnderTest>Test`.

### google

- Order the members of each class in a logical order that a maintainer could explain; do not just append new members at the end.
- Name constants (`static final` fields whose contents are deeply immutable) in `UPPER_SNAKE_CASE` and all other fields in `lowerCamelCase`; treat acronyms as words (`XmlHttpRequest`, `newCustomerId`).
- Write Javadoc for every visible class and every `public` or `protected` member except simple, obvious members and overrides; begin with a summary fragment, never "This method returns".
- Write TODO comments as `TODO: <link to an issue> - <explanation>`; do not name a person or team as the context.
- Test observable behavior through public APIs; do not test private methods or assert on call order unless the interaction is the behavior.
- Prefer real implementations, then hand-written fakes; use Mockito only for boundaries you cannot fake.
- Keep unit tests deterministic: no real network, clock, sleeps, or randomness without an injected fake or a fixed seed.
- Give each test one behavior and a name stating scenario and expected result; keep loops and conditionals out of test bodies and use `@ParameterizedTest` for repeated inputs.
- Place tests under `src/test/java` in the production class's package, in a class named `<ClassUnderTest>Test`.

## Adaptation points

- Groovy build scripts (`build.gradle`): write the same configuration in Groovy syntax, for example `id 'com.diffplug.spotless' version '...'`, `errorprone 'com.google.errorprone:error_prone_core:...'`, and `tasks.withType(JavaCompile).configureEach { options.compilerArgs.addAll(['-Xlint:all', '-Werror']) }`.
- Multi-project Gradle builds: apply the fragment in each Java subproject, or in the convention plugin the build already uses for shared configuration.
- Maven builds with a `maven-compiler-plugin` that forks the compiler (`<fork>true</fork>`) or uses `maven-toolchains-plugin`: pass the `.mvn/jvm.config` flags as `-J` compiler arguments instead, as the Error Prone installation documentation shows.
- Maven builds compiled with a JDK newer than 21: remove `-XDaddTypeAnnotationsToSymbol=true` when the Error Prone installation documentation no longer requires it.
- Annotation processors that make `-Xlint:all` warn, such as unclaimed annotations: narrow the option by excluding that category, for example `-Xlint:all,-processing`.
- Android Gradle projects with Java sources: Spotless cannot detect Android source sets, so add `target("src/*/java/**/*.java")` to the `java` block.
- The `google` fragments enable Error Prone checks that fail on existing code, such as `UngroupedOverloads` and `MissingDefault`; report the findings instead of removing a check.
- The `google` Gradle fragment starts with an `import` line: when merging it, keep that line at the top of the build file.
- Mockito, when the application needs it: on JDK 21 or newer attach its agent with `-javaagent` through a Gradle `jvmArgumentProviders` entry or the Surefire `argLine`, as the Mockito documentation shows.

## Existing tooling

- An existing Spotless, google-java-format, or Palantir Java Format setup covers formatting.
- An existing Error Prone, Checkstyle, PMD, SpotBugs, or NullAway setup covers linting; keep the existing compiler arguments.
- Android Gradle projects: Android Lint covers linting.
- An existing test framework or runner (JUnit 4, JUnit 5, TestNG) stays; add JUnit 6 only when none exists.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: the formatter through Spotless, Error Prone, and `javac` warnings as errors, configured in the build file, for formatting and linting; the Java compiler for type checking; and JUnit. Documentation-comment sentence: Documentation comments use Javadoc `/** ... */` blocks.
