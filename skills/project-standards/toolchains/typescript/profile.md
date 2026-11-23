# TypeScript and JavaScript Toolchain Profile

## Detection

A `package.json` with `.ts`, `.tsx`, `.mts`, `.cts`, `.js`, `.jsx`, `.mjs`, or `.cjs` sources, managed by npm, pnpm, Yarn, or Bun. Deno applications (`deno.json`) are not covered: use Deno's built-in `deno fmt`, `deno lint`, and `deno check`.

## Variants

| Variant | Style authority | Summary |
| --- | --- | --- |
| `recommended` | [typescript-eslint recommended configurations](https://typescript-eslint.io/users/configs) and Prettier defaults | Prettier defaults, ESLint with typescript-eslint `strictTypeChecked` and `stylisticTypeChecked`, sorted imports, type-only imports, strict TypeScript, Vitest for tests |
| `google` | [Google TypeScript Style Guide](https://google.github.io/styleguide/tsguide.html) | the `recommended` toolchain with the Prettier options of Google's `gts`, plus ESLint rules for the guide's export, naming, function, class, enum, coercion, assertion, and `@ts-` comment decisions |

The Google JavaScript Style Guide states that it is no longer being updated and recommends migrating to TypeScript and following the TypeScript guide, so JavaScript applications use the same variants.

## Toolchain

| Variant | Concern | Tool | Template | Target |
| --- | --- | --- | --- | --- |
| `recommended` | Formatter | Prettier, default options | `recommended/prettierrc.json` | `.prettierrc.json` |
| `recommended` | Linter | ESLint with typescript-eslint, perfectionist, and `globals` for JavaScript files | `recommended/eslint.config.mjs` | `eslint.config.mjs` |
| `google` | Formatter | Prettier with the `gts` options | `google/prettierrc.json` | `.prettierrc.json` |
| `google` | Linter | ESLint with typescript-eslint, perfectionist, `globals` for JavaScript files, and the Google rules | `google/eslint.config.mjs` | `eslint.config.mjs` |
| both | Formatter ignore | Prettier ignore list | `shared/prettierignore` | `.prettierignore` (merge) |
| both | Type checker | TypeScript compiler, strict options | `shared/tsconfig.fragment.json` | `tsconfig.json` (merge) |
| both | Test framework | Vitest, run once with `vitest run` | none | none |
| both | Coverage (optional) | `@vitest/coverage-v8`, run with `vitest run --coverage` | none | none |
| both | Commands | `package.json` scripts | `shared/package.fragment.json` | `package.json` (merge) |

## Install

Development dependencies: `prettier`, `eslint`, `@eslint/js`, `typescript-eslint`, `eslint-plugin-perfectionist`, `globals`, `typescript`. Install them in one command, and keep `typescript` within the range that the installed `typescript-eslint` declares as its peer dependency (`npm view typescript-eslint peerDependencies.typescript`): the latest `typescript` release can lie outside that range, because TypeScript 7 ships no programmatic API that typescript-eslint can use yet, so the range currently ends at the 6.0 line and the highest release inside it is the one to install. ESLint 10 requires Node.js `^20.19.0`, `^22.13.0`, or `>=24`; Vitest 5 requires Node.js `>=22.12.0`.

When the testing policy requires tests and none exists: `vitest`, plus `@vitest/coverage-v8` only when the user asks for coverage. Applications that use Vitest, existing or added, also install `@vitest/eslint-plugin` (see Adaptation points).

## Commands

Run each script with the application's package manager, for example `npm run verify` or `pnpm verify`.

| Command | Script |
| --- | --- |
| `format` | `eslint --fix . && prettier --write .` |
| `lint` | `eslint .` |
| `typecheck` | `tsc --noEmit` |
| `test` | the application's existing test runner; when the testing policy requires tests and none exists, add the script `vitest run --passWithNoTests` |
| `verify` | `prettier --check . && eslint . && tsc --noEmit` |

Prettier also formats the Markdown, JSON, YAML, and CSS files inside the application directory, except the files that `.gitignore` and `.prettierignore` list. Import order is fixed by `eslint --fix`, not by Prettier.

## Import order

Both variants enforce the same order with `perfectionist/sort-imports`, autofixable with `eslint --fix`. Groups are separated by one blank line and sorted naturally within each group:

1. Node.js built-in modules, with or without the `node:` prefix.
2. External packages.
3. Internal aliases matching `@/`, `~/`, or `#`.
4. Parent, sibling, and index imports.

A type-only import sorts into the same group as value imports from the same source. `@typescript-eslint/consistent-type-imports` requires `import type` for imports used only as types, in a separate statement.

## Style rules

### recommended

- Prefer named exports, and use a default export only where a framework or tool requires one, such as page components or configuration files.
- Narrow `unknown` values instead of asserting types, and justify every remaining type assertion with a comment unless the reason is evident from the surrounding code.
- Validate data at boundaries (network, storage, user input, environment) and give it a precise type there; trust types internally.
- Keep tests deterministic and hermetic: no real network, clock, randomness, or state shared between tests; inject dependencies and use fake timers.
- Prefer real implementations or in-memory fakes over mocks; mock only external boundaries, and assert on calls only when the call is the behavior under test.
- Test observable behavior through the public API, and name each test after the behavior and its expected outcome.
- Model alternatives with discriminated unions instead of optional fields or boolean flags.
- Use `undefined` for absent values unless an external API requires `null`.
- Do not put conditionals or loops in test bodies; express repeated cases with `it.each` tables.
- Place unit tests next to the source as `<name>.test.ts`, and put integration and end-to-end tests in `tests/`.

### google

- Name source files in `snake_case` and namespace imports in `lowerCamelCase`, as in `import * as fooBar from './foo_bar'`.
- Document every exported symbol with a `/** JSDoc */` comment that adds information beyond its name, and do not write types in `@param` or `@return`.
- Write implementation comments as `//` lines, never as multi-line `/* */` blocks.
- Export only the symbols that other modules use.
- Use type assertions only with a comment that explains why they are safe, unless the reason is obvious, and prefer a runtime check.
- Use `undefined` or `null` for absence as the surrounding API does, and do not put `|null` or `|undefined` in a type alias; add it where the alias is used.
- Keep getters pure so they never change observable state, and make a property public or `readonly` instead of writing a pass-through accessor.
- Keep tests deterministic and hermetic: no real network, clock, randomness, or state shared between tests; inject dependencies and use fake timers.
- Prefer real implementations or in-memory fakes over mocks; mock only external boundaries, and assert on calls only when the call is the behavior under test.
- Test observable behavior through the public API, and name each test after the behavior and its expected outcome.
- Do not put conditionals or loops in test bodies; express repeated cases with `it.each` tables.
- Place unit tests next to the source as `<snake_case_name>.test.ts`, and put integration and end-to-end tests in `tests/`.
- Name things descriptively, and do not use ambiguous abbreviations or abbreviations that delete letters, except for variables in scope for 10 lines or fewer.
- Prefer small, focused functions, and consider splitting a function that exceeds about 40 lines.

## Adaptation points

- JavaScript-only applications without a `tsconfig.json`: keep the template and the `typescript-eslint` and `typescript` dependencies unchanged, because typescript-eslint also lints JavaScript files; do not merge the tsconfig fragment, and drop `typecheck` and the `tsc` part of `verify`.
- Applications that use Node.js, DOM, or other ambient types: list them in `compilerOptions.types` of the merged tsconfig, for example `"types": ["node"]`; TypeScript 6 and later default `types` to `[]`, and without it `node:` imports and `process` fail to type-check.
- JavaScript files that run in a browser: add `globals.browser` to the `languageOptions.globals` of the JavaScript entry, next to `globals.node` for configuration files.
- Build output directories other than `dist/`, `build/`, and `coverage/`: add them to `globalIgnores` and to `.prettierignore`.
- Import aliases other than `@/`, `~/`, and `#`: replace the `internalPattern` entries with the application's alias patterns from its `tsconfig.json` `paths`.
- TypeScript files that no `tsconfig.json` includes, such as tool configuration files: list them in `parserOptions.projectService.allowDefaultProject`.
- A root `tsconfig.json` that only lists project `references`: merge the fragment into each referenced configuration and replace `tsc --noEmit` with `tsc --build` in `typecheck` and `verify`.
- Applications that use Vitest: import `@vitest/eslint-plugin` as `vitest`, and add `{files: ['**/*.{test,spec}.{ts,tsx}'], plugins: {vitest}, rules: {...vitest.configs.recommended.rules}}` to `eslint.config.mjs` before the `**/*.{js,mjs,cjs}` entry.
- Coverage reports only the files that tests import unless `--coverage.include` lists the source files, for example `vitest run --coverage --coverage.include='src/**/*.{ts,tsx}'`.
- `google` with framework files that must default-export, such as Next.js pages or Storybook stories: add their glob patterns to the `files` list of the override that turns off `no-restricted-exports`.
- Frameworks with an official ESLint plugin or config, such as React Hooks, Next.js, Vue, Svelte, or Angular: append that plugin's recommended flat config as its current documentation shows, before the `**/*.{js,mjs,cjs}` entry.

## Existing tooling

- Biome configured (`biome.json` or `biome.jsonc`) covers formatting and linting. Keep it, use `biome check` in `verify`, and add only the type-check concern from this profile.
- An existing ESLint configuration, including a legacy `.eslintrc*` file, covers linting; an existing Prettier configuration or `dprint.json` covers formatting.
- `gts` configured covers formatting and linting for the `google` variant.
- A `tsconfig.json` with `"strict": true`, in the root configuration or in every referenced one, covers type checking; keep it unchanged. Without `strict`, type checking is missing: merge the fragment.
- A framework that generates its own ESLint configuration, such as `create-next-app`, covers linting.
- An existing test framework or runner, such as Vitest, Jest, Mocha, or `node:test`, stays: its script is the `test` command, and no second runner is added.

## Standards notes
Follow Recording the toolchain in `references/toolchains.md`. Authorities: Prettier (`.prettierrc.json`) for formatting, ESLint with typescript-eslint (`eslint.config.mjs`) for linting, strict TypeScript (`tsconfig.json`) for type checking, and the application's test framework. Documentation-comment sentence: Documentation comments use JSDoc `/** ... */` blocks.
