
#************************************************************
# Copyright (c) MLRS project
# GPL3
# https://www.gnu.org/licenses/gpl-3.0.de.html
# OlliW @ www.olliw.eu
#************************************************************
# mLRS Flasher Desktop App
# 30. Nov. 2025 001
#************************************************************

import os, sys, time
import re

import esptool

import api.apInitPassthru as appassthru
import api.edgetxInitPassthru as radio
from api.helpers import os_system_run_as_script, os_popen

'''
--------------------------------------------------
ESP32/ESP82XX Flashing Tools
--------------------------------------------------
'''

# RadioMaster Bandit, BetaFPV1WMicro seem to use a CP210x usb-ttl adapter
def find_serial_ports_esp_tx_devices():
    try:
        from serial.tools.list_ports import comports
        portList = list(comports())
    except:
        print('ERROR: find_serial_ports_esp_tx_devices() (pyserial missing?) [1]')
        return None
    deviceportList = []
    for port in portList:
        if not 'USB' in port.hwid.upper():
            continue
        if port.vid == 0x0483 and port.pid == 0x374E: # this is STLink
            continue
        if port.vid == 0x0483 and port.pid == 0x5740: # this is EdgeTx/OpenTx, vid registered via pidcodes, so unique
            continue
        if port.vid == 0x1209 and (port.pid == 0x5740 or port.pid == 0x5741): # this is ArduPilot
            continue
# we support the RP4TD, which requires using a USB-TTL adapter
# but the user may not use a CP21x device
#        if 'CP210' not in port.description: # was 'Silicon Labs CP210x', gave issues on nix
#            continue
        deviceportList.append(port.device)
    return deviceportList

def flatten_list(raw_args):
    args = []

    for item in raw_args:
        if item is None:
            continue
        if isinstance(item, list):
            args.extend(item)
        else:
            args.append(item)
    return args

def _flash_esptool_argstr(programmer, firmware, comport, baudrate):

    assets_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'assets')

    if 'no dtr' in programmer:
        before_arg = ['--before', 'no-reset']
    else:
        before_arg = ['--before', 'default-reset']
    if 'full_erase' in programmer:
        erase_arg = ['-e']
    else:
        erase_arg = None
    if 'esp32c3' in programmer: # must come before we test for 'esp32'!
        args = (
            '--chip esp32c3 ' +
            '--port "' + comport + '" ' +
            '--baud ' + str(baudrate) + ' ' +
            before_arg + ' --after hard_reset ' +
            'write_flash ' + erase_arg +
            '-z ' +
            '--flash_mode dio --flash_freq 40m --flash_size 4MB ' +
            '0x0000 ' +
            '"' + os.path.join(assets_path,'esp32c3','bootloader.bin') + '" ' +
            '0x8000 ' +
            '"' + os.path.join(assets_path,'esp32c3','partitions.bin') + '" ' +
            '0xe000 ' +
            '"' + os.path.join(assets_path,'esp32c3','boot_app0.bin') + '" ' +
            '0x10000 ' +
            '"' + firmware + '"'
            )
    elif 'esp32' in programmer:
        # flash was changed to 80 MHz QIO with this PR: https://github.com/olliw42/mLRS/pull/320
        # observed that the code will still run but flash writes fail with older bootloader
        firmware_version = int(''.join(re.search(r'v(\d+\.\d+\.\d+)', os.path.basename(firmware)).group(1).split('.')))

        if firmware_version >= 1307:
            bootloader_file = 'bootloader_80qio.bin'
        else:
            bootloader_file = 'bootloader_40dio.bin'
        #print(firmware_version, bootloader_file)

        # get the path to esp32 assets, from pacakge or running diretcly in Python
        if hasattr(sys, "_MEIPASS"):
            base_path = os.path.join(sys._MEIPASS, "assets", "esp32")
        else:
            base_path = os.path.join("assets", "esp32")

        args = [
            '--chip', 'esp32',
            '--port', comport,
            '--baud', str(baudrate),
            before_arg,
            '--after', 'hard-reset',
            'write-flash',
            erase_arg,
            '-z',
            '--flash-mode', 'dio',
            '--flash-freq', '40m',
            '--flash-size', '4MB',
            '--no-progress',
            '0x1000',
            os.path.join(base_path, bootloader_file),
            '0x8000',
            os.path.join(base_path,'partitions.bin'),
            '0xe000',
            os.path.join(base_path,'boot_app0.bin'),
            '0x10000',
            firmware
        ]
    elif ('esp8266' in programmer or 'esp8285' in programmer):
        args = [
            '--chip', 'esp8266',
            '--port', comport,
            '--baud', str(baudrate),
            before_arg,
            '--after', 'hard-reset',
            'write-flash',
            erase_arg,
            '--no-progress',
            '0x0',
            firmware
        ]
    #print(args)
    #args = '--port "' + radioport + '" ' + '--baud ' + str(baudrate) + ' ' + 'flash_id'
    args = flatten_list(args)
    return args

def flash_esptool(programmer, firmware, comport, baudrate):
    #erase_flash(comport, baudrate)
    args = _flash_esptool_argstr(programmer, firmware, comport, baudrate)
    esptool.main(args)

# def flash_esptool_win_as_script(programmer, firmware, comport, baudrate):
#     F = open(os.path.join('mlrs_flasher_runner.py'), 'w')
#     F.write('import os\n')
#     F.write('from mLRS_Flasher import _flash_esptool_argstr\n')
#     F.write("ESP_Programmer = os.path.join('thirdparty','esptool','esptool.py')\n")
#     F.write('args = _flash_esptool_argstr('+_cvtstr(programmer)+', '+_cvtstr(firmware)+', '+_cvtstr(comport)+', '+str(baudrate)+')\n')
#     F.write('os.system(ESP_Programmer + \' \' + args)\n')
#     F.write('print()\n')
#     F.write('print("*** DONE ***")\n')
#     F.write('print()\n')
#     F.write('print("Cheers, and have fun.")\n')
#     F.write('os.system("pause")\n')
#     F.close()
#     os_popen(['python','mlrs_flasher_runner.py'])


def flash_esptool_appassthru_win_as_script(programmer, serialx_no, firmware):
    F = open(os.path.join('mlrs_flasher_runner.py'), 'w')
    F.write('import os, time\n')
    F.write('from mLRS_Flasher import _flash_esptool_argstr\n')
    F.write('import apInitPassthru as appassthru\n')
    F.write("print('opening passthru...')\n")
    F.write('comport, baudrate = appassthru.mlrs_open_passthrough(None, 57600, ' + str(serialx_no) + ', ["nosysboot", "scripting"])\n')
    F.write("print('waiting for 5 secs...')\n")
    F.write('time.sleep(5.0)\n')
    F.write("print('flashing...')\n")
    F.write("ESP_Programmer = os.path.join('thirdparty','esptool','esptool.py')\n")
    F.write('args = _flash_esptool_argstr('+_cvtstr(programmer)+', '+_cvtstr(firmware)+', comport, baudrate)\n')
    F.write('os.system(ESP_Programmer + \' \' + args)\n')
    F.write('print()\n')
    F.write('print("*** DONE ***")\n')
    F.write('print()\n')
    F.write('print("Cheers, and have fun.")\n')
    F.write('os.system("pause")\n')
    F.close()
    os_popen(['python','mlrs_flasher_runner.py'])

def flash_esptool_passthru(programmer, serialx_no, firmware):
    print('opening passthru...')
    comport, baudrate = appassthru.mlrs_open_passthrough(None, 57600, serialx_no, ['nosysboot', 'scripting'])
    print('waiting for 5 secs...')
    time.sleep(5.0)
    print('flashing...')
    flash_esptool(programmer, firmware, comport, baudrate)

def flash_esptool_appassthru(programmer, serialx_no, firmware):
    print('Opening passthru...')
    comport, baudrate = appassthru.mlrs_open_passthrough(None, 57600, serialx_no, ['nosysboot', 'scripting'])
    #TODO: add a way to gracefully jump out in case of an error
    print('Flashing...')

    flash_esptool(programmer, firmware, comport, baudrate)
    print("*** DONE ***")
    print()
    print("Cheers, and have fun.")

def flashEspToolProgrammer(programmer, firmware, comport, baudrate):
    serialx_no = None
    f = re.search(r' serial([0-9]+?)', programmer.lower())
    if f:
        serialx_no = f.group(1)

    if os_system_run_as_script():
        #print('run as script file')
        if 'appassthru' in programmer:
            #flash_esptool_appassthru_win_as_script(programmer, serialx_no, firmware)
            flash_esptool_appassthru(programmer, serialx_no, firmware)

        else:
            #flash_esptool_win_as_script(programmer, firmware, comport, baudrate)
            flash_esptool(programmer, firmware, comport, baudrate)

        return # done

    if 'appassthru' in programmer:
        flash_esptool_appassthru(programmer, serialx_no, firmware)
    else:
        flash_esptool(programmer, firmware, comport, baudrate)
    print()
    print('*** DONE ***')
    print()
    print('Please remove the USB cable.')
    print('Cheers, and have fun.')


#flashEspToolProgrammer('esp8285 appassthru serial2', 'temp/rx-bayck-nano-pro-900-v1.3.05-@28fe6be0.bin', None, None)
#exit(1)


'''
--------------------------------------------------
Internal Tx Module Flashing Tools
--------------------------------------------------
'''

def flash_internal_elrs_tx_module_win_as_script(programmer, firmware, baudrate, wirelessbridge):
    F = open(os.path.join('mlrs_flasher_runner.py'), 'w')
    F.write('import os, time\n')
    F.write('from mLRS_Flasher import _flash_esptool_argstr\n')
    F.write('import edgetxInitPassthru as radio\n')
    F.write('radioport = radio.open_passthrough(comport = None, baudrate = '+str(baudrate)+', wirelessbridge = '+str(wirelessbridge)+')\n')
    F.write('print()\n')
    F.write('print("*** 3. Flashing the internal Tx Module ***")\n')
    F.write('print()\n')
    F.write('print("The firmware to flash is:",'+_cvtstr(firmware)+')\n')
    F.write("ESP_Programmer = os.path.join('thirdparty','esptool','esptool.py')\n")
    F.write('args = _flash_esptool_argstr('+_cvtstr(programmer)+', '+_cvtstr(firmware)+', radioport, '+str(baudrate)+')\n')
    F.write('os.system(ESP_Programmer + \' \' + args)\n')
    F.write('print()\n')
    F.write('print("*** DONE ***")\n')
    F.write('print()\n')
    F.write('print("Please remove the USB cable.")\n')
    F.write('print("Cheers, and have fun.")\n')
    F.write('os.system("pause")\n')
    F.close()
    os_popen(['python','mlrs_flasher_runner.py'])

#flash_internal_elrs_tx_module_win_as_script('temp/tx-jumper-internal-900-v1.3.05-@28fe6be0.bin')
#exit(1)


def flash_internal_elrs_tx_module(programmer, firmware, baudrate, wirelessbridge):
    # firmware filename gives the complete path
    #print(filename)
    #print(programmer)
    radioport = radio.open_passthrough(comport = None, baudrate = baudrate, wirelessbridge = wirelessbridge)

    print()
    print('*** 3. Flashing the internal Tx Module ***')
    print()
    print('The firmware to flash is:', firmware)

    # TODO: can we catch if this was succesfull?
    flash_esptool(programmer, firmware, radioport, baudrate)

    print()
    print('*** DONE ***')
    print()
    print('Please remove the USB cable.')
    print('Cheers, and have fun.')


def flashInternalElrsTxModule(programmer, firmware):
    if os_system_run_as_script():
        #print('run as script file')
        flash_internal_elrs_tx_module_win_as_script('esp32', firmware, baudrate = 921600, wirelessbridge = False)
        return # done

    flash_internal_elrs_tx_module('esp32', firmware, 921600, False)


def flashInternalElrsTxModuleWirelessBridge(programmer, firmware):
    if os_system_run_as_script():
        #print('run as script file')
        flash_internal_elrs_tx_module_win_as_script(programmer, firmware, baudrate = 115200, wirelessbridge = True)
        return # done

    flash_internal_elrs_tx_module(programmer, firmware, 115200, True)
