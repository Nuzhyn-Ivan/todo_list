from kivy.config import ConfigParser

__configfile = ConfigParser(interpolation=None)
__configfile.read('main.ini')


# TODO implement independence from 'section' - add section automatically
def get(section, option):
    return __configfile.get(section, option)


def set(section, option, value):
    __configfile.set(section, option, value)
