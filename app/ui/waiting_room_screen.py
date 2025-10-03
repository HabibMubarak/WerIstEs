from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.clock import Clock
import threading
import socket

from app.core.character import Character
from kivy.lang import Builder

Builder.load_file("app/ui/waiting_room_screen.kv")

class WaitingRoomScreen(MDScreen):
    waiting_text = StringProperty("Warte auf Spieler…")
    player_count_text = StringProperty("Spieler verbunden: 1/2")
    room_id = None  # wird vom Server gesetzt

    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5000

    def on_pre_enter(self):
        threading.Thread(target=self.connect_to_server, daemon=True).start()

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.SERVER_IP, self.SERVER_PORT))
            print("[VERBUNDEN] Zum Warteraum-Server")
            # Listener-Thread starten
            threading.Thread(target=self.listen_to_server, daemon=True).start()
        except Exception as e:
            print("Fehler beim Verbinden:", e)
            Clock.schedule_once(lambda dt: self.show_connection_error())

    def listen_to_server(self):
        """
        Hört auf Nachrichten vom Server und reagiert darauf.
        """
        buffer = ""
        try:
            while True:
                data = self.sock.recv(1024).decode("utf-8")
                if not data:
                    print("Verbindung zum Server beendet")
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.process_server_message(line.strip())
        except Exception as e:
            print("Verbindung verloren:", e)
            Clock.schedule_once(lambda dt: self.show_connection_error())

    def process_server_message(self, msg: str):
        if msg.startswith("PLAYER_COUNT"):
            try:
                count = int(msg.split()[1])
                self.update_player_count(count)
            except Exception:
                print("Fehler beim Parsen von PLAYER_COUNT:", msg)

        elif msg.startswith("START_GAME"):
            # z. B. "START_GAME ab12cd34"
            parts = msg.split()
            if len(parts) >= 2:
                self.room_id = parts[1]

                print(f"[START_GAME] Room {self.room_id} → Wechsel zur Charakterauswahl")

                # Direkt ins TwoPlayerScreen (Anime-Auswahl) wechseln
                Clock.schedule_once(lambda dt: setattr(self.manager, "current", "twoplayer"))
            else:
                print("START_GAME Nachricht unvollständig:", msg)


    def switch_to_game(self, dt):
        """
        Screenwechsel ins Spielfeld (twoplayer).
        """
        if self.manager.has_screen("twoplayer"):
            self.manager.current = "twoplayer"
        else:
            print("Fehler: Screen 'twoplayer' existiert nicht!")

    def update_player_count(self, count):
        Clock.schedule_once(lambda dt: self._update_player_count(count))

    def _update_player_count(self, count):
        self.player_count_text = f"Spieler verbunden: {count}/2"

    def show_connection_error(self):
        self.player_count_text = "Server nicht erreichbar"
        self.waiting_text = "Bitte überprüfe die Serververbindung"

    def go_back(self):
        try:
            self.sock.close()
        except:
            pass
        self.manager.current = "menu"
