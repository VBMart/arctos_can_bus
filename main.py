import argparse
from time import sleep

import can
from can import ThreadSafeBus

from arctos import Arctos
from motors import XMotor, YMotor, ZMotor


def run_fn(fn):
    bus = can.interface.Bus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
    fn(bus)
    bus.shutdown()

def run_threaded_fn(fn):
    bus = ThreadSafeBus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
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
    arctos = Arctos(bus)
    arctos.a_motor().set_active(False)
    arctos.b_motor().set_active(False)
    arctos.c_motor().set_active(False)
    arctos.go_home()
    print("Home sent")
    print('-')

    for i in range(15):
        print(f"Waiting for home {i} / 14")
        sleep(1)

    print('-')
    print("Going zero")
    arctos.z_motor().go_zero(timeout=0)
    arctos.y_motor().go_zero(timeout=0)
    arctos.x_motor().go_zero(timeout=0)


def say_hello(bus: can.interface.Bus):
    x_motor = XMotor(bus)
    y_motor = YMotor(bus)
    z_motor = ZMotor(bus)

    go_home(bus)

    x_motor.make_turn(90)
    y_motor.make_turn(90)
    x_motor.make_turn(45)
    x_motor.make_turn(-90)
    x_motor.make_turn(45)
    y_motor.make_turn(-90)
    x_motor.make_turn(-90)
    y_motor.make_turn(40)
    y_motor.make_turn(-40)


def test_x_run(bus: can.interface.Bus):
    x_motor = XMotor(bus)
    x_motor.set_zero()
    x_motor.make_turn(90, speed=500, acc=100, timeout=20)
    x_motor.make_turn(-90, speed=500, acc=100, timeout=20)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control motors via CAN bus")
    parser.add_argument("command", choices=["read_encoders", "go_home", "test_x_run", "say_hello"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "read_encoders":
        run_threaded_fn(read_encoders)
    elif args.command == "test_x_run":
        run_threaded_fn(test_x_run)
    elif args.command == "go_home":
        run_threaded_fn(go_home)
    elif args.command == "say_hello":
        run_threaded_fn(say_hello)
