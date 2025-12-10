#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import os, sys
import subprocess
'''
--------------------------------------------------
Miscellaneous utils
--------------------------------------------------
'''

# helper
def _cvtstr(s):
    if not s: return str(s)
    return '"' + s.replace('\\','\\\\') + '"'

def version_str_to_int(v_str):
    if v_str[0] != 'v':
        return 0
    return int(v_str[1]+'0'+v_str[3]+v_str[5:7])


# def os_system(programmer_path, args):
#     process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True, text=True)
#     res = os.system(args)
#     if res != 0:
#         print("ERROR: os system res =", res)

CREATE_NO_WINDOW = 0x08000000

def os_popen(args):
    print(f"Flashing binary via dfu-util...\n")
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=CREATE_NO_WINDOW,)
    for line in iter(process.stdout.readline, ''):
        print(line, end='')
    process.stdout.close()
    process.wait()
    print("Command complete.\n")


def os_system_run_as_script():
    #return False
    #return True
    if os.name == 'posix': return False
    if getattr(sys, 'frozen', False): return False # don't do as it conflicts with pyinstaller
    return True

def find_serial_ports():
    try:
        from serial.tools.list_ports import comports
        portList = list(comports())
    except:
        print('ERROR: find_serial_ports() (pyserial missing?) [1]')
        return None
    deviceportList = []
    for port in portList:
        #print('*',port.device, port.name, port.description)
        #print(' ',port.hwid, port.vid, port.pid)
        #print(' ',port.manufacturer, port.location, port.product, port.interface)
        deviceportList.append(port.device)
    return deviceportList


def find_serial_ports_usbttl_devices():
    try:
        from serial.tools.list_ports import comports
        portList = list(comports())
    except:
        print('ERROR: find_serial_ports_usbttl_devices() (pyserial missing?) [1]')
        return None
    deviceportList = []
    for port in portList:
        if not 'USB' in port.hwid.upper():
            continue
        if port.vid == 0x0483 and port.pid == 0x374E: # this is STLink
            continue
        if port.vid == 0x0483 and port.pid == 0x5740:  # this is EdgeTx/OpenTx, vid registered via pidcodes, so unique
            continue
        if port.vid == 0x1209 and (port.pid == 0x5740 or port.pid == 0x5741): # this is ArduPilot
            continue
        deviceportList.append(port.device)
    return deviceportList


def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)  # PyInstaller path
    return os.path.join(os.path.abspath("."), relative)

def get_stm32programmer_path():

    if getattr(sys, 'frozen', False):
        # PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # non-bundled/development
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'thirdparty')

    if sys.platform.lower() == 'darwin':
        return os.path.join(base_path, 'stm32cubeprogrammer', 'mac', 'bin', 'STM32_Programmer_CLI')
    elif sys.platform.lower() == 'linux':
        return os.path.join(base_path, 'stm32cubeprogrammer', 'linux', 'bin', 'STM32_Programmer_CLI')
    else:
        return os.path.join(base_path, 'stm32cubeprogrammer', 'win', 'bin', 'STM32_Programmer_CLI.exe')

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
