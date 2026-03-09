# Self-Balancing Robot Python Simulator

A self-balancing two-wheeled robot simulator built with Python, featuring two simulation environments: a custom OpenGL 3D renderer and a professional Webots physics engine. The robot models a real inverted pendulum system controlled by cascaded PID controllers.

---

## Overview

This project simulates a self-balancing service robot operating in a restaurant environment. It demonstrates control theory concepts (PID), rigid body dynamics (Runge-Kutta), and 3D visualization — all in Python.

Two simulation backends are provided:

| Simulator | Description |
|-----------|-------------|
| **OpenGL** (`self_balancing_robot/`) | Lightweight custom 3D renderer using PyOpenGL |
| **Webots** (`webots_project/`) | Professional physics engine with realistic collision detection |

---

## Features

- Inverted pendulum mathematical model with Runge-Kutta ODE solver
- Cascaded PID control: pendulum angle, linear speed, and angular rotation
- Interactive 3D visualization with day/night cycle and camera controls
- Restaurant environment with tables and autonomous food delivery
- Obstacle detection and avoidance
- Arduino code included for real hardware deployment

---

## Project Structure

```
Self-Balancing-Robot-Python-Simulator/
├── self_balancing_robot/       # OpenGL simulator
│   ├── main.py                 # Entry point, OpenGL rendering loop
│   ├── iballancingbot.py       # Robot dynamics and Runge-Kutta solver
│   └── pid.py                  # Discrete PID controller
├── webots_project/             # Webots simulator
│   ├── controllers/            # Robot and supervisor controllers
│   ├── protos/                 # Custom robot 3D models
│   └── worlds/                 # Simulation world files
├── Arduino_code/               # Firmware for physical robot hardware
└── pid.mlx                     # MATLAB PID tuning script
```

---

## Getting Started

### OpenGL Simulator

**Requirements:** Python 3.8+, PyOpenGL, numpy

```bash
pip install PyOpenGL PyOpenGL_accelerate numpy
```

Run the simulator:

```bash
cd self_balancing_robot
python main.py
```

Or on Windows, double-click `quick_launch.bat`.

### Webots Simulator

1. Install [Webots](https://cyberbotics.com/) (free, open-source)
2. Open `webots_project/worlds/restaurant_service.wbt` in Webots
3. Or double-click `webots_project/launch_webots.bat`

---

## Controls (OpenGL Simulator)

| Key | Action |
|-----|--------|
| W / X | Move forward / backward |
| A / D | Turn left / right |
| Q / Space | Stop |
| M | Toggle delivery mode |
| C | Toggle PID control |
| O | Toggle obstacle detection |
| F | Toggle follow camera |
| R | Reset simulation |
| Arrow Keys | Rotate / zoom camera |

---

## How It Works

### Robot Model (`iballancingbot.py`)

The physics are based on the mathematical model from *"A Comparison of Controllers for Balancing Two Wheeled Inverted Pendulum Robot"*. State equations are solved using a 4th-order Runge-Kutta method at each simulation step.

### PID Controller (`pid.py`)

Three PIDs run in cascade:
- **Angle PID** — keeps the robot upright
- **Speed PID** — controls linear velocity
- **Rotation PID** — controls turning

### Webots Controllers

- `self_balancing_robot.py` — main balance controller
- `restaurant_controller.py` — autonomous navigation and delivery logic
- `restaurant_supervisor.py` — environment supervisor and state manager

---

## Arduino Hardware

The `Arduino_code/` directory contains firmware to deploy the same PID control logic on actual hardware. The MATLAB script `pid.mlx` can be used to tune PID gains before flashing.

---

## License

See [LICENSE](LICENSE) for details.
