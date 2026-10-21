@echo off

@rem if not "%~1"=="p" start /min cmd.exe /c %0 p&exit

set PATH=%~dp0\..\Python27;%PATH%

python Tools/generate_se_csv_text.py

pause