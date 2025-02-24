import configparser
import json
import os.path
from pathlib import Path
from typing import Optional

from chemotion_api import Reaction
from platformdirs import user_config_dir
from chemotion_api import Instance

config_dir = Path(user_config_dir("ChemDoE"))
templates_dir = config_dir / "templates"
config_path = config_dir / "config.ini"


class ConfigManager:
    _instance = None
    header_font = ('Arial', 16, 'bold')

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            cls._instance.read()
            cls._instance._favorites_reactions = None
            cls._instance._instance_key = None
            cls._instance._chemotion = None
            cls._instance._segments = None
        return cls._instance

    @property
    def chemotion(self) -> Optional[Instance]:
        return self._chemotion

    @chemotion.setter
    def chemotion(self, value: Optional[Instance]):
        self._chemotion = value

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
        if section not in cls.instance().config.sections():
            cls.instance().config.add_section(section)
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

    @property
    def favorites_with_names(self):
        if self.chemotion is None:
            self._favorites_reactions = []
        elif self._favorites_reactions is None:
            self._favorites_reactions = []
            for fav_id in self._load_favorites():
                self._load_add_reaction_fav(fav_id)
        return self._favorites_reactions

    def _load_add_reaction_fav(self, reaction_id: int, reaction: Optional[Reaction] = None) -> None:
        if reaction is None:
            reaction = self.chemotion.get_reaction(reaction_id)
        self._favorites_reactions.append((reaction_id, f"{reaction.short_label}: {reaction.name}"))

    @property
    def favorites(self):
        return [x[0] for x in self.favorites_with_names]

    def _load_favorites(self):
        self._instance_key = f"{self.get('Last', 'Host')}_{self.get('Last', 'User')}"
        return [int(id) for id in json.loads(self.get(self._instance_key, "Reaction", '[]'))]

    def add_to_favorites(self, reaction: Reaction):
        if reaction.id in self.favorites:
            return
        self._load_add_reaction_fav(reaction.id, reaction)
        self.favorites_with_names.sort(key=lambda x: int(x[0]))
        self.set(self._instance_key, "Reaction", json.dumps(self.favorites))

    def remove_from_favorites(self, reaction: Reaction):
        try:
            idx = self.favorites.index(int(reaction.id))
            del self._favorites_reactions[idx]
            self.set(self._instance_key, "Reaction", json.dumps(self.favorites))
        except ValueError:
            pass

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
            "User": "",
            "Remember": "0",
        }

        self.config["Favorites"] = {
            "Reaction": "[]"
        }
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        self.save()

    def save(self):
        with open(config_path, "w") as configfile:
            self.config.write(configfile)

    def all_additional_fields(self):
        if self._segments is None:
            segments = self.chemotion.generic_manager().load_all_segments()
            self._segments = []
            for segment in segments:
                if segment._element_klass.name == 'reaction' and segment.is_active:
                    for l in segment.properties.layers:
                        for f in l.fields:
                            self._segments.append((segment, l ,f))
        return self._segments


    def save_template(self, template, name):
        with open(templates_dir / name + '.json', "w") as configfile:
            configfile.write(json.dumps(template))