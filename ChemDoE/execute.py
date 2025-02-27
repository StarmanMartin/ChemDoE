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
        self.sf = ScrollableFrame(self, horizontal=True)
        self.sf.pack(fill="both", expand=True, padx=10, pady=10)
        self._label = ttk.Label(self.sf.scrollable_frame, text="Running...", anchor="w")
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
        self._label.destroy()
        tree.pack(expand=True, fill="x", padx=10, pady=10)
        if out_ft == 'json':
            self.load_json(tree, out_file_path)
        elif out_ft == 'csv':
            self.load_csv(tree, out_file_path)
        self._root.after(10, self.sf.update_sc_view)
        os.remove(out_file_path)

    @staticmethod
    def load_json(tree, file_path):

        with open(file_path, 'r', encoding='utf-8') as json_file:
            reader = json.loads(json_file.read())
            headers = list(reader.keys())

            if headers:
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

    @staticmethod
    def load_csv(tree, file_path):

        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)  # Get headers from the first row

            if headers:
                tree["columns"] = headers
                tree["show"] = "headings"  # Hide default first column
                new_height = 1
                # Set up column headers
                for col in headers:
                    tree.heading(col, text=col)
                    tree.column(col, anchor="w", width=100)

                # Insert data into the treeview
                for row in reader:
                    new_height += 1
                    tree.insert("", "end", values=row)

            tree.configure(height=new_height)
