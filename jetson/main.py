"""
Interactive main loop for the robot.
"""
import argparse
import json
from sys import argv

import drive
from course import *
from pid import PID

def get_pid_from_file(path_to_pid_json):
    with open(path_to_pid_json, "r") as f:
        data = json.load(f)

    left_data = data["left"]
    left = PID(0, left_data["kp"], left_data["ki"], left_data["kd"])
    right_data = data["right"]
    right = PID(0, right_data["kp"], right_data["ki"], right_data["kd"])

    return left, right


def handle_pid_command(robot, args):
    # Print current params if no args were specified
    if len(args) == 0:
        params = robot.get_pid_params()
        print(json.dumps(params, indent=2))
    elif args[0] == "help":
        print("PID commands:")
        print("  - '' (no command) to view current pid params")
        print("  - 'lset <kp> <ki> <kd>' to set left pid")
        print("  - 'rset <kp> <ki> <kd>' to set right pid")
        print("  - 'set <lkp> <lki> <lkd> <rkp> <rki> <rkd>' to set both pid")
        print("  - 'save <filename>' to save the current parameters to a file")
    elif args[0] == "lset":
        kp, ki, kd = [float(x) for x in args[1:]]
        robot.set_pid(left=(kp, ki, kd), right=None)
    elif args[0] == "rset":
        kp, ki, kd = [float(x) for x in args[1:]]
        robot.set_pid(right=(kp, ki, kd), left=None)
    elif args[0] == "set":
        lkp, lki, lkd, rkp, rki, rkd = [float(x) for x in args[1:]]
        robot.set_pid(left=(lkp, lki, lkd), right=(rkp, rki, rkd))
    elif args[0] == "save":
        filename = f"{args[1]}.json"
        params = robot.get_pid_params()
        with open(filename, "w") as f:
            json.dump(params, f, indent=2)
    else:
        print("Unknown pid subcommand")


def run_loop(robot):
    user_help()

    while True:
        command, *args = input("> ").split()

        if command in ("q", "quit"):
            break
        if command in ("h", "help"):
            user_help()
        if command == "d":
            try:
                directive = Directive(" ".join(args))
                robot.drive(directive)
            except KeyboardInterrupt:
                print("Cancelled by user")
                robot.reconnect()
            except Exception as e:
                print(type(e), e)
            finally:
                robot.reconnect()
                robot.stop()
        elif command == "r":
            robot.reconnect()
        elif command == "s":
            robot.stop()
        elif command == "pid":
            handle_pid_command(robot, args)
        else:
            print("Unknown command")


def user_help():
    print("Enter commands to execute:")
    print("  - enter 'h' to print this help message")
    print("  - enter 'q' to quit")
    print("  - enter 'r' to reestablish connection")
    print("  - enter 's' to stop driving")
    print("  - enter 'd <directive>' to run a directive")
    print("  - enter 'pid <subcommand>' to update PID")
    print("     'pid help' to display PID subcommands")


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


def main(args):
    # Initialize robot.
    left_pid, right_pid = get_pid_from_file(args.pid)
    robot = drive.RobotDrive(args.port, left_pid, right_pid)

    run_loop(robot)

    robot.disconnect()


if __name__ == "__main__":
    main(parse_arguments())
