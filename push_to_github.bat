@echo off
REM Script to push project to GitHub
REM Make sure Git is installed and added to PATH

echo ========================================
echo   Push Project to GitHub
echo   Interactive English Learning Quiz
echo ========================================
echo.

REM Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed or not in PATH
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo Make sure to select "Add Git to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if .git exists
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

REM Check if remote exists
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    echo Adding remote repository...
    git remote add origin https://github.com/29SalahMo/Interactive-learnig.git
    echo.
) else (
    echo Remote repository already configured.
    echo.
)

REM Show current status
echo Current Git status:
git status
echo.

REM Ask user if they want to continue
set /p confirm="Do you want to add all files and push to GitHub? (y/n): "
if /i not "%confirm%"=="y" (
    echo Operation cancelled.
    pause
    exit /b 0
)

echo.
echo Adding all files...
git add .

echo.
echo Committing changes...
git commit -m "Update: Interactive English Learning Quiz System"

echo.
echo Pushing to GitHub...
echo Note: You may be prompted for GitHub credentials
echo.

REM Set main branch
git branch -M main

REM Push to GitHub
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Project pushed to GitHub!
    echo ========================================
    echo.
    echo Repository: https://github.com/29SalahMo/Interactive-learnig
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR: Failed to push to GitHub
    echo ========================================
    echo.
    echo Possible issues:
    echo 1. Authentication failed - use Personal Access Token
    echo 2. Network connection issue
    echo 3. Repository permissions
    echo.
    echo Try using GitHub Desktop for easier authentication:
    echo https://desktop.github.com/
    echo.
)

pause
