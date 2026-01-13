@echo off
REM Unified launcher for the Interactive English Learning Quiz System
REM Flow: Teacher Dashboard -> C# App -> (optionally) reacTIVision -> Main GUI

setlocal

REM You can change this if you use a different Python executable
set PY=python

echo ================================
echo 1) Starting Teacher Dashboard
echo ================================
start "" %PY% teacher_interface\main_teacher.py
timeout /t 2 >nul

echo ================================
echo 2) Starting C# Learning/Quiz App
echo ================================
REM This path must point to the built TuioDemo.exe
set CSHARP_EXE=TUIO11_NET-master\TUIO11_NET-master update\bin\Debug\TuioDemo.exe

if not exist "%CSHARP_EXE%" (
    echo [ERROR] C# executable not found:
    echo         %CSHARP_EXE%
    echo Please open the solution and build it in Visual Studio:
    echo         TUIO11_NET-master\TUIO11_NET-master update\TUIO_CSHARP.sln
    echo.
    pause
    goto :EOF
)

start "" "%CSHARP_EXE%"
timeout /t 3 >nul

echo ==========================================
echo 3) Make sure your TUIO source is running
echo ==========================================
echo - Start reacTIVision (or your TUIO tracker)
echo - Use port 3333
echo - Use marker IDs:
echo     * 0-8 for kids' learning markers
echo     * 50 for teacher circular menu control
echo.
pause

echo ================================
echo 4) Starting Main Student GUI
echo ================================
start "" %PY% main_gui.py

echo.
echo === NEXT STEPS INSIDE THE MAIN GUI ===
echo - First: use "Sign Up" to register a child face.
echo - Then: use "Face Login" to log in as that child.
echo - For Learning Mode: click "Start Learning Mode"
echo   (opens the C# app if not already visible).
echo - For Quiz Mode: click "Start Quiz Mode"
echo   (launches hand-gesture recognition and sends
echo    left/right answers to the C# app on port 8888).
echo.
echo The Teacher Dashboard circular menu is controlled
echo by rotating marker ID 50; pages will change when
echo you rotate that marker.
echo.
echo All components should now be running.
echo You can close this window.

endlocal


