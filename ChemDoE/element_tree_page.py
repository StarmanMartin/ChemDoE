import threading
from tkinter import ttk
import tkinter as tk
from typing import Optional, Literal

from chemotion_api import Reaction, Sample
from chemotion_api.collection import Collection, RootCollection

from ChemDoE.icons import IconManager
from ChemDoE.utils.pages import ToolBarPage
from ChemDoE.utils.keyboard_shortcuts import add_placeholder


class ElementTreePage(ToolBarPage):
    number_of_elements_per_page = 10
    search_placeholder = "Enter search text..."

    class TreeElement:
        def __init__(self, title: str):
            self.title = title
            self.tree_node: Optional[str] = None

    class TreeElementElement(TreeElement):
        def __init__(self, rea: Sample | Reaction):
            if isinstance(rea, Sample):
                super().__init__(f"{rea.short_label}: {rea.molecule['cano_smiles']}")
            else:
                super().__init__(f"{rea.short_label}: {rea.name}")

            self.rea = rea


    class TreeElementCollection(TreeElement):
        def __init__(self, col: Collection | RootCollection):
            super().__init__(col.label)
            self.loaded = False
            self.col = col
            self.children: list[ElementTreePage.TreeElementCollection] = []
            self.elements: list[ElementTreePage.TreeElementElement] = []

    def __init__(self, element_type: Literal['Reaction', 'Sample'] = 'Reaction'):
        super().__init__()
        self._tree_structor = ElementTreePage.TreeElementCollection(self.instance.get_root_collection())
        self._tree_structor.tree_node = ""
        self._search_var = tk.StringVar()
        self._collection_registry: dict[str, ElementTreePage.TreeElementCollection] = {}
        self._search_task_id = None
        self._element_type = element_type


    def render(self, container: ttk.Frame):
        super().render(container)
        entry = ttk.Entry(container, textvariable=self._search_var)
        entry.pack(fill="x", padx=5, pady=2)
        entry.bind("<KeyRelease>", lambda e: self._search_tree())
        add_placeholder(entry, self.search_placeholder)

        self.paned_window = ttk.PanedWindow(container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(self.paned_window, width=200, relief=tk.SUNKEN)
        self.paned_window.add(left_frame, weight=3)  # weight allows resizing
        self._render_collection_tree(left_frame)

    def _render_collection_tree(self, container: ttk.Frame):
        self.collection_tree = ttk.Treeview(container)

        self.collection_tree.heading("#0", text=f"Collections & {self._element_type}", anchor="w")
        self._tree_structor.children = self._load_tree(self._tree_structor.col)
        self._fill_tree(self._tree_structor)

        self.collection_tree.bind("<<TreeviewOpen>>", self._on_open)

        self.collection_tree.bind("<ButtonRelease-1>", self._on_element_click)

        self.collection_tree.pack(expand=True, fill="both")

    def set_style(self, style: ttk.Style):
        super().set_style(style)
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#ffffff", foreground="#000000",
                        borderwidth=0, relief="flat")
        style.map("Treeview.Heading", background=[("active", "#ffffff")], foreground=[("active", "#000000")])
        style.configure("Reaction.Treeview", rowheight=30)

    def _search_tree(self):
        if self._search_task_id is not None:
            self.page_manager.root.after_cancel(self._search_task_id)
        self._search_task_id = self.page_manager.root.after(500, self._filter_tree)

    def _filter_tree(self, root = None, disable_detach:bool = False):
        """Filter treeview based on search input."""
        if root is None:
            root = self._tree_structor
        if isinstance(root, ElementTreePage.TreeElementElement):
            return False
        query = self._search_var.get().lower()
        if len(query) < 2:
            disable_detach = True
        res = False
        for item in root.children + root.elements:
            match = query in item.title.lower()
            if disable_detach or match or self._filter_tree(item):
                if disable_detach or match:
                    self._filter_tree(item, True)
                res = True
                try:# Check if query matches any column
                    self.collection_tree.reattach(item.tree_node, root.tree_node, "end")  #
                except tk.TclError:
                    pass
                if not disable_detach and isinstance(item, ElementTreePage.TreeElementCollection):
                    self.collection_tree.item(item.tree_node, open=True)  #
                    self._load_on_open(item.tree_node)
            else:
                self.collection_tree.detach(item.tree_node)
        return res

    def _load_tree(self, root_col):
        root = []
        for col in root_col.children:
            te = self.TreeElementCollection(col)
            self._collection_registry[str(col.id)] = te
            root.append(te)
            te.children = self._load_tree(col)
        return root

    def _fill_tree(self, root_col: TreeElementCollection, parent="", filter_label=None):
        ret = []
        for te in root_col.children:
            te.tree_node = self.collection_tree.insert(parent, "end", text=te.title, open=False,
                                                  image=IconManager().FOLDER_ICON,
                                                  values=(str(te.col.id), 'Collection'))
            self._fill_tree(te, te.tree_node, filter_label)

            self.collection_tree.insert(te.tree_node, "end", text=f'Create new {self._element_type}', open=False,
                                        image=IconManager().PLUS_ICON,
                                        values=(str(te.col.id), 'NewElement'))
            self._load_on_open(te.tree_node)

        return ret


    def _load_next_page(self, te: TreeElementCollection):
        try:
            if self._element_type == 'Reaction':
                elements = te.col.get_reactions(self.number_of_elements_per_page)
                icon = IconManager().REACTION_ICON
            else:
                elements = te.col.get_samples(self.number_of_elements_per_page)
                icon = IconManager().SAMPLE_ICON
            current_length = len(te.elements)
            all_elements = len(elements)
            if all_elements == current_length:
                return False

            if not self.is_visible:
                return
            self.page_manager.root.after(0, lambda te: self.collection_tree.item(te.tree_node, text=te.title + " ⏳"), te)

            end_length = min(all_elements, current_length + self.number_of_elements_per_page)
            for i in range(current_length, end_length):
                if not self.is_visible:
                    return
                re = ElementTreePage.TreeElementElement(elements[i])
                te.elements.append(re)
                def add_node(re, te):
                    if self.is_visible:
                        re.tree_node = self.collection_tree.insert(te.tree_node, "end", text=re.title, open=False,
                                                image=icon,
                                                values=(str(re.rea.id), "Element"))
                self.page_manager.root.after(0, add_node, re, te)

            if self.is_visible:
                self.page_manager.root.after(0, lambda te: self.collection_tree.item(te.tree_node, text=te.title ), te)
            if len(te.elements) < all_elements:
                self.page_manager.root.after(0, lambda te: self.collection_tree.insert(te.tree_node, "end", text="...Load more...", open=False, image=icon, values=(str(te.col.id), "LOAD")), te)


        except tk.TclError:
            return


    def _on_open(self, event):
        """Triggered when a tree item is opened (expanded)."""

        item = self.collection_tree.focus()  # Get currently opened item
        self._load_on_open(item)

    def _load_on_open(self, item):
        vals = self.collection_tree.item(item, 'values')
        if len(vals) > 1 and vals[1] == 'Collection':
            te: ElementTreePage.TreeElementCollection = self._collection_registry[vals[0]]
            if not te.loaded:
                te.loaded = True
                thread = threading.Thread(target=self._load_next_page, args=(te,), daemon=True)
                thread.start()

    def _on_element_click(self, event):
        """Triggered when a tree item is opened (expanded)."""

        item = self.collection_tree.focus()  # Get currently opened item
        self._load_on_open(item)
        vals = self.collection_tree.item(item, 'values')
        if len(vals) < 2:
            return
        if vals[1] == 'LOAD':
            te: ElementTreePage.TreeElementCollection = self._collection_registry[vals[0]]
            te.loaded = True
            thread = threading.Thread(target=self._load_next_page, args=(te,), daemon=True)
            thread.start()
            self.collection_tree.delete(item)
        elif vals[1] == 'NewElement':
            te: ElementTreePage.TreeElementCollection = self._collection_registry[vals[0]]
            self.create_new(te.col)
        elif vals[1] == 'Element':
            if  hasattr(self, 'select_element'):
                parent = self.collection_tree.parent(item)
                col_id = self.collection_tree.item(parent, 'values')[0]
                te: ElementTreePage.TreeElementCollection = self._collection_registry[col_id]
                if self._element_type == 'Reaction':
                    element = self.instance.get_reaction(int(vals[0]))
                else:
                    element = self.instance.get_sample(int(vals[0]))
                self.select_element(te.col, element)
    
    def create_new(self, collection):
        pass