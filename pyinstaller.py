import PyInstaller.__main__


def install():
    PyInstaller.__main__.run(['ChemDoE.spec'])

if __name__ == '__main__':
    install()