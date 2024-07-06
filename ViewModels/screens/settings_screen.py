from kivy.uix.screenmanager import Screen

from Models.utils import database_layer as db
from Models.utils.screen_manager import ScreenManager
from Models.utils.config_parser import Config
from main import MainApp


class SettingsScreen(Screen):
    manager: ScreenManager
    configuration: Config
    current_settings: dict

    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.configuration = Config()

        self.current_settings = dict(
            {
                "background_color": self.configuration.get("background_color"),
                "lang": self.configuration.get("lang"),
                "entries_font_size": self.configuration.get("entries_font_size"),
                "lists_font_size": self.configuration.get("lists_font_size"),
                "max_suggestions_count": self.configuration.get("max_suggestions_count"),
                "font_size": self.configuration.get("font_size"),
                "padding": self.configuration.get("padding"),
                "spacing": self.configuration.get("spacing"),
                "scrollview_size": self.configuration.get("scrollview_size"),
            }
        )

    def actualize_current_settings(self):
        """
        Actualize self.current_settings from app config
        """
        for key in self.current_settings:
            self.current_settings[key] = self.configuration.get(key)

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
            self.configuration.set(option=key, value=self.current_settings[key])
        # TODO lang reload does not work
        self.manager.refresh_screens()
