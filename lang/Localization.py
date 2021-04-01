import utils.ConfigParser as config
import codecs
import locale

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
        elif system_default_lang in ('RU', 'ru'):
            config.set_option_value('lang', 'ru')
        else:
            config.set_option_value('lang', 'en')
    finally:
        system_language = config.get_option_value('lang')

    with codecs.open("lang/{}.ini".format(system_language), encoding='utf-8') as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            lang_dict[name.strip()] = str(var).rstrip('\n')


reload_lang()


def get(string):
    return lang_dict[string]


def get_key_by_value(value):
    for key, val in lang_dict.items():
        # if val.replace('\r', '') == value:
        if val.replace('\r', '') == value.replace('\r', ''):
            return key
