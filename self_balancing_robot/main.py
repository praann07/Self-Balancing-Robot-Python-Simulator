

import sys as sys;
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from math import cos
from math import sin
from math import pi
from math import sqrt
from math import atan2
from iballancingbot import IBalancingBot
from pid import PID


print("╔═══════════════════════════════════════════════════════════╗")
print("║   HOTEL RESTAURANT - SERVICE ROBOT SIMULATOR [HD]         ║")
print("║   🤖 Professional Food Service Robot with AI Features!    ║")
print("║   🍽️  7 Tables • 20+ Customers • 4 Wandering People       ║")
print("║   🚧 3D Obstacle Detection: Tables, Chairs, Pillars!      ║")
print("║   ✨ NEW FEATURES:                                        ║")
print("║      😊 Animated Robot Face with Emotions                ║")
print("║      🦾 Articulated Arms for Food Delivery               ║")
print("║      🔊 Sound Effects System                             ║")
print("║      🌅 Dynamic Day/Night Lighting Cycle                 ║")
print("║      📊 Real-time Status HUD Display                     ║")
print("╚═══════════════════════════════════════════════════════════╝\n")

print("=== ROBOT CONTROLS (WASD Keys) ===")
print("  ⬆️  W : MOVE FORWARD (Fast!)")
print("  ⬇️  X : MOVE BACKWARD")
print("  ⬅️  A : TURN LEFT")
print("  ➡️  D : TURN RIGHT")
print("  ⏹️  Q/Space : STOP")
print("")
print("=== NEW ROBOT FEATURES ===")
print("   M : Toggle DELIVERY MODE (Activate arms & food delivery)")
print("   B : Toggle SOUND EFFECTS on/off")
print("   T : Toggle AUTO DAY/NIGHT CYCLE")
print("   N : Change TIME manually (cycle through day/night)")
print("")
print("=== OTHER CONTROLS ===")
print("   C : Toggle PID control")
print("   O : Toggle OBSTACLE DETECTION (Auto-stop near objects)")
print("   R : Reset simulation")
print("   S : Start | P : Pause")
print("   F : Toggle follow camera")
print("   H : Show detailed help")
print("")
print(" [Function Keys - Alt Controls]")
print("   F1 : Move backward | F2 : Move forward")
print("   F3 : Turn | F4 : Stop motion")
print("   F5 : Toggle PID | F6 : Reset")
print("   F7/F8 : Push robot | F9 : Toggle follow camera")
print("   Page Down/Up : Start/Pause simulation")
print("")
print(" [Camera Controls]")
print("   Arrow Keys : Rotate/Zoom camera")
print("   Shift + Up/Down : Raise/Lower camera")
print("")

# -- Programme variables --

# variables for the animation of the dynamics
# ref_time : to compute the time between two redisplay$
# FPS : Frame per second, to 
ref_time, FPS = 0, 10

# position of the camera (glulookat parameters)
CameraPosX = 0.0
CameraPosY = 3
CameraPosZ = 10.0
ViewUpX = 0.0
ViewUpY = 1.0
ViewUpZ = 0.0
CenterX = 0.0
CenterY = 0.0
CenterZ = 0.0
follow_robot = True  # Camera automatically follows the robot

# to deal with the camera rotation and zoom
Theta,dtheta=0.0,2*pi/100.0
Radius = sqrt( CameraPosX**2+CameraPosZ**2)

# to draw cylinder
quadric = gluNewQuadric()
gluQuadricNormals(quadric, GLU_SMOOTH)

# the balancing robot
myBot = IBalancingBot()

# for the PIDs correction:
#   1 PID for the pendulum angle (phi)
#   1 PID for the linear x speed (xp)
#   1 PID for the robot angular speed rotation (psip)
myPIDphi = PID()
myPIDx = PID()
myPIDpsi = PID()

# to draw the robot at its actual position in the world
posx = posz = 0

# the command of the robot's wheels
F = [0, 0]

# activate or distactivate the PIDs correction
use_pid = True  # Start with PID enabled by default

# to deal with the "moving forwars" and "turning" commands
speed = 0
current_speed = 0
turn = 0
current_turn = 0

# Wandering people positions and animations
import random
people_positions = [
    {'x': -3, 'z': -3, 'angle': 0, 'dx': 0.002, 'dz': 0.003, 'shirt': (0.8, 0.3, 0.3)},
    {'x': 5, 'z': 2, 'angle': 90, 'dx': -0.003, 'dz': 0.001, 'shirt': (0.3, 0.5, 0.8)},
    {'x': -7, 'z': 7, 'angle': 180, 'dx': 0.001, 'dz': -0.002, 'shirt': (0.5, 0.3, 0.6)},
    {'x': 3, 'z': -8, 'angle': 270, 'dx': -0.002, 'dz': 0.002, 'shirt': (0.2, 0.6, 0.3)},
]

# ========== NEW PROFESSIONAL SERVICE ROBOT FEATURES ==========

# Robot face display system (animated emotions)
robot_face_emotion = "happy"  # Options: happy, neutral, worried, delivering, stopped
robot_face_blink_timer = 0
robot_face_blink_state = False

# Robot arms system for food delivery
robot_arm_left = {'shoulder': 0, 'elbow': 0}
robot_arm_right = {'shoulder': 0, 'elbow': 0}
robot_carrying_food = True  # Start with food loaded!
robot_arm_animation_timer = 0
robot_delivery_mode = False  # True when actively delivering
robot_target_table = None  # Which table to deliver to (1-7)

# Table positions for delivery system
restaurant_tables = [
    {'id': 1, 'x': -5, 'z': -5, 'radius': 0.5, 'served': False},
    {'id': 2, 'x': 4, 'z': -6, 'radius': 0.5, 'served': False},
    {'id': 3, 'x': -6, 'z': 5, 'radius': 0.45, 'served': False},
    {'id': 4, 'x': 6, 'z': 3, 'radius': 0.5, 'served': False},
    {'id': 5, 'x': 2, 'z': 6, 'radius': 0.5, 'served': False},
    {'id': 6, 'x': -8, 'z': -7, 'radius': 0.45, 'served': False},
    {'id': 7, 'x': 7, 'z': -3, 'radius': 0.4, 'served': False},
]

# Delivery tracking
delivery_distance = 1.0  # How close robot needs to be to deliver
delivery_animation_time = 0
delivery_in_progress = False

# Sound effects system
sound_enabled = True
last_sound_time = {'motor': 0, 'stop': 0, 'delivery': 0, 'pickup': 0}

# Dynamic day/night lighting cycle
time_of_day = 12.0  # Hours (0-24), starts at noon
time_speed = 0.01  # How fast time progresses
auto_time_cycle = True  # Automatic day/night progression

# Enhanced graphics settings
enable_shadows = True
enable_reflections = True
texture_quality = "high"  # Options: low, medium, high
ambient_occlusion = True

# Robot status indicators
robot_status = "idle"  # idle, moving, turning, delivering, stopped_obstacle
robot_deliveries_completed = 0
robot_distance_traveled = 0.0

# Obstacle avoidance system
# List of obstacles with positions (x, z), collision radius, and height range (min_y, max_y)
# Robot height: base at 0 to ~0.5m (can pass under objects above 0.5m)
obstacles = [
    # Tables (7 tables) - legs start at 0, top at 0.75, can't pass under
    {'x': -5, 'z': -5, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': 4, 'z': -6, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': -6, 'z': 5, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': 6, 'z': 3, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': 2, 'z': 6, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': -8, 'z': -7, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    {'x': 7, 'z': -3, 'radius': 1.2, 'min_y': 0.0, 'max_y': 0.8, 'type': 'table'},
    
    # Chairs around tables - seat at 0.45, back extends to ~1.0, can't pass under
    {'x': -5.7, 'z': -5, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -4.3, 'z': -5, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -5, 'z': -5.7, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -5, 'z': -4.3, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 4.7, 'z': -6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 3.3, 'z': -6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 4, 'z': -6.7, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -6.6, 'z': 5, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -5.4, 'z': 5, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -6, 'z': 5.6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 6.7, 'z': 3, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 5.3, 'z': 3, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 2.7, 'z': 6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 1.3, 'z': 6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 2, 'z': 6.7, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -8.6, 'z': -7, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -7.4, 'z': -7, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': -8, 'z': -7.6, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 7.5, 'z': -3, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    {'x': 6.5, 'z': -3, 'radius': 0.4, 'min_y': 0.0, 'max_y': 1.0, 'type': 'chair'},
    
    # Plants (8 plants) - from ground to ~0.7m height, robot might squeeze past but avoid
    {'x': -8, 'z': -8, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': 8, 'z': -8, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': -8, 'z': 8, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': 7, 'z': 7, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': -10, 'z': 0, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': 10, 'z': 0, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': 0, 'z': 8, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': -3, 'z': -9, 'radius': 0.6, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    
    # Service counter - tall obstacle from floor to 1.0m
    {'x': 0, 'z': -9, 'radius': 1.8, 'min_y': 0.0, 'max_y': 1.1, 'type': 'counter'},
    
    # Bar stools at counter
    {'x': -1, 'z': -7.5, 'radius': 0.35, 'min_y': 0.0, 'max_y': 0.7, 'type': 'stool'},
    {'x': 0, 'z': -7.5, 'radius': 0.35, 'min_y': 0.0, 'max_y': 0.7, 'type': 'stool'},
    {'x': 1, 'z': -7.5, 'radius': 0.35, 'min_y': 0.0, 'max_y': 0.7, 'type': 'stool'},
    
    # Decorative columns/pillars - floor to ceiling (2.5m), can't pass under
    {'x': -2, 'z': 0, 'radius': 0.4, 'min_y': 0.0, 'max_y': 2.6, 'type': 'pillar'},
    {'x': 2, 'z': 0, 'radius': 0.4, 'min_y': 0.0, 'max_y': 2.6, 'type': 'pillar'},
    
    # Extra plants for navigation challenge
    {'x': 0, 'z': -3, 'radius': 0.5, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': -5, 'z': 2, 'radius': 0.5, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    {'x': 5, 'z': -1, 'radius': 0.5, 'min_y': 0.0, 'max_y': 0.7, 'type': 'plant'},
    
    # Room divider sections - start at ground, height 1.5m
    {'x': -3, 'z': 3, 'radius': 0.7, 'min_y': 0.0, 'max_y': 1.5, 'type': 'divider'},
    {'x': 3, 'z': 4, 'radius': 0.7, 'min_y': 0.0, 'max_y': 1.5, 'type': 'divider'},
    
    # Boundary walls (invisible barriers at room edges to prevent robot from leaving)
    # North wall (z = -11)
    {'x': -10, 'z': -11, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -5, 'z': -11, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 0, 'z': -11, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 5, 'z': -11, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 10, 'z': -11, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    # South wall (z = 10)
    {'x': -10, 'z': 10, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -5, 'z': 10, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 0, 'z': 10, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 5, 'z': 10, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 10, 'z': 10, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    # West wall (x = -11)
    {'x': -11, 'z': -8, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -11, 'z': -4, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -11, 'z': 0, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -11, 'z': 4, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': -11, 'z': 8, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    # East wall (x = 11)
    {'x': 11, 'z': -8, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 11, 'z': -4, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 11, 'z': 0, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 11, 'z': 4, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    {'x': 11, 'z': 8, 'radius': 0.3, 'min_y': 0.0, 'max_y': 2.5, 'type': 'wall'},
    
    # Wandering people (will be updated dynamically in code)
    # These are placeholders for the 4 wandering people
    {'x': -3, 'z': -3, 'radius': 0.35, 'min_y': 0.0, 'max_y': 1.0, 'type': 'person', 'dynamic': True},
    {'x': 5, 'z': 2, 'radius': 0.35, 'min_y': 0.0, 'max_y': 1.0, 'type': 'person', 'dynamic': True},
    {'x': -7, 'z': 7, 'radius': 0.35, 'min_y': 0.0, 'max_y': 1.0, 'type': 'person', 'dynamic': True},
    {'x': 3, 'z': -8, 'radius': 0.35, 'min_y': 0.0, 'max_y': 1.0, 'type': 'person', 'dynamic': True},
]

avoidance_active = True  # Enable/disable obstacle avoidance
avoidance_distance = 2.0  # Distance at which robot starts detecting (realistic close range)
avoidance_strength = 0.8  # How aggressively to turn away
stop_threshold = 0.25  # Stop when within 25% of avoidance distance (0.5 units - very close!)
last_warning_time = 0  # Last time warning was printed (to prevent spam)

def updateWanderingPeople():
    """ Update positions of wandering people and their collision obstacles """
    global people_positions, obstacles
    for i, person in enumerate(people_positions):
        # Update position
        person['x'] += person['dx']
        person['z'] += person['dz']
        
        # Update angle to face movement direction
        if abs(person['dx']) > 0.0001:
            person['angle'] = 90 if person['dx'] > 0 else -90
        
        # Bounce off boundaries
        if abs(person['x']) > 10:
            person['dx'] = -person['dx']
        if abs(person['z']) > 10:
            person['dz'] = -person['dz']
        
        # Random direction change occasionally
        if random.random() < 0.01:  # 1% chance each frame
            person['dx'] = random.uniform(-0.003, 0.003)
            person['dz'] = random.uniform(-0.003, 0.003)
        
        # Update the corresponding dynamic obstacles for collision detection
        # Find and update dynamic person obstacles
        for obstacle in obstacles:
            if obstacle.get('type') == 'person' and obstacle.get('dynamic'):
                # Match by index (last 4 obstacles are the wandering people)
                obstacle_index = obstacles.index(obstacle)
                if obstacle_index >= len(obstacles) - 4:
                    person_idx = obstacle_index - (len(obstacles) - 4)
                    if person_idx == i:
                        obstacle['x'] = person['x']
                        obstacle['z'] = person['z']

def checkNearbyTable():
    """ Check if robot is near any unserved table - returns table if found """
    global posx, posz, restaurant_tables, delivery_distance, robot_carrying_food
    
    # Only check if robot has food to deliver
    if not robot_carrying_food:
        return None
    
    for table in restaurant_tables:
        # Skip already served tables
        if table['served']:
            continue
        
        # Calculate distance to table
        dx = table['x'] - posx
        dz = table['z'] - posz
        distance = sqrt(dx**2 + dz**2)
        
        # Check if within delivery range
        if distance < (delivery_distance + table['radius']):
            return table
    
    return None

def deliverFoodToTable(table):
    """ Deliver food to a table - trigger animation and mark as served """
    global robot_delivery_mode, robot_carrying_food, robot_deliveries_completed
    global delivery_animation_time, delivery_in_progress
    
    # Start delivery animation
    robot_delivery_mode = True
    delivery_in_progress = True
    delivery_animation_time = 0
    
    # Mark table as served
    table['served'] = True
    robot_deliveries_completed += 1
    
    # Show delivery message
    print(f"\n{'='*60}")
    print(f"🍽️  ✨ DELIVERY SUCCESSFUL! ✨")
    print(f"   📍 Table #{table['id']} at position ({table['x']:.1f}, {table['z']:.1f})")
    print(f"   🎉 Total Deliveries: {robot_deliveries_completed}")
    print(f"{'='*60}\n")
    
    playSound('delivery')

def updateDeliverySystem():
    """ Automatic delivery system - checks for nearby tables and delivers food """
    global delivery_animation_time, delivery_in_progress, robot_carrying_food
    global robot_delivery_mode
    
    # Check if delivery animation is in progress
    if delivery_in_progress:
        delivery_animation_time += 1
        
        # After 60 frames (about 1 second), complete delivery
        if delivery_animation_time > 60:
            delivery_in_progress = False
            robot_delivery_mode = False
            robot_carrying_food = False  # Food has been delivered
            
            # Automatically pick up new food after 30 more frames
            delivery_animation_time = 0
    
    # If robot doesn't have food, automatically give new food after a short delay
    if not robot_carrying_food and not delivery_in_progress:
        delivery_animation_time += 1
        if delivery_animation_time > 30:  # Wait 30 frames before new food
            robot_carrying_food = True
            delivery_animation_time = 0
            print("📦 New food loaded onto robot!")
    
    # Check for nearby tables to deliver to
    nearby_table = checkNearbyTable()
    if nearby_table and not delivery_in_progress:
        deliverFoodToTable(nearby_table)

def drawFoodOnTable(x, z):
    """ Draw delivered food items on a table """
    global quadric
    
    table_height = 0.77  # Height of table surface
    
    # Plate
    glPushMatrix()
    glTranslatef(x, table_height, z)
    glColor3d(0.95, 0.95, 0.9)  # White plate
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.12, 20, 20)
    glPopMatrix()
    
    # Food sphere/dome on plate
    glPushMatrix()
    glTranslatef(x, table_height + 0.05, z)
    glColor3d(0.9, 0.6, 0.2)  # Orange/yellow food color (appetizing!)
    glutSolidSphere(0.08, 16, 16)
    glPopMatrix()
    
    # Small garnish/details
    glPushMatrix()
    glTranslatef(x + 0.04, table_height + 0.03, z + 0.03)
    glColor3d(0.2, 0.7, 0.2)  # Green garnish
    glutSolidSphere(0.02, 10, 10)
    glPopMatrix()

def checkHardCollision():
    """ Hard collision check - returns True if robot is TOUCHING or INSIDE an obstacle
        This prevents the robot from passing through solid objects
        Stops at exact touch point - no penetration!
    """
    global posx, posz, obstacles
    
    robot_radius = 0.25  # Robot's collision radius (body is ~0.15m, with personal space ~0.25m)
    robot_min_y = 0.0
    robot_max_y = 0.5
    
    for obstacle in obstacles:
        dx = obstacle['x'] - posx
        dz = obstacle['z'] - posz
        distance = sqrt(dx**2 + dz**2)
        
        # Check if robot is touching or penetrating the obstacle
        # Using <= instead of < to stop AT the contact point
        collision_distance = robot_radius + obstacle['radius']  # Exact contact - no extra buffer
        
        if distance <= collision_distance:
            # Check height overlap
            obstacle_min_y = obstacle.get('min_y', 0.0)
            obstacle_max_y = obstacle.get('max_y', 999.9)
            height_overlap = (robot_min_y < obstacle_max_y) and (robot_max_y > obstacle_min_y)
            
            if height_overlap:
                return True  # Robot is colliding!
    
    return False

def checkPositionCollision(test_x, test_z):
    """ Check if a specific position would collide with obstacles
        Used to test positions BEFORE moving there
        Works for: tables, chairs, plants, humans, pillars, walls, ALL objects!
    """
    global obstacles
    
    robot_radius = 0.25  # Robot's collision radius (body is ~0.15m, with personal space ~0.25m)
    robot_min_y = 0.0
    robot_max_y = 0.5
    
    for obstacle in obstacles:
        dx = obstacle['x'] - test_x
        dz = obstacle['z'] - test_z
        distance = sqrt(dx**2 + dz**2)
        
        # Check if robot would touch or penetrate the obstacle
        # Using <= to prevent ANY penetration - stops at exact contact point
        collision_distance = robot_radius + obstacle['radius']  # Exact contact - no extra buffer
        
        if distance <= collision_distance:
            # Check height overlap
            obstacle_min_y = obstacle.get('min_y', 0.0)
            obstacle_max_y = obstacle.get('max_y', 999.9)
            height_overlap = (robot_min_y < obstacle_max_y) and (robot_max_y > obstacle_min_y)
            
            if height_overlap:
                return True  # Would collide!
    
    return False

# Removed applyObstacleAvoidance() - No warnings, only hard collision!
# Robot moves freely until it physically touches an object, then stops immediately.

def initPIDs():
    """ Function that initializes the PIDs parameters (Kp, Ki, Kd)
    """
    global myPIDphi, myPIDx, myPIDpsi

    myPIDphi.setKp(7.0)
    myPIDphi.setKi(0.1)
    myPIDphi.setKd(6.0)
    myPIDphi.setPoint(0)

    myPIDx.setKp(0.01)
    myPIDx.setKi(0.005)
    myPIDx.setKd(0.01)
    myPIDx.setPoint(0)

    myPIDpsi.setKp(1)
    myPIDpsi.setKi(1)
    myPIDpsi.setKd(0)
    myPIDpsi.setPoint(0)
    

def correction():
    """ Function that uses the PID and the robot state to generate a new 
        command according to the speed and turn objectives
    """
    global myBot, F, myPIDx, myPIDphi, myPIDpsi, use_pid
    global speed, current_speed, turn, current_turn

    if(use_pid):
        if(current_speed != speed):
            current_speed = speed
            myPIDx.setPoint(speed)  # we only want to reset the PID when the speed changes

        if(current_turn != turn):
            current_turn = turn
            myPIDpsi.setPoint(turn)  # we only want to reset the PID when the rotation changes

        pidx_value = myPIDx.update(myBot.xp)  # Pid over linear a speed
        pidpsi_value = myPIDpsi.update(-myBot.psip)  # Pid over psi angular speed rotation

        tilt = - pidx_value + myBot.phi
        rotation = pidpsi_value

        pidphi_value = myPIDphi.update(tilt)  # pid over the pendulum angle phi

        F = [-pidphi_value-rotation,-pidphi_value+rotation]
    else:
        F = [0, 0]


def animation():
    """ Function to compute the robot state at each time step and to draw it in the world
    """
    global ref_time, FPS, F, posx, posz, myBot, robot_distance_traveled, speed
    # FPS expressed in ms between 2 consecutive frame
    delta_t = 0.001 # the time step for the computation of the robot state
    if glutGet(GLUT_ELAPSED_TIME)-ref_time > (1.0/FPS)*1000 :
        # at each redisplay (new display frame)
        dst = 0
        for i in range(0,100):
            # we want the computation of the robot state to be faster than the 
            # display to limit the compution errors
            # display : new frame at each 100ms
            # deltat : 1ms for the differential equation evaluation
            
            # Store previous position before update
            prev_posx = posx
            prev_posz = posz
            
            myBot.dynamics(delta_t, F)
            # we also compute the new x and z position of the robot in the world
            dst = (myBot.xp * delta_t)
            new_posx = posx + dst*cos(myBot.psi)
            new_posz = posz + (-dst*sin(myBot.psi))
            
            # HARD COLLISION CHECK - Test new position BEFORE moving there!
            if checkPositionCollision(new_posx, new_posz):
                # Cannot move to this position - solid object blocking!
                # Don't update position, force complete stop
                myBot.xp = 0  # Stop velocity immediately
                myBot.xpp = 0  # Stop acceleration
                dst = 0
                # Keep previous position (don't move)
            else:
                # Safe to move - update position
                posx = new_posx
                posz = new_posz
            
            # Track distance traveled
            robot_distance_traveled += abs(dst)

        # ========== NEW: Update service robot features ==========
        updateTimeOfDay()  # Update day/night cycle
        animateRobotArms()  # Animate robot arms
        updateRobotFaceEmotion()  # Update face expression
        updateDeliverySystem()  # Automatic food delivery system
        
        # Play movement sounds
        if abs(speed) > 0:
            playSound('motor')
        if abs(turn) > 0:
            playSound('turn')
        
        # Physics-based collision only - no warnings, just real solid object collision!
        correction()  # calls the PIDs if enable
        updateWanderingPeople()  # Update wandering people positions
        glutPostRedisplay()  # refresh the display
        ref_time=glutGet(GLUT_ELAPSED_TIME)

def drawGround():
    """ Function to draw a realistic polished restaurant floor
    """
    nb_rows = 30
    nb_cols = 30
    
    # Draw main floor with elegant tiles
    for r in range(0, nb_rows):
        for c in range(0, nb_cols):
            # Elegant marble-like floor pattern
            if (r % 2 == 0 and c % 2 == 0) or (r % 2 == 1 and c % 2 == 1):
                glColor3d(0.92, 0.88, 0.85)  # Light cream tile
            else:
                glColor3d(0.85, 0.82, 0.78)  # Slightly darker cream
            
            glBegin(GL_QUADS)
            glVertex3f(c - nb_cols/2, 0, r - nb_rows/2)
            glVertex3f(c - nb_cols/2 + 1, 0, r - nb_rows/2)
            glVertex3f(c - nb_cols/2 + 1, 0, r - nb_rows/2 + 1)
            glVertex3f(c - nb_cols/2, 0, r - nb_rows/2 + 1)
            glEnd()
    
    # Draw grout lines between tiles (subtle)
    glLineWidth(1.5)
    glColor3d(0.75, 0.72, 0.68)  # Grout color
    
    # Horizontal lines
    for r in range(0, nb_rows + 1):
        glBegin(GL_LINES)
        glVertex3f(-nb_cols/2, 0.005, r - nb_rows/2)
        glVertex3f(nb_cols/2, 0.005, r - nb_rows/2)
        glEnd()
    
    # Vertical lines
    for c in range(0, nb_cols + 1):
        glBegin(GL_LINES)
        glVertex3f(c - nb_cols/2, 0.005, -nb_rows/2)
        glVertex3f(c - nb_cols/2, 0.005, nb_rows/2)
        glEnd()
    
    glLineWidth(1.0)

def drawSky():
    """ Function to draw a sky gradient background
    """
    # Draw a large quad behind everything for sky
    glDisable(GL_DEPTH_TEST)  # Draw behind everything
    
    glBegin(GL_QUADS)
    # Sky blue gradient from top to horizon
    glColor3d(0.4, 0.6, 0.9)  # Top - bright blue
    glVertex3f(-50, 30, -50)
    glVertex3f(50, 30, -50)
    
    glColor3d(0.7, 0.8, 0.95)  # Horizon - lighter blue
    glVertex3f(50, 0, -50)
    glVertex3f(-50, 0, -50)
    glEnd()
    
    glEnable(GL_DEPTH_TEST)

def drawWalls():
    """ Function to draw walls for a hotel restaurant
    """
    wall_height = 3.0
    wall_distance = 15
    
    # Back wall (warm restaurant color)
    glPushMatrix()
    glColor3d(0.88, 0.85, 0.78)  # Warm beige/cream restaurant wall
    glBegin(GL_QUADS)
    glVertex3f(-wall_distance, 0, -wall_distance)
    glVertex3f(wall_distance, 0, -wall_distance)
    glVertex3f(wall_distance, wall_height, -wall_distance)
    glVertex3f(-wall_distance, wall_height, -wall_distance)
    glEnd()
    glPopMatrix()
    
    # Add crown molding at top of back wall
    glColor3d(0.95, 0.95, 0.92)
    glBegin(GL_QUADS)
    glVertex3f(-wall_distance, wall_height-0.1, -wall_distance+0.05)
    glVertex3f(wall_distance, wall_height-0.1, -wall_distance+0.05)
    glVertex3f(wall_distance, wall_height, -wall_distance)
    glVertex3f(-wall_distance, wall_height, -wall_distance)
    glEnd()
    
    # Side walls (warm color)
    glColor3d(0.85, 0.82, 0.75)
    
    # Left wall
    glBegin(GL_QUADS)
    glVertex3f(-wall_distance, 0, -wall_distance)
    glVertex3f(-wall_distance, 0, wall_distance)
    glVertex3f(-wall_distance, wall_height, wall_distance)
    glVertex3f(-wall_distance, wall_height, -wall_distance)
    glEnd()
    
    # Right wall
    glBegin(GL_QUADS)
    glVertex3f(wall_distance, 0, -wall_distance)
    glVertex3f(wall_distance, 0, wall_distance)
    glVertex3f(wall_distance, wall_height, wall_distance)
    glVertex3f(wall_distance, wall_height, -wall_distance)
    glEnd()

def drawTable(x, z, radius):
    """ Draw a round dining table at position (x, z)
    """
    global quadric
    table_height = 0.75
    
    # Table top (round)
    glPushMatrix()
    glTranslatef(x, table_height, z)
    glColor3d(0.4, 0.25, 0.15)  # Dark wood color
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, radius, 32, 32)
    glPopMatrix()
    
    # Table edge (cylinder)
    glPushMatrix()
    glTranslatef(x, table_height-0.05, z)
    glColor3d(0.35, 0.22, 0.12)  # Darker wood
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, radius, radius, 0.05, 32, 16)
    glPopMatrix()
    
    # Table leg (center pedestal)
    glPushMatrix()
    glTranslatef(x, 0.1, z)
    glColor3d(0.3, 0.2, 0.1)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.08, 0.12, table_height-0.1, 16, 16)
    glPopMatrix()
    
    # Table base
    glPushMatrix()
    glTranslatef(x, 0.02, z)
    glColor3d(0.25, 0.15, 0.08)
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.3, 32, 32)
    glPopMatrix()

def drawChair(x, z, rotation):
    """ Draw a dining chair at position (x, z) with rotation
    """
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    
    # Seat
    glPushMatrix()
    glTranslatef(0, 0.45, 0)
    glColor3d(0.35, 0.2, 0.1)  # Wood color
    glScalef(0.35, 0.05, 0.35)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Backrest
    glPushMatrix()
    glTranslatef(0, 0.7, -0.15)
    glColor3d(0.35, 0.2, 0.1)
    glScalef(0.35, 0.5, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Legs (4 legs)
    leg_positions = [(-0.15, -0.15), (0.15, -0.15), (-0.15, 0.15), (0.15, 0.15)]
    for lx, lz in leg_positions:
        glPushMatrix()
        glTranslatef(lx, 0.225, lz)
        glColor3d(0.3, 0.18, 0.08)
        glScalef(0.04, 0.45, 0.04)
        glutSolidCube(1.0)
        glPopMatrix()
    
    glPopMatrix()

def drawPlant(x, z):
    """ Draw a decorative potted plant
    """
    global quadric
    
    # Pot
    glPushMatrix()
    glTranslatef(x, 0.15, z)
    glColor3d(0.6, 0.3, 0.2)  # Terracotta pot
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.12, 0.15, 0.3, 16, 16)
    glPopMatrix()
    
    # Pot base
    glPushMatrix()
    glTranslatef(x, 0.01, z)
    glColor3d(0.55, 0.28, 0.18)
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.15, 16, 16)
    glPopMatrix()
    
    # Plant leaves (multiple spheres)
    leaf_positions = [(0, 0.5, 0), (-0.1, 0.55, 0.05), (0.1, 0.6, -0.05), 
                      (0.05, 0.65, 0.08), (-0.08, 0.62, -0.06)]
    for lx, ly, lz in leaf_positions:
        glPushMatrix()
        glTranslatef(x+lx, ly, z+lz)
        glColor3d(0.2, 0.6, 0.2)  # Green leaves
        glutSolidSphere(0.12, 12, 12)
        glPopMatrix()

def drawServiceCounter(x, z):
    """ Draw a service counter/bar
    """
    counter_height = 1.0
    counter_length = 2.5
    counter_depth = 0.6
    
    # Counter top
    glPushMatrix()
    glTranslatef(x, counter_height, z)
    glColor3d(0.15, 0.15, 0.18)  # Dark granite countertop
    glScalef(counter_length, 0.05, counter_depth)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Counter base/cabinets
    glPushMatrix()
    glTranslatef(x, counter_height/2, z)
    glColor3d(0.5, 0.5, 0.52)  # Stainless steel
    glScalef(counter_length, counter_height, counter_depth)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Menu board on wall behind counter
    glPushMatrix()
    glTranslatef(x, counter_height + 0.8, z - counter_depth/2 - 0.02)
    glColor3d(0.1, 0.1, 0.12)  # Dark board
    glScalef(counter_length * 0.8, 0.6, 0.02)
    glutSolidCube(1.0)
    glPopMatrix()

def drawWallDecor(x, y, z, size):
    """ Draw wall decorations (paintings/frames)
    """
    # Frame
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3d(0.6, 0.5, 0.3)  # Gold frame
    glScalef(size, size*0.7, 0.02)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Picture (interior)
    glPushMatrix()
    glTranslatef(x, y, z + 0.01)
    glColor3d(0.7, 0.5, 0.4)  # Abstract art color
    glScalef(size*0.85, size*0.6, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()

def drawFoodTray():
    """ Draw a food service tray on top of the robot
    """
    global quadric
    tray_height = 0.52  # Height above robot base
    
    # Tray platform (rectangular)
    glPushMatrix()
    glTranslatef(0, tray_height, 0)
    glColor3d(0.7, 0.7, 0.75)  # Metallic tray
    glScalef(0.25, 0.02, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Food items on tray (represented as colored shapes)
    # Plate 1
    glPushMatrix()
    glTranslatef(-0.06, tray_height + 0.02, 0)
    glColor3d(0.95, 0.95, 0.9)  # White plate
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.05, 16, 16)
    glPopMatrix()
    
    # Food on plate 1 (small sphere)
    glPushMatrix()
    glTranslatef(-0.06, tray_height + 0.04, 0)
    glColor3d(0.8, 0.6, 0.3)  # Food color
    glutSolidSphere(0.03, 12, 12)
    glPopMatrix()
    
    # Glass/cup
    glPushMatrix()
    glTranslatef(0.06, tray_height + 0.02, 0)
    glColor3d(0.3, 0.5, 0.8)  # Blue drink
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.025, 0.03, 0.08, 16, 16)
    glPopMatrix()

def drawPerson(x, z, rotation, shirt_color):
    """ Draw a person/customer sitting at a table
    """
    glPushMatrix()
    glTranslatef(x, 0, z)
    glRotatef(rotation, 0, 1, 0)
    
    # Legs (sitting)
    glPushMatrix()
    glTranslatef(0, 0.25, 0)
    glColor3d(0.2, 0.2, 0.3)  # Dark pants
    glScalef(0.15, 0.3, 0.12)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Torso/shirt
    glPushMatrix()
    glTranslatef(0, 0.6, 0)
    glColor3d(*shirt_color)  # Shirt color
    glScalef(0.2, 0.35, 0.15)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Arms (2)
    for side in [-0.13, 0.13]:
        glPushMatrix()
        glTranslatef(side, 0.55, 0)
        glColor3d(shirt_color[0]*0.9, shirt_color[1]*0.9, shirt_color[2]*0.9)
        glScalef(0.06, 0.25, 0.06)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(0, 0.88, 0)
    glColor3d(0.92, 0.75, 0.62)  # Skin tone
    glutSolidSphere(0.1, 16, 16)
    glPopMatrix()
    
    # Hair
    glPushMatrix()
    glTranslatef(0, 0.93, 0)
    glColor3d(0.15, 0.1, 0.05)  # Dark hair
    glutSolidSphere(0.095, 12, 12)
    glPopMatrix()
    
    glPopMatrix()

def drawCeilingLight(x, z):
    """ Draw a hanging ceiling light
    """
    global quadric
    
    # Hanging cord
    glPushMatrix()
    glTranslatef(x, 2.5, z)
    glColor3d(0.1, 0.1, 0.1)  # Black cord
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.01, 0.01, 0.4, 8, 8)
    glPopMatrix()
    
    # Light fixture (shade)
    glPushMatrix()
    glTranslatef(x, 2.1, z)
    glColor3d(0.9, 0.85, 0.7)  # Warm light shade
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.25, 0.15, 0.2, 16, 16)
    glPopMatrix()
    
    # Light bulb glow (bright yellow sphere)
    glPushMatrix()
    glTranslatef(x, 2.05, z)
    glColor3d(1.0, 0.95, 0.7)  # Bright warm glow
    glutSolidSphere(0.08, 16, 16)
    glPopMatrix()

def drawWindow(x, y, z):
    """ Draw a restaurant window
    """
    window_width = 1.2
    window_height = 1.5
    
    # Window frame
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3d(0.3, 0.25, 0.2)  # Dark wood frame
    glScalef(window_width + 0.1, window_height + 0.1, 0.05)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Window glass (semi-transparent blue)
    glEnable(GL_BLEND)
    glPushMatrix()
    glTranslatef(x, y, z + 0.01)
    glColor4f(0.6, 0.75, 0.9, 0.5)  # Light blue glass
    glScalef(window_width, window_height, 0.02)
    glutSolidCube(1.0)
    glPopMatrix()
    glDisable(GL_BLEND)
    
    # Window divider (vertical)
    glPushMatrix()
    glTranslatef(x, y, z + 0.02)
    glColor3d(0.3, 0.25, 0.2)
    glScalef(0.05, window_height, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Window divider (horizontal)
    glPushMatrix()
    glTranslatef(x, y, z + 0.02)
    glColor3d(0.3, 0.25, 0.2)
    glScalef(window_width, 0.05, 0.01)
    glutSolidCube(1.0)
    glPopMatrix()

def drawTableSetting(x, z):
    """ Draw plates, cups, and utensils on a table
    """
    global quadric
    table_height = 0.75
    
    # Plate
    glPushMatrix()
    glTranslatef(x, table_height + 0.01, z)
    glColor3d(0.95, 0.95, 0.9)  # White plate
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.12, 24, 24)
    glPopMatrix()
    
    # Food on plate (small colorful items)
    for offset in [(-0.03, -0.02), (0.03, 0.02), (0, -0.03)]:
        glPushMatrix()
        glTranslatef(x + offset[0], table_height + 0.03, z + offset[1])
        glColor3d(0.85, 0.5, 0.2)  # Food color
        glutSolidSphere(0.02, 12, 12)
        glPopMatrix()
    
    # Cup/glass
    glPushMatrix()
    glTranslatef(x + 0.15, table_height + 0.01, z)
    glColor3d(0.85, 0.85, 0.9)  # Glass
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.03, 0.035, 0.1, 16, 16)
    glPopMatrix()

def drawBarStool(x, z):
    """ Draw a bar stool at the service counter
    """
    global quadric
    stool_height = 0.65
    
    # Seat (round)
    glPushMatrix()
    glTranslatef(x, stool_height, z)
    glColor3d(0.5, 0.3, 0.2)  # Brown leather
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.15, 0.15, 0.05, 24, 24)
    glPopMatrix()
    
    # Top cushion
    glPushMatrix()
    glTranslatef(x, stool_height + 0.05, z)
    glColor3d(0.55, 0.35, 0.25)
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.15, 24, 24)
    glPopMatrix()
    
    # Center pole
    glPushMatrix()
    glTranslatef(x, stool_height/2, z)
    glColor3d(0.4, 0.4, 0.42)  # Metal pole
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, 0.03, 0.03, stool_height, 16, 16)
    glPopMatrix()
    
    # Base
    glPushMatrix()
    glTranslatef(x, 0.02, z)
    glColor3d(0.35, 0.35, 0.37)
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, 0.2, 24, 24)
    glPopMatrix()

def drawDecorativeColumn(x, z):
    """ Draw a decorative column/pillar
    """
    global quadric
    column_height = 2.5
    column_radius = 0.25
    
    # Base pedestal
    glPushMatrix()
    glTranslatef(x, 0.1, z)
    glColor3d(0.85, 0.82, 0.78)  # Marble-like color
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, column_radius + 0.05, column_radius, 0.2, 24, 24)
    glPopMatrix()
    
    # Main column shaft
    glPushMatrix()
    glTranslatef(x, column_height/2 + 0.1, z)
    glColor3d(0.90, 0.88, 0.85)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, column_radius, column_radius, column_height - 0.4, 24, 24)
    glPopMatrix()
    
    # Top capital
    glPushMatrix()
    glTranslatef(x, column_height - 0.1, z)
    glColor3d(0.88, 0.85, 0.82)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, column_radius, column_radius + 0.05, 0.2, 24, 24)
    glPopMatrix()
    
    # Top disk
    glPushMatrix()
    glTranslatef(x, column_height + 0.1, z)
    glColor3d(0.85, 0.82, 0.78)
    glRotatef(90, 1, 0, 0)
    gluDisk(quadric, 0, column_radius + 0.05, 24, 24)
    glPopMatrix()

def drawRoomDivider(x, z):
    """ Draw a decorative room divider/partition
    """
    divider_height = 1.5
    divider_width = 0.8
    divider_thickness = 0.08
    
    # Main panel
    glPushMatrix()
    glTranslatef(x, divider_height/2, z)
    glColor3d(0.45, 0.35, 0.25)  # Dark wood
    glScalef(divider_width, divider_height, divider_thickness)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Decorative lattice pattern (cross beams)
    glColor3d(0.55, 0.45, 0.35)  # Lighter wood
    
    # Horizontal beams
    for h in [0.5, 1.0]:
        glPushMatrix()
        glTranslatef(x, h, z)
        glScalef(divider_width + 0.1, 0.05, divider_thickness + 0.02)
        glutSolidCube(1.0)
        glPopMatrix()
    
    # Vertical beam (center)
    glPushMatrix()
    glTranslatef(x, divider_height/2, z)
    glScalef(0.05, divider_height + 0.1, divider_thickness + 0.02)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Base
    glPushMatrix()
    glTranslatef(x, 0.05, z)
    glColor3d(0.4, 0.3, 0.2)
    glScalef(divider_width + 0.2, 0.1, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()

def drawRestaurantObstacles():
    """ Draw all restaurant obstacles, furniture, and people
    """
    # Table 1 with chairs, people, and table settings
    drawTable(-5, -5, 0.5)
    drawChair(-5.7, -5, 90)
    drawPerson(-5.5, -5, 90, (0.8, 0.3, 0.3))  # Person in red shirt
    drawChair(-4.3, -5, -90)
    drawPerson(-4.5, -5, -90, (0.3, 0.5, 0.8))  # Person in blue shirt
    drawChair(-5, -5.7, 0)
    drawPerson(-5, -5.5, 0, (0.2, 0.6, 0.3))  # Person in green shirt
    drawChair(-5, -4.3, 180)
    drawTableSetting(-5, -5)
    
    # Table 2 with chairs and people
    drawTable(4, -6, 0.5)
    drawChair(4.7, -6, 90)
    drawPerson(4.5, -6, 90, (0.6, 0.4, 0.8))  # Person in purple shirt
    drawChair(3.3, -6, -90)
    drawPerson(3.5, -6, -90, (0.9, 0.7, 0.3))  # Person in yellow shirt
    drawChair(4, -6.7, 0)
    drawTableSetting(4, -6)
    
    # Table 3 with chairs and people
    drawTable(-6, 5, 0.45)
    drawChair(-6.6, 5, 90)
    drawPerson(-6.4, 5, 90, (0.4, 0.4, 0.5))  # Person in gray shirt
    drawChair(-5.4, 5, -90)
    drawPerson(-5.6, 5, -90, (0.8, 0.5, 0.3))  # Person in orange shirt
    drawChair(-6, 5.6, 0)
    drawTableSetting(-6, 5)
    
    # Table 4 with people
    drawTable(6, 3, 0.5)
    drawChair(6.7, 3, 90)
    drawPerson(6.5, 3, 90, (0.3, 0.3, 0.7))  # Person in navy shirt
    drawChair(5.3, 3, -90)
    drawTableSetting(6, 3)
    
    # NEW Table 5 - Near entrance
    drawTable(2, 6, 0.5)
    drawChair(2.7, 6, 90)
    drawPerson(2.5, 6, 90, (0.7, 0.4, 0.5))  # Pink shirt
    drawChair(1.3, 6, -90)
    drawPerson(1.5, 6, -90, (0.4, 0.7, 0.6))  # Teal shirt
    drawChair(2, 6.7, 0)
    drawTableSetting(2, 6)
    
    # NEW Table 6 - Corner table
    drawTable(-8, -7, 0.45)
    drawChair(-8.6, -7, 90)
    drawPerson(-8.4, -7, 90, (0.6, 0.3, 0.4))  # Maroon shirt
    drawChair(-7.4, -7, -90)
    drawChair(-8, -7.6, 0)
    drawTableSetting(-8, -7)
    
    # NEW Table 7 - Small table for 2
    drawTable(7, -3, 0.4)
    drawChair(7.5, -3, 90)
    drawPerson(7.3, -3, 90, (0.5, 0.5, 0.3))  # Olive shirt
    drawChair(6.5, -3, -90)
    drawTableSetting(7, -3)
    
    # Plants - more throughout the space (8 total)
    drawPlant(-8, -8)   # Corner 1
    drawPlant(8, -8)    # Corner 2
    drawPlant(-8, 8)    # Corner 3
    drawPlant(7, 7)     # Corner 4
    drawPlant(-10, 0)   # Left wall center
    drawPlant(10, 0)    # Right wall center
    drawPlant(0, 8)     # Back center
    drawPlant(-3, -9)   # Near counter
    
    # Service counter with bar stools
    drawServiceCounter(0, -9)
    drawBarStool(-1, -7.5)
    drawBarStool(0, -7.5)
    drawBarStool(1, -7.5)
    drawPerson(0, -7.5, 180, (0.5, 0.5, 0.6))  # Person at counter
    
    # Wandering people (ANIMATED - moving around the restaurant!)
    global people_positions
    for person in people_positions:
        drawPerson(person['x'], person['z'], person['angle'], person['shirt'])
    
    # Ceiling lights (7 total)
    drawCeilingLight(-5, -5)
    drawCeilingLight(4, -6)
    drawCeilingLight(-6, 5)
    drawCeilingLight(6, 3)
    drawCeilingLight(0, 0)
    drawCeilingLight(2, 6)  # New light
    drawCeilingLight(-8, -7)  # New light
    
    # Windows on walls
    drawWindow(-10, 1.5, -14.9)
    drawWindow(10, 1.5, -14.9)
    
    # Wall decorations  
    drawWallDecor(-7, 1.8, -14.9, 0.5)
    drawWallDecor(0, 2.0, -14.9, 0.7)
    drawWallDecor(7, 1.8, -14.9, 0.5)
    
    # Draw delivered food on tables that have been served
    global restaurant_tables
    for table in restaurant_tables:
        if table['served']:
            drawFoodOnTable(table['x'], table['z'])
    
    # === NEW OBSTACLES FOR AVOIDANCE CHALLENGE ===
    # Decorative columns (elegant pillars)
    drawDecorativeColumn(-2, 0)
    drawDecorativeColumn(2, 0)
    
    # Additional plants for navigation challenge
    drawPlant(0, -3)     # Center obstacle
    drawPlant(-5, 2)     # Left side
    drawPlant(5, -1)     # Right side
    
    # Room dividers (partitions creating paths)
    drawRoomDivider(-3, 3)
    drawRoomDivider(3, 4)

# ========== NEW SERVICE ROBOT FEATURES ==========

def playSound(sound_type):
    """ Play sound effects for robot actions (simulated with console output) """
    global sound_enabled, last_sound_time
    
    if not sound_enabled:
        return
    
    from OpenGL.GLUT import glutGet, GLUT_ELAPSED_TIME
    current_time = glutGet(GLUT_ELAPSED_TIME)
    
    # Debounce sounds (don't play too frequently)
    if (current_time - last_sound_time.get(sound_type, 0)) < 500:
        return
    
    last_sound_time[sound_type] = current_time
    
    # Simulated sound effects (in real implementation, use pygame.mixer or winsound)
    sound_messages = {
        'motor': '🔊 *whirrrr* (motor sound)',
        'stop': '🔊 *beep beep* (stop alert)',
        'delivery': '🔊 *ding!* (delivery complete)',
        'pickup': '🔊 *click!* (food picked up)',
        'turn': '🔊 *servo whine* (turning)'
    }
    
    # Only print occasionally to avoid spam
    if random.random() < 0.1:  # 10% chance to print
        print(f"  {sound_messages.get(sound_type, '🔊 *sound*')}")

def updateRobotFaceEmotion():
    """ Update robot face emotion based on current status """
    global robot_face_emotion, robot_status, speed, avoidance_active
    
    # Determine emotion based on robot state
    if robot_delivery_mode:
        robot_face_emotion = "delivering"
    elif robot_status == "stopped_obstacle":
        robot_face_emotion = "surprised"
    elif abs(speed) > 0.2:
        robot_face_emotion = "happy"
    elif abs(turn) > 0.3:
        robot_face_emotion = "focused"
    else:
        robot_face_emotion = "neutral"

def drawRobotFace(width):
    """ Draw an animated robot face display on the robot body """
    global robot_face_emotion, robot_face_blink_timer, robot_face_blink_state, quadric
    
    # Update blink animation
    robot_face_blink_timer += 1
    if robot_face_blink_timer > 120:  # Blink every ~2 seconds
        robot_face_blink_state = not robot_face_blink_state
        robot_face_blink_timer = 0
    
    # Face display screen (glowing panel on front of robot)
    glPushMatrix()
    glTranslatef(width*4, width*12, 0)
    glColor3d(0.1, 0.15, 0.2)  # Dark screen background
    glScalef(width*6, width*8, width*0.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Display border (glowing effect)
    glPushMatrix()
    glTranslatef(width*4, width*12, width*0.3)
    glColor3d(0.3, 0.6, 1.0)  # Blue glow
    glScalef(width*6.2, width*8.2, width*0.1)
    glutWireCube(1.0)
    glPopMatrix()
    
    # Draw eyes based on emotion
    eye_left_x = width*2
    eye_right_x = width*6
    eye_y = width*14
    eye_size = width*1.2
    
    if robot_face_emotion == "happy":
        # Happy eyes (^_^)
        glColor3d(0.3, 1.0, 0.3)  # Green happy eyes
        # Left eye
        glPushMatrix()
        glTranslatef(eye_left_x, eye_y, width*0.6)
        glutSolidSphere(eye_size, 12, 12)
        glPopMatrix()
        # Right eye
        glPushMatrix()
        glTranslatef(eye_right_x, eye_y, width*0.6)
        glutSolidSphere(eye_size, 12, 12)
        glPopMatrix()
        # Smile
        glLineWidth(3.0)
        glColor3d(0.3, 1.0, 0.3)
        glBegin(GL_LINE_STRIP)
        for i in range(11):
            angle = -pi/4 + (pi/2 * i / 10)
            x = width*4 + cos(angle) * width*2
            y = width*10 + sin(angle) * width*1.5
            glVertex3f(x, y, width*0.6)
        glEnd()
        glLineWidth(1.0)
        
    elif robot_face_emotion == "surprised":
        # Surprised eyes (O_O)
        glColor3d(1.0, 0.5, 0.0)  # Orange surprise
        glPushMatrix()
        glTranslatef(eye_left_x, eye_y, width*0.6)
        glutSolidSphere(eye_size*1.4, 12, 12)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(eye_right_x, eye_y, width*0.6)
        glutSolidSphere(eye_size*1.4, 12, 12)
        glPopMatrix()
        # O mouth
        glPushMatrix()
        glTranslatef(width*4, width*10, width*0.6)
        glColor3d(1.0, 0.5, 0.0)
        glutSolidSphere(width*1.2, 12, 12)
        glPopMatrix()
        
    elif robot_face_emotion == "delivering":
        # Delivering mode (focused eyes with arrow)
        glColor3d(0.3, 0.8, 1.0)  # Cyan focused
        glPushMatrix()
        glTranslatef(eye_left_x, eye_y, width*0.6)
        glutSolidSphere(eye_size, 12, 12)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(eye_right_x, eye_y, width*0.6)
        glutSolidSphere(eye_size, 12, 12)
        glPopMatrix()
        # Arrow pointing forward
        glLineWidth(4.0)
        glColor3d(0.3, 0.8, 1.0)
        glBegin(GL_LINES)
        glVertex3f(width*4, width*10, width*0.6)
        glVertex3f(width*4 + width*2, width*10, width*0.6)
        # Arrow head
        glVertex3f(width*4 + width*2, width*10, width*0.6)
        glVertex3f(width*4 + width*1.5, width*11, width*0.6)
        glVertex3f(width*4 + width*2, width*10, width*0.6)
        glVertex3f(width*4 + width*1.5, width*9, width*0.6)
        glEnd()
        glLineWidth(1.0)
        
    else:  # neutral
        # Neutral eyes (-_-)
        glColor3d(0.6, 0.6, 1.0)  # Blue neutral
        glPushMatrix()
        glTranslatef(eye_left_x, eye_y, width*0.6)
        glutSolidSphere(eye_size*0.8, 12, 12)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(eye_right_x, eye_y, width*0.6)
        glutSolidSphere(eye_size*0.8, 12, 12)
        glPopMatrix()
        # Neutral line mouth
        glLineWidth(2.0)
        glColor3d(0.6, 0.6, 1.0)
        glBegin(GL_LINES)
        glVertex3f(width*2.5, width*10, width*0.6)
        glVertex3f(width*5.5, width*10, width*0.6)
        glEnd()
        glLineWidth(1.0)

def drawRealisticRobotHand(width, side_multiplier):
    """ Draw a realistic human-like robot hand with 5 fingers and natural pose
        width: base scaling factor
        side_multiplier: 1 for right, -1 for left
    """
    global quadric
    
    # Palm base - white/gray metallic
    glPushMatrix()
    glColor3d(0.88, 0.87, 0.85)  # Light gray
    
    # Palm (flat rectangular box shape)
    glPushMatrix()
    glTranslatef(side_multiplier * width*0.8, 0, 0)
    glScalef(1.6, 1.0, 0.6)  # Elongated palm
    glutSolidCube(width*1.3)
    glPopMatrix()
    
    # Define finger positions (spread naturally like human hand)
    finger_positions = [
        {'name': 'thumb', 'x': width*0.3, 'y': width*0.8, 'z': width*0.5, 'angle': 45},
        {'name': 'index', 'x': width*1.8, 'y': width*0.4, 'z': width*0.2, 'angle': 5},
        {'name': 'middle', 'x': width*2.0, 'y': width*0.55, 'z': 0, 'angle': 0},
        {'name': 'ring', 'x': width*1.85, 'y': width*0.4, 'z': -width*0.2, 'angle': -5},
        {'name': 'pinky', 'x': width*1.5, 'y': width*0.3, 'z': -width*0.35, 'angle': -10}
    ]
    
    for finger in finger_positions:
        glPushMatrix()
        glTranslatef(side_multiplier * finger['x'], finger['y'], finger['z'])
        
        # Rotate finger naturally
        if finger['name'] == 'thumb':
            glRotatef(side_multiplier * finger['angle'], 0, 0, 1)
            glRotatef(30, 0, 1, 0)  # Thumb rotates outward
        else:
            glRotatef(side_multiplier * finger['angle'], 0, 0, 1)
        
        # Draw finger segments (3 phalanges)
        for segment in range(3):
            if segment > 0:
                glTranslatef(side_multiplier * width*0.45, 0, 0)
            
            # Joint sphere (knuckle)
            glColor3d(0.82, 0.81, 0.79)  # Slightly darker for joints
            glutSolidSphere(width*0.22, 10, 10)
            
            # Finger segment (cylinder)
            glPushMatrix()
            glTranslatef(side_multiplier * width*0.22, 0, 0)
            
            # Make finger segments slightly smaller and tapered
            segment_length = width*0.42 if segment < 2 else width*0.35
            start_radius = width*0.2 if segment == 0 else width*0.17
            end_radius = width*0.17 if segment < 2 else width*0.13
            
            glColor3d(0.86, 0.85, 0.83)  # Light gray finger
            glRotatef(90, 0, 1, 0)
            gluCylinder(quadric, start_radius, end_radius, segment_length, 8, 8)
            glPopMatrix()
        
        # Fingertip (rounded cap)
        glTranslatef(side_multiplier * width*0.4, 0, 0)
        glColor3d(0.78, 0.77, 0.75)  # Darker tip
        glutSolidSphere(width*0.15, 10, 10)
        
        glPopMatrix()
    
    glPopMatrix()

def drawRobotArm(side, width):
    """ Professional articulated robot arm - ORANGE/YELLOW with perfect proportions!
        side: 'left' or 'right'
        width: base width for scaling
    """
    global robot_arm_left, robot_arm_right, robot_carrying_food, quadric
    
    arm = robot_arm_left if side == 'left' else robot_arm_right
    side_multiplier = -1 if side == 'left' else 1
    
    # Shoulder position (natural humanoid position on body sides)
    shoulder_x = side_multiplier * width*7.5  # Slightly wider for more natural look
    shoulder_y = width*12  # Higher up on the body, like human shoulders
    
    glPushMatrix()
    glTranslatef(shoulder_x, shoulder_y, 0)
    
    # Shoulder ball joint (white/gray)
    glColor3d(0.88, 0.87, 0.85)  # Light gray joint
    glutSolidSphere(width*1.2, 20, 20)
    
    # Rotate for shoulder angle
    glRotatef(arm['shoulder'], 0, 0, 1)
    
    # Shoulder cover (orange housing)
    glPushMatrix()
    glTranslatef(side_multiplier * width*0.8, 0, 0)
    glColor3d(1.0, 0.62, 0.12)  # Vibrant orange
    glutSolidSphere(width*1.4, 18, 18)
    glPopMatrix()
    
    # Upper arm section (BRIGHT ORANGE cylinder)
    glPushMatrix()
    glTranslatef(side_multiplier * width*2, 0, 0)
    glColor3d(0.98, 0.58, 0.08)  # Rich orange
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, width*1.1, width*0.95, width*4, 20, 16)
    glPopMatrix()
    
    # Orange accent band on upper arm
    glPushMatrix()
    glTranslatef(side_multiplier * width*3.5, 0, 0)
    glColor3d(0.92, 0.52, 0.05)  # Darker orange band
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, width*1.15, width*1.15, width*0.4, 20, 16)
    glPopMatrix()
    
    # Elbow joint
    glTranslatef(side_multiplier * width*4, 0, 0)
    glColor3d(0.86, 0.85, 0.83)  # Light gray joint
    glutSolidSphere(width*1.0, 18, 18)
    
    # Rotate for elbow angle
    glRotatef(arm['elbow'], 0, 0, 1)
    
    # Forearm (YELLOW-ORANGE - lighter than upper arm)
    glPushMatrix()
    glTranslatef(side_multiplier * width*1.8, 0, 0)
    glColor3d(1.0, 0.78, 0.22)  # Bright yellow-orange
    glRotatef(90, 0, 1, 0)
    gluCylinder(quadric, width*0.95, width*0.75, width*3.6, 20, 16)
    glPopMatrix()
    
    # Wrist joint
    glTranslatef(side_multiplier * width*3.6, 0, 0)
    glColor3d(0.84, 0.83, 0.81)  # Gray wrist
    glutSolidSphere(width*0.75, 16, 16)
    
    # === NEW: Realistic Human-like Robot Hand with 5 Fingers ===
    glPushMatrix()
    glTranslatef(side_multiplier * width*0.3, 0, 0)
    # Rotate hand to natural forward-facing position
    if side == 'left':
        glRotatef(-10, 0, 0, 1)  # Slight natural bend
    else:
        glRotatef(10, 0, 0, 1)
    drawRealisticRobotHand(width, side_multiplier)
    glPopMatrix()
    
    glPopMatrix()

def animateRobotArms():
    """ Animate robot arms for picking up and delivering food """
    global robot_arm_left, robot_arm_right, robot_arm_animation_timer
    global robot_carrying_food, robot_delivery_mode
    
    robot_arm_animation_timer += 1
    
    if robot_carrying_food:
        # Arms holding tray in front
        target_shoulder_left = -45
        target_shoulder_right = 45
        target_elbow_left = -90
        target_elbow_right = -90
    elif robot_delivery_mode:
        # Arms reaching out to deliver
        target_shoulder_left = -60
        target_shoulder_right = 60
        target_elbow_left = -45
        target_elbow_right = -45
    else:
        # Arms at natural rest position (hanging down like human arms)
        target_shoulder_left = -25  # Arms angled slightly downward and forward
        target_shoulder_right = 25
        target_elbow_left = -15  # Slight bend in elbows for natural look
        target_elbow_right = -15
    
    # Smooth interpolation to target positions
    lerp_speed = 0.1
    robot_arm_left['shoulder'] += (target_shoulder_left - robot_arm_left['shoulder']) * lerp_speed
    robot_arm_right['shoulder'] += (target_shoulder_right - robot_arm_right['shoulder']) * lerp_speed
    robot_arm_left['elbow'] += (target_elbow_left - robot_arm_left['elbow']) * lerp_speed
    robot_arm_right['elbow'] += (target_elbow_right - robot_arm_right['elbow']) * lerp_speed

def updateTimeOfDay():
    """ Update time of day for dynamic lighting """
    global time_of_day, time_speed, auto_time_cycle
    
    if auto_time_cycle:
        time_of_day += time_speed
        if time_of_day >= 24.0:
            time_of_day = 0.0

def getDayNightLightingFactors():
    """ Calculate lighting intensity based on time of day """
    global time_of_day
    
    # Time ranges:
    # 0-6: Night (dark)
    # 6-8: Dawn (transitioning)
    # 8-18: Day (bright)
    # 18-20: Dusk (transitioning)
    # 20-24: Night (dark)
    
    if 6 <= time_of_day < 8:
        # Dawn
        factor = (time_of_day - 6) / 2.0
        return 0.3 + (0.7 * factor), (0.4, 0.5, 0.7), "dawn"
    elif 8 <= time_of_day < 18:
        # Day
        return 1.0, (1.0, 0.95, 0.85), "day"
    elif 18 <= time_of_day < 20:
        # Dusk
        factor = (time_of_day - 18) / 2.0
        return 1.0 - (0.7 * factor), (1.0, 0.6, 0.3), "dusk"
    else:
        # Night
        return 0.3, (0.2, 0.3, 0.5), "night"

def setupLighting():
    """ Function to setup realistic restaurant lighting with dynamic day/night cycle
    """
    global time_of_day
    
    # Get dynamic lighting based on time of day
    intensity, light_color, period = getDayNightLightingFactors()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    glEnable(GL_LIGHT3)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Ambient light (changes with time of day)
    ambient_intensity = 0.3 + (0.2 * intensity)
    ambient = [ambient_intensity * light_color[0], 
               ambient_intensity * light_color[1], 
               ambient_intensity * light_color[2], 1.0]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient)
    
    # Main overhead light (ceiling light - stronger indoors during day)
    light0_position = [0.0, 25.0, 0.0, 1.0]  # Directly above
    light0_diffuse = [intensity * light_color[0], 
                      intensity * light_color[1], 
                      intensity * light_color[2], 1.0]
    light0_specular = [0.8 * intensity, 0.8 * intensity, 0.75 * intensity, 1.0]
    light0_attenuation = 0.01
    glLightfv(GL_LIGHT0, GL_POSITION, light0_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light0_specular)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, light0_attenuation)
    
    # Secondary ceiling light (from front)
    light1_position = [0.0, 20.0, -80.0, 1.0]
    light1_diffuse = [0.8 * intensity * light_color[0], 
                      0.78 * intensity * light_color[1], 
                      0.72 * intensity * light_color[2], 1.0]
    light1_specular = [0.6 * intensity, 0.6 * intensity, 0.6 * intensity, 1.0]
    glLightfv(GL_LIGHT1, GL_POSITION, light1_position)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diffuse)
    glLightfv(GL_LIGHT1, GL_SPECULAR, light1_specular)
    
    # Window light from left (natural light - strong during day)
    light2_position = [-100.0, 15.0, 0.0, 1.0]
    if period == "night":
        # Dim window light at night
        light2_diffuse = [0.2, 0.25, 0.35, 1.0]
    else:
        # Natural daylight through windows
        light2_diffuse = [0.6 * intensity * light_color[0], 
                          0.65 * intensity * light_color[1], 
                          0.75 * intensity * light_color[2], 1.0]
    light2_specular = [0.3 * intensity, 0.3 * intensity, 0.35 * intensity, 1.0]
    glLightfv(GL_LIGHT2, GL_POSITION, light2_position)
    glLightfv(GL_LIGHT2, GL_DIFFUSE, light2_diffuse)
    glLightfv(GL_LIGHT2, GL_SPECULAR, light2_specular)
    
    # Window light from right
    light3_position = [100.0, 15.0, 0.0, 1.0]
    if period == "night":
        light3_diffuse = [0.2, 0.25, 0.35, 1.0]
    else:
        light3_diffuse = [0.6 * intensity * light_color[0], 
                          0.65 * intensity * light_color[1], 
                          0.75 * intensity * light_color[2], 1.0]
    glLightfv(GL_LIGHT3, GL_POSITION, light3_position)
    glLightfv(GL_LIGHT3, GL_DIFFUSE, light3_diffuse)
    
    # Material properties for shiny surfaces (enhanced for realism)
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [80.0]  # Shinier surfaces
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

def drawGround():
    """ Function to draw a realistic ground with concrete texture and grid lines
    """
    nb_rows = 30
    nb_cols = 30
    
    # Draw main floor (concrete color)
    for r in range(0, nb_rows):
        for c in range(0, nb_cols):
            # Concrete gray with slight variation
            base_color = 0.45
            variation = 0.03 if (r + c) % 3 == 0 else 0.0
            gray = base_color + variation
            glColor3d(gray, gray, gray + 0.02)  # Slightly bluish concrete
            
            glBegin(GL_QUADS)
            glVertex3f(c - nb_cols/2, 0, r - nb_rows/2)
            glVertex3f(c - nb_cols/2 + 1, 0, r - nb_rows/2)
            glVertex3f(c - nb_cols/2 + 1, 0, r - nb_rows/2 + 1)
            glVertex3f(c - nb_cols/2, 0, r - nb_rows/2 + 1)
            glEnd()
    
    # Draw grid lines on floor
    glLineWidth(2.0)
    glColor3d(0.35, 0.35, 0.38)  # Darker lines
    
    # Horizontal lines
    for r in range(0, nb_rows + 1, 2):
        glBegin(GL_LINES)
        glVertex3f(-nb_cols/2, 0.01, r - nb_rows/2)
        glVertex3f(nb_cols/2, 0.01, r - nb_rows/2)
        glEnd()
    
    # Vertical lines
    for c in range(0, nb_cols + 1, 2):
        glBegin(GL_LINES)
        glVertex3f(c - nb_cols/2, 0.01, -nb_rows/2)
        glVertex3f(c - nb_cols/2, 0.01, nb_rows/2)
        glEnd()
    
    glLineWidth(1.0)

def drawIBot(ibot):
    """ Function to draw the robot
        ibot: the robot (IBalancingBot) to draw
    """
    global myBot
    drawWheels(ibot.d_dstw, ibot.d_widthw, ibot.d_rw)  # draw the wheels
    drawBase(ibot.d_dstw, ibot.d_widthp)  # draw the robot body
    drawPendulum(ibot.d_heightp, ibot.d_widthp, ibot.d_centerp)  # draw the pendulum

def drawWheels(dst_wheels, width_wheel, radius_wheel):
    """ Function to draw the robot's wheels
        dst_wheels : distances between the two wheels
        width_wheel : width of the wheels
        radius_wheel : radius of the wheels
    """
    global quadric  # to use gluCylinder to draw cylinder
    # draw the first wheel
    glPushMatrix()
    glTranslatef(0, 0, -dst_wheels/2)
    drawWheel(radius_wheel/2, width_wheel) 
    glPopMatrix()
    # draw the second wheel
    glPushMatrix()
    glTranslatef(0, 0, dst_wheels/2)
    drawWheel(radius_wheel/2, width_wheel)
    glPopMatrix()


def drawWheel(size, width):
    """ Function to draw a realistic wheel with tire and rim
        size : size of the wheel (radius)
        width : width of the wheel (width of the cylinder)
    """
    global quadric
    # Make wheels thicker and more substantial
    wheel_width = width * 3.0  # Thicker wheels
    
    # draw the tire (black rubber)
    glPushMatrix()
    glColor3d(0.1, 0.1, 0.1)  # Dark tire color
    glTranslatef(0, 0, -wheel_width/2)
    gluCylinder(quadric, size, size, wheel_width, 32, 16)
    glPopMatrix()
    
    # draw the first rim (metallic)
    glPushMatrix()
    glColor3d(0.3, 0.3, 0.35)  # Metallic gray
    glTranslatef(0, 0, -wheel_width/2)
    gluDisk(quadric, 0, size*0.7, 32, 32)
    glPopMatrix()
    
    # draw the second rim
    glPushMatrix()
    glColor3d(0.3, 0.3, 0.35)
    glTranslatef(0, 0, wheel_width/2)
    gluDisk(quadric, 0, size*0.7, 32, 32)
    glPopMatrix()
    
    # draw tire treads (outer rings)
    glPushMatrix()
    glColor3d(0.05, 0.05, 0.05)  # Very dark for treads
    glTranslatef(0, 0, -wheel_width/2 + wheel_width*0.25)
    gluDisk(quadric, size*0.95, size, 32, 32)
    glPopMatrix()
    
    glPushMatrix()
    glColor3d(0.05, 0.05, 0.05)
    glTranslatef(0, 0, wheel_width/2 - wheel_width*0.25)
    gluDisk(quadric, size*0.95, size, 32, 32)
    glPopMatrix()

def drawBase(dst_wheels, radius_pipe):
    """ Function to draw a robust chassis base connecting the wheels
        dst_wheels : distance between the wheels
        radius_pipe : the width of the cylinder body
    """
    global quadric
    
    # Main axle (thicker cylinder connecting wheels)
    glPushMatrix()
    glColor3d(0.2, 0.2, 0.22)  # Dark metallic
    glTranslatef(0, 0, -dst_wheels/2)
    gluCylinder(quadric, radius_pipe*3, radius_pipe*3, dst_wheels, 32, 16)
    glPopMatrix()
    
    # Central motor housing (box at center)
    glPushMatrix()
    glColor3d(0.15, 0.15, 0.18)  # Darker gray
    glTranslatef(0, radius_pipe*2, 0)
    glScalef(radius_pipe*8, radius_pipe*6, dst_wheels*0.5)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Lower mounting plate
    glPushMatrix()
    glColor3d(0.25, 0.25, 0.28)  # Light metallic gray
    glTranslatef(0, radius_pipe*5, 0)
    glScalef(radius_pipe*10, radius_pipe*1.5, dst_wheels*0.7)
    glutSolidCube(1.0)
    glPopMatrix()

def drawPendulum(height_pendulum, radius_pipe, center_pendulum):
    """ PROFESSIONAL SERVICE ROBOT - Compact, well-proportioned design!
        height_pendulum : height of the pendulum from the center of the wheels
        radius_pipe : the width of the pendulum cylinder
        center_pendulum :  height of the center of mass of the pendulum from the center of the wheels
    """
    global quadric
    
    # ========== PERFECT PROFESSIONAL ROBOT BODY ==========
    
    # Base connection (dark gray support)
    glPushMatrix()
    glColor3d(0.25, 0.25, 0.28)
    glTranslatef(0, height_pendulum*0.05, 0)
    glScalef(radius_pipe*6, radius_pipe*1.5, radius_pipe*6)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Lower body platform (smooth white base)
    glPushMatrix()
    glColor3d(0.95, 0.94, 0.92)  # Cream white
    glTranslatef(0, height_pendulum*0.15, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, radius_pipe*7, radius_pipe*8, height_pendulum*0.12, 32, 16)
    glPopMatrix()
    
    # Main torso body (compact rounded cylinder)
    glPushMatrix()
    glColor3d(0.98, 0.97, 0.95)  # Pure white
    glTranslatef(0, height_pendulum*0.35, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, radius_pipe*7.5, radius_pipe*6.5, height_pendulum*0.25, 32, 16)
    glPopMatrix()
    
    # Upper torso (slightly wider round section)
    glPushMatrix()
    glColor3d(0.96, 0.95, 0.93)  # Off-white
    glTranslatef(0, height_pendulum*0.52, 0)
    glScalef(radius_pipe*6.5, radius_pipe*2.5, radius_pipe*6.5)
    glutSolidSphere(1.0, 24, 24)
    glPopMatrix()
    
    # Chest panel (light blue accent - prominent)
    glPushMatrix()
    glColor3d(0.82, 0.86, 0.91)  # Soft blue-gray
    glTranslatef(0, height_pendulum*0.38, radius_pipe*6.8)
    glScalef(radius_pipe*5, height_pendulum*0.22, radius_pipe*0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Neck (slim connection to head)
    glPushMatrix()
    glColor3d(0.93, 0.92, 0.90)  # Slightly darker white
    glTranslatef(0, height_pendulum*0.62, 0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quadric, radius_pipe*3, radius_pipe*3.5, height_pendulum*0.08, 20, 16)
    glPopMatrix()
    
    # Head section (compact rounded top with face display)
    glPushMatrix()
    glColor3d(0.98, 0.97, 0.95)  # Pure white head
    glTranslatef(0, height_pendulum*0.73, 0)
    glScalef(radius_pipe*5.5, radius_pipe*3.8, radius_pipe*5)
    glutSolidSphere(1.0, 28, 28)  # High quality sphere
    glPopMatrix()
    
    # Head top cap (rounded dome)
    glPushMatrix()
    glColor3d(0.94, 0.93, 0.91)  # Slightly darker cap
    glTranslatef(0, height_pendulum*0.82, 0)
    glScalef(radius_pipe*4.5, radius_pipe*2, radius_pipe*4.5)
    glutSolidSphere(1.0, 24, 24)
    glPopMatrix()
    
    # Shoulder mounting points (smooth rounded joints)
    for side in [-1, 1]:
        glPushMatrix()
        glColor3d(0.92, 0.91, 0.89)  # Joint color
        glTranslatef(side * radius_pipe*7, height_pendulum*0.5, 0)
        glutSolidSphere(radius_pipe*1.8, 20, 20)
        glPopMatrix()
    
    # Status LED strip (vertical indicators on chest)
    led_data = [
        (height_pendulum*0.43, (0.2, 0.85, 0.3)),   # Green
        (height_pendulum*0.38, (0.3, 0.65, 0.95)),  # Blue  
        (height_pendulum*0.33, (0.95, 0.75, 0.2))   # Amber
    ]
    
    for led_y, led_color in led_data:
        glPushMatrix()
        glColor3d(*led_color)
        glTranslatef(0, led_y, radius_pipe*7.3)
        glutSolidSphere(radius_pipe*0.5, 12, 12)
        glPopMatrix()
    
    # Center of mass indicator (internal)
    glPushMatrix()
    glColor3d(0.85, 0.25, 0.25)  # Red marker
    glTranslatef(0, center_pendulum, 0)
    glutSolidSphere(radius_pipe*0.6, 12, 12)
    glPopMatrix()
    
    # ========== Robot Face Display (prominent on front of head) ==========
    drawRobotFace(radius_pipe)
    
    # ========== Robot Arms (Orange/Yellow - better positioned) ==========
    drawRobotArm('left', radius_pipe)
    drawRobotArm('right', radius_pipe)

def drawHUD():
    """ Draw on-screen HUD with robot status information """
    global robot_deliveries_completed, robot_distance_traveled
    global robot_status, robot_face_emotion, time_of_day, myBot, speed, turn
    
    # Switch to 2D orthographic projection for HUD
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)  # 2D coordinate system
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Speed indicator (bar graph)
    speed_magnitude = abs(speed) * 100
    speed_color = (0.3, 0.8, 1.0) if speed < 0 else (1.0, 0.5, 0.2)
    glColor3d(*speed_color)
    glBegin(GL_QUADS)
    glVertex2f(20, 560)
    glVertex2f(20 + speed_magnitude, 560)
    glVertex2f(20 + speed_magnitude, 580)
    glVertex2f(20, 580)
    glEnd()
    
    # Speed border
    glColor3d(0.8, 0.8, 0.8)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(20, 560)
    glVertex2f(120, 560)
    glVertex2f(120, 580)
    glVertex2f(20, 580)
    glEnd()
    glLineWidth(1.0)
    
    # Time of day indicator (sun/moon icon)
    _, _, period = getDayNightLightingFactors()
    time_color = (1.0, 0.9, 0.3) if period in ['day', 'dawn', 'dusk'] else (0.7, 0.7, 0.9)
    glColor3d(*time_color)
    # Simple circle for sun/moon
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(750, 570)
    for i in range(21):
        angle = 2 * pi * i / 20
        glVertex2f(750 + 15 * cos(angle), 570 + 15 * sin(angle))
    glEnd()
    
    # Robot emotion indicator (small colored square)
    emotion_colors = {
        'happy': (0.3, 1.0, 0.3),
        'surprised': (1.0, 0.5, 0.0),
        'delivering': (0.3, 0.8, 1.0),
        'neutral': (0.6, 0.6, 1.0),
        'focused': (0.8, 0.3, 1.0)
    }
    emotion_color = emotion_colors.get(robot_face_emotion, (0.8, 0.8, 0.8))
    glColor3d(*emotion_color)
    glBegin(GL_QUADS)
    glVertex2f(720, 560)
    glVertex2f(735, 560)
    glVertex2f(735, 575)
    glVertex2f(720, 575)
    glEnd()
    
    # Statistics (distance, deliviries) - draw simple colored bars
    # Distance indicator
    glColor3d(0.5, 0.9, 0.5)
    distance_display = min(robot_distance_traveled / 10.0, 150)  # Scale
    glBegin(GL_QUADS)
    glVertex2f(20, 500)
    glVertex2f(20 + distance_display, 500)
    glVertex2f(20 + distance_display, 515)
    glVertex2f(20, 515)
    glEnd()
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    
    # Restore projection
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()


def Displayfct():
    """ Function to draw the world
    """

    scaleCoeff = 10  # to scale the robot display

    glClearColor(0.5, 0.7, 0.9, 1.0)  # Sky blue background
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Projection
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glFrustum(-1,1,-1,1,1,80.)

    # Camera position and orientation
    global CameraPosX, CameraPosY, CameraPosZ, CenterX, CenterY, CenterZ, ViewUpX, ViewUpY, ViewUpZ
    global myBot, posx, posz, follow_robot

    if(follow_robot):
        # Update both camera position AND center for smooth cinematic tracking
        CenterX = -posx*scaleCoeff
        CenterZ = -posz*scaleCoeff
        CameraPosX = -posx*scaleCoeff  # Camera follows robot's X position
        CameraPosZ = -posz*scaleCoeff + 10.0  # Camera stays 10 units behind robot

    gluLookAt(CameraPosX, CameraPosY , CameraPosZ, CenterX, CenterY, CenterZ, ViewUpX, ViewUpY, ViewUpZ)

    # Draw the objects and geometrical transformations
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Setup realistic lighting
    setupLighting()

    # Draw sky gradient background
    drawSky()
    
    # Draw walls
    glPushMatrix()
    glScalef(scaleCoeff, scaleCoeff, scaleCoeff)
    drawWalls()
    glPopMatrix()

    # draw the ground
    glPushMatrix()
    glScalef(scaleCoeff, scaleCoeff, scaleCoeff)  # to scale the ground as the robot
    glTranslatef(0,-myBot.d_rw/2,0)
    drawGround()
    glPopMatrix()
    
    # Draw restaurant obstacles and furniture
    glPushMatrix()
    glScalef(scaleCoeff, scaleCoeff, scaleCoeff)
    glTranslatef(0, -myBot.d_rw/2, 0)
    drawRestaurantObstacles()
    glPopMatrix()

    # draw the robot
    glPushMatrix()
    glScalef(scaleCoeff, scaleCoeff, scaleCoeff)  # to scale the robot
    glTranslatef(-posx,0,-posz)
    glRotatef(myBot.psi*180/pi, 0, 1, 0)  # psi rotation (robot)
    glRotatef(myBot.phi*180/pi, 0, 0, 1)  # phi rotation (pendulum)
    drawIBot(myBot)
    # Draw food tray on robot
    drawFoodTray()
    glPopMatrix()

    # ========== NEW: Draw HUD overlay ==========
    drawHUD()

    # To efficient display
    glutSwapBuffers()


def ReshapeFunc(w,h):
    """ Function calls when reshaping the window
    """
    glViewport(0,0,w,h)

def rotate_camera(angle):
    """ Function to rotate the camera according to an angle
        angle : step angle for the camera rotation
    """
    global CameraPosX,CameraPosZ,Radius,Theta
    Theta+=angle
    CameraPosZ=Radius*cos(Theta)
    CameraPosX=Radius*sin(Theta)
    return 0

def zoom_camera(factor):
    """ Function to zoom the camera according to a factor
        factor : zoom factor
    """
    global CameraPosX,CameraPosY,CameraPosZ,Radius
    # Update camera center
    CameraPosX, CameraPosY, CameraPosZ = factor*CameraPosX, factor*CameraPosY, factor*CameraPosZ
    # Update radius (for next rotations)
    Radius = sqrt( CameraPosX**2 + CameraPosZ**2 )

def KeyboardFunc(key, x, y):
    """ Function to handle regular keyboard keys (alternative controls)
    """
    global CameraPosY, Theta, dtheta
    global myBot, speed, use_pid, turn
    global posx, posz, follow_robot, avoidance_active
    
    if key == b's' or key == b'S':
        print("\tSimulation ON")
        glutIdleFunc(animation)
    elif key == b'p' or key == b'P':
        print("\tSimulation PAUSE")
        glutIdleFunc(None)
    elif key == b'w' or key == b'W':
        speed = -0.35  # Negative = forward
        turn = 0  # Make sure we're not turning
        print("\t>>> FORWARD (Fast)")
    elif key == b'x' or key == b'X':
        speed = 0.35  # Positive = backward
        turn = 0  # Make sure we're not turning
        print("\t>>> BACKWARD (Fast)")
    elif key == b'a' or key == b'A':
        turn = 0.5  # Turn left
        print("\t>>> TURNING LEFT")
    elif key == b'd' or key == b'D':
        turn = -0.5  # Turn right
        print("\t>>> TURNING RIGHT")
    elif key == b'q' or key == b'Q' or key == b' ':
        speed = 0
        turn = 0
        print("\tStopped")
    elif key == b'c' or key == b'C':
        use_pid = not(use_pid)
        print("\tUsing PID : " + str(use_pid))
        if(use_pid == True):
            initPIDs()
    elif key == b'o' or key == b'O':
        avoidance_active = not(avoidance_active)
        print("\tObstacle Detection (Auto-Stop) : " + str(avoidance_active))
    elif key == b'r' or key == b'R':
        posx = posz = 0
        myBot.initRobot()
        initPIDs()
        print("\tReset simulation")
    elif key == b'f' or key == b'F':
        follow_robot = not(follow_robot)
        print("\tFollowing robot : " + str(follow_robot))
    elif key == b't' or key == b'T':
        # Toggle time cycle
        global auto_time_cycle
        auto_time_cycle = not auto_time_cycle
        print(f"\tAutomatic Day/Night Cycle: {auto_time_cycle}")
    elif key == b'b' or key == b'B':
        # Toggle sound effects
        global sound_enabled
        sound_enabled = not sound_enabled
        print(f"\tSound Effects: {sound_enabled}")
    elif key == b'm' or key == b'M':
        # Toggle delivery mode (arms extend)
        global robot_delivery_mode, robot_carrying_food
        robot_delivery_mode = not robot_delivery_mode
        if robot_delivery_mode:
            robot_carrying_food = True
            playSound('pickup')
            print("\t📦 Delivery Mode ACTIVATED! Robot picking up food...")
        else:
            robot_carrying_food = False
            playSound('delivery')
            print("\t✅ Delivery Mode OFF. Food delivered!")
    elif key == b'n' or key == b'N':
        # Cycle through times of day manually
        global time_of_day
        time_of_day = (time_of_day + 3) % 24
        _, _, period = getDayNightLightingFactors()
        print(f"\t🕐 Time: {int(time_of_day):02d}:00 ({period})")
    elif key == b'h' or key == b'H':
        print("\n╔════════════ KEYBOARD CONTROLS ════════════╗")
        print("║ MOVEMENT                                  ║")
        print("║   W : Move forward        X : Move back   ║")
        print("║   A : Turn left           D : Turn right  ║")
        print("║   Q/Space : Stop motion                   ║")
        print("║                                           ║")
        print("║ ROBOT FEATURES                            ║")
        print("║   M : Toggle Delivery Mode (Arms/Food)    ║")
        print("║   B : Toggle Sound Effects                ║")
        print("║   T : Toggle Day/Night Auto-Cycle         ║")
        print("║   N : Change Time of Day (manual)         ║")
        print("║                                           ║")
        print("║ SIMULATION                                ║")
        print("║   C : Toggle PID control                  ║")
        print("║   O : Toggle Obstacle Detection           ║")
        print("║   F : Toggle Camera Follow                ║")
        print("║   R : Reset simulation                    ║")
        print("║   S : Start | P : Pause                   ║")
        print("║   H : Show this help                      ║")
        print("║   ESC : Exit                              ║")
        print("╚═══════════════════════════════════════════╝\n")
    elif key == b'\x1b':  # ESC key
        print("\tExiting...")
        sys.exit(0)
    
    glutPostRedisplay()
    return 0

def SpecialFunc(skey,x,y):
    """ Function to handle the keybord keys
    """
    global CameraPosY, Theta, dtheta
    global myBot, speed, use_pid, turn
    global posx, posz, follow_robot

    if glutGetModifiers() == GLUT_ACTIVE_SHIFT:
        # SHIFT pressed
        if skey == GLUT_KEY_UP :
            CameraPosY+=0.3  # put the camera higher
        if skey == GLUT_KEY_DOWN :
            CameraPosY-=0.3  # put the camera lower
    else:
        # standard
        if skey == GLUT_KEY_LEFT :
            rotate_camera(-dtheta)
        elif skey == GLUT_KEY_RIGHT :
            rotate_camera(dtheta)
        elif skey == GLUT_KEY_UP :
            zoom_camera(0.9)
        elif skey == GLUT_KEY_DOWN :
            zoom_camera(1.1)
        elif skey == GLUT_KEY_PAGE_DOWN : 
            print("\tSimulation ON")
            glutIdleFunc(animation)
        elif skey == GLUT_KEY_PAGE_UP :
            print("\tSimulation PAUSE")
            glutIdleFunc(None)
        elif skey == GLUT_KEY_F1 :
            speed = 0.35  # Faster speed
        elif skey == GLUT_KEY_F2 :
            speed = -0.35  # Faster speed
        elif skey == GLUT_KEY_F3 : 
            turn = 0.5  # Faster turn
        elif skey == GLUT_KEY_F4 : 
            speed = 0
            turn = 0
        elif skey == GLUT_KEY_F5 : 
            use_pid = not(use_pid)
            print("\tUsing PID : " + str(use_pid))
            if(use_pid == True):
                initPIDs()
        elif skey == GLUT_KEY_F6 : 
            posx = posz = 0
            myBot.initRobot()
            initPIDs()
        elif skey == GLUT_KEY_F7 : 
            myBot.phi += (10*pi/180)
        elif skey == GLUT_KEY_F8 : 
            myBot.phi += (-20*pi/180)
        elif skey == GLUT_KEY_F9 : 
            follow_robot = not(follow_robot)
            print("\tFollowing robot : " + str(follow_robot))
    glutPostRedisplay()
    return 0

# Initialization of the Window stuff
glutInit(sys.argv)
glutInitWindowPosition(50, 50)
glutInitWindowSize(1280, 720)  # HD resolution for 8GB graphics
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | GLUT_MULTISAMPLE)  # Add antialiasing
glutCreateWindow(b"Hotel Restaurant - Food Service Robot Simulator [HD]")

# Opengl Initialization for high-quality rendering
glClearColor(0.5, 0.7, 0.9, 1.0)  # Sky blue background
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
glEnable(GL_DEPTH_TEST)  # Hidden objects are not drawn
glEnable(GL_BLEND)  # Enable transparency
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Standard blending
glShadeModel(GL_SMOOTH)  # Smooth shading for better appearance
glEnable(GL_NORMALIZE)  # Normalize vectors for lighting
glEnable(GL_MULTISAMPLE)  # Enable antialiasing for smooth edges
glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)  # Best quality perspective
glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)  # Smooth polygons
glEnable(GL_LINE_SMOOTH)  # Smooth lines
glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

# Display are reshape function
glutDisplayFunc(Displayfct)
glutReshapeFunc(ReshapeFunc)
glutSpecialFunc(SpecialFunc)
glutKeyboardFunc(KeyboardFunc)  # Add regular keyboard handler

# Initialize PIDs and start simulation automatically
print("\n=== INITIALIZING ===")
initPIDs()
print("  PID controllers initialized")
print("  Starting simulation automatically...")
print("  Press 'H' for keyboard controls help\n")
glutIdleFunc(animation)  # Start animation automatically

# Infinite loop
glutMainLoop()
