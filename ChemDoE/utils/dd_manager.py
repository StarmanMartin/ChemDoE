from tkinter import ttk
import tkinter as tk
from typing import Callable


class DragManager():
    def __init__(self, tree: ttk.Treeview, root: tk.Tk):
        self.drag_window = None
        self.tree = tree
        self.dragged_item = None
        self.root = root

        self.tree.bind("<ButtonPress-1>", self._on_start, True)
        self.tree.bind("<B1-Motion>", self._on_drag, True)
        self.tree.bind("<ButtonRelease-1>", self._on_drop, True)
        self.tree.configure(cursor="hand1")

        self.key_pressed = False
        self._on_drag_start = lambda x: True
        self._on_drop_handler = []

    @property
    def on_drag_start(self) -> Callable[[str],bool]:
        return self._on_drag_start

    @on_drag_start.setter
    def on_drag_start(self, value: Callable[[str],bool]):
        self._on_drag_start = value


    def on_drop_in_target(self, target: tk.Widget, value: Callable[[str, tk.Widget],bool]):
        self._on_drop_handler.append((target, value))

    def _on_start(self, event):
        self.key_pressed = True
        self.root.after(100, self._start_dragging, event)

    def _start_dragging(self, event):
        if not self.key_pressed or not self.tree.winfo_exists():
            return

        selection = self.tree.selection()[0]
        if not selection or not self._on_drag_start(selection):
            return
        self.dragged_item = selection
        dragged_text = self.tree.item(selection, "text")
        self.drag_window = tk.Toplevel(self.root)
        self.drag_window.overrideredirect(True)
        self.drag_window.geometry(f"100x30+{event.x_root}+{event.y_root}")

        label = tk.Label(self.drag_window, text=dragged_text, background="lightgray", relief="solid", borderwidth=0)
        label.pack(fill="both", expand=True)

        # that represents what is being dragged.
        pass

    def _on_drag(self, event):
        # you could use this method to move a floating window that
        # represents what you're dragging
        if self.drag_window:
            self.drag_window.geometry(f"100x30+{event.x_root}+{event.y_root}")

    def _on_drop(self, event):
        self.key_pressed = False
        if self.drag_window is None:
            return
        # find the widget under the cursor
        x, y = event.widget.winfo_pointerxy()
        self.drag_window.destroy()
        self.drag_window = None
        first_target = event.widget.winfo_containing(x, y)
        for goal_target, handler in self._on_drop_handler:
            target = first_target
            found = False
            while target:
                found |= target == goal_target
                if found:
                    break
                target = target.master
            if found:
                try:
                    handler(self.dragged_item, target)
                except:
                    pass
                return
