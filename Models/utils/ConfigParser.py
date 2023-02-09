import os
import shutil

from kivy.config import ConfigParser

__configfile = ConfigParser(interpolation=None)
__configfile.read('Models/main.ini')


def get_option_value(option: str, default: str = None) -> str:
    """ Get option value from configfile
    :param option: title of option
    :type option: str
    :param default value to return if option not presented
    :type default: str
    :return: option value
    :rtype: str
    :raises:
    """
    try:
        return __configfile.get('DEFAULT', option)
    except:
        return default


def set_option_value(option: str, value: str):
    """ Set option value to configfile
    :param option: title of option
    :type option: str
    :param value: new value for option
    :type value: str
    :return:
    :rtype:
    :raises:
    """
    __configfile.set('DEFAULT', option, value)
    __configfile.write()
    shutil.copyfile('Models/main.ini', '../TODO_config.ini')


def load_config():
    # TODO: move out str to var, like '../TODO_config.ini'
    if os.path.exists('../TODO_config.ini'):
        shutil.copyfile('../TODO_config.ini', 'Models/main.ini')  # load saved config
        __configfile.read('Models/main.ini')  # refresh Kivy config
        __configfile.write()  # save config to main.ini file # todo - is this step needed?
        shutil.copyfile('Models/main.ini', '../TODO_config.ini')
