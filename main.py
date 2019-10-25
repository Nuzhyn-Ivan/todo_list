import kivy
import Database.DBLayer as db
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.clock import Clock

kivy.require("1.10.1")

# TODO move to properties and add properties reader
BUTTON_FONT_SIZE = 22
BUTTON_SIZE = (1.0, 1.0)
BUTTON_BACKGROUND_COLOR = [1, 1, 1, .3]
BUTTON_COLOR = [1, 1, 1, .5]

list_name = 'gfdgfg'


class ListsPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # TODO cover lists with genelad GridLayout
        # TODO add Label = counter of active entries for list
        # TODO add create list button inside another GridLayout
        # TODO add Settings and Search buttons inside another GridLayout
        self.cols = 1

        # TODO - add another class for converting dblayer to list of dict
        # TODO - add support for all dblayer def
        values = db.read_lists()
        fields = ["id", "name", "order_id", "created_date", ]
        lists = [dict(zip(fields, d)) for d in values]

        values = db.read_entries()
        fields = ["id", "list_id", "name", "is_completed", "created_date", "due_date", "frequency", ]
        entries = [dict(zip(fields, d)) for d in values]

        # TODO need to add buttons to Lists dynamically based on db state
        list_1_description = lists[0]["name"]
        list_2_description = lists[1]["name"]
        list_3_description = lists[2]["name"]
        list_4_description = lists[3]["name"]

        self.list_1 = Button(
            text=list_1_description,
            font_size=BUTTON_FONT_SIZE,
            size_hint=BUTTON_SIZE,
            background_color=BUTTON_BACKGROUND_COLOR,
            color=BUTTON_COLOR,
            #halign='left',
            #valign='middle',
            #padding_y= 1,
            #text_size=self.size
            #pos_hint={'center_x': 1, 'center_y': 1},
            #background_normal='',

        )
        self.list_1.bind(on_press=self.list_button_press)
        self.add_widget(self.list_1)
        #self.disabled = True

        self.list_2 = Button(
            text=list_2_description,
            font_size=BUTTON_FONT_SIZE,
            size_hint=BUTTON_SIZE,
        )
        self.list_2.bind(on_press=self.list_button_press)
        self.add_widget(self.list_2)

        self.list_3 = Button(
            text=list_3_description,
            font_size=BUTTON_FONT_SIZE,
            size_hint=BUTTON_SIZE,
        )
        self.list_3.bind(on_press=self.list_button_press)
        self.add_widget(self.list_3)

        self.list_4 = Button(
            text=list_4_description,
            font_size=BUTTON_FONT_SIZE,
            size_hint=BUTTON_SIZE,
        )
        self.list_4.bind(on_press=self.list_button_press)
        self.add_widget(self.list_4)

    def list_button_press(self, instance):
        global list_name
        list_name = instance.text
        chat_app.screen_manager.transition.direction = 'left'
        chat_app.screen_manager.current = 'Entries'


class EntriesPage(GridLayout):
    # TODO - open entries screen
    # TODO - need to add entries  dynamically based on db state
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # Back button
        self.back_to_lists = Button(
            # TODO replace with icon
            text="<--",
            font_size=BUTTON_FONT_SIZE,
            size_hint=BUTTON_SIZE,
        )
        self.back_to_lists.bind(on_press=self.open_screen_lists)
        self.add_widget(self.back_to_lists)

        # test Label
        self.message = Label(halign="center", valign="middle", font_size=30, text=list_name)
        self.add_widget(self.message)

    def open_screen_lists(self, instance):

        chat_app.screen_manager.transition.direction = 'right'
        chat_app.screen_manager.current = 'Lists'


class EpicApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.screen_manager = ScreenManager()
        self.lists_page = ListsPage()
        self.entries_page = EntriesPage()

    def build(self):

        # Lists page
        screen = Screen(name='Lists')
        screen.add_widget(self.lists_page)
        self.screen_manager.add_widget(screen)

        # Entries page
        screen = Screen(name='Entries')
        screen.add_widget(self.entries_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    chat_app = EpicApp()
    chat_app.run()
