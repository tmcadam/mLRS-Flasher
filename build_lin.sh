echo Building executable with PyInstaller...
pyinstaller mLRS_Flasher.py \
    --noconsole \
    --onefile \
    --hidden-import=pymavlink \
    --hidden-import=pymavlink.mavutil \
    --hidden-import=pymavlink.dialects.v20.common \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=PIL.ImageTk \
    --add-data "venv/lib/python3.12/site-packages/pymavlink/dialects:pymavlink/dialects" \
    --add-data "venv/lib/python3.12/site-packages/esptool/targets/stub_flasher:esptool/targets/stub_flasher" \
    --add-data "assets/*:assets" \
    --add-data "thirdparty/STM32CubeProgrammer/linux*:STM32CubeProgrammer" \
    --icon "assets/mLRS_logo_round.ico" \
    --name "mLRS_Flasher" \
    --clean


echo Build complete. EXE should be in the dist/ folder.

