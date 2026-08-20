@echo off
title Build Kayzit NetManager v1.0.1 Portable
echo ===================================================
echo [Kayzit NetManager v1.0.1] Building Instant Portable Package...
echo ===================================================

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

:: 1. Build Instant Portable Directory (Pre-extracted DLLs, Instant 0.1s Launch)
echo [1/3] Compiling Instant Portable Directory (DLL Architecture)...
"%PYTHON_EXE%" -m PyInstaller --noconsole --onedir --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager" --distpath "Kayzit_NetManager_v1.0.1" --workpath "%TEMP%\kayzit_build" --clean main.py

:: Move files from subdirectory to clean root folder format
if exist "Kayzit_NetManager_v1.0.1\Kayzit_NetManager" (
    xcopy /E /I /Y "Kayzit_NetManager_v1.0.1\Kayzit_NetManager\*" "Kayzit_NetManager_v1.0.1\" >nul
    rmdir /s /q "Kayzit_NetManager_v1.0.1\Kayzit_NetManager"
)

:: 2. Build Single Portable Executable (Fallback)
echo [2/3] Compiling Single-File Portable Executable...
"%PYTHON_EXE%" -m PyInstaller --noconsole --onefile --icon="resources/icon.ico" --add-data="resources;resources" --version-file="version_info.txt" --name="Kayzit_NetManager_Portable" --distpath . --workpath "%TEMP%\kayzit_build" --clean main.py

:: 3. Create Distribution ZIP archive
echo [3/3] Generating Kayzit_NetManager_v1.0.1_Portable.zip...
powershell -Command "Compress-Archive -Path 'Kayzit_NetManager_v1.0.1\*' -DestinationPath 'Kayzit_NetManager_v1.0.1_Portable.zip' -Force"

:: Clean up temporary build artifacts
if exist "%TEMP%\kayzit_build" rmdir /s /q "%TEMP%\kayzit_build"
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo ===================================================
echo [Kayzit NetManager v1.0.1] Build Complete!
echo.
echo 📁 1. Instant Portable Folder: %~dp0Kayzit_NetManager_v1.0.1\Kayzit_NetManager.exe (Instant launch)
echo 📦 2. Release ZIP Package:     %~dp0Kayzit_NetManager_v1.0.1_Portable.zip
echo ⚡ 3. Single EXE File:         %~dp0Kayzit_NetManager_Portable.exe
echo ===================================================
pause
