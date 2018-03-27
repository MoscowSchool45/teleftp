from teleftp.ftp import TelegramBotFTP
from teleftp.config import Config

import importlib

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("config_file", help="Path to config.json", type=str)
parser.add_argument("--bot_package", default="teleftp.ftp", type=str,
                    help="Bot package (default is teleftp.ftp)")
parser.add_argument("--bot_class", default="TelegramBotFTP", type=str,
                    help="Bot class (default is TelegramBotFTP)")

parser.parse_args()

args = parser.parse_args()

config = Config(args.config_file)

bot = getattr(importlib.import_module(args.bot_package), args.bot_class)(config)

print("Running teleftp bot")
bot.run_until_stopped()