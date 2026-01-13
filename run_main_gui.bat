@echo off
REM Launcher for the Main GUI Application
REM This launches the unified GUI that integrates Login, Learning, and Quiz modes

echo ========================================
echo Interactive English Learning Quiz System
echo Main GUI Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo Checking Python packages...
python -c "import tkinter" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: tkinter is not available
    echo Please install Python with tkinter support
    pause
    exit /b 1
)

REM Check for face_recognition (optional but recommended)
python -c "import face_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: face_recognition library not found
    echo Face login/signup will not work without it
    echo Install with: pip install face-recognition
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" (
        exit /b 1
    )
)

REM Check for other required packages
python -c "import cv2" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing opencv-python...
    pip install opencv-python
)

python -c "import mediapipe" >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: mediapipe not found. Hand gesture recognition will not work.
    echo Install with: pip install mediapipe
)

echo.
echo Starting Main GUI Application...
echo.

REM Run the main GUI
python main_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start GUI application
    pause
)

