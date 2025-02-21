from tkinter import ttk
import tkinter as tk

from chemotion_api import Reaction
from chemotion_api.elements.reaction import QuantityUnit

from ChemDoE.config import ConfigManager
from ChemDoE.utils.pages import ToolBarPage


class DoEPage(ToolBarPage):
    def __init__(self, reaction: Reaction):
        super().__init__()
        self.reaction = reaction
        self._rows = None
        self._columns = None


    def _get_rows(self):
        self.reaction.variations.add_new()
        v = self.reaction.variations.add_new()
        self.reaction.variations.pop()
        for mat_type in ["products", "starting_materials", "solvent", "products"]:
            pass

    def render(self, container: ttk.Frame):
        super().render(container)
        ttk.Label(container, text=f'{self.reaction.short_label} {self.reaction.name}', style='Header.TLabel', font=ConfigManager.header_font).pack(fill='x')

        self.table = tk.Frame(background='red')
        self.table.pack(fill='x', expand=True)
        self._get_rows()


    def set_style(self, style: ttk.Style):
        style.configure('Header.TLabel', background='red')