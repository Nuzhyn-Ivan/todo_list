from enum import Enum
from kivy.core.window import Window
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.screenmanager import ScreenManager, CardTransition

from Models.utils import ConfigParser as config


# TODO add type of param and return for all methods
class ScreenManagement(ScreenManager):
    """
    Class to handle screens transition in app and access to all instances of screens
    """
    lists_screen = 'lists_screen'
    entries_screen = 'entries_screen'
    complete_entry_screen = 'complete_entry_screen'
    entry_info_screen = 'entry_info_screen'
    settings_screen = 'settings_screen'
    history_screen = 'history_screen'
    tags_screen = 'tags_screen'

    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        """
        Handle 'key pressed' events
        Full list of key codes:
        https://gist.github.com/Enteleform/a2e4daf9c302518bf31fcc2b35da4661
        """
        back_key = 27  # the 'ESC' key on win or 'Back' key on phone

        if key == back_key:
            match self.current_screen.name:
                case self.lists_screen:
                    return False  # exit the app from this page
                case self.settings_screen:
                    self.change_screen(self.lists_screen, 'right')
                    return True  # do not exit the app
                case self.entries_screen:
                    self.change_screen(self.lists_screen, 'right')
                    return True  # do not exit the app

    # todo add keyword arguments for all usages
    def change_screen(self, screen_name: str, transition_direction: str):
        """
        Change app screen.
        Screen title its 'name' param from kv screen file. Screens list can be found in self.screen_title.

        :param screen_name: title of screen to open.
        :param transition_direction: Direction of screen change(left, right, up, down)
        :return:
        """
        self.transition = CardTransition(direction=transition_direction,
                                         duration=float(config.get_option_value('screen_transition_duration')))
        self.current = screen_name

    def _update_screens(self, new_screens):
        """
        Remove and re-adds screens to match the new configuration
        """
        # Prevent events from triggering and interfering with this update process
        self._initialized = False
        carousel = self.ids.carousel
        current_screens = self._screens
        loaded_screens = self._loaded_screens

        new_screen_count = len(new_screens)
        current_screen_count = len(current_screens)
        original_screen_count = current_screen_count

        # Note, our lazy loading scheme has the actual dashboard
        # screens as part of the outer screen containers - placeholders.

        # clear all the dashboard screens from the outer container
        for screen in loaded_screens.values():
            if screen.parent:
                screen.parent.remove_widget(screen)

        # add more carousel panes as needed
        while True:
            if current_screen_count == new_screen_count:
                break
            if current_screen_count < new_screen_count:
                carousel.add_widget(AnchorLayout())
                current_screen_count += 1
            if current_screen_count > new_screen_count:
                carousel.remove_widget(carousel.slides[0])
                current_screen_count -= 1

        # Now re-add the screens for the new screen keys
        for (screen_key, container) in zip(new_screens, carousel.slides):
            screen = loaded_screens.get(screen_key)
            if screen:
                container.add_widget(screen)

        self._screens = new_screens

        if original_screen_count == 0 and new_screen_count > original_screen_count:
            carousel.index = 0

        self._check_load_screen(carousel.current_slide)
        self._initialized = True

    def refresh_screens(self):
        pass
        # TODO remove all and add again
