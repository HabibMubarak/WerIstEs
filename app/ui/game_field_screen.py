from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from .components.tab import Tab
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from .components.character_tile import CharacterTile
from kivy.properties import ObjectProperty,ListProperty,StringProperty
from app.core.character import Character
import random
import socket
import threading
from kivy.clock import Clock
import ast


Builder.load_file(r"app/ui/game_field_screen.kv")


class GameFieldScreen(MDScreen):

    dialog: MDDialog = None
    send_btn = ObjectProperty(None)
    available_chars = ListProperty([])
    eliminated_chars = ListProperty([])
    selected_character = StringProperty("")
    client_socket = None
    is_my_turn = True # oder True, je nach Spieler


    def on_enter(self):
        self.connect_to_server(host="127.0.0.1", port=5000)  # IP vom Server
        self.init_field(total=24)
        self.set_send_button_enabled(self.is_my_turn)

    def init_field(self, total=24):
        """Füllt available_chars auf insgesamt `total` Charaktere auf, ohne Duplikate, und mischt sie."""
        current_count = len(self.available_chars)

        while current_count < total:
            comom_animes = []
            new_chars = self.get_random_characters(comom_animes)
            for char in new_chars:
                if current_count >= total:
                    break
                if not any(c["name"] == char["name"] for c in self.available_chars):
                    self.available_chars.append(char)
                    current_count += 1

        # Zufällig mischen
        random.shuffle(self.available_chars)

        # RecycleView aktualisieren
        self.ids.rv_available.data = [
            {
                "tile_text": char["name"],
                "tile_source": char["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": False,
                "tile_left_icon": "thumb-down",
                "tile_right_icon": "thumb-up",
                "on_eliminate": self.move_to_eliminated,
                "on_thumb_up_message": self.send_message
            }
            for char in self.available_chars
        ]

        self.ids.rv_eliminated.data = [
            {
                "tile_text": char["name"],
                "tile_source": char["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": True,
                "tile_left_icon": "undo",
                "on_undo": self.move_to_available
            }
            for char in self.eliminated_chars
        ]
    def on_leave(self):
        """Wird aufgerufen, wenn der Screen verlassen wird."""
        self.available_chars.clear()
        self.eliminated_chars.clear()
        self.ids.rv_available.data = []
        self.ids.rv_eliminated.data = []

    def get_random_characters(self, comon_animes):

        comon_animes = [
            "Attack on Titan (Shingeki no Kyojin)",
            "One Piece",
            "Naruto / Naruto Shippuden"
            ]
        char_manager = Character()
        random_character = char_manager.get_random_characters_with_images(comon_animes, 12)
        
        
        return random_character

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        """Wird aufgerufen, wenn ein Tab gewechselt wird."""
        if tab_text == "Verfügbar":
            self.populate_available()
        elif tab_text == "Ausgeschieden":
            self.populate_eliminated()
    
    def populate_available(self):
        """Füllt den 'Verfügbar'-Tab mit Buttons für jeden Charakter."""
        container = self.ids.available_characters
        container.clear_widgets()  # alte Widgets löschen

        for player in self.available_chars:
            tile = CharacterTile(
                tile_text=player["name"],
                tile_source=player["img"],
                tile_size=[160, 360],
                show_icons=True,
                on_eliminate=self.move_to_eliminated
            )
            container.add_widget(tile)

    def populate_eliminated(self):
        """Füllt den 'Ausgeschieden'-Tab mit Buttons für jeden Charakter."""
        container = self.ids.eliminated_characters
        container.clear_widgets()  # alte Widgets löschen

        for player in self.eliminated_chars:
            tile = CharacterTile(
                tile_text=player["name"],
                tile_source=player["img"],
                tile_size=[160, 360],
                show_icons=True,
                on_eliminate=None
            )
            container.add_widget(tile)

    def send_message(self,msg):
        print(msg)
        self.send_question(msg)
        self.ids.input_field.text = ""
        self.set_send_button_enabled(False)

    def show_receive_dialog(self, msg):
        """Dialog öffnen, wenn Gegner eine Frage stellt."""
        dialog = MDDialog(
            title="Frage von Gegner",
            text=msg,
            auto_dismiss=False,
            buttons=[
                MDFlatButton(text="Ja", on_release=lambda x: self.send_answer("Ja", dialog)),
                MDFlatButton(text="Nein", on_release=lambda x: self.send_answer("Nein", dialog)),
                MDFlatButton(text="Ich weiß nicht", on_release=lambda x: self.send_answer("Ich weiß nicht", dialog)),
            ],
        )
        dialog.open()

        # Jetzt bist du **nicht** am Zug → Button deaktivieren
        self.set_send_button_enabled(True)
        self.is_my_turn = True

    def send_answer(self, answer, dialog):
        """Antwort senden und Dialog schließen."""
        if self.client_socket:
            try:
                self.client_socket.sendall(f"ANSWER|{answer}".encode("utf-8"))
            except Exception as e:
                print("Fehler beim Antworten:", e)
        dialog.dismiss()
        # Nach einer Antwort ist der Gegner wieder dran



    def on_dialog_answer(self, answer, dialog):
        print(f"Antwort gewählt: {answer}")
        dialog.dismiss()

    
    def set_send_button_enabled(self, enabled: bool):
        """Aktiviert oder deaktiviert den Senden-Button."""
        self.ids.send_btn.disabled = not enabled

    
    # Callback für CharacterTile
    def move_to_eliminated(self, name):
        # passenden Char finden
        char = next((c for c in self.available_chars if c["name"] == name), None)
        if not char:
            return

        # aus "Verfügbar" rausnehmen und in "Ausgeschieden" verschieben
        self.available_chars.remove(char)
        self.eliminated_chars.append(char)

        # RecycleView aktualisieren
        # available
        self.ids.rv_available.data = [
            {
                "tile_text": c["name"],
                "tile_source": c["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": False,           # alle verfügbare Tiles: beide Icons
                "tile_left_icon": "thumb-down",
                "tile_right_icon": "thumb-up",
                "on_eliminate": self.move_to_eliminated,
                "on_thumb_up_message": self.send_message
            }
            for c in self.available_chars
        ]


        # eliminated → Icons ausblenden
        self.ids.rv_eliminated.data = [
            {
                "tile_text": c["name"],
                "tile_source": c["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": True,            # nur links Undo
                "tile_left_icon": "undo",
                "on_undo": self.move_to_available
            }
            for c in self.eliminated_chars
        ]

        # Force refresh
        self.ids.rv_available.refresh_from_data()
        self.ids.rv_eliminated.refresh_from_data()
    
    def move_to_available(self, name):
        """Charakter aus 'Ausgeschieden' zurück in 'Verfügbar'."""
        char = next((c for c in self.eliminated_chars if c["name"] == name), None)
        if not char:
            return

        self.eliminated_chars.remove(char)
        self.available_chars.append(char)

        # RecycleViews aktualisieren
        self.ids.rv_available.data = [
            {
                "tile_text": c["name"],
                "tile_source": c["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": False,           # wieder beide Icons sichtbar
                "tile_left_icon": "thumb-down",
                "tile_right_icon": "thumb-up",
                "on_eliminate": self.move_to_eliminated,
                "on_thumb_up_message": self.send_message
            }
            for c in self.available_chars
        ]

        self.ids.rv_eliminated.data = [
            {
                "tile_text": c["name"],
                "tile_source": c["img"],
                "tile_size": [160, 360],
                "show_icons": True,
                "left_only": True,            # nur links Undo
                "tile_left_icon": "undo",
                "on_undo": self.move_to_available
            }
            for c in self.eliminated_chars
        ]
        self.ids.rv_available.refresh_from_data()
        self.ids.rv_eliminated.refresh_from_data()


    def connect_to_server(self, host, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            print("Mit Server verbunden!")
            self.set_send_button_enabled(True)  # erst aktivieren, wenn verbunden
            threading.Thread(target=self.listen_for_messages, daemon=True).start()
        except Exception as e:
            print("Verbindung fehlgeschlagen:", e)
            self.client_socket = None

    def listen_for_messages(self):
        while True:
            try:
                msg = self.client_socket.recv(4096).decode("utf-8")
                if msg:
                    parts = msg.split("|", 1)
                    if parts[0] == "QUESTION":
                        Clock.schedule_once(lambda dt: self.show_receive_dialog(parts[1]))
                    elif parts[0] == "ANSWER":
                        Clock.schedule_once(lambda dt: self.show_answer(parts[1]))
                    elif parts[0] == "CHARACTERS":
                        # Hier kommt die Charakterliste vom Server
                        import ast
                        chars = ast.literal_eval(parts[1])  # in echte Liste umwandeln
                        Clock.schedule_once(lambda dt: self.set_characters(chars))
            except:
                break

    def show_answer(self, answer):
        """Antwort vom Gegner anzeigen."""
        dialog = MDDialog(
            title="Antwort erhalten",
            text=f"Gegner: {answer}",
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ],
        )
        dialog.open()

        # Jetzt bist DU wieder am Zug
        self.is_my_turn = False
        self.set_send_button_enabled(False)

    def send_question(self, msg):
        """Spieler stellt eine Frage."""
        if self.is_my_turn and self.client_socket:
            try:
                # Prefix QUESTION
                self.client_socket.sendall(f"QUESTION|{msg}".encode("utf-8"))
                self.is_my_turn = False
                self.set_send_button_enabled(False)
            except Exception as e:
                print("Fehler beim Senden:", e)

        # eigenen Button sperren bis Antwort kommt
        self.ids.input_field.text = ""
