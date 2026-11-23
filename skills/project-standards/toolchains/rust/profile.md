# Rust Toolchain Profile

## Detection

A `Cargo.toml` with `.rs` sources.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [The Rust Style Guide](https://doc.rust-lang.org/style-guide/) and [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/) | rustfmt defaults, Clippy `pedantic` with documentation and `must_use` lints relaxed, `dbg!` and `todo!` reported, missing `Debug` on public types reported, `unsafe` forbidden |
| `google` | [Google Rust Style Guide](https://google.github.io/styleguide/rustguide.html) | the `recommended` toolchain plus rustfmt `max_width` and `hex_literal_case`, `missing_docs`, and Clippy `exhaustive_enums`, `exhaustive_structs`, and `undocumented_unsafe_blocks`, as the guide asks for documented public APIs, `#[non_exhaustive]` on public API types, and `SAFETY:` comments |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter | rustfmt, default style | none | none |
| `google` | Formatter | rustfmt with the options in the template | `google/rustfmt.toml` | `rustfmt.toml` |
| `recommended` | Linter | Clippy with the lint levels in the template | `recommended/Cargo.fragment.toml` | `Cargo.toml` (merge) |
| `google` | Linter | Clippy and rustc lints with the levels in the template | `google/Cargo.fragment.toml` | `Cargo.toml` (merge) |
| both | Type checker | Rust compiler, through Clippy | none | none |
| both | Test framework | Cargo's built-in test framework, run by `cargo test` | none | none |
| both | Coverage (optional) | cargo-llvm-cov: `cargo llvm-cov --workspace --all-features` | none | none |

## Install

The `rustfmt` and `clippy` components: `rustup component add rustfmt clippy`. Cargo ships the test framework, so tests need no installation. Coverage needs `cargo-llvm-cov` (rustc 1.87 or newer), a tool outside the project: report `cargo install cargo-llvm-cov --locked`, only when the user asks for coverage.

## Commands

| Command | Invocation |
| --- | --- |
| `format` | `cargo fmt --all` |
| `lint` | `cargo clippy --workspace --all-targets --all-features -- -D warnings` |
| `typecheck` | covered by `lint` |
| `test` | `cargo test --workspace --all-features` |
| `verify` | `cargo fmt --all --check && cargo clippy --workspace --all-targets --all-features -- -D warnings` |

`cargo test` runs unit, integration, and documentation tests.

## Import order
rustfmt sorts `use` declarations alphabetically within each group of consecutive lines but never moves them across blank lines, and its options that regroup or merge imports are unstable, so the grouping is a Style rule.

## Style rules

### recommended

- Return `Option` when absence is the only failure and `Result` when the caller needs the cause; reserve `panic!`, `unwrap`, and `expect` for invariant violations, with an `expect` message that states the invariant.
- Define error types with an enum per module or crate boundary; do not return `Box<dyn Error>` from library APIs.
- Document in `# Errors` and `# Panics` sections the failure modes of public functions that are not evident from their signature.
- Do not prefix getters with `get_`; name a getter after the field it returns.
- Write documentation examples with `?` instead of `unwrap`.
- Put unit tests in a `#[cfg(test)] mod tests` in the file under test, and integration tests in `tests/` that use only the public API.
- Keep unit tests hermetic: no network access, wall-clock time, or unseeded randomness, and write files only to a temporary directory.
- Name each test after the behavior it checks, assert one behavior per test, and drive repeated cases from a table of rows whose assertion message names the input.
- Group `use` declarations into three blocks separated by one blank line, in this order: `std`, `core`, and `alloc`; external crates; then `crate`, `super`, and `self` paths.

### google

- Return `Option` when the cause of failure is obvious, `Result` when the caller needs the cause to recover, and `panic!` only for bugs and violated invariants.
- Document in a `# Panics` section every public function that can panic on malformed input.
- When a panic is required, use `expect` with a message that states the invariant, never a bare `unwrap`.
- Import types by name and call free functions through their module (`use std::fs; fs::read(...)`).
- Prefer unique ownership and borrowing over `Rc` and `Arc`; use them only when the alternative is unreasonably complex.
- Use `.clone()` only for a genuine deep copy, never as a substitute for borrowing.
- Define a trait only to enable generic programming, to accept or return `impl Trait` or `dyn Trait`, or as an extension trait; otherwise use inherent methods.
- Allow `exhaustive_enums` or `exhaustive_structs` only on types that are not used by other teams, will never change, or must support struct update syntax, and give the `reason`.
- Do not take `impl Into<T>` parameters in application code; in libraries use them only when call-site ergonomics matter.
- Add `#[must_use]` to functions whose result must not be ignored, including pure functions, and to error types and lazily evaluated computations.
- Use an `enum` instead of a `bool` parameter when the argument's meaning is not obvious at the call site; otherwise comment the argument.
- Annotate the type of variables that receive `.into()`, `.parse()`, or a complex iterator chain, on the variable rather than in a turbofish.
- Keep unit tests hermetic: no network access, wall-clock time, or unseeded randomness, and write files only to a temporary directory.
- Prefer real implementations, then in-process fakes, then mocks; use `mockall` only at trait boundaries that cannot run in-process.
- Put unit tests in a `#[cfg(test)] mod tests` in the file under test, and integration tests in `tests/` that use only the public API.
- Group `use` declarations into three blocks separated by one blank line, in this order: `std`, `core`, and `alloc`; external crates; then `crate`, `super`, and `self` paths.

## Adaptation points

- A Cargo workspace: put the fragment's tables under `[workspace.lints.rust]` and `[workspace.lints.clippy]` in the workspace `Cargo.toml`, and add `[lints]` with `workspace = true` to every member.
- An application that requires `unsafe` code, such as FFI bindings: set `unsafe_code` to `"deny"` instead of `"forbid"`, so each `unsafe` block needs a local `#[allow(unsafe_code)]` with a reason; in `recommended`, also add `undocumented_unsafe_blocks = "warn"` to `[lints.clippy]`.
- A dependency whose macro fails the build with error E0453 under `forbid`: set `unsafe_code` to `"deny"` instead of `"forbid"`.
- Cargo features that are mutually exclusive or nightly-only: remove `--all-features` from `lint`, `test`, and `verify`.
- `google` for a binary crate, or with the `None` code-comment policy: remove `missing_docs`.

## Existing tooling

- A `[lints]` table, `clippy.toml`, or crate-level `#![warn(...)]` or `#![deny(...)]` attributes cover linting.
- A `rustfmt.toml` or `.rustfmt.toml` covers formatting.
- An existing test runner or test crate, such as `cargo-nextest` (`.config/nextest.toml`), `googletest`, `rstest`, or `proptest`, covers the test framework. Keep it; `cargo-nextest` does not run documentation tests, so keep `cargo test --doc` as well.
- An existing coverage tool, such as `cargo-tarpaulin`, covers coverage. Keep it.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: rustfmt (default settings in `recommended`, `rustfmt.toml` in `google`) for formatting, Clippy with the `[lints]` table in `Cargo.toml` for linting, the Rust compiler through Clippy for type checking, and Cargo's test framework or the existing test runner. Documentation-comment sentence: Documentation comments use `///` for items and `//!` for modules and crates.
