from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy import platform
# Importiere ScreenManager-Setup aus deiner App
from app.ui import register_screens, PRIMARY_PALETTE, THEME_STYLE # kümmert sich um das Hinzufügen der Screens
import json

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission  # pylint: disable=import-error # type: ignore
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE,
                        Permission.CAMERA,
                        ])

class AnimeWerIstDasApp(MDApp):
    def build(self):
        self.title = "Anime Wer ist das?"
        self.theme_cls.primary_palette = PRIMARY_PALETTE  # Palette bleibt nötig, z.B. für Buttons
        self.theme_cls.theme_style = THEME_STYLE

        sm = ScreenManager()
        register_screens(sm)  # Screens werden hier hinzugefügt
        return sm
    
    def on_enter(self):
        # Berechtigungen für Android anfragen
        if platform == "android":
            print("Berechtigungen werden angefragt...")
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.CAMERA,
                Permission.FLASHLIGHT,
            ])
            print("Berechtigungen wurden angefragt.")

if __name__ == "__main__":
    AnimeWerIstDasApp().run()
