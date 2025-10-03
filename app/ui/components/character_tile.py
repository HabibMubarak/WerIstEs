from kivy.properties import StringProperty, ListProperty, BooleanProperty, ObjectProperty
from kivymd.uix.imagelist import MDSmartTile
from kivy.lang import Builder

Builder.load_file(r"app/ui/components/character_tile.kv")


class CharacterTile(MDSmartTile):

    tile_text = StringProperty("Spieler Name")
    tile_source = StringProperty("app/assets/img/twoplayer.png")
    tile_size = ListProperty([320, 320])
    on_eliminate = ObjectProperty(None, allow_none=True)
    on_undo = ObjectProperty(None, allow_none=True)
    left_only = BooleanProperty(False) 

    # Icons ein/aus
    show_icons = BooleanProperty(True)

    # Neue Properties für dynamische Icons
    tile_left_icon = StringProperty("thumb-down")
    tile_right_icon = StringProperty("thumb-up")


    def on_right_icon(self):
        """Daumen-hoch gedrückt."""
        if self.ids.left_icon.icon.startswith("thumb"):
            if not self.left_only and self.on_eliminate:
                print(f"Daumen hoch für {self.tile_text} ausgewählt")

    def on_left_icon(self):
        if self.left_only and self.on_undo:
            self.on_undo(self.tile_text)
        elif not self.left_only and self.on_eliminate:
            self.on_eliminate(self.tile_text)
