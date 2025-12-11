@echo off
setlocal

echo Building executable with PyInstaller...
pyinstaller mLRS_Flasher.py ^
    --noconsole ^
    --onefile ^
    --hidden-import=pymavlink ^
    --hidden-import=pymavlink.mavutil ^
    --hidden-import=pymavlink.dialects.v20.common ^
    --add-data "venv\Lib\site-packages\pymavlink\dialects;pymavlink/dialects" ^
    --add-data "venv\Lib\site-packages\esptool\targets\stub_flasher;esptool/targets/stub_flasher" ^
    --add-data "assets\*;assets" ^
    --add-data "thirdparty\stm32cubeprogrammer\win*;stm32cubeprogrammer" ^
    --icon "assets\mLRS_logo_round.ico" ^
    --name "mLRS_Flasher" ^
    --clean


echo.
echo Build complete. EXE should be in the dist/ folder.
pause
