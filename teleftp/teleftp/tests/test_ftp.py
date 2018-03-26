from unittest import TestCase
from telegram.error import InvalidToken

from teleftp.tests.test_config import TestConfigHelperMixin

import teleftp.config
import teleftp.ftp


class TestTelegramBot(TestConfigHelperMixin, TestCase):
    def test_sample_config_loads(self):
        config = teleftp.config.Config(self.conf_file_path)

        bot = teleftp.ftp.TelegramBotFTP(config)
        self.assertRaises(RuntimeError, bot.idle)
        self.assertRaises(InvalidToken, bot.setup)