import customtkinter as ctk
from gui.ctkinter_components import CTkFlashButton, CTkInfoTextbox
from gui.messages import warning_dev_version, warning_dev_version_tag
from gui.ctkinter_components import CTkCompPortOptionMenu

from api import flashDevice
from api.remoteResources import g_wirelessbridge_path_url
from gui.run_tool import cmd_in_output_window

class TxModuleExternalMixin:


    # needs to be called whenever device type or firmware version changes
    # calls _download_firmware_files() to get the 'tx' file names in the tree, and updates TxModuleExternal 'Firmware Files' widget
    def updateTxModuleExternalFirmwareFiles(self):
        device_type = self.fTxModuleExternal_DeviceType_menu.get()
        firmware_version = self.fTxModuleExternal_FirmwareVersion_menu.get().split()[0] # remove the added ' (...)' from the version
        keys = self._download_firmware_files('tx', device_type, firmware_version)
        self.fTxModuleExternal_FirmwareFile_menu.configure(values=keys)
        self.fTxModuleExternal_FirmwareFile_menu.set(keys[0])
        return 'failed' not in keys[0]


    # calls flashDevice() for the selected device, firmware url, and filename, to initiate flashing
    def flashTxModuleExternalFirmware(self):
        #print('flashTxModuleExternalFirmware()')
        device_type = self.fTxModuleExternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleExternal_FirmwareFile_menu.get()
        if 'failed' in firmware_filename:
            print('ERROR: flashTxModuleExternalFirmware() [1]')
            return
        #print(device_type, self.txDeviceTypeDict[device_type])
        #print(firmware_filename)
        chipset, flashmethod, description, wireless = self.get_metadata('tx', device_type, firmware_filename)
        if not flashmethod: flashmethod = 'default' # can be None
        #print(self.txFirmwareFilesList)
        #print(chipset)
        for key in self.txFirmwareFilesList:
            if firmware_filename in key['path']: # that's our firmware entry
                if 'stm32' in chipset:
                    if 'dfu' in flashmethod:
                        cmd_in_output_window(flashDevice, chipset + ' dfu', key['url'], firmware_filename)
                    else:
                        cmd_in_output_window(flashDevice, chipset + ' stlink', key['url'], firmware_filename)
                    return
                elif 'esp32' in chipset:
                    comport = self.fTxModuleExternal_ComPort_menu.get()
                    print('--->',comport)
                    cmd_in_output_window(flashDevice, chipset, key['url'], firmware_filename, comport=comport, baudrate=921600)
                    return
        print('ERROR: flashTxModuleExternalFirmware() [2]')


    def flashTxModuleExternalWirelessBridgeFirmware(self):
        #print('flashTxModuleExternalWirelessBridgeFirmware()')
        comport = self.fTxModuleExternal_ComPort_menu.get()
        #print('--->',comport)
        device_type = self.fTxModuleExternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleExternal_FirmwareFile_menu.get()
        if 'failed' in firmware_filename:
            print('ERROR: flashTxModuleExternalWirelessBridgeFirmware() [1]')
            return
        chipset, flashmethod, description, wireless = self.get_metadata('tx', device_type, firmware_filename)
        #print('--->',wireless)
        programmer = 'wirelessbridge'
        if 'chipset' in wireless:
            programmer = programmer + ' ' + wireless['chipset']
        else:
            programmer = programmer + ' esp8266'
        if 'reset' in wireless:
            programmer = programmer + ' ' + wireless['reset']
        else:
            programmer = programmer + ' dtr'
        if 'erase' in wireless:
            programmer = programmer + ' ' + wireless['erase']
        if 'baud' in wireless:
            baudrate = wireless['baud']
        else:
            baudrate = 921600
        #url = 'https://raw.githubusercontent.com/olliw42/mLRS/refs/heads/main/firmware/wirelessbridge-esp8266/mlrs-wireless-bridge-esp8266.ino.bin'
        if 'esp32c3' in programmer: # the wireless chipset is in wireless['chipset'], not chipset, so we test programmer to catch the fallback
            firmware_filename = 'mlrs-wireless-bridge-esp32c3.ino.bin'
        else:
            firmware_filename = 'mlrs-wireless-bridge-esp8266.ino.bin'
        url = g_wirelessbridge_path_url + firmware_filename
        cmd_in_output_window(flashDevice, programmer, url, firmware_filename, comport, baudrate)


    #--------------------------------------------------
    #-- Tx Module (external) frame
    #--------------------------------------------------

    def initTxModuleExternalFrame(self):
        self.fTxModuleExternal = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fTxModuleExternal.grid_columnconfigure(0, weight=0)
        self.fTxModuleExternal.grid_columnconfigure(1, weight=1)
        self.fTxModuleExternal.grid_rowconfigure(5, weight=1)

        wrow = 0

        # Device Type
        self.fTxModuleExternal_DeviceType_label = ctk.CTkLabel(self.fTxModuleExternal,
            text="Device Type",
            )
        self.fTxModuleExternal_DeviceType_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleExternal_DeviceType_menu = ctk.CTkOptionMenu(self.fTxModuleExternal,
            values=["downloading..."],
            width=440, # this sets a min width, can grow larger
            #dynamic_resizing = False, # when false it prevents the box to grow with the entry
            command=self.fTxModuleExternal_DeviceType_menu_event)
        self.fTxModuleExternal_DeviceType_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware Version
        self.fTxModuleExternal_FirmwareVersion_label = ctk.CTkLabel(self.fTxModuleExternal,
            text="Firmware Version",
            )
        self.fTxModuleExternal_FirmwareVersion_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleExternal_FirmwareVersion_menu = ctk.CTkOptionMenu(self.fTxModuleExternal,
            values=["downloading..."],
            width=440,
            command=self.fTxModuleExternal_FirmwareVersion_menu_event)
        self.fTxModuleExternal_FirmwareVersion_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware File
        self.fTxModuleExternal_FirmwareFile_label = ctk.CTkLabel(self.fTxModuleExternal,
            text="Firmware File",
            )
        self.fTxModuleExternal_FirmwareFile_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleExternal_FirmwareFile_menu = ctk.CTkOptionMenu(self.fTxModuleExternal,
            values=["downloading..."],
            width=440,
            command=self.fTxModuleExternal_FirmwareFile_menu_event)
        self.fTxModuleExternal_FirmwareFile_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Flash Button
        self.fTxModuleExternal_fFlash = ctk.CTkFrame(self.fTxModuleExternal, corner_radius=0, fg_color="transparent")
        self.fTxModuleExternal_fFlash.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20)
        wrow += 1

        self.fTxModuleExternal_Flash_button = CTkFlashButton(self.fTxModuleExternal_fFlash,
            text = "Flash Tx Module",
            #fg_color="green", hover_color="#006400",
            command = self.fTxModuleExternal_Flash_button_event)
        self.fTxModuleExternal_Flash_button.grid(row=0, column=0)

        self.fTxModuleExternal_ComPort_menu = CTkCompPortOptionMenu(self.fTxModuleExternal_fFlash,
            porttype = 'esp,tx',
            values=['COM1'],
            width=10,
            )#command=self.fTxModuleExternal_ComPort_menu_event)
        self.fTxModuleExternal_ComPort_menu.grid(row=0, column=1, padx=20)
        self.fTxModuleExternal_ComPort_menu.grid_remove() # grid_remove() memorizes settings, grid_forget() looses them

        #-- Wireless Bridge --
        self.fTxModuleExternal_fWirelessBridge = ctk.CTkFrame(self.fTxModuleExternal, corner_radius=0, fg_color="transparent")
        self.fTxModuleExternal_fWirelessBridge.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20, sticky="we")
        self.fTxModuleExternal_fWirelessBridge.grid_columnconfigure(0, weight=1)
        wrow += 1

        self.fTxModuleExternal_WirelessBridge_label = ctk.CTkLabel(self.fTxModuleExternal_fWirelessBridge,
            text="Wireless Bridge",
            font=ctk.CTkFont(weight="bold")
            )
        self.fTxModuleExternal_WirelessBridge_label.grid(row=0, column=0, sticky="w")

        self.fTxModuleExternal_WirelessBridgeFlash_button = CTkFlashButton(self.fTxModuleExternal_fWirelessBridge,
            text = "Flash Wireless Bridge",
            command = self.fTxModuleExternal_WirelessBridgeFlash_button_event)
        self.fTxModuleExternal_WirelessBridgeFlash_button.grid(row=1, column=0, pady=(20,0))

        #-- Description text box --
        self.fTxModuleExternal_Description_textbox = CTkInfoTextbox(self.fTxModuleExternal,
            #height=100,
            font=("Courier New",12),
            #activate_scrollbars=False,
            )
        self.fTxModuleExternal_Description_textbox.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        wrow += 1

        self.fTxModuleExternal_fWirelessBridge.grid_remove() # pack_forget() did not work!
        self.fTxModuleExternal_Description_textbox.setText("downloading metadata...\n")
        #self.fTxModuleExternal_Description_textbox.grid_remove()

    def fTxModuleExternal_UpdateWidgets(self):
        device_type = self.fTxModuleExternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleExternal_FirmwareFile_menu.get()
        _, _, description, wireless = self.get_metadata('tx', device_type, firmware_filename)
        if wireless != None:
            self.fTxModuleExternal_fWirelessBridge.grid()
        else:
            self.fTxModuleExternal_fWirelessBridge.grid_remove()
        text, tag = '', None
        if 'dev' in self.fTxModuleExternal_FirmwareVersion_menu.get():
            text, tag = warning_dev_version, warning_dev_version_tag
        if description != None:
            text += description
        if text != '':
            self.fTxModuleExternal_Description_textbox.grid()
            self.fTxModuleExternal_Description_textbox.setText(text, tag)
        else:
            self.fTxModuleExternal_Description_textbox.grid_remove()

    def fTxModuleExternal_ComPort_HandleIt(self):
        device_type = self.fTxModuleExternal_DeviceType_menu.get()
        chipset = self.txDeviceTypeDict[device_type]['chipset']
        if 'stm32' in chipset:
            self.fTxModuleExternal_ComPort_menu.grid_remove()
        elif 'esp32' in chipset:
            self.fTxModuleExternal_ComPort_menu.update()
            self.fTxModuleExternal_ComPort_menu.grid()

    def fTxModuleExternal_Startup(self):
        res = self.updateTxModuleExternalFirmwareFiles()
        self.fTxModuleExternal_ComPort_HandleIt()
        self.fTxModuleExternal_UpdateWidgets()
        return res

    def fTxModuleExternal_DeviceType_menu_event(self, opt):
        self.updateTxModuleExternalFirmwareFiles()
        self.fTxModuleExternal_ComPort_HandleIt()
        self.fTxModuleExternal_UpdateWidgets()

    def fTxModuleExternal_FirmwareVersion_menu_event(self, opt):
        self.updateTxModuleExternalFirmwareFiles()
        self.fTxModuleExternal_UpdateWidgets()

    def fTxModuleExternal_FirmwareFile_menu_event(self, opt):
        self.fTxModuleExternal_UpdateWidgets()

    def fTxModuleExternal_Flash_button_event(self):
        self.flashTxModuleExternalFirmware()

    def fTxModuleExternal_WirelessBridgeFlash_button_event(self):
        self.flashTxModuleExternalWirelessBridgeFirmware()
