import codecs
import locale

from Models.utils import ConfigParser as config

lang_dict = {}


def reload_lang():
    lang_dict.clear()
    try:
        # this var is not useless. If no lang key in main.ini - this row trigger exception
        system_language = config.get_option_value('lang')
    except:
        system_default_lang = locale.getdefaultlocale()[0][:2]
        if system_default_lang in ('EN', 'en'):
            config.set_option_value('lang', 'en')
        elif system_default_lang in ('UA', 'ua'):
            config.set_option_value('lang', 'ua')
        else:
            config.set_option_value('lang', 'en')
    finally:
        system_language = config.get_option_value('lang')

    with codecs.open("Models/lang/{}.ini".format(system_language), encoding='utf-8') as file:
        for line in file:
            name, var = line.partition("=")[::2]
            lang_dict[name.strip()] = str(var).rstrip('\n')


def get(string):
    return lang_dict[string]


def get_key_by_value(value):
    for key, val in lang_dict.items():
        if val.replace('\r', '') == value.replace('\r', ''):
            return key
