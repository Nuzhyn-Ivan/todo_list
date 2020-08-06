import utils.ConfigParser as config

system_language = config.get('lang')
lang_dict = {}


with open("lang/{}.ini".format(system_language)) as myfile:
    for line in myfile:
        name, var = line.partition("=")[::2]
        lang_dict[name.strip()] = str(var)


def get(string):
    return lang_dict[string]
