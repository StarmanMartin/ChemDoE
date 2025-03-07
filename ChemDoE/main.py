import tkinter as tk
from ChemDoE.icons import IconManager
from ChemDoE.login_manager import LoginManager
from ChemDoE.utils.page_manager import PageManager





def run():
    root = tk.Tk()

    photo = IconManager().CHEMOTION
    root.iconphoto(True, photo)

    root.title("Chemotion DoE")
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("%dx%d+0+0" % (max(w, 700), max(h, 600)))
    pm = PageManager(root)
    pm.start_page(LoginManager())


if __name__ == '__main__':
    run()