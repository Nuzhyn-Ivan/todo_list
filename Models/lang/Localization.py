import codecs
import locale

from Models.utils import ConfigParser as config

lang_dict = {}
supported_lang_path = {
    'en': 'Models/lang/english.ini',
    'ua': 'Models/lang/ukrainian.ini',
}


def reload_lang():
    lang_dict.clear()
    system_language = config.get_option_value('lang')
    if system_language is None:
        system_default_lang = locale.getdefaultlocale()[0][:2].lower()
        system_language = 'en' if system_default_lang not in supported_lang_path.keys() else system_default_lang
        config.set_option_value('lang', system_language)

    with codecs.open(supported_lang_path.get(system_language), encoding='utf-8') as file:
        for line in file:
            name, _, var = line.partition("=")
            lang_dict[name.strip()] = var.rstrip()


def get(key: str):
    return lang_dict[key]


def get_key_by_value(value):
    for key, val in lang_dict.items():
        if val.rstrip() == value.rstrip():
            return key
