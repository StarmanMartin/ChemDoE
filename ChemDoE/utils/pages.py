import os
from tkinter import ttk
from typing import Optional

from PIL import ImageTk, Image
from chemotion_api import Instance

from ChemDoE.config import ConfigManager
from ChemDoE.utils.page_manager import Page


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
        toolbar = self.toolbar = ttk.Frame(container, padding=0)
        toolbar.pack(side="top", fill="x")

        # Add buttons to the toolbar

        icon_path_right = os.path.join(os.path.dirname(__file__), '../icons/fixed/arrow-right-circle-fill.svg.png')
        icon_path_left = os.path.join(os.path.dirname(__file__), '../icons/fixed/arrow-left-circle-fill.svg.png')
        back_icon = Image.open(icon_path_left)  # Replace with your image path
        back_icon = back_icon.resize((20, 20))  # Resize if needed
        back_icon = ImageTk.PhotoImage(back_icon)
        forw_icon = Image.open(icon_path_right)  # Replace with your image path
        forw_icon = forw_icon.resize((20, 20))  # Resize if needed
        forw_icon = ImageTk.PhotoImage(forw_icon)
        if self.page_manager.can_go_back():
            back_btn = ttk.Button(toolbar, style="NAV.Active.TButton", image=back_icon,
                                  command=lambda *x: self.page_manager.go_back())
        else:
            back_btn = ttk.Button(toolbar, style="NAV.NotActive.TButton", image=back_icon)

        if self.page_manager.can_go_forward():
            forward_btn = ttk.Button(toolbar, style="NAV.Active.TButton", image=forw_icon,
                                     command=lambda *x: self.page_manager.go_forward())
        else:
            forward_btn = ttk.Button(toolbar, style="NAV.NotActive.TButton", image=forw_icon)
        back_btn.image = back_icon
        forward_btn.image = forw_icon
        back_btn.pack(side="left", padx=5)
        forward_btn.pack(side="left", padx=5)



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
