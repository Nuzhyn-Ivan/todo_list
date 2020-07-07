from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, SlideTransition, CardTransition
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
import gesture_box as gesture

import Database.DBLayer as db


Window.softinput_mode = 'below_target'
# https://android.developreference.com/article/19684878/Android+on-screen+keyboard+hiding+Python+Kivy+TextInputs



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

    def read_entries_count(self, list_id):
        return db.read_entries_count(list_id)

    def open_list_popup(self, *args):
        CreateListPopup().open()

    def refresh_lists(self):
        lists = db.read_lists()
        self.ids.lists_panel_id.clear_widgets()
        for i in lists:
            list_btn = ButtonListItem(
                id=str(i[0]),  # id
                text=str(i[1] + " (" + db.read_entries_count(i[0]) + ")"),  # list name
                size_hint=(1, None),
                height="70dp",
            )
            list_btn.bind(on_press=self.open_entry)
            lists_panel = self.ids.lists_panel_id
            lists_panel.add_widget(list_btn)

    def open_entry(self, btn_obj):
        EntriesScreen.list_id = btn_obj.id
        EntriesScreen.list_name = db.get_list_name(btn_obj.id)
        self.manager.transition = CardTransition(direction='left', duration=0.1)
        self.manager.current = "entries_screen"


class EntriesScreen(MDScreen):
    list_id = StringProperty()
    list_name = StringProperty()
    # TODO add scroll

    def add_entry(self, id, text):
        entry = ButtonListItem(
            id=id,
            text=text,
            size_hint=(1, None),
            height="70dp",

        )
        entry.bind(on_release=self.done_entry)
        entry_panel = self.ids.entries_panel_id
        entry_panel.add_widget(entry)

    def refresh_entries(self):
        entries_list = db.read_entries(int(self.list_id))
        self.ids.entries_panel_id.clear_widgets()
        for no in range(len(entries_list)):
            self.add_entry('id_entry', entries_list[no][2])  # TODO - generate id correctly

    def done_entry(self, btn_obj):
        db.complete_entry(btn_obj.text)  # TODO entrie id
        self.ids.entries_panel_id.remove_widget(btn_obj)

    def focus_text_input(self, df):
        self.ids.input_id.focus = True

    def create_entry(self, text):
        text = text.strip()
        if text:
            self.add_entry(text, text)
            db.create_entry(self.list_id, text)
        Clock.schedule_once(self.focus_text_input, 0.1)


class SettingsScreen(MDScreen):
    def reset_db(self):
        db.recreate_database()

    def delete_list_by_name(self, text):
        db.delete_list_by_name(text)


class CreateListPopup(Popup):

    def create_list(self, text):
        text = text.strip()
        if text:
            db.create_list(text)

    def focus_text_input(self, df):
        self.ids.add_list_input_id.focus = True


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
                self.transition = CardTransition(direction='right', duration=0.1)
                self.current = "lists_screen"
                return True  # do not exit the app
            elif self.current_screen.name == "entries_screen":
                self.transition = CardTransition(direction='right', duration=0.1)
                self.current = "lists_screen"
                return True  # do not exit the app


class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'
        # self.theme_cls.theme_style = 'Dark'
        return Runner()


if __name__ == '__main__':
    MainApp().run()



