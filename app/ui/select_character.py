from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from app.ui.components.game_card import GameCard

Builder.load_file("app/ui/select_character.kv")

class SelectCharacter(MDScreen):
    selected_anime = ""

    def on_pre_enter(self):
        self.ids.select_anime_top_bar.title = self.selected_anime
        self.fill_carousel()


    def fill_carousel(self):
        carousel = self.ids.carousel
        carousel.clear_widgets()  # sicherstellen, dass es leer ist

        # Beispiel: 5 GameCards hinzufügen
        for i in range(5):
            card = GameCard(
                title=f"Character {i+1}",
                bg_image=f"app/assets/img/intro.png",  # Beispielbilder
                available=True
            )
            # Karte so groß wie das Carousel
            card.size_hint = (1, 1)
            carousel.add_widget(card)

    

    def on_back_pressed(self):
        if self.manager.current != "twoplayer":
            self.manager.current = "twoplayer"
