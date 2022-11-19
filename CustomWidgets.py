from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivymd.uix.behaviors import TouchBehavior

import main
import utils.DBLayer as db


class TextInputWithEntriesDropDown(TextInput):
    """
    TextInput with DropDown for 'suggestions' feature
    https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    """

    suggestions = ListProperty([])

    def __init__(self, **kwargs):
        super(TextInputWithEntriesDropDown, self).__init__(**kwargs)
        self.suggestions = kwargs.pop('suggestions', [])  # list of suggestions
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = 'left'
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = ' '

    def on_touch_down(self, touch):
        super(TextInputWithEntriesDropDown, self).on_touch_down(touch)

    def load_choices(self, entry_name_part, chooser):
        self.suggestions.clear()

        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(screen_manager.entries_screen)
        available_suggestions = db.read_entries_by_name_part(list_id=entries_screen_instance.current_list_id,
                                                             name_part=entry_name_part)
        self.suggestions.extend(available_suggestions)

        # The first entry has to be under TextInput - this is the last position in suggestions
        self.suggestions.reverse()

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        self.load_choices(text, chooser)

        if self.suggestions:
            if len(self.text) < len(self.suggestions[0]):
                self.suggestion_text = self.suggestions[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for suggestion in self.suggestions:
                button = Button(text=suggestion[0],
                                size_hint_y=None,
                                height="60dp",
                                on_release=self.do_choose,
                                )
                self.dropdown.add_widget(button)
            self.dropdown.open(self)

    def do_choose(self, btn_obj: Button):
        self.text = ''
        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(screen_manager.entries_screen)
        entries_screen_instance.create_entry(btn_obj.text)
        self.focused = True
        # TODO press enter here
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None


class TextInputWithSourcesDropDown(TextInput):
    """
    TextInput with DropDown for 'suggestions' feature
    https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    """

    suggestions = ListProperty([])

    def __init__(self, **kwargs):
        super(TextInputWithSourcesDropDown, self).__init__(**kwargs)
        self.suggestions = kwargs.pop('suggestions', [])  # list of suggestions
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = 'left'
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = ' '

    def on_touch_down(self, touch):
        super(TextInputWithSourcesDropDown, self).on_touch_down(touch)
        self.text = ''

    def load_choices(self, entry_name_part, chooser):
        screen_manager = main.MainApp.get_running_app().root
        entry_details_screen_instance = screen_manager.get_screen(screen_manager.entry_details_screen)
        self.suggestions.clear()
        available_suggestions = db.read_sources_by_name_part(entry_details_screen_instance.entry_id, entry_name_part,)
        self.suggestions.extend(available_suggestions)

        # The first entry has to be next to TextInput - this is the last position in suggestions
        self.suggestions.reverse()

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        self.load_choices(text, chooser)

        if self.suggestions:
            if len(self.text) < len(self.suggestions[0]):
                self.suggestion_text = self.suggestions[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything

            self.dropdown = DropDown()
            for suggestion in self.suggestions:
                button = Button(text=suggestion[0],
                                size_hint_y=None,
                                height="60dp",
                                on_release=self.do_choose,
                                )
                self.dropdown.add_widget(button)
            self.dropdown.open(self)

    def do_choose(self, btn_obj: Button):
        """
        Set text of chosen suggestion as a source InputLine text
        """
        self.text = ''
        screen_manager = main.MainApp.get_running_app().root
        entry_details_screen_instance = screen_manager.get_screen(screen_manager.entry_details_screen)
        entry_details_screen_instance.ids.source_id.text = btn_obj.text
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
        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(screen_manager.entries_screen)
        entries_screen_instance.complete_entry_with_details(self)

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
            db.rename_list(list_name=self.list_name, new_list_name=text)

    def delete_list(self):
        list_name = self.ids.list_name_id.text
        list_id = db.get_list_id(list_name=list_name)
        db.delete_list_by_id(list_id)
        self.dismiss()

    @staticmethod
    def refresh_lists():
        screen_manager = main.MainApp.get_running_app().root
        lists_screen_instance = screen_manager.get_screen(screen_manager.lists_screen)
        lists_screen_instance.refresh_lists()


class EntriesNotesPopup(Popup):
    entry_id = NumericProperty()
    note_text = ''
    popup_title = ''

    def init_popup(self):
        pass

    def save_note(self):
        self.dismiss()
