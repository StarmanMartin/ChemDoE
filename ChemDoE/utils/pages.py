import threading
import webbrowser
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import Combobox
from typing import Optional, Callable

from ChemDoE.config import ConfigManager
from ChemDoE.icons import IconManager
from ChemDoE.utils.page_manager import Page


class EasyOptionMenu(tk.OptionMenu):
    def __init__(self, master, *values: str, **kwargs):
        self.var = tk.StringVar()
        self.silent = False
        super().__init__(master, self.var, "", **kwargs)
        self.values = list(values)

        self._on_select = lambda _v, _i: None
        self._current = -1
        self.var.trace_add("write", lambda _a, _b, _c: self.on_select(self.var.get(), self.current_idx))

    @property
    def on_select(self) -> Callable[[str, int], None]:
        if self.silent:
            return lambda _v, _i: None
        return self._on_select

    @on_select.setter
    def on_select(self, value: Callable[[str, int], None]):
        self._on_select = value

    @property
    def values(self) -> list[str]:
        return self._values

    @property
    def current_idx(self):
        return self._current

    @current_idx.setter
    def current_idx(self, i):
        self._set_var_on_select(self.values[i], i)

    @values.setter
    def values(self, new_options: list[str]):
        menu = self["menu"]
        menu.delete(0, "end")  # Clear existing options
        for idx, option in enumerate(new_options):
            menu.add_command(label=option,
                             command=lambda v=option, i=idx: self._set_var_on_select(v, i))  # Update options
        self.var.set('')
        self._current = -1
        self._values = new_options  # Set a default value

    def insert_separator(self, idx: int):
        self["menu"].insert_separator(idx)

    def _set_var_on_select(self, val, i):
        self._current = i
        self.var.set(val)

    def get(self):
        return self.var.get()

    def current(self, i: int = None):
        if i is not None:
            self.current_idx = i
        return self.current_idx

    def set(self, val: str):
        idx = self.values.index(val)
        self._set_var_on_select(val, idx)


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame that can be embedded in other widgets.
    It creates a canvas with a vertical scrollbar and places a frame inside the canvas.
    """

    def __init__(self, container, horizontal=False, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # Create a canvas widget inside the frame
        self._yscroll_disabled = True
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        if horizontal:
            self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
            # Configure the canvas to use the scrollbar
            self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
            self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        else:
            self.scrollbar_x = None

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create a frame inside the canvas which will hold the content
        self.scrollable_frame = ttk.Frame(self.canvas, style='Background.TFrame')

        # Create a window inside the canvas to hold the inner frame
        self.window_item = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")

        # Update the scrollregion of the canvas whenever the size of the inner frame changes
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

    def update_sc_view(self):
        self._on_canvas_configure(None)

    def _on_canvas_configure(self, event):
        # Set the inner frame's width to match the canvas's width.
        bbox = self.canvas.bbox("all")
        self.canvas.configure(scrollregion=bbox)
        self.update_scroll_visibility(bbox)
        self.update_frame_width()

    def update_frame_width(self):
        """Adjust frame width if canvas is wider than the content"""
        canvas_width = self.canvas.winfo_width()
        frame_width = self.scrollable_frame.winfo_reqwidth()

        if canvas_width > frame_width:
            self.canvas.itemconfig(self.window_item, width=canvas_width)
        else:
            self.canvas.itemconfig(self.window_item, width=frame_width)

    def update_scroll_visibility(self, bbox):
        """Show scrollbars only if needed"""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if bbox:
            frame_width = bbox[2] - bbox[0]
            frame_height = bbox[3] - bbox[1]

            # Show/hide vertical scrollbar
            if frame_height > canvas_height:
                self._yscroll_disabled = False
                self.scrollbar.grid(row=0, column=1, sticky="ns")
                self.canvas.configure(yscrollcommand=self.scrollbar.set)
            else:
                self._yscroll_disabled = True
                self.scrollbar.grid_remove()
                self.canvas.configure(yscrollcommand="")

            # Show/hide horizontal scrollbar
            if self.scrollbar_x and frame_width > canvas_width:
                self.scrollbar_x.grid(row=1, column=0, sticky="ew")
                self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
            elif self.scrollbar_x:
                self.scrollbar_x.grid_remove()
                self.canvas.configure(xscrollcommand="")

    def _on_mouse_scroll(self, event):
        if self._yscroll_disabled:
            return
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
        ConfigManager().logout()
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
        self.fav_dropdown = ttk.Combobox(toolbar, values=[], state="readonly")
        self.fav_dropdown.pack(side="left", padx=5, pady=0)
        self.fav_dropdown.bind("<<ComboboxSelected>>", self._on_fav_select)
        url = f'{self.instance.host_url}/mydb'
        if hasattr(self, 'reaction') and self.reaction.id:
            url += f'/collection/{self.instance.get_root_collection().id}/reaction/{self.reaction.id}'

        ttk.Button(toolbar, image=IconManager().CHEMOTION, command=lambda: webbrowser.open(url), style="Info.TButton").pack(side="left", padx=5)
        ttk.Button(toolbar, image=IconManager().INFO, command=lambda: webbrowser.open('https://chemdoe.readthedocs.io/en/latest'), style="Info.TButton").pack(side="left", padx=5)

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

        style.configure("Outer.TFrame", background="white")
        style.configure("Info.TButton", background="#c2e7ff")
        style.map("Info.TButton", background=[("active", "#d2f7ff")], foreground=[("active", "white")])
