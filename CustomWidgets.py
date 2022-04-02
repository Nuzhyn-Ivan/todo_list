from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from kivymd.uix.behaviors import TouchBehavior

import main
import utils.DBLayer as db


class TextInputWithDropDown(TextInput):
    """
    TextInput with DropDown for 'suggestions' feature
    https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    """

    suggestions = ListProperty([])

    def __init__(self, **kwargs):
        super(TextInputWithDropDown, self).__init__(**kwargs)
        self.suggestions = kwargs.pop('suggestions', [])  # list of suggestions
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = 'left'
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = ' '

    def on_touch_down(self, touch):
        super(TextInputWithDropDown, self).on_touch_down(touch)

    def load_choices(self, entry_name_part, chooser):
        entries_screen_instance = main.MainApp.get_running_app().root.get_screen('entries_screen')
        self.suggestions.clear()
        for i in db.read_entries_by_name_part(int(entries_screen_instance.current_list_id), entry_name_part):
            self.suggestions.append(i)
        # the first entry has to be under TextInput - this is the last position in suggestions
        self.suggestions.reverse()

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        self.load_choices(text, chooser)

        if len(self.suggestions) > 0:
            if len(self.text) < len(self.suggestions[0]):
                self.suggestion_text = self.suggestions[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for val in self.suggestions:
                self.dropdown.add_widget(
                    Button(text=str(val[0]), size_hint_y=None, height="60dp", on_release=self.do_choose))
            self.dropdown.open(self)

    def do_choose(self, btn_obj):
        self.text = ''
        self.parent.parent.parent.create_entry(btn_obj.text)
        self.focused = True
        # TODO press enter here
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None


class Button(Button, TouchBehavior):
    """
    Button with long press(long touch) implementation using KiviMD TouchBehavior, see more:
    https://kivymd.readthedocs.io/en/latest/behaviors/touch/
    """

    def on_long_touch(self, *args):
        entries_screen_instance = main.MainApp.get_running_app().root.get_screen('entries_screen')
        entries_screen_instance.complete_entry_with_details(self,)

    def on_double_tap(self, *args):
        pass

    def on_triple_tap(self, *args):
        pass


class ErrorPopup(Popup):
    # TODO implement exact error display
    popup_title = ''
    error_text = "some error text"


class ListEditPopup(Popup):
    list_name = StringProperty()

    def rename_list(self, text):
        if text != self.list_name:
            db.rename_list(self.list_name, text)

    def delete_list(self):
        list_name = self.ids.list_name_id.text
        list_id = db.get_list_id(list_name)
        db.delete_list_by_id(list_id)
        self.dismiss()


class EntriesNotesPopup(Popup):
    entry_id = NumericProperty()
    note_text = ''
    popup_title = ''

    def init_popup(self):
        pass

    def save_note(self):
        self.dismiss()
