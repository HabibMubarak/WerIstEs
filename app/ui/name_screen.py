from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
import json
import os

# Lade die .kv-Datei manuell
Builder.load_file("app/ui/name_screen.kv")
profil_path = "app/assets/settings/profil.json"

class NameScreen(MDScreen):
    all_names = []

    # Sprache der App laden
    if os.path.exists(profil_path):
        with open(profil_path, "r", encoding="utf-8") as f:
            profil_data = json.load(f)
    else:
        profil_data = {"lang": "de"}  # Standard: Deutsch

    lang = profil_data.get("lang", "de")
    data = json.load(open(f"app/assets/lang/{lang}.json", encoding="utf-8"))

    # Texte aus der Sprachdatei laden
    welcome = data["name"]["welcome"]
    entername = data["name"]["entername"]
    namehint = data["name"]["namehint"]
    namefield = data["name"]["namefield"]
    next = data["name"]["next"]
    error_long_name = data["name"]["error_long_name"]
    error_empty_name = data["name"]["error_empty_name"]
    error_name_taken = data["name"]["error_name_taken"]

    def set_language(self, lang):
        """Sprache ändern und speichern."""
        self.lang = lang
        try:
            with open(profil_path, "r", encoding="utf-8") as f:
                profil_data = json.load(f)
        except FileNotFoundError:
            profil_data = {}
        
        profil_data["lang"] = lang
        with open(profil_path, "w", encoding="utf-8") as f:
            json.dump(profil_data, f, ensure_ascii=False, indent=4)

        # Texte neu laden
        self.data = json.load(open(f"app/assets/lang/{lang}.json", encoding="utf-8"))
        self.welcome = self.data["name"]["welcome"]
        self.entername = self.data["name"]["entername"]
        self.namehint = self.data["name"]["namehint"]
        self.namefield = self.data["name"]["namefield"]
        self.next = self.data["name"]["next"]
        self.error_long_name = self.data["name"]["error_long_name"]
        self.error_empty_name = self.data["name"]["error_empty_name"]
        self.error_name_taken = self.data["name"]["error_name_taken"]

        # UI sofort aktualisieren
        self.ids.welcome_label.text = self.welcome
        self.ids.entername_label.text = self.entername
        self.ids.name_hint.text = self.namehint
        self.ids.name_field.hint_text = self.namefield
        self.ids.next_button.text = self.next

        # Flaggen visuell aktualisieren
        self.ids.flag_de.opacity = 1 if lang == "de" else 0.5
        self.ids.flag_en.opacity = 1 if lang == "en" else 0.5

    def check_name(self):
        name = self.ids.name_field.text.strip()
        text_field = self.ids.name_field

        # Validierung
        if len(name) > 10:
            text_field.error = True
            text_field.helper_text = self.error_long_name
            text_field.helper_text_mode = "on_error"
            return False
        if not name:
            text_field.error = True
            text_field.helper_text = self.error_empty_name
            text_field.helper_text_mode = "on_error"
            return False
        elif name in self.all_names:
            text_field.error = True
            text_field.helper_text = self.error_name_taken
            text_field.helper_text_mode = "on_error"
            return False
        else:
            text_field.error = False
            text_field.helper_text = ""

            try:
                with open(profil_path, "r", encoding="utf-8") as f:
                    profil_data = json.load(f)
            except FileNotFoundError:
                profil_data = {}

            profil_data["name"] = name

            with open(profil_path, "w", encoding="utf-8") as f:
                json.dump(profil_data, f, ensure_ascii=False, indent=4)

            return True
