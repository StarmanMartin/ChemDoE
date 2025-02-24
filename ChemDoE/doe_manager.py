from tkinter import ttk
import tkinter as tk

from chemotion_api import Reaction
from chemotion_api.labImotion.items.options import FieldType, UNITS

from ChemDoE.config import ConfigManager
from ChemDoE.utils.pages import ToolBarPage


class DoEPage(ToolBarPage):
    def __init__(self, reaction: Reaction):
        super().__init__()
        self.reaction = reaction
        self._rows = None
        self._additional_fields = []
        self._addable_fields = None
        self._addable_field_dropdown = None
        self._columns = 3
        self._columnes_var = tk.IntVar(value=self._columns)
        self._columnes_var.trace_add("write", self._columns_change)

    def _get_validation_templates(self):
        self.reaction.variations.add_new()
        v = self.reaction.variations.add_new()
        self.reaction.variations.pop()
        return v
    
    def _get_addable_fields(self):
        self._addable_fields = [s for s in ConfigManager().all_additional_fields() if s not in self._additional_fields]
        return self._addable_fields

    def render(self, container: ttk.Frame):
        super().render(container)
        ttk.Label(container, text=f'{self.reaction.short_label} {self.reaction.name}', style='Header.TLabel',
                  font=ConfigManager.header_font).pack(fill='x')
        button_frame = tk.Frame(container)
        button_frame.pack(fill='x')
        ttk.Label(button_frame, text="# columns:").pack(side='left', padx=5, pady=5)
        ttk.Entry(button_frame, textvariable=self._columnes_var, validate="all", validatecommand=self._page_manager.validators["numeric"]).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text="Reshape", command=self._update_table).pack(side='left', padx=5, pady=5)

        self.table = ttk.Frame(container, style='Table.TFrame')
        self.table.pack(fill='x')
        self._update_table()

    def set_style(self, style: ttk.Style):
        style.configure('Table.TFrame', background='white')
        style.configure('Header.TLabel', background='white')
        style.configure('TableHeader.TLabel', borderwidth=1, relief='solid', background='white', padding=10)
        style.configure('TableRowHeader.TLabel', borderwidth=1, relief='solid', background='white', padding=5)
        style.configure('TableInnerHeader.TLabel', background='#0091ea', padding=(10, 2))
        style.configure('AddButton.TButton', background='#5cb85c', padding=(10, 2))

    def _update_table(self, *args):
        self._clean_table()
        ttk.Frame(self.table, style='TableHeader.TLabel').grid(row=0, column=0)
        ttk.Label(self.table, text='Units', style='TableHeader.TLabel', anchor='center').grid(row=0, column=1, sticky="ew")
        for i in range(2, self._columns + 2):
            if i == 2:
                text = 'Min'
            elif i - 1 == self._columns:
                text = 'Max'
            else:
                text = '     '
            ttk.Label(self.table, text=text, style='TableHeader.TLabel', anchor='center').grid(row=0, column=i, sticky="ew")
        row = 0
        validation = self._get_validation_templates()

        for key, title in (("starting_materials", "Starting Material"), ("reactants", "Reactants"), ("products", "Products"), ("solvents", "Solvents")):
            row = self._render_mat_rows(row + 1, validation, key, title)
        row += 1
        ttk.Label(self.table, text='Properties', style='TableInnerHeader.TLabel', justify='left').grid(row=row, column=0,
                                                                                                sticky="ew",
                                                                                                columnspan=self._columns + 2)
        for k, p in validation.properties.items():
            row += 1
            text = k.title()
            units = p['unit']
            self._render_row(row, text, units)


        row += 1
        ttk.Label(self.table, text='Segment properties', style='TableInnerHeader.TLabel', justify='left').grid(row=row, column=0,
                                                                                                sticky="ew",
                                                                                                columnspan=self._columns + 2)
        row += 1
        add_frame = ttk.Frame(self.table, style='TableHeader.TLabel')
        add_frame.grid(row=row, column=0, sticky="ew", columnspan=self._columns + 2)

        fields = [f"{s[0].label}: {s[1].label}: {s[2].label}" for s in self._get_addable_fields()]
        self._addable_field_dropdown = ttk.Combobox(add_frame, values=fields)
        self._addable_field_dropdown.pack(side='left', padx=5, pady=5)
        ttk.Button(add_frame, text='Add properties', style='AddButton.TButton', command=self._add_addable_field).pack(side='left', padx=5, pady=5)

        for s in self._additional_fields:
            row += 1
            text = f"{s[0].label}: {s[1].label}: {s[2].label}"
            units = '-'
            if s[2].field_type == FieldType.SYSTEM_DEFINED:
                units = [x.replace('_2', '²').replace('_3', '³').replace('2', '²').replace('3', '³').replace('_', '/') for x in UNITS[s[2].option_layers]]
            self._render_row(row, text, units)




    def _render_mat_rows(self, row, validation, key, title):
        mats = getattr(validation, key)
        if len(mats) == 0:
            return row - 1
        ttk.Label(self.table, text=title, style='TableInnerHeader.TLabel', justify='left').grid(row=row, column=0, sticky="ew",
                                                                                  columnspan=self._columns + 2)
        for i in mats:
            row += 1
            text = f"{i.sample.short_label}: {i.sample.molecule['cano_smiles']}"
            units = [x.value for x in i.potential_units()]
            self._render_row(row, text, units)
        return row

    def _add_addable_field(self, *args):
        idx = self._addable_field_dropdown.current()
        self._additional_fields.append(self._addable_fields[idx])
        self._update_table()


    def _render_row(self, row, text, units)  :
        label_frame = ttk.Frame(self.table)
        label_frame.grid(row=row, column=0, sticky="ew")
        ttk.Label(label_frame, text=text, style='TableRowHeader.TLabel').pack(fill='x')
        unit_sel = ttk.Combobox(self.table, values=units)
        unit_sel.current(0)
        unit_sel.grid(row=row, column=1, sticky="ew")
        for i in range(self._columns):
            ttk.Entry(self.table, validate="all", validatecommand=self._page_manager.validators["float"]).grid(row=row, column=i + 2, sticky="ns")



    def _clean_table(self):
        for widget in self.table.winfo_children():
            widget.destroy()

    def _columns_change(self, *args):
        try:
            a = self._columnes_var.get()
            if a > 0:
                self._columns = self._columnes_var.get()
        except tk.TclError:
            return
