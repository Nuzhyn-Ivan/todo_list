from kivy.uix.button import Button
from kivymd.uix.behaviors import TouchBehavior

import main


class Button(Button, TouchBehavior):
    """
    Button with long press(long touch) implementation using KiviMD TouchBehavior, see more:
    https://kivymd.readthedocs.io/en/latest/behaviors/touch/
    """

    def on_long_touch(self, *args):
        screen_manager = main.MainApp.get_running_app().root
        entries_screen_instance = screen_manager.get_screen(
            screen_manager.entries_screen
        )
        entries_screen_instance.complete_entry_with_details(self)

    def on_double_tap(self, *args):
        pass

    def on_triple_tap(self, *args):
        pass
