@echo off
title NetManager - Windows Process and Network Firewall
echo Starting NetManager...
set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

"%PYTHON_EXE%" "%~dp0main.py"
pause
