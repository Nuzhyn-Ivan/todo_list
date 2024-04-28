import os
import shutil

import configparser


DEFAULT_SECTION = "DEFAULT"
MAIN_CONFIG_PATH = "Models/main.ini"
BACKUP_CONFIG_PATH = "../TODO_config.ini"

_config_parser = configparser.ConfigParser(interpolation=None)
_config_parser.read(MAIN_CONFIG_PATH)


def get_option_value(option: str, default: str = None) -> str:
    """Get option value from configfile
    :param option: title of option
    :type option: str
    :param default value to return if option not presented
    :type default: str
    :return: option value
    :rtype: str
    :raises:
    """
    try:
        return _config_parser.get(DEFAULT_SECTION, option)
    except:
        return default


def set_option_value(option: str, value: str):
    """Set option value to configfile
    :param option: title of option
    :type option: str
    :param value: new value for option
    :type value: str
    :return:
    :rtype:
    :raises:
    """
    _config_parser.set(DEFAULT_SECTION, option, value)

    with open(MAIN_CONFIG_PATH, "w") as configfile:
        _config_parser.write(configfile)
    shutil.copyfile(MAIN_CONFIG_PATH, BACKUP_CONFIG_PATH)


def load_config():
    # TODO: move out str to var, like '../TODO_config.ini'
    if os.path.exists(BACKUP_CONFIG_PATH):
        shutil.copyfile(BACKUP_CONFIG_PATH, MAIN_CONFIG_PATH)  # load saved config

    _config_parser = configparser.ConfigParser(interpolation=None)
    _config_parser.read(MAIN_CONFIG_PATH)
    # save config to main.ini file # TODO - is this step needed?
    shutil.copyfile(MAIN_CONFIG_PATH, BACKUP_CONFIG_PATH)
