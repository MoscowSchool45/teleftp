import json


class Config(object):
    def __init__(self, config_filename):
        with open(config_filename, "r") as f:
            self.config = json.load(f)

    def __getattr__(self, name):
        return self.config[name]
