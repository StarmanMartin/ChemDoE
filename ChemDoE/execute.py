import csv
import json
import os
import re
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
import tkinter as tk
from tkinter import ttk

from ChemDoE.utils.pages import ScrollableFrame


class ExecuteManager(tk.Toplevel):

    def __init__(self, root):
        super().__init__(root)
        self._root = root
        self.title("Run")
        self.geometry("600x300")
        sf = ScrollableFrame(self)
        sf.pack(fill="both", expand=True, padx=10, pady=10)
        self._label = ttk.Label(sf.scrollable_frame, text="Running...", anchor="w")
        self._label.pack(fill="x", padx=10, pady=10)

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
                  universal_newlines=True # Handles newlines properly across platforms
            )
        lines = ""
        for line in iter(p.stdout.readline, ''):
            lines += line
            self._root.after(0, lambda: self._label.config(text=lines))
        os.remove(file_path)
        self._root.after(10, self.load_csv, out_file_path)

    def load_csv(self, file_path):
        tree = ttk.Treeview(self._label.master)
        self._label.destroy()
        tree.pack(expand=True, fill="both", padx=10, pady=10)
        # Clear existing data in the treeview
        tree.delete(*tree.get_children())

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)  # Get headers from the first row

            if headers:
                tree["columns"] = headers
                tree["show"] = "headings"  # Hide default first column

                # Set up column headers
                for col in headers:
                    tree.heading(col, text=col)
                    tree.column(col, anchor="w", width=100)

                # Insert data into the treeview
                for row in reader:
                    tree.insert("", "end", values=row)
