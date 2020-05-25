from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import Database.DBLayer as db


class ButtonListItem(Button):
    id = StringProperty(None)
    text = StringProperty(None)

    def click(button):
        global app
        app.clearSelection()
        button.background_color = (0,160,66,.9)


class ListsScreen(Screen):
    Lists_list = ListProperty(db.read_lists())

    def set_list_id_pressed(self, list_id):
        # TODO find correct solution
        EntriesScreen.list_id = list_id

    def read_entries_count(self, list_id):
        return db.read_entries_count(list_id)


class EntriesScreen(Screen):
    list_id = None
    # TODO add scroll

    def add_entrie(self, id, text):
        ib = ButtonListItem(
            id=id,
            text=text
        )
        entrie_panel = self.ids.entries_panel_id
        entrie_panel.add_widget(ib)

    def add_all_entries(self):
        entries_list = db.read_entries(self.list_id)
        for no in range(len(entries_list)):
            self.add_entrie('id_entrie', entries_list[no][2])  # id_entrie just a useless text, not used at all

    def remove_all_entries(self):
        self.ids.entries_panel_id.clear_widgets()

    def done_entrie(self):
        db.complete_entrie('entrie name')  # TODO entrie name

    def print_this(self, text):
        EntriesScreen.add_entrie(self, 'dsf', text)


class SettingsScreen(Screen):
    pass


class ScreenManagement(ScreenManager):
    pass


pre = Builder.load_file("main.kv")


class MainApp(App):
    def build(self):
        return pre


if __name__ == '__main__':
    MainApp().run()

