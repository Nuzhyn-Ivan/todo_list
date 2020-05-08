from kivy.app import App
from kivy.uix.boxlayout import BoxLayout


class EntriesWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        def refresh_entries(self):
        # https://www.youtube.com/watch?v=H-3LX3tbtb8&list=PLW062AfleDZbWPQXjyMeLOlcL8aQ4aLeP&index=13
            pass


class EntriesApp(App):
    def build(self):
        return EntriesWindow()


if __name__ == "__main__":
    oa = EntriesApp()
    oa.run()
