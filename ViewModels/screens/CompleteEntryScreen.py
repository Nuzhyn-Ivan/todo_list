from kivy.uix.screenmanager import Screen

from Models.utils import DBLayer as db


class CompleteEntryScreen(Screen):
    def __init__(self, **kwargs):
        super(CompleteEntryScreen, self).__init__(**kwargs)
        self.note_text = ''
        self.entry_id = ''
        self.last_source = ''

    # TODO clear source_id.text if another list opened
    def clear_source(self):
        self.ids.source_id.text = ""

    def save(self):
        # TODO - add validation(empty, int only for qty, float for price )
        source_name = self.ids.source_id.text
        price = self.ids.price_id.text
        quantity = self.ids.qty_id.text

        if not db.source_exist(source_name):
            db.create_source(source_name)
        source_id = db.get_source_id(source_name)
        db.create_entries_history(
            source_id=source_id, entry_id=int(self.entry_id), price=float(price), quantity=int(quantity)
        )

        self.ids.qty_id.text = ""
        self.ids.price_id.text = ""
        self.manager.change_screen(self.manager.entries_screen, "down")
