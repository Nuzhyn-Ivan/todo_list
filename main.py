import kivy.config
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import DictProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


import CustomWidgets
import lang.Localization as lang
import utils.ConfigParser as config
import utils.DBLayer as db
from utils.ScreenManagement import ScreenManagement


class ListsScreen(Screen):
    def __init__(self, **kwargs):
        super(ListsScreen, self).__init__(**kwargs)
        self.is_edit_mode = False
        Clock.schedule_once(self.init_screen, 0.5)  # Add lists to Lists screen on app start

    def init_screen(self, *delta_time: float):
        self.refresh_lists()

    def add_list(self, list_id: str, list_name: str, index: int):
        """
        Add List on Lists screen.
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
            list_btn.text = F"{list_btn.name} ({list_btn.entries_count})"
        self.ids.lists_panel_id.add_widget(list_btn, index)

    def refresh_lists(self):
        """
        Remove all lists from Lists screen and add them again from database.
        """
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for list_id, list_name, _, _ in lists:
            self.add_list(
                list_id=list_id,
                list_name=list_name,
                index=0,
            )

    def open_list(self, btn_obj: Button):
        """
        Change screen to 'Entries', add entries of exact list
        :param btn_obj: Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        :return:
        """

        # Set pressed list_id  to entries_screen
        list_id = btn_obj.id
        entries_screen_instance = self.manager.get_screen(self.manager.entries_screen)
        entries_screen_instance.set_current_list(list_id)

        # Open entries_screen
        self.manager.change_screen(self.manager.entries_screen, 'left')

    def create_list(self, list_name: str):
        """
        Add list_name to database and Lists screen
        :param list_name: Name of list to create
        :return:
        """
        # todo - implement lists order display
        # todo - handle duplicates
        order_id_of_list = 1
        list_name = list_name.strip()
        if list_name:
            db.create_list(list_name, order_id_of_list)
            list_id, list_name = db.read_last_list()
            # todo add keyword arguments
            self.add_list(
                list_id=list_id,
                list_name=list_name,
                index=0,
            )
        else:
            MainApp.open_error_popup(lang.get('list_name_empty'))

        # TODO - handle all errors
        #     MainApp.open_error_popup(error.args[0])

    def delete_list(self, btn_obj: Button):
        """
        Delete list from database and Lists screen
        :param btn_obj: Object of pressed list button from Lists screen. Contain 'id' and 'name' of the list
        :return:
        """
        db.delete_list_by_id(btn_obj.id)
        self.ids.lists_panel_id.remove_widget(btn_obj)

    def change_edit_mode(self):
        self.is_edit_mode = not self.is_edit_mode
        if self.is_edit_mode:
            self.ids.lists_edit_btn.text = lang.get('apply_edit_btn')
        else:
            self.ids.lists_edit_btn.text = lang.get('edit_btn')
        self.refresh_lists()

    @staticmethod
    def open_edit_popup(btn_obj: Button):
        """
        Open ListEditPopup
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
        self.current_list_id = ''
        self.current_list_name = ''

    def set_current_list(self, list_id: str):
        self.current_list_id = list_id
        self.current_list_name = db.get_list_name(self.current_list_id)

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """
        Add entry to EntriesScreen
        :param entry_id: ID of entry
        :param entry_name: name of entry
        :param index: index of entry to display on entries screen. Not implemented
        """
        entry_note = Button(
            text=lang.get('open_entry_info'),
            size_hint=(0.2, None),
            height=config.get_option_value('entries_height'),
            font_size=config.get_option_value('entries_font_size'),
            on_release=self.open_entry_info_screen,
        )
        entry_note.id = entry_id
        self.ids.entries_panel_id.add_widget(entry_note, index)

        entry = CustomWidgets.Button(
            text=entry_name,
            size_hint=(0.6, None),
            height=config.get_option_value('entries_height'),
            font_size=config.get_option_value('entries_font_size'),
            on_release=self.complete_entry,
            duration_long_touch=0.4,
        )
        entry.id = entry_id
        self.ids.entries_panel_id.add_widget(entry, index)

    def refresh_entries_screen(self):
        """
        Refresh EntriesScreen
        :param:
        :return:
        """
        # TODO remove and refactor label sizing

        # Remove all entries
        for widget in self.ids.entries_panel_id.children:
            widget.clear_widgets()  # remove all child's from Layout
        self.ids.entries_panel_id.clear_widgets()  # remove all layouts from entries_panel

        # Add actual entries
        entries_list = db.read_entries(self.current_list_id)
        for entry in entries_list:
            self.add_entry(
                entry_id=entry[0],
                entry_name=entry[2],
                index=0
            )

        # Add actual list name to 'Back' button
        self.ids.current_list_btn.text = F"<--   {self.current_list_name}"
        self.ids.tools_btn_id.text = lang.get('tools_btn')

    def complete_entry(self, btn_obj: Button):
        """
        Remove entry from entries screen and mark as completed in db
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        """
        db.complete_entry(btn_obj.id)
        self.ready_to_revoke_entries.append(btn_obj.text)
        self.ids.entries_panel_id.remove_widget(btn_obj)
        self.ids.revoke_btn_id.disabled = False
        self.refresh_entries_screen()

    def complete_entry_with_details(self, btn_obj: Button):
        """
        Remove entry from entries screen and mark as completed in db with adding details
        :param btn_obj: Object of pressed entry button from Entries screen. Contain 'id' and 'name' of the entry
        """
        # TODO complete_entry have to be in EntryDetailsScreen.save
        #  Now entry completed even if close app on entry_details_screen without save
        self.complete_entry(btn_obj)

        complete_entry_screen_instance = self.manager.get_screen(self.manager.complete_entry_screen)
        complete_entry_screen_instance.entry_id = btn_obj.id
        self.manager.change_screen(self.manager.complete_entry_screen, "up")

    def create_entry(self, text: str):
        """
        Add entry to database and refresh EntriesScreen
        :param text: Entry name
        :return:
        """
        text = text.strip()
        # TODO add error handling same with add_list
        if text:
            db.create_entry(
                list_id=int(self.current_list_id),
                entry_name=text,
            )
            self.refresh_entries_screen()

    def revoke_entry(self):
        """
        Recover last completed entry and add it back to EntriesScreen
        :param:
        :return:
        """
        entry_text = self.ready_to_revoke_entries.pop()
        self.create_entry(entry_text)

        # Disable revoke btn if no entries to revoke
        if not self.ready_to_revoke_entries:
            self.ids.revoke_btn_id.disabled = True

    # todo add annotation for all btn_obj
    def open_tools_screen(self, btn_obj: Button):
        """
        Open one of the Tools screen - TagsScreen, HistoryScreen
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
        Open EntryInfo screen
        :param btn_obj: Object of pressed button.
        :return:
        """
        # Init entry_info_screen
        entry_info_screen_instance = self.manager.get_screen(self.manager.entry_info_screen)
        current_entry_id = btn_obj.id
        entry_info_screen_instance.init_screen(current_entry_id)

        # Change screen to entry_info_screen
        self.manager.change_screen(self.manager.entry_info_screen, "right")


class EntryInfoScreen(Screen):
    def __init__(self, **kwargs):
        super(EntryInfoScreen, self).__init__(**kwargs)
        self.note_text = str
        self.current_entry_id = None

    def init_screen(self, current_entry_id):
        """
        Initiate EntryNotesScreen
        :param:
        :return:
        """
        self.current_entry_id = current_entry_id
        self.note_text = db.get_entry_note(current_entry_id)
        self.ids.note_id.text = self.note_text

    def save_note(self):
        """
        Save note to database
        :param:
        :return:
        """
        self.manager.change_screen(self.manager.entries_screen, "left")
        db.set_entry_note(self.entry_id, self.ids.note_id.text)
        self.ids.note_id.text = ''

    def back(self):
        """
        Change screen to EntriesScreen
        :param:
        :return:
        """
        self.manager.change_screen(self.manager.entries_screen, "left")


class CompleteEntryScreen(Screen):
    def __init__(self, **kwargs):
        super(CompleteEntryScreen, self).__init__(**kwargs)
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

        if not db.is_source_exist(source_name):
            db.create_source(source_name)
        source_id = db.get_source_id(source_name)
        db.create_entries_history(
            source_id=source_id, entry_id=int(self.entry_id), price=float(price), quantity=int(quantity)
        )

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

    def init_screen(self):
        self.get_current_settings()

    def get_current_settings(self):
        """
        Actualize self.current_settings from app config
        :param:
        :return:
        """
        for key in self.current_settings:
            self.current_settings[key] = config.get_option_value(key)

    @staticmethod
    def reset_db():
        """
        Drop current database and recreate it
        :param:
        :return:
        """
        # TODO Add popup msg that app will be closed and need to run manually. Or add correct restart of app
        db.drop_database()
        MainApp.get_running_app().stop()

    def apply_settings(self):
        """
        Apply settings from self.current_settings to app config
        :param:
        :return:
        """
        for key in self.current_settings:
            config.set_option_value(option=key, value=self.current_settings[key])
        # TODO lang reload doesnt work
        self.manager.refresh_screens()


class TagsScreen(Screen):
    # todo implement
    pass


class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super(HistoryScreen, self).__init__(**kwargs)
        self.entries_list = []
        self.entries_list_to_delete = []
        self.sorting_type = config.get_option_value('history_sorting')

    def init_screen(self):
        self.refresh_history_screen()

    def add_entry(self, entry_id: str, entry_name: str, index=0):
        """
        Add entry to HistoryScreen and database
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
        Refresh History Screen
        :param:
        :return:
        """
        entries_screen_instance = self.manager.get_screen(self.manager.entries_screen)

        # Remove all
        self.ids.history_panel_id.clear_widgets()

        # Add actual list name to 'Back' button
        self.ids.back_btn.text = F"<--   {entries_screen_instance.current_list_name}"

        # Add properly sorted entries
        self.entries_list = db.read_entries_history(entries_screen_instance.current_list_id)
        self.apply_entries_sorting(self.sorting_type)
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
        Apply chosen sort type
        :param:
        :return:
        """
        match sorting_type:
            case 'az_sorting':
                self.entries_list.sort(key=lambda x: x[2])
            case 'za_sorting':
                self.entries_list.sort(key=lambda x: x[2], reverse=True)
            case 'min_max_usage_sorting':
                self.entries_list.sort(key=lambda x: x[7])
            case 'max_min_usage_sorting':
                self.entries_list.sort(key=lambda x: x[7], reverse=True)

    def tag_entry_to_delete(self, btn_obj: Button):
        """
        Delete entry from UI
        Put to self.entries_list_to_delete
        Enable Revoke btn
        :param: btn_obj
        :return:
        """
        self.ids.history_panel_id.remove_widget(btn_obj)
        self.entries_list_to_delete.append(btn_obj.id)
        self.ids.revoke_btn_id.disabled = False

    def apply_delete_entry(self):
        """
        Delete entry from HistoryScreen
        :param:
        :return:
        """
        for entry in self.entries_list_to_delete:
            db.delete_entry(entry)
        self.entries_list_to_delete.clear()
        self.ids.revoke_btn_id.disabled = True

    def revoke_entry(self):
        """
        Recover last completed entry and add it back to HistoryScreen
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
        Build app
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
        Build app config
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
        }, )

    @staticmethod
    def open_error_popup(text):
        """
        Open ErrorPopup
        :param:
        :return:
        """
        CustomWidgets.ErrorPopup.error_text = text
        CustomWidgets.ErrorPopup().open()


if __name__ == '__main__':
    db.actualize_database()
    MainApp().run()
