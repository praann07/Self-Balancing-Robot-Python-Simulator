# OpenGL Self-Balancing Robot Simulator

## 🤖 Interactive 3D Restaurant Service Robot Simulation

This is a Python + OpenGL/GLUT-based self-balancing robot simulator featuring a hotel restaurant environment with tables, customers, and realistic physics.

---

## 🚀 Quick Start

### Option 1: Quick Launch (Recommended)
**Double-click:** `quick_launch.bat`

This will immediately start the simulator.

### Option 2: Full Launch with Checks
**Double-click:** `launch_opengl_simulator.bat`

This will:
- Check Python installation
- Verify all dependencies
- Auto-install missing packages
- Launch the simulator with full diagnostics

---

## 📦 Installation

### First Time Setup

1. **Install Python** (if not already installed)
   - Download from: https://python.org
   - Version: Python 3.8 or higher
   - ✅ Make sure to check "Add Python to PATH" during installation

2. **Run Setup Script**
   - Double-click: `setup_dependencies.bat`
   - This installs all required packages:
     - PyOpenGL
     - PyOpenGL_accelerate
     - numpy

### Manual Installation (if needed)
```bash
pip install PyOpenGL PyOpenGL_accelerate numpy
```

---

## 🎮 Controls

### Robot Movement (WASD)
- **W** - Move Forward (Fast!)
- **X** - Move Backward
- **A** - Turn Left
- **D** - Turn Right
- **Q** or **Space** - Stop

### Robot Features
- **M** - Toggle Delivery Mode (Activate arms & food delivery)
- **B** - Toggle Sound Effects
- **T** - Toggle Auto Day/Night Cycle
- **N** - Change Time Manually (cycle through day/night)

### Simulation Controls
- **C** - Toggle PID Control
- **O** - Toggle Obstacle Detection (Auto-stop near objects)
- **R** - Reset Simulation
- **S** - Start
- **P** - Pause
- **F** - Toggle Follow Camera
- **H** - Show Detailed Help

### Camera Controls
- **Arrow Keys** - Rotate/Zoom Camera
- **Shift + Up/Down** - Raise/Lower Camera

### Function Keys (Alternative Controls)
- **F1** - Move Backward
- **F2** - Move Forward
- **F3** - Turn
- **F4** - Stop Motion
- **F5** - Toggle PID
- **F6** - Reset
- **F7/F8** - Push Robot
- **F9** - Toggle Follow Camera
- **Page Down/Up** - Start/Pause

---

## 🌟 Features

### Restaurant Environment
- ✅ 7 Tables with customers
- ✅ 20+ Seated customers
- ✅ 4 Wandering people
- ✅ 3D Obstacle detection (tables, chairs, pillars)

### Robot Capabilities
- ✅ Self-balancing two-wheeled design
- ✅ PID control system for stability
- ✅ Animated robot face with emotions 😊
- ✅ Articulated arms for food delivery 🦾
- ✅ Sound effects system 🔊
- ✅ Dynamic day/night lighting cycle 🌅
- ✅ Real-time status HUD display 📊

### Physics & Control
- ✅ Inverted pendulum dynamics
- ✅ PID controllers (angle, speed, rotation)
- ✅ Real-time obstacle avoidance
- ✅ Collision detection

---

## 📁 Files

### Launch Scripts
- `quick_launch.bat` - Simple launcher (fastest)
- `launch_opengl_simulator.bat` - Full launcher with checks
- `setup_dependencies.bat` - Install required packages

### Python Files
- `main.py` - Main simulation entry point
- `iballancingbot.py` - Robot physics and dynamics
- `pid.py` - PID controller implementation

---

## 🐛 Troubleshooting

### Problem: "Python is not recognized"
**Solution:** Add Python to your system PATH
1. Find Python installation folder (usually `C:\Python3X\`)
2. Add to system PATH environment variable
3. Restart command prompt

### Problem: "OpenGL import error"
**Solution:** Run `setup_dependencies.bat` or manually install:
```bash
pip install PyOpenGL PyOpenGL_accelerate
```

### Problem: "GLUT not found"
**Solution:** 
- Windows: May need to download freeglut from https://freeglut.sourceforge.net/
- Or try: `pip install freeglut`

### Problem: Simulation window closes immediately
**Solution:** Check console for error messages, ensure all dependencies are installed

### Problem: Low FPS / Slow performance
**Solution:** 
- Close other applications
- Update graphics drivers
- Try running without accelerate: uninstall PyOpenGL_accelerate

---

## 📊 System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- OpenGL 2.0+ compatible graphics
- Windows 7/10/11

### Recommended
- Python 3.10+
- 4GB RAM
- Dedicated GPU with OpenGL 3.0+
- Windows 10/11

---

## 🎓 Project Information

This is a self-balancing robot simulator demonstrating:
- Inverted pendulum control theory
- PID feedback systems
- 3D graphics with OpenGL
- Real-time physics simulation
- Restaurant service robot behavior

Perfect for:
- Control systems education
- Robotics demonstrations
- Project reviews and presentations
- Algorithm testing before hardware deployment

---

## 📝 License

See LICENSE file in project root.

---

## 🤝 Contributing

This is an educational project for self-balancing robot demonstration.

---

## 💡 Tips

1. **Start with PID enabled (C key)** - The robot balances automatically
2. **Use obstacle detection (O key)** - Prevents crashes
3. **Try delivery mode (M key)** - See articulated arms in action
4. **Enable follow camera (F key)** - Camera tracks robot movement
5. **Press H in simulation** - See all available controls

---

**Enjoy experimenting with the self-balancing robot! 🤖✨**
