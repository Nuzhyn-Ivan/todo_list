from kivy.config import ConfigParser
import os
import shutil

__configfile = ConfigParser(interpolation=None)
__configfile.read('main.ini')


def get_option_value(option: str) -> str:
    """ Get option value from configfile
    :param option: title of option
    :type option: str
    :return: option value
    :rtype: str
    :raises:
    """
    return __configfile.get('DEFAULT', option)


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
    shutil.copyfile('main.ini', '../TODO_config.ini')


def load_config():
    # TODO: move out str to var, like '../TODO_config.ini'
    if os.path.exists('../TODO_config.ini'):
        shutil.copyfile('../TODO_config.ini', 'main.ini')  # load saved config
        __configfile.read('main.ini')  # refresh Kivy config
        __configfile.write()  # save config to main.ini file # todo - is this step needed?
        shutil.copyfile('main.ini', '../TODO_config.ini')

