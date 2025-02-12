import configparser
import os.path
from pathlib import Path

from platformdirs import user_config_dir

config_dir = Path(user_config_dir("ChemDoE"))
config_path = config_dir / "config.ini"


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            cls._instance.read()
        return cls._instance

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance

    @classmethod
    def read(cls):
        if os.path.exists(config_path):
            cls.instance().config.read(config_path)
        else:
            cls.instance()._set_defaults()

    @classmethod
    def set(cls, section, option, value, commit: bool = True):
        cls.instance().config.set(section, option, value)
        if commit:
            cls.instance().save()
            cls.instance().config = configparser.ConfigParser()
            cls.instance().read()


    @classmethod
    def get(cls, section, option, default=None):
        try:
            return cls.instance().config.get(section, option)
        except (configparser.NoOptionError, configparser.NoSectionError):
            return default

    def _set_defaults(self):
        self.config["DEFAULT"] = {
            "AppName": "ChemDoE",
            "Debug": "False"
        }

        self.config["Chemotion"] = {
            "Host": "",
            "User": "",
            "Token": "",
        }

        self.config["Last"] = {
            "Host": "",
            "Remember": "0",
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        self.save()

    def save(self):
        with open(config_path, "w") as configfile:
            self.config.write(configfile)



