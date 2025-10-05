from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from app.ui.components.game_card import GameCard
from kivy.core.window import Window
from app.core.character import Character
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.uix.screenmanager import SlideTransition

import os, json, requests

Builder.load_file("app/ui/select_character.kv")


class SelectCharacter(MDScreen):
    selected_anime = ""
    selected_character = ""
    dialog: MDDialog = None

    # Appwrite Setup
    data = json.load(open(f"app/assets/settings/profil.json", encoding="utf-8"))

    SELECT_CHARACTER_ENDPOINT = "https://68e25f6a002383add63d.fra.appwrite.run/v1/functions"
    SELECT_CHARACTER_ID = "68e25f6a001c6321f9e9"
    API_KEY = os.getenv("APPWRITE_API_KEY")
    USER_ID = data["name"]

    def on_pre_enter(self):
        self.ids.select_anime_top_bar.title = self.selected_anime
        self.fill_recycleview()
        Clock.schedule_once(lambda dt: self.scroll_to_start(), 0)

    def scroll_to_start(self):
        if hasattr(self.ids.rv, "scroll_x"):
            self.ids.rv.scroll_x = 0

    def fill_recycleview(self):
        card_width = Window.width
        card_height = Window.height * 0.8
        self.ids.rv.size_hint = (None, None)
        self.ids.rv.size = (Window.width, card_height)
        self.ids.rv.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        self.ids.rv.layout_manager.default_size = (card_width, card_height)
        self.ids.rv.layout_manager.default_size_hint = (None, None)

        data = []
        character_manger = Character()
        names = character_manger.get_characters_by_anime(self.selected_anime)
        for name in names:
            data.append({
                "title": f"{name}",
                "bg_image": character_manger.get_image_url_for_character(name),
                "available": True,
                "on_release": lambda x=name: self.character_clicked(x)
            })
        self.ids.rv.data = data

    def character_clicked(self, name):
        self.selected_character = name
        if not self.dialog:
            self.dialog = MDDialog(
                title="Charakter auswählen",
                text=f"Möchtest du wirklich {name} auswählen?",
                buttons=[
                    MDFlatButton(text="ABBRECHEN", on_release=self.dismiss_dialog),
                    MDFlatButton(text="JA", on_release=self.confirm_character),
                ],
            )
        else:
            self.dialog.text = f"Möchtest du wirklich {name} auswählen?"
        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    def confirm_character(self, *args):
        self.dialog.dismiss()
        print(f"[INFO] Charakter bestätigt: {self.selected_character}")

        try:
            payload = {
                "roomId": self.manager.get_screen("waiting_room").room_id,
                "userId": self.USER_ID,
                "character": {
                    "name": self.selected_character,
                    "img": Character().get_image_url_for_character(self.selected_character)
                }
            }

            # POST an Appwrite Function – kein API-Key nötig
            response = requests.post(
                url = f"{self.SELECT_CHARACTER_ENDPOINT}/{self.SELECT_CHARACTER_ID}/executions",
                json=payload,  # JSON Body
                timeout=10
            )

            if response.status_code == 200:
                print("[DEBUG] Charakter erfolgreich gesendet")
                ready_screen = self.manager.get_screen("ready")
                ready_screen.room_id = payload["roomId"]
                ready_screen.user_id = self.USER_ID  # optional für Polling
                self.ready()
            else:
                print("[ERROR] Funktion returned:", response.status_code, response.text)

        except Exception as e:
            print("[ERROR] Fehler beim Senden:", e)

        

    def ready(self):
        """Wechselt zum Spielfeld."""
        self.manager.transition.direction = "left"
        self.manager.current = "ready"

    def on_back_pressed(self):
        if self.manager.current != "twoplayer":
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "twoplayer"
