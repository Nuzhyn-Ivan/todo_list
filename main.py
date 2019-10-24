import kivy
import Database.DBLayer as db
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
# to use buttons:
from kivy.uix.button import Button

kivy.require("1.10.1")


class ConnectPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2

        # TODO - move inside dblayer
        values = db.read_lists()
        fields = ["id", "name", "order_id", "created_date", ]
        lists = [dict(zip(fields, d)) for d in values]

        #values = db.read_entries()
       # fields = ["id", "list_id", "name", "is_completed", "created_date", "due_date", "frequency", ]
       # entries = [dict(zip(fields, d)) for d in values]

        list_1_description = lists[0]["name"]
        list_2_description = lists[1]["name"]
        list_3_description = lists[2]["name"]
        list_4_description = lists[3]["name"]

        self.list_1 = Button(text=list_1_description)
        self.list_1.bind(on_press=self.join_button)
        self.add_widget(self.list_1)

        self.list_2 = Button(text=list_2_description)
        self.list_2.bind(on_press=self.join_button)
        self.add_widget(self.list_2)

        self.list_3 = Button(text=list_3_description)
        self.list_3.bind(on_press=self.join_button)
        self.add_widget(self.list_3)

        self.list_4 = Button(text=list_4_description)
        self.list_4.bind(on_press=self.join_button)
        self.add_widget(self.list_4)



    def join_button(self, instance):
        port = self.port.text
        ip = self.ip.text
        username = self.username.text
        with open("prev_details.txt","w") as f:
            f.write(f"{ip},{port},{username}")
        #print(f"Joining {ip}:{port} as {username}")
        # Create info string, update InfoPage with a message and show it
        info = f"Joining {ip}:{port} as {username}"
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = 'Info'


# Simple information/error page
class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Just one column
        self.cols = 1

        # And one label with bigger font and centered text
        self.message = Label(halign="center", valign="middle", font_size=30)

        # By default every widget returns it's side as [100, 100], it gets finally resized,
        # but we have to listen for size change to get a new one
        # more: https://github.com/kivy/kivy/issues/1044
        self.message.bind(width=self.update_text_width)

        # Add text widget to the layout
        self.add_widget(self.message)

    # Called with a message, to update message text in widget
    def update_info(self, message):
        self.message.text = message

    # Called on label width update, so we can set text width properly - to 90% of label width
    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)

class EpicApp(App):
    def build(self):

        # We are going to use screen manager, so we can add multiple screens
        # and switch between them
        self.screen_manager = ScreenManager()

        # Initial, connection screen (we use passed in name to activate screen)
        # First create a page, then a new screen, add page to screen and screen to screen manager
        self.connect_page = ConnectPage()
        screen = Screen(name='Connect')
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)

        # Info page
        self.info_page = InfoPage()
        screen = Screen(name='Info')
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager


if __name__ == "__main__":
    chat_app = EpicApp()
    chat_app.run()