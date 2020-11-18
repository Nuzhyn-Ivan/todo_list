from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput
from kivy.factory import Factory

import utils.DBLayer as db
import main
# TODO rewrite with https://kivy.org/doc/stable/api-kivy.uix.spinner.html
class CustomDropDown(BoxLayout):
    # settings - background
    pass


# TODO https://www.reddit.com/r/kivy/comments/99n2ct/anyone_having_idea_for_autocomplete_feature_in/
class DropDownWidget(BoxLayout):
    txt_input = ObjectProperty()
    rv = ObjectProperty()


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)


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

    # def keyboard_on_key_down(self, window, keycode, text, modifiers):
    #     if self.suggestion_text and keycode[0] == ord('\r'):  # enter selects current suggestion
    #         self.suggestion_text = ' '  # setting suggestion_text to '' screws everything
    #         self.text = self.values[0]
    #         if self.dropdown:
    #             self.dropdown.dismiss()
    #             self.dropdown = None
    #     else:
    #         super(Chooser, self).keyboard_on_key_down(window, keycode, text, modifiers)

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





