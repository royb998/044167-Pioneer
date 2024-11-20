# ----- Imports ----- #

import struct

# ----- Consts ----- #

PACKET_FMT = "??BB?"

# ----- Functions ----- #


def build_packet(left: int, right: int, stop=False) -> bytes:
    """
    Build packet for drive command to send to the robot.

    :param left: Signed value for left motor.
    :param right: Signed value for right motor.
    :param stop: True to stop the robot's motion (disregards left/right
        values). False to drive.
    """
    if stop:
        return b"\x00\x00\x00\x00\x01"

    # Set direction bits
    left_forward = int(left > 0)
    right_forward = int(right > 0)

    # Motors receive positive values.
    left_value = abs(left)
    right_value = abs(right)

    return struct.pack(PACKET_FMT,
                       left_forward, right_forward,
                       left_value, right_value,
                       False)
