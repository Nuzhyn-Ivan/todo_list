from kivy.properties import StringProperty
from kivy.uix.popup import Popup

from Models.utils.screen_manager import ScreenNames
from Models.utils.config_parser import Config
from Models.utils.screen_manager import ScreenManager
import main
from Models.utils import database_layer as db


class ListEditPopup(Popup):
    configuration: Config = Config()
    list_name = StringProperty()

    def rename_list(self, text):
        if text != self.list_name:
            db.rename_list(list_name=self.list_name, new_list_name=text)

    def delete_list(self):
        list_name = self.ids.list_name_id.text
        list_id = db.get_list_id(list_name=list_name)
        db.delete_list_by_id(list_id)
        self.dismiss()

    @staticmethod
    def refresh_lists():
        screen_manager: ScreenManager = main.MainApp.get_running_app().root
        lists_screen_instance = screen_manager.get_screen(ScreenNames.LISTS)
        lists_screen_instance.refresh_lists()
