from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty
from kivymd.uix.list import OneLineListItem
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelOneLine
from kivy.uix.boxlayout import BoxLayout
import json
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField

Builder.load_file("app/ui/setting_screen.kv")


class SettingScreen(MDScreen):
    previous_screen = "menu"

    # Properties für Übersetzungen
    setting = StringProperty("")
    edit_profil = StringProperty("")
    change_lang = StringProperty("")
    notification = StringProperty("")
    about = StringProperty("")
 
    dialog = None
    def on_pre_enter(self):
        self.lang = json.load(open("app/assets/settings/profil.json", encoding="utf-8"))["lang"]
        data = json.load(open(f"app/assets/lang/{self.lang}.json", encoding="utf-8"))

        # Labels aus JSON laden
        self.setting = data["setting"]["setting"]
        self.edit_profil = data["setting"]["edit_profil"]["title"]
        self.change_name = data["setting"]["edit_profil"]["change_name"]
        self.enter_new_name = data["setting"]["edit_profil"]["enter_new_name"]
        self.exit = data["setting"]["edit_profil"]["exit"]
        self.save = data["setting"]["edit_profil"]["save"]
        self.name_taken = data["setting"]["edit_profil"]["name_taken"]
        self.name_empty = data["setting"]["edit_profil"]["name_empty"]
        self.change_known_animes = data["setting"]["edit_profil"]["change_known_animes"]

        self.change_lang = data["setting"]["change_lang"]["title"]
        self.lang_de = data["setting"]["change_lang"]["de"]
        self.lang_en = data["setting"]["change_lang"]["en"]

        self.notification = data["setting"]["notification"]["title"]
        self.notification_on = data["setting"]["notification"]["on"]
        self.notification_off = data["setting"]["notification"]["off"]

        self.about = data["setting"]["about"]["title"]
        self.version = data["setting"]["about"]["version"]
        self.instagram = data["setting"]["about"]["instagram"]

        self.create_panels()

    def create_panels(self):
        """Dynamisch alle Panels erstellen und Unteroptionen hinzufügen."""
        self.ids.settings_list.clear_widgets()

        settings = {
            self.edit_profil: [(self.change_name, self.change_name_action), (self.change_known_animes, self.change_anime_list)],
            self.change_lang: [
                (self.lang_de, self.change_lang_to_de),
                (self.lang_en, self.change_lang_to_en)
            ],
            self.notification: [
                (self.notification_on, self.enable_notifications),
                (self.notification_off, self.disable_notifications)
            ],
            self.about: [
                (self.version, self.show_version),
                (self.instagram, self.open_instagram)
            ]
        }

        icons = {
            self.edit_profil: "account",
            self.change_lang: "translate",
            self.notification: "bell",
            self.about: "information"
        }

        for title, sub_opts in settings.items():
            panel = MDExpansionPanel(
                icon=icons[title],
                panel_cls=MDExpansionPanelOneLine(text=title),
                content=self.build_panel_content(sub_opts)
            )
            self.ids.settings_list.add_widget(panel)

    def build_panel_content(self, options):
        """Erstellt ein BoxLayout mit OneLineListItems als Unteroptionen."""
        layout = BoxLayout(orientation="vertical", size_hint_y=None)
        layout.bind(minimum_height=layout.setter("height"))

        for opt, callback in options:
            item = OneLineListItem(text=opt, on_release=lambda x, cb=callback: cb())
            layout.add_widget(item)

        return layout

    # ------------------- OPTIONEN ALS FUNKTIONEN -------------------

    def change_name_action(self):
        # Aktuellen Namen aus profil.json laden
        with open("app/assets/settings/profil.json", encoding="utf-8") as f:
            self.profil_data = json.load(f)
        
        current_name = self.profil_data.get("name", "")

        # MDTextField für neue Eingabe
        self.name_input = MDTextField(
            text=current_name,
            hint_text=self.enter_new_name,
            size_hint_x=0.9,
            pos_hint={"center_x": 0.5},
            helper_text="",
            helper_text_mode="on_error"
        )

        # Dialog erstellen
        self.dialog = MDDialog(
            title=self.change_name,
            type="custom",
            content_cls=self.name_input,
            buttons=[
                MDFlatButton(
                    text=self.exit, 
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDFlatButton(
                    text=self.save,
                    on_release=lambda x: self.validate_and_save_name()
                )
            ],
        )
        self.dialog.open()

    def validate_and_save_name(self):
        new_name = self.name_input.text.strip()
        
        # Liste aller bereits existierenden Namen (kann später aus JSON geladen werden)
        all_names = ["Max", "Anna", "aa"]  
        current_name = self.profil_data.get("name", "")

        # Prüfen, ob Name leer ist
        if not new_name:
            self.name_input.error = True
            self.name_input.helper_text = self.name_empty
            return  # Dialog bleibt geöffnet

        # Prüfen, ob Name bereits existiert
        if new_name in all_names and new_name != current_name:
            self.name_input.error = True
            self.name_input.helper_text = self.name_taken
            return  # Dialog bleibt geöffnet

        # Name ist gültig, speichern und Dialog schließen
        self.profil_data["name"] = new_name
        with open("app/assets/settings/profil.json", "w", encoding="utf-8") as f:
            json.dump(self.profil_data, f, ensure_ascii=False, indent=4)
        
        print(f"Name erfolgreich geändert zu: {new_name}")
        self.dialog.dismiss()  # Dialog nur hier schließen
        self.on_pre_enter()  # Bildschirm neu laden


    
    def change_anime_list(self):
        self.manager.current = "anime_selection"

    def change_lang_to_de(self):
        print("Sprache auf Deutsch umstellen")
        self.set_language("de")

    def change_lang_to_en(self):
        print("Sprache auf Englisch umstellen")
        self.set_language("en")

    def enable_notifications(self):
        print("Benachrichtigungen aktiviert!")

    def disable_notifications(self):
        print("Benachrichtigungen deaktiviert!")

    def show_version(self):
        print("App-Version anzeigen (Popup oder Dialog)")

    def open_instagram(self):
        print("Instagram-Link öffnen")

    # Hilfsfunktion, um Sprache zu wechseln
    def set_language(self, lang):
        with open("app/assets/settings/profil.json", "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["lang"] = lang
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()
        print(f"Sprache auf {lang} gesetzt")
        self.on_pre_enter()  # Bildschirm neu laden
        
    def on_back_pressed(self):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = self.previous_screen
