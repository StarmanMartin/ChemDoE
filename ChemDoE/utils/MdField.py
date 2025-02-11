import re
import tkinter as tk
import webbrowser
from enum import Enum
from tkinter import ttk


class MdField(tk.Text):
    class FS(Enum):
        H1 = 'A'
        H2 = 'B'
        H3 = 'C'
        ITALIC = 'I'
        BOLD = 'D'
        LIST_U = 'U'
        LIST_O = 'O'
        LINK = 'L'
        END = 'X'
        FINALEND = 'E'

        @classmethod
        def all_styles(cls):
            result = []
            for s in cls:
                result.append(s.__str__())
            return result

        def __str__(self):
            return '#' + self.value

    def __init__(self, frame: ttk.Widget, font=("Arial", 12)):
        super().__init__(frame, wrap="word", font=font)
        self._font = font

        self._tags = {
            "A": {'font': (None, self._font[1] + 6, "bold")},
            "B": {'font': (None, self._font[1] + 4, "bold")},
            "C": {'font': (None, self._font[1] + 2, "bold")},
            "D": {'font': (None, None, "bold")},
            "I": {'font': (None, None, "italic")},
            "O": {'font': (None, None, None)},
            "U": {'font': (None, None, None)},
            "L": {'font': (None, None, None),'foreground': 'blue', 'underline': True},
            "E": {'font': (None, None, None)},
        }

    def _prepare_tags(self, tags):
        tags = [t.value for t in tags]
        tag = ''.join(tags)
        if tag == '' or tag in self.tag_names():
            return
        font = [self._font[0], self._font[1], []]
        rest_style_info = {}
        for t in tags:
            for key, val in self._tags[t].items():
                if key != 'font':
                    rest_style_info[key] = val

            for i in range(2):
                if self._tags[t]['font'][i] is not None:
                    font[i] = self._tags[t]['font'][i]
            if self._tags[t]['font'][2] is not None:
                font[2].append(self._tags[t]['font'][2])

        self.tag_config(tag, font=(font[0], font[1], ' '.join(font[2])), **rest_style_info)

        return tag

    def _change_cursor(self, event, cursor_type):
        self.config(cursor=cursor_type)
        self.current_cursor = cursor_type  # Store cursor state

    def set_md_file(self, md_fp):
        with open(md_fp, "r", encoding="utf-8") as f:
            self.set_md_text(f.read())

    def open_link(self, url):
        webbrowser.open(url)

    def set_md_text(self, md_text):

        self.tag_configure("hyperlink", foreground="blue", underline=True)
        self.tag_bind("hyperlink", "<Enter>", lambda e: self._change_cursor(e, "hand2"))
        self.tag_bind("hyperlink", "<Leave>", lambda e: self._change_cursor(e, "xterm"))
        

        # Convert headers
        md_text = re.sub(r"^# (.*)", fr"{self.FS.H1}\1{self.FS.END}", md_text, flags=re.MULTILINE)
        md_text = re.sub(r"^## (.*)", fr"{self.FS.H2}\1{self.FS.END}", md_text, flags=re.MULTILINE)
        md_text = re.sub(r"^### (.*)", fr"{self.FS.H3}\1{self.FS.END}", md_text, flags=re.MULTILINE)

        # Convert bold (**text** or __text__)
        md_text = re.sub(r"\*\*(.*?)\*\*", fr"{self.FS.BOLD}\1{self.FS.END}", md_text)
        md_text = re.sub(r"__(.*?)__", fr"{self.FS.BOLD}\1{self.FS.END}", md_text)

        # Convert italic (*text* or _text_)
        md_text = re.sub(r"\*(.*?)\*", fr"{self.FS.ITALIC}\1{self.FS.END}", md_text)
        md_text = re.sub(r"_(.*?)_", fr"{self.FS.ITALIC}\1{self.FS.END}", md_text)

        # Convert unordered lists (- item)
        md_text = re.sub(r"^- (.*)", fr"   - {self.FS.LIST_U}\1{self.FS.END}", md_text, flags=re.MULTILINE)
        md_text = re.sub(r"^(\d+)\. (.*)", fr"   \1. {self.FS.LIST_O}\2{self.FS.END}", md_text, flags=re.MULTILINE)
        link_re = re.compile(r"\[(.*?)]\((.*?)\)")
        md_text = re.sub(link_re, fr"{self.FS.LINK}[\1](\2){self.FS.END}", md_text)

        md_text += str(self.FS.FINALEND)
        text = ''



        current_style_tags = []
        last = False
        for i in range(len(md_text) - 1):
            if md_text[i:i + 2] in self.FS.all_styles():
                last = True
                fs = self.FS(md_text[i + 1])
                st = self._prepare_tags(current_style_tags)
                if len(current_style_tags) > 0 and current_style_tags[-1] == self.FS.LINK:
                    res = link_re.findall(text)[0]
                    text = res[0]
                    st = (st, 'hyperlink', res[1])
                    self.tag_configure(res[1])
                    self.tag_bind(res[1], "<Button-1>", lambda x: self.open_link(res[1]))  # Click event

                self.insert("end", text, st)

                text = ''
                if fs == self.FS.END:
                    current_style_tags.pop()
                elif fs != self.FS.FINALEND:
                    current_style_tags.append(fs)
            elif not last:
                text += md_text[i]
            else:
                last = False
        return md_text
