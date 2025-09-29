"""
Enthält die Logik für den Chat-Bildschirm

Sendet & empfängt Nachrichten

Ruft Moderationslogik aus core/chat_logic.py auf

Wechselt zurück zum Home-Screen, wenn der Chat fertig ist

"""
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy.lang import Builder
from app.ui.components.game_card import GameCard
from kivy.uix.screenmanager import SlideTransition
import json

# Lade die .kv-Datei manuell
Builder.load_file("app/ui/menu_screen.kv")
Builder.load_file("app/ui/components/game_card.kv")

from kivymd.uix.screen import MDScreen

class MenuScreen(MDScreen):
    lang = "de"
    # Properties statt normale Attribute
    soonavailable = StringProperty("")
    twoplayer = StringProperty("")
    settings = StringProperty("")
    select_game_mode = StringProperty("")

    def on_pre_enter(self):
        # Sprache aus Profil laden
        self.lang = json.load(open("app/assets/settings/profil.json", encoding="utf-8"))["lang"]
        data = json.load(open(f"app/assets/lang/{self.lang}.json", encoding="utf-8"))
        self.soonavailable = data["menu"]["soonavailable"]
        self.twoplayer = data["menu"]["twoplayerCard"]
        self.settings = data["menu"]["settings"]
        self.select_game_mode = data["menu"]["select_game_mode"]

    def two_player_mode(self):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "twoplayer"
