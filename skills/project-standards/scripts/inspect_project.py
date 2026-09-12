#!/usr/bin/env python3
"""Inspects a repository and emits evidence for the project-standards skill.

The scanner reports repository facts only. It does not decide application
boundaries, standards, or user preferences.

Usage:
    python3 inspect_project.py [ROOT] [--max-depth N]
"""

from __future__ import annotations

import argparse
from collections.abc import Iterator
import json
import os
import pathlib
from typing import Any

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".build",
    ".swiftpm",
    ".claude",
    "node_modules",
    "Pods",
    "DerivedData",
    "dist",
    "build",
    "coverage",
    ".next",
    ".nuxt",
    ".output",
    "vendor",
    "target",
    "__pycache__",
}

XCODE_BUNDLE_SUFFIXES = {".xcodeproj", ".xcworkspace"}

MANIFESTS = {
    "Package.swift": "swift-package",
    "go.mod": "go",
    "package.json": "javascript",
    "deno.json": "deno",
    "deno.jsonc": "deno",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "Cargo.toml": "rust",
    "pom.xml": "java-maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "settings.gradle": "gradle",
    "settings.gradle.kts": "gradle",
    "Gemfile": "ruby",
    "composer.json": "php",
    "pubspec.yaml": "dart-flutter",
    "mix.exs": "elixir",
    "rebar.config": "erlang",
    "deps.edn": "clojure",
    "project.clj": "clojure",
    "stack.yaml": "haskell",
    "CMakeLists.txt": "cmake",
    "meson.build": "meson",
    "build.zig": "zig",
    "pnpm-workspace.yaml": "pnpm-workspace",
    "turbo.json": "turborepo",
    "nx.json": "nx",
}

MANIFEST_SUFFIXES = {
    ".csproj": "dotnet",
    ".fsproj": "dotnet",
    ".vbproj": "dotnet",
    ".sln": "dotnet-solution",
    ".cabal": "haskell",
}

TOOLING_CONFIGS = {
    ".editorconfig",
    ".swiftlint.yml",
    ".swiftformat",
    ".prettierrc",
    ".prettierrc.json",
    "prettier.config.js",
    "prettier.config.mjs",
    "eslint.config.js",
    "eslint.config.mjs",
    ".eslintrc",
    ".golangci.yml",
    ".golangci.yaml",
    "biome.json",
    "biome.jsonc",
    "ruff.toml",
    "mypy.ini",
    "pytest.ini",
    "vitest.config.ts",
    "jest.config.js",
    "jest.config.ts",
}

SOURCE_EXTENSIONS = {
    ".swift", ".m", ".mm",
    ".go",
    ".ts", ".tsx",
    ".js", ".jsx",
    ".vue", ".svelte",
    ".py",
    ".rs",
    ".java",
    ".kt", ".kts",
    ".scala",
    ".cs", ".fs", ".vb",
    ".rb",
    ".php",
    ".dart",
    ".c", ".h", ".cc", ".cpp", ".cxx", ".hpp", ".hh",
    ".ex", ".exs",
    ".erl", ".hrl",
    ".clj", ".cljs", ".cljc",
    ".hs", ".lhs",
    ".ml", ".mli",
    ".lua",
    ".r",
    ".jl",
    ".sh", ".bash", ".zsh", ".fish",
    ".sql",
    ".proto",
    ".graphql", ".gql",
    ".zig",
    ".nim",
}


def _walk_repository(
    root: pathlib.Path,
    max_depth: int,
) -> Iterator[tuple[pathlib.Path, list[str], list[str]]]:
    """Yields repository directories, files, and Xcode bundles."""
    root_depth = len(root.parts)

    for current, dirs, files in os.walk(root):
        directory = pathlib.Path(current)
        depth = len(directory.parts) - root_depth

        xcode_bundles = [
            name
            for name in dirs
            if pathlib.Path(name).suffix.lower() in XCODE_BUNDLE_SUFFIXES
        ]

        dirs[:] = [
            name
            for name in dirs
            if name not in SKIP_DIRS
            and not name.startswith(".cache")
            and pathlib.Path(name).suffix.lower() not in XCODE_BUNDLE_SUFFIXES
        ]

        if depth >= max_depth:
            dirs[:] = []

        yield directory, files, xcode_bundles


def _read_package_json(path: pathlib.Path) -> dict[str, Any]:
    """Returns project metadata from a package.json file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}

    dependencies: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = data.get(key)
        if isinstance(value, dict):
            dependencies.update(value)

    scripts = data.get("scripts")
    return {
        "name": data.get("name"),
        "private": data.get("private"),
        "workspaces": data.get("workspaces"),
        "dependencies": sorted(dependencies),
        "scripts": sorted(scripts) if isinstance(scripts, dict) else [],
    }


def _inspect_claude_file(path: pathlib.Path) -> dict[str, Any]:
    """Returns Claude Code integration evidence from a CLAUDE.md file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        text = ""

    stripped = text.strip()
    imports_agents = any(
        line.strip() == "@AGENTS.md" for line in text.splitlines()
    )
    thin_adapter = stripped == "@AGENTS.md"

    return {
        "imports_agents": imports_agents,
        "thin_adapter": thin_adapter,
        "user_maintained_content": bool(stripped) and not thin_adapter,
    }


def _parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect repository structure and tooling for project-standards."
        )
    )
    parser.add_argument("root", nargs="?", default=".", help="repository root")
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="maximum directory depth to inspect (default: 5)",
    )
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    if not root.is_dir():
        parser.error(f"repository root is not a directory: {root}")
    if args.max_depth < 0:
        parser.error("--max-depth must be zero or greater")

    args.root = root
    return args


def _inspect_repository(root: pathlib.Path, max_depth: int) -> dict[str, Any]:
    """Collects repository evidence used by the project-standards skill."""
    manifests: list[dict[str, Any]] = []
    tooling_configs: list[str] = []
    agents_files: list[str] = []
    claude_files: list[dict[str, Any]] = []
    claude_directories: list[str] = []
    standards_directories: list[str] = []
    xcode_bundles: list[str] = []
    markdown_file_count = 0
    project_markdown_file_count = 0
    source_file_counts: dict[str, int] = {}
    file_extension_counts: dict[str, int] = {}

    for directory, files, bundles in _walk_repository(root, max_depth):
        relative_directory = directory.relative_to(root)

        if directory.name == "standards":
            standards_directories.append(str(relative_directory) or ".")

        claude_directory = directory / ".claude"
        if claude_directory.is_dir():
            claude_directories.append(str(claude_directory.relative_to(root)))

        for bundle in bundles:
            bundle_path = directory / bundle
            xcode_bundles.append(str(bundle_path.relative_to(root)))

        for name in files:
            path = directory / name
            relative_path = str(path.relative_to(root))
            suffix = path.suffix.lower()

            if suffix:
                file_extension_counts[suffix] = (
                    file_extension_counts.get(suffix, 0) + 1
                )

            if suffix == ".md":
                markdown_file_count += 1
                if name not in {"AGENTS.md", "CLAUDE.md"}:
                    project_markdown_file_count += 1

            if suffix in SOURCE_EXTENSIONS:
                source_file_counts[suffix] = (
                    source_file_counts.get(suffix, 0) + 1
                )

            manifest_kind = MANIFESTS.get(name) or MANIFEST_SUFFIXES.get(suffix)
            if manifest_kind:
                manifest: dict[str, Any] = {
                    "path": relative_path,
                    "kind": manifest_kind,
                    "directory": str(relative_directory),
                }
                if name == "package.json":
                    manifest["package"] = _read_package_json(path)
                manifests.append(manifest)

            if name in TOOLING_CONFIGS:
                tooling_configs.append(relative_path)

            if name == "AGENTS.md":
                agents_files.append(relative_path)

            if name == "CLAUDE.md":
                claude_files.append(
                    {"path": relative_path, **_inspect_claude_file(path)}
                )

    candidate_directories = {
        manifest["directory"] or "." for manifest in manifests
    }
    candidate_directories.update(
        str(pathlib.Path(path).parent)
        if str(pathlib.Path(path).parent) != "."
        else "."
        for path in xcode_bundles
    )

    claude_files.sort(key=lambda item: item["path"])
    claude_directories = sorted(set(claude_directories))

    return {
        "root": str(root),
        "candidate_application_directories": sorted(candidate_directories),
        "manifests": sorted(manifests, key=lambda item: item["path"]),
        "xcode": sorted(set(xcode_bundles)),
        "tooling_configs": sorted(set(tooling_configs)),
        "agents_files": sorted(set(agents_files)),
        "standards_directories": sorted(set(standards_directories)),
        "claude_code": {
            "detected": bool(claude_files or claude_directories),
            "integration_enabled": any(
                item["imports_agents"] for item in claude_files
            ),
            "claude_directories": claude_directories,
            "claude_files": claude_files,
        },
        "source_file_counts": dict(sorted(source_file_counts.items())),
        "file_extension_counts": dict(sorted(file_extension_counts.items())),
        "markdown_file_count": markdown_file_count,
        "project_markdown_file_count": project_markdown_file_count,
        "documentation_only_candidate": (
            not manifests
            and not xcode_bundles
            and not source_file_counts
            and project_markdown_file_count > 0
        ),
    }


def main() -> None:
    """Runs the repository inspector and prints JSON evidence."""
    args = _parse_args()
    result = _inspect_repository(args.root, args.max_depth)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
