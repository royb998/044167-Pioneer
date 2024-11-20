"""
Robot drive handler for the pioneer.
"""
# ----- Imports ----- #

import serial
from time import sleep

import course

# ----- Classes ----- #


class RobotDrive:
    def __init__(self, serial_port):
        self._conn = serial.Serial(serial_port)

    def drive(self, directive: course.Directive):
        """
        Build and send drive command to the robot based on the given directive.

        :param directive: Directive to perform.
        """
        packet = directive.get_packet()

        # Open the connection if it is closed; Wait before starting to send
        # commands.
        try:
            self._conn.open()
        except serial.SerialException:
            pass
        else:
            sleep(1.5)
        self._conn.write(packet)

        if directive.duration > 0:
            sleep(directive.duration)
            self.stop()

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
