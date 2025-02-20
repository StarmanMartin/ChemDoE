from tkinter import ttk

from ChemDoE.utils.pages import ToolBarPage


class DoEPage(ToolBarPage):
    def __init__(self, reaction):
        super().__init__()
        self.reaction = reaction
        self.reaction.variations.add_new()
        self._v = self.reaction.variations.add_new()
        self.reaction.variations.pop()


    def render(self, container: ttk.Frame):
        super().render(container)
        pass
