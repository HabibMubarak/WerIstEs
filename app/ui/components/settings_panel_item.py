from kivymd.uix.expansionpanel import MDExpansionPanel
from kivy.lang import Builder


Builder.load_file(r"app/ui/components/trailing_pressed_icon_button.kv")

class SettingsPanelItem(MDExpansionPanel):
    title = "Setting"