from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
import time
import Database.DBLayer as db



class ListsScreen(Screen):
    pass


class EntriesScreen(Screen):
    entries_descriptions = ListProperty(db.read_lists())





class MyScreenManager(ScreenManager):
    def refresh_entries(self):
        name = str(time.time())
        s = EntriesScreen(name=name,
                          entries_descriptions=db.read_lists()[1][1])
        self.add_widget(s)
        self.current = name


root_widget = Builder.load_string('''
#:import FadeTransition kivy.uix.screenmanager.FadeTransition
MyScreenManager:
    transition: FadeTransition()
    ListsScreen:
    EntriesScreen:
<ListsScreen>:
    name: 'lists'
    GridLayout:
        cols:1
        size: root.width, root.height
        
    # Upper Panel
        GridLayout:
            cols:3
            size_hint: 0.1, 0.1
            
            Button:
                text: 'Settings'
            Button:
                text: 'Edit'
            Button:
                text: 'Search'       
                
    # Lists buttons  
        GridLayout:
            cols:1
            size: root.width, root.height
            
            Button:
                text: 'Create new List' 
                font_size: 30
                
            Button:
                text: 'Create new List' 
                font_size: 30
                
            Button:
                text: 'Create new List' 
                font_size: 30
                
            Button:
                text: 'Create new List' 
                font_size: 30
                
            Button:
                text: 'Drag Store' 
                font_size: 30
                on_release: app.root.refresh_entries()
                
            Button:
                text: 'To Do'
                font_size: 30
                on_release: app.root.refresh_entries()
                
            Button:
                text: 'Supermarket'
                font_size: 30
                on_release: app.root.refresh_entries()
                
<EntriesScreen>:
#:import os os
    name: 'entries'
    GridLayout:
        cols:1
        # Upper panel
        GridLayout:
            size_hint: 0.1, 0.1
            cols:2
            
            Button:
                size_hint: 0.3, 0.1
                text: 'Back to Lists'
                on_release: app.root.current = 'lists'
            Label:
                size_hint: 0.7, 0.1
                text: 'name of current list'
                
        # Entries 
        GridLayout:
            cols:2
            
            # entry 1
            Label:
                text: 'My state is ' +  'root.entries_descriptions'
                font_size: 30 
            Button:
                text: 'sd'
                #'Plop world' if self.state == 'normal' else 'Release me!'
                #'My state is %s' % root.entries_descriptions
                font_size: 30
                on_release: app.root.refresh_entries()
                
                
        # add entry

''')


class ScreenManagerApp(App):
    def build(self):
        return root_widget


ScreenManagerApp().run()
