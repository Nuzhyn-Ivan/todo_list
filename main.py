from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

import Models.lang.localization as lang
from Models.utils.config_parser import Config
from Models.utils import database_layer as db
from Models.utils.screen_manager import ScreenManager
from ViewModels.popups.error_popup import ErrorPopup


class MainApp(App):
    configuration: Config
    icon: str
    title: str

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        self.configuration = Config()  # kivy adds 'config' object so cant use this name

    def build(self):
        """
        Build app
        """
        # TODO refactor background - handle list type for config.get()
        background_dict = {
            "Orange": [0.8, 0.4, 0.0, 1],
            "White": [1.0, 1.0, 1.0, 1],
            "Black": [0, 0, 0, 1],
        }
        Window.clearcolor = background_dict[self.configuration.get("background_color")]
        Window.softinput_mode = "below_target"  # TextInput keyboard position https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs
        # TODO move ALL paths to system settings
        self.icon = "images/icon.png"
        self.title = (
            f"{self.configuration.get('app_title')}  {self.configuration.get('app_version')}"
        )
        lang.reload_lang()

        return ScreenManager()

    @staticmethod
    def open_error_popup(text):
        """
        Open ErrorPopup

        """
        ErrorPopup.error_text = text
        ErrorPopup.ErrorPopup().open()


if __name__ == "__main__":
    db.actualize_database()
    Builder.load_file("Views/main.kv")
    MainApp().run()
