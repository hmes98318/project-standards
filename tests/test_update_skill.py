"""End-to-end tests for skills/project-standards/scripts/update_skill.py.

Each test runs the script as a subprocess against a local fake release server
that serves the `/releases/latest` redirect and tag archives, so no network
access is needed. The tests run on Windows, macOS and Linux. Run them from the
repository root with:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import datetime
import http.server
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from typing import Any

_SKILL_SOURCE = (pathlib.Path(__file__).resolve().parent.parent
                 / 'skills' / 'project-standards')
_ARCHIVE_ROOT = 'project-standards-archive'


def _set_version(text: str, version: str) -> str:
    return re.sub(r'(version:\s*")[^"]+(")', rf'\g<1>{version}\g<2>', text,
                  count=1)


def _build_archive(version: str, skill_version: str | None = None,
                   extra: dict[str, bytes] | None = None) -> bytes:
    """Builds a tag archive laid out like GitHub's, from the real skill."""
    buffer = io.BytesIO()
    prefix = f'{_ARCHIVE_ROOT}/skills/project-standards/'
    with zipfile.ZipFile(buffer, 'w') as archive:
        for path in sorted(_SKILL_SOURCE.rglob('*')):
            if path.is_dir() or '__pycache__' in path.parts:
                continue
            relative = path.relative_to(_SKILL_SOURCE).as_posix()
            data = path.read_bytes()
            if relative == 'SKILL.md':
                data = _set_version(
                    data.decode(), skill_version or version).encode()
            info = zipfile.ZipInfo(prefix + relative)
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            archive.writestr(info, data)
        archive.writestr(f'{_ARCHIVE_ROOT}/README.md', 'outside the skill')
        for name, data in (extra or {}).items():
            if isinstance(data, tuple):  # (bytes, external_attr)
                info = zipfile.ZipInfo(name)
                info.external_attr = data[1] << 16
                archive.writestr(info, data[0])
            else:
                archive.writestr(name, data)
    return buffer.getvalue()


class _Handler(http.server.BaseHTTPRequestHandler):
    """Serves `/releases/latest`, `/releases/tag/<tag>` and tag archives."""

    def log_message(self, *args: Any) -> None:
        pass

    def _respond(self) -> None:
        release = self.server.release
        release.requests.append((self.command, self.path))
        release.headers.append(
            {name.lower(): value for name, value in self.headers.items()})
        base = f'http://127.0.0.1:{self.server.server_address[1]}'
        body = b''
        if self.path == '/moved/releases/latest':
            # A renamed repository: a permanent redirect with a relative
            # Location, followed by the normal redirect to the tag.
            self.send_response(301)
            self.send_header('Location', '/releases/latest')
        elif self.path == '/releases/latest' and release.latest_tag:
            self.send_response(302)
            self.send_header(
                'Location', f'{base}/releases/tag/{release.latest_tag}')
        elif self.path.startswith('/releases/tag/'):
            self.send_response(200)
        elif re.fullmatch(r'/archive/[^/]+\.zip', self.path):
            tag = self.path[len('/archive/'):-len('.zip')]
            if tag in release.archives:
                body = release.archives[tag]
                self.send_response(200)
            else:
                self.send_response(404)
        else:
            self.send_response(404)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command == 'GET':
            self.wfile.write(body)

    do_GET = _respond  # pylint: disable=invalid-name
    do_HEAD = _respond  # pylint: disable=invalid-name


class _ReleaseServer:
    """A fake release site on a random local port."""

    def __init__(self) -> None:
        self.latest_tag: str | None = None
        self.archives: dict[str, bytes] = {}
        self.requests: list[tuple[str, str]] = []
        self.headers: list[dict[str, str]] = []
        self._server = http.server.ThreadingHTTPServer(
            ('127.0.0.1', 0), _Handler)
        self._server.release = self
        threading.Thread(target=self._server.serve_forever,
                         daemon=True).start()
        self.url = f'http://127.0.0.1:{self._server.server_address[1]}'

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def count(self, prefix: str) -> int:
        return sum(1 for _, path in self.requests if path.startswith(prefix))


class UpdateSkillTest(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix='ps-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.server = _ReleaseServer()
        self.addCleanup(self.server.close)
        self.cache = self.tmp / 'cache' / 'update-check.json'
        self.git_url = str(self.tmp / 'no-such-repo')

    # Helpers ---------------------------------------------------------------

    def install(self, version: str, name: str = 'a') -> pathlib.Path:
        """Installs a copy of the skill that reports `version`."""
        destination = self.tmp / name / 'skills' / 'project-standards'
        shutil.copytree(_SKILL_SOURCE, destination,
                        ignore=shutil.ignore_patterns('__pycache__'))
        skill_md = destination / 'SKILL.md'
        skill_md.write_text(
            _set_version(skill_md.read_text(encoding='utf-8'), version),
            encoding='utf-8')
        return destination

    def release(self, version: str, **kwargs: Any) -> None:
        """Publishes `version` as the latest release on the fake server."""
        self.server.latest_tag = f'v{version}'
        self.server.archives[f'v{version}'] = _build_archive(
            version, **kwargs)

    def run_script(self, skill_dir: pathlib.Path, *args: str,
                   repo: pathlib.Path | None = None,
                   env: dict[str, str] | None = None) -> dict[str, Any]:
        command = [
            sys.executable, '-I',
            str(skill_dir / 'scripts' / 'update_skill.py'),
            '--latest-url', f'{self.server.url}/releases/latest',
            '--git-url', self.git_url,
            '--archive-url', f'{self.server.url}/archive/{{tag}}.zip',
            '--cache-file', str(self.cache),
            '--repo', str(repo or self.tmp), *args]
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=60, check=False,
            env=dict(os.environ, **(env or {})))
        self.assertEqual(completed.returncode, 0, completed.stderr)
        lines = completed.stdout.strip().splitlines()
        self.assertEqual(len(lines), 1, completed.stdout)
        return json.loads(lines[0])

    def read_cache(self) -> dict[str, Any]:
        return json.loads(self.cache.read_text(encoding='utf-8'))

    def version_of(self, skill_dir: pathlib.Path) -> str:
        match = re.search(r'version:\s*"([^"]+)"',
                          (skill_dir / 'SKILL.md').read_text(encoding='utf-8'))
        return match.group(1)

    def leftovers(self, skill_dir: pathlib.Path) -> list[str]:
        return [path.name for path in skill_dir.parent.iterdir()
                if path.name.startswith('.project-standards.')]

    # Update flow -----------------------------------------------------------

    def test_updates_outdated_install_through_symlink(self) -> None:
        installed = self.install('0.4.0')
        alias = self.tmp / 'a' / 'alias'
        try:
            alias.symlink_to(installed, target_is_directory=True)
        except (OSError, NotImplementedError):
            alias = installed  # Creating symlinks needs a privilege on Windows.
        self.release('0.5.0')

        result = self.run_script(alias)

        self.assertEqual(result['status'], 'updated')
        self.assertEqual(
            (result['installed_before'], result['installed']),
            ('0.4.0', '0.5.0'))
        self.assertTrue(result['reread_skill'])
        self.assertIn('v0.4.0', result['notice'])
        self.assertIn('v0.5.0', result['notice'])
        self.assertEqual(self.version_of(installed), '0.5.0')
        self.assertEqual(alias.is_symlink(), alias != installed)
        self.assertFalse((installed / 'README.md').exists())
        self.assertEqual(self.leftovers(installed), [])

    @unittest.skipIf(os.name == 'nt', 'Windows has no executable bit')
    def test_update_keeps_the_executable_bit(self) -> None:
        installed = self.install('0.4.0')
        prefix = f'{_ARCHIVE_ROOT}/skills/project-standards/scripts/'
        self.release('0.5.0', extra={
            prefix + 'tool.sh': (b'#!/bin/sh\n', stat.S_IFREG | 0o755),
            prefix + 'notes.txt': (b'text\n', stat.S_IFREG | 0o644),
        })

        self.run_script(installed)

        def executable(name: str) -> bool:
            mode = (installed / 'scripts' / name).stat().st_mode
            return bool(stat.S_IMODE(mode) & 0o111)

        self.assertTrue(executable('tool.sh'))
        self.assertFalse(executable('notes.txt'))

    def test_cache_records_check_update_and_run(self) -> None:
        installed = self.install('0.4.0')
        self.release('0.5.0')

        self.run_script(installed)
        cache = self.read_cache()

        self.assertEqual(cache['schema'], 1)
        check = cache['last_check']
        self.assertEqual(
            (check['result'], check['source'], check['tag'],
             check['latest'], check['error']),
            ('ok', 'redirect', 'v0.5.0', '0.5.0', None))
        self.assertIsInstance(check['duration_ms'], int)
        update = cache['last_update']
        self.assertEqual(
            (update['from'], update['to'], update['result']),
            ('0.4.0', '0.5.0', 'ok'))
        run = cache['last_run']
        self.assertEqual((run['status'], run['installed']),
                         ('updated', '0.5.0'))
        for stamp in (check['at'], update['at'], run['at']):
            parsed = datetime.datetime.fromisoformat(stamp)
            self.assertIsNotNone(parsed.tzinfo)

    def test_second_run_uses_cache_without_network(self) -> None:
        installed = self.install('0.5.0')
        self.release('0.5.0')
        self.run_script(installed)
        requests_before = len(self.server.requests)
        self.release('9.9.9')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'current')
        self.assertTrue(result['from_cache'])
        self.assertEqual(len(self.server.requests), requests_before)

    def test_force_and_elapsed_interval_trigger_new_lookup(self) -> None:
        installed = self.install('0.5.0')
        self.release('0.5.0')
        self.run_script(installed)

        self.release('0.6.0')
        forced = self.run_script(installed, '--check-only', '--force')
        self.assertEqual(forced['status'], 'update-available')
        self.assertFalse(forced['from_cache'])

        self.release('0.7.0')
        elapsed = self.run_script(installed, '--check-only',
                                  '--interval', '0')
        self.assertEqual(elapsed['latest'], '0.7.0')

    def test_requests_ask_caches_for_a_fresh_answer(self) -> None:
        installed = self.install('0.4.0')
        self.release('0.5.0')

        self.run_script(installed)

        # The lookup follows the redirect with HEAD (no release page body is
        # transferred), then the archive is downloaded.
        self.assertEqual(
            self.server.requests,
            [('HEAD', '/releases/latest'), ('HEAD', '/releases/tag/v0.5.0'),
             ('GET', '/archive/v0.5.0.zip')])
        for headers in self.server.headers:
            self.assertEqual(headers.get('cache-control'), 'no-cache')
            self.assertEqual(headers.get('pragma'), 'no-cache')
            self.assertEqual(headers.get('user-agent'),
                             'project-standards-updater')

    def test_lookup_follows_redirect_chains(self) -> None:
        installed = self.install('0.4.0')
        self.release('0.5.0')

        result = self.run_script(
            installed, '--check-only',
            '--latest-url', f'{self.server.url}/moved/releases/latest')

        self.assertEqual(result['status'], 'update-available')
        self.assertEqual(result['latest'], '0.5.0')
        self.assertEqual(self.read_cache()['last_check']['source'], 'redirect')
        self.assertEqual(
            [path for _, path in self.server.requests],
            ['/moved/releases/latest', '/releases/latest',
             '/releases/tag/v0.5.0'])

    def test_check_only_changes_nothing(self) -> None:
        installed = self.install('0.4.0')
        self.release('0.5.0')

        result = self.run_script(installed, '--check-only')

        self.assertEqual(result['status'], 'update-available')
        self.assertEqual(self.version_of(installed), '0.4.0')
        self.assertEqual(self.server.count('/archive/'), 0)

    def test_newer_than_latest_is_left_alone(self) -> None:
        installed = self.install('0.9.0')
        self.release('0.5.0')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'ahead')
        self.assertEqual(self.version_of(installed), '0.9.0')

    def test_release_is_newer_than_its_prerelease(self) -> None:
        installed = self.install('1.0.0-rc.1')
        self.release('1.0.0')

        result = self.run_script(installed, '--check-only')

        self.assertEqual(result['status'], 'update-available')

    # Lookup failures -------------------------------------------------------

    def test_failed_lookup_does_not_block_and_is_retried_later(self) -> None:
        installed = self.install('0.4.0')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'check-failed')
        self.assertIn('redirect:', result['error'])
        self.assertIn('git:', result['error'])
        self.assertEqual(self.version_of(installed), '0.4.0')
        self.assertEqual(self.read_cache()['last_check']['result'], 'failed')

        requests_before = len(self.server.requests)
        again = self.run_script(installed)
        self.assertEqual(again['status'], 'check-failed')
        self.assertTrue(again['from_cache'])
        self.assertEqual(len(self.server.requests), requests_before)

    @unittest.skipUnless(shutil.which('git'), 'git is required')
    def test_git_fallback_picks_highest_stable_tag(self) -> None:
        repository = self.tmp / 'upstream'
        repository.mkdir()
        git = ['git', '-C', str(repository), '-c', 'user.name=t',
               '-c', 'user.email=t@example.com', '-c',
               'commit.gpgsign=false']
        subprocess.run([*git, 'init', '-q'], check=True)
        subprocess.run([*git, 'commit', '-q', '--allow-empty', '-m', 'x'],
                       check=True)
        for tag in ('v0.1.0', 'v0.5.0', 'v0.6.0-rc.1', 'not-a-version'):
            subprocess.run([*git, 'tag', tag], check=True)
        self.git_url = str(repository)
        self.server.archives['v0.5.0'] = _build_archive('0.5.0')
        installed = self.install('0.4.0')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'updated')
        self.assertEqual(self.read_cache()['last_check']['source'], 'git')
        self.assertEqual(self.version_of(installed), '0.5.0')

    def test_invalid_cache_is_ignored(self) -> None:
        installed = self.install('0.5.0')
        self.release('0.5.0')
        self.cache.parent.mkdir(parents=True)
        self.cache.write_text('{ not json', encoding='utf-8')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'current')
        self.assertFalse(result['from_cache'])
        self.assertEqual(self.read_cache()['schema'], 1)

    # Safety ----------------------------------------------------------------

    def test_bad_archives_are_rejected_and_install_is_intact(self) -> None:
        skill_prefix = f'{_ARCHIVE_ROOT}/skills/project-standards/'
        link = (b'/etc/passwd', stat.S_IFLNK | 0o777)
        cases: list[tuple[str, dict[str, Any], str]] = [
            ('version mismatch', {'skill_version': '0.4.9'}, 'expected 0.5.0'),
            ('path traversal',
             {'extra': {skill_prefix + '../../../../evil.txt': b'x'}},
             'escapes'),
            ('symbolic link', {'extra': {skill_prefix + 'link': link}},
             'symbolic link'),
        ]
        for name, kwargs, expected in cases:
            with self.subTest(name):
                installed = self.install('0.4.0', name=name.replace(' ', '-'))
                self.release('0.5.0', **kwargs)
                result = self.run_script(installed, '--force')
                self.assertEqual(result['status'], 'update-failed')
                self.assertIn(expected, result['error'])
                self.assertEqual(self.version_of(installed), '0.4.0')
                self.assertEqual(self.leftovers(installed), [])
        self.assertFalse((self.tmp / 'evil.txt').exists())

    def test_corrupt_archive_is_reported(self) -> None:
        installed = self.install('0.4.0')
        self.server.latest_tag = 'v0.5.0'
        self.server.archives['v0.5.0'] = b'not a zip'

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'update-failed')
        self.assertIn('not a valid zip', result['error'])
        self.assertEqual(self.version_of(installed), '0.4.0')

    def test_failed_update_is_not_retried_immediately(self) -> None:
        installed = self.install('0.4.0')
        self.server.latest_tag = 'v0.5.0'
        self.server.archives['v0.5.0'] = b'not a zip'
        self.run_script(installed)
        downloads = self.server.count('/archive/')
        self.release('0.5.0')

        again = self.run_script(installed)
        self.assertEqual(again['status'], 'update-failed')
        self.assertIn('retrying later', again['notice'])
        self.assertEqual(self.server.count('/archive/'), downloads)

        forced = self.run_script(installed, '--force')
        self.assertEqual(forced['status'], 'updated')

    def test_managed_copies_are_not_replaced(self) -> None:
        self.release('0.5.0')
        checkout = self.install('0.4.0', name='checkout')
        (checkout / '.git').mkdir()
        plugin_skill = self.install('0.4.0', name='plugin')
        manifest = plugin_skill.parent.parent / '.claude-plugin'
        manifest.mkdir()
        (manifest / 'plugin.json').write_text('{}', encoding='utf-8')

        for skill_dir in (checkout, plugin_skill):
            with self.subTest(skill_dir.parent.parent.name):
                result = self.run_script(skill_dir, '--force')
                self.assertEqual(result['status'], 'managed')
                self.assertIn('v0.5.0 is available', result['notice'])
                self.assertEqual(self.version_of(skill_dir), '0.4.0')
        self.assertEqual(self.server.count('/archive/'), 0)

    def test_opt_out_environment_variable(self) -> None:
        installed = self.install('0.4.0')
        self.release('0.5.0')

        result = self.run_script(
            installed, env={'PROJECT_STANDARDS_NO_UPDATE': '1'})

        self.assertEqual(result['status'], 'disabled')
        self.assertEqual(self.version_of(installed), '0.4.0')
        self.assertEqual(self.server.requests, [])
        self.assertFalse(self.cache.exists())

    def test_unreadable_skill_version_is_an_error_not_a_crash(self) -> None:
        installed = self.install('0.4.0')
        (installed / 'SKILL.md').write_text('no frontmatter',
                                            encoding='utf-8')

        result = self.run_script(installed)

        self.assertEqual(result['status'], 'error')
        self.assertIn('metadata.version', result['error'])

    def test_windows_style_files_are_understood(self) -> None:
        """A UTF-8 BOM and CRLF line endings, as Windows editors write them."""
        installed = self.install('0.5.0')
        skill_md = installed / 'SKILL.md'
        text = skill_md.read_text(encoding='utf-8')
        skill_md.write_bytes(
            b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode('utf-8'))
        repository = self.tmp / 'repo'
        repository.mkdir()
        (repository / 'AGENTS.md').write_bytes(
            b'\xef\xbb\xbf# AGENTS.md\r\n\r\n'
            b'<!-- project-standards: 0.5.0 -->\r\n')
        self.release('0.5.0')

        result = self.run_script(installed, repo=repository)

        self.assertEqual(result['status'], 'current')
        self.assertEqual(result['installed'], '0.5.0')
        self.assertEqual(result['stamp_status'], 'match')

    # Repository stamp ------------------------------------------------------

    def test_repository_stamp_comparison(self) -> None:
        self.release('0.5.0')
        installed = self.install('0.5.0')
        repository = self.tmp / 'repo'
        repository.mkdir()
        cases = (('0.5.0', 'match', False), ('0.4.0', 'repo-older', True),
                 ('0.7.0', 'repo-newer', True))
        for stamp, expected, has_notice in cases:
            with self.subTest(stamp):
                (repository / 'AGENTS.md').write_text(
                    f'# AGENTS.md\n\n<!-- project-standards: {stamp} -->\n',
                    encoding='utf-8')
                result = self.run_script(installed, repo=repository)
                self.assertEqual(result['stamp_status'], expected)
                self.assertEqual(bool(result['stamp_notice']), has_notice)
        (repository / 'AGENTS.md').unlink()
        self.assertEqual(
            self.run_script(installed, repo=repository)['stamp_status'],
            'none')


class VersionKeyTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        path = _SKILL_SOURCE / 'scripts' / 'update_skill.py'
        spec = importlib.util.spec_from_file_location('update_skill', path)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_ordering(self) -> None:
        key = self.module._version_key  # pylint: disable=protected-access
        ordered = ['0.9.0', '1.0.0-alpha', '1.0.0-alpha.1', '1.0.0-beta',
                   '1.0.0-rc.1', '1.0.0', 'v1.0.1', '1.10.0', '2.0.0']
        keys = [key(version) for version in ordered]
        self.assertEqual(keys, sorted(keys))

    def test_rejects_non_versions(self) -> None:
        key = self.module._version_key  # pylint: disable=protected-access
        for text in ('', 'latest', '1.2', '1.2.3.4', 'v', '<html>'):
            with self.subTest(text):
                self.assertIsNone(key(text))


if __name__ == '__main__':
    unittest.main()
