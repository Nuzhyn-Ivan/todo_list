import os
import shutil

import configparser

from Models.utils.singleton import Singleton

DEFAULT_SECTION = "DEFAULT"
MAIN_CONFIG_PATH = "Models/main.ini"
BACKUP_CONFIG_PATH = "../TODO_config.ini"


class Config(metaclass=Singleton):
    _config_parser: configparser.ConfigParser = None

    def __init__(self):
        self._config_parser = configparser.ConfigParser()
        self._parse_config()

    def _parse_config(self):
        if os.path.exists(BACKUP_CONFIG_PATH):
            shutil.copyfile(BACKUP_CONFIG_PATH, MAIN_CONFIG_PATH)

        self._config_parser.read(MAIN_CONFIG_PATH)

    def get(self, option: str) -> str:
        """Get option value from _config_parser

        Args:
            option (str): Title of option.


        Returns:
            str: Option value
        """
        return self._config_parser.get(DEFAULT_SECTION, option)

    def set(self, option: str, value: str):
        """Set option value to configfile

        Args:
            option (str): title of option
            value (str): new value for option
        """

        self._config_parser.set(DEFAULT_SECTION, option, value)

        with open(MAIN_CONFIG_PATH, "w") as configfile:
            self._config_parser.write(configfile)
        shutil.copyfile(MAIN_CONFIG_PATH, BACKUP_CONFIG_PATH)
