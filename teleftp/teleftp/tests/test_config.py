from unittest import TestCase
from os import path

import teleftp.config


class TestConfig(TestCase):
    def setUp(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conf_file_path = path.join(path.dirname(path.dirname(path.dirname(path.realpath(__file__)))),
                                        "config-example.json")

    def test_sample_config_loads(self):
        config = teleftp.config.Config(self.conf_file_path)
        self.assertEqual(config.config['telegram']['api-key'], "SECRET")
