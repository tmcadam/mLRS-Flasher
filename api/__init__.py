#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************
app_version = '30.11.2025-001'

import os
import tempfile

from api.espFlash import flashEspToolProgrammer, flashInternalElrsTxModule, flashInternalElrsTxModuleWirelessBridge
from api.stm32Flash import flashSTM32CubeProgrammer

'''
--------------------------------------------------
API Helper
--------------------------------------------------
'''

g_TxModuleExternal_minimal_version = 'v1.3.00'
g_Receiver_minimal_version = 'v1.3.00'
g_TxModuleInternal_minimal_version = 'v1.3.05'
g_LuaScript_minimal_version = 'v1.3.00'

from api.remoteResources import downloadFileAndWriteToDisk

# API for app
def flashDevice(programmer, url, filename, comport=None, baudrate=None):
    #print('flashDevice()',programmer)
    #print(url)
    #print(filename)
    #create_dir('temp')

    temp_dir = tempfile.mkdtemp()
    print("Temporary folder:", temp_dir)
    res = downloadFileAndWriteToDisk(url, os.path.join(temp_dir,filename))
    if not res:
        print('ERROR: flashDevice() [1]')
        return
    #print(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(temp_dir,filename)
    print(filepath)
    if 'wirelessbridge' in programmer:
        # handle WirelessBridge
        if 'internal' in programmer:
            if ('esp8266' in programmer or 'esp8285' in programmer or 'esp32c3' in programmer):
                flashInternalElrsTxModuleWirelessBridge(programmer, filepath)
                return
        else:
            if ('esp8266' in programmer or 'esp8285' in programmer):
                flashEspToolProgrammer(programmer, filepath, comport, baudrate)
                return
            elif ('esp32c3' in programmer):
                flashEspToolProgrammer(programmer, filepath, comport, baudrate)
                return
    elif 'stm32' in programmer:
        # STM32
        flashSTM32CubeProgrammer(programmer, filepath, comport, baudrate)
        return
    elif 'esp' in programmer: # 'esp32'
        # ESP
        if 'internal' in programmer:
            flashInternalElrsTxModule(programmer, filepath)
            return
        else:
            flashEspToolProgrammer(programmer, filepath, comport, baudrate)
            return
    print('ERROR: flashDevice() [2]')




