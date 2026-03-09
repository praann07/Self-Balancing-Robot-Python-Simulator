@echo off
REM Setup Script - Install Dependencies for OpenGL Simulator

echo ============================================
echo   OPENGL SIMULATOR - DEPENDENCY INSTALLER
echo ============================================
echo.

cd /d "%~dp0"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.x from https://python.org
    pause
    exit /b 1
)

echo [OK] Python installed
echo.

echo Installing required packages...
echo.

echo [1/3] Installing PyOpenGL...
pip install PyOpenGL

echo.
echo [2/3] Installing PyOpenGL accelerate...
pip install PyOpenGL_accelerate

echo.
echo [3/3] Installing additional dependencies...
pip install numpy

echo.
echo ========================================
echo   INSTALLATION COMPLETE!
echo ========================================
echo.
echo You can now run the simulator using:
echo   - launch_opengl_simulator.bat (full version)
echo   - quick_launch.bat (simple version)
echo.
pause
