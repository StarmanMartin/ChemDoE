from tkinter import ttk, messagebox
import tkinter as tk
from urllib.parse import urlparse

from chemotion_api import Instance
from requests import RequestException

from ChemDoE.utils.keyboard_shortcuts import add_input_shortcuts
from ChemDoE.utils.page_manager import Page
from ChemDoE.start_view import StartPage

from ChemDoE.config import ConfigManager


class LoginManager(Page):
    def __init__(self):
        super().__init__()
        self.check_var = tk.IntVar(value=int(ConfigManager.get("Last", "remember")))
        self.host_var = tk.StringVar(value=ConfigManager.get("Last", "host"))
        self.host_var.trace_add("write", self._validate_input)
        self.check_label = self.username_entry = self.username_entry = None

    def _check_token(self):
        host = ConfigManager.get("Chemotion", "host")
        token = ConfigManager.get("Chemotion", "token")
        username = ConfigManager.get("Chemotion", "user")
        if host and token:
            try:
                instance = Instance(host).login_token(token).test_connection()
                ConfigManager().chemotion = instance

                ConfigManager().set('Last', 'host', host, commit=False)
                ConfigManager().set('Last', 'user', username)
                self.page_manager.start_page(StartPage())
                return True
            except (RequestException, PermissionError, ConnectionError):
                ConfigManager().chemotion = None
                pass
        return False

    def _login(self, *args):
        host = self.host_var.get()
        instance = Instance(host)
        username = self.username_entry.get()
        password = self.password_entry.get()


        try:
            instance.login(username, password).test_connection()
            ConfigManager().chemotion = instance
            if self.check_var.get():
                ConfigManager().set("Chemotion", "host", host, commit=False)
                ConfigManager().set("Chemotion", "user", username, commit=False)
                ConfigManager().set("Chemotion", "token", instance.token, commit=False)
            else:
                ConfigManager().set("Chemotion", "host", '', commit=False)
                ConfigManager().set("Chemotion", "user", '', commit=False)
                ConfigManager().set("Chemotion", "token", '', commit=False)

            ConfigManager().set('Last', 'remember', str(self.check_var.get()), commit=False)
            ConfigManager().set('Last', 'User', username)
            self.page_manager.start_page(StartPage())
        except RequestException:
            ConfigManager().chemotion = None
            messagebox.showerror("Login Failed", f"Invalid HOST url: {host}")
        except PermissionError:
            ConfigManager().chemotion = None
            messagebox.showerror("Login Failed", "Invalid username or password")

    def _validate_input(self, *args):
        """Check if input is a valid email and update the checkmark label."""
        host = self.host_var.get()
        instance = Instance(host)
        try:
            urlparse(host)
            instance.test_connection()
            self.check_label.config(text="✅", foreground="green")
            ConfigManager().set('Last', 'Host', host)
        except:
            self.check_label.config(text="", foreground="green")

    def leave(self):
        self.page_manager.root.unbind("<Return>")

    def render(self, root: ttk.Frame):
        if self._check_token():
            return
        frame = ttk.Frame(root, padding=20, style="Inner.TFrame")
        frame.pack(expand=True)

        row = 0

        ttk.Label(frame, text="Chemotion host:").grid(row=row, column=0, pady=5, sticky="w")
        url_entry = ttk.Entry(frame, textvariable=self.host_var)
        url_entry.grid(row=row, column=1, pady=5)
        add_input_shortcuts(url_entry)
        self.check_label = ttk.Label(frame, text="", font=("Arial", 14))
        self.check_label.grid(row=row, column=2, pady=5)
        row += 1

        # Username label and entry
        ttk.Label(frame, text="Username:").grid(row=row, column=0, pady=5, sticky="w")
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=row, column=1, pady=5)
        add_input_shortcuts(self.username_entry)
        row += 1

        # Password label and entry
        ttk.Label(frame, text="Password:").grid(row=row, column=0, pady=5, sticky="w")
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=row, column=1, pady=5)
        add_input_shortcuts(self.password_entry)

        row += 1

        # Login button
        login_button = ttk.Button(frame, text="Login", command=self._login)
        self.page_manager.root.bind("<Return>", self._login)
        login_button.grid(row=row, column=0, columnspan=1, pady=20)

        row += 1

        checkbox = ttk.Checkbutton(frame, text="Remember Me", variable=self.check_var)
        checkbox.grid(row=row, column=0, pady=5)

    def set_style(self, style: ttk.Style):
        style.configure("Inner.TFrame", background="#ffffff")
