from tkinter import ttk
import tkinter as tk
from typing import Optional

from chemotion_api import Instance, Reaction, Sample
from chemotion_api.collection import Collection

from ChemDoE.element_tree_page import ElementTreePage
from ChemDoE.icons import IconManager
from ChemDoE.utils.dd_manager import DragManager
from ChemDoE.utils.pages import ListRow, ScrollableFrame


class NewReaction(ElementTreePage):
    def __init__(self, instance: Instance, collection: Collection, reaction: Optional[Reaction] = None):
        super().__init__(instance, 'Sample')
        self._collection = collection
        self._is_new = reaction is None
        self._dh: Optional[DragManager] = None
        if self._is_new:
            self.reaction = collection.new_reaction()
            self._name_var = tk.StringVar(value="New Reaction")
        else:
            self.reaction = reaction
            self._name_var = tk.StringVar(value=reaction.name)

    def render(self, container: ttk.Frame):
        super().render(container)

        left_frame = ScrollableFrame(self.paned_window, relief=tk.SUNKEN, padding=5)
        self.paned_window.add(left_frame, weight=1)  # weight allows resizing
        left_frame = left_frame.scrollable_frame
        if self._is_new:
            ttk.Label(left_frame, text='New Reaction', font=('Arial', 16, 'bold'), justify='right').pack(fill=tk.X)
        else:
            ttk.Label(left_frame, text=f'Edit Reaction {self.reaction.short_label}', font=('Arial', 16, 'bold'), justify='right').pack(fill=tk.X)

        entry_row = tk.Frame(left_frame)
        entry_row.pack(fill="x", pady=2)

        # Label (Fixed width)
        label = ttk.Label(entry_row, text="Reaction name:")
        label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        entry_row.grid_columnconfigure(1, weight=1)# Left-aligned

        # Entry (Expands)
        entry = ttk.Entry(entry_row)
        entry.insert(0, self.reaction.name)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))


        self._dh = DragManager(self.collection_tree, self.page_manager.root)
        self._on_drag_start = self._drag_start

        self._render_material_input(left_frame, 'Starting Material', self.reaction.properties['starting_materials'])
        self._render_material_input(left_frame, 'Reactants', self.reaction.properties['reactants'])
        self._render_material_input(left_frame, 'Products', self.reaction.properties['products'])

        ttk.Button(left_frame, style="Save.TButton", text="Save",
                              command=lambda *x: self._save()).pack()

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
        self._dh.on_drop_in_target(drop_frame, lambda selection, target: self._on_drop(selection, list_frame, elements))

    def _list_materials(self, materials: list[Sample], frame):
        for sample in materials:
            self._list_sdd_materials(sample, frame)


    def _list_sdd_materials(self, sample: Sample, frame):
        row = ListRow(frame, IconManager().SAMPLE_ICON, sample.short_label, sample.name, lambda *args: self._delete_row(sample, *args))
        row.pack(fill="x", pady=2)

    def _delete_row(self, sample, *args):
        pass

    def _drag_start(self, selection):
        vals = self.collection_tree.item(selection, "values")
        return len(vals) > 1 and vals[1] == 'Element'

    def _on_drop(self, selection, frame, elements):
        vals = self.collection_tree.item(selection, "values")
        sample = self.instance.get_sample(int(vals[0]))
        elements.append(sample)
        self._list_sdd_materials(sample, frame.master)

    def set_style(self, style: ttk.Style):
        super().set_style(style)
        style.configure('Drop.TLabel', foreground="#555555", padx=(0, 5), pady=(0, 5))
        style.configure('Save.TButton', background='#5cb85c', foreground="#ffffff", padx=(0, 5), pady=(0, 5))

    def _save(self):
        self.reaction.properties['name'] = self._name_var.get()
        self.reaction.save()