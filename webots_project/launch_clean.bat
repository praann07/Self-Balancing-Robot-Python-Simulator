@echo off
REM Clean Restaurant Environment - Self-Balancing Robot with Safety Features
REM Focus: Collision avoidance and boundary detection

echo ========================================
echo   CLEAN RESTAURANT ENVIRONMENT v4.0
echo   Self-Balancing Robot with Safety
echo ========================================
echo.

cd /d "%~dp0"

echo Starting restaurant world with enhanced robot...
echo.
echo NEW SAFETY FEATURES:
echo   - Restaurant boundary detection
echo   - Smart collision avoidance
echo   - Obstacle detection with 3 distance sensors
echo   - Emergency stop for critical obstacles
echo   - Intelligent path planning around obstacles
echo.
echo WHAT YOU'LL SEE:
echo   - Clean restaurant with 11 tables
echo   - Self-balancing two-wheeled robot
echo   - Automatic food delivery system
echo   - Robot stays inside restaurant boundaries
echo   - Avoids collisions with tables and walls
echo.

start "" "worlds\clean_restaurant.wbt"

echo.
echo Simulation launched!
echo If Webots doesn't open, manually open: worlds\clean_restaurant.wbt
echo.
pause
