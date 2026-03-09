@echo off
REM Quick Launch - OpenGL Self-Balancing Robot Simulator

cd /d "%~dp0"

echo Starting OpenGL Self-Balancing Robot Simulator...
echo.
echo Controls: W/A/S/D = Move, M = Delivery Mode, O = Obstacles, R = Reset
echo.

python main.py

if errorlevel 1 (
    echo.
    echo Error! Check if Python and PyOpenGL are installed:
    echo   pip install PyOpenGL PyOpenGL_accelerate
    pause
)
