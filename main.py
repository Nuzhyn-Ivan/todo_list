import kivy.config
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import DictProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, CardTransition, Screen

import CustomWidgets
import lang.Localization as lang
import utils.ConfigParser as config
import utils.DBLayer as db

# TODO add type of param and return for all methods


class ScreenManagement(ScreenManager):
    """
    Class to handle all screens in app
    """
    lists_screen = 'lists_screen'
    entries_screen = 'entries_screen'
    entry_details_screen = 'entry_details_screen'
    entry_info_screen = 'entry_info_screen'
    settings_screen = 'settings_screen'
    history_screen = 'history_screen'
    tags_screen = 'tags_screen'

    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        """
        Method to handle 'key pressed' events
        Full list of key codes:
        https://gist.github.com/Enteleform/a2e4daf9c302518bf31fcc2b35da4661
        """
        back_key = 27  # the 'ESC' key on win or 'Back' key on phone

        if key == back_key:
            if self.current_screen.name == self.lists_screen:
                return False  # exit the app from this page
            elif self.current_screen.name == self.settings_screen:
                self.change_screen(self.lists_screen, 'right')
                return True  # do not exit the app
            elif self.current_screen.name == self.entries_screen:
                self.change_screen(self.lists_screen, 'right')
                return True  # do not exit the app

    # todo add keyword arguments for all usages
    def change_screen(self, screen_name: str, transition_direction: str):
        """
        Method to change app screen.
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

    def refresh_screens(self):
        pass
        # TODO remove all and add again


class ListsScreen(Screen):
    def __init__(self, **kwargs):
        super(ListsScreen, self).__init__(**kwargs)
        self.is_edit_mode = False
        Clock.schedule_once(self.refresh_lists, 0.5)  # Add lists to Lists screen on app start

    def add_list(self, list_id: str, list_name: str, index: int):
        """
        Method to add List on Lists screen.
        :param list_id: List ID
        :param list_name: List name
        :param index: Index of exact list on Lists screen.
        :return:
        """
        list_btn = Button(
            font_size=config.get_option_value('lists_font_size'),
            size_hint=(1, None),
            height="70dp",
        )
        list_btn.id = list_id
        list_btn.name = list_name
        list_btn.entries_count = db.read_entries_count(list_id)

        # todo move out is_edit_mode . One responsibility for one object
        if self.is_edit_mode:
            list_btn.bind(on_release=self.open_edit_popup)
            list_btn.text = F"{list_btn.name}{lang.get('tap_to_edit')}"
        else:
            list_btn.bind(on_release=self.open_list)
            list_btn.text = F"{ list_btn.name} ({list_btn.entries_count})"
        self.ids.lists_panel_id.add_widget(list_btn, index)

    def refresh_lists(self, *delta_time: float):
        """
        Method to remove all lists from Lists screen and add them again from database.
        :param delta_time: Time in sec for Clock.schedule_once(). See ListsScreen __init__
        :return:
        """
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for list in lists:
            self.add_list(
                list_id=list[0],
                list_name=list[1],
                index=0,
            )

    def open_list(self, btn_obj):
        """
        Method to change screen to 'Entries', and add entries of exact list
        :param btn_obj: Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        :return:
        """

        # Init entries_screen
        list_id = btn_obj.id
        entries_screen_instance = self.manager.get_screen(self.manager.entries_screen)
        entries_screen_instance.init_entries_screen(list_id)

        # Open entries_screen
        self.manager.change_screen(self.manager.entries_screen, 'left')

    def create_list(self, list_name: str):
        """
        Method to add list to database and Lists screen
        :param list_name: Name of list to create
        :return:
        """
        # TODO - implement lists order display
        order_id_of_list = 1
        list_name = list_name.strip()
        if len(list_name) == 0:
            # TODO - move to lang
            MainApp.open_error_popup('List name cant be empty')
        else:
            result, error = db.create_list(list_name, order_id_of_list)
            if result:
                last_list = db.read_last_list()[0]
                # todo add keyword arguments
                self.add_list(
                    list_id=last_list[0],
                    list_name=last_list[1],
                    index=0,
                )
            elif error.args[0]:  # TODO - handle all errors
                MainApp.open_error_popup(error.args[0])

    def delete_list(self, btn_obj):
        """
        Method to delete list from database and Lists screen
        :param btn_obj: Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        :return:
        """
        db.delete_list_by_id(btn_obj.id)
        self.ids.lists_panel_id.remove_widget(btn_obj)

    def change_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        # refresh_lists_timer = Clock.schedule_interval(self.refresh_lists, 0.5)
        if self.is_edit_mode:
            self.ids.lists_edit_btn.text = lang.get('apply_edit_btn')
        else:
            self.ids.lists_edit_btn.text = lang.get('edit_btn')
            # refresh_lists_timer.cancel()
        self.refresh_lists()
        # refresh_lists_timer()

    @staticmethod
    def open_edit_popup(btn_obj):
        """
        Method to open ListEditPopup
        :param btn_obj: Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        :return:
        """
        list_edit_popup = CustomWidgets.ListEditPopup(
            title=btn_obj.text.replace(lang.get('tap_to_edit'), ''),
            title_align='center',
        )
        list_edit_popup.list_name = btn_obj.text.replace(lang.get('tap_to_edit'), '')
        list_edit_popup.open()


class EntriesScreen(Screen):
    def __init__(self, **kwargs):
        super(EntriesScreen, self).__init__(**kwargs)
        self.ready_to_revoke_entries = []
        self.current_list_id = None
        self.current_list_name = None

    def init_entries_screen(self, list_id: str):
        self.current_list_id = list_id
        self.current_list_name = db.get_list_name(int(self.current_list_id))
        self.refresh_entries_screen()

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """
        Method to add entry to EntriesScreen and database
        :param entry_id: ID of entry
        :param entry_name: name of entry
        :param index: index of entry to display on entries screen. Not implemented
        :return:
        """
        entry_note = Button(
            text=lang.get('open_entry_info'),
            size_hint=(0.2, None),
            height=config.get_option_value('entries_height'),
            font_size=config.get_option_value('entries_font_size'),
            on_release=self.open_entry_info_screen,
        )
        entry_note.id = entry_id

        entry = CustomWidgets.Button(
            text=entry_name,
            size_hint=(0.6, None),
            height=config.get_option_value('entries_height'),
            font_size=config.get_option_value('entries_font_size'),
            on_release=self.complete_entry,
            duration_long_touch=0.4,
        )
        entry.id = entry_id

        self.ids.entries_panel_id.add_widget(entry_note, index)
        self.ids.entries_panel_id.add_widget(entry, index)

    def refresh_entries_screen(self):
        """
        Method to refresh EntriesScreen
        :param:
        :return:
        """
        # TODO remove and refactor label sizing

        # Remove all entries
        for widget in self.ids.entries_panel_id.children:
            widget.clear_widgets()  # remove all child's from Layout
        self.ids.entries_panel_id.clear_widgets()  # remove all layouts from entries_panel

        # Add actual entries
        entries_list = db.read_entries(int(self.current_list_id))
        for entry in entries_list:
            self.add_entry(
                entry_id=entry[0],
                entry_name=entry[2],
                index=0,
            )

        # Add actual list name to 'Back' button

        self.ids.current_list_btn.text = F"<--   {self.current_list_name}"
        self.ids.tools_btn_id.text = lang.get('tools_btn')

    def complete_entry(self, btn_obj):
        """
        Method to remove entry from entries screen and mark as completed in db
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        :return:
        """
        db.complete_entry(btn_obj.id)
        self.ready_to_revoke_entries.append(btn_obj.text)
        self.ids.entries_panel_id.remove_widget(btn_obj)
        self.ids.revoke_btn_id.disabled = False
        self.refresh_entries_screen()

    def complete_entry_with_details(self, btn_obj):
        """
        Method to remove entry from entries screen and mark as completed in db with adding details
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        :return:
        """
        self.complete_entry(btn_obj)
        # TODO complete_entry have to be in EntryDetailsScreen.save
        #  Now entry completed even if close app on entry_details_screen without save
        entry_details_screen_instance = self.manager.get_screen(self.manager.entry_details_screen)
        entry_details_screen_instance.entry_id = btn_obj.id
        self.manager.change_screen(self.manager.entry_details_screen, "up")

    def create_entry(self, text: str):
        """
        Method to add entry to database and refresh EntriesScreen
        :param text: Entry name
        :return:
        """
        text = text.strip()
        # TODO add error handling same with add_list
        if text:
            db.create_entry(list_id=int(self.current_list_id),
                            entry_name=text,
                            )
            self.refresh_entries_screen()

    def revoke_entry(self):
        """
        Method to recover last completed entry and add it back to EntriesScreen
        :param:
        :return:
        """
        entry_text = self.ready_to_revoke_entries.pop()
        self.create_entry(entry_text)
        if len(self.ready_to_revoke_entries) == 0:
            self.ids.revoke_btn_id.disabled = True

    # todo add annotation for all btn_obj
    def open_tools_screen(self, btn_obj):
        """
        Method to open one of the Tools screen - TagsScreen, HistoryScreen
        :param btn_obj: Object of pressed button.
        :return:
        """
        pressed_button = lang.get_key_by_value(btn_obj.text)
        if pressed_button == 'tags_btn':
            self.manager.change_screen(self.manager.tags_screen, "right")
        elif pressed_button == 'history_btn':
            self.manager.change_screen(self.manager.history_screen, "right")
        else:
            # TODO: add exception handling
            pass

    def open_entry_info_screen(self, btn_obj: Button):
        """
        Method to open EntryInfo screen
        :param btn_obj: Object of pressed button.
        :return:
        """
        # Init entry_info_screen
        entry_info_screen_instance = self.manager.get_screen(self.manager.entry_info_screen)
        current_entry_id = btn_obj.id
        entry_info_screen_instance.init_entry_info_screen(current_entry_id)

        # Change screen to entry_info_screen
        self.manager.change_screen(self.manager.entry_info_screen, "right")


class EntryInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(EntryInfoScreen, self).__init__(**kwargs)
        self.note_text = str
        self.current_entry_id = None

    def save_note(self):
        """
        Method to save note to database
        :param:
        :return:
        """
        self.manager.change_screen(self.manager.entries_screen, "left")
        db.set_entry_note(self.entry_id, self.ids.note_id.text)
        self.ids.note_id.text = ''

    def back(self):
        """
        Method to change screen to EntriesScreen
        :param:
        :return:
        """
        self.manager.change_screen(self.manager.entries_screen, "left")

    def init_entry_info_screen(self, current_entry_id):
        """
        Method to initiate EntryNotesScreen
        :param:
        :return:
        """
        self.current_entry_id = current_entry_id
        self.note_text = db.get_entry_note(current_entry_id)
        self.ids.note_id.text = self.note_text


class EntryDetailsScreen(Screen):
    def __init__(self, **kwargs):
        super(EntryDetailsScreen, self).__init__(**kwargs)
        self.note_text = ''
        self.entry_id = ''
        self.last_source = ''

        # TODO clear source_id.text if another list opened

    def clear_source(self):
        self.ids.source_id.text = ""

    def save(self):
        # TODO - add validation(empty, int only for qty, float for price )
        source_name = self.ids.source_id.text
        price = self.ids.price_id.text
        quantity = self.ids.qty_id.text
        source_id = None

        if not db.is_source_exist(source_name):
            db.create_source(source_name)
        source_id = db.get_source_id(source_name)

        db.create_entries_history(source_id, self.entry_id, price, quantity)

        self.ids.qty_id.text = ""
        self.ids.price_id.text = ""
        self.manager.change_screen(self.manager.entries_screen, "down")


class SettingsScreen(Screen):
    # TODO fix bug with font_size not apply on save(same as lang)
    # TODO move all kv strings to lang
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)

    current_settings = DictProperty({
        'background_colour': config.get_option_value('background_colour'),
        'lang': config.get_option_value('lang'),
        'entries_font_size': config.get_option_value('entries_font_size'),
        'lists_font_size': config.get_option_value('lists_font_size'),
        'max_suggestions_count': config.get_option_value('max_suggestions_count'),
        'font_size': config.get_option_value('font_size'),
        'padding': config.get_option_value('padding'),
        'spacing': config.get_option_value('spacing'),
        'scrollview_size': config.get_option_value('scrollview_size'),
    })

    def get_current_settings(self):
        """
        Method to actualize self.current_settings from app config
        :param:
        :return:
        """
        for key in self.current_settings:
            self.current_settings[key] = config.get_option_value(key)

    @staticmethod
    def reset_db():
        """
        Method to drop current database and recreate it
        :param:
        :return:
        """
        # TODO Add popup msg that app will be closed and need to run manually. Or add correct restart of app
        db.drop_database()
        MainApp.get_running_app().stop()

    def apply_settings(self):
        """
        Method to apply settings from self.current_settings to app config
        :param:
        :return:
        """
        for key in self.current_settings:
            config.set_option_value(key, self.current_settings[key])
        # TODO lang reload doesnt work
        self.manager.refresh_screens()


class TagsScreen(Screen):
    pass


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.entries_list = []
        self.entries_list_to_delete = []
        self.sorting_type = config.get_option_value('history_sorting')

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """
        Method to add entry to HistoryScreen and database
        :param entry_id: ID of entry
        :param entry_name: name of entry
        :param index: index of entry to display on entries screen. Not implemented
        :return:
        """
        entry = Button(
            text=entry_name,
            size_hint=(1, None),
            height="70dp",
            font_size=config.get_option_value('entries_font_size'),
            on_release=self.tag_entry_to_delete,
        )
        entry.id = entry_id
        self.ids.history_panel_id.add_widget(entry, index)

    def refresh_history_screen(self):
        """
        Method to refresh History Screen
        :param:
        :return:
        """
        entries_screen_instance = self.manager.get_screen(self.manager.entries_screen)

        # Remove all
        self.ids.history_panel_id.clear_widgets()

        # Add actual list name to 'Back' button
        self.ids.back_btn.text = F"<--   {entries_screen_instance.current_list_name}"

        # Add properly sorted entries
        self.entries_list = db.read_entries_history(int(entries_screen_instance.current_list_id))
        self.apply_entries_sorting(self.sorting_type)
        # TODO replace range(len()) with enumerate(), compare memory
        # for entry_num in range(len(self.entries_list)):
        #     self.add_entry(
        #         self.entries_list[entry_num][0],  # entry_id
        #         self.entries_list[entry_num][2],  # entry_name
        #         0,  # index
        #     )
        for entry in self.entries_list:
            self.add_entry(
                entry_id=entry[0],
                entry_name=entry[2],
                index=0,
            )

    def apply_entries_sorting(self, sorting_type: str):
        """
        Method to apply chosen sort type
        :param:
        :return:
        """
        if sorting_type == 'az_sorting':
            self.entries_list.sort(key=lambda x: x[2])
        elif sorting_type == 'za_sorting':
            self.entries_list.sort(key=lambda x: x[2], reverse=True)
        elif sorting_type == 'min_max_usage_sorting':
            self.entries_list.sort(key=lambda x: x[7])
        elif sorting_type == 'max_min_usage_sorting':
            self.entries_list.sort(key=lambda x: x[7], reverse=True)

    def tag_entry_to_delete(self, btn_obj):
        """
        Method to
        :param:
        :return:
        """
        self.ids.history_panel_id.remove_widget(btn_obj)
        self.entries_list_to_delete.append(btn_obj.id)
        self.ids.revoke_btn_id.disabled = False

    def apply_delete_entry(self):
        """
        Method to delete entry from HistoryScreen
        :param:
        :return:
        """
        for entry in self.entries_list_to_delete:
            db.delete_entry(entry)
        self.entries_list_to_delete.clear()
        self.ids.revoke_btn_id.disabled = True

    def revoke_entry(self):
        """
        Method to recover last completed entry and add it back to HistoryScreen
        :param:
        :return:
        """
        last_entry = self.entries_list_to_delete.pop(-1)

        # Disable 'revoke' button if no entries left to revoke
        if len(self.entries_list_to_delete) == 0:
            self.ids.revoke_btn_id.disabled = True

        # Add entry
        self.add_entry(
            entry_id=last_entry[0],
            entry_name=last_entry[1],
            index=0,
        )


class MainApp(App):
    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)

    def build(self):
        """
        Method to build app
        :param:
        :return:
        """
        # TODO refactor background - handle list type for config.get()
        background_dict = {
            'Orange': [0.8, 0.4, 0.0, 1],
            "White": [1.0, 1.0, 1.0, 1],
            "Black": [0, 0, 0, 1],
        }
        Window.clearcolor = background_dict[config.get_option_value('background_colour')]
        Window.softinput_mode = 'below_target'  # TextInput keyboard position https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs
        # TODO move ALL paths to system settings
        self.icon = 'images/icon.png'
        self.title = F"{config.get_option_value('app_title')}  {config.get_option_value('app_version')}"
        lang.reload_lang()
        config.load_config()

        return ScreenManagement()

    def build_config(self, app_config: kivy.config.ConfigParser):
        """
        Method to build app config
        :param app_config:
        :return:
        """
        app_config.setdefaults('', {
            # 'font_size': '15dp',
            # 'entries_font_size': 42,
            # 'lists_font_size': '15dp',
            'app_version': '0.0.20',
            'app_title': 'TODOit',
            'db_path': r"..\TODO.db",
        },)

    @staticmethod
    def open_error_popup(text):
        """
        Method to open ErrorPopup
        :param:
        :return:
        """
        CustomWidgets.ErrorPopup.error_text = text
        CustomWidgets.ErrorPopup().open()


if __name__ == '__main__':
    db.actualize_database()
    MainApp().run()
