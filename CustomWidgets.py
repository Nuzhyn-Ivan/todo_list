from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from utils import gesture_box as gesture
import main
import utils.ConfigParser as config
from kivy.base import EventLoop
from kivy.config import Config

#Config.set('input', 'mouse', 'mouse,disable_multitouch')


class TextInputCustomValidate(TextInput):
    def __init__(self, **kwargs):
        super(TextInputCustomValidate, self).__init__(**kwargs)
        self.text_validate_unfocus = False

    def on_touch_down(self, touch):
        super(TextInputCustomValidate, self).on_touch_down(touch)

        if touch.button == 'right':
            self.parent.parent.parent.focus_entries_panel_id()
            print('sdf')


# TODO why do I need it?
class ButtonListItem(Button):
    id = StringProperty(None)
    text = StringProperty(None)

    def click(button):
        global app
        app.clearSelection()
        button.background_color = (0,160,66,.9)


class Runner(gesture.GestureBox):
    pass




