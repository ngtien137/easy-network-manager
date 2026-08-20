@echo off
title Build Kayzit NetManager Portable
echo ===================================================
echo [Kayzit NetManager] Building Standalone Portable EXE to root folder...
echo ===================================================

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Build directly to root folder
"%PYTHON_EXE%" -m PyInstaller --noconsole --onefile --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager_Portable" --distpath . --workpath "%TEMP%\kayzit_build" --clean main.py

:: Clean up temporary build artifacts
if exist "%TEMP%\kayzit_build" rmdir /s /q "%TEMP%\kayzit_build"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo ===================================================
echo [Kayzit NetManager] Build complete! 
echo Output file: %~dp0Kayzit_NetManager_Portable.exe
echo ===================================================
pause
