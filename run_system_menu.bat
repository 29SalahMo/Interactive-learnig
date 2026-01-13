@echo off
echo TuioKidsQuiz Interactive Learning System
echo ================================================
echo.

echo Checking system components...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

REM Check if required Python packages are installed
echo Checking Python packages...
python -c "import mediapipe, cv2, dollarpy" >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Required Python packages not found
    echo Installing packages...
    pip install mediapipe opencv-python dollarpy
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install Python packages
        echo WARNING: Continuing without Bluetooth support...
    )
) else (
    echo SUCCESS: Core Python packages are ready
)

REM Check if C# executable exists
if not exist "TUIO11_NET-master\TUIO11_NET-master\bin\Debug\TuioDemo.exe" (
    echo ERROR: C# executable not found
    echo Building C# project...
    cd "TUIO11_NET-master\TUIO11_NET-master"
    msbuild TUIO_DEMO.csproj
    if %errorlevel% neq 0 (
        echo ERROR: Failed to build C# project
        pause
        exit /b 1
    )
    cd ..\..
)

echo SUCCESS: All components ready!
echo.

echo Choose how to run the system:
echo.
echo 1. Run Complete System (GUI + Hand Recognition - PC Camera)
echo 2. Run Complete System with PHONE Camera (Phone for gestures, PC for markers)
echo 3. Run GUI Only (Test interface without hand gestures)
echo 4. Run Hand Recognition Only (Test camera and gestures)
echo 5. Test System Components
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto complete_system
if "%choice%"=="2" goto phone_camera_system
if "%choice%"=="3" goto gui_only
if "%choice%"=="4" goto hand_recognition_only
if "%choice%"=="5" goto test_system
if "%choice%"=="6" goto exit
goto invalid_choice

:complete_system
echo.
echo Starting Complete System...
echo.

REM Start C# GUI application FIRST (so socket server is ready)
echo Starting C# GUI Application...
cd "TUIO11_NET-master\TUIO11_NET-master\bin\Debug"
start "TuioKidsQuiz GUI" TuioDemo.exe
cd ..\..\..\..

REM Wait for C# GUI to start and initialize socket server
echo Waiting for GUI to initialize...
timeout /t 5 /nobreak >nul

REM Start Python hand gesture recognition
echo Starting Hand Gesture Recognition...
start "Hand Gesture Recognition" python stable_hand_recognition.py

REM Wait a moment for Python to start
timeout /t 3 /nobreak >nul

echo.
echo SUCCESS: Complete system started!
echo.
echo Running Components:
echo    Hand Gesture Recognition: Camera window open
echo    C# GUI Application: Full-screen interface
echo    TUIO Protocol: Active for marker communication
echo    Speech Recognition: Active for voice input
echo.
echo How to test:
echo    1. Look at the camera window for hand gestures
echo    2. Look at the GUI window for the quiz interface
echo    3. Place TUIO markers on table surface
echo    4. Speak answers aloud
echo    5. Show hand gestures to camera
echo.
echo Press any key to stop all components...
pause >nul

echo.
echo Stopping system components...
taskkill /f /im "python.exe" >nul 2>&1
taskkill /f /im "TuioDemo.exe" >nul 2>&1
echo System stopped.
goto end

:phone_camera_system
echo.
echo Starting Complete System with PHONE Camera Setup...
echo.
echo Make sure IriunWebcam is running (phone + Windows app connected)
echo.

REM Start C# GUI application FIRST (so socket server is ready)
echo Starting C# GUI Application...
cd "TUIO11_NET-master\TUIO11_NET-master\bin\Debug"
start "TuioKidsQuiz GUI" TuioDemo.exe
cd ..\..\..\..

REM Wait for C# GUI to start and initialize socket server
echo Waiting for GUI to initialize...
timeout /t 5 /nobreak >nul

REM Start Python hand gesture recognition with CAMERA 0 (phone)
echo Starting Hand Gesture Recognition with Phone Camera...
start "Hand Gesture Recognition - Phone" python stable_hand_recognition.py 0

REM Wait a moment for Python to start
timeout /t 3 /nobreak >nul

echo.
echo SUCCESS: Complete system started with phone camera!
echo.
echo CAMERA SETUP:
echo    Camera 0 = Phone (hand gestures)
echo    Camera 1 = PC (reacTIVision markers)
echo.
echo INSTRUCTIONS:
echo    1. Make sure IriunWebcam is running (phone + Windows app)
echo    2. Open reacTIVision.exe
echo    3. Select Camera 1 (PC camera) in reacTIVision
echo    4. Click Start in reacTIVision
echo    5. Place markers 0-5 on table
echo    6. Show hand gestures to PHONE camera
echo.
echo Press any key to stop all components...
pause >nul

echo.
echo Stopping system components...
taskkill /f /im "python.exe" >nul 2>&1
taskkill /f /im "TuioDemo.exe" >nul 2>&1
echo System stopped.
goto end

:gui_only
echo.
echo Starting GUI Only...
cd "TUIO11_NET-master\TUIO11_NET-master\bin\Debug"
start "TuioKidsQuiz GUI" TuioDemo.exe
cd ..\..\..\..

echo.
echo SUCCESS: GUI started!
echo.
echo You can test:
echo    TUIO markers (if you have them)
echo    Speech recognition
echo    Interface and animations
echo.
echo Press any key to close GUI...
pause >nul
taskkill /f /im "TuioDemo.exe" >nul 2>&1
goto end

:hand_recognition_only
echo.
echo Starting Hand Recognition Only...
python stable_hand_recognition.py
goto end

:test_system
echo.
echo Testing System Components...
python test_system.py
echo.
echo Press any key to continue...
pause >nul
goto end

:invalid_choice
echo.
echo ERROR: Invalid choice. Please enter 1-6.
echo.
goto end

:exit
echo.
echo Goodbye!
goto end

:end
echo.
echo System ready for interactive learning!
pause
