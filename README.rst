TeleFTP
-------

A tool to provide file access through telegram interface. Waning: has
**insecure** authorisation: ftp password is sent in plain text through telegram chat, so it is a pretty bad idea to use this for any sensible data.

Installation
^^^^^^^^^^^^
``pip install teleftp``

Usage
^^^^^
To run the bot:

``python -m teleftp config.json``

To use from your own code: ::

 from teleftp.ftp import TelegramBotFTP
 from teleftp.config import Config

 config = Config('some_file.json')
 bot = TelegramBotFTP(config)
 bot.run_until_stopped()

Configuration
^^^^^^^^^^^^^

Sample configuration file is included here: `config-example.json <https://github.com/MoscowSchool45/teleftp/blob/master/config-example.json>`_.

Known issues
^^^^^^^^^^^^

* FTP session objects are stored forever, no timeout
* No support for FTP proxies
* Insecure password communication needs to be reworked (probably using a link to web page over https and password field)
