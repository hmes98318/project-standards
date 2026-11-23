"""Structural tests for the project-standards skill files.

They check that the toolchain catalog, its profiles, and their templates stay
consistent, that skill-relative paths cited in Markdown exist, and that the
repository inspector maps sources to toolchain profiles. Run them from the
repository root with:

    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

_SKILL = (pathlib.Path(__file__).resolve().parent.parent
          / 'skills' / 'project-standards')
_TOOLCHAINS = _SKILL / 'toolchains'
_PROFILE_SECTIONS = [
    'Detection',
    'Variants',
    'Toolchain',
    'Install',
    'Commands',
    'Import order',
    'Style rules',
    'Adaptation points',
    'Existing tooling',
    'Standards notes',
]
_VARIANTS = ['recommended', 'google']
_TEMPLATE_DIRS = ('recommended', 'google', 'shared')
_SKILL_PATH = re.compile(
    r'`((?:references|templates|scripts|toolchains)/[^`\s*<>{}]+)`')


def _profiles() -> list[pathlib.Path]:
    return sorted(path.parent for path in _TOOLCHAINS.glob('*/profile.md'))


class ToolchainCatalogTest(unittest.TestCase):

    def test_catalog_lists_exactly_the_profiles_on_disk(self) -> None:
        catalog = (_SKILL / 'references' / 'toolchains.md').read_text(
            encoding='utf-8')
        listed = set(re.findall(r'\(\.\./toolchains/([^/]+)/profile\.md\)',
                                catalog))
        on_disk = {profile.name for profile in _profiles()}
        self.assertTrue(on_disk)
        self.assertEqual(listed, on_disk)

    def test_profiles_use_the_fixed_section_order(self) -> None:
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                sections = re.findall(r'^## (.+)$', text, flags=re.M)
                self.assertEqual(sections, _PROFILE_SECTIONS)

    def test_profiles_define_every_variant(self) -> None:
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                rows = re.findall(r'^\| `([a-z]+)` \|', text.split('## Variants')[1].split('\n## ')[0], flags=re.M)
                self.assertIn(rows, [_VARIANTS, _VARIANTS[:1]])
                style = text.split('## Style rules')[1].split('\n## ')[0]
                self.assertEqual(re.findall(r'^### (.+)$', style, flags=re.M), rows)
                for variant in rows:
                    rules = style.split(f'### {variant}')[1].split('\n### ')[0]
                    self.assertGreaterEqual(rules.count('\n- '), 3, variant)

    def test_profiles_name_a_test_framework(self) -> None:
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                toolchain = text.split('## Toolchain')[1].split('\n## ')[0]
                self.assertRegex(toolchain, r'(?m)^\| [^|]+ \| Test framework \|')

    def test_google_variants_link_their_style_guide(self) -> None:
        for profile in _profiles():
            text = (profile / 'profile.md').read_text(encoding='utf-8')
            variants = text.split('## Variants')[1].split('\n## ')[0]
            rows = [line for line in variants.splitlines()
                    if line.startswith('| `google` |')]
            if not rows:
                continue
            with self.subTest(profile=profile.name):
                self.assertRegex(rows[0], r'\]\(https://[^)]+\)')

    def test_profile_templates_and_files_match(self) -> None:
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                cited = set(re.findall(
                    r'`((?:recommended|google|shared)/[^`]+)`', text))
                on_disk = {
                    path.relative_to(profile).as_posix()
                    for directory in _TEMPLATE_DIRS
                    for path in (profile / directory).rglob('*')
                    if path.is_file()
                }
                self.assertFalse((profile / 'files').exists())
                self.assertEqual(cited - on_disk, set(),
                                 'profile cites missing templates')
                self.assertEqual(on_disk - cited, set(),
                                 'templates not cited by the profile')

    def test_structured_templates_parse(self) -> None:
        for path in sorted(_TOOLCHAINS.rglob('*')):
            if not path.is_file() or path.name == 'profile.md':
                continue
            text = path.read_text(encoding='utf-8')
            with self.subTest(template=str(path.relative_to(_TOOLCHAINS))):
                if path.suffix == '.json':
                    json.loads(text)
                elif path.suffix in {'.xml', '.props'}:
                    import xml.etree.ElementTree as ElementTree
                    ElementTree.fromstring(text)

    def test_toml_templates_parse(self) -> None:
        try:
            import tomllib
        except ModuleNotFoundError:
            self.skipTest('tomllib needs Python 3.11 or newer')
        for path in sorted(_TOOLCHAINS.rglob('*.toml')):
            with self.subTest(template=str(path.relative_to(_TOOLCHAINS))):
                tomllib.loads(path.read_text(encoding='utf-8'))

    def test_commands_tables_define_the_five_names(self) -> None:
        write_flags = ('--fix', '--write', '--in-place', 'spotlessApply',
                       'dart fix', ' -w ')
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                commands = text.split('## Commands')[1].split('\n## ')[0]
                rows = dict(re.findall(r'(?m)^\| `(\w+)` \| (.+) \|$', commands))
                self.assertEqual(list(rows), ['format', 'lint', 'typecheck',
                                              'test', 'verify'])
                for flag in write_flags:
                    self.assertNotIn(flag, rows['verify'])

    def test_style_rules_are_single_imperative_bullets(self) -> None:
        for profile in _profiles():
            with self.subTest(profile=profile.name):
                text = (profile / 'profile.md').read_text(encoding='utf-8')
                style = text.split('## Style rules')[1].split('\n## ')[0]
                for bullet in re.findall(r'(?m)^- (.+)$', style):
                    self.assertTrue(bullet.endswith('.'), bullet)
                    self.assertTrue(bullet[0].isupper() or bullet[0] == '`',
                                    bullet)


class SkillPathTest(unittest.TestCase):

    def test_cited_skill_paths_exist(self) -> None:
        for document in sorted(_SKILL.rglob('*.md')):
            if 'templates' in document.relative_to(_SKILL).parts:
                continue
            text = document.read_text(encoding='utf-8')
            for cited in _SKILL_PATH.findall(text):
                with self.subTest(document=document.name, path=cited):
                    self.assertTrue((_SKILL / cited.rstrip('/')).exists())


class InspectorToolchainTest(unittest.TestCase):

    def test_sources_map_to_profiles_per_application(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            files = {
                'apps/web/package.json': '{"name": "web"}',
                'apps/web/src/main.ts': '',
                'apps/web/src/view.tsx': '',
                'services/api/go.mod': 'module example.com/api\n',
                'services/api/main.go': '',
                'services/api/build.gradle.kts': '',
                'tools/script.py': '',
                'tools/deploy.sh': '',
                'mobile/settings.gradle.kts': '',
                'mobile/app/build.gradle.kts': '',
                'mobile/app/src/main/AndroidManifest.xml': '<manifest/>',
                'mobile/app/src/main/kotlin/Main.kt': '',
                'ios/App.xcodeproj/project.pbxproj': 'SDKROOT = iphoneos;',
                'ios/App/ContentView.swift': '',
                'shop/pubspec.yaml': 'name: shop\n',
                'shop/lib/main.dart': '',
                'shop/android/app/src/main/AndroidManifest.xml': '<manifest/>',
                'shop/ios/Runner.xcodeproj/project.pbxproj': 'SDKROOT = iphoneos;',
                'shop/ios/Runner/AppDelegate.swift': '',
                'tools/pyproject.toml': (
                    '[project]\nname = "tools"\n\n[tool.ruff.lint]\n'
                    'select = ["E"]\n\n[[tool.mypy.overrides]]\n'
                    'module = "x"\n'),
            }
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')

            result = subprocess.run(
                [sys.executable, str(_SKILL / 'scripts' / 'inspect_project.py'),
                 str(root)],
                check=True, capture_output=True, text=True)
            evidence = json.loads(result.stdout)
            profiles = evidence['toolchain_profiles']

        self.assertEqual(profiles['apps/web'], [{
            'profile': 'typescript',
            'profile_path': 'toolchains/typescript/profile.md',
            'source_files': 2,
        }])
        self.assertEqual([item['profile'] for item in profiles['services/api']],
                         ['go'])
        self.assertEqual([item['profile'] for item in profiles['tools']],
                         ['python', 'shell'])
        self.assertEqual(
            [(item['profile'], item.get('extends'))
             for item in profiles['mobile/app']],
            [('android', 'kotlin'), ('kotlin', None)])
        self.assertEqual(
            [(item['profile'], item.get('extends')) for item in profiles['ios']],
            [('ios', 'swift'), ('swift', None)])
        self.assertEqual([item['profile'] for item in profiles['shop']],
                         ['flutter'])
        self.assertFalse([owner for owner in profiles
                          if owner.startswith('shop/')])
        pyproject = next(manifest for manifest in evidence['manifests']
                         if manifest['path'] == 'tools/pyproject.toml')
        self.assertEqual(pyproject['tool_tables'], ['mypy', 'ruff'])


    def _inspect(self, files: dict[str, str], *options: str) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(_SKILL / 'scripts' / 'inspect_project.py'),
                 str(root), *options],
                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_flutter_application_at_the_repository_root(self) -> None:
        evidence = self._inspect({
            'pubspec.yaml': 'name: app\n',
            'lib/main.dart': '',
            'android/app/src/main/AndroidManifest.xml': '<manifest/>',
            'android/app/src/main/kotlin/Main.kt': '',
            'ios/Runner.xcodeproj/project.pbxproj': 'SDKROOT = iphoneos;',
            'ios/Runner/AppDelegate.swift': '',
            'tool/release.sh': '',
        })
        self.assertEqual(
            [item['profile'] for item in evidence['toolchain_profiles']['.']],
            ['flutter', 'shell'])
        self.assertEqual(list(evidence['toolchain_profiles']), ['.'])

    def test_platform_profiles_need_sources_of_the_extended_language(self) -> None:
        evidence = self._inspect({
            'java-app/build.gradle.kts': '',
            'java-app/src/main/AndroidManifest.xml': '<manifest/>',
            'java-app/src/main/java/Main.java': '',
            'objc/App.xcodeproj/project.pbxproj': 'SDKROOT = iphoneos;',
            'objc/main.m': '',
            'mac/Mac.xcodeproj/project.pbxproj': 'SDKROOT = macosx;',
            'mac/App.swift': '',
        })
        profiles = evidence['toolchain_profiles']
        self.assertEqual([item['profile'] for item in profiles['java-app']],
                         ['java'])
        self.assertNotIn('objc', profiles)
        self.assertEqual([item['profile'] for item in profiles['mac']],
                         ['swift'])

    def test_depth_limit_is_reported(self) -> None:
        files = {'service/go.mod': 'module x\n', 'service/a/b/c/main.go': ''}
        self.assertFalse(self._inspect(files)['max_depth_reached'])
        shallow = self._inspect(files, '--max-depth', '2')
        self.assertTrue(shallow['max_depth_reached'])
        self.assertNotIn('go', [item['profile'] for item in
                                shallow['toolchain_profiles'].get('service', [])])

    def test_tooling_evidence_covers_profile_configuration_files(self) -> None:
        evidence = self._inspect({
            'package.json': '{"name": "x", "prettier": {}, "eslintConfig": {}}',
            'analysis_options.yaml': '',
            '.shellcheckrc': '',
            'scripts/check.bats': '',
        })
        self.assertIn('analysis_options.yaml', evidence['tooling_configs'])
        self.assertIn('.shellcheckrc', evidence['tooling_configs'])
        package = evidence['manifests'][0]['package']
        self.assertEqual(package['embedded_tool_configs'],
                         ['eslintConfig', 'prettier'])
        self.assertEqual(
            [item['profile'] for item in evidence['toolchain_profiles']['.']],
            ['shell'])


if __name__ == '__main__':
    unittest.main()
