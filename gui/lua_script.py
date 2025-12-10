#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import customtkinter as ctk
from customtkinter import filedialog
from gui.ctkinter_components import CTkFlashButton

from api.remoteResources import downloadFilesListFromTree, downloadFileAndWriteToDisk

class LuaScriptMixin:


    # helper
    def _download_luascript_files(self, firmware_version):
        if self.firmwareVersionDict == None:
            return ['download failed...']
        firmware_version_gitUrl = self.firmwareVersionDict[firmware_version]['gitUrl']
        #print(firmware_version, firmware_version_gitUrl)
        self.luaScriptFilesList = downloadFilesListFromTree('lua', firmware_version_gitUrl) # must be self as list is needed later also
        #print(self.luaScriptFilesList)
        if self.luaScriptFilesList == None:
            return ['download failed...']
        keys = []
        for key in self.luaScriptFilesList:
            if 'mLRS.lua' in key['path']: keys.append('color screen (mLRS.lua)')
        for key in self.luaScriptFilesList:
            if 'mLRS-bw.lua' in key['path']: keys.append('bw screen (mLRS-bw.lua)')
        for key in self.luaScriptFilesList:
            if 'mLRS-bw-luac.lua' in key['path']: keys.append('bw screen compiled (mLRS-bw-luac.lua)')
        if not keys:
            keys.append('not available') # can happen
        #print(keys)
        return keys

    # needs to be called whenever device type or firmware version changes
    # calls _download_luascript_files() to get the '.lua' file names in the tree, and updates LuaScript 'Radio Screen Type' widget
    def updateLuaScriptFiles(self):
        firmware_version = self.fLuaScript_FirmwareVersion_menu.get().split()[0] # remove the added ' (...)' from the version
        keys = self._download_luascript_files(firmware_version)
        self.fLuaScript_RadioScreen_menu.configure(values=keys)
        self.fLuaScript_RadioScreen_menu.set(keys[0])
        return 'failed' not in keys



    # calls downloadFileAndWriteToDisk() for the selected filename, and saves it
    def saveLuaScript(self, filename):
        #print(filename)
        # hä, what was this good for ??
        #if self.firmwareVersionDict == None:
        #    return
        #firmware_version = self.fLuaScript_FirmwareVersion_menu.get().split()[0] # remove the added ' (...)' from the version
        #firmware_version_gitUrl = self.firmwareVersionDict[firmware_version]['gitUrl']
        #print(firmware_version, firmware_version_gitUrl)
        if self.luaScriptFilesList == None:
            print('ERROR: saveLuaScript() [1]')
            return
        #print(self.luaScriptFilesList)
        for key in self.luaScriptFilesList        :
            fpath, fname = os.path.split(key['path'])
            if fname.lower() in filename.lower():
                downloadFileAndWriteToDisk(key['url'], filename)
                return
        print('ERROR: saveLuaScript() [2]')



    #--------------------------------------------------
    #-- Lua Script frame
    #--------------------------------------------------

    def initLuaScriptFrame(self):
        self.fLuaScript = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fLuaScript.grid_columnconfigure(1, weight=1)

        wrow = 0

        # Firmware Version
        self.fLuaScript_FirmwareVersion_label = ctk.CTkLabel(self.fLuaScript,
            text="Firmware Version",
            )
        self.fLuaScript_FirmwareVersion_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fLuaScript_FirmwareVersion_menu = ctk.CTkOptionMenu(self.fLuaScript,
            values=["downloading..."],
            width=440,
            command=self.fLuaScript_FirmwareVersion_menu_event)
        self.fLuaScript_FirmwareVersion_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Radio Screen
        self.fLuaScript_RadioScreen_label = ctk.CTkLabel(self.fLuaScript,
            text="Radio Screen Type",
            )
        self.fLuaScript_RadioScreen_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fLuaScript_RadioScreen_menu = ctk.CTkOptionMenu(self.fLuaScript,
            values=["downloading..."],
            width=440,
            )#command=self.fLuaScript_RadioScreen_menu_event)
        self.fLuaScript_RadioScreen_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Download Lua Script Button
        self.fLuaScript_Download_button = CTkFlashButton(self.fLuaScript,
            text = "Download Lua Script",
            command = self.fLuaScript_Download_button_event)
        self.fLuaScript_Download_button.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20)
        wrow += 1

    def fLuaScript_Startup(self):
        return self.updateLuaScriptFiles()

    def fLuaScript_FirmwareVersion_menu_event(self, opt):
        self.updateLuaScriptFiles()

    def fLuaScript_Download_button_event(self):
        initialfile = self.fLuaScript_RadioScreen_menu.get()
        if 'bw' in initialfile and 'compiled' in initialfile:
            initialfile = 'mLRS-bw-luac.lua'
        elif 'bw' in initialfile:
            initialfile = 'mLRS-bw.lua'
        else:
            initialfile = 'mLRS.lua'
        filename = filedialog.asksaveasfilename(
            initialfile = initialfile,
            filetypes = (('Lua files', '*.lua'),('All files', '*.*')),
            #defaultextension = '.lua',
            confirmoverwrite = True,
            )
        if not filename:
            return
        self.saveLuaScript(filename)
