from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.lang import Builder

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition


class ListsScreen(Screen):

    def navigate_to_entries_in_list(self):
        print(self)


class EntriesScreen(Screen):

    pass


class ScreenManagement(ScreenManager):
    pass

pre = Builder.load_file("main.kv")

class MainApp(App):

    def build(self):
        return pre

sa = MainApp()
sa.run()

