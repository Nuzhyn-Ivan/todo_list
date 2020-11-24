from kivy.app import App
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, CardTransition, Screen
from kivy.core.window import Window

import CustomWidgets
import utils.DBLayer as db
import lang.Localization as lang
import utils.ConfigParser as config


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


class ListsScreen(Screen):
    def __init__(self,  **kw):
        super().__init__(**kw)
        Clock.schedule_once(self._do_setup)
        self.edit_mode = False

    def _do_setup(self, *l):
        """
        Initial build on lists screen
        """
        self.refresh_lists()

    def add_list(self, list_id, list_name):
        list_btn = CustomWidgets.ButtonCustom(
            id=str(list_id),
            long_press_time=1,
            font_size=config.get('lists_font_size'),
            size_hint=(1, None),
            on_long_press=self.delete_list,
        )
        if self.edit_mode:
            list_btn.bind(on_release=self.open_edit_popup)
            list_btn.text = str(list_name + '  - Tap to edit')
        else:
            list_btn.bind(on_release=self.open_list)
            list_btn.text = str(list_name + " (" + db.read_entries_count(list_id) + ")")
        self.ids.lists_panel_id.add_widget(list_btn)

    def refresh_lists(self, *l):
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for i in lists:
            self.add_list(i[0], i[1])

    def open_list(self, btn_obj):
        EntriesScreen.current_list_id = btn_obj.id
        # TODO add entries counter to back button on EntriesScreen
        EntriesScreen.current_list_name = db.get_list_name(btn_obj.id)
        self.manager.transition = CardTransition(direction='left', duration=float(config.get('screen_transition_duration')))
        self.manager.current = "entries_screen"

    def create_list(self, text):
        text = text.strip()
        if text:
            result = db.create_list(text)
            if not result:
                MainApp.open_error_popup('Database error')
        last_list = db.read_last_list()[0]
        self.add_list(last_list[0], last_list[1])

    def delete_list(self, btn_obj):
        db.delete_list_by_id(btn_obj.id)
        self.ids.lists_panel_id.remove_widget(btn_obj)

    # TODO complete edit lists feature
    def change_edit_mode(self):
        self.edit_mode = not self.edit_mode  # change to opposite
        if not self.edit_mode:
            self.ids.lists_edit_btn.text = lang.get('edit_btn')
        else:
            self.ids.lists_edit_btn.text = lang.get('apply_edit_btn')
            #  Clock.schedule_interval(self.refresh_lists, 0.5)
        self.refresh_lists()

    @staticmethod
    def open_edit_popup(btn_obj):
        # TODO fix bug - Lists screen not refreshed after close pop-up
        list_edit_popup = CustomWidgets.ListEditPopup(
            title=btn_obj.text.replace('  - Tap to edit', ''),
        )
        list_edit_popup.list_name = btn_obj.text.replace('  - Tap to edit', '')
        list_edit_popup.open()


class EntriesScreen(Screen):
    def __init__(self,  **kw):
        super().__init__(**kw)
        self.ready_to_revoke_entries = []

    current_list_id = StringProperty()
    current_list_name = StringProperty()

    def add_entry(self, entry_id, text, index):
        entry = CustomWidgets.ButtonCustom(
            id=str(entry_id),
            text=str(text),
            size_hint=(1, None),
            height="70dp",
            font_size=config.get('entries_font_size'),
        )
        entry.bind(on_release=self.complete_entry)
        self.ids.entries_panel_id.add_widget(entry, index)

    def refresh_entries(self):
        entries_list = db.read_entries(self.current_list_id)
        self.ids.entries_panel_id.clear_widgets()
        for entry_num in range(len(entries_list)):
            self.add_entry(entries_list[entry_num][0], entries_list[entry_num][2], 0)

    def complete_entry(self, btn_obj):
        db.complete_entry(btn_obj.id)
        self.ready_to_revoke_entries.append(btn_obj.text)
        self.ids.entries_panel_id.remove_widget(btn_obj)
        self.ids.revoke_btn_id.disabled = False

    # def focus_entries_panel_id(self):
    #     self.ids.entries_panel_id.focus = True

    def create_entry(self, text):
        text = text.strip()
        if text:
            db.create_entry(self.current_list_id, text)
            last_entry = db.read_last_entry(self.current_list_id)[0]
            self.add_entry(last_entry[0], last_entry[1], 0)

    def revoke_entry(self):
        self.create_entry(self.ready_to_revoke_entries.pop())
        if len(self.ready_to_revoke_entries) == 0:
            self.ids.revoke_btn_id.disabled = True


class SettingsScreen(Screen):
    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    current_settings = {
        'background_colour': config.get('background_colour'),
        'lang': config.get('lang'),
        'entries_font_size': config.get('entries_font_size'),
        'lists_font_size': config.get('lists_font_size'),
        'max_suggestions_count': config.get('max_suggestions_count'),
        'font_size': config.get('font_size'),
        'padding': config.get('padding'),
        'spacing': config.get('spacing'),
    }

    def get_current_settings(self):
        for key in self.current_settings:
            self.current_settings[key] = config.get(key)

    @staticmethod
    def reset_db():
        db.recreate_database()

    def apply_settings(self):
        for key in self.current_settings:
            config.set(key, self.current_settings[key])
        # TODO lang reload doesnt work
        # lang.reload_lang()
        # config.load_config()
        MainApp.build(self)


class MainApp(App):

    def build(self):
        # TODO refactor backgroung - handle list type for config.get()
        backgroung_dict = {'Orange': [0.8, 0.4, 0.0, 1], "White": [1.0, 1.0, 1.0, 1]}
        Window.clearcolor = backgroung_dict[config.get('background_colour')]
        Window.softinput_mode = 'below_target'  # TextInput keyboard position https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs
        # TODO move ALL paths to system settings
        self.icon = 'images/icon.png'
        self.title = config.get('app_title') + '   ' + config.get('app_version')
        return ScreenManagement()

    def build_config(self, app_config):
        app_config.setdefaults('', {
            #'font_size': '15dp',
            #'entries_font_size': 42,
            #'lists_font_size': '15dp',
            'app_version': '0.0.20',
            'app_title': 'TODOit',
            'db_path': "..// TODO.db",
            'screen_transition_duration': 0,
        },
                               )

    @staticmethod
    def open_error_popup(text):
        CustomWidgets.ErrorPopup.error_text = text
        CustomWidgets.ErrorPopup().open()


if __name__ == '__main__':
    config.load_config()
    db.create_db()
    MainApp().run()






