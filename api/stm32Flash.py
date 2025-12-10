import time
import re

import api.apInitPassthru as appassthru
from api.helpers import get_stm32programmer_path, os_popen

'''
--------------------------------------------------
STM32 Flashing Tools
--------------------------------------------------
'''

def _flash_stm32cubeprogrammer_args(programmer, firmware, comport, baudrate):
    if 'dfu' in programmer:
        args = ['-c', 'port=usb1', '-w', firmware, '-v', '-g']
    elif 'uart' in programmer:
        args = ['-c', 'port='+comport, 'br='+str(baudrate), '-w', firmware, '-v', '-g']
    elif 'stlink' in programmer:
        args = [ '-c', 'port=SWD', 'freq=3900', '-w', firmware, '-v', '-g' ]
    return args


def flash_stm32cubeprogrammer(programmer, firmware, comport, baudrate):
    ST_Programmer = get_stm32programmer_path()
    print('Using STM32CubeProgrammer at:', ST_Programmer)
    args = _flash_stm32cubeprogrammer_args(programmer, firmware, comport, baudrate)
    os_popen([ST_Programmer] + args)

# def flash_stm32cubeprogrammer_appassthru_win_as_script(serialx_no, firmware):
#     F = open(os.path.join('mlrs_flasher_runner.py'), 'w')
#     F.write('import os, time\n')
#     F.write('from mLRS_Flasher import _flash_stm32cubeprogrammer_argstr\n')
#     F.write('import apInitPassthru as appassthru\n')
#     F.write("print('opening passthru...')\n")
#     F.write('comport, baudrate = appassthru.mlrs_open_passthrough(None, 57600, ' + str(serialx_no) + ')\n')
#     F.write("print('waiting for 5 secs...')\n")
#     F.write('time.sleep(5.0)\n')
#     F.write("print('flashing...')\n")
#     F.write("ST_Programmer = os.path.join('thirdparty','STM32CubeProgrammer','win','bin','STM32_Programmer_CLI.exe')\n")
#     F.write('args = _flash_stm32cubeprogrammer_argstr("uart", '+_cvtstr(firmware)+', comport, baudrate)\n')
#     F.write('os.system(ST_Programmer + \' \' + args)\n')
#     F.write('print()\n')
#     F.write('print("*** DONE ***")\n')
#     F.write('print()\n')
#     F.write('print("Cheers, and have fun.")\n')
#     F.write('os.system("pause")\n')
#     F.close()
#     os_popen(['python','mlrs_flasher_runner.py'])


def flash_stm32cubeprogrammer_appassthru(serialx_no, firmware):
    print('opening passthru...')
    comport, baudrate = appassthru.mlrs_open_passthrough(None, 57600, serialx_no)
    #TODO: add a way to gracefully jump out in case of an error
    print('waiting for 5 secs...')
    time.sleep(5.0)
    print('flashing...')
    flash_stm32cubeprogrammer('uart', firmware, comport, baudrate)


def flashSTM32CubeProgrammer(programmer, firmware, comport, baudrate):
    #print('flashSTM32CubeProgrammer()',programmer)

    serialx_no = None
    f = re.search(r' serial([0-9]+?)', programmer.lower())
    if f:
        serialx_no = f.group(1)

    if 'appassthru' in programmer:
        flash_stm32cubeprogrammer_appassthru(serialx_no, firmware)
    else:
        flash_stm32cubeprogrammer(programmer, firmware, comport, baudrate)

    print()
    print('*** DONE ***')
    print()
    print('Cheers, and have fun.')
