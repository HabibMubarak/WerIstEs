from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen

# Lade die .kv-Datei manuell
Builder.load_file("app/ui/twoplayer_screen.kv")

class TwoPlayerScreen(MDScreen):

    anime_data = [
        {"title": "Naruto", "desc": "Ninja-Abenteuer", "img": "app/assets/img/naruto.png"},
        {"title": "One Piece", "desc": "Piraten-Abenteuer", "img": "app/assets/img/onepiece.png"},
        {"title": "Attack on Titan", "desc": "Titanen-Apokalypse", "img": "app/assets/img/aot.png"},
        {"title": "My Hero Academia", "desc": "Superhelden-Schule", "img": "app/assets/img/mha.png"},
        {"title": "Demon Slayer", "desc": "Dämonenjäger", "img": "app/assets/img/demonslayer.png"},
        {"title": "Fullmetal Alchemist", "desc": "Alchemie-Abenteuer", "img": "app/assets/img/fma.png"},
        {"title": "Death Note", "desc": "Psychothriller", "img": "app/assets/img/deathnote.png"},
        {"title": "Dragon Ball Z", "desc": "Kämpfe & Abenteuer", "img": "app/assets/img/dbz.png"},
    ]
    
    def on_pre_enter(self):
        # Vor dem Anzeigen der Seite füllen
        self.fill_view()

    def fill_view(self):
        anime_list_layout = self.ids.anime_list
        anime_list_layout.clear_widgets()

        for anime in self.anime_data:
            # ListItem erstellen
            item = TwoLineAvatarListItem(
                text=anime["title"],
                secondary_text=anime["desc"],
                on_release=lambda x, title=anime["title"]: self.selcect_anime(title))
            # Avatar-Bild hinzufügen
            avatar = ImageLeftWidget(source=anime["img"])
            item.add_widget(avatar)
            anime_list_layout.add_widget(item)


    def on_back_pressed(self):
        if self.manager.current != "menu":
            self.manager.current = "menu"

    def selcect_anime(self, anime_title):
        self.manager.get_screen("select_character").selected_anime = anime_title
        self.manager.current = "select_character"
        print(f"Anime ausgewählt: {anime_title}")

    def search(self):
        # Hier kann eine Suchfunktion implementiert werden
        print("Suche gestartet")