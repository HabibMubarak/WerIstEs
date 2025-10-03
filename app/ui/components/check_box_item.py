from kivymd.uix.list import IRightBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.properties import StringProperty
from kivy.lang import Builder

Builder.load_file(r"app/ui/components/check_box_item.kv")


class RightCheckBox(IRightBodyTouch, MDCheckbox):
    anime_name = StringProperty()
    pass