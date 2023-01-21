from kivy.properties import DictProperty
from kivy.uix.screenmanager import Screen

from Models.utils import ConfigParser as config, DBLayer as db
from main import MainApp


class SettingsScreen(Screen):
    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    current_settings = DictProperty({
        'background_colour': config.get_option_value('background_colour'),
        'lang': config.get_option_value('lang'),
        'entries_font_size': config.get_option_value('entries_font_size'),
        'lists_font_size': config.get_option_value('lists_font_size'),
        'max_suggestions_count': config.get_option_value('max_suggestions_count'),
        'font_size': config.get_option_value('font_size'),
        'padding': config.get_option_value('padding'),
        'spacing': config.get_option_value('spacing'),
        'scrollview_size': config.get_option_value('scrollview_size'),
    })

    def init_screen(self):
        self.get_current_settings()

    def get_current_settings(self):
        """
        Actualize self.current_settings from app config
        :param:
        :return:
        """
        for key in self.current_settings:
            self.current_settings[key] = config.get_option_value(key)

    @staticmethod
    def reset_db():
        """
        Drop current database and recreate it
        :param:
        :return:
        """
        # TODO Add popup msg that app will be closed and need to run manually. Or add correct restart of app
        db.drop_database()
        MainApp.get_running_app().stop()

    def apply_settings(self):
        """
        Apply settings from self.current_settings to app config
        :param:
        :return:
        """
        for key in self.current_settings:
            config.set_option_value(option=key, value=self.current_settings[key])
        # TODO lang reload doesnt work
        self.manager.refresh_screens()
