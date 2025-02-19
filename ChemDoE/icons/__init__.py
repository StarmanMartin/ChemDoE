import itertools
import os
import tkinter as tk
from PIL import Image, ImageTk

__all__ = ['IconManager']

class LoadingGIF:
    def __init__(self, root, gif_path):
        self.root = root
        self.gif_path = gif_path

        # Load the GIF
        self.image = Image.open(self.gif_path)
        self.frames = []
        self._call_id = None

        # Extract all frames
        try:
            while True:
                frame = self.image.copy()  # Copy current frame
                self.frames.append(ImageTk.PhotoImage(frame))
                self.image.seek(len(self.frames))  # Move to next frame
        except EOFError:
            pass  # End of frames

        self.current_frame = itertools.cycle(self.frames)

        # Display first frame
        self.labels = []

    def add_label(self, label: tk.Widget):
        l = tk.Label(label)
        l.pack()
        self.labels.append(l)
        return l

    def _animate(self):
        """Update the GIF frame repeatedly"""
        self.labels = [l for l in self.labels if l.winfo_ismapped()]
        for l in self.labels:
            l.config(image=next(self.current_frame))
        self._call_id =  self.root.after(20, self._animate)  #  Adjust delay based on GIF speed

    def start(self):
        self._animate()

    def stop(self):
        self.root.after_cancel(self._call_id)
        for l in self.labels:
            l.destroy()



class IconManager():
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_icons()
        return cls._instance

    def load_icons(self):
        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/folder.svg.png')
        self.FOLDER_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((16, 16)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/flask.svg.png')
        self.REACTION_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((14, 14)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/plus.svg.png')
        self.PLUS_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((14, 14)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/arrow-left-circle-fill.svg.png')
        self.BACK_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((20,20)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/arrow-right-circle-fill.svg.png')
        self.FORWARD_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((20,20)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/sample.png')
        self.SAMPLE_ICON = ImageTk.PhotoImage(Image.open(_icon_path).resize((20,20)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/trash.png')
        self.TRASH = ImageTk.PhotoImage(Image.open(_icon_path).resize((20,20)))

        _icon_path = os.path.join(os.path.dirname(__file__), 'fixed/chemotion-full.png')
        self.CHEMOTION = ImageTk.PhotoImage(Image.open(_icon_path).resize((104,61)))