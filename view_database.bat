@echo off
REM Database Viewer Launcher
REM Opens the interactive database viewer for the Child Learning System

echo ========================================
echo   Database Viewer - Child Learning System
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

REM Check if view_database.py exists
if not exist "view_database.py" (
    echo ERROR: view_database.py not found!
    echo Make sure you're running this from the project root directory.
    pause
    exit /b 1
)

REM Check if database.py exists (required dependency)
python -c "import database" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: database.py module not found
    echo Make sure database.py is in the project directory
    pause
    exit /b 1
)

echo Starting Database Viewer...
echo.

REM Run the database viewer
python view_database.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Database viewer encountered an error
    pause
)
