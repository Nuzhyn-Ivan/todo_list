from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder

import ViewModels.popups.ErrorPopup
import Models.lang.Localization as lang
from Models.utils import ConfigParser as config
from Models.utils import DBLayer as db
from Models.utils.ScreenManagement import ScreenManagement


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        """
        Build app
        :param:
        :return:
        """
        # TODO refactor background - handle list type for config.get()
        background_dict = {
            'Orange': [0.8, 0.4, 0.0, 1],
            "White": [1.0, 1.0, 1.0, 1],
            "Black": [0, 0, 0, 1],
        }
        Window.clearcolor = background_dict[config.get_option_value('background_colour')]
        Window.softinput_mode = 'below_target'  # TextInput keyboard position https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs
        # TODO move ALL paths to system settings
        self.icon = 'images/icon.png'
        self.title = F"{config.get_option_value('app_title')}  {config.get_option_value('app_version')}"
        lang.reload_lang()
        config.load_config()

        return ScreenManagement()

    @staticmethod
    def open_error_popup(text):
        """
        Open ErrorPopup
        :param:
        :return:
        """
        ViewModels.popups.ErrorPopup.ErrorPopup.error_text = text
        ViewModels.popups.ErrorPopup.ErrorPopup().open()


if __name__ == '__main__':
    db.actualize_database()
    Builder.load_file('Views/main.kv')
    MainApp().run()
