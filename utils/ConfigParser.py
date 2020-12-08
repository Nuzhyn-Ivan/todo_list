from kivy.config import ConfigParser
import os
import shutil

__configfile = ConfigParser(interpolation=None)
__configfile.read('main.ini')


def get(option):
    return __configfile.get('DEFAULT', option)


def set(option, value):
    __configfile.set('DEFAULT', option, value)
    __configfile.write()
    shutil.copyfile('main.ini', '../TODO_config.ini')


def load_config():
    if os.path.exists('../TODO_config.ini'):
        shutil.copyfile('../TODO_config.ini', 'main.ini')  # load saved config
        __configfile.read('main.ini')  # refresh Kivy config
        __configfile.write()  # save config to main.ini file
        shutil.copyfile('main.ini', '../TODO_config.ini')

