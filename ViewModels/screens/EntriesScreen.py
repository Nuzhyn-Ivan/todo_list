from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from Models.screen_names import ScreenNames
import ViewModels.widgets.Button
from Models.lang import Localization as lang
from Models.utils import DBLayer as db
from Models.utils.config_parser import Config


class EntriesScreen(Screen):
    def __init__(self, **kwargs):
        super(EntriesScreen, self).__init__(**kwargs)
        self.config = Config()
        self.ready_to_revoke_entries = []
        self.current_list_id = ""
        self.current_list_name = ""

    def set_current_list(self, list_id: str):
        self.current_list_id = list_id
        self.current_list_name = db.get_list_name(self.current_list_id)

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """
        Add entry to EntriesScreen
        :param entry_id: ID of entry
        :param entry_name: name of entry
        :param index: index of entry to display on entries screen. Not implemented
        """
        entry_note = Button(
            text=lang.get("open_entry_info"),
            size_hint=(0.2, None),
            height=self.config.get("entries_height"),
            font_size=self.config.get("entries_font_size"),
            on_release=self.open_entry_info_screen,
        )
        entry_note.id = entry_id
        self.ids.entries_panel_id.add_widget(entry_note, index)

        entry = ViewModels.widgets.Button.Button(
            text=entry_name,
            size_hint=(0.6, None),
            height=self.config.get("entries_height"),
            font_size=self.config.get("entries_font_size"),
            on_release=self.complete_entry,
            duration_long_touch=0.4,
        )
        entry.id = entry_id
        self.ids.entries_panel_id.add_widget(entry, index)

    def refresh_entries_screen(self):
        """
        Refresh EntriesScreen
        """
        # TODO remove and refactor label sizing

        # Remove all entries
        for widget in self.ids.entries_panel_id.children:
            widget.clear_widgets()  # remove all child's from Layout
        self.ids.entries_panel_id.clear_widgets()  # remove all layouts from entries_panel

        # Add actual entries
        entries_list = db.read_entries(list_id=self.current_list_id)
        for entry in entries_list:
            self.add_entry(entry_id=entry[0], entry_name=entry[2], index=0)

        # Add actual list name to 'Back' button
        self.ids.current_list_btn.text = f"<--   {self.current_list_name}"
        self.ids.tools_btn_id.text = lang.get("tools_btn")

    def complete_entry(self, btn_obj: Button):
        """
        Remove entry from entries screen and mark as completed in db
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        """
        db.complete_entry(btn_obj.id)
        self.ready_to_revoke_entries.append(btn_obj.text)
        self.ids.entries_panel_id.remove_widget(btn_obj)
        self.ids.revoke_btn_id.disabled = False
        self.refresh_entries_screen()

    def complete_entry_with_details(self, btn_obj: Button):
        """
        Remove entry from entries screen and mark as completed in db with adding details
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        """
        # TODO complete_entry have to be in EntryDetailsScreen.save
        #  Now entry completed even if close app on entry_details_screen without save
        self.complete_entry(btn_obj)

        complete_entry_screen_instance = self.manager.get_screen(self.manager.complete_entry_screen)
        complete_entry_screen_instance.entry_id = btn_obj.id
        self.manager.change_screen(ScreenNames.COMPLETE_ENTRY, "up")

    def create_entry(self, text: str):
        """
        Add entry to database and refresh EntriesScreen

        Args:
            text (str): Entry name
        """

        text = text.strip()
        # TODO add error handling same with add_list
        if text:
            db.create_entry(
                list_id=int(self.current_list_id),
                entry_name=text,
            )
            self.refresh_entries_screen()

    def revoke_entry(self):
        """
        Recover last completed entry and add it back to EntriesScreen
        """
        entry_text = self.ready_to_revoke_entries.pop()
        self.create_entry(entry_text)

        # Disable revoke btn if no entries to revoke
        if not self.ready_to_revoke_entries:
            self.ids.revoke_btn_id.disabled = True

    # TODO add annotation for all btn_obj
    def open_tools_screen(self, btn_obj: Button):
        """
        Open one of the Tools screen - TagsScreen, HistoryScreen

        Args:
            btn_obj (Button): Object of pressed button.
        """

        pressed_button = lang.get_key_by_value(btn_obj.text)
        if pressed_button == "tags_btn":
            self.manager.change_screen(ScreenNames.TAGS, "right")
        elif pressed_button == "history_btn":
            self.manager.change_screen(ScreenNames.HISTORY, "right")
        else:
            # TODO: add exception handling
            pass

    def open_entry_info_screen(self, btn_obj: Button):
        """
        Open EntryInfo screen

        Args:
            btn_obj (Button): Object of pressed button.
        """

        # Init entry_info_screen
        entry_info_screen_instance = self.manager.get_screen(ScreenNames.ENTRY_INFO)
        current_entry_id = btn_obj.id
        entry_info_screen_instance.init_screen(current_entry_id)

        # Change screen to entry_info_screen
        self.manager.change_screen(ScreenNames.ENTRY_INFO, "right")
