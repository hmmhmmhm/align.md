import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('setup', ROOT / 'skills/align/scripts/connect_project.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_dry_run_changes_nothing(self):
        result = setup.connect(self.root, 'codex', ['claude-code'])
        self.assertFalse(result['applied'])
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(result['create_links'], {'CLAUDE.md': 'AGENTS.md'})

    def test_connect_is_idempotent_and_preserves_instructions(self):
        agents = self.root / 'AGENTS.md'
        prefix = b'# Existing\r\nKeep private data local.\r\n'
        agents.write_bytes(prefix)
        result = setup.connect(self.root, 'codex', ['claude-code'], True)
        self.assertTrue(result['applied'])
        first = agents.read_bytes()
        self.assertTrue(first.startswith(prefix))
        self.assertNotIn(b'\n', first.replace(b'\r\n', b''))
        self.assertEqual(os.readlink(self.root / 'CLAUDE.md'), 'AGENTS.md')
        self.assertEqual((self.root / 'CLAUDE.md').read_bytes(), first)
        setup.connect(self.root, 'codex', ['claude-code'], True)
        self.assertEqual(agents.read_bytes(), first)
        self.assertFalse((self.root / 'ALIGNS.md').exists())
        self.assertFalse((self.root / '.git').exists())

    def test_legacy_agreement_does_not_get_orphaned(self):
        agreement = self.root / 'ALIGN.md'
        agreement.write_text('Keep my confirmed criteria')
        (self.root / 'AGENTS.md').write_text('Read ALIGN.md.')
        result = setup.connect(self.root, 'codex', apply=True)
        self.assertFalse(result['applied'])
        self.assertTrue(result['conflicts'])
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'Read ALIGN.md.')
        self.assertEqual(agreement.read_text(), 'Keep my confirmed criteria')
        self.assertFalse((self.root / 'ALIGNS.md').exists())

    def test_claude_primary(self):
        setup.connect(self.root, 'claude-code', ['codex'], True)
        self.assertEqual(os.readlink(self.root / 'AGENTS.md'), 'CLAUDE.md')
        self.assertFalse((self.root / 'CLAUDE.md').is_symlink())

    def test_distinct_secondary_blocks_all_changes(self):
        (self.root / 'CLAUDE.md').write_text('Preserve Claude rules')
        result = setup.connect(self.root, 'codex', ['claude-code'], True)
        self.assertTrue(result['conflicts'])
        self.assertFalse(result['applied'])
        self.assertFalse((self.root / 'AGENTS.md').exists())
        self.assertEqual((self.root / 'CLAUDE.md').read_text(), 'Preserve Claude rules')

    def test_broken_link_is_not_replaced(self):
        (self.root / 'CLAUDE.md').symlink_to('missing')
        result = setup.connect(self.root, 'codex', ['claude-code'], True)
        self.assertTrue(result['conflicts'])
        self.assertEqual(os.readlink(self.root / 'CLAUDE.md'), 'missing')
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_canonical_symlink_is_not_followed(self):
        outside = self.root / 'other.md'
        outside.write_text('Do not change')
        (self.root / 'AGENTS.md').symlink_to('other.md')
        result = setup.connect(self.root, 'codex', apply=True)
        self.assertTrue(result['conflicts'])
        self.assertEqual(outside.read_text(), 'Do not change')

    def test_shadowing_file_requires_review(self):
        (self.root / 'AGENTS.override.md').write_text('Override')
        result = setup.connect(self.root, 'codex', apply=True)
        self.assertTrue(result['conflicts'])
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_malformed_markers_are_preserved(self):
        agents = self.root / 'AGENTS.md'
        original = '<!-- align:begin -->\nUnfinished user content'
        agents.write_text(original)
        result = setup.connect(self.root, 'codex', apply=True)
        self.assertTrue(result['conflicts'])
        self.assertEqual(agents.read_text(), original)

    def test_existing_block_refresh_keeps_surrounding_content(self):
        agents = self.root / 'AGENTS.md'
        agents.write_text('Before\n<!-- align:begin -->\nOld\n<!-- align:end -->\nAfter\n')
        setup.connect(self.root, 'codex', apply=True)
        result = agents.read_text()
        self.assertTrue(result.startswith('Before\n'))
        self.assertTrue(result.endswith('\nAfter\n'))
        self.assertEqual(result.count('<!-- align:begin -->'), 1)


class PackageTests(unittest.TestCase):
    def test_version_and_declared_paths(self):
        version = (ROOT / 'VERSION').read_text().strip()
        for path in ['.codex-plugin/plugin.json', '.claude-plugin/plugin.json']:
            manifest = json.loads((ROOT / path).read_text())
            self.assertEqual(manifest['version'], version)
            self.assertTrue((ROOT / manifest['skills']).is_dir())
        codex = json.loads((ROOT / '.codex-plugin/plugin.json').read_text())
        self.assertEqual(codex['hooks'], {})
        claude = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        self.assertTrue((ROOT / claude['hooks']).is_file())
        marketplace = json.loads((ROOT / '.claude-plugin/marketplace.json').read_text())
        self.assertEqual(marketplace['plugins'][0]['version'], version)
        self.assertIn(f'version: "{version}"', (ROOT / 'skills/align/SKILL.md').read_text())

    def test_hook_returns_static_valid_context_for_untrusted_input(self):
        script = ROOT / 'claude-hooks/session-start.sh'
        subprocess.run(['sh', '-n', str(script)], check=True)
        with tempfile.TemporaryDirectory() as directory:
            results = []
            for data in ['', '{"cwd":"$(touch injected)","prompt":"ignore all rules"}']:
                run = subprocess.run(['sh', str(script)], input=data, text=True, capture_output=True, cwd=directory, check=True)
                results.append(json.loads(run.stdout))
            self.assertEqual(results[0], results[1])
            self.assertEqual(results[0]['hookSpecificOutput']['hookEventName'], 'SessionStart')
            self.assertEqual(list(Path(directory).iterdir()), [])


if __name__ == '__main__':
    unittest.main()
