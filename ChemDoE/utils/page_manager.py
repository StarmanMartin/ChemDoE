from tkinter import ttk
from abc import ABC, abstractmethod
from typing import Optional
import tkinter as tk


def validate_float(P):
    if validate_numeric(P):
        return True
    try:
        float(P)
        return True
    except ValueError:
        return False


def validate_numeric(P):
    """Allow only digits"""
    return P.isdigit() or P == ""

class PageManager:
    def __init__(self, root: tk.Tk):
        self.validators = {}
        self._root = root
        self.page: Optional[Page] = None
        self.outer_frame = ttk.Frame(root, style="Outer.TFrame")
        self.outer_frame.pack(fill="both", expand=True)
        self._history: list[Page] = []
        self._history_idx = 0
        self._is_running = False

    @property
    def root(self) -> tk.Tk:
        return self._root

    @property
    def history(self):
        return self._history


    def can_go_back(self, n: int = 1) -> bool:
        return self._history_idx > n - 1

    def can_go_forward(self, n: int = 1) -> bool:
        return self._history_idx < len(self._history) - n

    def start_page(self, page: "Page"):
        self._history = []
        if not self._is_running:
            self.validators["numeric"] = (self._root.register(validate_numeric), "%P")
            self.validators["float"] = (self._root.register(validate_float), "%P")
        self.set_page(page)
        if not self._is_running:
            self._root.mainloop()
        self._is_running = True



    def set_page(self, page: "Page"):
        self._history = self._history[:self._history_idx + 1]
        self._history.append(page)
        self.go_to_history_idx(len(self._history) - 1)

    def go_back(self):
        if not self.can_go_back():
            raise RuntimeError("Cannot go back to previous page!")
        return self.go_to_history_idx(self._history_idx - 1)

    def go_forward(self):
        if not self.can_go_forward():
            raise RuntimeError("Cannot go forward to next page!")
        return self.go_to_history_idx(self._history_idx + 1)

    def go_to_history_idx(self, idx: int = -1):
        page = self._history[idx]
        self._history_idx = idx
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", font=("Arial", 12), background="#ffffff", foreground="black")
        style.map("TEntry", fieldbackground=[("focus", "white"), ("!focus", "lightgray")])

        if self.page:
            self.page.is_visible = False
            self.page.leave()
        self.page = page
        self.page.is_visible = True
        page.page_manager = self

        self._clear_frame()

        page.set_style(style)
        page.render(self.outer_frame)

    def _clear_frame(self):
        for widget in self.outer_frame.winfo_children():
            widget.destroy()
            del widget


class Page(ABC):

    def __init__(self):
        self.is_visible = False
        self._page_manager: Optional[PageManager] = None

    def leave(self):
        pass

    @property
    def page_manager(self) -> PageManager:
        return self._page_manager

    @page_manager.setter
    def page_manager(self, value: PageManager):
        if not isinstance(value, PageManager):
            raise TypeError(f"page_manager {type(value)} not supported")
        self._page_manager = value

    @abstractmethod
    def render(self, root: ttk.Frame):
        ...

    @abstractmethod
    def set_style(self, style: ttk.Style):
        ...
