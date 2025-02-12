from tkinter import ttk
import tkinter as tk
from typing import Optional

from chemotion_api import Instance

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

    def _on_canvas_configure(self, event):
        # Set the inner frame's width to match the canvas's width.
        self.canvas.itemconfig(self.window_item, width=event.width)

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
    def __init__(self, instance: Instance):
        super().__init__()
        self.instance = instance
        self.toolbar: Optional[ttk.Frame] = None

    def _logout(self):
        from ChemDoE.login_manager import LoginManager
        ConfigManager().set("Chemotion", "host", '', commit=False)
        ConfigManager().set("Chemotion", "user", '', commit=False)
        ConfigManager().set("Chemotion", "token", '')
        self.page_manager.start_page(LoginManager())

    def render(self, container: ttk.Frame):
        # Create a toolbar frame at the top
        toolbar =  ttk.Frame(container, padding=0)
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
        self.toolbar = ttk.Frame(toolbar, padding=0)
        self.toolbar.pack(side="left", padx=5)

        logout_button = ttk.Button(toolbar, text="Logout", style="Logout.TButton", command=self._logout)
        logout_button.pack(side="right", padx=5)

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
