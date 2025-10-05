# ReadyScreen.py

import time
import threading
import requests
from kivy.clock import mainthread
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.lang import Builder
import json

Builder.load_file("app/ui/ready_screen.kv")

class ReadyScreen(MDScreen):
    room_id = ""
    check_room_endpoint = "https://68e2990a000acf33f158.fra.appwrite.run/v1/functions/68e2999f2a69d286b57d/executions"
    
    status_text = StringProperty("Warten auf deinen Gegner...")
    you_ready = BooleanProperty(False)
    opponent_ready = BooleanProperty(False)
    
    player_color = ListProperty([0.2, 0.2, 0.2, 1])
    opponent_color = ListProperty([0.2, 0.2, 0.2, 1])
    
    def on_enter(self):
        self.you_ready = True
        self.player_color = [0.15, 0.4, 0.2, 1]
        self.status_text = "Du bist bereit!"
        
        threading.Thread(target=self.poll_room_state, daemon=True).start()

    def poll_room_state(self):
        while True:
            try:
                payload = {"roomId": self.room_id}
                response = requests.post(self.check_room_endpoint, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    both_ready = data.get("both_ready", False)
                    state = data.get("state", "waiting")
                    self.opponent_ready = both_ready
                    self.opponent_color = [0.15, 0.4, 0.2, 1] if both_ready else [0.2, 0.2, 0.2, 1]

                    # Charaktere extrahieren (nur name & img)
                    char_data = data.get("character_data", {})
                    characters = []
                    for key, value in char_data.items():
                        if key == "random":
                            characters.extend(value)
                        else:
                            characters.append(value)

                    # Übergabe an GameFieldScreen, wenn beide ready
                    if both_ready and state == "ready":
                        self.update_ui("Beide sind bereit! Spiel startet...")
                        self.switch_to_game_field(characters)
                        break
                    else:
                        self.update_ui("Warten auf Gegner...")
                else:
                    self.update_ui("Fehler beim Abrufen des Room-Status")
            except Exception as e:
                print("[ERROR] Polling Fehler:", e)
                self.update_ui("Verbindung verloren...")
            time.sleep(3)

    @mainthread
    def update_ui(self, text):
        self.status_text = text

    @mainthread
    def switch_to_game_field(self, characters):
        """Wechselt zum GameFieldScreen und übergibt die Charaktere"""
        game_screen = self.manager.get_screen("game_field")
        game_screen.available_chars = characters  # direkt übergeben
        self.manager.transition.direction = "left"
        self.manager.current = "game_field"
