# Toolchain Profiles

A toolchain profile is a fixed setup of the formatter, linter, type checker, and test framework for one language, with the configuration files, the commands that run them, the import order, and the style rules that tools cannot check. Applying the same profile gives every project the same tools, configuration, and rules, so generated standards do not vary between runs and no style guide has to be researched during setup.

Profiles exist for TypeScript and JavaScript, Python, Go, Rust, Java, Kotlin, C#, Swift, Flutter and Dart, and shell scripts. The Android and iOS profiles extend the Kotlin and Swift profiles with Android Lint and Xcode build checks. The tools of each profile are listed in the catalog in [references/toolchains.md](../skills/project-standards/references/toolchains.md), and each profile's files are under `skills/project-standards/toolchains/<language>/`.

## Variants

Each profile has a `recommended` variant, the default, which follows the language's official conventions with the tooling most widely adopted for it. The `google` variant follows the language's [Google Style Guide](https://google.github.io/styleguide/) and enforces it through configuration wherever a tool can, leaving the remaining rules as written style rules. Flutter has only the `recommended` variant, because Effective Dart is the Dart guide listed in Google's style guide index, so it also serves a Google Style Guide choice.

## Which Profiles Apply

An application uses one profile for every language with source files in it, not only its main language: a Flutter application with release scripts uses the Flutter and shell profiles. A secondary profile governs only its own files, and generated or vendored code and the host folders of a Flutter application are left out.

## How a Profile Is Applied

The skill offers a profile only for concerns that have no enforced tooling, and tooling the repository already enforces always stays. Applying a profile:

1. copies the configuration templates of the chosen variant, changing only the points each profile marks as adaptable;
2. adds the development dependencies the application does not declare, resolved to the latest stable releases through the package manager so that no version is typed from memory;
3. records the `format`, `verify`, and `test` commands in the application's `AGENTS.md`;
4. runs `verify` and reports any failures in existing code, without changing application source and without weakening a rule.

A test framework is added only when the testing policy requires tests and the application has none. Setup installs no SDKs or tools outside the project; when one is missing, it reports the tool with its install command and does not run `verify`.
