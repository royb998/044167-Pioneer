"""
Handle command chains for driving courses that take several movements.
"""
from typing import Tuple

# ----- Imports ----- #

import packets

# ----- Consts ----- #

_MAX_MOTOR = 255

# ----- Functions ----- #


def _calc_lr_values(x: float, y: float) -> (int, int):
    """
    Calculate the left-right values for the robot based no x-y coordinates given
    as input. The coordinates given describe forward speed (y) and rotation
    speed (x).

    The values of x and y are enforced to sum to a valid left/right value (i.e.,
    between -1 and 1).

    :param x: Rotation speed (positive clockwise; negative ccw).
    :param y: General speed forward. Note that "forward" here is relative to the
        robot's body, not to the ground.
    :return: Signed motor values for the (left, right) motors (negative values
        for reverse drive).
    """
    left = y + x
    right = y - x

    if round(abs(left), 3) > 1 or round(abs(right), 3) > 1:
        print(x, y, left, right)
        raise ValueError("Invalid x,y values")

    return int(left * _MAX_MOTOR), int(right * _MAX_MOTOR)


def _calc_xy_values(left: int, right: int) -> Tuple[float, float]:
    if abs(left) > _MAX_MOTOR or abs(right) > _MAX_MOTOR:
        raise ValueError("Invalid L,R values")

    x = (left - right) / (2 * _MAX_MOTOR)
    y = (right + left) / (2 * _MAX_MOTOR)

    return x, y

# ----- Classes ----- #


class Directive:
    _stop = None

    @classmethod
    def stop(cls) -> "Directive":
        if cls._stop is None:
            cls._stop = Directive("0 0 0")
        return cls._stop

    @staticmethod
    def from_left_right(left: int, right: int, time: float) -> "Directive":
        x, y = _calc_xy_values(left, right)
        return Directive(f"{x} {y} {time}")

    def __init__(self, line: str):
        values = line.split()
        self._x = float(values[0])
        self._y = float(values[1])
        self._time = float(values[2])

    @property
    def duration(self):
        return self._time

    def get_packet(self) -> bytes:
        left, right = _calc_lr_values(self._x, self._y)
        stop = (left == 0) and (right == 0)
        return packets.build_command_packet(left, right,
                                            stop=stop)

    def get_values(self) -> Tuple[int, int]:
        return _calc_lr_values(self._x, self._y)

    def __str__(self):
        x = round(self._x, 3)
        y = round(self._y, 3)
        time = round(self._time, 3)
        return f"{x} {y} {time}"

    def __repr__(self):
        x = round(self._x, 3)
        y = round(self._y, 3)
        time = round(self._time, 3)
        return f"<x: {x} y: {y} time: {time}>"


class Course:
    def __init__(self, directives_path: str):
        with open(directives_path) as directives_file:
            lines = directives_file.readlines()

        self._directives = [Directive(line) for line in lines]
        self._directives.append(Directive.stop())

    def get_packets(self):
        return [directive.get_packet() for directive in self._directives]

    def __iter__(self):
        return iter(self._directives)
