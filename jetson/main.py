"""
Interactive main loop for the robot.
"""
import argparse
import json
from sys import argv

import drive
from course import *
from pid import PID

def get_pid_controllers(path_to_pid_json):
    with open(path_to_pid_json, "r") as f:
        data = json.load(f)

    left_data = data["left"]
    left = PID(0, left_data["kp"], left_data["ki"], left_data["kd"])
    right_data = data["right"]
    right = PID(0, right_data["kp"], right_data["ki"], right_data["kd"])

    return left, right


def main(args):
    left_pid, right_pid = get_pid_controllers(args.pid)
    robot = drive.RobotDrive(args.port, left_pid, right_pid)

    print("Enter commands to execute:")
    print("  - enter 'q' to quit")
    print("  - enter 'r' to reestablish connection")
    print("  - enter 's' to stop driving")
    print("  - enter 'd <directive>' to run a directive")
    print("  - enter 'pid <lkp> <lki> <lkd> <rkp> <rki> <rkd>' to update left or right PID")

    while True:
        command, *args = input("> ").split()

        if command == "q":
            break
        if command == "d":
            try:
                directive = Directive(" ".join(args))
                robot.drive(directive)
            except KeyboardInterrupt:
                continue
        elif command == "r":
            robot.reconnect()
        elif command == "s":
            robot.stop()
        elif command == "pid":
            lkp, lki, lkd, rkp, rki, rkd = [float(x) for x in args]
            robot.set_pid(lkp, lki, lkd, rkp, rki, rkd)
        else:
            print("Unknown command")

    robot.disconnect()


def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--port",
                        help="Serial port for the motor controller",
                        type=str,
                        required=True)
    parser.add_argument("--pid",
                        default="resources/pid.json",
                        help="Path to json with PID params",
                        type=str,
                        required=False)

    return parser.parse_args(argv[1:])


if __name__ == "__main__":
    main(parse_arguments())
