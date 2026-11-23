# Flutter and Dart Toolchain Profile

## Detection

A `pubspec.yaml` with `.dart` sources. The Flutter application owns its `android/`, `ios/`, `web/`, and desktop host directories; do not apply the `android`, `ios`, `kotlin`, or `swift` profiles to them.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Effective Dart](https://dart.dev/effective-dart) | `dart format` (tall style, 80 columns), the official `flutter_lints` set with strict analyzer modes and a few low-noise rules, `--fatal-infos` analysis |

Effective Dart is the Dart guide listed in [Google's style guide index](https://google.github.io/styleguide/), so a `google` choice uses `recommended` and needs no report.

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter | `dart format`, default tall style | none | none |
| `recommended` | Linter and type checker | Dart analyzer with `flutter_lints`, strict modes, and the rules in the template | `recommended/analysis_options.yaml` | `analysis_options.yaml` |
| `recommended` | Test framework | `flutter_test` for unit and widget tests and `integration_test` for integration tests, both from the Flutter SDK, run with `flutter test`; `package:test` with `dart test` for pure Dart | none | none |
| `recommended` | Coverage (optional) | `flutter test --coverage`, which writes `coverage/lcov.info` | none | none |

## Install

The `flutter_lints` development dependency: `flutter pub add dev:flutter_lints`. Pure Dart packages use `dart pub add dev:lints` instead.

When the testing policy requires tests and none exists, Flutter applications add `flutter_test` with `flutter pub add "dev:flutter_test:{sdk: flutter}"`, and `integration_test` the same way only when the policy requires integration tests; pure Dart packages run `dart pub add dev:test`.

## Commands

Pure Dart packages replace `flutter` with `dart` in `lint`, `test`, and `verify`.

| Command | Invocation |
| --- | --- |
| `format` | `dart fix --apply && dart format .` |
| `lint` | `flutter analyze --fatal-infos` |
| `typecheck` | covered by `lint` |
| `test` | `flutter test` |
| `verify` | `dart format --output=none --set-exit-if-changed . && flutter analyze --fatal-infos` |

## Import order

`directives_ordering` enforces the Effective Dart order, autofixable with `dart fix --apply`: `dart:` imports, then `package:` imports, then relative imports, each section sorted alphabetically and separated by one blank line, with exports in a separate section after all imports. `prefer_relative_imports` requires relative paths for libraries inside the package's own `lib/` directory.

## Style rules

### recommended

- Keep widgets small and composable: extract a widget class instead of a helper method that returns a widget.
- Keep business logic and I/O out of widgets; expose state to the UI through the application's chosen state-management approach, and keep widgets free of side effects in `build`.
- Check `mounted` before calling `setState` after an `await`.
- Dispose of every controller, stream subscription, and animation in `dispose()`.
- Build long or unbounded lists with lazy builders such as `ListView.builder`, not with a concrete list of children.
- Avoid the null assertion `!`; use null-aware operators or null checks that promote.
- Write a doc comment for each public API, starting with a single-sentence summary.
- Explain parameters, return values, and exceptions in prose in doc comments; do not use `@param` tags or parameter lists.
- Keep tests deterministic: no real network, clock, or timers; inject clients and clocks, and advance time with `pump(Duration)` or `fakeAsync`, not real delays.
- Prefer real objects or hand-written fakes over mocks; use `mocktail` only at I/O boundaries, and assert on state rather than call sequences.
- Mirror `lib/` under `test/` with files named `<source>_test.dart`, and group related cases with `group()`.

## Adaptation points

- Pure Dart packages: replace the `include` line with `include: package:lints/recommended.yaml`.
- Packages whose existing code consistently imports its own libraries with `package:` paths: replace `prefer_relative_imports` with `always_use_package_imports`, and report the choice.
- Generated files, such as `*.g.dart` and `*.freezed.dart`: add them to `analyzer.exclude`.
- Packages whose `environment: sdk` lower bound is below 3.7: `dart format` then uses the old short style instead of the tall style; raise the bound before formatting, or report it.
- Published packages: add `public_member_api_docs` to `linter.rules`.
- Applications that deliberately omit the `prefer_const_*` rules, as `flutter_lints` does: remove `prefer_const_constructors` and `prefer_const_declarations` from `linter.rules`.

## Existing tooling

- An existing `analysis_options.yaml` covers linting and type checking; keep it. A different lint package, such as `very_good_analysis`, stays.
- `dart format` is always the formatter; existing `formatter` settings in `analysis_options.yaml` stay.
- An existing test framework or runner stays, including `mockito` with its generated mocks and `package:test`. Add `mocktail` only when a test needs a mock.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: `dart format` with default settings for formatting, the Dart analyzer (`analysis_options.yaml`) for linting and type checking, and `flutter test`. Documentation-comment sentence: Documentation comments use `///` comments.
