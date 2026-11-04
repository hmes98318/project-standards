#!/usr/bin/env python3
"""Checks for a newer project-standards release and updates the skill.

The script is independent of how the skill was installed. It locates the skill
directory from its own path, so user-level, project-level, symlinked, copied
and agent-installed skills all work.

Each run does the following:

  1. Reads the installed version from SKILL.md (`metadata.version`).
  2. Looks up the latest stable release tag, at most once per interval (24
     hours by default), and records the outcome in a cache file.
  3. If a newer release exists, replaces the skill with the archive of that
     release tag. No confirmation is requested.
  4. Compares the installed version with the version stamp in the repository's
     root AGENTS.md. This step is offline.

The latest-release lookup is a lightweight HEAD request to
`.../releases/latest`. Redirects are followed automatically, including those
caused by a renamed or moved repository, and the final URL names the release
tag. If that fails, the script falls back to `git ls-remote --tags`.

Cache file (JSON): `project-standards/update-check.json` under
`$XDG_CACHE_HOME` (or `~/.cache`) on macOS and Linux, and under
`%LOCALAPPDATA%` on Windows. Fields:

  schema:       Cache format version.
  last_run:     When the script last ran, and its status and installed version.
  last_check:   The last latest-release lookup: time, result, source, tag,
                version, error and duration.
  last_update:  The last update attempt: time, from/to versions, result, error.

The script prints exactly one JSON object to stdout and exits 0 for every
operational outcome, so a failed check never blocks the calling agent. Set
PROJECT_STANDARDS_NO_UPDATE to any non-empty value to disable it.

It uses only the Python standard library and is meant to run unchanged on
Windows, macOS and Linux. It is developed and tested with Python 3.14.
"""

from __future__ import annotations

import argparse
import datetime
import http.client
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from typing import Any

_REPO = 'hmes98318/project-standards'
_SKILL_NAME = 'project-standards'
_LATEST_URL = f'https://github.com/{_REPO}/releases/latest'
_GIT_URL = f'https://github.com/{_REPO}.git'
_ARCHIVE_URL = f'https://github.com/{_REPO}/archive/refs/tags/{{tag}}.zip'

_CACHE_SCHEMA = 1
_CHECK_INTERVAL_SECONDS = 24 * 60 * 60
_RETRY_INTERVAL_SECONDS = 60 * 60
_LOOKUP_TIMEOUT_SECONDS = 3.0
_ARCHIVE_TIMEOUT_SECONDS = 30.0
_MAX_ARCHIVE_BYTES = 20 * 1024 * 1024
_MAX_EXTRACTED_BYTES = 20 * 1024 * 1024
_OPT_OUT_ENV = 'PROJECT_STANDARDS_NO_UPDATE'
# Every request asks proxies and caches for a fresh answer; the script itself
# keeps no HTTP cache, only the interval-based cache file.
_REQUEST_HEADERS = {
    'User-Agent': 'project-standards-updater',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}
_PLUGIN_MANIFESTS = ('.claude-plugin/plugin.json', '.codex-plugin/plugin.json')

_SEMVER = re.compile(
    r'^v?(\d+)\.(\d+)\.(\d+)'
    r'(?:-([0-9A-Za-z.-]+))?(?:\+[0-9A-Za-z.-]+)?$')
_FRONTMATTER = re.compile(r'\A---\r?\n(.*?)\r?\n---', re.DOTALL)
_STAMP = re.compile(r'<!--\s*project-standards:\s*([^\s>]+?)\s*-->')
_RELEASE_TAG_PATH = re.compile(r'/releases/tag/([^/]+)$')
_SKILL_MD_IN_ARCHIVE = re.compile(
    rf'^(?:[^/]+/)?skills/{re.escape(_SKILL_NAME)}/SKILL\.md$')


class UpdateError(Exception):
    """A failure that is reported in the output but must not abort the run."""


# ---------------------------------------------------------------------------
# Versions and time.
# ---------------------------------------------------------------------------


def _version_key(text: str) -> tuple[Any, ...] | None:
    """Returns a sortable key for a semantic version, or None if invalid.

    Args:
      text: A version such as `1.2.3`, `v1.2.3` or `1.2.3-rc.1`.

    Returns:
      A tuple `(major, minor, patch, is_stable, prerelease_identifiers)`.
      Releases sort after their own pre-releases.
    """
    match = _SEMVER.match(text.strip())
    if match is None:
        return None
    major, minor, patch = (int(match.group(i)) for i in (1, 2, 3))
    prerelease = match.group(4)
    if prerelease is None:
        return (major, minor, patch, 1, ())
    identifiers = tuple(
        (0, int(part), '') if part.isdigit() else (1, 0, part)
        for part in prerelease.split('.'))
    return (major, minor, patch, 0, identifiers)


def _tag_version(tag: str) -> str | None:
    """Returns the version a release tag names, or None if it is not one."""
    if _version_key(tag) is None:
        return None
    return tag.removeprefix('v')


def _utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _format_time(moment: datetime.datetime) -> str:
    return moment.isoformat(timespec='seconds')


def _age_seconds(stamp: Any, now: datetime.datetime) -> float | None:
    """Returns seconds since an ISO 8601 timestamp, or None if unusable."""
    if not isinstance(stamp, str):
        return None
    try:
        then = datetime.datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if then.tzinfo is None:
        return None
    return (now - then).total_seconds()


# ---------------------------------------------------------------------------
# Skill and repository metadata.
# ---------------------------------------------------------------------------


def _frontmatter_value(text: str, key: str) -> str | None:
    """Returns the first value for `key` in the SKILL.md frontmatter."""
    match = _FRONTMATTER.match(text)
    if match is None:
        return None
    found = re.search(
        rf'^\s*{re.escape(key)}:\s*["\']?([^"\'\s#]+)', match.group(1),
        re.MULTILINE)
    return found.group(1) if found else None


def _read_skill_version(skill_md: pathlib.Path) -> str | None:
    try:
        return _frontmatter_value(skill_md.read_text(encoding='utf-8-sig'),
                                  'version')
    except OSError:
        return None


def _read_stamp(repo: pathlib.Path) -> str | None:
    """Reads the version stamp from the repository's root AGENTS.md."""
    try:
        text = (repo / 'AGENTS.md').read_text(encoding='utf-8-sig')
    except OSError:
        return None
    match = _STAMP.search(text)
    return match.group(1) if match else None


def _stamp_status(stamp: str | None,
                  installed: str) -> tuple[str, str | None]:
    """Compares the repository stamp with the installed version.

    Args:
      stamp: The version stamp found in the repository, if any.
      installed: The installed skill version.

    Returns:
      A tuple of the status (`none`, `unknown`, `match`, `repo-newer` or
      `repo-older`) and an explanatory notice, or None when nothing needs to
      be said.
    """
    if stamp is None:
        return 'none', None
    stamp_key, installed_key = _version_key(stamp), _version_key(installed)
    if stamp_key is None or installed_key is None:
        return 'unknown', None
    if stamp_key == installed_key:
        return 'match', None
    if stamp_key > installed_key:
        return 'repo-newer', (
            f'The standards in this repository were generated with '
            f'project-standards v{stamp}, which is newer than the installed '
            f'v{installed}; the skill should be updated.')
    return 'repo-older', (
        f'The standards in this repository were generated with '
        f'project-standards v{stamp}; installed v{installed} can refresh '
        f'them in update mode.')


def _managed_reason(skill_dir: pathlib.Path) -> str | None:
    """Returns why the skill must not be replaced in place, if it must not."""
    if (skill_dir / '.git').exists():
        return 'a git checkout'
    plugin_root = skill_dir.parent.parent
    if any((plugin_root / manifest).is_file()
           for manifest in _PLUGIN_MANIFESTS):
        return 'a plugin or repository checkout'
    return None


# ---------------------------------------------------------------------------
# Cache.
# ---------------------------------------------------------------------------


def _default_cache_path() -> pathlib.Path:
    base = os.environ.get('XDG_CACHE_HOME')
    if not base and os.name == 'nt':
        base = os.environ.get('LOCALAPPDATA')
    root = pathlib.Path(base) if base else pathlib.Path.home() / '.cache'
    return root / _SKILL_NAME / 'update-check.json'


def _load_cache(path: pathlib.Path) -> dict[str, Any]:
    """Loads the cache, returning an empty one if it is missing or invalid."""
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get('schema') != _CACHE_SCHEMA:
        return {}
    return data


def _save_cache(path: pathlib.Path, cache: dict[str, Any]) -> None:
    """Atomically writes the cache. Failures are ignored; it is only a cache."""
    temp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temp_name = tempfile.mkstemp(
            dir=path.parent, prefix='.update-check-')
        with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
            json.dump(cache, handle, indent=2, sort_keys=True)
            handle.write('\n')
        os.replace(temp_name, path)
        temp_name = None
    except OSError:
        pass
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Latest-release lookup.
# ---------------------------------------------------------------------------


def _tag_from_redirect(url: str, timeout: float) -> str:
    """Returns the latest release tag named by the redirect of `url`.

    A HEAD request is made and redirects are followed automatically, so a
    renamed or moved repository (which adds a hop) still resolves. HEAD is
    kept across redirects, so no release page body is transferred.

    Args:
      url: The `.../releases/latest` URL.
      timeout: Request timeout in seconds.

    Raises:
      UpdateError: If the request fails or the final URL names no tag.
    """
    request = urllib.request.Request(
        url, method='HEAD', headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
    except (OSError, http.client.HTTPException, ValueError) as exc:
        raise UpdateError(f'{type(exc).__name__}: {exc}') from exc
    match = _RELEASE_TAG_PATH.search(urllib.parse.urlparse(final_url).path)
    if match is None:
        raise UpdateError(f'no release tag in {final_url}')
    return urllib.parse.unquote(match.group(1))


def _tag_from_git(url: str, timeout: float) -> str:
    """Returns the highest stable version tag of a repository.

    Args:
      url: A git repository URL or path.
      timeout: Time limit for `git ls-remote`, in seconds.

    Raises:
      UpdateError: If git fails or the repository has no stable version tag.
    """
    environment = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    try:
        completed = subprocess.run(
            ['git', 'ls-remote', '--tags', '--refs', url, 'v*'],
            capture_output=True, encoding='utf-8', errors='replace',
            timeout=timeout, check=False, env=environment)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise UpdateError(f'{type(exc).__name__}: {exc}') from exc
    if completed.returncode != 0:
        raise UpdateError(f'git exited with {completed.returncode}')
    best_key, best_tag = None, None
    for line in completed.stdout.splitlines():
        tag = line.partition('\t')[2].removeprefix('refs/tags/')
        key = _version_key(tag)
        if key is None or key[3] != 1:
            continue
        if best_key is None or key > best_key:
            best_key, best_tag = key, tag
    if best_tag is None:
        raise UpdateError('no stable version tag found')
    return best_tag


def _look_up_latest(args: argparse.Namespace,
                    now: datetime.datetime) -> dict[str, Any]:
    """Looks up the latest release, trying the redirect and then git.

    Args:
      args: Parsed command-line arguments.
      now: The time to record for this lookup.

    Returns:
      The `last_check` cache record. Its `result` is `ok` or `failed`.
    """
    started = time.monotonic()
    record: dict[str, Any] = {
        'at': _format_time(now), 'result': 'failed', 'source': None,
        'tag': None, 'latest': None, 'error': None, 'duration_ms': 0}
    errors = []
    sources = (('redirect', _tag_from_redirect, args.latest_url),
               ('git', _tag_from_git, args.git_url))
    for source, lookup, url in sources:
        try:
            tag = lookup(url, args.timeout)
            version = _tag_version(tag)
            if version is None:
                raise UpdateError(f'{tag!r} is not a version tag')
        except UpdateError as exc:
            errors.append(f'{source}: {exc}')
            continue
        record.update(result='ok', source=source, tag=tag, latest=version)
        break
    if record['result'] != 'ok':
        record['error'] = '; '.join(errors)
    record['duration_ms'] = int((time.monotonic() - started) * 1000)
    return record


def _is_check_due(cache: dict[str, Any], now: datetime.datetime,
                  args: argparse.Namespace) -> bool:
    """Returns whether a new latest-release lookup should be made."""
    if args.force:
        return True
    last = cache.get('last_check')
    if not isinstance(last, dict):
        return True
    age = _age_seconds(last.get('at'), now)
    if age is None or age < 0:
        return True
    if last.get('result') == 'ok':
        valid = (isinstance(last.get('latest'), str)
                 and isinstance(last.get('tag'), str)
                 and _version_key(last['latest']) is not None)
        return not valid or age >= args.interval
    return age >= _RETRY_INTERVAL_SECONDS


# ---------------------------------------------------------------------------
# Applying an update.
# ---------------------------------------------------------------------------


def _download(url: str, timeout: float, max_bytes: int) -> bytes:
    """Downloads `url`, refusing responses larger than `max_bytes`."""
    request = urllib.request.Request(url, headers=_REQUEST_HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = response.read(max_bytes + 1)
    except (OSError, http.client.HTTPException, ValueError) as exc:
        raise UpdateError(f'download failed: {type(exc).__name__}: {exc}'
                          ) from exc
    if len(data) > max_bytes:
        raise UpdateError(f'download is larger than {max_bytes} bytes')
    return data


def _extract_skill(archive: zipfile.ZipFile, staging: pathlib.Path) -> None:
    """Extracts `skills/project-standards/` from a release archive.

    Args:
      archive: The opened release archive.
      staging: A directory that must not exist yet; it is created.

    Raises:
      UpdateError: If the archive lacks the skill, holds a symbolic link, has
        an entry that escapes `staging`, or expands beyond the size limit.
    """
    prefix = next((name[:-len('SKILL.md')] for name in archive.namelist()
                   if _SKILL_MD_IN_ARCHIVE.match(name)), None)
    if prefix is None:
        raise UpdateError(f'archive has no skills/{_SKILL_NAME}/SKILL.md')
    staging.mkdir(parents=True)
    base = os.path.normpath(str(staging))
    total = 0
    for info in archive.infolist():
        if not info.filename.startswith(prefix) or info.filename == prefix:
            continue
        mode = (info.external_attr >> 16) & 0xFFFF
        if stat.S_ISLNK(mode):
            raise UpdateError(f'archive has a symbolic link: {info.filename}')
        target = os.path.normpath(
            os.path.join(base, info.filename[len(prefix):]))
        if target != base and not target.startswith(base + os.sep):
            raise UpdateError(f'archive entry escapes: {info.filename}')
        if info.is_dir():
            os.makedirs(target, exist_ok=True)
            continue
        total += info.file_size
        if total > _MAX_EXTRACTED_BYTES:
            raise UpdateError('archive expands beyond the size limit')
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with archive.open(info) as source, open(target, 'wb') as sink:
            shutil.copyfileobj(source, sink)
        if mode & 0o111:
            os.chmod(target, 0o755)


def _validate_staged(staging: pathlib.Path, version: str) -> None:
    """Checks that the extracted skill is the expected version."""
    try:
        text = (staging / 'SKILL.md').read_text(encoding='utf-8-sig')
    except OSError as exc:
        raise UpdateError('downloaded skill has no readable SKILL.md'
                          ) from exc
    if _frontmatter_value(text, 'name') != _SKILL_NAME:
        raise UpdateError(f'downloaded SKILL.md is not {_SKILL_NAME}')
    found = _frontmatter_value(text, 'version')
    if found != version:
        raise UpdateError(
            f'downloaded skill is version {found}, expected {version}')


def _rename(source: pathlib.Path, destination: pathlib.Path) -> None:
    """Renames a path, retrying briefly on Windows.

    On Windows a virus scanner or file indexer can hold a freshly written file
    open for a moment, which makes renaming its directory fail with
    PermissionError. POSIX systems do not have this problem.

    Args:
      source: The existing path.
      destination: The new path, which must not exist.

    Raises:
      OSError: If the rename still fails after the retries.
    """
    attempts = 5 if os.name == 'nt' else 1
    for attempt in range(1, attempts + 1):
        try:
            os.rename(source, destination)
            return
        except PermissionError:
            if attempt == attempts:
                raise
            time.sleep(0.2 * attempt)


def _remove_tree(path: pathlib.Path) -> None:
    """Deletes a directory tree if it exists, including read-only files.

    Windows refuses to delete read-only files, such as those extracted from a
    git checkout, so permissions are relaxed and the delete is retried once.
    Failures are ignored: a leftover temporary directory is harmless.
    """
    for _ in range(2):
        shutil.rmtree(path, ignore_errors=True)
        if not path.exists():
            return
        for root, directories, files in os.walk(path):
            for name in directories + files:
                try:
                    os.chmod(os.path.join(root, name), stat.S_IRWXU)
                except OSError:
                    pass


def _apply_update(skill_dir: pathlib.Path, tag: str, version: str,
                  args: argparse.Namespace) -> None:
    """Replaces `skill_dir` with the skill from the archive of `tag`.

    The new copy is extracted and validated next to the old one, then swapped
    in with renames, and rolled back if the swap fails. The old directory is
    left untouched on any failure.

    Args:
      skill_dir: The real (symlink-resolved) installed skill directory.
      tag: The release tag to install.
      version: The version `tag` names; SKILL.md must report the same one.
      args: Parsed command-line arguments.

    Raises:
      UpdateError: If any step fails.
    """
    url = args.archive_url.format(tag=urllib.parse.quote(tag, safe=''))
    payload = _download(url, args.archive_timeout, _MAX_ARCHIVE_BYTES)
    suffix = f'{os.getpid()}-{int(time.time())}'
    staging = skill_dir.parent / f'.{skill_dir.name}.new-{suffix}'
    backup = skill_dir.parent / f'.{skill_dir.name}.old-{suffix}'
    try:
        with tempfile.TemporaryFile() as handle:
            handle.write(payload)
            handle.seek(0)
            try:
                with zipfile.ZipFile(handle) as archive:
                    _extract_skill(archive, staging)
            except zipfile.BadZipFile as exc:
                raise UpdateError('download is not a valid zip file') from exc
        _validate_staged(staging, version)
        _rename(skill_dir, backup)
        try:
            _rename(staging, skill_dir)
        except OSError:
            _rename(backup, skill_dir)
            raise
        _remove_tree(backup)
    except OSError as exc:
        raise UpdateError(f'{type(exc).__name__}: {exc}') from exc
    finally:
        _remove_tree(staging)


# ---------------------------------------------------------------------------
# Orchestration.
# ---------------------------------------------------------------------------


def _update_recently_failed(cache: dict[str, Any], version: str,
                            now: datetime.datetime) -> dict[str, Any] | None:
    """Returns the failed update record if it is recent and for `version`."""
    last = cache.get('last_update')
    if (not isinstance(last, dict) or last.get('result') != 'failed'
            or last.get('to') != version):
        return None
    age = _age_seconds(last.get('at'), now)
    if age is None or not 0 <= age < _RETRY_INTERVAL_SECONDS:
        return None
    return last


def _check_and_update(args: argparse.Namespace, skill_dir: pathlib.Path,
                      cache: dict[str, Any], now: datetime.datetime,
                      result: dict[str, Any]) -> None:
    """Runs the lookup and update, recording the outcome in cache and result."""
    installed = result['installed']
    due = _is_check_due(cache, now, args)
    if due:
        cache['last_check'] = _look_up_latest(args, now)
    check = cache['last_check']
    result.update(from_cache=not due, checked_at=check.get('at'))

    if check.get('result') != 'ok':
        error = check.get('error') or 'unknown error'
        result.update(
            status='check-failed', error=error,
            notice=f'project-standards v{installed} in use '
                   f'(update check unavailable: {error})')
        return

    latest, tag = check['latest'], check['tag']
    result['latest'] = latest
    installed_key, latest_key = _version_key(installed), _version_key(latest)
    if latest_key <= installed_key:
        if latest_key == installed_key:
            result.update(
                status='current',
                notice=f'project-standards v{installed} in use (latest)')
        else:
            result.update(
                status='ahead',
                notice=f'project-standards v{installed} in use (newer than '
                       f'latest release v{latest})')
        return

    available = f'v{latest} is available'
    if args.check_only:
        result.update(
            status='update-available',
            notice=f'project-standards v{installed} in use ({available})')
        return
    managed = _managed_reason(skill_dir)
    if managed:
        result.update(
            status='managed',
            notice=f'project-standards v{installed} in use ({available}; '
                   f'this copy is {managed}, so update it there)')
        return
    failed = None if args.force else _update_recently_failed(
        cache, latest, now)
    if failed is not None:
        reason = failed.get('error')
        result.update(
            status='update-failed', error=reason,
            notice=f'project-standards v{installed} in use (update to '
                   f'v{latest} failed recently: {reason}; retrying later)')
        return

    update = {'at': _format_time(now), 'from': installed, 'to': latest,
              'result': 'ok', 'error': None}
    try:
        _apply_update(skill_dir, tag, latest, args)
    except UpdateError as exc:
        update.update(result='failed', error=str(exc))
        result.update(
            status='update-failed', error=str(exc),
            notice=f'project-standards v{installed} in use (update to '
                   f'v{latest} failed: {exc})')
    else:
        result.update(
            status='updated', installed=latest, reread_skill=True,
            notice=f'project-standards updated v{installed} → '
                   f'v{latest}; now using v{latest}')
    cache['last_update'] = update


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Runs one check, and the update if one is due and allowed.

    Args:
      args: Parsed command-line arguments.

    Returns:
      The JSON-serializable result printed by `main`.
    """
    script_dir = pathlib.Path(__file__).parent
    skill_dir = pathlib.Path(args.skill_dir or script_dir.parent).resolve()
    installed = _read_skill_version(skill_dir / 'SKILL.md')
    result: dict[str, Any] = {
        'status': 'error', 'installed_before': installed,
        'installed': installed, 'latest': None, 'checked_at': None,
        'from_cache': None, 'stamp': None, 'stamp_status': 'none',
        'skill_dir': str(skill_dir), 'cache_file': None,
        'reread_skill': False, 'notice': None, 'stamp_notice': None,
        'error': None}
    if installed is None or _version_key(installed) is None:
        reason = f'no valid metadata.version in {skill_dir}/SKILL.md'
        result.update(
            error=reason,
            notice=f'project-standards version could not be determined '
                   f'({reason})')
        return result

    if os.environ.get(_OPT_OUT_ENV):
        result.update(
            status='disabled',
            notice=f'project-standards v{installed} in use '
                   f'(update check disabled by {_OPT_OUT_ENV})')
    else:
        cache_path = pathlib.Path(args.cache_file or _default_cache_path())
        cache = _load_cache(cache_path)
        now = _utc_now()
        _check_and_update(args, skill_dir, cache, now, result)
        cache['schema'] = _CACHE_SCHEMA
        cache['last_run'] = {
            'at': _format_time(now), 'status': result['status'],
            'installed': result['installed'], 'skill_dir': str(skill_dir)}
        _save_cache(cache_path, cache)
        result['cache_file'] = str(cache_path)

    stamp = _read_stamp(pathlib.Path(args.repo).resolve())
    status, notice = _stamp_status(stamp, result['installed'])
    result.update(stamp=stamp, stamp_status=status, stamp_notice=notice)
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Check for and apply project-standards updates.')
    parser.add_argument(
        '--repo', default='.',
        help='repository whose root AGENTS.md carries the version stamp '
             '(default: current directory)')
    parser.add_argument(
        '--check-only', action='store_true',
        help='report an available update without applying it')
    parser.add_argument(
        '--force', action='store_true',
        help='look up the latest release now, ignoring the cache interval')
    parser.add_argument(
        '--interval', type=float, default=_CHECK_INTERVAL_SECONDS,
        help='seconds between lookups after a successful one (default: 24h)')
    parser.add_argument(
        '--timeout', type=float, default=_LOOKUP_TIMEOUT_SECONDS,
        help='latest-release lookup timeout in seconds')
    parser.add_argument(
        '--archive-timeout', type=float, default=_ARCHIVE_TIMEOUT_SECONDS,
        help='archive download timeout in seconds')
    # The options below exist for tests and mirrors. Agents must not pass them.
    parser.add_argument('--skill-dir', help=argparse.SUPPRESS)
    parser.add_argument('--cache-file', help=argparse.SUPPRESS)
    parser.add_argument('--latest-url', default=_LATEST_URL,
                        help=argparse.SUPPRESS)
    parser.add_argument('--git-url', default=_GIT_URL, help=argparse.SUPPRESS)
    parser.add_argument('--archive-url', default=_ARCHIVE_URL,
                        help=argparse.SUPPRESS)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parses arguments, runs the check and prints one JSON object."""
    args = _build_parser().parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Isolation point: the update check must never crash the calling
        # agent, so any unexpected error is reported in the output instead.
        result = {'status': 'error',
                  'error': f'{type(exc).__name__}: {exc}',
                  'notice': 'project-standards update check failed'}
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    sys.exit(main())
