from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import Database.DBLayer as db
import settings as settings



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
        entrie = ButtonListItem(
            id=id,
            text=text,
            size_hint=(1, None)
        )
        entrie.bind(on_press=self.done_entrie)
        entrie_panel = self.ids.entries_panel_id
        entrie_panel.add_widget(entrie)

    def add_all_entries(self):
        entries_list = db.read_entries(self.list_id)
        for no in range(len(entries_list)):
            self.add_entrie('id_entrie', entries_list[no][2])  # TODO - generate id correctly

    def remove_all_entries(self):
        self.ids.entries_panel_id.clear_widgets()

    def done_entrie(self, btn_obj):
        db.complete_entrie(btn_obj.text)  # TODO entrie id
        self.ids.entries_panel_id.remove_widget(btn_obj)

    def create_entrie(self, id, text):
        self.add_entrie(id, text)
        db.create_entrie(self.list_id, text)



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

