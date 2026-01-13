@echo off
REM Complete setup and push script for GitHub
REM Run this after installing Git and restarting your terminal

echo ========================================
echo   GitHub Setup and Push Script
echo   Interactive English Learning Quiz
echo ========================================
echo.

REM Check if Git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not found in PATH
    echo.
    echo Please:
    echo 1. Make sure Git is installed from https://git-scm.com/download/win
    echo 2. During installation, select "Add Git to PATH"
    echo 3. RESTART your terminal/command prompt after installation
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Git is installed
git --version
echo.

REM Navigate to script directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Step 1: Initialize Git (if not already done)
if not exist ".git" (
    echo [1/7] Initializing Git repository...
    git init
    echo [OK] Git repository initialized
    echo.
) else (
    echo [1/7] Git repository already initialized
    echo.
)

REM Step 2: Check/Add remote
echo [2/7] Configuring remote repository...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    git remote add origin https://github.com/29SalahMo/Interactive-learnig.git
    echo [OK] Remote repository added
) else (
    git remote set-url origin https://github.com/29SalahMo/Interactive-learnig.git
    echo [OK] Remote repository updated
)
echo.

REM Step 3: Check Git config
echo [3/7] Checking Git configuration...
git config user.name >nul 2>&1
if %errorlevel% neq 0 (
    echo Git user name not configured.
    set /p gitname="Enter your name for Git commits: "
    git config --global user.name "%gitname%"
)

git config user.email >nul 2>&1
if %errorlevel% neq 0 (
    echo Git user email not configured.
    set /p gitemail="Enter your email for Git commits: "
    git config --global user.email "%gitemail%"
)
echo [OK] Git configuration checked
echo.

REM Step 4: Add all files
echo [4/7] Adding all files to Git...
git add .
echo [OK] Files added
echo.

REM Step 5: Show status
echo [5/7] Current status:
git status --short
echo.

REM Step 6: Commit
echo [6/7] Committing changes...
git commit -m "Initial commit: Interactive English Learning Quiz System

- Main GUI with gender-based themes
- Face recognition login/signup
- Interactive learning mode with TUIO markers
- Quiz mode with gesture and laser pointer support
- Database management system
- Teacher interface
- Complete documentation"
echo [OK] Changes committed
echo.

REM Step 7: Push to GitHub
echo [7/7] Pushing to GitHub...
echo.
echo NOTE: You will be prompted for GitHub credentials.
echo If you haven't set up authentication:
echo 1. Use Personal Access Token (not password)
echo 2. Generate token at: https://github.com/settings/tokens
echo 3. Select 'repo' scope
echo.
pause

git branch -M main
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   SUCCESS! Project pushed to GitHub!
    echo ========================================
    echo.
    echo Repository URL: https://github.com/29SalahMo/Interactive-learnig
    echo.
    echo You can now view your code on GitHub!
    echo.
) else (
    echo.
    echo ========================================
    echo   ERROR: Failed to push to GitHub
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Verify GitHub credentials
    echo 3. Use Personal Access Token instead of password
    echo 4. Make sure you have write access to the repository
    echo.
    echo To generate a Personal Access Token:
    echo https://github.com/settings/tokens
    echo.
)

pause
