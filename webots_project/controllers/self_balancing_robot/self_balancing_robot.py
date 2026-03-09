"""
Self-Balancing Restaurant Service Robot Controller
Webots Python Controller with PID balancing and food delivery

Features:
- Two-wheeled self-balancing robot with PID control
- Automatic food pickup and delivery to tables
- Restaurant boundary detection and enforcement
- Smart collision avoidance with distance sensors
- Emergency stop for critical obstacles
- Intelligent path planning around obstacles
"""

from controller import Robot, Motor, PositionSensor, InertialUnit, GPS, DistanceSensor
import math

# PID Controller Class
class PID:
    def __init__(self, kp=0, ki=0, kd=0):
        self.kp = kp
        self.ki = kd
        self.kd = kd
        self.previous_error = 0
        self.integral = 0
        
    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.previous_error = error
        return output


class ServiceRobotController:
    def __init__(self):
        # Initialize the Robot instance
        self.robot = Robot()
        self.timestep = int(self.robot.getBasicTimeStep())
        
        # Motors
        self.left_motor = self.robot.getDevice('left_wheel_motor')
        self.right_motor = self.robot.getDevice('right_wheel_motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)
        
        # Arm motors
        self.left_shoulder = self.robot.getDevice('left_shoulder_motor')
        self.right_shoulder = self.robot.getDevice('right_shoulder_motor')
        self.left_elbow = self.robot.getDevice('left_elbow_motor')
        self.right_elbow = self.robot.getDevice('right_elbow_motor')
        
        # Set initial arm positions (natural resting pose)
        self.left_shoulder.setPosition(-0.4)  # Arms hanging down naturally
        self.right_shoulder.setPosition(0.4)
        self.left_elbow.setPosition(-0.3)
        self.right_elbow.setPosition(-0.3)
        
        # Sensors
        self.imu = self.robot.getDevice('imu')
        self.imu.enable(self.timestep)
        
        self.gps = self.robot.getDevice('gps')
        self.gps.enable(self.timestep)
        
        self.distance_front = self.robot.getDevice('distance_front')
        self.distance_left = self.robot.getDevice('distance_left')
        self.distance_right = self.robot.getDevice('distance_right')
        self.distance_front.enable(self.timestep)
        self.distance_left.enable(self.timestep)
        self.distance_right.enable(self.timestep)
        
        # Wheel encoders
        self.left_sensor = self.robot.getDevice('left_wheel_sensor')
        self.right_sensor = self.robot.getDevice('right_wheel_sensor')
        self.left_sensor.enable(self.timestep)
        self.right_sensor.enable(self.timestep)
        
        # PID Controllers
        self.balance_pid = PID(kp=25.0, ki=0.5, kd=15.0)  # For tilt angle
        self.speed_pid = PID(kp=0.5, ki=0.01, kd=0.1)     # For forward/backward
        self.turn_pid = PID(kp=2.0, ki=0.0, kd=0.5)       # For turning
        
        # Robot state
        self.target_speed = 0.0
        self.target_turn = 0.0
        self.carrying_food = False
        self.delivery_mode = False
        self.target_table = None
        
        # Table positions (from world file)
        self.tables = [
            {'name': 'Table 1', 'pos': (-3, 3), 'has_food': False},
            {'name': 'Table 2', 'pos': (3, 3), 'has_food': False},
            {'name': 'Table 3', 'pos': (-3, -3), 'has_food': False},
            {'name': 'Table 4', 'pos': (3, -3), 'has_food': False},
            {'name': 'Table 5', 'pos': (-4.5, 0), 'has_food': False},
            {'name': 'Table 6', 'pos': (4.5, 0), 'has_food': False},
        ]
        
        self.service_counter_pos = (0, -6.5)
        self.food_on_robot = 0
        self.deliveries_made = 0
        
        # Restaurant boundaries (keep robot inside) - Based on 25x20 arena
        self.boundary_limits = {
            'x_min': -10.0,
            'x_max': 10.0,
            'y_min': -8.0,
            'y_max': 8.0
        }
        
        # Collision avoidance parameters
        self.obstacle_threshold = 1.2  # meters - trigger avoidance
        self.critical_threshold = 0.6  # meters - emergency stop
        self.avoidance_active = False
        self.avoidance_counter = 0
        self.boundary_violation_counter = 0
        self.last_safe_position = (0, 0)
        self.returning_to_center = False
        
        print("╔════════════════════════════════════════════════════════╗")
        print("║  WEBOTS RESTAURANT SERVICE ROBOT - INITIALIZED!       ║")
        print("║  🤖 Self-Balancing Two-Wheeled Robot                   ║")
        print("║  🦾 Articulated Arms with Human-like Hands            ║")
        print("║  🍽️  Automatic Food Delivery System                    ║")
        print("║  🛡️  Boundary Detection & Collision Avoidance         ║")
        print("╚════════════════════════════════════════════════════════╝\n")
        print("SAFETY FEATURES:")
        print("  ✓ Restaurant boundary detection (stays inside)")
        print(f"  ✓ Obstacle avoidance threshold: {self.obstacle_threshold}m")
        print(f"  ✓ Emergency stop threshold: {self.critical_threshold}m")
        print(f"  ✓ Boundaries: X[{self.boundary_limits['x_min']}, {self.boundary_limits['x_max']}] Y[{self.boundary_limits['y_min']}, {self.boundary_limits['y_max']}]")
        print("\nCONTROLS:")
        print("  Robot will automatically navigate and deliver food!")
        print("  - Balancing using IMU + PID control")
        print("  - Smart obstacle avoidance with distance sensors")
        print("  - Automatic table detection and food delivery\n")
        
    def get_tilt_angle(self):
        """Get tilt angle from IMU"""
        roll_pitch_yaw = self.imu.getRollPitchYaw()
        return roll_pitch_yaw[1]  # Pitch angle (forward/backward tilt)
    
    def get_position(self):
        """Get robot position from GPS"""
        pos = self.gps.getValues()
        return (pos[0], pos[1])
    
    def get_yaw(self):
        """Get robot heading from IMU"""
        roll_pitch_yaw = self.imu.getRollPitchYaw()
        return roll_pitch_yaw[2]  # Yaw angle (heading)
    
    def check_obstacles(self):
        """Check distance sensors for obstacles - RAW DEBUG VERSION"""
        front_dist = self.distance_front.getValue()
        left_dist = self.distance_left.getValue()
        right_dist = self.distance_right.getValue()
        
        # Sensors return 0-3000 (0-3 meters mapped)
        # Convert: value / 1000 = meters
        front = front_dist / 1000.0
        left = left_dist / 1000.0
        right = right_dist / 1000.0
        
        # Clamp to max range
        front = min(front, 3.0)
        left = min(left, 3.0)
        right = min(right, 3.0)
        
        # Print raw values for debugging
        print(f"🔍 RAW SENSORS: Front={front_dist:.0f}→{front:.2f}m | Left={left_dist:.0f}→{left:.2f}m | Right={right_dist:.0f}→{right:.2f}m")
        
        return {'front': front, 'left': left, 'right': right}
    
    def check_boundaries(self):
        """Check if robot is near or outside boundaries - AGGRESSIVE VERSION"""
        pos = self.get_position()
        x, y = pos[0], pos[1]
        
        # Print position every time for debugging
        print(f"📍 POSITION: X={x:.2f} Y={y:.2f} | Limits: X[{self.boundary_limits['x_min']},{self.boundary_limits['x_max']}] Y[{self.boundary_limits['y_min']},{self.boundary_limits['y_max']}]")
        
        # Define safe zone (well inside boundaries)
        safe_zone = {
            'x_min': self.boundary_limits['x_min'] + 3.0,
            'x_max': self.boundary_limits['x_max'] - 3.0,
            'y_min': self.boundary_limits['y_min'] + 3.0,
            'y_max': self.boundary_limits['y_max'] - 3.0
        }
        
        # Check if outside safe zone
        outside_safe = (x < safe_zone['x_min'] or x > safe_zone['x_max'] or
                       y < safe_zone['y_min'] or y > safe_zone['y_max'])
        
        # Check if outside actual boundaries
        outside_boundary = (x < self.boundary_limits['x_min'] or x > self.boundary_limits['x_max'] or
                          y < self.boundary_limits['y_min'] or y > self.boundary_limits['y_max'])
        
        if outside_boundary:
            print(f"🚨🚨🚨 OUTSIDE BOUNDARY! EMERGENCY STOP! 🚨🚨🚨")
            return {'stop_now': True, 'outside_safe': True}
        
        if outside_safe:
            print(f"⚠️⚠️ OUTSIDE SAFE ZONE! STOPPING! ⚠️⚠️")
            return {'stop_now': True, 'outside_safe': True}
        
        print(f"✅ Inside safe zone")
        return {'stop_now': False, 'outside_safe': False}
    
    def collision_avoidance_behavior(self, obstacles):
        """Smart collision avoidance - steer around obstacles"""
        front = obstacles['front']
        left = obstacles['left']
        right = obstacles['right']
        
        # Critical obstacle - emergency stop
        if front < self.critical_threshold:
            print(f"🚨 EMERGENCY STOP! Front obstacle at {front:.2f}m (threshold: {self.critical_threshold}m)")
            return {'action': 'STOP', 'turn': 0, 'speed': 0}
        
        # Obstacle detected - intelligent avoidance
        if front < self.obstacle_threshold:
            self.avoidance_active = True
            self.avoidance_counter = 50
            
            # Decide which way to turn
            if left > right + 0.2:
                print(f"🔄 AVOIDING - Turn LEFT | Front:{front:.2f}m L:{left:.2f}m R:{right:.2f}m")
                return {'action': 'AVOID_LEFT', 'turn': 1.2, 'speed': -0.2}
            else:
                print(f"🔄 AVOIDING - Turn RIGHT | Front:{front:.2f}m L:{left:.2f}m R:{right:.2f}m")
                return {'action': 'AVOID_RIGHT', 'turn': -1.2, 'speed': -0.2}
        
        # Side obstacles
        if left < 0.7:
            print(f"↗️ LEFT obstacle {left:.2f}m - Drift right")
            return {'action': 'DRIFT_RIGHT', 'turn': -0.4, 'speed': -0.8}
        
        if right < 0.7:
            print(f"↖️ RIGHT obstacle {right:.2f}m - Drift left")
            return {'action': 'DRIFT_LEFT', 'turn': 0.4, 'speed': -0.8}
        
        # Continue avoidance after clearing
        if self.avoidance_active and self.avoidance_counter > 0:
            self.avoidance_counter -= 1
            return {'action': 'CONTINUE_AVOIDANCE', 'turn': 0, 'speed': -0.5}
        
        self.avoidance_active = False
        return {'action': 'CLEAR', 'turn': None, 'speed': None}
    
    
    def distance_to_point(self, target):
        """Calculate distance to a target point"""
        pos = self.get_position()
        dx = target[0] - pos[0]
        dy = target[1] - pos[1]
        return math.sqrt(dx**2 + dy**2)
    
    def angle_to_point(self, target):
        """Calculate angle to a target point"""
        pos = self.get_position()
        dx = target[0] - pos[0]
        dy = target[1] - pos[1]
        target_angle = math.atan2(dy, dx)
        
        current_yaw = self.get_yaw()
        angle_diff = target_angle - current_yaw
        
        # Normalize to [-pi, pi]
        while angle_diff > math.pi:
            angle_diff -= 2 * math.pi
        while angle_diff < -math.pi:
            angle_diff += 2 * math.pi
            
        return angle_diff
    
    def find_nearest_table_needing_food(self):
        """Find the nearest table that doesn't have food yet"""
        pos = self.get_position()
        nearest = None
        min_dist = float('inf')
        
        for table in self.tables:
            if not table['has_food']:
                dist = self.distance_to_point(table['pos'])
                if dist < min_dist:
                    min_dist = dist
                    nearest = table
        
        return nearest
    
    def animate_arms_for_delivery(self, delivering=True):
        """Animate arms for food delivery"""
        if delivering:
            # Extend arms forward to place food
            self.left_shoulder.setPosition(-0.8)
            self.right_shoulder.setPosition(0.8)
            self.left_elbow.setPosition(-1.5)
            self.right_elbow.setPosition(-1.5)
        else:
            # Return to resting position
            self.left_shoulder.setPosition(-0.4)
            self.right_shoulder.setPosition(0.4)
            self.left_elbow.setPosition(-0.3)
            self.right_elbow.setPosition(-0.3)
    
    def balance_and_move(self):
        """Main control loop: balance robot and move - SIMPLIFIED WITH HARD STOPS"""
        dt = self.timestep / 1000.0  # Convert to seconds
        
        # Get tilt angle
        tilt = self.get_tilt_angle()
        
        # Check boundaries FIRST - HIGHEST PRIORITY
        boundary_status = self.check_boundaries()
        
        if boundary_status['stop_now']:
            # IMMEDIATELY STOP - Don't try to navigate back
            print("🛑 BOUNDARY STOP ACTIVATED - HALTING ALL MOVEMENT")
            self.target_speed = 0
            self.target_turn = 0
            
            # Still balance, but don't move
            balance_correction = self.balance_pid.update(-tilt, dt)
            self.left_motor.setVelocity(balance_correction)
            self.right_motor.setVelocity(balance_correction)
            return
        
        # Check obstacles
        obstacles = self.check_obstacles()
        
        # Apply collision avoidance
        avoidance = self.collision_avoidance_behavior(obstacles)
        
        if avoidance['action'] == 'STOP':
            print("🛑 OBSTACLE STOP")
            self.target_speed = 0
            self.target_turn = 0
        elif avoidance['action'] in ['AVOID_LEFT', 'AVOID_RIGHT', 'DRIFT_LEFT', 'DRIFT_RIGHT']:
            if avoidance['turn'] is not None:
                self.target_turn = avoidance['turn']
            if avoidance['speed'] is not None:
                self.target_speed = avoidance['speed']
        
        # Calculate balance correction
        balance_correction = self.balance_pid.update(-tilt, dt)
        
        # Calculate speed and turn corrections
        speed_correction = self.speed_pid.update(self.target_speed, dt)
        turn_correction = self.turn_pid.update(self.target_turn, dt)
        
        # Combine all corrections
        left_velocity = balance_correction + speed_correction - turn_correction
        right_velocity = balance_correction + speed_correction + turn_correction
        
        # Limit velocities
        max_vel = 15.0
        left_velocity = max(-max_vel, min(max_vel, left_velocity))
        right_velocity = max(-max_vel, min(max_vel, right_velocity))
        
        # Apply to motors
        self.left_motor.setVelocity(left_velocity)
        self.right_motor.setVelocity(right_velocity)
    
    def navigate_to_target(self, target_pos, arrival_distance=0.5):
        """Navigate to a target position with boundary and obstacle awareness"""
        distance = self.distance_to_point(target_pos)
        
        if distance < arrival_distance:
            # Arrived at target
            self.target_speed = 0
            self.target_turn = 0
            return True
        else:
            # Check if we're in avoidance mode - let collision avoidance handle movement
            if self.avoidance_active:
                return False  # Don't override avoidance behavior
            
            # Calculate desired angle
            angle_to_target = self.angle_to_point(target_pos)
            
            # Turn towards target
            if abs(angle_to_target) > 0.1:
                self.target_turn = angle_to_target * 2.0  # Proportional turning
                self.target_speed = -0.5  # Move slowly while turning
            else:
                self.target_turn = 0
                self.target_speed = -2.0  # Move forward at moderate speed
            
            return False
    
    def run(self):
        """Main control loop - SIMPLIFIED FOR TESTING"""
        state = 'IDLE'
        state_timer = 0
        
        print("\n" + "="*60)
        print("🤖 ROBOT STARTING - BOUNDARY TEST MODE")
        print("   Robot will stay in place and only balance")
        print("   Testing boundary detection and collision avoidance")
        print("="*60 + "\n")
        
        while self.robot.step(self.timestep) != -1:
            state_timer += 1
            
            # DISABLED AUTOMATIC NAVIGATION FOR TESTING
            # Just stay still and balance
            self.target_speed = 0
            self.target_turn = 0
            
            # Always maintain balance and check boundaries
            self.balance_and_move()


if __name__ == "__main__":
    controller = ServiceRobotController()
    controller.run()
