import argparse

import can

from motors import XMotor, YMotor, ZMotor


def run_fn(fn):
    bus = can.interface.Bus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
    fn(bus)
    bus.shutdown()

def read_encoders(bus: can.interface.Bus):
    print("Reading encoders")
    x_motor = XMotor(bus)
    y_motor = YMotor(bus)
    z_motor = ZMotor(bus)

    x_motor.read_encoder()
    y_motor.read_encoder()
    z_motor.read_encoder()
    print("Encoders read")


def go_home(bus: can.interface.Bus):
    print("Going home")
    x_motor = XMotor(bus)
    y_motor = YMotor(bus)
    z_motor = ZMotor(bus)

    z_motor.go_home(timeout=5)
    y_motor.go_home(timeout=5)
    x_motor.go_home(timeout=5)
    print("Homed")


def test_x_run(bus: can.interface.Bus):
    x_motor = XMotor(bus)
    x_motor.set_zero()
    x_motor.make_turn(90, speed=500, acc=100, timeout=20)
    x_motor.make_turn(-90, speed=500, acc=100, timeout=20)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control motors via CAN bus")
    parser.add_argument("command", choices=["read_encoders", "go_home", "test_x_run"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "read_encoders":
        run_fn(read_encoders)
    elif args.command == "test_x_run":
        run_fn(test_x_run)
    elif args.command == "go_home":
        run_fn(go_home)
