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


class EntriesScreen(Screen):
    # TODO add scroll
    # TODO add entries dynamically
    Entries_list = ListProperty(db.read_entries(1))

    def add_entrie(self, id, text):
        ib = ButtonListItem(
            id=id,
            text=text
        )
        entrie_panel = self.ids.entries_panel_id
        entrie_panel.add_widget(ib)

    def add_all_entries(self):
        for no in range(4):
            self.add_entrie('id_my', self.Entries_list[no][2])

    def remove_all_entries(self):
        self.ids.entries_panel_id.clear_widgets()

    def done_entrie(self):
        db.complete_entrie('entrie name')  # TODO entrie name


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

