import threading
from tkinter import ttk, messagebox
import tkinter as tk
from typing import Optional

from chemotion_api import Instance, Reaction, Sample
from chemotion_api.collection import Collection
from requests import RequestException

from ChemDoE.analyses_uploader import AnalysesUploader
from ChemDoE.config import ConfigManager
from ChemDoE.element_tree_page import ElementTreePage
from ChemDoE.icons import IconManager, LoadingGIF
from ChemDoE.new_sample import NewSample
from ChemDoE.utils.dd_manager import DragManagerTree
from ChemDoE.utils.pages import ListRow, ScrollableFrame
from ChemDoE.doe_manager import DoEPage


class NewReaction(ElementTreePage):
    def __init__(self, collection: Collection, reaction: Optional[Reaction] = None):
        super().__init__('Sample')
        self._collection = collection
        self._is_new = reaction is None
        self._dh: Optional[DragManagerTree] = None
        if self._is_new:
            self.reaction = collection.new_reaction()
            self._name_var = tk.StringVar(value="New Reaction")
        else:
            self.reaction = reaction
            self._name_var = tk.StringVar(value=reaction.name)
        self._name_var.trace_add("write", self._name_change)
        self._origen_data = self._prepare_compare_data()

    def render(self, container: ttk.Frame):
        super().render(container)
        if not self._is_new:
            self.reaction = self.instance.get_reaction(self.reaction.id)
        outher_frame = tk.Frame(self.paned_window, bg="")
        left_frame = ScrollableFrame(outher_frame, relief=tk.SUNKEN, padding=5)
        left_frame.pack(side=tk.LEFT, fill="both", expand=True)
        self.paned_window.add(outher_frame, weight=3)  # weight allows resizing
        left_frame = left_frame.scrollable_frame
        button_row = tk.Frame(left_frame, bg="white")
        self._save_btn = ttk.Button(button_row, style="Save.TButton", text="Save",
                              command=lambda *x: self._save())
        self._save_btn.pack(side=tk.LEFT)
        self._doe_btn = ttk.Button(button_row, style="Menu.TButton", text="Adjust DoE",
                              command=lambda *x: self._go_to_doe())

        self._doe_btn.pack(side=tk.LEFT)
        ana_btn = ttk.Button(button_row, style="Menu.TButton", text="Upload Analyses",
                              command=lambda *x: self._go_to_ana())
        ana_btn.pack(side=tk.LEFT)
        if not any(x.notes.startswith('ChemDoE: ') for x in self.reaction.variations):
            ana_btn.state(["disabled"])

        self._fav_btn = ttk.Button(button_row, style="Fav.TButton", text="Add ot Favorites",
                              command=lambda *x: self._toggel_favorites())
        self._fav_btn.pack(side=tk.RIGHT)
        button_row.pack(fill="x", expand=True)

        if self._is_new:
            ttk.Label(left_frame, text='New Reaction', font=ConfigManager.header_font, justify='right').pack(fill=tk.X)
        else:
            ttk.Label(left_frame, text=f'Edit Reaction {self.reaction.short_label}', font=ConfigManager.header_font, justify='right').pack(fill=tk.X)

        entry_row = tk.Frame(left_frame)
        entry_row.pack(fill="x", pady=2)

        # Label (Fixed width)
        label = ttk.Label(entry_row, text="Reaction name:")
        label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        entry_row.grid_columnconfigure(1, weight=1)# Left-aligned

        # Entry (Expands)
        entry = ttk.Entry(entry_row, textvariable=self._name_var)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))


        self._dh = DragManagerTree(self.collection_tree, self.page_manager.root)
        self._dh.on_drag_start = self._drag_start

        self._render_material_input(left_frame, 'Starting Material', self.reaction.properties['starting_materials'])
        self._render_material_input(left_frame, 'Reactants', self.reaction.properties['reactants'])
        self._render_material_input(left_frame, 'Products', self.reaction.properties['products'])
        self._check_change()
        self._style_favorite()


    def _render_material_input(self, left_frame, title, elements):
        start_mat_row = tk.Frame(left_frame, borderwidth=1, relief=tk.RAISED, background="#ffffff")
        ttk.Label(start_mat_row, text=title).pack(fill=tk.X)
        list_frame = tk.Frame(start_mat_row)
        self._list_materials(elements, list_frame)
        list_frame.pack(fill="x", pady=(0, 5))
        drop_frame = tk.Frame(start_mat_row, background='#aaaaaa')
        drop_lable = ttk.Label(drop_frame, text='Drop New Material', anchor="center", style='Drop.TLabel')
        drop_lable.pack(expand=True, fill=tk.X, pady=5, padx=5)
        start_mat_row.pack(fill=tk.X, pady=5)
        drop_frame.pack(fill=tk.X, pady=5)
        self._dh.on_drop_in_target(drop_frame, lambda selection, target: self._on_drop(str(selection), list_frame, elements))

    def _list_materials(self, materials: list[Sample], frame):
        for idx, sample in enumerate(materials):
            self._list_sdd_materials(materials, idx, frame)


    def _list_sdd_materials(self, materials: list[Sample], idx: int, frame):
        sample = materials[idx]
        row = ListRow(frame, IconManager().SAMPLE_ICON, sample.short_label, sample.molecule['cano_smiles'], lambda *args: self._delete_row(sample, materials, row, *args))
        row.pack(fill="x", pady=2)

    def _delete_row(self, sample: Sample, materials: list[Sample], row: ListRow, *args):
        materials.remove(sample)
        row.destroy()
        self._check_change()

    def _drag_start(self, selection):
        vals = self.collection_tree.item(selection, "values")
        return len(vals) > 1 and vals[1] == 'Element'

    def _on_drop(self, selection, frame, elements):
        vals = self.collection_tree.item(selection, "values")
        sample = self.instance.get_sample(int(vals[0]))
        elements.append(sample)
        self._list_sdd_materials(elements, len(elements) - 1, frame)
        self._check_change()

    def set_style(self, style: ttk.Style):
        super().set_style(style)
        style.configure('Drop.TLabel', foreground="#555555", padx=(0, 5), pady=(0, 5))
        style.configure('Save.TButton', background='#5cb85c', foreground="#ffffff", padx=(0, 5), pady=(0, 5))
        style.configure('Menu.TButton', background='#333333', foreground="#ffffff", padx=(0, 5), pady=(0, 5))
        style.configure('Fav.TButton',  background="#ffffff", relief=tk.SOLID, borderwidth=0, padx=(0, 5), pady=(0, 5))

    def _save(self):
        self.reaction.properties['name'] = self._name_var.get()
        lg = LoadingGIF(self._page_manager.root)
        lg.add_label(self._save_btn)
        lg.start()
        def stop(success):
            lg.stop()
            if success:
                self._origen_data = self._prepare_compare_data()
                self._is_new = False
                self._check_change()
                messagebox.showinfo("Saving Success", "The Reaction was saved.")
            else:
                messagebox.showerror("Saving failed", "The Reaction was not saved.")

        def run():
            try:
                self.reaction.save(True)
                self._page_manager.root.after(1000, stop, True)
            except RequestException as e:
                self._page_manager.root.after(1000, stop, False)

        threading.Thread(target=run).start()

    def _name_change(self, *args):
        self.reaction.properties['name'] = self._name_var.get()
        self._check_change()

    def _check_change(self):
        if self._origen_data == self._prepare_compare_data():
            self._save_btn.state(["disabled"])
            if not self._is_new:
                self._doe_btn.state(["!disabled"])
            else:
                self._doe_btn.state(["disabled"])
        else:
            self._save_btn.state(["!disabled"])
            self._doe_btn.state(["disabled"])

    def _prepare_compare_data(self):
        return "__".join([
            self.reaction.properties['name'],
            "_".join([str(x.id) for x in self.reaction.properties['starting_materials']]),
            "_".join([str(x.id) for x in self.reaction.properties['reactants']]),
            "_".join([str(x.id) for x in self.reaction.properties['products']]),
        ])

    def _style_favorite(self):
        if self.reaction.id in ConfigManager().favorites:
            self._fav_btn.config(image=IconManager().FAVORITE)
        else:
            self._fav_btn.config(image=IconManager().NO_FAVORITE)

    def _toggel_favorites(self):
        if self.reaction.id in ConfigManager().favorites:
            ConfigManager().remove_from_favorites(self.reaction)
        else:
            ConfigManager().add_to_favorites(self.reaction)
        self.update_fav_dropdown()
        self._style_favorite()

    def _go_to_doe(self):
        doe = DoEPage(self.reaction)
        self._page_manager.set_page(doe)

    def _go_to_ana(self):
        ana = AnalysesUploader(self.reaction)
        self._page_manager.set_page(ana)

    def create_new(self, col: Collection):
        self._page_manager.set_page(NewSample(col))