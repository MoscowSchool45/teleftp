from telegram.ext import Updater
import logging


class TelegramBot(object):
    def __init__(self, config):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.dp = None
        self.updater = None

    def setup(self):
        self.updater = Updater(
            token=self.config.telegram['api-key'],
            request_kwargs={
                'proxy_url': self.config.telegram['proxy-url']
            } if self.config.telegram['proxy-url'] is not None else {}
        )
        self.dp = self.updater.dispatcher
        self.setup_handlers()

    def start(self):
        if self.updater is None:
            raise RuntimeError("Attempt to start TelegramBot before calling setup()")
        self.updater.start_polling()

    def idle(self):
        if self.updater is None:
            raise RuntimeError("Attempt to idle TelegramBot before calling setup()")
        self.updater.idle()

    def setup_handlers(self):
        raise NotImplementedError()

    def run_until_stopped(self):
        self.setup()
        self.start()
        self.idle()
