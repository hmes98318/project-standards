# Go Toolchain Profile

## Detection

A `go.mod` with `.go` sources.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [Effective Go](https://go.dev/doc/effective_go) and [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments) | golangci-lint v2 `standard` linters plus low-noise bug, modernization, and test linters, `gofumpt`, imports grouped by `gci`, package `testing` with `go-cmp` |
| `google` | [Google Go Style Guide](https://google.github.io/styleguide/go/) | the `recommended` linters plus `nakedret`, explicit revive rules for Google naming and documentation decisions, staticcheck naming checks, doc comments required on exported names, assertion libraries banned in tests |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter | golangci-lint v2 formatters `gofumpt` and `gci` | `recommended/golangci.yml` | `.golangci.yml` |
| `recommended` | Linter | golangci-lint v2 | `recommended/golangci.yml` | `.golangci.yml` |
| `google` | Formatter | golangci-lint v2 formatters `gofmt` and `gci` | `google/golangci.yml` | `.golangci.yml` |
| `google` | Linter | golangci-lint v2 with the revive rules and staticcheck checks in the template | `google/golangci.yml` | `.golangci.yml` |
| both | Type checker | Go compiler | none | none |
| both | Test framework | package `testing` from the standard library, run as `go test -race -shuffle=on ./...` | none | none |
| both | Coverage (optional) | `go test -coverprofile=coverage.out ./...`, summarized with `go tool cover -func=coverage.out` | none | none |

## Install

golangci-lint v2 lies outside the project: when it is not installed, report its binary installation from the official installation documentation, not `go install`.

Tests use package `testing`, which needs no installation, so setup adds no test dependency. A change that compares structured values adds `github.com/google/go-cmp` with `go get` in the same change that first imports it.

## Commands

| Command | Invocation |
| --- | --- |
| `format` | `golangci-lint fmt` |
| `lint` | `golangci-lint run` |
| `typecheck` | `go build -o /dev/null ./...` |
| `test` | `go test -race -shuffle=on ./...` |
| `verify` | `golangci-lint fmt --diff && golangci-lint run && go build -o /dev/null ./...` |

## Import order

`gci` sorts each group alphabetically and separates groups with one blank line.

- `recommended`: standard library, then third-party modules, then packages of the current module.
- `google`: standard library, then all other packages, then blank (`_`) imports for side effects.

## Style rules

### recommended

- Wrap an error only when callers may need to inspect it, and add context that the caller does not already have.
- Accept interfaces and return concrete types. Define an interface in the package that consumes it, and only when more than one implementation exists or is needed for tests.
- Pass `context.Context` as the first parameter of functions that do I/O or may block.
- Name packages with short lowercase words; never `util`, `common`, `helpers`, or `misc`.
- Do not panic for errors a caller can handle; reserve `panic` for programmer errors and impossible states.
- Start goroutines only with a defined way to stop them and to report their errors.
- Write table-driven tests with a descriptive name per case run through `t.Run`; call `t.Parallel()` only when cases share no state.
- Compare structured values with `cmp.Diff` from `go-cmp`, not `reflect.DeepEqual`, and report failures as `YourFunc(%v) = %v, want %v`.
- Keep unit tests hermetic and deterministic: no network, real clock, or shared mutable state; use `httptest`, `t.TempDir()`, and fakes for external dependencies.
- Prefer the real implementation or a small hand-written fake to a mock or a generated mock.

### google

- Name packages with short lowercase words that describe what they provide; avoid uninformative names such as `util`, `common`, `helper`, and `model`.
- Do not prefix getters with `Get`; name them after the value they return.
- Keep names proportional to scope: short names for small scopes, descriptive names for package-level identifiers. Do not repeat the package name in exported identifiers.
- Take the `context.Context` from the caller; call `context.Background()` only in entry points such as `main` and `init`.
- Return an error instead of calling `panic` for conditions a caller can handle.
- Use named result parameters only when they document the meaning of several values of the same type.
- Use `MustXxx` functions only during program initialization or in test helpers.
- Use generics only when the same code would otherwise be repeated for several types.
- Define an interface in the package that consumes it, with only the methods the consumer uses, and return concrete types.
- Give every goroutine an obvious lifetime: a defined way to stop it, and documentation of when and why it exits.
- Write doc comments as complete, capitalized, punctuated sentences.
- In tests, use `t.Error` and keep checking; use `t.Fatal` only when later checks cannot run. Report failures as `YourFunc(%v) = %v, want %v` and compare structured values with `cmp.Diff`.
- Write table-driven tests with a descriptive name per case run through `t.Run`; call `t.Parallel()` only when cases share no state.
- Keep unit tests hermetic and deterministic: no network, real clock, or shared mutable state; use `httptest`, `t.TempDir()`, and fakes for external dependencies.
- Prefer the real implementation or a small hand-written fake to a mock or a generated mock.

## Adaptation points

- A module that is not at the application directory root: run the commands from the module directory.
- A repository with several Go modules governed as one application: run the commands in each module, or list the modules in a `go.work` file.
- `google` with the `None` code-comment policy: add `comments` to `linters.exclusions.presets` so missing doc comments are not reported.
- `-race` unavailable (`CGO_ENABLED=0`, no C compiler on a non-macOS system, or an unsupported platform): remove `-race` from `test`.
- `google` with an application that already uses `testify`, `gomega`, or `gotest.tools` in tests: remove the `tests` rule from `linters.settings.depguard.rules`.

## Existing tooling

- An existing `.golangci.yml`, `.golangci.yaml`, `.golangci.toml`, or `.golangci.json` covers linting and, when it enables formatters, formatting. A v1 configuration stays; do not migrate it to v2 during setup.
- Formatting checked with `gofmt -l` or `goimports` in CI covers formatting.
- A test setup already in use (package `testing` with `testify`, `gomega`, `gotestsum`, or `go test` wrappers in a Makefile or CI) covers testing; keep it and run it with its own invocation. `testifylint` reports misuse of `testify` in the `recommended` variant.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: golangci-lint (`.golangci.yml`) for formatting and linting, the Go compiler for type checking, and package `testing`. Documentation-comment sentence: Documentation comments use `//` comments directly above the declaration.
