from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class TextInputCustomValidate(TextInput):
    def __init__(self, **kwargs):
        super(TextInputCustomValidate, self).__init__(**kwargs)
        self.text_validate_unfocus = False


# TODO why do I need it?
class ButtonListItem(Button):
    id = StringProperty(None)
    text = StringProperty(None)

    def click(button):
        global app
        app.clearSelection()
        button.background_color = (0,160,66,.9)