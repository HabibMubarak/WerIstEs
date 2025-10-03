from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.animation import Animation
from app.core.character import Character
from .components.anime_list_item import AnimeListItem
from .components.check_box_item import RightCheckBox
import json
import os

Builder.load_file(r"app/ui/anime_selection_screen.kv")

class AnimeSelectionScreen(MDScreen):
    selected_items = set()

    def on_pre_enter(self):

        character_manager = Character()
        lang = json.load(open("app/assets/settings/profil.json", encoding="utf-8"))["lang"]
        self.anime_data = character_manager.get_anime_details(lang)
        self.create_list()

    def create_list(self):
        self.ids.anime_list.clear_widgets()

        # bekannte Animes aus profil.json laden
        profile_path = r"app/assets/settings/profil.json"
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                profile_data = json.load(f)
                known_animes = set(profile_data.get("known_animes", []))
        else:
            known_animes = set()

        # Liste aufbauen
        for anime in self.anime_data:
            item = AnimeListItem(text=anime["title"], icon=anime["img"])
            item.checkbox.bind(active=self.on_checkbox_active)
            self.ids.anime_list.add_widget(item)

            # falls Anime schon in profil.json drin → Checkbox setzen + set hinzufügen
            if anime["title"] in known_animes:
                item.checkbox.active = True
                self.selected_items.add(anime["title"])

    def on_checkbox_active(self, checkbox, value):
        anime_name = checkbox.anime_name
        if value:
            self.selected_items.add(anime_name)
        else:
            self.selected_items.discard(anime_name)

        # Button ein- oder ausblenden
        if self.selected_items:
            self.show_confirm_button()
        else:
            self.hide_confirm_button()

    def show_confirm_button(self):
        topbar = self.ids.topbar
        if not topbar.right_action_items:
            topbar.right_action_items = [["check", lambda x: self.confirm_selection(), "check"]]
            

    def hide_confirm_button(self):
        topbar = self.ids.topbar
        if topbar.right_action_items:
            anim = Animation(opacity=1, d=0.3)
            anim.bind(on_complete=lambda *args: setattr(topbar, "right_action_items", []))
            anim.start(topbar)

    def confirm_selection(self):
        print("Ausgewählte Animes:", self.selected_items)
        self.known_animes(self.selected_items)
        self.selected_items.clear()
        # Checkboxes zurücksetzen
        for child in self.ids.anime_list.children:
            child.checkbox.active = False
        self.hide_confirm_button()
        self.manager.current = "menu"

    
    def known_animes(self, anime_names):
        profile_path = r"app/assets/settings/profil.json"

        # Prüfen, ob die Datei existiert
        if os.path.exists(profile_path):
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            # Wenn Datei nicht existiert, Standardstruktur erstellen
            data = {"name": "", "lang": "en", "known_animes": []}

        # vorhandene Liste überschreiben
        data["known_animes"] = list(anime_names)

        # Zurückschreiben
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
