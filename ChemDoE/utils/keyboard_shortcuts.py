import tkinter as tk


def add_input_shortcuts(entry):
    def select_all(event):
        event.widget.select_range(0, tk.END)  # Select all text
        event.widget.icursor(tk.END)  # Move cursor to the end
        return "break"

    entry.bind("<Control-a>", select_all)


def add_placeholder(entry, placeholder):
    entry.bind("<FocusIn>", lambda x: _remove_placeholder(entry, placeholder))
    entry.bind("<FocusOut>", lambda x: _add_placeholder(entry, placeholder))
    _add_placeholder(entry, placeholder)


def _add_placeholder(entry, placeholder):
    """Show placeholder text when Entry is empty and loses focus."""
    if not entry.get():
        entry.insert(0, placeholder)
        entry.config(foreground="gray")  # Placeholder color


def _remove_placeholder(entry, placeholder):
    """Remove placeholder text when user starts typing."""
    if entry.get() == placeholder:
        entry.delete(0, tk.END)
        entry.config(foreground="black")  # Normal text color
