from unittest import TestCase
from os import path

import teleftp.config


class TestConfigHelperMixin(object):
    @property
    def conf_file_path(self):
        return path.join(path.dirname(path.dirname(path.dirname(path.realpath(__file__)))), "config-example.json")


class TestConfig(TestConfigHelperMixin, TestCase):
    def test_sample_config_loads(self):
        config = teleftp.config.Config(self.conf_file_path)

        # Config has all necessary keys
        self.assertListEqual(list(config.config.keys()), ['telegram', 'ftp', 'local'])

        # Sample config doesn't have sensible data
        self.assertEqual(config.telegram['api-key'], "SECRET")