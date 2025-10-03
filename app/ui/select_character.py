from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from app.ui.components.game_card import GameCard
from kivy.core.window import Window
from app.core.character import Character
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.clock import Clock
from kivy.uix.screenmanager import SlideTransition

Builder.load_file("app/ui/select_character.kv")


class SelectCharacter(MDScreen):
    selected_anime = ""
    selected_character = ""
    dialog: MDDialog = None

    def on_pre_enter(self):
        self.ids.select_anime_top_bar.title = self.selected_anime
        self.fill_recycleview()
        # Horizontale RecycleView nach ganz links scrollen
        Clock.schedule_once(lambda dt: self.scroll_to_start(), 0)

    def scroll_to_start(self):
        """Scrollt die horizontale RecycleView nach ganz links (Index 0)."""
        if hasattr(self.ids.rv, "scroll_x"):
            self.ids.rv.scroll_x = 0  # 0 = ganz links
    def fill_recycleview(self):
        card_width = Window.width
        card_height = Window.height * 0.8

        # RecycleView zentrieren
        self.ids.rv.size_hint = (None, None)
        self.ids.rv.size = (Window.width, card_height)
        self.ids.rv.pos_hint = {"center_x": 0.5, "center_y": 0.5}

        # Karten-Größe setzen
        self.ids.rv.layout_manager.default_size = (card_width, card_height)
        self.ids.rv.layout_manager.default_size_hint = (None, None)


        # Daten füllen
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
    
    def confirm_character(self, *args):
        print(f"Character confirmed: {self.selected_character}")
        self.dialog.dismiss()

        # An den Server senden, dass dieser Spieler gewählt hat
        try:
            if hasattr(self.manager, "sock") and self.manager.sock:
                self.manager.sock.sendall(
                    f"CHAR_SELECTED {self.selected_character}\n".encode("utf-8")
                )
        except Exception as e:
            print("[ERROR] Konnte Auswahl nicht an Server senden:", e)


    def character_clicked(self, name):
        """Wird aufgerufen, wenn ein Charakter angeklickt wird."""
        self.selected_character = name

        # Dialog erstellen
        if not self.dialog:
            self.dialog = MDDialog(
                title="Charakter auswählen",
                text=f"Möchtest du wirklich {name} auswählen?",
                buttons=[
                    MDFlatButton(
                        text="ABBRECHEN",
                        on_release=self.dismiss_dialog
                    ),
                    MDFlatButton(
                        text="JA",
                        on_release=self.confirm_character
                    ),
                ],
            )
        else:
            # Text aktualisieren, falls Dialog schon existiert
            self.dialog.text = f"Möchtest du wirklich {name} auswählen?"

        self.dialog.open()

    def dismiss_dialog(self, *args):
        self.dialog.dismiss()

    def confirm_character(self, *args):
        print(f"Character confirmed: {self.selected_character}")
        self.dialog.dismiss()

        try:
            waiting_screen = self.manager.get_screen("waiting_room")
            room_id = waiting_screen.room_id  # hier liegt die room_id aus START_GAME
            if room_id and hasattr(waiting_screen, "sock") and waiting_screen.sock:
                waiting_screen.sock.sendall(
                    f"CHAR_SELECTED {room_id} {self.selected_character}\n".encode("utf-8")
                )
        except Exception as e:
            print("[ERROR] Konnte Auswahl nicht an Server senden:", e)

        # Danach ins Spielfeld wechseln
        self.manager.transition.direction = "left"
        self.manager.current = "game_field"





    def on_back_pressed(self):
        if self.manager.current != "twoplayer":
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = "twoplayer"