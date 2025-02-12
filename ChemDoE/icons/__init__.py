import os

from PIL import Image, ImageTk

__all__ = ['IconManager']


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