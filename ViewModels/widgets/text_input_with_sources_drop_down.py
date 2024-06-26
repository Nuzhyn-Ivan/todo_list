from kivy.properties import ListProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput

from Models.utils.screen_manager import ScreenManager
import main
from Models.utils import database_layer as db
from ViewModels.widgets.button import Button
from Models.utils.config_parser import Config


class TextInputWithSourcesDropDown(TextInput):
    """
    TextInput with DropDown for 'suggestions' feature
    https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    """

    screen_manager: ScreenManager
    config: Config

    suggestions = ListProperty([])

    def __init__(self, **kwargs):
        super(TextInputWithSourcesDropDown, self).__init__(**kwargs)
        self.config = Config()
        self.screen_manager = main.MainApp.get_running_app().root
        self.suggestions = kwargs.pop("suggestions", [])  # list of suggestions
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = "left"
        self.bind(text=self.on_text)
        self.dropdown = None
        self.suggestion_text = " "

    def on_touch_down(self, touch):
        super(TextInputWithSourcesDropDown, self).on_touch_down(touch)
        self.text = ""

    def load_choices(self, entry_name_part, chooser):
        entry_details_screen_instance = self.screen_manager.get_screen(
            self.screen_manager.entry_details_screen
        )
        self.suggestions.clear()
        max_suggestions_count = int(self.config.get("max_suggestions_count"))
        available_suggestions = db.read_sources_by_name_part(
            list_id=entry_details_screen_instance.entry_id,
            name_part=entry_name_part,
            limit=max_suggestions_count,
        )
        self.suggestions.extend(available_suggestions)

        # The first entry has to be next to TextInput - this is the last position in suggestions
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
        """
        Set text of chosen suggestion as a source InputLine text
        """
        self.text = ""
        entry_details_screen_instance = self.screen_manager.get_screen(
            self.screen_manager.entry_details_screen
        )
        entry_details_screen_instance.ids.source_id.text = btn_obj.text
        self.focused = True
        # TODO press enter here
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
