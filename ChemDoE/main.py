import tkinter as tk
from tkinter import ttk
from chemotion_api import Instance
from ChemDoE.login_manager import LoginManager
from ChemDoE.utils.page_manager import PageManager

instance : Instance | None = None

def open_list_view():
    """Opens the list view window and hides the login window."""
    root.withdraw()  # Hide the login window

    list_window = tk.Toplevel(root)
    list_window.title("List View")
    list_window.geometry("300x300")

    ttk.Label(list_window, text="Welcome to the List View!", font=("Arial", 14)).pack(pady=10)

    # Sample list
    items = ["Item 1", "Item 2", "Item 3", "Item 4"]
    listbox = tk.Listbox(list_window)
    for item in items:
        listbox.insert(tk.END, item)
    listbox.pack(pady=10)

    ttk.Button(list_window, text="Logout", command=lambda: logout(list_window)).pack(pady=10)


def logout(window):
    """Closes the list view window and shows the login window again."""
    window.destroy()
    root.deiconify()  # Show the login window again





if __name__ == '__main__':
    root = tk.Tk()
    root.title("Login Form")
    root.geometry("500x500")
    pm = PageManager(root)
    pm.start_page(LoginManager())