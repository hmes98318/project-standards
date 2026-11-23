# Python Toolchain Profile

## Detection

A `pyproject.toml`, `requirements*.txt`, `setup.py`, `setup.cfg`, or `Pipfile` with `.py` sources.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [PEP 8](https://peps.python.org/pep-0008/) and [PEP 257](https://peps.python.org/pep-0257/) | Ruff formatter defaults (88 columns), Ruff lint rules with broad community adoption, strict mypy, pytest |
| `google` | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) | Ruff formatter at 80 columns, Google docstring convention, one import per line, absolute imports only, strict mypy, pytest |

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| both | Formatter | Ruff formatter | the variant's `ruff.toml` | `ruff.toml` |
| `recommended` | Linter | Ruff | `recommended/ruff.toml` | `ruff.toml` |
| `google` | Linter | Ruff, including pydocstyle with the `google` convention | `google/ruff.toml` | `ruff.toml` |
| both | Type checker | mypy in strict mode | `shared/mypy.ini` | `mypy.ini` |
| both | Test framework | pytest, run as `pytest --strict -ra -W error` | none | none |
| both | Coverage (optional) | pytest-cov with branch coverage: `pytest --cov=<package> --cov-branch --cov-report=term-missing` | none | none |

## Install

Development dependencies: `ruff`, `mypy`, plus the type-stub packages mypy reports as missing for the application's dependencies. When the testing policy requires tests and none exists, also `pytest` 9 or later, plus `pytest-cov` only when the user asks for coverage.

Add them with the application's dependency manager, for example `uv add --dev`, `poetry add --group dev`, or the development requirements file it already uses.

## Commands

Prefix each command with the environment runner the application uses, such as `uv run` or `poetry run`.

| Command | Invocation |
| --- | --- |
| `format` | `ruff check --fix --select I . && ruff format .` |
| `lint` | `ruff check .` |
| `typecheck` | `mypy .` |
| `test` | the application's existing test runner; when the testing policy requires tests and none exists, add the `pytest` development dependency (version 9 or later) and run `pytest --strict -ra -W error` |
| `verify` | `ruff format --check . && ruff check . && mypy .` |

## Import order

Both variants sort imports with Ruff's isort rules (`I`) into blank-line-separated sections: `__future__` imports, standard library, third-party packages, first-party packages, then local relative imports. Ruff detects first-party packages from the project root and its `src/` directory.

- `recommended` sorts `import x` statements before `from x import y` statements within each section and combines `from` imports of one module into a single statement.
- `google` writes one import per line, except for names from `typing`, `collections.abc`, and `typing_extensions`, sorts each section lexicographically by full module path regardless of import form, and bans relative imports.

## Style rules

### recommended

- Follow PEP 8 for naming and layout that the formatter and linter do not decide.
- Annotate every module-level or class-level variable whose type is not obvious from its value.
- Catch the most specific exception type that can occur. Catch `Exception` only at a process or request boundary that logs the error or converts it into a response.
- Do not use mutable module-level state for data that changes at runtime; pass it explicitly or hold it in an object.
- Write tests as plain `pytest` functions named `test_<unit>_<behavior>` in `tests/test_<module>.py`; use `assert`, fixtures, and `@pytest.mark.parametrize` for repeated cases.
- Keep unit tests deterministic and independent: no network, real clock, or shared mutable state; use `tmp_path`, `monkeypatch`, test doubles, and explicit random seeds.
- Prefer real or in-memory implementations to mocks; mock only at the system boundary and assert on observable behavior, not on implementation details.

### google

- Import packages and modules, not classes or functions, except names from `typing`, `collections.abc`, and `typing_extensions`. Use `import module as alias` only for standard abbreviations and `from package import module as alias` for name conflicts.
- Use descriptive names: no unfamiliar abbreviations, no single-character names except `i`, `j`, `k`, `e`, `f`, and standard mathematical notation, and no type in the name (`id_to_name_dict`).
- Do not use mutable global state. Module-level constants use `CONSTANT_CASE`.
- Use implicit false for sequences and strings (`if not items:`).
- Keep `try` blocks minimal. Do not use `assert` to validate arguments or other preconditions.
- Format strings with f-strings, `%`, or `str.format()`, not `+`; accumulate pieces in a list and `''.join` it instead of using `+=` in a loop.
- Keep comprehensions and generator expressions to one `for` clause and at most one filter; use a loop otherwise.
- Make an attribute public instead of writing a getter and setter that only read and write it; use `@property` only for cheap, unsurprising computations.
- Do not use `@staticmethod`; write a module-level function. Use `@classmethod` only for named constructors.
- Document public functions with `Args:`, `Returns:` or `Yields:`, and `Raises:` sections, and public class attributes in an `Attributes:` section; omit sections the signature makes obvious.
- Write `TODO` comments as `# TODO(<link to a bug or other context>): <explanation>`; do not name a person or team.
- Prefer small, focused functions; consider splitting a function that exceeds about 40 lines.
- Write tests as plain `pytest` functions named `test_<unit>_<behavior>` in `tests/test_<module>.py`; use `assert`, fixtures, and `@pytest.mark.parametrize` for repeated cases.
- Keep unit tests deterministic and independent: no network, real clock, or shared mutable state; use `tmp_path`, `monkeypatch`, test doubles, and explicit random seeds.
- Prefer real or in-memory implementations to mocks; mock only at the system boundary and assert on observable behavior, not on implementation details.

## Adaptation points

- An application that keeps tool configuration in `pyproject.toml` `[tool.*]` sections: put the same settings under `[tool.ruff]`, `[tool.ruff.lint]`, and `[tool.mypy]` instead of creating `ruff.toml` and `mypy.ini`.
- No `requires-python` in `pyproject.toml`: set `target-version` at the top of `ruff.toml` to the application's minimum Python version, for example `target-version = "py312"`.
- Source layouts where `mypy .` finds duplicate modules, or where only some directories are typed: replace `.` in `typecheck` and `verify` with the application's package and test directories.
- `google` with the `None` code-comment policy: add `"D1"` to `ignore` so missing docstrings are not reported; the other docstring rules still check docstrings that exist.
- Tests that use custom `pytest` markers: register them in the application's `pytest` configuration (`[tool.pytest]` in `pyproject.toml`, or `pytest.toml`), because `--strict` rejects unregistered markers.
- A dependency emits warnings the application cannot fix: append `-W` ignore filters after `-W error` in `test`, for example `-W ignore::DeprecationWarning:<module>`; `filterwarnings` in the `pytest` configuration cannot override `-W error`.
- Tests outside `tests/` or test files not named `test_*.py` or `*_test.py`: extend the `per-file-ignores` globs in `ruff.toml` to the application's test paths.

## Existing tooling

- Black, isort, Flake8, or Pylint configured: keep each one for the concern it covers. Ruff covers only the concerns none of them covers.
- Pyink, or Black with `line-length = 80`, covers formatting for the `google` variant.
- Pyright, basedpyright, or Pyrefly configured (`pyrightconfig.json`, `pyrefly.toml`, or a `[tool.pyright]` or `[tool.pyrefly]` table) covers type checking.
- A test framework or runner already in use (`pytest`, `unittest`, or `tox` and `nox` test environments) covers testing; keep it and run it with its own invocation.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: Ruff (`ruff.toml`) for formatting and linting, strict mypy (`mypy.ini`) for type checking, and pytest or the application's test framework. Documentation-comment sentence: Documentation comments use triple-quoted docstrings.
