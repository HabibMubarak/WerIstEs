from kivymd.uix.list import OneLineAvatarIconListItem

from kivy.properties import StringProperty,ObjectProperty
from kivy.lang import Builder

Builder.load_file(r"app/ui/components/anime_list_item.kv")


class AnimeListItem(OneLineAvatarIconListItem):
    icon = StringProperty("android")
    checkbox = ObjectProperty(None)
    
