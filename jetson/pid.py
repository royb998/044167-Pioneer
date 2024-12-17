"""
File: pid.py
Date: 2024-12-10
"""
# ---------- Classes ---------- #


class PID(object):
    def __init__(self, current_time, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.current_time = current_time

        self.previous_time = current_time
        self.previous_error = 0
        self.integral = 0

    def pid_step(self, ref, current, clock):
        # Calculate time difference from the previous step
        # dt = clock - self.previous_time
        dt = 0.01

        # Calculate error
        error = ref - current

        # Proportional term
        P = self.kp * error

        # Integral term with anti-windup (simple clamping)
        self.integral += error * dt
        I = self.ki * self.integral

        # Derivative term
        if dt > 0:
            D = self.kd * (error - self.previous_error) / dt
        else:
            D = 0

        # Update previous values for next iteration
        self.previous_time = clock
        self.previous_error = error

        # Calculate the control output
        control_output = P + I + D

        # Optionally, apply constraints or limits to control output
        # Example: if control_output > MAX_OUTPUT:
        #              control_output = MAX_OUTPUT
        #          elif control_output < MIN_OUTPUT:
        #              control_output = MIN_OUTPUT

        return round(control_output, 3)
