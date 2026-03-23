@echo off
echo Cleaning old builds...
rd /s /q build dist
echo.
echo Starting Build Process...
pyinstaller --noconsole --onefile --distpath . main.py
echo.
echo BUILD COMPLETE! 
echo Your app is now ready as 'main.exe' in this folder.
pause