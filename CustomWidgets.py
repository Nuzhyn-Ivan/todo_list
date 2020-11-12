from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ListProperty, NumericProperty
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.factory import Factory


import main
import utils.ConfigParser as config
from kivy.base import EventLoop
from kivy.config import Config


class TextInputCustomValidate(TextInput):
    def __init__(self, **kwargs):
        super(TextInputCustomValidate, self).__init__(**kwargs)
        self.text_validate_unfocus = False

    def on_touch_down(self, touch):
        super(TextInputCustomValidate, self).on_touch_down(touch)

        # if touch.button == 'right':
        #     self.parent.parent.parent.focus_entries_panel_id()


txt_input = ObjectProperty()
flt_list = ObjectProperty()
word_list = ListProperty()
# this is the variable storing the number to which the look-up will start
starting_no = NumericProperty(3)
suggestion_text = ''


def on_text(self, instance, value):
    # find all the occurrence of the word
    self.parent.ids.rv.data = []
    matches = [self.word_list[i] for i in range(len(self.word_list)) if
               self.word_list[i][:self.starting_no] == value[:self.starting_no]]
    # display the data in the recycleview
    display_data = []
    for i in matches:
        display_data.append({'text': i})
    self.parent.ids.rv.data = display_data
    # ensure the size is okay
    if len(matches) <= 10:
        self.parent.height = (50 + (len(matches) * 20))
    else:
        self.parent.height = 240


def keyboard_on_key_down(self, window, keycode, text, modifiers):
    if self.suggestion_text and keycode[1] == 'tab':
        self.insert_text(self.suggestion_text + ' ')
        return True
    return super(TextInputCustomValidate, self).keyboard_on_key_down(window, keycode, text, modifiers)


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







