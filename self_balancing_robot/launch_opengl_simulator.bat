@echo off
REM ============================================================
REM   OpenGL Self-Balancing Robot Simulator Launcher
REM   Python + OpenGL/GLUT Interactive 3D Simulation
REM ============================================================

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   OPENGL SELF-BALANCING ROBOT SIMULATOR v2.0             ║
echo ║   Interactive 3D Restaurant Service Robot                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Change to the script directory
cd /d "%~dp0"

echo [INFO] Current directory: %CD%
echo [INFO] Checking Python installation...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo [HELP] Please install Python 3.x from https://python.org
    echo.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Found: %PYTHON_VERSION%
echo.

echo ========================================
echo   CHECKING REQUIRED PACKAGES
echo ========================================
echo.

REM Check for PyOpenGL
python -c "import OpenGL" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PyOpenGL not found!
    echo [INFO] Installing PyOpenGL...
    pip install PyOpenGL PyOpenGL_accelerate
    if errorlevel 1 (
        echo [ERROR] Failed to install PyOpenGL
        echo [HELP] Try manually: pip install PyOpenGL PyOpenGL_accelerate
        pause
        exit /b 1
    )
) else (
    echo [OK] PyOpenGL is installed
)

REM Check for GLUT (freeglut)
python -c "from OpenGL.GLUT import *" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] GLUT not found!
    echo [INFO] Installing freeglut...
    pip install freeglut
    if errorlevel 1 (
        echo [WARNING] Could not install freeglut via pip
        echo [INFO] You may need to install freeglut manually
        echo [HELP] Windows: Download from https://freeglut.sourceforge.net/
    )
) else (
    echo [OK] GLUT is installed
)

echo.
echo ========================================
echo   LAUNCHING SIMULATOR
echo ========================================
echo.
echo [INFO] Starting main.py...
echo [INFO] Use WASD keys to control the robot!
echo.
echo CONTROLS:
echo   W/A/S/D - Move and turn
echo   M - Toggle delivery mode
echo   O - Toggle obstacle detection
echo   C - Toggle PID control
echo   R - Reset simulation
echo   Press 'H' in simulator for full controls
echo.

REM Run the simulation
python main.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo [ERROR] Simulation terminated with errors!
    echo [HELP] Check the error messages above
) else (
    echo.
    echo [INFO] Simulation closed successfully
)

echo.
pause
