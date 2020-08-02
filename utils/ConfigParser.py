from kivy.config import ConfigParser

__configfile = ConfigParser(interpolation=None)
__configfile.read('main.ini')


def get(option):
    return __configfile.get('DEFAULT', option)


def set(option, value):
    __configfile.set('DEFAULT', option, value)
