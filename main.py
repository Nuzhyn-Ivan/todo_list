from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, DictProperty, ListProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, CardTransition, Screen

import CustomWidgets
import lang.Localization as lang
import utils.ConfigParser as config
import utils.DBLayer as db


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
        # screens as part of the outer screen containers
        # screen containers - placeholders.

        # clear all of the dashboard screens from the outer container
        for screen in loaded_screens.values():
            parent = screen.parent
            if parent is not None:
                parent.remove_widget(screen)

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
            if screen is not None:
                container.add_widget(screen)

        self._screens = new_screens

        if original_screen_count == 0 and new_screen_count > original_screen_count:
            carousel.index = 0

        self._check_load_screen(carousel.current_slide)

        self._initialized = True


class ListsScreen(Screen):
    def __init__(self, **kwargs):
        super(ListsScreen, self).__init__(**kwargs)
        self.edit_mode = False
        Clock.schedule_once(self.refresh_lists, 0.5)

    def add_list(self, list_id, list_name, index):
        list_btn = Button(
            id=str(list_id),
            font_size=config.get('lists_font_size'),
            size_hint=(1, None),
            height="70dp",
        )
        if self.edit_mode:
            list_btn.bind(on_release=self.open_edit_popup)
            list_btn.text = F"{list_name} - Tap to edit"
        else:
            list_btn.bind(on_release=self.open_list)
            list_btn.text = F"{list_name} ({db.read_entries_count(list_id)})"
        self.ids.lists_panel_id.add_widget(list_btn, index)

    def refresh_lists(self, *l):
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for i in lists:
            self.add_list(
                i[0],   # list id
                i[1],   # list name
                0,      # index
            )

    def open_list(self, btn_obj):
        EntriesScreen.current_list_id = btn_obj.id
        # TODO add entries counter to back button on EntriesScreen
        EntriesScreen.current_list_name = db.get_list_name(btn_obj.id)
        self.manager.transition = CardTransition(direction='left',
                                                 duration=float(config.get('screen_transition_duration'))
                                                 )
        self.manager.current = "entries_screen"

    def create_list(self, text):
        order_id_of_list = 1  # TODO - fix lists order display
        text = text.strip()
        if text:
            result = db.create_list(text, order_id_of_list)
            if not result:
                MainApp.open_error_popup('Database error')
        last_list = db.read_last_list()[0]
        self.add_list(
            last_list[0],    # list id
            last_list[1],    # list name
            0,               # index
        )

    def delete_list(self, btn_obj):
        db.delete_list_by_id(btn_obj.id)
        self.ids.lists_panel_id.remove_widget(btn_obj)

    def change_edit_mode(self):
        self.edit_mode = not self.edit_mode  # change to opposite
        refresh_lists_timer = Clock.schedule_interval(self.refresh_lists, 0.5)
        if not self.edit_mode:
            self.ids.lists_edit_btn.text = lang.get('edit_btn')
            refresh_lists_timer.cancel()
        else:
            self.ids.lists_edit_btn.text = lang.get('apply_edit_btn')
        refresh_lists_timer()

    @staticmethod
    def open_edit_popup(btn_obj):
        list_edit_popup = CustomWidgets.ListEditPopup(
            title=btn_obj.text.replace('  - Tap to edit', ''),
        )
        list_edit_popup.list_name = btn_obj.text.replace('  - Tap to edit', '')
        list_edit_popup.open()


class EntriesScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.ready_to_revoke_entries = []

    current_list_id = StringProperty()
    current_list_name = StringProperty()

    def add_entry(self, entry_id, entry_name, index):
        entry = Button(
            id=str(entry_id),
            text=str(entry_name),
            size_hint=(1, None),
            height="70dp",
            font_size=config.get('entries_font_size'),
            on_release=self.complete_entry,
        )
        self.ids.entries_panel_id.add_widget(entry, index)

    def refresh_entries(self):
        entries_list = db.read_entries(self.current_list_id)
        self.ids.entries_panel_id.clear_widgets()
        for entry_num in range(len(entries_list)):
            self.add_entry(
                entries_list[entry_num][0],    # entry_id
                entries_list[entry_num][2],    # entry_name
                0,                             # index
            )

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
            self.add_entry(
                last_entry[0],  # entry_id
                last_entry[1],  # entry_name
                0                # index
            )

    def revoke_entry(self):
        self.create_entry(self.ready_to_revoke_entries.pop())
        if len(self.ready_to_revoke_entries) == 0:
            self.ids.revoke_btn_id.disabled = True

    def open_tools_screen(self, btn_obj):
        pressed_button = lang.get_key_by_value(btn_obj.text)
        if pressed_button == 'tags_btn':
            self.manager.change_screen('tags_screen', "right")
        elif pressed_button == 'history_btn':
            self.manager.change_screen('history_screen', "right")


class SettingsScreen(Screen):
    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang

    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    current_settings = DictProperty({
        'background_colour': config.get('background_colour'),
        'lang': config.get('lang'),
        'entries_font_size': config.get('entries_font_size'),
        'lists_font_size': config.get('lists_font_size'),
        'max_suggestions_count': config.get('max_suggestions_count'),
        'font_size': config.get('font_size'),
        'padding': config.get('padding'),
        'spacing': config.get('spacing'),
    })

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


class TagsScreen(Screen):
    pass


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.current_list_id = EntriesScreen.current_list_id
        self.current_list_name = EntriesScreen.current_list_name
        self.entries_list = []
        self.entries_list_to_delete = []
        self.sorting_type = config.get('history_sorting')

    def apply_entries_sorting(self):
        if self.sorting_type == 'az_sorting':
            self.entries_list.sort(key=lambda x: x[2])
        elif self.sorting_type == 'za_sorting':
            self.entries_list.sort(key=lambda x: x[2], reverse=True)
        elif self.sorting_type == 'min_max_usage_sorting':
            self.entries_list.sort(key=lambda x: x[7])
        elif self.sorting_type == 'max_min_usage_sorting':
            self.entries_list.sort(key=lambda x: x[7], reverse=True)

    def add_entry(self, entry_id, entry_name, index):
        entry = Button(
            id=str(entry_id),
            text=str(entry_name),
            size_hint=(1, None),
            height="70dp",
            font_size=config.get('entries_font_size'),
            on_release=self.tag_entry_to_delete,
        )
        self.ids.history_panel_id.add_widget(entry, index)

    def refresh_history(self):
        self.current_list_id = EntriesScreen.current_list_id
        self.current_list_name = EntriesScreen.current_list_name
        self.entries_list = db.read_entries_history(self.current_list_id)
        self.apply_entries_sorting()
        self.entries_list_to_delete.clear()
        self.ids.revoke_btn_id.disabled = True
        self.ids.history_panel_id.clear_widgets()
        for entry_num in range(len(self.entries_list)):
            self.add_entry(
                self.entries_list[entry_num][0],    # entry_id
                self.entries_list[entry_num][2],    # entry_name
                0,                                  # index
            )

    def search_entry(self):
        pass

    def tag_entry_to_delete(self, btn_obj):
        self.ids.history_panel_id.remove_widget(btn_obj)
        self.entries_list_to_delete.append([btn_obj.id, btn_obj.text])
        self.ids.revoke_btn_id.disabled = False

    def apply_delete_entry(self):
        for i in self.entries_list_to_delete:
            db.delete_entry(i[0])

    def revoke_entry(self):
        last_entry = self.entries_list_to_delete.pop(-1)
        if len(self.entries_list_to_delete) == 0:
            self.ids.revoke_btn_id.disabled = True
        self.add_entry(last_entry[0], last_entry[1], 0)


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        # TODO refactor backgroung - handle list type for config.get()
        backgroung_dict = {
            'Orange': [0.8, 0.4, 0.0, 1],
            "White": [1.0, 1.0, 1.0, 1],
            "Black": [0, 0, 0, 1],
        }
        Window.clearcolor = backgroung_dict[config.get('background_colour')]
        Window.softinput_mode = 'below_target'  # TextInput keyboard position https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs
        # TODO move ALL paths to system settings
        self.icon = 'images/icon.png'
        self.title = F"{config.get('app_title')}  {config.get('app_version')}"
        config.load_config()
        db.create_db()
        lang.reload_lang()
        return ScreenManagement()

    def build_config(self, app_config):
        app_config.setdefaults('', {
            # 'font_size': '15dp',
            # 'entries_font_size': 42,
            # 'lists_font_size': '15dp',
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
    db.create_db()  # will create database at first start
    MainApp().run()
