from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

import main
from Models.utils import ConfigParser as config
from Models.utils import DBLayer as db
from ViewModels.widgets.Button import Button


class TextInputWithEntriesDropDown(TextInput):
    """
    TextInput with DropDown for 'suggestions' feature
    https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    """

    suggestions = ListProperty([])

    def __init__(self, **kwargs):
        super(TextInputWithEntriesDropDown, self).__init__(**kwargs)
        self.suggestions = kwargs.pop("suggestions", [])  # list of suggestions
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = "left"
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = " "

    def on_touch_down(self, touch):
        super(TextInputWithEntriesDropDown, self).on_touch_down(touch)

    def load_choices(self, entry_name_part, chooser):
        self.suggestions.clear()

        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(screen_manager.entries_screen)
        max_suggestions_count = int(config.get_option_value("max_suggestions_count"))
        available_suggestions = db.read_entries_by_name_part(
            list_id=entries_screen_instance.current_list_id,
            name_part=entry_name_part,
            limit=max_suggestions_count,
        )
        self.suggestions.extend(available_suggestions)

        # The first entry has to be under TextInput - this is the last position in suggestions
        self.suggestions.reverse()

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == "":
            return
        self.load_choices(text, chooser)

        if self.suggestions:
            if len(self.text) < len(self.suggestions[0]):
                self.suggestion_text = self.suggestions[0][len(self.text) :]
            else:
                self.suggestion_text = " "  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for suggestion in self.suggestions:
                button = Button(
                    text=suggestion[0],
                    size_hint_y=None,
                    height="60dp",
                    on_release=self.do_choose,
                )
                self.dropdown.add_widget(button)
            self.dropdown.open(self)

    def do_choose(self, btn_obj: Button):
        self.text = ""
        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(screen_manager.entries_screen)
        entries_screen_instance.create_entry(btn_obj.text)
        self.focused = True
        # TODO press enter here
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
