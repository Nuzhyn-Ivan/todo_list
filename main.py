import os
import shutil

from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, CardTransition
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from utils import gesture_box as gesture
import utils.DBLayer as db
import utils.ConfigParser as config


Window.softinput_mode = 'below_target'
# https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs


class TextInputCustomValidate(TextInput):
    def __init__(self, **kwargs):
        super(TextInputCustomValidate, self).__init__(**kwargs)
        self.text_validate_unfocus = False


class ButtonListItem(Button):
    id = StringProperty(None)
    text = StringProperty(None)

    def click(button):
        global app
        app.clearSelection()
        button.background_color = (0,160,66,.9)


class ListsScreen(MDScreen):
    def __init__(self,  **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._do_setup)

    def _do_setup(self, *l):
        self.refresh_lists()

    @staticmethod
    def read_entries_count(list_id):
        return db.read_entries_count(list_id)

    def refresh_lists(self):
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for i in lists:
            list_btn = ButtonListItem(
                id=str(i[0]),  # id
                text=str(i[1] + " (" + db.read_entries_count(i[0]) + ")"),  # list name
                size_hint=(1, None),
                height="70dp",
                font_size=config.get('UI', 'lists_font_size'),
            )
            list_btn.bind(on_press=self.open_entry)
            lists_panel = self.ids.lists_panel_id
            lists_panel.add_widget(list_btn)

    def open_entry(self, btn_obj):
        EntriesScreen.list_id = btn_obj.id
        EntriesScreen.list_name = db.get_list_name(btn_obj.id)
        self.manager.transition = CardTransition(direction='left', duration=float(config.get('System', 'screen_transition_duration')))
        self.manager.current = "entries_screen"

    @staticmethod
    def create_list(text):
        text = text.strip()
        if text:
            db.create_list(text)


class EntriesScreen(MDScreen):
    list_id = StringProperty()
    list_name = StringProperty()
    done_entry_sound = SoundLoader.load(config.get('System', 'done_entry_sound'),)

    def add_entry(self, entry_id, text):
        entry = ButtonListItem(
            id=entry_id,
            text=text,
            size_hint_y=None,
            height="70dp",
            font_size=config.get('UI', 'entries_font_size'),
        )
        entry.bind(on_release=self.done_entry)
        entry_panel = self.ids.entries_panel_id
        entry_panel.add_widget(entry)

    def refresh_entries(self):
        entries_list = db.read_entries(int(self.list_id))
        self.ids.entries_panel_id.clear_widgets()
        for no in range(len(entries_list)):
            self.add_entry(entries_list[no][2], entries_list[no][2])  # TODO - generate id correctly

    def done_entry(self, btn_obj):
        db.complete_entry(btn_obj.text)  # TODO entrie id
        self.ids.entries_panel_id.remove_widget(btn_obj)
        self.done_entry_sound.play()

    def focus_entries_panel_id(self):
        self.ids.entries_panel_id.focus = True

    def create_entry(self, text):
        text = text.strip()
        if text:
            self.add_entry(text, text)
            db.create_entry(self.list_id, text)


class SettingsScreen(MDScreen):

    @staticmethod
    def reset_db():
        db.recreate_database()

    @staticmethod
    def delete_list_by_name(text):
        db.delete_list_by_name(text)

    def save_settings(self):
        pass


class Runner(gesture.GestureBox):
    pass


class ScreenManagement(ScreenManager):

    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key or 'Back' key on phone
            if self.current_screen.name == "lists_screen":
                return False  # exit the app from this page
            elif self.current_screen.name == "settings_screen":
                self.change_screen("lists_screen", 'right')
                return True  # do not exit the app
            elif self.current_screen.name == "entries_screen":
                self.change_screen("lists_screen", 'right')
                return True  # do not exit the app

    def change_screen(self, screen_name, direction):
        self.transition = CardTransition(direction=direction, duration=float(config.get('System', 'screen_transition_duration')))
        self.current = screen_name


class ErrorPopup(Popup):
    error_text = 'some error text'
    pass


class MainApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = 'Light'
        # self.theme_cls.theme_style = 'Dark'
        self.icon = 'images/icon.png'
        self.title = config.get('System', 'app_title') + '   ' + config.get('System', 'app_version')
        return Runner()

    def build_config(self, config):
        config.setdefaults('UI', {
            'font_size': '30dp',
            'entries_font_size': 42,
            'lists_font_size': '30dp',
            'background_colour': 'CC6600',
        },
)
        # TODO - this is stupid to write whole file on every change. Replace to edit file
        if not os.path.exists('../TODO_config.ini'):  # first install or config was removed
            shutil.copyfile('main.ini', '../TODO_config.ini')
        else:
            shutil.copyfile('../TODO_config.ini', 'main.ini')  # load existing config

    def on_config_change(self, config, section, key, value):
        shutil.copyfile('main.ini', '../TODO_config.ini')

    @staticmethod
    def open_error_popup(text):
        ErrorPopup.error_text = text
        ErrorPopup().open()


if __name__ == '__main__':
    db.create_db()
    MainApp().run()



