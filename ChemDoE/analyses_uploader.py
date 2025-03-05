import os
import re
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, ttk, messagebox

from chemotion_api import Reaction

from ChemDoE.config import ConfigManager
from ChemDoE.icons import IconManager
from ChemDoE.utils.dd_manager import DragManagerWidget
from ChemDoE.utils.pages import ToolBarPage, ScrollableFrame


class AnalysesUploader(ToolBarPage):
    def __init__(self, reaction: Reaction):
        super().__init__()
        self._container = []
        self.reaction = reaction
        self._folder_btn = None
        self._folder_path = None
        self._has_sub_dir = False
        self._files = []
        self._extensions = dict()
        self._is_tar = tk.BooleanVar(value=False)

    def select_directory(self):
        _folder_path = filedialog.askdirectory()
        if _folder_path:  # If a folder is selected
            self._folder_btn.config(text=f"Selected: {_folder_path}")
            self._folder_btn.config(width=len(_folder_path) + 10)
            self._folder_path = Path(_folder_path)
            self._check_sub_dirs()
            self._read_file_names()

    def render(self, container: ttk.Frame):
        super().render(container)
        mc = ttk.Frame(container, style='Background.TFrame')
        mc.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scf = ScrollableFrame(mc, horizontal=True, style='Background.TFrame')
        for i in range(4):
            self._container.append(ttk.Frame(scf.scrollable_frame, style='Step.TFrame'))

        scf.pack(fill="both", expand=True)
        self.render_1()

    def render_1(self):
        container, clean = self._clean_container(0)
        ttk.Label(container, text="1) Select a folder", style='Header.TLabel').pack(padx=5, pady=5, anchor=tk.W)
        text = ("Please select a folder in which the analysis files are located. "
                "Please note that the files can also be located in subfolders of the selected "
                "folder. In order for the automatic assignment to work, it is necessary for the "
                "naming convention to be followed and for the file names to begin with the variation names.")
        ttk.Label(container, text=text, style='Para.TLabel', wraplength=500, justify="left").pack(padx=5, pady=5,
                                                                                                  anchor=tk.W)
        self._folder_btn = ttk.Button(container, text="Select Folder", command=self.select_directory)
        self._folder_btn.pack(padx=5, pady=5, anchor=tk.W)
        clean()

    def render_2(self):
        container, clean = self._clean_container(1)
        if not self._has_sub_dir:
            ttk.Label(container, text="2) Can be skipped ", style='Header.TLabel').pack(padx=5, pady=10, anchor=tk.W)
            text = "Step 2 is only needed if the selected directory has subdirectories"
            l = ttk.Label(container, text=text, style='Para.TLabel', wraplength=500, justify="left")
            l.pack(padx=5, pady=5, anchor=tk.W)
        else:
            ttk.Label(container, text="2) How to handle subdirectories", style='Header.TLabel').pack(padx=5, pady=10,
                                                                                                     anchor=tk.W)
            text = "Select every file in the subdirectory as single file or bundle them into a Tar archive"
            l = ttk.Label(container, text=text, style='Para.TLabel', wraplength=500, justify="left")
            l.pack(padx=5, pady=5, anchor=tk.W)

            c2 = ttk.Checkbutton(container, text='As Tar archive', onvalue=True, offvalue=False, variable=self._is_tar,
                                 command=self._read_file_names)
            c2.pack(padx=5, pady=5, anchor=tk.W)
        clean()

    def render_3(self):
        container, clean = self._clean_container(2)
        ttk.Label(container, text="3) Filter File extension", style='Header.TLabel').pack(padx=5, pady=10, anchor=tk.W)
        text = "Please select the relevant file extension to upload as an analysis."
        l = ttk.Label(container, text=text, style='Para.TLabel', wraplength=500, justify="left")
        l.pack(padx=5, pady=5, anchor=tk.W)

        ext_frame = ttk.Frame(container)
        ext_frame.pack(padx=5, pady=5, anchor=tk.W)

        for ext, ext_values in self._extensions.items():
            c2 = ttk.Checkbutton(ext_frame, text=ext, onvalue=True, offvalue=False, variable=ext_values,
                                 command=self._update_ext_filter)
            c2.pack(padx=5, pady=3, anchor=tk.W)
        clean()

    def render_4(self):
        container, clean = self._clean_container(3)
        ttk.Label(container, text="4) Map Files", style='Header.TLabel').pack(padx=5, pady=10, anchor=tk.W)
        text = "Please select the relevant file extension to upload as an analysis."
        l = ttk.Label(container, text=text, style='Para.TLabel', wraplength=500, justify="left")
        l.pack(padx=5, pady=5, anchor=tk.W)

        main_frame = ttk.Frame(container, style='Move.TFrame')
        column = 0
        cols = []
        dm = DragManagerWidget(self.page_manager.root)
        for name, files in self._file_mapping.items():
            row = 0
            header = ttk.Label(main_frame, text=name, style='TableHeader.TLabel', anchor='center')
            header.grid(row=row, column=column, sticky="ew")
            dm.on_drop_in_target(header, self._on_drop_in_target)
            for file in files['files']:
                row += 1
                col = ttk.Label(main_frame, text=file, style='TableItem.TLabel')
                col.grid(row=row, column=column, sticky="nsew")
                cols.append(col)
            column += 1
        dm.set_elements(cols)

        main_frame.pack(padx=5, pady=5, anchor=tk.W)
        ttk.Button(container, text="Transfer analyses files", image=IconManager().CHEMOTION, compound="left",
                   command=self._prepare_transfer).pack(anchor="w")
        clean()

    def _prepare_transfer(self):
        win = tk.Toplevel(self.page_manager.root, background="#ffffff" )

        win.title("Transfer")
        win.transient(self.page_manager.root)
        win.wm_overrideredirect(True)
        win.attributes('-topmost', 'true')
        win.resizable(False, False)
        win_width = 500
        win_height = 200
        x = self.page_manager.root.winfo_x() + self.page_manager.root.winfo_width() // 2 - win_width // 2
        y = self.page_manager.root.winfo_y() + self.page_manager.root.winfo_height() // 2 - win_height // 2

        win.geometry(f"{win_width}x{win_height}+{x}+{y}")


        label = ttk.Label(win, wraplength=15*30, text="Are you sure you want tp transfer the analyses files", style='Header.TLabel')
        progress_bar = ttk.Progressbar(win, length=300, mode="determinate")
        button = None

        btn_row = ttk.Frame(win)
        button = ttk.Button(btn_row, text="Transfer", command=lambda: self._transfer_analyses(win ,label, progress_bar, button, close_button))
        close_button = ttk.Button(btn_row, text="Close", command=win.destroy)
        label.pack(padx=5, pady=5)
        progress_bar.pack(padx=5, pady=5)
        btn_row.pack(padx=5, pady=5)
        button.pack(padx=5, pady=5, side=tk.LEFT)
        close_button.pack(padx=5, pady=5, side=tk.LEFT)

    def _transfer_analyses(self, win, label, progress_bar, button, close_button):
        label.config(text="Start transferring analyses files")
        button.pack_forget()
        close_button.pack_forget()
        progress_bar.pack(pady=20)
        progress_bar["value"] = 0
        texts = ['Uploading Files', 'Files Uploaded', 'linking Variations', 'Saved reaction. Analyses transferred.']
        step = 100 // len(texts)


        def update_bar(i):
            progress_bar["value"] = step * (i + 1)
            label.config(text=texts[i])
            if i + 1 == len(texts):
                close_button.pack(padx=5, pady=5)

        def upload():
            ana = self.reaction.analyses
            _current_anas = [a.id for a in ana]
            today = datetime.now().isoformat()

            for name, files in self._file_mapping.items():
                if name == 'Ignore':
                    continue
                for file in files['files']:
                    analyses = ana.add_analyses(f'{file}')
                    analyses['content'] = {
                        'ops': [{'attributes': {'bold': True}, 'insert': 'Variation: '}, {'insert': f'{name}\n'},
                                {'attributes': {'bold': True}, 'insert': 'Datime: '}, {'insert': f'{today}\n'},
                                {'attributes': {'bold': True}, 'insert': 'File: '}, {'insert': f'{file}\n'}]}
                    fp = os.path.join(self._folder_path, file)
                    analyses.add_dataset(str(fp))
            self.page_manager.root.after(0, update_bar, 0)
            self.reaction.save(True)
            self.page_manager.root.after(0, update_bar, 1)
            for ana in self.reaction.analyses:
                if ana.id not in _current_anas:
                    name = ana['content']['ops'][1]['insert'][:-1]
                    if self._file_mapping[name]['variation'] is not None:
                        v = next((s for s in self.reaction.variations if
                                  s.id == self._file_mapping[name]['variation']), None)
                        if v is not None:
                            v.link_analyses(ana)
            self.page_manager.root.after(0, update_bar, 2)
            self.reaction.save(True)
            self.page_manager.root.after(0, update_bar, 3)

        threading.Thread(target=upload).start()

    def _on_drop_in_target(self, src: tk.Widget, target: tk.Widget) -> bool:
        file_name = src.cget("text")
        target_name = target.cget("text")
        for name, files in self._file_mapping.items():
            if file_name in files['files']:
                files['files'].remove(file_name)
        self._file_mapping[target_name]['files'].append(file_name)
        column = target.grid_info()['column']
        src.grid_forget()
        src.grid(row=len(self._file_mapping[target_name]['files']), column=column, sticky="nsew")
        return False

    def set_style(self, style: ttk.Style):
        super().set_style(style)
        style.configure('Header.TLabel', font=ConfigManager.header_font)
        style.configure('Para.TLabel', font=ConfigManager.normal_font)
        style.configure('Background.TFrame', background="white")
        style.configure('Step.TFrame', borderwidth=2, relief=tk.SUNKEN)
        style.configure('Move.TFrame', borderwidth=2, relief=tk.SUNKEN)
        style.configure('TableHeader.TLabel', background="#d2f7ff", font=ConfigManager.header_font, borderwidth=1,
                        relief='solid', padding=10)
        style.configure('TableItem.TLabel', borderwidth=2, relief=tk.SOLID, padding=10, background='white')

    def _update_ext_filter(self):
        self._file_mapping = {}
        v_name_reg = re.compile(pattern=r'ChemDoE: <<(.+)>>')

        def find_v_names(text):
            match = re.search(v_name_reg, text)
            if match:
                return match.group(1)
            return None

        v_names = []
        for v in self.reaction.variations:
            name = find_v_names(v.notes)
            if name is not None:
                v_names.append(name)
                self._file_mapping[name] = {'variation': v.id, 'files': []}
        self._file_mapping['Reaction'] = {'variation': None, 'files': []}
        self._file_mapping['Ignore'] = {'variation': None, 'files': []}
        v_names.sort(key=lambda x: len(x), reverse=True)
        extensions = [x for x, var in self._extensions.items() if var.get()]
        for f in self._files:
            if any(f.endswith(ext) for ext in extensions):
                added = False
                for name in v_names:
                    if os.path.basename(f).startswith(name):
                        self._file_mapping[name]['files'].append(f)
                        added = True
                        break
                if not added:
                    self._file_mapping['Reaction']['files'].append(f)

        self.render_4()

    def _read_file_names(self):
        if self._is_tar.get():
            self._read_file_names_flat()
        else:
            self._read_file_names_deep()
            if len(self._files) > 50:
                self._is_tar.set(True)
                messagebox.showerror("Error",
                                     f"Too many files were selected. {len(self._files)} are too many files")
                self._read_file_names()
                return

        ext = {}
        for f in self._files:
            filename, file_extension = os.path.splitext(f)
            _filename, file_extension_2 = os.path.splitext(filename)
            if file_extension_2 == '.tar':
                file_extension = file_extension_2 + file_extension
            ext[file_extension] = self._extensions.get(file_extension, tk.BooleanVar(value=True))

        self._extensions = ext
        self.render_2()
        self.render_3()
        self._update_ext_filter()

    def _read_file_names_flat(self):
        self._files = []
        for f in self._folder_path.iterdir():
            if f.is_file():
                self._files.append(f.name)
            elif f.is_dir():
                self._files.append(f.name + '.tar.gz')

    def _read_file_names_deep(self):
        self._files = []
        for root, dir, files in self._folder_path.walk():
            root = root.relative_to(self._folder_path)
            for file in files:
                self._files.append(str(root / file))

    def _check_sub_dirs(self):
        self._has_sub_dir = False
        for f in self._folder_path.iterdir():
            if f.is_dir():
                self._has_sub_dir = True
                return

    def _clean_container(self, idx):
        if len(self._container) > idx + 1:
            for c in self._container[idx + 1:]:
                for widget in c.winfo_children():
                    widget.destroy()
                    del widget
                c.pack_forget()
        ws = [w for w in self._container[idx].winfo_children()]

        def clean():
            for w in ws:
                w.destroy()

        self._container[idx].pack(fill="x", padx=10, pady=10)
        return (self._container[idx], clean)
