from tkinter import ttk
import tkinter as tk
import tkinter.font as tkFont

from chemotion_api import Reaction
from chemotion_api.labImotion.items.options import FieldType, UNITS

from ChemDoE.config import ConfigManager
from ChemDoE.script_manager import ScriptOrganizer
from ChemDoE.utils.pages import ToolBarPage


class DoEPage(ToolBarPage):
    def __init__(self, reaction: Reaction):
        super().__init__()
        self._run_manager = None
        self.reaction = reaction
        self._name = f'{self.reaction.short_label} {self.reaction.name}'
        self._rows = None
        self._additional_fields = []
        self._addable_fields = None
        self._addable_field_dropdown = None
        self._table = None
        self._columns = 3
        self._columnes_var = tk.IntVar(value=self._columns)
        self._columnes_var.trace_add("write", self._columns_change)
        self._entries = {}
        self._values = {}
        self._save_after_id = None

    def render(self, container: ttk.Frame):
        super().render(container)

        ttk.Label(container, text=self._name, style='Header.TLabel',
                  font=ConfigManager.header_font).pack(fill='x')
        button_frame = tk.Frame(container)
        button_frame.pack(fill='x')
        
        self._run_manager = ScriptOrganizer(self._page_manager, button_frame, self.reaction)
        self._run_manager.pack(side='left', padx=5, pady=5)
        ttk.Label(button_frame, text="# columns:").pack(side='left', padx=5, pady=5)
        ttk.Entry(button_frame, textvariable=self._columnes_var, validate="all", width=4,
                  validatecommand=self._page_manager.validators["numeric"]).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text="Reshape", command=self._update_table).pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text="Save Template", command=lambda *x: self._save_template(self._name)).pack(
            side='left',
            padx=5,
            pady=5)
        selected_template = ttk.Combobox(button_frame, values=[], state="readonly")
        selected_template.bind("<Button-1>", lambda *x: self._on_dropdown_template(selected_template))
        selected_template.pack(side='left', padx=5, pady=5)
        ttk.Button(button_frame, text="Load Template", command=lambda *x: self._load_templte(selected_template)).pack(
            side='left', padx=5, pady=5)

        self._table = ttk.Frame(container, style='Table.TFrame')
        self._table.pack(fill='x')
        

        values = ConfigManager().load_doe(self._name)
        if values and 'values' in values and 'template' in values:
            self._values = values['values']
            self._execute_template(values['template'])
        self._run_manager.values = self._values
        self._update_table()

    def set_style(self, style: ttk.Style):
        ScriptOrganizer.set_style(style)
        style.configure('Table.TFrame', background='white')
        style.configure('Header.TLabel', background='white')
        style.configure('TableHeader.TLabel', borderwidth=1, relief='solid', background='white', padding=10)
        style.configure('TableRowHeader.TLabel', borderwidth=1, relief='solid', background='white', padding=5)
        style.configure('TableInnerHeader.TLabel', background='#0091ea', padding=(10, 2))
        style.configure('AddButton.TButton',  padding=(10, 2))
        style.configure('TableInnerRemove.TButton',  padding=(2, 2))

        style.map('AddButton.TButton',
                  foreground=[('!active', 'white'), ('pressed', 'white'), ('active', '#333333')],
                  background=[('!active', '#5cb85c'), ('pressed', '#5cb85c'), ('active', '#5cb85c')]
                  )

        style.map('TableInnerRemove.TButton',
                  foreground=[('!active', 'white'), ('pressed', 'white'), ('active', '#333333')],
                  background=[('!active', '#d9534f'), ('pressed', '#d9534f'), ('active', '#d9534f')]
                  )

    def _get_validation_templates(self):
        v = self.reaction.variations.add_new()
        self.reaction.variations.remove(v)
        return v

    def _get_addable_fields(self):
        self._addable_fields = [s for s in ConfigManager().all_additional_fields() if s not in self._additional_fields]
        return self._addable_fields

    def _update_table(self, *_args):
        self._clean_table()
        ttk.Frame(self._table, style='TableHeader.TLabel').grid(row=0, column=0)
        ttk.Label(self._table, text='Units', style='TableHeader.TLabel', anchor='center').grid(row=0, column=1,
                                                                                               sticky="ew")
        for i in range(2, self._columns + 2):
            if i == 2:
                text = 'Min'
            elif i - 1 == self._columns:
                text = 'Max'
            else:
                text = '     '
            ttk.Label(self._table, text=text, style='TableHeader.TLabel', anchor='center').grid(row=0, column=i,
                                                                                                sticky="ew")
        row = 0
        validation = self._get_validation_templates()

        for key, title in (
                ("starting_materials", "Starting Material"), ("reactants", "Reactants"), ("products", "Products"),
                ("solvents", "Solvents")):
            row = self._render_mat_rows(row + 1, validation, key, title)
        row += 1
        ttk.Label(self._table, text='Properties', style='TableInnerHeader.TLabel', justify='left').grid(row=row,
                                                                                                        column=0,
                                                                                                        sticky="ew",
                                                                                                        columnspan=self._columns + 2)
        for k, p in validation.properties.items():
            row += 1
            text = k.title()
            units = [p['unit']]
            self._render_row(text, row, text, units)

        row += 1
        ttk.Label(self._table, text='Segment properties', style='TableInnerHeader.TLabel', justify='left').grid(row=row,
                                                                                                                column=0,
                                                                                                                sticky="ew",
                                                                                                                columnspan=self._columns + 2)
        row += 1
        add_frame = ttk.Frame(self._table, style='TableHeader.TLabel')
        add_frame.grid(row=row, column=0, sticky="ew", columnspan=self._columns + 2)

        fields = [f"{s[0].label}: {s[1].label}: {s[2].label}" for s in self._get_addable_fields()]
        self._addable_field_dropdown = ttk.Combobox(add_frame, values=fields, state="readonly")

        font = tkFont.Font(font=self._addable_field_dropdown.cget("font"))
        if len(fields) > 0:
            max_width = max(font.measure(option) for option in fields)  # Get max text width in pixels
            self._addable_field_dropdown.config(width=max_width // font.measure("0") + 2)

        self._addable_field_dropdown.pack(side='left', padx=5, pady=5)
        ttk.Button(add_frame, text='Add properties', style='AddButton.TButton', command=self._add_addable_field).pack(
            side='left', padx=5, pady=5)

        for s in self._additional_fields:
            row += 1
            text = f"{s[0].label}: {s[1].label}: {s[2].label}"
            row_id = '__'.join(self._field_to_key(s))
            units = '-'
            if s[2].field_type == FieldType.SYSTEM_DEFINED:
                units = [x.replace('_2', '²').replace('_3', '³').replace('2', '²').replace('3', '³').replace('_', '/')
                         for x in UNITS[s[2].option_layers]]
            button = ttk.Button(self._table, text="🗑", style='TableInnerRemove.TButton', width=2,
                                command=lambda x=s: self._remove_addable_field(x))
            self._render_row(row_id, row, text, units, button)

        self._clean_values()
        self._save()

    @staticmethod
    def _field_to_key(field_tuple):
        return [field_tuple[0].identifier, field_tuple[1].key, field_tuple[2].field]

    def _render_mat_rows(self, row, validation, key, title):
        mats = getattr(validation, key)
        if len(mats) == 0:
            return row - 1
        ttk.Label(self._table, text=title, style='TableInnerHeader.TLabel', justify='left').grid(row=row, column=0,
                                                                                                 sticky="ew",
                                                                                                 columnspan=self._columns + 2)
        for i in mats:
            row += 1
            text = f"{title[0]}:{i.sample.id}: {i.sample.short_label}: {i.sample.molecule['cano_smiles']}"
            units = [x.value for x in i.potential_units()]
            self._render_row(f'{title[0]}:{i.sample.id}', row, text, units)
        return row

    def _remove_addable_field(self, row):
        self._additional_fields.remove(row)
        self._update_table()

    def _add_addable_field(self, *_args):
        idx = self._addable_field_dropdown.current()
        if idx == -1:
            return
        self._additional_fields.append(self._addable_fields[idx])
        self._update_table()

    def _on_table_entry_change(self, row_id, col):
        self._values[row_id][col] = self._entries[row_id][col].get()
        if self._save_after_id is not None:
            self._page_manager.root.after_cancel(self._save_after_id)
        self._save_after_id = self._page_manager.root.after(500, self._save)

    def _on_table_unit_change(self, row_id):
        self._on_table_entry_change(row_id, col=0)

    def _render_row(self, row_id, row, text, units, button=None):
        label_frame = ttk.Frame(self._table)
        label_frame.grid(row=row, column=0, sticky="ew")
        ttk.Label(label_frame, text=text, style='TableRowHeader.TLabel').pack(fill='x')
        unit_var = tk.StringVar(value=self._get_value_unit(row_id, units))
        unit_sel = ttk.Combobox(self._table, values=units, state="readonly", textvariable=unit_var)
        unit_var.trace_add("write", lambda _a, _b, _c: self._on_table_unit_change(row_id))
        unit_sel.grid(row=row, column=1, sticky="ew")
        self._entries[row_id] = [unit_var]
        for col_idx in range(self._columns):
            col = col_idx + 2
            ev = tk.DoubleVar(value=self._get_value(row_id, col_idx))
            self._entries[row_id].append(ev)
            entry = ttk.Entry(self._table, textvariable=ev, validate="all",
                              validatecommand=self._page_manager.validators["float"])
            entry.grid(row=row,
                       column=col,
                       sticky="ns")
            ev.trace_add("write", lambda _a, _b, _c, i=col_idx: self._on_table_entry_change(row_id, i + 1))

        if button:
            button.grid(row=row, column=self._columns + 2)

    def _clean_table(self):
        for widget in self._table.winfo_children():
            widget.destroy()
            del widget

    def _get_value(self, row, col):
        col += 1
        if row not in self._values:
            self._values[row] = [''] + [0.0] * self._columns
        while len(self._values[row]) <= col:
            self._values[row].append(0.0)
        return self._values[row][col]

    def _get_value_unit(self, row, default_units):
        value = self._get_value(row, -1)
        if value not in default_units:
            self._values[row][0] = default_units[0]
        return self._values[row][0]

    def _columns_change(self, *_args):
        try:
            a = self._columnes_var.get()
            if a > 0:
                self._columns = self._columnes_var.get()
        except tk.TclError:
            return

    def _prepare_template(self):
        return {
            'size': self._columns,
            'fields': [self._field_to_key(s) for s in self._additional_fields]
        }

    def _save_template(self, name):
        template = self._prepare_template()
        ConfigManager().save_template(template, name)

    def _load_templte(self, select_template):
        selected_template = select_template.get()
        if selected_template == '':
            return
        template = ConfigManager().load_template(selected_template)
        self._execute_template(template)

    def _execute_template(self, template):
        self._columns = template['size']
        self._columnes_var.set(template['size'])
        self._additional_fields.clear()
        for field in template['fields']:
            for potential_field in self._get_addable_fields():
                if field[0] == potential_field[0].identifier and field[1] == potential_field[1].key and field[2] == \
                        potential_field[2].field:
                    self._additional_fields.append(potential_field)

        self._update_table()

    @staticmethod
    def _on_dropdown_template(selected_template):
        selected_template.config(values=[x.name[:-5] for x in ConfigManager().load_templates()])

    def _clean_values(self):
        for key in list(self._values.keys()):
            if key not in self._entries.keys():
                del self._values[key]
            else:
                self._values[key] = self._values[key][:self._columns + 1]

    def _save(self):
        ConfigManager().save_doe({'values':self._values, 'template': self._prepare_template()}, self._name)
