# Shell Toolchain Profile

## Detection

`.sh`, `.bash`, or `.bats` files, or executable files with a `sh` or `bash` shebang; the inspector counts only the files with those extensions, so look for extensionless shebang scripts in directories such as `bin/` and `scripts/` yourself. Shell scripts usually belong to the application whose directory contains them; repository-level scripts belong to the repository root scope.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [ShellCheck wiki](https://www.shellcheck.net/wiki/) and shfmt conventions | shfmt with two-space indentation and indented `case` items, ShellCheck with every default check plus two low-noise optional checks, Bats for tests |
| `google` | [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) | the `recommended` toolchain plus shfmt line breaks before binary operators, and ShellCheck checks that require `[[ ]]`, `${var}` braces, and quoting every variable, with Bash as the only dialect |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter | shfmt, configured through EditorConfig | `recommended/editorconfig` | `.editorconfig` (merge) |
| `recommended` | Linter | ShellCheck | `recommended/shellcheckrc` | `.shellcheckrc` |
| `google` | Formatter | shfmt, configured through EditorConfig | `google/editorconfig` | `.editorconfig` (merge) |
| `google` | Linter | ShellCheck with the Google optional checks and the Bash dialect | `google/shellcheckrc` | `.shellcheckrc` |
| both | Type checker | none; ShellCheck covers static analysis | none | none |
| both | Test framework | Bats (bats-core) with `bats-support` and `bats-assert` | none | none |

## Install

ShellCheck and shfmt lie outside the project: when they are not installed, report their installation from the system package manager.

When the testing policy requires tests and none exists, report Bats (bats-core) with `bats-support` and `bats-assert` as tools to install from the system package manager; setup adds no files for them.

## Commands

| Command | Invocation |
| --- | --- |
| `format` | `shfmt -w .` |
| `lint` | `shfmt -f . \| xargs shellcheck` |
| `typecheck` | none |
| `test` | the application's existing shell test runner; when the testing policy requires tests and none exists, add `bats --recursive --print-output-on-failure test` |
| `verify` | `shfmt -d . && shfmt -f . \| xargs shellcheck` |

`shfmt -f .` lists every shell file below the directory, including `.bats` files and extensionless scripts detected by their shebang, and skips the directories that the ignore section of `.editorconfig` names.

## Import order
Shell has no imports, so the placement of `source` lines is a Style rule.

## Style rules

### recommended

- Start every script with an explicit shebang, `#!/usr/bin/env bash` for Bash or `#!/bin/sh` for POSIX scripts, start sourced libraries with `# shellcheck shell=bash`, and keep Bash features out of `sh` scripts.
- Begin Bash scripts with `set -euo pipefail`, and handle expected failures explicitly with `if` or `|| true` plus a comment.
- Put logic in functions, declare function variables with `local`, and end scripts that define functions with `main "$@"` inside an `if [[ "${BASH_SOURCE[0]}" == "${0}" ]]` guard so tests can source them.
- Create temporary files and directories with `mktemp`, and remove them in a `trap ... EXIT` handler.
- Write error messages to standard error and exit with a non-zero status.
- Use arrays, not strings, for lists and command arguments, and expand them as `"${array[@]}"`.
- Make each Bats test hermetic: use `$BATS_TEST_TMPDIR` for files, stub external commands with scripts on a temporary `PATH`, and never depend on the real home directory, network, clock, or locale.
- Test scripts with Bats `run`, assert on exit status and output with `bats-assert`, and name each `@test` after the behavior and its expected outcome.
- Put `source` lines at the top of the script, after the header comment and `set` options, and give ShellCheck a `# shellcheck source=path` directive when the sourced path is computed.

### google

- Check the return value of every command that can fail with an informative message, and write error messages to standard error.
- Use arrays, not strings, for lists and command arguments, and expand them as `"${array[@]}"`.
- Declare function-local variables with `local`.
- Put all functions together near the top of the file after constants, and call `main "$@"` as the last line of scripts that contain at least one other function.
- Keep lines to at most 80 characters, put long literal strings in here-documents, and leave unsplittable paths and URLs on their own line.
- Name functions and variables in `lower_snake_case`, separate library names with `::`, and name constants and exported environment variables in `UPPER_SNAKE_CASE`, declared at the top of the file with `readonly` or `export`.
- Name source files in lowercase with underscores, not hyphens, as in `make_template`, not `make-template`.
- Start each file with a top-level comment describing its contents.
- Comment every library function and every other function that is not both obvious and short, describing its globals, arguments, outputs, and non-default return values.
- Use Bash for executable scripts (`#!/bin/bash`), keep shell for small utilities and wrappers, and rewrite a script that exceeds about 100 lines or uses complex control flow in a structured language.
- Test scripts as black boxes through Bats: `run` the executable, assert on exit status and output with `bats-assert`, and name each `@test` after the behavior and its expected outcome.
- Make each Bats test hermetic: use `$BATS_TEST_TMPDIR` for files, stub external commands with scripts on a temporary `PATH`, and never depend on the real home directory, network, clock, or locale.
- Use process substitution or `readarray` instead of piping into `while`.
- Do not use `eval` or aliases in scripts.
- Give executables a `.sh` extension or no extension, and give libraries a `.sh` extension without making them executable.
- Put `source` lines at the top of the script, after the header comment and `set` options, and give ShellCheck a `# shellcheck source=path` directive when the sourced path is computed.

## Adaptation points

- An existing `.editorconfig`: add the fragment's `[*.{sh,bash,bats}]` section and its ignore section, or their properties to existing sections for those files.
- Extensionless scripts: add an EditorConfig section that names their paths, for example `[bin/*]`, with the same properties; the `.bats` extension is already covered.
- Scripts that must run under `sh`: keep their `#!/bin/sh` shebang; ShellCheck and shfmt then apply POSIX rules to them. In `google`, remove `shell=bash` from `.shellcheckrc` first, because it overrides the shebang and disables the POSIX checks.
- Other vendored or generated script directories: add them to the brace list of the `ignore = true` section of `.editorconfig`; shfmt skips them for `shfmt -f .` and `shfmt -d .`.
- Bats tests in a directory other than `test/`: use that directory in the `test` command.

## Existing tooling

- An existing `.shellcheckrc` or ShellCheck step in CI covers linting.
- An existing shfmt configuration, or shfmt flags in CI or a task runner, covers formatting.
- An existing shell test framework or runner, such as Bats, ShellSpec, or shunit2, stays: its invocation is the `test` command, and Bats is not added.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: shfmt (`.editorconfig`) for formatting, ShellCheck (`.shellcheckrc`) for linting, no type checker, and Bats or the application's test framework. Documentation-comment sentence: Documentation comments use `#` comments.
