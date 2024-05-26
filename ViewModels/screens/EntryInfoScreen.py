from kivy.uix.screenmanager import Screen

from Models.utils import DBLayer as db
from Models.utils.config_parser import Config


class EntryInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(EntryInfoScreen, self).__init__(**kwargs)
        self.config = Config()
        self.note_text = str
        self.current_entry_id = None

    def init_screen(self, current_entry_id):
        """
        Initiate EntryNotesScreen

        """
        self.current_entry_id = current_entry_id
        self.note_text = db.get_entry_note(current_entry_id)
        self.ids.note_id.text = self.note_text

    def save_note(self):
        """
        Save note to database

        """
        self.manager.change_screen(self.manager.entries_screen, "left")
        db.set_entry_note(self.entry_id, self.ids.note_id.text)
        self.ids.note_id.text = ""

    def back(self):
        """
        Change screen to EntriesScreen

        """
        self.manager.change_screen(self.manager.entries_screen, "left")
