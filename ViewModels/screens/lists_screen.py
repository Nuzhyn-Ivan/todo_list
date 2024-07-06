from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from Models.utils.screen_manager import ScreenNames
from Models.utils.screen_manager import ScreenManager
from ViewModels.popups.list_edit_popup import ListEditPopup
from Models.lang import localization as lang
from Models.utils import database_layer as db
from ViewModels.screens.entries_screen import EntriesScreen
from main import MainApp
from Models.utils.config_parser import Config


class ListsScreen(Screen):
    manager: ScreenManager
    configuration: Config
    is_edit_mode: bool

    def __init__(self, **kwargs):
        super(ListsScreen, self).__init__(**kwargs)
        self.configuration = Config()
        self.is_edit_mode = False
        Clock.schedule_once(self.init_screen, 0.5)  # Add lists to Lists screen on app start

    def init_screen(self, *delta_time: float):
        self.refresh_lists()

    def add_list(self, list_id: str, list_name: str, index: int):
        """
        Add List on Lists screen.

        Args:
            list_id (str): List ID
            list_name (str): List name
            index (int): Index of exact list on Lists screen.
        """

        list_btn = Button(
            font_size=self.configuration.get("lists_font_size"),
            size_hint=(1, None),
            height="70dp",
        )
        list_btn.id = list_id
        list_btn.name = list_name
        list_btn.entries_count = db.read_entries_count(list_id)

        # TODO move out is_edit_mode . One responsibility for one object
        if self.is_edit_mode:
            list_btn.bind(on_release=self.open_edit_popup)
            list_btn.text = f"{list_btn.name}{lang.get('tap_to_edit')}"
        else:
            list_btn.bind(on_release=self.open_list)
            list_btn.text = f"{list_btn.name} ({list_btn.entries_count})"
        self.ids.lists_panel_id.add_widget(list_btn, index)

    def refresh_lists(self):
        """
        Remove all lists from Lists screen and add them again from database.
        """
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for list_id, list_name, _, _ in lists:
            self.add_list(
                list_id=list_id,
                list_name=list_name,
                index=0,
            )

    def open_list(self, btn_obj: Button):
        """
        Change screen to 'Entries', add entries of exact list

        Args:
            btn_obj (Button): Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        """

        # Set pressed list_id  to entries_screen
        list_id = btn_obj.id
        entries_screen_instance: EntriesScreen = self.manager.get_screen(ScreenNames.ENTRIES)
        entries_screen_instance.set_current_list(list_id)

        # Open entries_screen
        self.manager.change_screen(ScreenNames.ENTRIES, "left")

    def create_list(self, list_name: str):
        """
        Add list_name to database and Lists screen

        Args:
            list_name (str): Name of list to create
        """

        # TODO - implement lists order display
        # TODO - handle duplicates
        order_id_of_list = 1
        list_name = list_name.strip()
        if list_name:
            db.create_list(list_name, order_id_of_list)
            list_id, list_name = db.read_last_list()
            # TODO add keyword arguments
            self.add_list(
                list_id=list_id,
                list_name=list_name,
                index=0,
            )
        else:
            MainApp.open_error_popup(lang.get("list_name_empty"))

        # TODO - handle all errors
        #     MainApp.open_error_popup(error.args[0])

    def delete_list(self, btn_obj: Button):
        """
        Delete list from database and Lists screen

        Args:
            btn_obj (Button): Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        """

        db.delete_list_by_id(btn_obj.id)
        self.ids.lists_panel_id.remove_widget(btn_obj)

    def change_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.ids.lists_edit_btn.text = lang.get("apply_edit_btn")
        else:
            self.ids.lists_edit_btn.text = lang.get("edit_btn")
        self.refresh_lists()

    @staticmethod
    def open_edit_popup(btn_obj: Button):
        """
        Open ListEditPopup

        Args:
            btn_obj (Button): Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        """

        list_edit_popup = ListEditPopup(
            title=btn_obj.text.replace(lang.get("tap_to_edit"), ""),
            title_align="center",
        )

        list_edit_popup.list_name = btn_obj.text.replace(lang.get("tap_to_edit"), "")
        list_edit_popup.open()
