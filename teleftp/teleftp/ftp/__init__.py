from teleftp.telegram import TelegramBot

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler

import tempfile
import os.path

from teleftp.ftp.filesystem import FTPDriver, LocalDriver, FilesystemDriver, FilesystemError, FilesystemAuthError


class TelegramBotFileAccess(TelegramBot):
    USERNAME, PASSWORD, WORKFLOW = range(3)
    driver = FilesystemDriver
    auth_required = True

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, error)

    def command_start(self, bot, update):
        if 'motd-message' in self.config.telegram:
            update.message.reply_text(self.config.telegram['motd-message'])
        else:
            update.message.reply_text("Please enter username:")
        return TelegramBotFTP.USERNAME

    def command_username(self, bot, update, user_data):
        text = update.message.text
        user_data['username'] = text
        update.message.reply_text("Please enter password (won't be stored anywhere):")
        return TelegramBotFTP.PASSWORD

    def command_password(self, bot, update, user_data):
        password = update.message.text
        user_data['filesystem'] = type(self).driver(config=self.config)
        try:
            user_data['filesystem'].connect(user_data, password)
        except FilesystemError:
            update.message.reply_text("Login failed. Check username and password or try again later.")
            return TelegramBotFTP.USERNAME
        return self.command_workflow(bot, update, user_data, override_message=".")

    def command_logout(self, bot, update, user_data):
        if 'username' in user_data:
            del user_data['username']
        if 'filesystem' in user_data:
            user_data['filesystem'].disconnect()
            del user_data['filesystem']
        update.message.reply_text("Logout successful")
        return TelegramBotFTP.USERNAME

    def command_workflow(self, bot, update, user_data, override_message=None):
        if override_message is not None:
            message = override_message
        elif hasattr(update.message, 'document') and update.message.document is not None:
            message = '.'
            filename = update.message.document['file_name']
            file = update.message.document.get_file()
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, filename)
            file.download(file_path)
            user_data['filesystem'].put(filename, file_path)
            try:
                os.rmdir(temp_dir)
            except OSError:
                try:
                    os.remove(file_path)
                    os.rmdir(temp_dir)
                except FileNotFoundError:
                    pass
        elif hasattr(update.message, 'text'):
            message = update.message.text
        else: #Nothing to do
            return TelegramBotFTP.WORKFLOW
        if 'filesystem' not in user_data:
            return self.command_start(bot, update)
        answer_type, answer = user_data['filesystem'].get(message)
        if answer_type == FilesystemDriver.FILE:
            update.message.reply_document(document=answer, filename=message)
            answer.close()
        else: # Directory, or error
            try:
                pwd = user_data['filesystem'].pwd()
                files = user_data['filesystem'].ls()
            except FilesystemError:
                pwd = "?"
                files = []
                answer_type = FilesystemDriver.ERROR
                answer = "Unknown error."
            if answer_type == FilesystemDriver.DIRECTORY:
                if message != '.':
                    result = "Directory changed."
                else:
                    result = ""
            else:
                result = "Error: {}".format(answer)

            update.message.reply_text("{}\nCurrent directory: {}\n\n{}".format(result, pwd, "\n".join(files)),
                                      reply_markup=ReplyKeyboardMarkup([[x, ] for x in [".", ".."] + files],
                                                                       one_time_keyboard=True))
        return TelegramBotFTP.WORKFLOW

    def setup_handlers(self):
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.command_start)],
            states={
                TelegramBotFTP.USERNAME: [MessageHandler(Filters.text, self.command_username, pass_user_data=True), ],

                TelegramBotFTP.PASSWORD: [MessageHandler(Filters.text, self.command_password, pass_user_data=True), ],

                TelegramBotFTP.WORKFLOW: [MessageHandler(Filters.text | Filters.document,
                                                         self.command_workflow, pass_user_data=True), ],
            },
            fallbacks=[CommandHandler('logout', self.command_logout, pass_user_data=True)]
        )
        self.dp.add_handler(conversation_handler)
        self.dp.add_error_handler(self.error)


class TelegramBotFTP(TelegramBotFileAccess):
    driver = FTPDriver


class TelegramBotLocal(TelegramBotFileAccess):
    driver = LocalDriver
