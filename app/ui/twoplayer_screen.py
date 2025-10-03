from app.core.character import Character
import json
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty


# Lade die .kv-Datei manuell
Builder.load_file("app/ui/twoplayer_screen.kv")

class TwoPlayerScreen(MDScreen):
    select_anime = StringProperty("")
    def on_pre_enter(self):
        # Vor dem Anzeigen der Seite füllen
        character_manager = Character()
        lang = json.load(open("app/assets/settings/profil.json", encoding="utf-8"))["lang"]
        self.anime_data = character_manager.get_anime_details(lang)
        self.fill_view()
        self.lang = json.load(open("app/assets/settings/profil.json", encoding="utf-8"))["lang"]
        data = json.load(open(f"app/assets/lang/{self.lang}.json", encoding="utf-8"))

        # Labels aus JSON laden
        self.select_anime = data["twoplayer"]["select_anime"]

    def fill_view(self):
        anime_list_layout = self.ids.anime_list
        anime_list_layout.clear_widgets()

        for anime in self.anime_data:
            item = TwoLineAvatarListItem(
                text=anime["title"],
                secondary_text=anime["desc"],
                on_release=lambda x, title=anime["title"]: self.selcect_anime(title)
            )
            item.md_bg_color = (0, 0, 0, 0)  # transparenter Hintergrund
            # Avatar-Bild asynchron laden (fixe Größe, kein Strecken)
            avatar_img = AsyncImage(
                source=anime["img"],
                size_hint=(None, None),       # wichtig: automatische Skalierung deaktivieren
                size=(dp(38), dp(38)),    
                allow_stretch=True,
                keep_ratio=False
            )
            avatar_img.bind(on_error=lambda inst, err: print("Fehler beim Laden:", err))
            avatar = ImageLeftWidget()
            avatar.add_widget(avatar_img)
            item.add_widget(avatar)

            anime_list_layout.add_widget(item)

    def on_back_pressed(self):
        if self.manager.current == "twoplayer":
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "menu"
        elif self.manager.current == "select_character":
            self.manager.transition = SlideTransition(direction="left")
            self.manager.current = "menu"
        elif self.manager.current != "menu":
            self.manager.current = "menu"

    def selcect_anime(self, anime_title):
        self.manager.get_screen("select_character").selected_anime = anime_title
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "select_character"
        print(f"Anime ausgewählt: {anime_title}")

    def search(self):
        # Hier kann eine Suchfunktion implementiert werden
        print("Suche gestartet")
    
    def go_to_settings(self):
        setting_screen = self.manager.get_screen("setting")
        setting_screen.previous_screen = self.manager.current  # merken
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "setting"