"""
Robot drive handler for the pioneer.
"""
# ----- Imports ----- #

import serial
from time import sleep, time

import random

import course
import pid
import packets

# ----- Classes ----- #


class RobotDrive:
    def __init__(self, serial_port):
        self._conn = serial.Serial(serial_port)
        self._left_pid = pid.PID(0, kp=3, kd=0, ki=0)
        self._right_pid = pid.PID(0, kp=3, kd=0, ki=0)
        self._last: course.Directive = None
        self._count = 0

    def drive(self, directive: course.Directive):
        """
        Build and send drive command to the robot based on the given directive.

        :param directive: Directive to perform.
        """
        self._conn.flushInput()
        self._conn.flush()

        # Open the connection if it is closed; Wait before starting to send
        # commands.
        try:
            self._conn.open()
        except serial.SerialException:
            pass
        else:
            sleep(1.5)

        self._last = directive
        self._count = 0

        start_time = time()
        while time() - start_time < directive.duration:
            self.command()

        print(self._count)

    def command(self):
        packet = self._last.get_packet()
        self._conn.write(packet)

        l_feedback, r_feedback = packets.parse_feedback(self._conn.read(8))  # TODO: Get this better
        l_feedback /= 3.2
        r_feedback /= 3.2
        self._count += 1

        l_command, r_command = self._last.get_values()
        l_feedback = l_command + (random.random() - 0.5) * 3
        r_feedback = r_command + (random.random() - 0.5) * 3

        l_correction = self._left_pid.pid_step(l_command, l_feedback, time())
        r_correction = self._right_pid.pid_step(r_command, r_feedback, time())

        l_next = round(min(max(l_command + l_correction, -255), 255), 0)
        r_next = round(min(max(r_command + r_correction, -255), 255), 0)

        self._last = course.Directive.from_left_right(l_next, r_next, 0)
        print(self._last, l_correction, r_correction)

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
