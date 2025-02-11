import os.path
import threading
from tkinter import ttk
import tkinter as tk
from typing import Optional

from PIL import Image, ImageTk

from chemotion_api import Instance, Reaction
from chemotion_api.collection import Collection

from ChemDoE.config import ConfigManager
from ChemDoE.utils.pages import ToolBarPage
from ChemDoE.utils.MdField import MdField
from ChemDoE.utils.keyboard_shortcuts import add_placeholder


class StartPage(ToolBarPage):
    number_of_reaction_per_page = 20
    search_placeholder = "Enter search text..."

    def __init__(self, instance: Instance):
        super().__init__(instance)

        icon_path = os.path.join(os.path.dirname(__file__), 'icons/fixed/folder.svg.png')
        self._folder_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((16, 16)))
        icon_path = os.path.join(os.path.dirname(__file__), 'icons/fixed/flask.svg.png')
        self._reaction_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((14, 14)))
        icon_path = os.path.join(os.path.dirname(__file__), 'icons/fixed/plus.svg.png')
        self._plus_icon = ImageTk.PhotoImage(Image.open(icon_path).resize((14, 14)))
        self._search_var = tk.StringVar()
        self.right_frame: Optional[tk.Frame] = None
        self.collection_tree: Optional[ttk.Treeview] = None
        self.reaction_tree: Optional[ttk.Treeview] = None
        self._reactions: Optional[list[Reaction]] = None
        self._collection: Optional[Collection] = None
        self.loading: Optional[tk.Text] = None

    def render(self, container: ttk.Frame):
        super().render(container)

        # text = MdField(container)
        # text.pack(fill="both", expand=True)
        # st = os.path.join(os.path.dirname(__file__), 'start.md')
        # text.set_md_file(st)
        entry = ttk.Entry(container, textvariable=self._search_var)
        entry.pack(fill="x", padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self._filter_trees())
        add_placeholder(entry, self.search_placeholder)

        self.paned_window = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Left Frame
        left_frame = ttk.Frame(self.paned_window, width=200, relief=tk.SUNKEN)
        self.paned_window.add(left_frame, weight=3)  # weight allows resizing

        col_id = ConfigManager.get("Last", "Collection")
        if col_id is not None:
            # Right Frame
            self._reactions = []
            self._render_reaction_tree(col_id)

        self._render_collection_tree(left_frame)

    def set_style(self, style: ttk.Style):
        super().set_style(style)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#ffffff", foreground="#000000",
                        borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("active", "#ffffff")], foreground=[("active", "#000000")])
        style.configure("Reaction.Treeview", rowheight=30)

    def _load_next_page(self):
        reactions = self._collection.get_reactions(self.number_of_reaction_per_page)
        current_length = len(self._reactions)
        all_reactions = len(reactions)
        if all_reactions == current_length:
            return False
        end_length = min(all_reactions, current_length + self.number_of_reaction_per_page)
        for i in range(current_length, end_length):
            self._reactions.append(reactions[i])
        return len(self._reactions) < all_reactions

    def _render_reaction_tree(self, col_id):
        if self.right_frame is None:
            self.right_frame = ttk.Frame(self.paned_window, width=200, relief=tk.SUNKEN)
            self.paned_window.add(self.right_frame, weight=2)  # Bigger weight makes it larger
        self._collection = self.instance.get_root_collection().find(id=int(col_id))[0]

        loading = tk.Label(self.right_frame, text="Loading...", font=("Arial", 14), background="white")
        loading.place(relx=0.5, rely=0.1, anchor="n")

        def set_tree(add_button):
            for widget in self.right_frame.winfo_children():
                widget.destroy()
            self.reaction_tree = ttk.Treeview(self.right_frame, style="Reaction.Treeview")
            self.reaction_tree.heading("#0", text=f"Reactions in {self._collection.label}", anchor="w")
            self._fill_reaction_tree()
            self.reaction_tree.pack(expand=True, fill="both")
            self.reaction_tree.bind("<Double-Button-1>", self._on_reaction_open)
            if add_button:
                next = ttk.Button(self.right_frame, text="Load more...",
                                  command=lambda *x: self._render_reaction_tree(col_id))
                next.pack(pady=10, padx=10)

        def background_task():
            add_button = self._load_next_page()
            self.page_manager.root.after(0, set_tree, add_button)

        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()

    def _render_collection_tree(self, container: ttk.Frame):
        self.collection_tree = ttk.Treeview(container)

        self.collection_tree.heading("#0", text="Collections", anchor="w")
        rc = self.instance.get_root_collection()
        self._fill_collection_tree(rc)

        self.collection_tree.bind("<ButtonRelease-1>", self._on_collection_click)

        self.collection_tree.pack(expand=True, fill="both")

    def _filter_collection_tree(self) -> None:
        """Filter treeview based on search input."""
        for item in self.collection_tree.get_children():
            self.collection_tree.delete(item)
        self._fill_collection_tree(self.instance.get_root_collection())

    def _filter_reaction_tree(self) -> None:
        """Filter treeview based on search input."""
        for item in self.reaction_tree.get_children():
            self.reaction_tree.delete(item)
        self._fill_reaction_tree()

    def _fill_collection_tree(self, root_col, parent="", filter_label=None):
        ret = False
        if filter_label is None:
            filter_label = self._search_var.get().lower()
            if filter_label == self.search_placeholder.lower():
                filter_label = ''
        for col in root_col.children:

            folder1 = self.collection_tree.insert(parent, "end", text=col.label, open=True, image=self._folder_icon,
                                                  values=(col.id,))
            has_added = self._fill_collection_tree(col, folder1, filter_label)
            if filter_label in col.label.lower() or has_added:
                ret = True
            else:
                self.collection_tree.delete(folder1)
        return ret

    def _fill_reaction_tree(self, filter_label=None) -> None:
        if filter_label is None:
            filter_label = self._search_var.get().lower()
            if filter_label == self.search_placeholder.lower():
                filter_label = ''

        self.reaction_tree.insert("", "end", text="Create new Reaction", image=self._plus_icon,
                                 values=(str(-1), 'New Reaction'))

        for rea in self._reactions:
            rea_name = f"{rea.short_label}: {rea.name}"
            if filter_label in rea_name.lower():
                self.reaction_tree.insert("", "end", text=rea_name, image=self._reaction_icon,
                                          values=(str(rea.id), rea.properties['name']))

    def _filter_trees(self):
        self._filter_collection_tree()
        self._filter_reaction_tree()

    def _on_collection_click(self, event):
        """Handles single-click event."""
        selected_item = self.collection_tree.focus()  # Get selected item
        col = self.collection_tree.item(selected_item, "values")[0]
        ConfigManager.set("Last", "Collection", col)
        self._reactions = []
        self._render_reaction_tree(int(col))

    def _on_reaction_open(self, event):
        """Handles single-click event."""
        selected_item = self.reaction_tree.focus()  # Get selected item
        rea = self.reaction_tree.item(selected_item, "values")
        if rea[0] == '-1':
            self._create_reaction(event, self.reaction_tree)
        ConfigManager.set("Last", "Reaction", rea[0])


    def _create_reaction(self, event, tree):
        """Open an Entry widget over the clicked cell for editing."""
        item = tree.selection()[0]  # Get selected item ID
        column = tree.identify_column(event.x)  # Get column clicked
        col_index = int(column[1:]) - 1  # Convert to index
        x, y, width, height = tree.bbox(item, column)  # Get cell position

        # Create Entry widget
        self.entry = tk.Entry(self.right_frame)
        self.entry.place(x=x, y=y + tree.winfo_rooty() - self.right_frame.winfo_rooty(), width=width, height=height)

        # Insert current text and focus
        self.entry.insert(0, tree.item(item, "values")[col_index])
        self.entry.focus()

        # Bind enter key to save changes
        self.entry.bind("<Return>", lambda e: self.save_edit(item, col_index))
        self.entry.bind("<FocusOut>", lambda e: self.save_edit(item, col_index))  # Save when losing focus
