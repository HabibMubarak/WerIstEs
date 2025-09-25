from kivymd.uix.card import MDCard
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.core.image import Image as CoreImage

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

    def on_bg_image(self, instance, value):
        if value:
            try:
                img = CoreImage(value)
                img.texture.mag_filter = 'nearest'
                img.texture.min_filter = 'nearest'
                self.bg_texture = img.texture  # KV wird automatisch neu gezeichnet
            except Exception as e:
                print("Fehler beim Laden des Bildes:", e)
                self.bg_texture = None
        else:
            self.bg_texture = None
