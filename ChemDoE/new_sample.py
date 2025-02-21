import threading
from tkinter import ttk, messagebox
from typing import Optional
import tkinter as tk

from chemotion_api import Instance, Sample
from chemotion_api.collection import Collection
from requests import RequestException

from ChemDoE.config import ConfigManager
from ChemDoE.icons import LoadingGIF
from ChemDoE.utils.pages import ToolBarPage, ScrollableFrame


class NewSample(ToolBarPage):
    def __init__(self, collection: Collection, sample: Optional[Sample] = None):
        super().__init__()
        self._save_btn = None
        self._collection = collection
        self._is_new = sample is None

        if self._is_new:
            self.sample = collection.new_sample()
            self._smiles_var = tk.StringVar(value="")
        else:
            self.sample = sample
            self._smiles_var = tk.StringVar(value=sample.molecule['cano_smiles'])
        self._smiles_var.trace_add("write", self._smiles_change)
        self._origen_smiles = self._smiles_var.get()

    def render(self, container: ttk.Frame):
        super().render(container)

        left_frame = ScrollableFrame(container, relief=tk.SUNKEN, padding=5)
        left_frame.pack(fill=tk.BOTH, expand=True)  # weight allows resizing
        left_frame = left_frame.scrollable_frame
        if self._is_new:
            ttk.Label(left_frame, text='New Sample', font=ConfigManager.header_font, justify='right').pack(fill=tk.X)
        else:
            ttk.Label(left_frame, text=f'Edit Sample {self.sample.short_label}', font=ConfigManager.header_font, justify='right').pack(fill=tk.X)

        entry_row = tk.Frame(left_frame)
        entry_row.pack(fill=tk.BOTH, pady=2)

        # Label (Fixed width)
        label = ttk.Label(entry_row, text="Sample SMILES:")
        label.grid(row=0, column=0, padx=(0, 5), sticky="w")
        entry_row.grid_columnconfigure(1, weight=1)# Left-aligned

        # Entry (Expands)
        entry = ttk.Entry(entry_row, textvariable=self._smiles_var)
        entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))


        self._save_btn = ttk.Button(left_frame, style="Save.TButton", text="Save",
                              command=lambda *x: self._save())
        self._save_btn.pack()
        self._check_change()

    def _save(self):
        self.sample.molecule = self.instance.molecule().create_molecule_by_smiles(self._smiles_var.get())
        lg = LoadingGIF(self._page_manager.root)
        lg.add_label(self._save_btn)
        lg.start()
        def stop(success):
            lg.stop()
            if success:
                self._origen_smiles = self._smiles_var.get()
                self._check_change()
                self._page_manager.go_back()
                messagebox.showinfo("Saving Success", "The Sample was saved.")
            else:
                messagebox.showerror("Saving failed", "The Sample was not saved.")

        def run():
            try:
                self.sample.save()
                self._page_manager.root.after(1000, stop, True)
            except RequestException as e:
                self._page_manager.root.after(1000, stop, False)



        threading.Thread(target=run).start()


    def _smiles_change(self, *args):
        self._check_change()

    def _check_change(self):
        if self._origen_smiles == self._smiles_var.get():
            self._save_btn.state(["disabled"])  # Disable the button.
        else:
            self._save_btn.state(["!disabled"])