from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import RotateBehavior
from kivymd.uix.list import MDListItemTrailingIcon
from kivy.lang import Builder
import json

Builder.load_file(r"app/ui/components/trailing_pressed_icon_button.kv")

class TrailingPressedIconButton(ButtonBehavior, RotateBehavior, MDListItemTrailingIcon):
    pass