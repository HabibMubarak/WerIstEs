from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

# Importiere ScreenManager-Setup aus deiner App
from app.ui import register_screens, PRIMARY_PALETTE, THEME_STYLE # kümmert sich um das Hinzufügen der Screens
import json


class AnimeWerIstDasApp(MDApp):
    def build(self):
        self.title = "Anime Wer ist das?"
        self.theme_cls.primary_palette = PRIMARY_PALETTE  # Palette bleibt nötig, z.B. für Buttons
        self.theme_cls.theme_style = THEME_STYLE

        sm = ScreenManager()
        register_screens(sm)  # Screens werden hier hinzugefügt
        return sm

if __name__ == "__main__":
    AnimeWerIstDasApp().run()
