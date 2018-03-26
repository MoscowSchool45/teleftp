from unittest import TestCase
from telegram import Update, Message, Chat, User, Document, File

from teleftp.tests.test_config import TestConfigHelperMixin

import teleftp.config
import teleftp.ftp
import teleftp.telegram

import tempfile
import os
import os.path
import datetime


class DummyTelegramBotMixin(object):
    class DummyUpdater(object):
        def __init__(self, dispatcher):
            self.dispatcher = dispatcher

        def handle(self, update):
            for handler in self.dispatcher.handlers:
                if handler.check_update(update):
                    handler.handle_update(update, self.dispatcher)

        def start_polling(self):
            pass

        def idle(self):
            pass

    class DummyDispatcher(object):
        def __init__(self):
            self.handlers = []
            self.error_handler = None
            self.bot = DummyTelegramBotMixin.DummyBot()
            self.user_data = {
                None: {},
                1: {}
            }

        def add_handler(self, handler):
            self.handlers.append(handler)

        def add_error_handler(self, handler):
            self.error_handler = handler

    class DummyBot(object):
        def __init__(self):
            self.messages = []
            self.request = DummyTelegramBotMixin.DummyBotRequest()

        @property
        def username(self):
            return ("bot")

        def send_message(self, *args, **kwargs):
            self.messages.append(args)

        def send_document(self, *args, **kwargs):
            self.messages.append((args[0], kwargs['filename'], kwargs['document'].read()))

        def clear(self):
            self.messages = []

        def get_file(self, id, timeout=1):
            return File(id, bot=self)

    class DummyBotRequest(object):
        def download(self, url, filename, timeout=1):
            with open(filename, 'wb') as f:
                f.write(b"Test Test Test")

    def setup(self):
        self.setup_handlers()

    def __init__(self, config):
        self.config = config
        self.dp = DummyTelegramBotMixin.DummyDispatcher()
        self.updater = DummyTelegramBotMixin.DummyUpdater(self.dp)

    def setup_handlers(self):
        raise NotImplementedError()

    def message(self, update):
        return self.updater.handle(update)

    def clear(self):
        self.dp.bot.clear()

    @property
    def answers(self):
        return self.dp.bot.messages



class DummyTelegramBotLocal(DummyTelegramBotMixin, teleftp.ftp.TelegramBotLocal):
    def setup_handlers(self):
        teleftp.ftp.TelegramBotLocal.setup_handlers(self)


class DummyTelegramBotFTP(DummyTelegramBotMixin, teleftp.ftp.TelegramBotFTP):
    def setup_handlers(self):
        teleftp.ftp.TelegramBotFTP.setup_handlers(self)


class TestTelegramLocalBot(TestConfigHelperMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(self.clean_temp_dir)
        self.temp_dir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.temp_dir, "dir1"))
        with open(os.path.join(self.temp_dir, "file1.txt"), 'w') as f:
            f.write("Test")
        with open(os.path.join(self.temp_dir, "file2.txt"), 'w') as f:
            f.write("Test")

    def clean_temp_dir(self):
        os.remove(os.path.join(self.temp_dir, "file1.txt"))
        os.remove(os.path.join(self.temp_dir, "file2.txt"))
        if os.path.exists(os.path.join(self.temp_dir, "file3.txt")):
            os.remove(os.path.join(self.temp_dir, "file3.txt"))
        os.rmdir(os.path.join(self.temp_dir, "dir1"))
        os.rmdir(self.temp_dir)

    def test_local_bot_filesize_exceeded(self):
        config = teleftp.config.Config(self.conf_file_path)
        config.local['root_directory'] = self.temp_dir
        config.ftp['size-limit'] = 2

        bot = DummyTelegramBotLocal(config)
        bot.run_until_stopped()

        user = User(1, 'Test', False)
        chat = Chat(1, 'private')

        bot.message(Update(1, message=Message(
                        1, user, datetime.datetime.now(), chat, text="/start", bot=bot.dp.bot))
                    )
        bot.message(Update(2, message=Message(
                        2, user, datetime.datetime.now(), chat, text="username1", bot=bot.dp.bot))
                    )
        bot.message(Update(3, message=Message(
                        3, user, datetime.datetime.now(), chat, text="password1", bot=bot.dp.bot))
                    )
        bot.clear()
        # Get file
        bot.message(Update(7, message=Message(
                        7, user, datetime.datetime.now(), chat, text="file2.txt", bot=bot.dp.bot))
                    )

        self.assertListEqual(bot.answers, [
            (1,'Error: File too large to be sent.\n'
               'Current directory: {}\n\ndir1\nfile1.txt\nfile2.txt'.format(self.temp_dir))
        ])
        bot.clear()


    def test_local_bot(self):
        config = teleftp.config.Config(self.conf_file_path)
        config.local['root_directory'] = self.temp_dir

        bot = DummyTelegramBotLocal(config)
        bot.run_until_stopped()

        user = User(1, 'Test', False)
        chat = Chat(1, 'private')

        # Username
        bot.message(Update(1, message=Message(
                        1, user, datetime.datetime.now(), chat, text="/start", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [(1, "Please enter username:"), ])
        bot.clear()

        # Password
        bot.message(Update(2, message=Message(
                        2, user, datetime.datetime.now(), chat, text="username1", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [(1, "Please enter password (won't be stored anywhere):"), ])
        bot.clear()

        bot.message(Update(3, message=Message(
                        3, user, datetime.datetime.now(), chat, text="password1", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [
            (1, "\nCurrent directory: {}\n\ndir1\nfile1.txt\nfile2.txt".format(self.temp_dir)),
        ])
        bot.clear()

        # Move down to directory
        bot.message(Update(4, message=Message(
                        4, user, datetime.datetime.now(), chat, text="dir1", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [
            (1, "Directory changed.\nCurrent directory: {}\n\n".format(os.path.join(self.temp_dir, 'dir1'))),
        ])
        bot.clear()

        # Move back and prevent escaping from root
        bot.message(Update(5, message=Message(
                        5, user, datetime.datetime.now(), chat, text="..", bot=bot.dp.bot))
                    )
        bot.message(Update(6, message=Message(
                        6, user, datetime.datetime.now(), chat, text="..", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [
            (1, "Directory changed.\nCurrent directory: {}\n\ndir1\nfile1.txt\nfile2.txt".format(self.temp_dir)),
            (1, "Directory changed.\nCurrent directory: {}\n\ndir1\nfile1.txt\nfile2.txt".format(self.temp_dir)),
        ])
        bot.clear()

        # Get file
        bot.message(Update(7, message=Message(
                        7, user, datetime.datetime.now(), chat, text="file2.txt", bot=bot.dp.bot))
                    )

        self.assertListEqual(bot.answers, [(1, 'file2.txt', b'Test')])
        bot.clear()

        # Get a nonexistent file
        bot.message(Update(8, message=Message(
                        8, user, datetime.datetime.now(), chat, text="file3.txt", bot=bot.dp.bot))
                    )

        self.assertListEqual(bot.answers, [
            (1, "Error: File not found.\nCurrent directory: {}\n\ndir1\nfile1.txt\nfile2.txt".format(self.temp_dir)),
        ])
        bot.clear()

        # Put a file
        document = Document(1, file_name="file3.txt", bot=bot.dp.bot)

        bot.message(Update(9, message=Message(
                        9, user, datetime.datetime.now(), chat, text="", document=document, bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [
            (1, "\nCurrent directory: {}\n\ndir1\nfile1.txt\nfile2.txt\nfile3.txt".format(self.temp_dir)),
        ])
        bot.clear()

        # Check if uploaded correctly
        bot.message(Update(7, message=Message(
                        7, user, datetime.datetime.now(), chat, text="file3.txt", bot=bot.dp.bot))
                    )

        self.assertListEqual(bot.answers, [(1, 'file3.txt', b'Test Test Test')])
        bot.clear()
        os.remove(os.path.join(self.temp_dir, "file3.txt"))

        # Check logout
        bot.message(Update(8, message=Message(
                        8, user, datetime.datetime.now(), chat, text="/logout", bot=bot.dp.bot))
                    )

        self.assertListEqual(bot.answers, [(1, 'Logout successful')])
        bot.clear()

        # Check wrong login
        bot.message(Update(9, message=Message(
                        9, user, datetime.datetime.now(), chat, text="user", bot=bot.dp.bot))
                    )
        bot.clear()
        bot.message(Update(10, message=Message(
                        10, user, datetime.datetime.now(), chat, text="password", bot=bot.dp.bot))
                    )
        self.assertListEqual(bot.answers, [(1, 'Login failed. Check username and password or try again later.')])
        bot.clear()