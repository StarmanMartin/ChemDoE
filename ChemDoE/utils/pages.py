import threading
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import Combobox
from typing import Optional

from chemotion_api import Reaction

from ChemDoE.config import ConfigManager
from ChemDoE.icons import IconManager
from ChemDoE.utils.page_manager import Page


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame that can be embedded in other widgets.
    It creates a canvas with a vertical scrollbar and places a frame inside the canvas.
    """

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create a canvas widget inside the frame
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill="both", expand=True)

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        # Configure the canvas to use the scrollbar
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas which will hold the content
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Create a window inside the canvas to hold the inner frame
        self.window_item = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")

        # Update the scrollregion of the canvas whenever the size of the inner frame changes
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Bind the canvas's resize event to update the width of the inner frame.
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )

        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)

    def destroy(self):
        self._unbound_to_mousewheel(None)
        self.canvas.destroy()
        super().destroy()

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_scroll)
        self.canvas.bind_all("<Button-4>", self._on_mouse_scroll)
        self.canvas.bind_all("<Button-5>", self._on_mouse_scroll)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_canvas_configure(self, event):
        # Set the inner frame's width to match the canvas's width.
        self.canvas.itemconfig(self.window_item, width=event.width)

    def _on_mouse_scroll(self, event):
        """Enable scrolling with mouse wheel"""
        if event.num == 4:  # Scroll Up (Linux)
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Scroll Down (Linux)
            self.canvas.yview_scroll(1, "units")
        elif event.delta:  # Windows & macOS
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")


class ListRow(tk.Frame):
    def __init__(self, parent, icon, title, subtitle, delete_callback):
        super().__init__(parent, bg="white", padx=5, pady=5)

        # Icon Label (Using Emoji as Placeholder)
        self.icon_label = tk.Label(self, image=icon, font=("Arial", 16), bg="white")
        self.icon_label.pack(side="left", padx=5)

        # Text Frame (Title + Subtitle)
        text_frame = tk.Frame(self, bg="white")
        text_frame.pack(side="left", fill="both", expand=True)

        self.title_label = tk.Label(text_frame, text=title, font=("Arial", 12, "bold"), bg="white")
        self.title_label.pack(anchor="w")

        self.subtitle_label = tk.Label(text_frame, text=subtitle, font=("Arial", 10), fg="gray", bg="white")
        self.subtitle_label.pack(anchor="w")

        # Delete Button
        self.delete_button = ttk.Button(self, image=IconManager().TRASH, width=3, command=lambda: delete_callback(self))
        self.delete_button.pack(side="right", padx=5)


class ToolBarPage(Page):
    fav_dropdown: Combobox

    def __init__(self):
        super().__init__()
        self._fav_reactions = None
        self.instance = ConfigManager().chemotion
        self.toolbar: Optional[ttk.Frame] = None

    def _logout(self):
        from ChemDoE.login_manager import LoginManager
        ConfigManager().set("Chemotion", "host", '', commit=False)
        ConfigManager().set("Chemotion", "user", '', commit=False)
        ConfigManager().set("Chemotion", "token", '')
        self.page_manager.start_page(LoginManager())

    def render(self, container: ttk.Frame):
        # Create a toolbar frame at the top
        toolbar = ttk.Frame(container, padding=0)
        toolbar.pack(side="top", fill="x")

        if self.page_manager.can_go_back():
            back_btn = ttk.Button(toolbar, style="NAV.Active.TButton", image=IconManager().BACK_ICON,
                                  command=lambda *x: self.page_manager.go_back())
        else:
            back_btn = ttk.Button(toolbar, style="NAV.NotActive.TButton", image=IconManager().BACK_ICON)

        if self.page_manager.can_go_forward():
            forward_btn = ttk.Button(toolbar, style="NAV.Active.TButton", image=IconManager().FORWARD_ICON,
                                     command=lambda *x: self.page_manager.go_forward())
        else:
            forward_btn = ttk.Button(toolbar, style="NAV.NotActive.TButton", image=IconManager().FORWARD_ICON)
        back_btn.image = IconManager().BACK_ICON
        forward_btn.image = IconManager().FORWARD_ICON
        back_btn.pack(side="left", padx=5)
        forward_btn.pack(side="left", padx=5)

        self._fav_reactions = []
        # Create a Combobox with the list of options
        self.fav_dropdown = ttk.Combobox(toolbar, values=[])
        self.fav_dropdown.pack(side="left", padx=5, pady=0)
        self.fav_dropdown.bind("<<ComboboxSelected>>", self._on_fav_select)
        self.toolbar = ttk.Frame(toolbar, padding=0)
        self.toolbar.pack(side="left", padx=5)

        logout_button = ttk.Button(toolbar, text="Logout", style="Logout.TButton", command=self._logout)
        logout_button.pack(side="right", padx=5)
        self.update_fav_dropdown()

    def update_fav_dropdown(self):
        def load():
            self._fav_reactions = [(-1, 'Favorites')] + ConfigManager().favorites_with_names
            self._page_manager.root.after(0, done_load)
        def done_load():
            self.fav_dropdown.config(values=[x[1] for x in self._fav_reactions])
            if hasattr(self, 'reaction'):
                idx = next((i for i, x in enumerate(self._fav_reactions) if x[0] == self.reaction.id), 0)
            else:
                idx = 0
            self.fav_dropdown.current(idx)

        t = threading.Thread(target=load)
        t.daemon = True
        t.start()

    def _on_fav_select(self, event):
        idx = self.fav_dropdown.current()
        id = self._fav_reactions[idx][0]
        if id > 0:
            from ChemDoE.new_reaction import NewReaction
            reaction = ConfigManager().chemotion.get_reaction(id)
            try:
                collection_id = reaction.json_data['tag']['taggable_data']['collection_labels'][0]["id"]
                col = ConfigManager().chemotion.get_root_collection().find(id=collection_id)[0]
            except (KeyError, IndexError):
                col = ConfigManager().chemotion.get_root_collection()
            self._page_manager.set_page(NewReaction(col, reaction))

    def set_style(self, style: ttk.Style):

        button_default = dict(
            padding=2,  # Left, Top, Right, Bottom
            borderwidth=0,  # Removes all borders
            relief="flat"
        )

        style.configure("Logout.TButton", background="#f54260",
                        foreground="white", **button_default)
        style.configure("NAV.Active.TButton", **button_default)
        style.configure("NAV.NotActive.TButton", background="#756b6d", foreground="lightgray", **button_default)
        style.map("NAV.NotActive.TButton", background=[("active", "#756b6d")], foreground=[("active", "lightgray")])
