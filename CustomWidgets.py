from kivy.clock import Clock
from kivy.properties import ListProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.factory import Factory

import utils.DBLayer as db
import main


class ButtonCustom(Button):
    __events__ = ('on_long_press',)
    long_press_time = Factory.NumericProperty(1)

    def on_state(self, instance, value):
        if value == 'down':
            lpt = self.long_press_time
            self._clockev = Clock.schedule_once(self._do_long_press, lpt)
        else:
            self._clockev.cancel()

    def _do_long_press(self, dt):
        self.dispatch('on_long_press')

    def on_long_press(self, *largs):
        pass


class Chooser(TextInput):
    # TODO Finish HIM!!
    # https://stackoverflow.com/questions/59779143/is-there-a-way-to-have-a-textinput-box-that-searches-automatically-searches-a-li
    choiceslist = ListProperty([])

    def __init__(self, **kwargs):
        self.choiceslist = kwargs.pop('choiceslist', [])  # list of choices
        super(Chooser, self).__init__(**kwargs)
        self.text_validate_unfocus = False
        self.multiline = False
        self.halign = 'left'
        #self.bind(choicesfile=self.load_choices)
        self.bind(text=self.on_text)
        #self.load_choices()
        self.dropdown = None

    def on_touch_down(self, touch):
        super(Chooser, self).on_touch_down(touch)

        # if touch.button == 'right':
        #     self.parent.parent.parent.focus_entries_panel_id()
    def open_dropdown(self, *args):
        if self.dropdown:
            self.dropdown.open(self)

    def load_choices(self, entry_name_part):
        self.choiceslist.clear()
        for i in db.read_entries_by_name_part(main.EntriesScreen.current_list_id, entry_name_part):
            self.choiceslist.append(i)

    def on_text(self, chooser, text):
        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None
        if text == '':
            return
        self.load_choices(text)
        # TODO review do I need load_choices def

        if len(self.choiceslist) > 0:
            if len(self.text) < len(self.choiceslist[0]):
                self.suggestion_text = self.choiceslist[0][len(self.text):]
            else:
                self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
            self.dropdown = DropDown()
            for val in self.choiceslist:
                self.dropdown.add_widget(Button(text=str(val[0]), size_hint_y=None, height=48, on_release=self.do_choose))
            self.dropdown.open(self)

    def do_choose(self, butt):
        self.text = butt.text
        # TODO press enter here

        if self.dropdown:
            self.dropdown.dismiss()
            self.dropdown = None


class ErrorPopup(Popup):
    # TODO implement exact error display
    popup_title = 'some popup title'
    error_text = "some error text"


class ListEditPopup(Popup):
    list_name = StringProperty()

    def rename_list(self):
        if self.ids.list_name_id.text != self.list_name:
            db.rename_list(self.list_name, self.ids.list_name_id.text)
