from kivy.properties import NumericProperty
from kivy.uix.popup import Popup


class EntriesNotesPopup(Popup):
    entry_id = NumericProperty()
    note_text = ''
    popup_title = ''

    def init_popup(self):
        pass

    def save_note(self):
        self.dismiss()
