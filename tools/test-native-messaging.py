#!/usr/bin/env python3
"""Tests isolés des manifestes : aucun accès aux profils ou comptes réels."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('native', Path(__file__).with_name('native-messaging.py'))
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)


class NativeMessagingTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = self.home / '.config'
        self.env = patch.dict(os.environ, {'CHROME_CONFIG_HOME': str(self.config)})
        self.env.start()
        self.addCleanup(self.env.stop)

    def manifest(self, folder, name=None):
        name = name or next(iter(native.HOSTS))
        executable = self.home / 'host'
        executable.write_text('#!/bin/sh\nexit 0\n')
        executable.chmod(0o700)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (name + '.json')
        path.write_text(json.dumps({'name': name, 'type': 'stdio',
            'path': str(executable), 'allowed_origins': sorted(native.HOSTS[name])}))
        return path

    def inspect(self, platform='linux', **kwargs):
        return native.inspect(self.config, home=self.home, platform=platform, **kwargs)

    def test_diagnosis_does_not_create_target(self):
        self.manifest(self.config / 'google-chrome/NativeMessagingHosts')
        result = self.inspect()
        self.assertFalse(Path(result['target']).exists())
        self.assertFalse(result['claude_present'])
        self.assertTrue(result['hosts'][0]['valid'])

    def test_linux_links_both_official_hosts_and_is_idempotent(self):
        for name in native.HOSTS:
            self.manifest(self.config / 'chromium/NativeMessagingHosts', name)
        result = self.inspect(link=True)
        self.assertTrue(result['claude_present'])
        self.assertTrue(result['codex_present'])
        before = {p.name: os.readlink(p) for p in Path(result['target']).iterdir()}
        self.inspect(link=True)
        self.assertEqual(before, {p.name: os.readlink(p) for p in Path(result['target']).iterdir()})

    def test_macos_targets_bluelium_not_linux_config(self):
        self.manifest(self.home / 'Library/Application Support/Google/Chrome/NativeMessagingHosts')
        result = self.inspect('mac', link=True)
        self.assertEqual(result['target'], str(self.home / 'Library/Application Support/Bluelium/NativeMessagingHosts'))
        self.assertTrue(result['claude_present'])
        self.assertFalse(self.config.exists())

    def test_broken_target_is_never_overwritten(self):
        self.manifest(self.config / 'google-chrome/NativeMessagingHosts')
        target, _ = native.locations(self.home, self.config, 'linux')
        target.mkdir(parents=True)
        dest = target / (next(iter(native.HOSTS)) + '.json')
        dest.symlink_to('/nonexistent/bluelium-test')
        self.assertFalse(self.inspect(link=True)['claude_present'])
        self.assertEqual(os.readlink(dest), '/nonexistent/bluelium-test')

    def test_invalid_origins_and_non_objects_are_not_installed(self):
        source = self.manifest(self.config / 'google-chrome/NativeMessagingHosts')
        data = json.loads(source.read_text())
        for origins in [[], ['chrome-extension://wrong/'], '*', [True],
                        [*data['allowed_origins'], 'chrome-extension://*/']]:
            data['allowed_origins'] = origins
            source.write_text(json.dumps(data))
            self.assertFalse(self.inspect(link=True)['claude_present'])
        source.write_text('[]')
        self.assertFalse(self.inspect(link=True)['claude_present'])

    def test_chrome_config_home_and_explicit_target(self):
        custom = self.home / 'chrome-config'
        with patch.dict(os.environ, {'CHROME_CONFIG_HOME': str(custom)}):
            self.manifest(custom / 'google-chrome/NativeMessagingHosts')
            target = self.home / 'isolated/NativeMessagingHosts'
            result = self.inspect(target=target, link=True)
            self.assertTrue(result['claude_present'])
            self.assertEqual(result['target'], str(target))


if __name__ == '__main__':
    unittest.main()
