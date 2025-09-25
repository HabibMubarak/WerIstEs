from .home_screen import HomeScreen
from .menu_screen import MenuScreen
from .name_screen import NameScreen
from .twoplayer_screen import TwoPlayerScreen
from .select_character import SelectCharacter

from kivy.core.text import LabelBase

import json

# Farben aus JSON laden
settings = json.load(open("app/assets/settings/color.json", encoding="utf-8"))
# Fonts aus JSON laden
fonts = json.load(open("app/assets/settings/fonts.json", encoding="utf-8"))

# Alle Fonts registrieren
for font_name, font_path in fonts.items():
    LabelBase.register(name=font_name, fn_regular=font_path) 

PRIMARY_PALETTE = settings["PRIMARY_PALETTE"]
THEME_STYLE = settings["THEME_STYLE"]
BUTTON_BG = settings["LIGHT_BLUE"]

def register_screens(screen_manager):
    screen_manager.add_widget(HomeScreen(name="home"))
    screen_manager.add_widget(NameScreen(name="name"))
    screen_manager.add_widget(MenuScreen(name="menu"))
    screen_manager.add_widget(TwoPlayerScreen(name="twoplayer"))
    screen_manager.add_widget(SelectCharacter(name="select_character"))