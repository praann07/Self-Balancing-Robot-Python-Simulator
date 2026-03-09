# Self-Balancing-Robot-Python-Simulator

A professional self-balancing two-wheeled restaurant service robot simulator with two versions:
1. **OpenGL Simulator** (src/) - Fast custom 3D visualization
2. **Webots Simulator** (webots_project/) - Professional physics engine (NEW! ⭐)

---

## 🎉 NEW: Webots Professional Simulator

A complete Webots implementation with realistic physics, collision detection, and autonomous food delivery!

**Quick Start:**
1. Install [Webots](https://cyberbotics.com/) (free)
2. Run: `webots_project\launch_webots.bat`
3. Or open: `webots_project\worlds\restaurant_service.wbt` in Webots

**Features:**
- ✅ Real physics engine (ODE)
- ✅ Professional robot model with arms and hands
- ✅ Realistic collision detection
- ✅ Autonomous navigation to tables
- ✅ Automatic food delivery system
- ✅ Distance sensors for obstacle avoidance

See [webots_project/README.md](webots_project/README.md) for full documentation.

---

## OpenGL Simulator (Original)

Here is presented a source code to simulate a self balancing two wheeled robot with python and using OpenGL to display the simulated robot.

This simulator has three files:

    ibalancingbot.py that provides a class IBallancingBot that deals with the mathematical model of the robot and with the resolution of the differencial equations.

    pid.py that provides a PID class to be able to control the robot.

    main.py that uses OpenGL to display the robot and provides the menu to use the simulation

Note that it is based on python 3.

## iballancingbot.py files

This file provides the IBalancingBot class. This class contains a mathematical model for the self balancing robot. This model is extract from the article 'A Comparison of Controllers for Balancing Two wheeled Inverted Pendulum Robot' available here.
The IBalancingBot class uses a Runge-Kutta approach to compute the differential equations of the robot's dynamic.

## pid.py file

This file provides a simple discrete PID class that is used to control the robot in the simulation. This implementation was found here. 

## main.py file

This is the main file of the simulator. It uses OpenGL to display the state the IBalancingBot and uses PID to control the robot. It uses 3 PIDs : one for the pendulum angle, one for the linear speed and one for the angular rotation speed. The OpenGL part is based on a Jean-Baptiste Fasquel file (http://perso-laris.univ-angers.fr/~fasquel). 
