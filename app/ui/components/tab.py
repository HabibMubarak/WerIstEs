from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.tab import MDTabsBase
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_file(r"app/ui/components/tab.kv")

class Tab(MDBoxLayout, MDTabsBase):
    scroll_box = ObjectProperty(None)

    def to_top(self):
        """Scrollt den ScrollView in dieser Tab nach oben."""
        if self.scroll_box:
            self.scroll_box.scroll_y = 1
