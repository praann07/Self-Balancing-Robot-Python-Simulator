@echo off
REM Professional Restaurant Simulation - Humanoid Robot Version
REM Launch script for GTA-5 Quality Graphics

echo ========================================
echo   HUMANOID RESTAURANT SIMULATION v2.0
echo   Realistic Human-Like Robots
echo   5-Finger Hands ^| GTA-5 Graphics
echo ========================================
echo.

cd /d "%~dp0"

echo Starting Webots with humanoid_restaurant.wbt...
echo.
echo What you'll see:
echo   - 3 Humanoid robots with realistic structure
echo   - Head, neck, torso, arms with 5-finger hands
echo   - Perfect self-balancing on two wheels
echo   - GTA-5 quality graphics with bloom and AO
echo   - Dynamic customers and food service
echo.

start "" "worlds\humanoid_restaurant.wbt"

echo.
echo Simulation launched!
echo If Webots doesn't open, manually open: worlds\humanoid_restaurant.wbt
echo.
pause
