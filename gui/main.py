#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import os
import configparser
from appdirs import user_config_dir

from PIL import ImageTk
import customtkinter as ctk

import api.mLRS_metadata as mlrs_md
from api import g_TxModuleExternal_minimal_version, g_Receiver_minimal_version, g_TxModuleInternal_minimal_version, g_LuaScript_minimal_version
from api.remoteResources import downloadVersionsDict, downloadFilesListFromTree
from api.helpers import version_str_to_int

from gui.lua_script import LuaScriptMixin
from gui.tx_module_ext import TxModuleExternalMixin
from gui.receiver import ReceiverMixin
from gui.tx_module_int import TxModuleInternalMixin
from gui.navigation import NavigationMixin
from gui.helpers import resource_path

APP_NAME = "mLRS_Flasher"

class App(ctk.CTk, LuaScriptMixin, TxModuleExternalMixin, ReceiverMixin, TxModuleInternalMixin, NavigationMixin):

    #--------------------------------------------------
    #-- Interface to low level handler
    #--------------------------------------------------

    # needs to be called only once at startup
    # calls getDevicesDict(), and updates the 'Device Type' widgets accordingly
    def updateDeviceTypes(self):
        self.txDeviceTypeDict = mlrs_md.g_txModuleExternalDeviceTypeDict
        keys = list(self.txDeviceTypeDict.keys())
        self.fTxModuleExternal_DeviceType_menu.configure(values=keys)
        self.fTxModuleExternal_DeviceType_menu.set(keys[0]) # this is needed to make the menu update itself

        self.rxDeviceTypeDict = mlrs_md.g_receiverDeviceTypeDict
        keys = list(self.rxDeviceTypeDict.keys())
        self.fReceiver_DeviceType_menu.configure(values=keys)
        self.fReceiver_DeviceType_menu.set(keys[0])

        self.txIntDeviceTypeDict = mlrs_md.g_txModuleInternalDeviceTypeDict
        keys = list(self.txIntDeviceTypeDict.keys())
        self.fTxModuleInternal_DeviceType_menu.configure(values=keys)
        self.fTxModuleInternal_DeviceType_menu.set(keys[0])

    # needs to be called only once at startup
    # calls downloadVersionsDict(), and updates the Firmware Version' widgets accordingly
    def updateFirmwareVersions(self):
        self.firmwareVersionDict = downloadVersionsDict(config_dir=self.config_dir)
        if self.firmwareVersionDict:
            keys = []
            for key in list(self.firmwareVersionDict.keys()): # we assume here it cannot be empty
                keys.append(self.firmwareVersionDict[key]['versionStr'])
        else:
            self.firmwareVersionDict = None
            keys = ['download failed...']
            # TODO: raise window
        txkeys = []; rxkeys = []; txintkeys = []; luakeys = []
        if 'failed' in keys[0]:
            txkeys = keys; rxkeys = keys; txintkeys = keys; luakeys = keys
        else:
            for key in keys:
                v = version_str_to_int(key)
                if v >= version_str_to_int(g_TxModuleExternal_minimal_version): txkeys.append(key)
                if v >= version_str_to_int(g_Receiver_minimal_version): rxkeys.append(key)
                if v >= version_str_to_int(g_TxModuleInternal_minimal_version): txintkeys.append(key)
                if v >= version_str_to_int(g_LuaScript_minimal_version): luakeys.append(key)
        self.fTxModuleExternal_FirmwareVersion_menu.configure(values=txkeys)
        self.fTxModuleExternal_FirmwareVersion_menu.set(txkeys[0]) # this is needed to make the menu update itself
        self.fReceiver_FirmwareVersion_menu.configure(values=rxkeys)
        self.fReceiver_FirmwareVersion_menu.set(rxkeys[0])
        self.fTxModuleInternal_FirmwareVersion_menu.configure(values=txintkeys)
        self.fTxModuleInternal_FirmwareVersion_menu.set(txintkeys[0])
        self.fLuaScript_FirmwareVersion_menu.configure(values=luakeys)
        self.fLuaScript_FirmwareVersion_menu.set(luakeys[0])
        #return self.firmwareVersionDict != None
        return 'failed' not in keys[0]

    # helper
    def _download_firmware_files(self, txrx, device_type, firmware_version):
        if txrx == 'tx':
            if self.txDeviceTypeDict == None or self.firmwareVersionDict == None:
                return ['download failed...']
            device_type_f = self.txDeviceTypeDict[device_type]['fname'] # that's the name of the device in the filename
        elif txrx == 'rx':
            if self.rxDeviceTypeDict == None or self.firmwareVersionDict == None:
                return ['download failed...']
            device_type_f = self.rxDeviceTypeDict[device_type]['fname'] # that's the name of the device in the filename
        elif txrx == 'txint':
            if self.txIntDeviceTypeDict == None or self.firmwareVersionDict == None:
                return ['download failed...']
            device_type_f = self.txIntDeviceTypeDict[device_type]['fname'] # that's the name of the device in the filename
        firmware_version_gitUrl = self.firmwareVersionDict[firmware_version]['gitUrl']
        #print(device_type, device_type_f)
        #print(firmware_version, firmware_version_gitUrl)
        res = downloadFilesListFromTree(txrx, firmware_version_gitUrl, device_type_f, firmware_version, config_dir=self.config_dir)
        if res == None:
            print('ERROR: _download_firmware_files() [1]')
            return ['download failed...']
        if txrx == 'tx':
            self.txFirmwareFilesList = res # must be self as list is needed later also
            firmwareFilesList = self.txFirmwareFilesList
        elif txrx == 'rx':
            self.rxFirmwareFilesList = res # must be self as list is needed later also
            firmwareFilesList = self.rxFirmwareFilesList
        elif txrx == 'txint':
            self.txIntFirmwareFilesList = res # must be self as list is needed later also
            firmwareFilesList = self.txIntFirmwareFilesList
        else:
            print('ERROR: _download_firmware_files() [2]')
            return ['download failed...']
        #print(firmwareFilesList)
        if firmwareFilesList == None:
            return ['download failed...']
        keys = []
        for key in firmwareFilesList:
            fpath, fname = os.path.split(key['path'])
            keys.append(fname)
        if not keys:
            keys.append('not available') # can happen
        #print(keys)
        return keys

    #--------------------------------------------------
    #-- Init and Startup
    #--------------------------------------------------

    def __init__(self, app_version):
        super().__init__()

        self.title('mLRS Flasher Desktop App ' + app_version)
        self.geometry('800x600')
        #self.iconbitmap(resource_path(os.path.join("assets", "mLRS_logo_round.ico"))) # does not work on Mac

        self.wm_iconbitmap()
        self.iconphoto(False, ImageTk.PhotoImage(file = resource_path(os.path.join("assets", "mLRS_logo_round.ico"))))

        #-- set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        #-- create high level frames
        self.initNavgiationPane()
        self.initTxModuleExternalFrame()
        self.initReceiverFrame()
        self.initTxModuleInternalFrame()
        self.initLuaScriptFrame()

        #-- finalize
        # select default frame
        self.fNavigation_select_frame_by_name('tx_module_ext')

        self.config_dir = user_config_dir(APP_NAME)
        os.makedirs(self.config_dir, exist_ok=True)

        self.startup()

        self.ini_open()

    def startup(self):
        # these are 'static' and equal for each section
        self.updateDeviceTypes()

    def after_startup(self):
        print('downloading metadata from github repository...')
        res1 = self.updateFirmwareVersions()
        res2 = self.fTxModuleExternal_Startup()
        res3 = self.fReceiver_Startup()
        res4 = self.fTxModuleInternal_Startup()
        res5 = self.fLuaScript_Startup()
        if (res1 and res2 and res3 and res4 and res5): print('... ok')

    def ini_open(self):
        self.ini_config = configparser.ConfigParser()
        found = self.ini_config.read(os.path.join(self.config_dir, 'mLRS_Flasher.ini'))
        #print(found)
        if not self.ini_config.has_section('app'): # missing so add with default
            self.ini_config.add_section('app')
            self.ini_config.set('app', 'appearance', self.fNavigation_SetAppearanceMode_menu.get())
        res = self.ini_config.get('app', 'appearance')
        #print(res)
        self.fNavigation_SetAppearanceMode_menu.set(res)
        ctk.set_appearance_mode(self.fNavigation_SetAppearanceMode_menu.get()) # it seems the event loop is not yet running

    def closed(self):
        print('Thanks for using mLRS.')
        self.ini_config.set('app', 'appearance', self.fNavigation_SetAppearanceMode_menu.get())
        try:
            F = open(os.path.join(self.config_dir, 'mLRS_Flasher.ini'), 'w')
            self.ini_config.write(F)
            F.close()
        except:
            pass



    #--------------------------------------------------
    #-- Miscellaneous
    #--------------------------------------------------

    def _get_metadata(self, device_type_f, firmware_filename):
        chipset = None
        flashmethod = None
        description = None
        wireless = None
        if device_type_f in mlrs_md.g_targetDict.keys():
            device_type_dict = mlrs_md.g_targetDict[device_type_f]
            if 'chipset' in device_type_dict.keys():
                chipset = device_type_dict['chipset']
            if 'flashmethod' in device_type_dict.keys():
                flashmethod = device_type_dict['flashmethod']
            if 'description' in device_type_dict.keys():
                description = device_type_dict['description']
            if 'wireless' in device_type_dict.keys():
                wireless = device_type_dict['wireless']
            #print("XXXX",device_type_dict)
            #print(firmware_filename)
            if not 'failed' in firmware_filename:
                for key in device_type_dict.keys(): # search for target entry
                    if key in firmware_filename:
                        target_dict = device_type_dict[key]
                        #print("found", target_dict)
                        if 'chipset' in target_dict.keys():
                            chipset = target_dict['chipset']
                        if 'flashmethod' in target_dict.keys():
                            flashmethod = target_dict['flashmethod']
                        if 'description' in target_dict.keys():
                            description = target_dict['description']
                        if 'wireless' in target_dict.keys():
                            wireless = target_dict['wireless']
                        break
        return chipset, flashmethod, description, wireless

    def get_metadata(self, txrx, device_type, firmware_filename):
        if txrx == 'tx':
            device_type_f = self.txDeviceTypeDict[device_type]['fname']
            chipset = self.txDeviceTypeDict[device_type]['chipset']
        elif txrx == 'rx':
            device_type_f = self.rxDeviceTypeDict[device_type]['fname']
            chipset = self.rxDeviceTypeDict[device_type]['chipset']
        elif txrx == 'txint':
            device_type_f = self.txIntDeviceTypeDict[device_type]['fname']
            chipset = self.txIntDeviceTypeDict[device_type]['chipset']
        #print(txrx, device_type_f, chipset)
        chipset2, flashmethod, description, wireless = self._get_metadata(device_type_f, firmware_filename)
        if chipset2:
            chipset = chipset2
        if 'xx' in chipset.lower():
            print("ERROR: Something wrong in get_metadata()")
        return chipset, flashmethod, description, wireless

    def get_flashmethod_list_for_menu(self, flashmethod_str):
        flashmethod_list = flashmethod_str.split(',')
        menu_list = []
        for flashmethod in flashmethod_list:
            if flashmethod == 'dfu': menu_list.append('DFU (USB)')
            if flashmethod == 'stlink': menu_list.append('STLink (SWD)')
            if flashmethod == 'uart': menu_list.append('SystemBoot (UART)')
            if flashmethod == 'esptool': menu_list.append('ESPTool (UART)')
            if flashmethod == 'appassthru': menu_list.append('AP Passthru')
        if len(menu_list) == 0: menu_list.append('failed')
        return menu_list

    def get_flashmethod_from_menu_opt(self, menu_opt):
        if 'DFU' in menu_opt: return 'dfu'
        if 'STLink' in menu_opt: return 'stlink'
        if 'SystemBoot' in menu_opt: return 'uart'
        if 'ESPTool' in menu_opt: return 'esptool'
        if 'AP Passthru' in menu_opt: return 'appassthru'
        return 'default'

