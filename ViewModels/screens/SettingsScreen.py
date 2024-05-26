from kivy.uix.screenmanager import Screen

from Models.utils import DBLayer as db
from Models.utils.config_parser import Config
from main import MainApp


class SettingsScreen(Screen):
    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.config = Config()

        self.current_settings = dict(
            {
                "background_colour": self.config.get("background_colour"),
                "lang": self.config.get("lang"),
                "entries_font_size": self.config.get("entries_font_size"),
                "lists_font_size": self.config.get("lists_font_size"),
                "max_suggestions_count": self.config.get("max_suggestions_count"),
                "font_size": self.config.get("font_size"),
                "padding": self.config.get("padding"),
                "spacing": self.config.get("spacing"),
                "scrollview_size": self.config.get("scrollview_size"),
            }
        )

    def init_screen(self):
        self.get_current_settings()

    def get_current_settings(self):
        """
        Actualize self.current_settings from app config
        """
        for key in self.current_settings:
            self.current_settings[key] = self.config.get(key)

    @staticmethod
    def reset_db():
        """
        Drop current database and recreate it
        """
        # TODO Add popup msg that app will be closed and need to run manually. Or add correct restart of app
        db.drop_database()
        MainApp.get_running_app().stop()

    def apply_settings(self):
        """
        Apply settings from self.current_settings to app config

        """
        for key in self.current_settings:
            self.config.set(option=key, value=self.current_settings[key])
        # TODO lang reload doesnt work
        self.manager.refresh_screens()
