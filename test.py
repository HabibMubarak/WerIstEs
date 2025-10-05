from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivymd.app import MDApp
from app.ui.components.character_tile import CharacterTile

KV = """
MDScreen:
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "PlayerTile Demo"
            md_bg_color: 0.2, 0.5, 0.7, 1
            elevation: 10

        ScrollView:
            GridLayout:
                id: grid
                cols: 2
                padding: dp(12)
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
"""

class PlayerTileApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        screen = Builder.load_string(KV)
        grid = screen.ids.grid

        # Beispiel-Tiles hinzufügen
        players = [
            {"name": "Julia & Julie", "img": "app/assets/img/twoplayer.png"},
            {"name": "Max & Anna", "img": "app/assets/img/comingsoon.png"},
            {"name": "John & Jane", "img": "app/assets/img/twoplayer.png"},
        ]

        for player in players:
            tile = CharacterTile(
                tile_text=player["name"],
                tile_source=player["img"],
                tile_size=[160, 360],
                show_icons=True
            )
            grid.add_widget(tile)

        return screen

if __name__ == "__main__":
    PlayerTileApp().run()
