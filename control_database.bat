@echo off
REM Database Control/Management Tool Launcher
REM Full control over database: add, edit, delete, manage data

echo ========================================
echo   Database Control Center
echo   Child Learning System - Full Management
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

REM Check if control_database.py exists
if not exist "control_database.py" (
    echo ERROR: control_database.py not found!
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

echo Starting Database Control Center...
echo.

REM Run the database control tool
python control_database.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Database control tool encountered an error
    pause
)
