@echo off
title Build Kayzit NetManager Portable
echo ===================================================
echo [Kayzit NetManager] Building Instant Portable Package...
echo ===================================================

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: Clean old build outputs
if exist "Kayzit_NetManager" rmdir /s /q "Kayzit_NetManager"
if exist "Kayzit_NetManager_v1.0.1.zip" del /f /q "Kayzit_NetManager_v1.0.1.zip"

:: 1. Single definitive build: Instant Portable Directory (Opens in 0.1s, zero runtime decompression)
"%PYTHON_EXE%" -m PyInstaller --noconsole --onedir --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager" --distpath "dist_temp" --workpath "%TEMP%\kayzit_build" --clean main.py

:: Move output to clean root directory: Kayzit_NetManager
move "dist_temp\Kayzit_NetManager" "Kayzit_NetManager" >nul
if exist "dist_temp" rmdir /s /q "dist_temp"

:: 2. Create single distribution ZIP
powershell -Command "Compress-Archive -Path 'Kayzit_NetManager\*' -DestinationPath 'Kayzit_NetManager_v1.0.1.zip' -Force"

:: Clean up temporary build artifacts
if exist "%TEMP%\kayzit_build" rmdir /s /q "%TEMP%\kayzit_build"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "Kayzit_NetManager.spec" del /f /q "Kayzit_NetManager.spec"

echo.
echo ===================================================
echo [Kayzit NetManager] Build Complete!
echo.
echo 📁 Output Folder: %~dp0Kayzit_NetManager\Kayzit_NetManager.exe (Instant launch)
echo 📦 Release ZIP:   %~dp0Kayzit_NetManager_v1.0.1.zip
echo ===================================================
pause
