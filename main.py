
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen


class MainWindow(Screen):
    pass


class SecondWindow(Screen):
    pass


class WindowManage(ScreenManager):
    pass


# lists = Builder.load_file("lists.kv")
kv = Builder.load_file("main.kv")


# TODO - rewrite to use memory on start. Save any changes to db



class MyMainApp(App):
    def build(self):
        return kv


if __name__ == "__main__":
    MyMainApp().run()
