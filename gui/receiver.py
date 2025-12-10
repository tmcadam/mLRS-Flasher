import customtkinter as ctk
from gui.ctkinter_components import CTkFlashButton, CTkInfoTextbox
from gui.messages import warning_dev_version, warning_dev_version_tag
from gui.ctkinter_components import CTkCompPortOptionMenu

from api import flashDevice
from gui.run_tool import cmd_in_output_window
from api.apInitPassthru import mlrs_open_passthrough


class ReceiverMixin:

    def appassthru_success(self, res):
        print("Restart device with receiver in boot mode")
        print("Then click 'Flash Receiver' to flash the firmware")
        self.rx_appassthru_state = True
        self.rx_appassthru_baud = res[1]
        self.rx_appassthru_comport = res[0]
        self.fReceiver_Flash_button.configure(text='Flash Receiver')

    # needs to be called whenever device type or firmware version changes
    # calls _download_firmware_files() to get the 'rx' file names in the tree, and updates Receiver 'Firmware Files' widget
    def updateReceiverFirmwareFiles(self):
        device_type = self.fReceiver_DeviceType_menu.get()
        firmware_version = self.fReceiver_FirmwareVersion_menu.get().split()[0] # remove the added ' (...)' from the version
        keys = self._download_firmware_files('rx', device_type, firmware_version)
        self.fReceiver_FirmwareFile_menu.configure(values=keys)
        self.fReceiver_FirmwareFile_menu.set(keys[0])
        return 'failed' not in keys[0]

 # calls flashDevice() for the selected device, firmware url, and filename, to initiate flashing
    def flashReceiverFirmware(self):
        device_type = self.fReceiver_DeviceType_menu.get()
        firmware_filename = self.fReceiver_FirmwareFile_menu.get()
        if 'failed' in firmware_filename:
            print('ERROR: flashReceiverFirmware() [1]')
            return
        #print(firmware_filename)
        chipset, flashmethod, description, wireless = self.get_metadata('rx', device_type, firmware_filename)
        if not flashmethod: flashmethod = 'default' # can be None
        if ',' in flashmethod: # the target allows several flashmethod, so we need to get the one which is selected
            sel = self.fReceiver_Flashmethod_menu.get()
            flashmethod = self.get_flashmethod_from_menu_opt(sel)
        #print('--->',flashmethod)
        #print(chipset)
        #print(self.rxFirmwareFilesList)
        for key in self.rxFirmwareFilesList:
            if firmware_filename in key['path']: # that's our firmware entry
                if 'stm32' in chipset:
                    if 'dfu' in flashmethod:
                        cmd_in_output_window(flashDevice, 'stm32 dfu', key['url'], firmware_filename)
                    elif 'appassthru' in flashmethod:
                        serialx = self.fReceiver_Serialx_menu.get().lower()
                        flashDevice('stm32 appassthru '+serialx, key['url'], firmware_filename)
                    elif 'uart' in flashmethod:
                        comport = self.fReceiver_ComPort_menu.get()
                        print('--->',comport)
                        cmd_in_output_window(flashDevice, 'stm32 uart', key['url'], firmware_filename, comport=comport, baudrate=115200)
                    else:
                        cmd_in_output_window(flashDevice, 'stm32 stlink', key['url'], firmware_filename) # STLink is default
                    return
                elif 'esp' in chipset:
                    # VSCODE/Platformio does 'no dtr', so we do too, seems not be critical
                    # VSCODE/Platformio uses for esp32 --flash_freq 80m, we do --flash_freq 40m
                    if 'appassthru' in flashmethod and self.rx_appassthru_state == False:
                        # This is the 'Start Passthrough' case
                        serialx = self.fReceiver_Serialx_menu.get().lower()
                        cmd_in_output_window(mlrs_open_passthrough, None, 57600, serialx[-1], ['nosysboot', 'scripting'], success_callback=self.appassthru_success)
                    elif 'appassthru' in flashmethod and self.rx_appassthru_state == True:
                        # This is the 'Flash Receiver' case in appassthru mode
                        serialx = self.fReceiver_Serialx_menu.get().lower()
                        comport, baudrate = self.fReceiver_ComPort_menu.get(), 921600
                        #print('--->',comport)
                        cmd_in_output_window(flashDevice, chipset + ' no dtr', key['url'], firmware_filename, comport=self.rx_appassthru_comport, baudrate=self.rx_appassthru_baud)

                    else: # 'esptool'
                        comport = self.fReceiver_ComPort_menu.get()
                        print('--->',comport)
                        flash_in_output_window(chipset + ' no dtr', key['url'], firmware_filename, comport=comport, baudrate=921600)
                    return
        print('ERROR: flashReceiverFirmware() [2]')


    #--------------------------------------------------
    #-- Receiver frame
    #--------------------------------------------------

    def initReceiverFrame(self):

        self.rx_appassthru_state = False

        self.fReceiver = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.fReceiver.grid_columnconfigure(1, weight=1)
        self.fReceiver.grid_columnconfigure(2, weight=0)
        self.fReceiver.grid_rowconfigure(5, weight=1)

        wrow = 0

        # Device Type
        self.fReceiver_DeviceType_label = ctk.CTkLabel(self.fReceiver,
            text="Device Type")
        self.fReceiver_DeviceType_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fReceiver_DeviceType_menu = ctk.CTkOptionMenu(self.fReceiver,
            values=["downloading..."],
            width=440,
            command=self.fReceiver_DeviceType_menu_event)
        self.fReceiver_DeviceType_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware Version
        self.fReceiver_FirmwareVersion_label = ctk.CTkLabel(self.fReceiver,
            text="Firmware Version")
        self.fReceiver_FirmwareVersion_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fReceiver_FirmwareVersion_menu = ctk.CTkOptionMenu(self.fReceiver,
            values=["downloading..."],
            width=440,
            command=self.fReceiver_FirmwareVersion_menu_event)
        self.fReceiver_FirmwareVersion_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Firmware File
        self.fReceiver_FirmwareFile_label = ctk.CTkLabel(self.fReceiver,
            text="Firmware File")
        self.fReceiver_FirmwareFile_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fReceiver_FirmwareFile_menu = ctk.CTkOptionMenu(self.fReceiver,
            values=["downloading..."],
            width=440,
            command=self.fReceiver_FirmwareFile_menu_event)
        self.fReceiver_FirmwareFile_menu.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        # Flash Buttons
        self.fReceiver_Flash_button = CTkFlashButton(self.fReceiver,
            text = "Flash Receiver",
            command = self.fReceiver_Flash_button_event)
        self.fReceiver_Flash_button.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20)
        wrow += 1

        # Flash Method Frame
        self.fReceiver_Flashmethod_label = ctk.CTkLabel(self.fReceiver,
            text="Flash Method")
        self.fReceiver_Flashmethod_label.grid(row=wrow, column=0, padx=20, pady=20)
        self.fReceiver_fFlashMethod = ctk.CTkFrame(self.fReceiver, corner_radius=0, fg_color="transparent")
        self.fReceiver_fFlashMethod.grid(row=wrow, column=1, padx=(0,20), sticky="w")
        wrow += 1

        self.fReceiver_Flashmethod_menu = ctk.CTkOptionMenu(self.fReceiver_fFlashMethod,
            #values=["-"],
            width=140,
            command=self.fReceiver_Flashmethod_menu_event)
        self.fReceiver_Flashmethod_menu.grid(row=0, column=0, padx=0, sticky="w")

        self.fReceiver_ComPort_menu = CTkCompPortOptionMenu(self.fReceiver_fFlashMethod,
            porttype = 'esp,usbttl',
            values=['COM1'],
            width=10,
            )#command=self.fReceiver_ComPort_menu_event)
        self.fReceiver_ComPort_menu.grid(row=0, column=1, padx=20)

        self.fReceiver_Serialx_menu = ctk.CTkOptionMenu(self.fReceiver_fFlashMethod,
            values=['SERIAL1','SERIAL2','SERIAL3','SERIAL4','SERIAL5','SERIAL6','SERIAL7','SERIAL8'],
            width=120,
            )#command=self.fReceiver_Serialx_menu_event)
        self.fReceiver_Serialx_menu.grid(row=0, column=1, padx=20)

        #self.fReceiver_Flashmethod_label.grid_remove()
        #self.fReceiver_fFlashMethod.grid_remove()
        #self.fReceiver_Serialx_menu.grid_remove()

        #-- Description text box --
        self.fReceiver_Description_textbox = CTkInfoTextbox(self.fReceiver,
            #height=100,
            font=("Courier New",12),
            )
        self.fReceiver_Description_textbox.grid(row=wrow, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")
        wrow += 1

        self.fReceiver_Description_textbox.setText("downloading metadata...\n")
        #self.fReceiver_Description_textbox.grid_remove()

    def fReceiver_UpdateWidgets(self):
        device_type = self.fReceiver_DeviceType_menu.get()
        firmware_filename = self.fReceiver_FirmwareFile_menu.get()
        _, flashmethod, description, wireless = self.get_metadata('rx', device_type, firmware_filename)
        text, tag = '', None
        if 'dev' in self.fReceiver_FirmwareVersion_menu.get():
            text, tag = warning_dev_version, warning_dev_version_tag
        if description != None:
            text += description
        if text != '':
            self.fReceiver_Description_textbox.grid()
            self.fReceiver_Description_textbox.setText(text, tag)
        else:
            self.fReceiver_Description_textbox.grid_remove()
        #flashmethod = 'esptool'
        #flashmethod = 'esptool,appassthru'
        #print(flashmethod)
        if flashmethod == None:
            self.fReceiver_Flashmethod_label.grid_remove()
            self.fReceiver_fFlashMethod.grid_remove()
        else:
            self.fReceiver_Flashmethod_label.grid()
            self.fReceiver_fFlashMethod.grid()
            menu_list = self.get_flashmethod_list_for_menu(flashmethod)
            self.fReceiver_Flashmethod_menu.configure(values=menu_list)
            self.fReceiver_Flashmethod_menu.set(menu_list[0])
            self.fReceiver_UpdateFlashMethodWidgets()

    def fReceiver_UpdateFlashMethodWidgets(self):
        sel = self.fReceiver_Flashmethod_menu.get()
        sel_flashmethod = self.get_flashmethod_from_menu_opt(sel)
        if sel_flashmethod == 'appassthru':
            self.fReceiver_ComPort_menu.grid_remove()
            self.fReceiver_Serialx_menu.grid()
            if self.rx_appassthru_state == True:
                self.fReceiver_Flash_button.configure(text='Flash Receiver')
            else:
                self.fReceiver_Flash_button.configure(text='Start Passthrough')
        elif sel_flashmethod == 'esptool':
            self.fReceiver_ComPort_menu.grid()
            self.fReceiver_Serialx_menu.grid_remove()
        elif sel_flashmethod == 'uart':
            self.fReceiver_ComPort_menu.grid()
            self.fReceiver_Serialx_menu.grid_remove()
        else:
            self.fReceiver_ComPort_menu.grid_remove()
            self.fReceiver_Serialx_menu.grid_remove()

    def fReceiver_ComPort_HandleIt(self):
        #device_type = self.fReceiver_DeviceType_menu.get()
        #firmware_filename = self.fReceiver_FirmwareFile_menu.get()
        #chipset, _, _, _ = self.get_metadata('rx', device_type, firmware_filename)
        self.fReceiver_ComPort_menu.update()

    def fReceiver_Startup(self):
        res = self.updateReceiverFirmwareFiles()
        self.fReceiver_ComPort_HandleIt()
        self.fReceiver_UpdateWidgets()
        return res

    def fReceiver_DeviceType_menu_event(self, opt):
        self.updateReceiverFirmwareFiles()
        self.fReceiver_ComPort_HandleIt()
        self.fReceiver_UpdateWidgets()

    def fReceiver_FirmwareVersion_menu_event(self, opt):
        self.updateReceiverFirmwareFiles()
        self.fReceiver_UpdateWidgets()

    def fReceiver_FirmwareFile_menu_event(self, opt):
        self.fReceiver_UpdateWidgets()

    def fReceiver_Flash_button_event(self):
        self.flashReceiverFirmware()

    def fReceiver_Flashmethod_menu_event(self, opt):
        self.fReceiver_UpdateFlashMethodWidgets()
