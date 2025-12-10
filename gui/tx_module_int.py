#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import sys
import customtkinter as ctk
from gui.ctkinter_components import CTkFlashButton, CTkInfoTextbox
from gui.messages import warning_dev_version, warning_dev_version_tag

from api import flashDevice
from api.remoteResources import g_wirelessbridge_path_url
from gui.run_tool import cmd_in_output_window

class TxModuleInternalMixin:

    # needs to be called whenever device type or firmware version changes
    # calls _download_firmware_files() to get the 'txint' file names in the tree, and updates TxModuleInternal 'Firmware Files' widget
    def updateTxModuleInternalFirmwareFiles(self):
        device_type = self.fTxModuleInternal_DeviceType_menu.get()
        firmware_version = self.fTxModuleInternal_FirmwareVersion_menu.get().split()[0] # remove the added ' (...)' from the version
        keys = self._download_firmware_files('txint', device_type, firmware_version)
        self.fTxModuleInternal_FirmwareFile_menu.configure(values=keys)
        self.fTxModuleInternal_FirmwareFile_menu.set(keys[0])
        return 'failed' not in keys[0]


    def flashTxModuleInternalFirmware(self):
        device_type = self.fTxModuleInternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleInternal_FirmwareFile_menu.get()
        if 'failed' in firmware_filename:
            print('ERROR: flashTxModuleInternalFirmware() [1]')
            return
        chipset, flashmethod, description, wireless = self.get_metadata('txint', device_type, firmware_filename)
        if chipset != 'esp32': # currently must be esp32
            print('ERROR: flashTxModuleInternalFirmware() [3]')
            sys.exit(1)
        for key in self.txIntFirmwareFilesList:
            if firmware_filename in key['path']: # that's our firmware entry
                cmd_in_output_window(flashDevice, 'esp32 internal', key['url'], firmware_filename)
                return
        print('ERROR: flashTxModuleInternalFirmware() [2]')

    def flashTxModuleInternalWirelessBridgeFirmware(self):
        device_type = self.fTxModuleInternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleInternal_FirmwareFile_menu.get()
        if 'failed' in firmware_filename:
            print('ERROR: flashTxModuleInternalWirelessBridgeFirmware() [1]')
            return
        chipset, flashmethod, description, wireless = self.get_metadata('txint', device_type, firmware_filename)
        programmer = 'wirelessbridge internal'
        if 'chipset' in wireless:
            programmer = programmer + ' ' + wireless['chipset']
        else:
            programmer = programmer + ' esp8266'
        if 'erase' in wireless:
            programmer = programmer + ' ' + wireless['erase']
        #print(programmer)
        #url = 'https://raw.githubusercontent.com/olliw42/mLRS/refs/heads/main/firmware/wirelessbridge-esp8266/mlrs-wireless-bridge-esp8266.ino.bin'
        if 'esp32c3' in programmer: # the wireless chipset is in wireless['chipset'], not chipset, so we test programmer to catch the fallback
            firmware_filename = 'mlrs-wireless-bridge-esp32c3.ino.bin'
        else:
            firmware_filename = 'mlrs-wireless-bridge-esp8266.ino.bin'
        url = g_wirelessbridge_path_url + firmware_filename
        flashDevice(programmer, url, firmware_filename)


    #--------------------------------------------------
    #-- Tx Module (internal) frame
    #--------------------------------------------------

    def initTxModuleInternalFrame(self):
        self.fTxModuleInternal = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fTxModuleInternal.grid_columnconfigure(1, weight=1)
        self.fTxModuleInternal.grid_rowconfigure(5, weight=1)

        wrow = 0

        # Device Type
        self.fTxModuleInternal_DeviceType_label = ctk.CTkLabel(self.fTxModuleInternal,
            text="Device Type",
            )
        self.fTxModuleInternal_DeviceType_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleInternal_DeviceType_menu = ctk.CTkOptionMenu(self.fTxModuleInternal,
            values=["downloading..."],
            width=440,
            command=self.fTxModuleInternal_DeviceType_menu_event)
        self.fTxModuleInternal_DeviceType_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware Version
        self.fTxModuleInternal_FirmwareVersion_label = ctk.CTkLabel(self.fTxModuleInternal,
            text="Firmware Version",
            )
        self.fTxModuleInternal_FirmwareVersion_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleInternal_FirmwareVersion_menu = ctk.CTkOptionMenu(self.fTxModuleInternal,
            values=["downloading..."],
            width=440,
            command=self.fTxModuleInternal_FirmwareVersion_menu_event)
        self.fTxModuleInternal_FirmwareVersion_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware File
        self.fTxModuleInternal_FirmwareFile_label = ctk.CTkLabel(self.fTxModuleInternal,
            text="Firmware File",
            )
        self.fTxModuleInternal_FirmwareFile_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fTxModuleInternal_FirmwareFile_menu = ctk.CTkOptionMenu(self.fTxModuleInternal,
            values=["downloading..."],
            width=440,
            command=self.fTxModuleInternal_FirmwareFile_menu_event)
        self.fTxModuleInternal_FirmwareFile_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Flash Button
        self.fTxModuleInternal_Flash_button = CTkFlashButton(self.fTxModuleInternal,
            text = "Flash Tx Module",
            command = self.fTxModuleInternal_Flash_button_event)
        self.fTxModuleInternal_Flash_button.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20)
        wrow += 1

        #-- Wireless Bridge --
        self.fTxModuleInternal_fWirelessBridge = ctk.CTkFrame(self.fTxModuleInternal, corner_radius=0, fg_color="transparent")
        self.fTxModuleInternal_fWirelessBridge.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20, sticky="we")
        self.fTxModuleInternal_fWirelessBridge.grid_columnconfigure(0, weight=1)
        wrow += 1

        self.fTxModuleInternal_WirelessBridge_label = ctk.CTkLabel(self.fTxModuleInternal_fWirelessBridge,
            text="Wireless Bridge",
            font=ctk.CTkFont(weight="bold")
            )
        self.fTxModuleInternal_WirelessBridge_label.grid(row=0, column=0, sticky="w")

        self.fTxModuleInternal_WirelessBridgeFlash_button = CTkFlashButton(self.fTxModuleInternal_fWirelessBridge,
            text = "Flash Wireless Bridge",
            command = self.fTxModuleInternal_WirelessBridgeFlash_button_event)
        self.fTxModuleInternal_WirelessBridgeFlash_button.grid(row=1, column=0, pady=(20,0))

        #-- Description text box --
        self.fTxModuleInternal_Description_textbox = CTkInfoTextbox(self.fTxModuleInternal,
            font=("Courier New",12),
            )
        self.fTxModuleInternal_Description_textbox.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        wrow += 1

        self.fTxModuleInternal_fWirelessBridge.grid_remove() # pack_forget() did not work!
        self.fReceiver_Description_textbox.setText("downloading metadata...\n")
        #self.fTxModuleInternal_Description_textbox.grid_remove()

    def fTxModuleInternal_UpdateWidgets(self):
        device_type = self.fTxModuleInternal_DeviceType_menu.get()
        firmware_filename = self.fTxModuleInternal_FirmwareFile_menu.get()
        _, _, description, wireless = self.get_metadata('txint', device_type, firmware_filename)
        if wireless != None:
            self.fTxModuleInternal_fWirelessBridge.grid()
        else:
            self.fTxModuleInternal_fWirelessBridge.grid_remove()
        text, tag = '', None
        if 'dev' in self.fTxModuleInternal_FirmwareVersion_menu.get():
            text, tag = warning_dev_version, warning_dev_version_tag
        if description != None:
            text += description
        if text != '':
            self.fTxModuleInternal_Description_textbox.grid()
            self.fTxModuleInternal_Description_textbox.setText(text, tag)
        else:
            self.fTxModuleInternal_Description_textbox.grid_remove()

    def fTxModuleInternal_Startup(self):
        res = self.updateTxModuleInternalFirmwareFiles()
        self.fTxModuleInternal_UpdateWidgets()
        return res

    def fTxModuleInternal_DeviceType_menu_event(self, opt):
        self.updateTxModuleInternalFirmwareFiles()
        self.fTxModuleInternal_UpdateWidgets()

    def fTxModuleInternal_FirmwareVersion_menu_event(self, opt):
        self.updateTxModuleInternalFirmwareFiles()
        self.fTxModuleInternal_UpdateWidgets()

    def fTxModuleInternal_FirmwareFile_menu_event(self, opt):
        self.fTxModuleInternal_UpdateWidgets()

    def fTxModuleInternal_Flash_button_event(self):
        self.flashTxModuleInternalFirmware()

    def fTxModuleInternal_WirelessBridgeFlash_button_event(self):
        self.flashTxModuleInternalWirelessBridgeFirmware()
