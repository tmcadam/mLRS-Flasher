import sys, os

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # PyInstaller path
    return os.path.join(os.path.abspath("."), relative)

def get_dfu_util_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'thirdparty')
    return os.path.join(base_path, "dfu-util-static.exe")  # or "dfu-util" on Linux/macOS

def get_st_flash_path():
    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'thirdparty')
    return os.path.join(base_path, "st-flash.exe")  # or "st-flash" on Linux/macOS
