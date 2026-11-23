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
import re
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
    ".swift-format",
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yaml",
    ".prettierrc.yml",
    ".prettierrc.js",
    ".prettierrc.cjs",
    ".prettierrc.mjs",
    "prettier.config.js",
    "prettier.config.cjs",
    "prettier.config.mjs",
    "eslint.config.js",
    "eslint.config.cjs",
    "eslint.config.mjs",
    "eslint.config.ts",
    "eslint.config.mts",
    "eslint.config.cts",
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.json",
    ".eslintrc.yml",
    ".eslintrc.yaml",
    "biome.json",
    "biome.jsonc",
    "dprint.json",
    "tsconfig.json",
    ".golangci.yml",
    ".golangci.yaml",
    ".golangci.toml",
    ".golangci.json",
    "ruff.toml",
    ".ruff.toml",
    "mypy.ini",
    ".flake8",
    ".pylintrc",
    "pyrightconfig.json",
    "pyrefly.toml",
    "pytest.ini",
    "rustfmt.toml",
    ".rustfmt.toml",
    "nextest.toml",
    "clippy.toml",
    ".clippy.toml",
    "Directory.Build.props",
    "checkstyle.xml",
    "lint.xml",
    "analysis_options.yaml",
    ".shellcheckrc",
    "detekt.yml",
    "vitest.config.ts",
    "jest.config.js",
    "jest.config.ts",
}

# Source extensions that select a toolchain profile under toolchains/.
# Kotlin build scripts (.kts) are excluded so Gradle builds of Java code do
# not select the Kotlin profile.
TOOLCHAIN_EXTENSIONS = {
    "typescript": {
        ".ts", ".tsx", ".mts", ".cts", ".js", ".jsx", ".mjs", ".cjs",
    },
    "python": {".py"},
    "go": {".go"},
    "rust": {".rs"},
    "java": {".java"},
    "kotlin": {".kt"},
    "csharp": {".cs"},
    "swift": {".swift"},
    "flutter": {".dart"},
    "shell": {".sh", ".bash", ".bats"},
}

# Platform profiles extend a language profile. They are selected by a marker
# file rather than by source extensions.
PLATFORM_PROFILES = {
    "android": "kotlin",
    "ios": "swift",
}

# Host platform directories that a Flutter application owns.
FLUTTER_HOST_DIRS = {"android", "ios", "macos", "linux", "windows", "web"}

TOOLCHAINS_DIR = pathlib.Path(__file__).resolve().parent.parent / "toolchains"

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
    ".sh", ".bash", ".bats", ".zsh", ".fish",
    ".sql",
    ".proto",
    ".graphql", ".gql",
    ".zig",
    ".nim",
}


def _walk_repository(
    root: pathlib.Path,
    max_depth: int,
    truncated: list[bool],
) -> Iterator[tuple[pathlib.Path, list[str], list[str]]]:
    """Yields repository directories, files, and Xcode bundles.

    Appends True to `truncated` when subdirectories lie beyond `max_depth`.
    """
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
            if dirs:
                truncated.append(True)
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
    embedded_tool_configs = sorted(
        key for key in ("eslintConfig", "prettier") if key in data
    )
    return {
        "name": data.get("name"),
        "private": data.get("private"),
        "workspaces": data.get("workspaces"),
        "dependencies": sorted(dependencies),
        "scripts": sorted(scripts) if isinstance(scripts, dict) else [],
        "embedded_tool_configs": embedded_tool_configs,
    }


def _read_pyproject_tools(path: pathlib.Path) -> list[str]:
    """Returns the `[tool.*]` table names configured in a pyproject.toml file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    tools = {
        match.group(1)
        for match in re.finditer(r"^\[+tool\.([A-Za-z0-9_-]+)", text, re.M)
    }
    return sorted(tools)


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


def _toolchain_profile(suffix: str) -> str | None:
    """Returns the toolchain profile that a source file extension selects."""
    for profile, extensions in TOOLCHAIN_EXTENSIONS.items():
        if suffix in extensions:
            return profile
    return None


def _directory_depth(directory: str) -> int:
    """Returns the number of path parts in a repository-relative directory."""
    return 0 if directory == "." else len(pathlib.PurePosixPath(directory).parts)


def _owning_directory(directory: str, candidates: list[str]) -> str:
    """Returns the deepest candidate application directory containing a path."""
    path = pathlib.PurePosixPath(directory)
    owners = [
        candidate
        for candidate in candidates
        if candidate == "."
        or path == pathlib.PurePosixPath(candidate)
        or pathlib.PurePosixPath(candidate) in path.parents
    ]
    if not owners:
        return "."
    return max(owners, key=_directory_depth)


def _is_ios_project(bundle: pathlib.Path) -> bool:
    """Returns whether an Xcode project builds for the iOS SDK."""
    try:
        text = (bundle / "project.pbxproj").read_text(
            encoding="utf-8", errors="ignore"
        )
    except OSError:
        return False
    return re.search(r"SDKROOT\s*=\s*iphoneos\s*;", text) is not None


def _in_flutter_host(directory: str, flutter_roots: list[str]) -> bool:
    """Returns whether a directory lies in a Flutter application's host folder."""
    path = pathlib.PurePosixPath(directory)
    for root in flutter_roots:
        if root == ".":
            relative = path
        else:
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
        if relative.parts and relative.parts[0] in FLUTTER_HOST_DIRS:
            return True
    return False


def _toolchain_profiles(
    counts: dict[tuple[str, str], int],
    platform_markers: list[tuple[str, str, str]],
    candidates: list[str],
    flutter_roots: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """Groups profile evidence by its candidate application directory.

    Platform profiles come first in each group, with the marker that selected
    them; language profiles follow, ordered by source file count. Evidence in
    a Flutter application's host folders belongs to the Flutter application.
    """
    platforms: dict[str, dict[str, str]] = {}
    for directory, profile, evidence in platform_markers:
        if _in_flutter_host(directory, flutter_roots):
            continue
        owner = _owning_directory(directory, candidates)
        platforms.setdefault(owner, {}).setdefault(profile, evidence)

    grouped: dict[str, dict[str, int]] = {}
    for (directory, profile), count in counts.items():
        if _in_flutter_host(directory, flutter_roots):
            continue
        owner = _owning_directory(directory, candidates)
        profiles = grouped.setdefault(owner, {})
        profiles[profile] = profiles.get(profile, 0) + count

    result: dict[str, list[dict[str, Any]]] = {}
    for owner in sorted(set(platforms) | set(grouped)):
        # A platform profile extends a language profile, so it applies only
        # where that language has sources.
        platforms[owner] = {
            profile: evidence
            for profile, evidence in platforms.get(owner, {}).items()
            if PLATFORM_PROFILES[profile] in grouped.get(owner, {})
        }
        entries: list[dict[str, Any]] = [
            {
                "profile": profile,
                "profile_path": f"toolchains/{profile}/profile.md",
                "extends": PLATFORM_PROFILES[profile],
                "evidence": evidence,
            }
            for profile, evidence in sorted(platforms.get(owner, {}).items())
        ]
        entries.extend(
            {
                "profile": profile,
                "profile_path": f"toolchains/{profile}/profile.md",
                "source_files": count,
            }
            for profile, count in sorted(
                grouped.get(owner, {}).items(),
                key=lambda item: (-item[1], item[0]),
            )
        )
        entries = [
            entry
            for entry in entries
            if (TOOLCHAINS_DIR / entry["profile"] / "profile.md").is_file()
        ]
        if entries:
            result[owner] = entries
    return result


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
        default=8,
        help="maximum directory depth to inspect (default: 8)",
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
    toolchain_counts: dict[tuple[str, str], int] = {}
    platform_markers: list[tuple[str, str, str]] = []

    truncated: list[bool] = []
    for directory, files, bundles in _walk_repository(root, max_depth, truncated):
        relative_directory = directory.relative_to(root)

        if directory.name == "standards":
            standards_directories.append(relative_directory.as_posix())

        claude_directory = directory / ".claude"
        if claude_directory.is_dir():
            claude_directories.append(claude_directory.relative_to(root).as_posix())

        for bundle in bundles:
            if _is_ios_project(directory / bundle):
                platform_markers.append(
                    (
                        relative_directory.as_posix(),
                        "ios",
                        (directory / bundle).relative_to(root).as_posix(),
                    )
                )
            bundle_path = directory / bundle
            xcode_bundles.append(bundle_path.relative_to(root).as_posix())

        for name in files:
            path = directory / name
            relative_path = path.relative_to(root).as_posix()
            suffix = path.suffix.lower()

            if suffix:
                file_extension_counts[suffix] = (
                    file_extension_counts.get(suffix, 0) + 1
                )

            if suffix == ".md":
                markdown_file_count += 1
                if name not in {"AGENTS.md", "CLAUDE.md"}:
                    project_markdown_file_count += 1

            if name == "AndroidManifest.xml":
                platform_markers.append(
                    (relative_directory.as_posix(), "android", relative_path)
                )

            profile = _toolchain_profile(suffix)
            if profile:
                key = (relative_directory.as_posix(), profile)
                toolchain_counts[key] = toolchain_counts.get(key, 0) + 1

            if suffix in SOURCE_EXTENSIONS:
                source_file_counts[suffix] = (
                    source_file_counts.get(suffix, 0) + 1
                )

            manifest_kind = MANIFESTS.get(name) or MANIFEST_SUFFIXES.get(suffix)
            if manifest_kind:
                manifest: dict[str, Any] = {
                    "path": relative_path,
                    "kind": manifest_kind,
                    "directory": relative_directory.as_posix(),
                }
                if name == "package.json":
                    manifest["package"] = _read_package_json(path)
                if name == "pyproject.toml":
                    manifest["tool_tables"] = _read_pyproject_tools(path)
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
        pathlib.PurePosixPath(path).parent.as_posix()
        for path in xcode_bundles
    )

    claude_files.sort(key=lambda item: item["path"])
    claude_directories = sorted(set(claude_directories))

    return {
        "root": root.as_posix(),
        "max_depth_reached": bool(truncated),
        "candidate_application_directories": sorted(candidate_directories),
        "manifests": sorted(manifests, key=lambda item: item["path"]),
        "xcode": sorted(set(xcode_bundles)),
        "tooling_configs": sorted(set(tooling_configs)),
        "toolchain_profiles": _toolchain_profiles(
            toolchain_counts,
            platform_markers,
            sorted(candidate_directories),
            sorted(
                manifest["directory"] or "."
                for manifest in manifests
                if manifest["kind"] == "dart-flutter"
            ),
        ),
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
