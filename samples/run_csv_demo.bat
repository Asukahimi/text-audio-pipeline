@echo off
rem 双击即可跑通 generate_se_csv_text.py（样例数据）
set PYTHONPATH=%~dp0..\tools\localization;%PYTHONPATH%
cd /d %~dp0
python ..\tools\localization\generate_se_csv_text.py
pause
