from .home_screen import HomeScreen
from .chat_screen import ChatScreen


PRIMARY_PALETTE = "Blue"
THEME_STYLE = "Light"
BUTTON_BG = [61/256, 105/256, 153/256, 1]

def register_screens(screen_manager):
    screen_manager.add_widget(HomeScreen(name="home"))
    screen_manager.add_widget(ChatScreen(name="chat"))
