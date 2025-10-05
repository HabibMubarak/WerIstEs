from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
import threading
import json
import requests
import os
import time

from kivy.lang import Builder
Builder.load_file("app/ui/waiting_room_screen.kv")


class WaitingRoomScreen(MDScreen):
    waiting_text = StringProperty("Warte auf Spieler…")
    player_count_text = StringProperty("Spieler verbunden: 1/2")
    room_id = None
    data = json.load(open(f"app/assets/settings/profil.json", encoding="utf-8"))

    MATCHMAKING_ENDPOINT = "https://68dfa70f000bcf6090ee.fra.appwrite.run/v1/functions"
    MATCHMAKING_ID = "68e03839a3b320f02bde"
    API_KEY = os.getenv("APPWRITE_API_KEY")
    USER_ID = data["name"]

    POLL_INTERVAL = 2  # Sekunden

    def on_pre_enter(self):
        # Starte das Polling in einem separaten Thread
        threading.Thread(target=self.poll_matchmaking, daemon=True).start()

    def poll_matchmaking(self):
        url = f"{self.MATCHMAKING_ENDPOINT}/{self.MATCHMAKING_ID}/executions"
        headers = {
            "X-Appwrite-Key": self.API_KEY,
            "Content-Type": "application/json"
        }
        payload = lambda: json.dumps({"userId": self.USER_ID})

        while True:
            try:
                response = requests.post(url, headers=headers, data=payload(), timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    room = data.get("room", {})
                    players = room.get("players", [])

                    # Player Count aktualisieren
                    self.update_player_count(len(players))

                    # Wenn Raum gestartet ist, Screen wechseln
                    print("state:", room.get("state"))
                    if room.get("state") == "started":
                        if self.room_id != room.get("roomId"):  # nur einmal wechseln
                            self.room_id = room.get("roomId")
                            Clock.schedule_once(lambda dt: setattr(self.manager, "current", "twoplayer"))
                        # Polling-Thread kann jetzt abbrechen
                        break
                else:
                    print("Fehler vom Server:", response.text)
            except Exception as e:
                print("Fehler beim Matchmaking-Poll:", e)

            time.sleep(self.POLL_INTERVAL)


    def update_player_count(self, count):
        Clock.schedule_once(lambda dt: self._update_player_count(count))

    def _update_player_count(self, count):
        self.player_count_text = f"Spieler verbunden: {count}/2"

    def show_connection_error(self):
        self.player_count_text = "Server nicht erreichbar"
        self.waiting_text = "Bitte überprüfe die Serververbindung"

    def go_back(self):
        self.manager.current = "menu"
