"""
Robot drive handler for the pioneer.
"""
# ----- Imports ----- #

import serial
from time import sleep, time

import course
import pid
import packets

# ----- Consts ----- #

MOTOR_COMMAND_LIMIT = 0xD0
CONTROLLED_MOTOR_LIMIT = 0xDF

# ----- Classes ----- #


class RobotDrive:
    def __init__(self, serial_port, left_pid: pid.PID, right_pid: pid.PID):
        self._conn = serial.Serial(serial_port)
        self._left_pid = left_pid
        self._right_pid = right_pid
        # self._last: course.Directive = None
        self._count = 0

        self._lines = [f"l_command,r_command,l_feedback,r_feedback\n"]
        self._l_feedbacks = []
        self._r_feedbacks = []

    def set_pid(self,
                left_kp: float, left_ki: float, left_kd: float,
                right_kp: float, right_ki: float, right_kd: float):
        self._left_pid.kp = left_kp
        self._left_pid.ki = left_ki
        self._left_pid.kd = left_kd
        self._right_pid.kp = right_kp
        self._right_pid.ki = right_ki
        self._right_pid.kd = right_kd

    def drive(self, directive: course.Directive):
        """
        Build and send drive command to the robot based on the given directive.

        :param directive: Directive to perform.
        """
        # Open the connection if it is closed; Wait before starting to send
        # commands.
        try:
            self._conn.open()
        except serial.SerialException:
            pass
        else:
            sleep(1.5)

        self._last = directive
        self._current_command = directive
        self._count = 0
        self._lines = [f"l_command,r_command,l_feedback,r_feedback\n"]
        self._l_feedbacks = []
        self._r_feedbacks = []

        # self._conn.flush()
        self._conn.flushInput()
        start_time = time()
        while time() - start_time < directive.duration:
            self.command()

        # with open(f"{directive} {round(time())}.csv", "wt") as f:
        #     f.writelines(self._lines)

        self.stop()
        print(self._count)

    def command(self):
        packet = self._last.get_packet()
        self._conn.write(packet)

        self._conn.flushInput()
        l_feedback, r_feedback = packets.parse_feedback(self._conn.read(8))  # TODO: Get this better
        self._count += 1

        l_command, r_command = self._current_command.get_values()

        # Get feedbacks and adjust sign values.
        l_command = self.limit_command(l_command, MOTOR_COMMAND_LIMIT)
        r_command = self.limit_command(r_command, MOTOR_COMMAND_LIMIT)
        l_feedback = -l_feedback if l_command < 0 else l_feedback
        r_feedback = -r_feedback if r_command < 0 else r_feedback

        l_last, r_last = self._last.get_values()
        self._lines.append(f"{l_last},{r_last},{l_feedback},{r_feedback}\n")

        # Filter feedbacks.
        self._l_feedbacks.append(l_feedback)
        self._r_feedbacks.append(r_feedback)
        if len(self._l_feedbacks) != len(self._r_feedbacks):
            raise RuntimeError("Unmatching history")
        if len(self._l_feedbacks) < 10:
            return
        l_feedback = sum(self._l_feedbacks) / 10
        r_feedback = sum(self._r_feedbacks) / 10
        self._l_feedbacks.pop(0)
        self._r_feedbacks.pop(0)

        # Get correction for values.
        l_feedback /= 3.35
        r_feedback /= 3.4
        l_correction = self._left_pid.pid_step(l_command, l_feedback, time())
        r_correction = self._right_pid.pid_step(r_command, r_feedback, time())

        l_next = self.limit_command(l_command + l_correction,
                                    CONTROLLED_MOTOR_LIMIT)
        r_next = self.limit_command(r_command + r_correction,
                                    CONTROLLED_MOTOR_LIMIT)

        self._last = course.Directive.from_left_right(l_next, r_next, 0)

    @staticmethod
    def limit_command(value, limit):
        return round(min(max(value, -limit), limit))

    def disable_pid(self):
        self._left_pid.kp = 0
        self._left_pid.ki = 0
        self._left_pid.kd = 0
        self._right_pid.kp = 0
        self._right_pid.ki = 0
        self._right_pid.kd = 0

    def stop(self):
        """
        Stop the robot from moving.
        """
        self._conn.write(course.Directive.stop().get_packet())

    def disconnect(self):
        """
        Close the connection to the motor controller.
        """
        self._conn.close()

    def reconnect(self):
        self._conn.close()
        self._conn.open()
