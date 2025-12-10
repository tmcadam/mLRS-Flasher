import customtkinter as ctk
from api.espFlash import  find_serial_ports_esp_tx_devices
from api.helpers import find_serial_ports, find_serial_ports_usbttl_devices

ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
#ctk.set_default_color_theme("green")
#ctk.set_default_color_theme("dark-blue")

'''
--------------------------------------------------
CustomTKInter App
--------------------------------------------------
'''

class CTkCompPortOptionMenu(ctk.CTkOptionMenu):
    def __init__(self, master, porttype='default', **kwargs):
        super().__init__(master=master, **kwargs)
        self.porttype = porttype

    def update(self):
        sel = self.get()
        if 'esp' in self.porttype and 'tx' in self.porttype:
            portlist = find_serial_ports_esp_tx_devices()
        elif 'usbttl' in self.porttype:
            portlist = find_serial_ports_usbttl_devices()
        else:
            portlist = find_serial_ports()
        if not portlist:
            portlist = ['COM1']
        #print(portlist)
        self.configure(values=portlist, require_redraw=True)
        if sel in portlist:
            self.set(sel)
        else:
            self.set(portlist[0])

    def _open_dropdown_menu(self):
        self.update()
        super()._open_dropdown_menu()


class CTkFlashButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        super().configure(fg_color="green", hover_color="#006400")


class CTkInfoTextbox(ctk.CTkTextbox):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        super().delete("0.0", "end")
        super().configure(state="disabled")
        super().tag_config('warning', foreground='red')

    def setText(self, txt, tag=None):
        super().configure(state="normal")
        super().delete("0.0", "end")
        super().insert("0.0", txt)
        if tag:
            super().tag_add(tag[0], tag[1], tag[2])
        super().configure(state="disabled")
