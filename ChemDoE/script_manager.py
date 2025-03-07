import os
import sys
import threading
import uuid
import webbrowser
from pathlib import Path
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkFont
from typing import Optional, Callable

from chemotion_api import Reaction

from ChemDoE.config import ConfigManager
from ChemDoE.execute import ExecuteManager
from ChemDoE.icons import IconManager

from ChemDoE.utils.keyboard_shortcuts import add_input_shortcuts
from ChemDoE.utils.pages import ScrollableFrame, EasyOptionMenu


class ScriptOrganizer(tk.Frame):
    def __init__(self, page_manager, master, reaction: Reaction, **kwargs):
        super().__init__(master, **kwargs)
        self._selected_template = EasyOptionMenu(self)
        self._fill_dropdown()
        self._run_btn = ttk.Button(self, text="▶", style='Run.TButton', width=2, command=self.run)
        self._selected_template.pack(side=tk.LEFT)
        self._selected_template.on_select = self._on_select
        self._run_btn.pack(side=tk.LEFT, padx=5, pady=0)
        self._root = page_manager.root
        self._page_manager = page_manager
        self._values = {}
        self._reaction = reaction

    @property
    def values(self) -> dict:
        return self._values

    @values.setter
    def values(self, values: dict):
        self._values = values

    def run(self):
        script = self._scripts[self._selected_template.current()]
        e = ExecuteManager(self._root, self._reaction)

        def run():
            e.run(script, self._values)

        threading.Thread(target=run).start()

    def _fill_dropdown(self):
        self._scripts = ConfigManager().load_scripts()
        self._selected_template.values = [x['name'] for x in self._scripts] + ["🛠 Edit configurations", '📖 How to?']
        self._selected_template.insert_separator(len(self._selected_template.values) - 2)
        self._set_last_run()

    def _set_last_run(self):
        rt = ConfigManager().get('Last', 'run_template')
        idx = 0
        if rt is not None:
            idx = next((i for i, x in enumerate(self._scripts) if x['id'] == rt), 0)
        self._selected_template.current(idx)

    def _on_select(self, val, idx):
        if idx == len(self._scripts) + 1:
            webbrowser.open('https://chemdoe.readthedocs.io/en/latest/executing_scripts.html')
        if idx == len(self._scripts):
            top = ScriptManager(self._root, self._scripts)

            def manager_on_close():
                self._selected_template.silent = True
                self._fill_dropdown()
                if top.last_edited != '':
                    self._selected_template.set(top.last_edited)
                self._selected_template.silent = False
                top.destroy()

            top.protocol("WM_DELETE_WINDOW", manager_on_close)
        else:
            current_script = self._scripts[idx]
            ConfigManager().set('Last', 'run_template', current_script['id'])

    @staticmethod
    def set_style(style: ttk.Style):

        style.configure('Run.TButton', borderwidth=1, relief='solid', padding=(0, 0))
        style.configure('FileLoad.TButton', borderwidth=1, relief='solid', padding=2, font=ConfigManager.small_font)
        style.configure('Remove.TButton', background='#d9534f')

        style.map('Run.TButton',
                  foreground=[('!active', 'white'), ('pressed', 'white'), ('active', '#333333')],
                  background=[('!active', '#5cb85c'), ('pressed', '#5cb85c'), ('active', '#5cb85c')]
                  )


class ScriptForm(ScrollableFrame):
    default_file_text = "... select a file"

    def __init__(self, master, scripts, **kwargs):
        super().__init__(master, horizontal=True, **kwargs)

        self._interpreter_var = tk.StringVar()
        self._name_var = tk.StringVar(value="New Script")
        self._type_var = tk.StringVar(value="R")
        self._type_var.trace_add("write", self._change_type)
        self._input_type_var = tk.StringVar(value="CSV")
        self._output_type_var = tk.StringVar(value="CSV")
        self._file_path = None
        self._id = None
        self._scripts = scripts
        self._on_save: Callable[[dict], None] = lambda x: None

        frame = ttk.Frame(self.scrollable_frame, padding=(5), style="Inner.TFrame")
        frame.pack(expand=True)

        row = 0

        ttk.Label(frame, text="Name:").grid(row=row, column=0, pady=5, sticky="w")
        names_entry = ttk.Entry(frame, textvariable=self._name_var)
        names_entry.grid(row=row, column=1, pady=5, sticky="we", padx=5)
        add_input_shortcuts(names_entry)

        row += 1

        # Username label and entry
        ttk.Label(frame, text="Script type:").grid(row=row, column=0, pady=5, sticky="w")
        ttk.Combobox(frame, values=['R', 'Python'], textvariable=self._type_var, state="readonly").grid(row=row, column=1, pady=5, padx=5,
                                                                                      sticky="we")

        row += 1

        # Username label and entry
        ttk.Label(frame, text="Interpreter:").grid(row=row, column=0, pady=5, sticky="w")
        self._interpreter_select = ttk.Combobox(frame, values=[], textvariable=self._interpreter_var)
        self._interpreter_select.grid(row=row, column=1, pady=5, padx=5, sticky="we")

        row += 1

        # Username label and entry
        ttk.Label(frame, text="Script path:").grid(row=row, column=0, pady=5, sticky="w")
        input_frame = ttk.Frame(frame)
        self._file_input = ttk.Button(input_frame, text=self.default_file_text, command=self.open_file,
                                      style="FileLoad.TButton")
        input_frame.grid(row=row, column=1, sticky="we", pady=5)
        self._file_input.pack(side="left")
        self._copy_button = ttk.Button(input_frame, text='Open', command=self.copy_file_dir,
                                       style="FileLoad.TButton")
        self._copy_button.pack(side="left")
        self._copy_button.config(state=tk.DISABLED)
        row += 1

        # Username label and entry
        ttk.Label(frame, text="INPUT type:").grid(row=row, column=0, pady=5, sticky="w")
        ttk.Combobox(frame, values=['CSV', 'JSON'], textvariable=self._input_type_var, state="readonly").grid(row=row, column=1, pady=5,
                                                                                            padx=5, sticky="we")

        row += 1

        # Username label and entry
        ttk.Label(frame, text="OUTPUT type:").grid(row=row, column=0, pady=5, sticky="w")
        ttk.Combobox(frame, values=['CSV', 'JSON'], textvariable=self._output_type_var, state="readonly").grid(row=row, column=1, pady=5,
                                                                                             padx=5, sticky="we")

        # You can also add buttons, entries, etc. to the subwindow
        bt_frame = ttk.Frame(self.scrollable_frame)
        bt_frame.pack(pady=10)
        close_button = ttk.Button(bt_frame, text="Save", command=self.save)
        close_button.pack(side='left')
        self.rm_btn = ttk.Button(bt_frame, text="Remove", command=self.remove, style="Remove.TButton")

    def copy_file_dir(self):
        foldername = str(self._file_path)
        if sys.platform.startswith('linux'):
            os.system('xdg-open "%s"' % foldername)
        elif sys.platform.startswith('win32'):
            os.startfile(foldername)
        elif sys.platform.startswith('foldername'):
            os.system('open "%s"' % foldername)

    @property
    def on_save(self) -> Callable[[dict], None]:
        return self._on_save

    @on_save.setter
    def on_save(self, value: Callable[[dict], None]):
        self._on_save = value

    def set_value(self, as_dict: dict):
        self._as_dict = as_dict
        self._set_values(**as_dict)

    def _set_values(self, id, name, file_type, input, file, interpreter=None, output=None):

        if interpreter is None:
            interpreter = file_type.lower()
        if output is None:
            output = input
        self._set_file(file)
        if id is None or id.startswith("__default_"):
            self._id = None
            self.rm_btn.pack_forget()
        else:
            self.rm_btn.pack(side='left', padx=5)
            self._id = str(id)
        self._name_var.set(name)
        self._type_var.set(file_type)
        self._interpreter_var.set(interpreter)
        self._input_type_var.set(input)
        self._output_type_var.set(output)

    def to_dict(self, values=None):
        if values is None:
            values = {}

        if self._id is None:
            self._id = values['id'] = uuid.uuid4().__str__()
        else:
            values['id'] = self._id

        values['name'] = self._name_var.get()
        if values['name'].startswith('[Default] '):
            values['name'] = values['name'][len('[Default] '):]

        values['file_type'] = self._type_var.get()
        values['input'] = self._input_type_var.get()
        values['output'] = self._output_type_var.get()
        values['file'] = self._file_path.__str__()
        values['interpreter'] = self._interpreter_var.get()
        return values

    def save(self):
        if self._id is None:
            values = self.to_dict()
            self.set_value(values)
            self._scripts.append(values)
        else:
            values = self.to_dict(self._as_dict)
        ConfigManager().save_scripts(self._scripts)
        self._on_save(values)

    def remove(self):
        if self._id is None:
            return
        values = self.to_dict()
        self._scripts.remove(values)
        values['id'] = None
        self.set_value(values)
        ConfigManager().save_scripts(self._scripts)
        self._on_save(None)

    def open_file(self):
        # Open a file dialog and return the selected file's path

        top = self.winfo_toplevel()

        filename = filedialog.askopenfilename(
            title="Select a File",
            filetypes=(("Python files", "*.py"), ("R files", "*.R"))
        )

        top.lift()  # Bring it to the front
        top.attributes("-topmost", True)  # Keep it on top
        top.after(100, lambda: top.attributes("-topmost", False))

        if filename:
            self._set_file(filename)

            # You can now open and process the file as needed

    def _change_type(self, _a: str, _b: str, _c: str):
        if self._type_var.get() == 'Python':
            options = ConfigManager().python_interpreters + [self._type_var.get().lower()]
        elif self._type_var.get() == 'R':
            options = ConfigManager().r_interpreters + [self._type_var.get().lower()]
        else:
            options = []
        self._interpreter_select.config(values=options)
        self._interpreter_select.current(0)
        font = tkFont.Font(font=self._interpreter_select.cget("font"))
        max_width = max(font.measure(option) for option in options)  # Get max text width in pixels
        self._interpreter_select.config(width=max_width // font.measure("0") + 2)

    def _set_file(self, filename):
        self._file_path = Path(filename)
        bt_text = filename
        if self._file_path.suffix.lower() == '.py':
            self._type_var.set('Python')
        elif self._file_path.suffix.lower() == '.r':
            self._type_var.set('R')
        else:
            bt_text = self.default_file_text
            self._file_path = None
        self._file_input.config(text=bt_text, width=len(bt_text) + 5)
        if self._file_path is not None:
            self._copy_button.config(state=f'!{tk.DISABLED}')
        if self._file_path is None:
            self._copy_button.config(state=tk.DISABLED)


class ScriptManager(tk.Toplevel):

    def __init__(self, root, scripts):
        super().__init__(root)
        self.title("Run configurations manager")

        w, h = root.winfo_screenwidth(), root.winfo_screenheight()
        self.geometry("%dx%d" % (min(w - 100, 1000), min(h - 100, 1000)))

        self.transient(root)

        self._scripts = scripts
        self._sf: Optional[ScriptForm] = None
        self._last_edited: str = ''

        # Add some content to the subwindow
        label = ttk.Label(self, text="Edit Run configurations")
        label.pack(fill="x", pady=5, padx=5)

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(paned_window, relief=tk.SUNKEN)
        paned_window.add(left_frame, weight=1)

        self._tree = ttk.Treeview(left_frame)
        self._tree.heading("#0", text="Run configurations", anchor="w")

        self._tree.insert("", "end", text=f'Add new', open=True,
                          image=IconManager().PLUS_ICON,
                          values=('_', 'Add_new'))

        self._python_node = self._tree.insert("", "end", text=f'Python', open=True,
                                              image=IconManager().PYTHON,
                                              values=('_', 'PYTHON'))

        self._r_node = self._tree.insert("", "end", text=f'R', open=True,
                                         image=IconManager().R,
                                         values=('_', 'R'))

        self._fill_scripts()

        self._tree.pack(fill=tk.BOTH)

        self._tree.bind("<ButtonRelease-1>", self._select_config)

        self._right_frame = ttk.Frame(paned_window, width=500, relief=tk.SUNKEN)
        paned_window.add(self._right_frame, weight=2)

    def _fill_scripts(self):
        for parent_node in [self._r_node, self._python_node]:
            for child in self._tree.get_children(parent_node):
                self._tree.delete(child)

        for s in self._scripts:
            if s['file_type'] == 'R':
                self._tree.insert(self._r_node, tk.END, text=s['name'], values=(s['id'], s['file_type']))
            elif s['file_type'] == 'Python':
                self._tree.insert(self._python_node, tk.END, text=s['name'], values=(s['id'], s['file_type']))

    def _on_save(self, as_dict: dict):
        self._fill_scripts()
        if as_dict:
            self._last_edited = as_dict.get('name', '')

    @property
    def last_edited(self) -> str:
        return self._last_edited

    def _select_config(self, event):
        """Handles single-click event."""
        selected_item = self._tree.focus()  # Get selected item
        item_text = self._tree.item(selected_item, "values")
        if len(item_text) < 2:
            return
        if item_text[1] == 'Add_new':
            if self._sf:
                self._sf.destroy()
            self._sf = ScriptForm(self._right_frame, self._scripts)
            self._sf.pack(fill=tk.BOTH, expand=True)
        elif item_text[0] != '_':
            if not self._sf:
                self._sf = ScriptForm(self._right_frame, self._scripts)
                self._sf.pack(fill=tk.BOTH, expand=True)

            self._sf.set_value(next((x for x in self._scripts if x['id'] == item_text[0])))

        else:
            return
        self._sf.on_save = self._on_save
