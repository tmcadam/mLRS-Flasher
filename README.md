<p align="left"><a href="https://raw.githubusercontent.com/olliw42/mLRS-docu/main/logos/mLRS_logo_long_w_slogan_1280x768.png"><img src="https://raw.githubusercontent.com/olliw42/mLRS-docu/main/logos/mLRS_logo_long_w_slogan_1280x768.png" align="center" height="153" width="256" ></a>

# mLRS Flasher Desktop App #

Link to the [mLRS project](https://github.com/olliw42/mLRS).


## Installation ##

### Windows ###

mLRSFlasher is based on Python, and thus needs a full Python3 installation on your system. Not very Win-like, we know, and we appologize for this.

- Install Python3 on your system, if you don't yet have it. Ensure that Python is in the PATH (the usual Python installation tutorials tell how to check that).
- Download the github repo and ensure you have unpacked it if you downloaded it as zip.
- Run the mLRS_Flasher.py script.
    - ***Note***: mLRS_Flasher needs the rights to write to disk and modify files on disk.
- It may happen that you get a bunch of errors and need to install additional packages. Follow the error messages. (you need "pillow", "requests", "pyserial", "customtkinter", "tk", "pymavlink")

### MacOS ###


### Ubuntu ###

```
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
```

```
sudo tee /etc/udev/rules.d/49-stm32dfu.rules << 'EOF'
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666"
EOF
sudo udevadm control --reload-rules
sudo udevadm trigger
```
Todo: Make an install script for this


#### Run the Flasher ####

````
./run_mLRS_Flasher_mac.sh
````

### Linux ###

TBD

## Developer Instructions ##

### Windows ###

  - Install Python and make sure available on path.
  - Create a virtual environment in the repo `python.exe -m venv venv`
  - Activate the virtual environment `venv\Scripts\activate.bat`
  - Install dependencies `pip install -r requirements.txt`
  - Run `build_win.bat` . The output will be in the `dist` folder, or...
  - Run `pyinstaller windows_exe.spec` or `pyinstaller windows_folder.spec`

### Linux ###

  - Install Python and make sure available on path.
  - Create a virtual environment in the repo `python3 -m venv venv`
  - May also need to install Tkinter `sudo apt install python3-tk`
  - Activate the virtual environment `. venv\Scripts\activate`
  - Install dependencies `pip install -r requirements.txt`
  - Run `bash build_lin.sh` . The output will be in the `dist` folder, or...
  - Run `pyinstaller linux_bin.spec` or `pyinstaller linux_folder.spec`


## Disclaimer ##

You of course use the app fully at your own risk.

