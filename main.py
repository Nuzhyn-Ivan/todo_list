from kivy.base import EventLoop
import locale
from kivy.core.audio import SoundLoader
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.dropdown import DropDown
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, CardTransition
from kivy.core.window import Window


from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen


import CustomWidgets
import utils.DBLayer as db
import utils.ConfigParser as config


Window.softinput_mode = 'below_target'
# https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs


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
        self.transition = CardTransition(direction=direction, duration=float(config.get('screen_transition_duration')))
        self.current = screen_name


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
            list_btn = CustomWidgets.MDFlatButtonCustom(
                id=str(i[0]),  # id
                text=str(i[1] + " (" + db.read_entries_count(i[0]) + ")"),  # list name
                long_press_time=2,
                font_size=config.get('lists_font_size'),
                size_hint=(1, None),


            )
            list_btn.bind(on_release=self.open_entry)
            list_btn.bind(on_long_press=self.delete_list)
            lists_panel = self.ids.lists_panel_id
            lists_panel.add_widget(list_btn)

    def open_entry(self, btn_obj):
        EntriesScreen.list_id = btn_obj.id
        EntriesScreen.list_name = db.get_list_name(btn_obj.id)
        self.manager.transition = CardTransition(direction='left', duration=float(config.get('screen_transition_duration')))
        self.manager.current = "entries_screen"

    @staticmethod
    def create_list(text):
        text = text.strip()
        if text:
            db.create_list(text)

    def delete_list(self, btn_obj):
        db.delete_list_by_id(btn_obj.id)
        self.refresh_lists()


class EntriesScreen(MDScreen):
    list_id = StringProperty()
    list_name = StringProperty()
    done_entry_sound = SoundLoader.load(config.get('done_entry_sound'),)

    def add_entry(self, entry_id, text):
        entry = MDFlatButton(
            id=entry_id,
            text=text,
            size_hint=(1, None),
            height="70dp",
            font_size=config.get('entries_font_size'),


        )
        entry.bind(on_release=self.done_entry)
        self.ids.entries_panel_id.add_widget(entry)

    def refresh_entries(self):
        entries_list = db.read_entries(int(self.list_id))
        self.ids.entries_panel_id.clear_widgets()
        for no in range(len(entries_list)):
            self.add_entry(entries_list[no][0], entries_list[no][2])

    def done_entry(self, btn_obj):
        db.complete_entry(btn_obj.id)
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


    def save_settings(self):
        pass


class ErrorPopup(Popup):
    error_text = "some error text"


class MainApp(MDApp):

    def build(self):
        self.theme_cls.theme_style = 'Dark'  # 'Light'
        self.theme_cls.primary_palette = 'Orange'
        # self.theme_cls.theme_style  =
        # TODO move ALL paths to system settings
        self.icon = 'images/icon.png'
        self.title = config.get('app_title') + '   ' + config.get('app_version')
        return CustomWidgets.Runner()


    def build_config(self, app_config):
        app_config.setdefaults('', {
            'font_size': '15dp',
            'entries_font_size': 42,
            'lists_font_size': '15dp',
            'app_version': '0.0.20',
            'app_title': 'TODOit',
            'db_path': "..// TODO.db",
            'screen_transition_duration': 0,
            'done_entry_sound': 'sounds // done_entry.wav',
        },
                               )

    @staticmethod
    def open_error_popup(text):
        ErrorPopup.error_text = text
        ErrorPopup().open()


if __name__ == '__main__':
    config.load_config()
    db.create_db()
    MainApp().run()






