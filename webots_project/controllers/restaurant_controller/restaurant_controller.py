"""
Self-Balancing Restaurant Service Robot Controller
PID balance + waypoint navigation + food pickup & delivery
"""

from controller import Robot
import math

# ======================== PID ========================
class PIDController:
    def __init__(self, kp, ki, kd, integral_limit=5.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.integral_limit = integral_limit

    def compute(self, error, dt):
        self.integral += error * dt
        self.integral = max(-self.integral_limit, min(self.integral_limit, self.integral))
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0


# ======================== LAYOUT ========================
TABLE_POS = {
    1: (-7, 7),  2: (-7, 4),  3: (-7, 1),  4: (-7, -2),  5: (-7, -5),
    6: (-2, 6),  7: (-2, 2),  8: (-2, -2),
    9: (2, 6),  10: (2, 2),  11: (2, -2),
}

ROBOT_TABLES = {1: [1, 2, 3, 4], 2: [5, 6, 7, 8], 3: [9, 10, 11]}

# Pickup spots near the service counter (counter at x=5, y=-6, width 4)
# Robots approach from restaurant side (x < 5)
# Aligned with food positions: food1=(5,-7), food2=(5,-6.3), food3=(5,-5.5)
ROBOT_PICKUP = {1: (4.5, -7.0), 2: (4.5, -6.3), 3: (4.5, -5.5)}

# Aisle X coordinates for navigation
AISLE_LEFT   = -4.5
AISLE_CENTER =  0.0
AISLE_RIGHT  =  4.0
AISLE_SOUTH_Y = -7.5   # horizontal corridor south of all tables


def pick_aisle(table_x):
    """Choose the nearest aisle for a given table x-coordinate."""
    if table_x <= -5:
        return AISLE_LEFT
    elif table_x <= -1:
        return AISLE_CENTER
    else:
        return AISLE_RIGHT


def route_to_pickup(start_x, start_y, pickup):
    """Navigate from anywhere to the kitchen pickup, via south corridor."""
    px, py = pickup
    wps = []
    # Go to the nearest aisle's south point first
    if start_x < -2:
        wps.append((AISLE_LEFT, AISLE_SOUTH_Y))
    elif start_x < 2:
        wps.append((AISLE_CENTER, AISLE_SOUTH_Y))
    # Then travel east along south corridor
    wps.append((AISLE_RIGHT, AISLE_SOUTH_Y))
    # Then move to the pickup
    wps.append(pickup)
    return wps


def route_to_table(table_id):
    """Navigate from kitchen area to a specific table."""
    tx, ty = TABLE_POS[table_id]
    aisle_x = pick_aisle(tx)
    wps = []
    # Start by going to the right aisle in the south corridor
    wps.append((AISLE_RIGHT, AISLE_SOUTH_Y))
    # If table is not in the right aisle, go west
    if aisle_x != AISLE_RIGHT:
        wps.append((aisle_x, AISLE_SOUTH_Y))
    # Go north to the table's Y
    wps.append((aisle_x, ty))
    # Approach the table from the aisle side
    if aisle_x > tx:
        wps.append((tx + 1.2, ty))
    else:
        wps.append((tx - 1.2, ty))
    return wps


def route_from_table(table_id, pickup):
    """Navigate from a table back to the kitchen pickup."""
    tx, ty = TABLE_POS[table_id]
    aisle_x = pick_aisle(tx)
    wps = []
    # Back to the aisle
    wps.append((aisle_x, ty))
    # South to the corridor
    wps.append((aisle_x, AISLE_SOUTH_Y))
    # East if needed
    if aisle_x != AISLE_RIGHT:
        wps.append((AISLE_RIGHT, AISLE_SOUTH_Y))
    # To pickup
    wps.append(pickup)
    return wps


# ======================== CONTROLLER ========================
class BalancingRobot:
    def __init__(self):
        self.robot = Robot()
        self.dt_ms = int(self.robot.getBasicTimeStep())
        self.dt = self.dt_ms / 1000.0

        # Identity
        cd = self.robot.getCustomData() or ""
        self.rid = 1
        if "robot_id=" in cd:
            try:
                self.rid = int(cd.split("robot_id=")[1].split()[0])
            except (ValueError, IndexError):
                pass
        self.name = self.robot.getName()
        self.tag = f"[R{self.rid}]"

        self.my_tables = ROBOT_TABLES.get(self.rid, [1, 2, 3, 4])
        self.my_pickup = ROBOT_PICKUP.get(self.rid, (4.5, -6.3))

        # Motors
        self.lm = self.robot.getDevice("left_wheel_motor")
        self.rm = self.robot.getDevice("right_wheel_motor")
        self.lm.setPosition(float("inf"))
        self.rm.setPosition(float("inf"))
        self.lm.setVelocity(0)
        self.rm.setVelocity(0)

        # Arms
        self.lsh = self.robot.getDevice("left_shoulder_motor")
        self.rsh = self.robot.getDevice("right_shoulder_motor")
        self.lel = self.robot.getDevice("left_elbow_motor")
        self.rel = self.robot.getDevice("right_elbow_motor")
        self._arms("rest")

        # Sensors
        self.imu = self.robot.getDevice("imu")
        self.imu.enable(self.dt_ms)
        self.gps = self.robot.getDevice("gps")
        self.gps.enable(self.dt_ms)
        self.accel = self.robot.getDevice("accelerometer")
        self.accel.enable(self.dt_ms)
        self.gyro = self.robot.getDevice("gyro")
        self.gyro.enable(self.dt_ms)
        for s in ["distance_front", "distance_left", "distance_right"]:
            self.robot.getDevice(s).enable(self.dt_ms)

        self.ls = self.robot.getDevice("left_wheel_sensor")
        self.rs = self.robot.getDevice("right_wheel_sensor")
        self.ls.enable(self.dt_ms)
        self.rs.enable(self.dt_ms)

        # Balance PID (tuned for basicTimeStep=4)
        self.pid = PIDController(kp=150.0, ki=20.0, kd=10.0, integral_limit=2.0)

        # Encoder state
        self.prev_l = 0.0
        self.prev_r = 0.0
        self.enc_init = False
        self.actual_speed = 0.0

        # Navigation
        self.target_speed = 0.0
        self.target_turn = 0.0
        self.waypoints = []
        self.wp_idx = 0

        # State machine
        self.state = "STABILIZE"
        self.timer = 0
        self.delivery_count = 0
        self.queue = []
        self.current_table = 0
        self.step_n = 0

        print(f"{self.tag} Init: tables={self.my_tables} pickup={self.my_pickup}")

    def _arms(self, pose):
        if pose == "rest":
            self.lsh.setPosition(-0.5); self.rsh.setPosition(0.5)
            self.lel.setPosition(-0.4); self.rel.setPosition(0.4)
        elif pose == "carry":
            self.lsh.setPosition(-1.2); self.rsh.setPosition(1.2)
            self.lel.setPosition(-1.6); self.rel.setPosition(1.6)
        elif pose == "serve":
            self.lsh.setPosition(-0.9); self.rsh.setPosition(0.9)
            self.lel.setPosition(-1.0); self.rel.setPosition(1.0)

    # ---- Sensors ----
    def pos(self):
        v = self.gps.getValues()
        return v[0], v[1]

    def yaw(self):
        return self.imu.getRollPitchYaw()[2]

    def pitch(self):
        return self.imu.getRollPitchYaw()[1]

    # ---- Navigation helpers ----
    def dist_to(self, tx, ty):
        x, y = self.pos()
        return math.hypot(tx - x, ty - y)

    def angle_to(self, tx, ty):
        x, y = self.pos()
        target = math.atan2(ty - y, tx - x)
        diff = target - self.yaw()
        while diff > math.pi: diff -= 2 * math.pi
        while diff < -math.pi: diff += 2 * math.pi
        return diff

    def steer_to(self, tx, ty, arrive=0.7):
        """Set target_speed and target_turn to navigate toward (tx,ty).
        Returns True when arrived."""
        d = self.dist_to(tx, ty)
        if d < arrive:
            self.target_speed = 0
            self.target_turn = 0
            return True

        a = self.angle_to(tx, ty)
        if abs(a) > 0.4:
            self.target_turn = max(-0.8, min(0.8, a))
            self.target_speed = 0.5
        elif abs(a) > 0.15:
            self.target_turn = a * 0.8
            self.target_speed = max(0.5, min(d * 0.4, 2.0))
        else:
            self.target_turn = a * 0.5
            self.target_speed = max(0.7, min(d * 0.5, 3.0))
        return False

    def follow_wps(self, arrive=0.7):
        """Follow waypoint list. Returns True when all done."""
        if self.wp_idx >= len(self.waypoints):
            self.target_speed = 0
            self.target_turn = 0
            return True
        tx, ty = self.waypoints[self.wp_idx]
        if self.steer_to(tx, ty, arrive):
            self.wp_idx += 1
        return self.wp_idx >= len(self.waypoints)

    # ---- Balance ----
    def balance(self):
        dt = self.dt
        p = self.pitch()

        if abs(p) > 0.8:
            self.lm.setVelocity(0)
            self.rm.setVelocity(0)
            return

        # Encoder speed
        lp = self.ls.getValue()
        rp = self.rs.getValue()
        if not self.enc_init:
            self.prev_l = lp
            self.prev_r = rp
            self.enc_init = True
        ls = (lp - self.prev_l) / dt
        rs = (rp - self.prev_r) / dt
        self.prev_l = lp
        self.prev_r = rp
        self.actual_speed = (ls + rs) / 2.0

        # Cascaded control: speed error -> desired lean -> PID
        LEAN_FACTOR = 0.015
        MAX_LEAN = 0.05
        speed_err = self.target_speed - self.actual_speed
        desired_lean = max(-MAX_LEAN, min(MAX_LEAN, speed_err * LEAN_FACTOR))

        balance_err = p - desired_lean
        motor_out = self.pid.compute(balance_err, dt)

        turn = self.target_turn * 2.0

        lv = max(-30, min(30, motor_out - turn))
        rv = max(-30, min(30, motor_out + turn))

        self.lm.setVelocity(lv)
        self.rm.setVelocity(rv)

    # ---- Signal delivery to supervisor ----
    def signal_delivery(self, table_id):
        self.delivery_count += 1
        self.robot.setCustomData(
            f"robot_id={self.rid} delivered={table_id} n={self.delivery_count}")

    # ---- State machine ----
    def run(self):
        # Staggered start
        stab_time = 2.0 + self.rid * 1.0
        stab_steps = int(stab_time / self.dt)

        while self.robot.step(self.dt_ms) != -1:
            self.step_n += 1
            self.timer += 1

            # Debug every 2 seconds
            if self.step_n % 500 == 0:
                x, y = self.pos()
                print(f"{self.tag} step={self.step_n} pos=({x:+.1f},{y:+.1f}) "
                      f"state={self.state} spd={self.actual_speed:+.1f}/{self.target_speed:.1f} "
                      f"pitch={math.degrees(self.pitch()):+.1f}deg")

            # ========== STATE MACHINE ==========
            if self.state == "STABILIZE":
                self.target_speed = 0
                self.target_turn = 0
                if self.timer > stab_steps:
                    self.queue = list(self.my_tables)
                    self.state = "NEXT_ORDER"
                    self.timer = 0
                    print(f"{self.tag} Stabilized! Starting deliveries.")

            elif self.state == "NEXT_ORDER":
                self.target_speed = 0
                self.target_turn = 0
                if not self.queue:
                    self.queue = list(self.my_tables)
                    # Brief pause before next round
                    self.state = "PAUSE"
                    self.timer = 0
                else:
                    self.current_table = self.queue.pop(0)
                    x, y = self.pos()
                    self.waypoints = route_to_pickup(x, y, self.my_pickup)
                    self.wp_idx = 0
                    self.state = "GOTO_KITCHEN"
                    self.timer = 0
                    print(f"\n{self.tag} >> Table {self.current_table}: Going to kitchen "
                          f"({len(self.waypoints)} waypoints)")

            elif self.state == "PAUSE":
                self.target_speed = 0
                self.target_turn = 0
                if self.timer > int(3.0 / self.dt):
                    self.state = "NEXT_ORDER"
                    self.timer = 0

            elif self.state == "GOTO_KITCHEN":
                done = self.follow_wps(arrive=0.8)
                if done:
                    self.state = "PICKUP"
                    self.timer = 0
                    self._arms("carry")
                    print(f"{self.tag} At kitchen counter. Picking up food...")

            elif self.state == "PICKUP":
                self.target_speed = 0
                self.target_turn = 0
                # Wait 0.5 seconds at counter
                if self.timer > int(0.5 / self.dt):
                    x, y = self.pos()
                    self.waypoints = route_to_table(self.current_table)
                    self.wp_idx = 0
                    self.state = "GOTO_TABLE"
                    self.timer = 0
                    print(f"{self.tag} Got food! Heading to Table {self.current_table} "
                          f"({len(self.waypoints)} waypoints)")

            elif self.state == "GOTO_TABLE":
                done = self.follow_wps(arrive=0.8)
                if done:
                    self.state = "SERVE"
                    self.timer = 0
                    self._arms("serve")
                    print(f"{self.tag} At Table {self.current_table}. Serving...")

            elif self.state == "SERVE":
                self.target_speed = 0
                self.target_turn = 0
                # Wait 0.6 seconds at table
                if self.timer > int(0.6 / self.dt):
                    self._arms("rest")
                    self.signal_delivery(self.current_table)
                    print(f"{self.tag} *** Delivered to Table {self.current_table}! "
                          f"(#{self.delivery_count} total)")

                    self.waypoints = route_from_table(self.current_table, self.my_pickup)
                    self.wp_idx = 0
                    self.state = "RETURNING"
                    self.timer = 0

            elif self.state == "RETURNING":
                done = self.follow_wps(arrive=0.8)
                if done:
                    self.state = "NEXT_ORDER"
                    self.timer = 0

            # Always run balance
            self.balance()


if __name__ == "__main__":
    bot = BalancingRobot()
    bot.run()
