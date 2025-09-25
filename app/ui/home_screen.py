"""
Enthält die Logik für den Startbildschirm

Lädt Charaktere (z. B. per API oder JSON-Datei)

Baut das Raster (GridLayout) dynamisch

Reagiert auf Tipp-Aktionen (grau hinterlegen, Auswahl bestätigen)

"""

from kivymd.uix.screen import MDScreen
from kivy.lang import Builder

# Lade die .kv-Datei manuell
Builder.load_file("app/ui/home_screen.kv")

class HomeScreen(MDScreen):
    def go_to_name(self):
        self.manager.current = "name"