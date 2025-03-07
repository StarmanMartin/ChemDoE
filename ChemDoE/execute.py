import json
import os
import re
import threading
from pathlib import Path
from subprocess import Popen, PIPE
import tkinter as tk
from tkinter import ttk, messagebox

from chemotion_api import Reaction

from ChemDoE.config import ConfigManager
from ChemDoE.icons import IconManager
from ChemDoE.registration.loader import read_csv, read_json
from ChemDoE.registration.result_validater import validate_results
from ChemDoE.utils.pages import ScrollableFrame


class ExecuteManager(tk.Toplevel):

    def __init__(self, root, reaction: Reaction):
        super().__init__(root)
        self._root = root
        self.title("Run")
        self.geometry("600x300")
        self.sf = ScrollableFrame(self, horizontal=True)
        self.sf.pack(fill="both", expand=True, padx=10, pady=10)
        self._label = ttk.Label(self.sf.scrollable_frame, text="Running...", anchor="w")
        self._label.pack(fill="x", padx=10, pady=10)
        self._reaction = reaction
        self._errors = []

    def run(self, script, values):
        fp = Path(script['file'])
        ft = script['input'].lower()
        out_ft = script['output'].lower()
        file_name = re.sub(r'[^A-Za-z]', '_', script['name']) + f'.{ft}'

        file_path = str(fp.parent / file_name)

        if ft == 'json':
            with open(file_path, 'w+') as f:
                f.write(json.dumps(values, indent=4))
        else:
            res = []
            for key, val in values.items():
                res.append(','.join([key] + [str(x) for x in val]))
            with open(file_path, 'w+') as f:
                f.write('\n'.join(res))
        out_file_path = str(fp.parent / f'out_{file_name}.{out_ft}')
        cmd = [script['interpreter'], script['file'], file_path, out_file_path]

        p = Popen(cmd, stdout=PIPE,
                  stderr=PIPE,
                  text=True,  # Ensures output is in string format instead of bytes
                  bufsize=1,  # Line-buffered output
                  universal_newlines=True,  # Handles newlines properly across platforms
                  cwd=fp.parent
                  )
        lines = ""
        for line in iter(p.stdout.readline, ''):
            lines += line
            self._root.after(0, lambda: self._label.config(text=lines))
        os.remove(file_path)
        self._root.after(10, self.load_results, out_file_path, out_ft)

    def load_results(self, out_file_path, out_ft):
        tree = ttk.Treeview(self._label.master)
        self._label.config(text=self._label.cget('text') + "\nResults")
        tree.pack(expand=True, fill="x", padx=10, pady=10)
        if out_ft == 'json':
            self._data = self.load_json(tree, out_file_path)
        elif out_ft == 'csv':
            self._data = self.load_csv(tree, out_file_path)
        if self._data is not None:
            self._root.after(10, self.sf.update_sc_view)
            ttk.Button(tree.master, text="Transfer variations", image=IconManager().CHEMOTION, compound="left",
                       command=self.transfer_variations).pack(anchor="w")
            self.sf.update_sc_view()
        os.remove(out_file_path)

    def transfer_variations(self):
        self._label.config(text="Transferring...")

        def save():
            self._reaction = ConfigManager().chemotion.get_reaction(self._reaction.id)
            for v in self._reaction.variations[:]:
                if v.notes.startswith('ChemDoE: '):
                    self._reaction.variations.remove(v)
            self._reaction.save(True)
            for v_name, val in self._data.items():
                if v_name not in ['UNIT', 'VARIABLE']:
                    variation = self._reaction.variations.add_new()
                    variation.notes = f'ChemDoE: <<{v_name}>>'
                    for materials in ['starting_materials', 'reactants', 'products', 'solvents']:
                        letter = materials.upper()[0]
                        for mat in getattr(variation, materials):
                            key = f"{letter}:{mat.sample.id}"
                            idx = self._data['VARIABLE'].index(key)
                            mat.set_quantity(float(val[idx]), str(self._data['UNIT'][idx]))
                    for key, prop in variation.properties.items():
                        key = key.capitalize()
                        idx = self._data['VARIABLE'].index(key)
                        prop['value'] = float(val[idx])
                        prop['unit'] = str(self._data['UNIT'][idx])
            self._reaction.save()
            self._root.after(0, lambda: self._label.config(text="Transferred"))

        threading.Thread(target=save).start()

    def _validate_json_results(self, data):
        self._errors = validate_results(data)

        return len(self._errors) == 0

    def load_json(self, tree, file_path):
            return self._render_tree(tree, read_json(file_path))

    def load_csv(self, tree, file_path):
            return self._render_tree(tree, read_csv(file_path))

    def _render_tree(self, tree, reader):
        if not self._validate_json_results(reader):
            messagebox.showerror('Invalid JSON!', '\n'.join(f' - {x}' for x in self._errors))
            return None
        headers = list(reader.keys())

        headers.remove('VARIABLE')
        headers.remove('UNIT')
        headers = ['VARIABLE', 'UNIT'] + headers
        tree["columns"] = headers
        tree["show"] = "headings"  # Hide default first column
        new_height = 1
        # Set up column headers
        for col in headers:
            tree.heading(col, text=col)
            tree.column(col, anchor="w", width=100)

        # Insert data into the treeview
        for i in range(len(reader[headers[0]])):
            new_height += 1
            tree.insert("", "end", values=[reader[head][i] for head in headers])

        tree.configure(height=new_height)
        return reader
