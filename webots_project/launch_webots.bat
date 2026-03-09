@echo off
REM Launch Webots Professional Restaurant Simulation
REM Features: Dynamic customers, multi-robot coordination, real-time orders

echo ========================================================
echo   🏪 PROFESSIONAL RESTAURANT SIMULATION - WEBOTS
echo ========================================================
echo.
echo Features:
echo   🤖 3 Self-Balancing Robots (Perfect PID tuning!)
echo   👥 Dynamic Customer Spawning System
echo   🍽️  Real-time Order Management
echo   🏪 Full Restaurant: Kitchen + Dining + Entrance
echo   ⏱️  Timed Deliveries with Statistics
echo.

REM Common Webots installation paths
set WEBOTS_PATH1="C:\Program Files\Webots\msys64\mingw64\bin\webots.exe"
set WEBOTS_PATH2="C:\Program Files (x86)\Webots\msys64\mingw64\bin\webots.exe"
set WEBOTS_PATH3="%LOCALAPPDATA%\Programs\Webots\msys64\mingw64\bin\webots.exe"

REM Check which path exists
if exist %WEBOTS_PATH1% (
    echo Found Webots at: %WEBOTS_PATH1%
    echo Launching PROFESSIONAL RESTAURANT simulation...
    echo.
    %WEBOTS_PATH1% "%~dp0worlds\professional_restaurant.wbt"
) else if exist %WEBOTS_PATH2% (
    echo Found Webots at: %WEBOTS_PATH2%
    echo Launching PROFESSIONAL RESTAURANT simulation...
    echo.
    %WEBOTS_PATH2% "%~dp0worlds\professional_restaurant.wbt"
) else if exist %WEBOTS_PATH3% (
    echo Found Webots at: %WEBOTS_PATH3%
    echo Launching PROFESSIONAL RESTAURANT simulation...
    echo.
    %WEBOTS_PATH3% "%~dp0worlds\professional_restaurant.wbt"
) else (
    echo.
    echo ERROR: Webots not found in common installation paths!
    echo.
    echo Please:
    echo   1. Install Webots from: https://cyberbotics.com/
    echo   2. Or manually open Webots and load:
    echo      %~dp0worlds\professional_restaurant.wbt
    echo.
    pause
    exit /b 1
)

echo.
echo Webots should be launching...
echo Watch the console for real-time updates!
echo.
echo Tips:
echo   - Wait for customers to arrive at tables
echo   - Robots will automatically pick up and deliver food
echo   - Check console for delivery statistics
echo.
