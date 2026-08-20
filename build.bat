@echo off
title Build Kayzit NetManager v1.0.1
echo ===================================================
echo [Kayzit NetManager] Building Single-File EXE to root folder...
echo ===================================================

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Build directly to root directory as a single portable executable
"%PYTHON_EXE%" -m PyInstaller --noconsole --onefile --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager_v1.0.1" --distpath . --workpath "%TEMP%\kayzit_build" --clean main.py

:: Clean up temporary build artifacts
if exist "%TEMP%\kayzit_build" rmdir /s /q "%TEMP%\kayzit_build"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Kayzit_NetManager_v1.0.1.spec" del /f /q "Kayzit_NetManager_v1.0.1.spec"

echo.
echo ===================================================
echo [Kayzit NetManager] Build Complete!
echo Output File: %~dp0Kayzit_NetManager_v1.0.1.exe
echo ===================================================
pause
