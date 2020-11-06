from kivy.clock import Clock
from kivy.properties import StringProperty
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

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class TextInputCustomValidate(TextInput):
    def __init__(self, **kwargs):
        super(TextInputCustomValidate, self).__init__(**kwargs)
        self.text_validate_unfocus = False

    def on_touch_down(self, touch):
        super(TextInputCustomValidate, self).on_touch_down(touch)

        # if touch.button == 'right':
        #     self.parent.parent.parent.focus_entries_panel_id()


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







