"""
Balance test controller for ServiceRobot_v3.
Tests both PID signs to find which one stabilizes the robot.
Prints detailed diagnostics.
"""

from controller import Robot
import math


def main():
    robot = Robot()
    timestep = int(robot.getBasicTimeStep())
    dt = timestep / 1000.0

    # Motors
    left_motor = robot.getDevice('left_wheel_motor')
    right_motor = robot.getDevice('right_wheel_motor')
    left_motor.setPosition(float('inf'))
    right_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    right_motor.setVelocity(0.0)

    # Arm motors (set to rest pose, won't affect balance)
    for name, pos in [('left_shoulder_motor', -0.5), ('right_shoulder_motor', 0.5),
                      ('left_elbow_motor', -0.4), ('right_elbow_motor', 0.4)]:
        dev = robot.getDevice(name)
        if dev:
            dev.setPosition(pos)

    # Sensors
    imu = robot.getDevice('imu')
    imu.enable(timestep)
    accel = robot.getDevice('accelerometer')
    accel.enable(timestep)
    gyro = robot.getDevice('gyro')
    gyro.enable(timestep)
    left_sensor = robot.getDevice('left_wheel_sensor')
    left_sensor.enable(timestep)
    right_sensor = robot.getDevice('right_wheel_sensor')
    right_sensor.enable(timestep)

    # PID state
    integral = 0.0
    prev_error = 0.0

    # PID gains — aggressive for inverted pendulum
    Kp = 150.0
    Ki = 20.0
    Kd = 10.0
    integral_limit = 2.0

    # Sign: +1 or -1. We try +1 first, flip if robot diverges.
    pid_sign = 1.0
    sign_locked = False
    initial_tilt_dir = 0  # which direction robot initially tilts

    step_count = 0
    max_abs_pitch_seen = 0.0

    prev_left_pos = 0.0
    prev_right_pos = 0.0

    print(f"[BALANCE v3] dt={dt:.4f}s  Kp={Kp} Ki={Ki} Kd={Kd}")
    print(f"[BALANCE v3] Starting with sign={pid_sign:+.0f}")

    while robot.step(timestep) != -1:
        step_count += 1

        # Read sensors
        rpy = imu.getRollPitchYaw()
        a = accel.getValues()
        g = gyro.getValues()

        pitch = rpy[1]
        roll = rpy[0]
        pitch_rate = g[1]

        left_pos = left_sensor.getValue()
        right_pos = right_sensor.getValue()
        wheel_speed = ((left_pos - prev_left_pos) + (right_pos - prev_right_pos)) / (2.0 * dt)
        prev_left_pos = left_pos
        prev_right_pos = right_pos

        # Auto-detect correct sign in first 50 steps
        if not sign_locked and step_count > 5:
            if abs(pitch) > 0.001 and initial_tilt_dir == 0:
                initial_tilt_dir = 1 if pitch > 0 else -1
                print(f"[SIGN] Initial tilt direction: pitch={math.degrees(pitch):+.3f}deg "
                      f"dir={'FORWARD' if initial_tilt_dir > 0 else 'BACKWARD'}")

            # If after 30 steps the pitch has grown past 0.15 rad (~9deg), wrong sign
            if step_count == 75 and abs(pitch) > 0.15:
                pid_sign = -pid_sign
                integral = 0.0
                prev_error = 0.0
                print(f"[SIGN] Pitch diverged to {math.degrees(pitch):+.2f}deg — "
                      f"flipping sign to {pid_sign:+.0f}")
            elif step_count > 75:
                sign_locked = True
                print(f"[SIGN] Locked sign={pid_sign:+.0f} "
                      f"(pitch={math.degrees(pitch):+.3f}deg at step {step_count})")

        # Diagnostics
        if step_count <= 30 or step_count % 50 == 0 or (70 <= step_count <= 85):
            print(f"[t={step_count:5d}] "
                  f"pitch={math.degrees(pitch):+8.3f}d "
                  f"roll={math.degrees(roll):+8.3f}d "
                  f"rate={math.degrees(pitch_rate):+8.2f}d/s "
                  f"a=[{a[0]:+6.2f},{a[2]:+6.2f}] "
                  f"wspd={wheel_speed:+6.1f} "
                  f"sign={pid_sign:+.0f}")

        max_abs_pitch_seen = max(max_abs_pitch_seen, abs(pitch))

        # Safety cutoff
        if abs(pitch) > 0.8:
            left_motor.setVelocity(0.0)
            right_motor.setVelocity(0.0)
            integral = 0.0
            if step_count % 500 == 0:
                print(f"[FALLEN] pitch={math.degrees(pitch):.1f}deg  "
                      f"max_seen={math.degrees(max_abs_pitch_seen):.1f}deg")
            continue

        # PID on pitch
        error = pid_sign * pitch
        integral += error * dt
        integral = max(-integral_limit, min(integral_limit, integral))
        derivative = (error - prev_error) / dt if dt > 0 else 0
        prev_error = error

        output = Kp * error + Ki * integral + Kd * derivative
        speed = max(-30.0, min(30.0, output))

        left_motor.setVelocity(speed)
        right_motor.setVelocity(speed)


if __name__ == "__main__":
    main()
