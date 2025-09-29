from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.core.image import Image as CoreImage
from kivy.uix.image import AsyncImage
import os
import requests
from io import BytesIO

class GameCard(MDCard):
    icon = StringProperty('folder')
    icon_color = ListProperty([1, 1, 1, 1])
    card_color = ListProperty([0.1, 0.1, 0.1, 1])
    text_color = ListProperty([1, 1, 1, 1])
    title = StringProperty('Title')
    size_text = StringProperty('0 MB')
    bg_image = StringProperty("")
    bg_texture = ObjectProperty(None)
    available = BooleanProperty(True)

    _async_img = None  # AsyncImage-Referenz speichern, damit es nicht vom GC gelöscht wird

    def on_bg_image(self, instance, value):
        # Wenn kein Bild → Textur entfernen
        if not value:
            self.bg_texture = None
            return

        try:
            if value.startswith("http"):  # URL → AsyncImage nutzen
                if not self._async_img:
                    self._async_img = AsyncImage(opacity=0)  # unsichtbar, nur zum Laden
                    self._async_img.bind(texture=self.on_texture_loaded)

                self._async_img.source = value

            else:  # Lokale Datei synchron laden
                if os.path.exists(value):
                    img = CoreImage(value)
                    img.texture.mag_filter = "nearest"
                    img.texture.min_filter = "nearest"
                    self.bg_texture = img.texture
                else:
                    print("Lokale Datei nicht gefunden:", value)
                    self.bg_texture = None

        except Exception as e:
            print("Fehler beim Laden des Bildes:", e)
            self.bg_texture = None
    
    def on_press(self):
        # Hier rufen wir die Methode des Screens auf
        if hasattr(self.parent.parent, "card_clicked"):
            self.parent.parent.card_clicked(self.title)

    def on_texture_loaded(self, async_img, texture):
        """Wird aufgerufen, sobald AsyncImage die Textur geladen hat."""
        try:
            if texture:
                texture.mag_filter = "nearest"
                texture.min_filter = "nearest"
                self.bg_texture = texture
            else:
                self.bg_texture = None
        except Exception as e:
            print("Fehler beim Setzen der Async-Textur:", e)
            self.bg_texture = None