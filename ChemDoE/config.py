import configparser
import glob
import json
import os.path
import shutil
import sys
import uuid
from pathlib import Path
from typing import Optional

from chemotion_api import Reaction
from chemotion_api.labImotion.items.options import FieldType
from platformdirs import user_config_dir
from chemotion_api import Instance
from requests import RequestException

config_dir = Path(user_config_dir("ChemDoE"))
templates_dir = config_dir / "templates"
script_dir = config_dir / "scripts"
doe_dir = config_dir / "doe"
config_path = config_dir / "config.ini"


class ConfigManager:
    _instance = None
    header_font = ('Arial', 16, 'bold')
    small_font = ('Arial', 10)
    normal_font = ('Arial', 12)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.config = configparser.ConfigParser()
            cls._instance.read()
            cls._instance._favorites_reactions = None
            cls._instance._instance_key = None
            cls._instance._chemotion = None
            cls._instance._segments = None
            cls._instance.python_interpreters = []
            cls._instance.r_interpreters = []
            cls._instance.find_all_python_interpreters()
            cls._instance.find_r_interpreters()
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

    def logout(self):
        self.set("Chemotion", "host", '', commit=False)
        self.set("Chemotion", "user", '', commit=False)
        self.set("Chemotion", "token", '')
        self.chemotion = None
        self._favorites_reactions = None

    @property
    def favorites_with_names(self):
        if self.chemotion is None:
            self._favorites_reactions = []
        elif self._favorites_reactions is None:
            self._favorites_reactions = []
            for fav_id in self._load_favorites():
                if not self._load_add_reaction_fav(fav_id):
                    self.remove_from_favorites(fav_id)
        return self._favorites_reactions

    def _load_add_reaction_fav(self, reaction_id: int, reaction: Optional[Reaction] = None) -> bool:
        if reaction is None:
            try:
                reaction = self.chemotion.get_reaction(reaction_id)
            except RequestException:
                return False
        self._favorites_reactions.append((reaction_id, f"{reaction.short_label}: {reaction.name}"))
        return True

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

    def remove_from_favorites(self, reaction: Reaction | int):
        try:
            if isinstance(reaction, Reaction):
                reaction = reaction.id
            idx = self.favorites.index(int(reaction))
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
                if segment.identifier is None:
                    segment.identifier = uuid.uuid4().__str__()
                    segment.save()
                if segment._element_klass.name == 'reaction' and segment.is_active:
                    for l in segment.properties.layers:
                        for f in l.fields:
                            if f.field_type in [FieldType.SYSTEM_DEFINED, FieldType.FORMULA_FIELD, FieldType.INTEGER]:
                                self._segments.append((segment, l, f))
        return self._segments

    def save_doe(self, template, name):
        os.makedirs(doe_dir, exist_ok=True)
        with open(doe_dir / (name + '.json'), "w+") as configfile:
            configfile.write(json.dumps(template))

    def load_doe(self, name, ):
        file_path = doe_dir / (name + '.json')
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r") as configfile:
            return json.loads(configfile.read())

    def load_scripts(self):
        file_path = script_dir / 'config.json'
        if not os.path.exists(file_path):
            self.save_scripts([])
        with open(file_path, "r") as configfile:
            return json.loads(configfile.read())['runs'] + self._generate_default_scripts()

    def save_scripts(self, content: list[dict]):
        file_path = script_dir / 'config.json'
        os.makedirs(script_dir, exist_ok=True)
        with open(file_path, "w+") as configfile:
            configfile.write(json.dumps({'runs': [x for x in content if not x['id'].startswith('__default_')]}))

    def save_template(self, template, name):
        os.makedirs(templates_dir, exist_ok=True)
        with open(templates_dir / (name + '.json'), "w+") as configfile:
            configfile.write(json.dumps(template))

    def load_template(self, name):
        with open(templates_dir / (name + '.json'), "r") as configfile:
            return json.loads(configfile.read())

    def load_templates(self):
        os.makedirs(templates_dir, exist_ok=True)
        return [file for file in templates_dir.iterdir() if file.is_file()]

    def find_all_python_interpreters(self):
        interpreters = set()
        interpreters.update(self.find_python_interpreters())
        interpreters.update(self.find_python_in_common_locations())

        self.python_interpreters = list(interpreters)
        self.python_interpreters.sort(key=lambda x: len(x))
        if len(self.python_interpreters) == 0:
            from tkinter import messagebox
            messagebox.showwarning("Python not installed", "Please install a Python interpreter!")

    @staticmethod
    def find_python_interpreters():
        possible_interpreters = ["python", "python3", "python3.10", "python3.11", "python3.12", "python3.13"]
        found_interpreters = []

        for interpreter in possible_interpreters:
            path = shutil.which(interpreter)
            if path and path not in found_interpreters:
                found_interpreters.append(path)

        return found_interpreters

    @staticmethod
    def find_python_in_common_locations():
        paths = [
            "C:\\Python*\\python.exe",  # Common Windows installations
            "C:\\Users\\*\\AppData\\Local\\Programs\\Python\\Python*\\python.exe",
            "/usr/bin/python*",  # Linux/macOS system-wide
            "/usr/local/bin/python*",
            "/opt/python*",
        ]

        found = []
        for pattern in paths:
            found.extend([x for x in glob.glob(pattern) if not x.endswith("-config")])

        return found

    @staticmethod
    def find_win_r_executables() -> list[str]:
        possible_paths = [
            os.path.join(os.getenv("ProgramFiles"), "R"),  # Standard install location
            os.path.join(os.getenv("ProgramFiles(x86)"), "R"),  # 32-bit install location
            os.path.join(os.getenv("LOCALAPPDATA"), "Programs", "R"),  # Some custom installs
            "C:\\R"  # Occasionally used custom path
        ]

        found_executables = []

        # Search for R.exe in common paths
        for base_path in possible_paths:
            if base_path and os.path.exists(base_path):
                found_executables.extend(glob.glob(os.path.join(base_path, "**", "Rscript.exe"), recursive=True))

        # Search in system PATH
        for path in os.getenv("PATH", "").split(os.pathsep):
            r_exe = os.path.join(path, "Rscript.exe")
            if os.path.exists(r_exe):
                found_executables.append(str(r_exe))

        return found_executables

    def find_r_interpreters(self):
        r_path = shutil.which("Rscript")
        if not r_path:
            r_path = []
        else:
            r_path = [r_path]

        if os.name == "nt":
            r_path += self.find_python_interpreters()

        if len(r_path) == 0:
            from tkinter import messagebox
            messagebox.showwarning("R not installed", "Please install a R interpreter!")

        self.r_interpreters = r_path

    def _generate_default_scripts(self):
        results = []
        src_dir = Path(__file__).parent / 'examples'
        os.makedirs(script_dir, exist_ok=True)
        if len(self.python_interpreters) >= 0:
            for i, filename in enumerate(os.listdir(src_dir)):
                src = src_dir / filename
                if src.suffix != '.py':
                    continue
                dst = script_dir / filename
                if not dst.exists():
                    shutil.copyfile(src, dst)
                results.append({
                    'id': f'__default_P{i}',
                    'name': f'[Default] {filename}',
                    'file_type': 'Python',
                    'input': filename.split('_')[0].upper(),
                    'output': filename.split('_')[0].upper(),
                    'file': dst.__str__(),
                    'interpreter': self.python_interpreters[0]
                })
        if len(self.r_interpreters) >= 0:
            for i, filename in enumerate(os.listdir(src_dir)):
                src = src_dir / filename
                dst = script_dir / filename

                if src.suffix != '.R':
                    continue
                if not dst.exists():
                    shutil.copyfile(src, dst)
                results.append({
                    'id': f'__default_R{i}',
                    'name': f'[Default] {filename}',
                    'file_type': 'R',
                    'input': filename.split('_')[0].upper(),
                    'output': filename.split('_')[0].upper(),
                    'file': str(dst),
                    'interpreter': self.r_interpreters[0]
                })


        return results
