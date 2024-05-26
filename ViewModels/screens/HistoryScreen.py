from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from Models.screen_names import ScreenNames
from Models.utils import DBLayer as db
from Models.utils.ScreenManagement import ScreenManagement
from Models.utils.config_parser import  Config


class HistoryScreen(Screen):
    manager: ScreenManagement
    
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.config = Config()
        self.entries_list = []
        self.entries_list_to_delete = []
        self.sorting_type = self.config.get('history_sorting')

    def init_screen(self):
        self.refresh_history_screen()

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """        
        Add entry to HistoryScreen and database

        Args:
            entry_id (str): ID of entry
            entry_name (str): name of entry
            index (int, optional): index of entry to display on entries screen. Not implemented. Defaults to 0.
        """

        entry = Button(
            text=entry_name,
            size_hint=(1, None),
            height="70dp",
            font_size=self.config.get('entries_font_size'),
            on_release=self.tag_entry_to_delete,
        )
        entry.id = entry_id
        self.ids.history_panel_id.add_widget(entry, index)

    def refresh_history_screen(self):
        """
        Refresh History Screen
        """
        entries_screen_instance = self.manager.get_screen(ScreenNames.ENTRIES)

        # Remove all
        self.ids.history_panel_id.clear_widgets()

        # Add actual list name to 'Back' button
        self.ids.back_btn.text = F"<--   {entries_screen_instance.current_list_name}"

        # Add properly sorted entries
        self.entries_list = db.read_entries(list_id=entries_screen_instance.current_list_id, completed=True)
        self.apply_entries_sorting(self.sorting_type)
        # for entry_num in range(len(self.entries_list)):
        #     self.add_entry(
        #         self.entries_list[entry_num][0],  # entry_id
        #         self.entries_list[entry_num][2],  # entry_name
        #         0,  # index
        #     )
        for entry in self.entries_list:
            self.add_entry(
                entry_id=entry[0],
                entry_name=entry[2],
                index=0,
            )

    def apply_entries_sorting(self, sorting_type: str):
        """
        Apply chosen sort type
        """
        match sorting_type:
            case 'az_sorting':
                self.entries_list.sort(key=lambda x: x[2])
            case 'za_sorting':
                self.entries_list.sort(key=lambda x: x[2], reverse=True)
            case 'min_max_usage_sorting':
                self.entries_list.sort(key=lambda x: x[7])
            case 'max_min_usage_sorting':
                self.entries_list.sort(key=lambda x: x[7], reverse=True)

    def tag_entry_to_delete(self, btn_obj: Button):
        """
        Delete entry from UI
        Put to self.entries_list_to_delete
        Enable Revoke btn

        Args:
            btn_obj (Button): Button object.
        """

        self.ids.history_panel_id.remove_widget(btn_obj)
        self.entries_list_to_delete.append(btn_obj.id)
        self.ids.revoke_btn_id.disabled = False

    def apply_delete_entry(self):
        """
        Delete entry from HistoryScreen
        """
        for entry in self.entries_list_to_delete:
            db.delete_entry(entry)
        self.entries_list_to_delete.clear()
        self.ids.revoke_btn_id.disabled = True

    def revoke_entry(self):
        """
        Recover last completed entry and add it back to HistoryScreen
        """
        last_entry = self.entries_list_to_delete.pop(-1)

        # Disable 'revoke' button if no entries left to revoke
        if len(self.entries_list_to_delete) == 0:
            self.ids.revoke_btn_id.disabled = True

        # Add entry
        # TODO fix bug - crash if revoke last element
        self.add_entry(
            entry_id=last_entry[0],
            entry_name=last_entry[1],
            index=0,
        )
