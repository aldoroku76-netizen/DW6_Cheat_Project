@echo off
echo Installing PyInstaller...
pip install pyinstaller
echo.
echo Building DW6_Launcher.exe...
pyinstaller --noconsole --onefile --uac-admin --name "DW6_Launcher" launcher.py
echo.
echo BUILD SELESAI! Cek folder 'dist' untuk mengambil DW6_Launcher.exe.
pause