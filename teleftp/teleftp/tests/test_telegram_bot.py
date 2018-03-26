from unittest import TestCase
from os import path
from telegram.error import InvalidToken

from teleftp.tests.test_config import TestConfigHelperMixin

import teleftp.config
import teleftp.telegram


class TestTelegramBot(TestConfigHelperMixin, TestCase):
    def test_sample_config_loads(self):
        config = teleftp.config.Config(self.conf_file_path)

        bot = teleftp.telegram.TelegramBot(config.telegram)
        self.assertRaises(RuntimeError, bot.idle)
        self.assertRaises(InvalidToken, bot.setup)