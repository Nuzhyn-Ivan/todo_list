from kivy.app import App
from kivy.uix.gridlayout import GridLayout

class ListsWindow(GridLayout):
    pass

class ListsApp(App):
    def build(self):
        return ListsWindow()

if __name__=="__main__":
        la = ListsApp()
        la.run()