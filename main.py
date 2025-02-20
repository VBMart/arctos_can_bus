import argparse
import can
from time import sleep, time

from arctos import Arctos
from motors import XMotor, YMotor, ZMotor, AMotor, BMotor, CMotor


def run_fn(fn):
    bus = can.interface.Bus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
    fn(bus)
    bus.shutdown()

def run_threaded_fn(fn):
    bus = can.ThreadSafeBus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
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
    arctos.b_motor().set_active(False)
    arctos.c_motor().set_active(False)
    arctos.go_home()
    print("Home sent")

    for i in range(40):
        # Measure speed
        for active_motor in arctos.get_active_motors():
            active_motor.get_current_speed()
        t1 = time()
        while time() - t1 < 2:
            has_all_motor_speeds = True
            for active_motor in arctos.get_active_motors():
                has_all_motor_speeds = has_all_motor_speeds and active_motor.current_speed is not None
            if has_all_motor_speeds:
                break
            sleep(0.1)
        print(f"Waiting {i} / 40")
        print(arctos)
        # is_ready = True
        # for active_motor in arctos.get_active_motors():
        #     is_ready = is_ready and active_motor.is_ready()
        #     is_ready = is_ready and active_motor.position == 0
        # if is_ready:
        #     print("All motors are ready")
        #     break
        sleep(0.5)

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

def debug_motor(bus: can.interface.Bus):
    arctos = Arctos(bus)
    a_motor = arctos.a_motor()
    a_motor.set_zero()
    sleep(1)
    a_motor.run_in_speed_mode(1, 1000, 100)
    sleep(5)
    a_motor.stop_in_speed_mode(100)
    sleep(5)
    a_motor.run_in_speed_mode(-1, 1000, 100)
    sleep(5)
    a_motor.stop_in_speed_mode(100)
    sleep(5)


    # arctos.a_motor().go_home()
    # arctos.go_home()
    # a_motor.go_home()
    # sleep(30)
    # x_motor = arctos.x_motor()
    # x_motor.go_home()
    # a_motor.set_zero()
    # a_motor.make_turn(-90, speed=500, acc=100, timeout=20)
    # x_motor.set_zero()
    # x_motor.make_turn(45, speed=500, acc=100, timeout=1)
    # a_motor.make_turn(90, speed=500, acc=100, timeout=20)
    # a_motor.make_turn(-180, speed=500, acc=100, timeout=20)
    # a_motor.make_turn(90, speed=500, acc=100, timeout=20)
    # x_motor.make_turn(-45, speed=500, acc=100, timeout=1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control motors via CAN bus")
    parser.add_argument("command", choices=["read_encoders", "go_home", "test_x_run", "say_hello"], help="Command to execute")
    args = parser.parse_args()

    command = args.command
    command = 'debug_motor'
    # command = 'go_home'

    if command == "read_encoders":
        run_threaded_fn(read_encoders)
    elif command == "test_x_run":
        run_threaded_fn(test_x_run)
    elif command == "go_home":
        run_threaded_fn(go_home)
    elif command == "say_hello":
        run_threaded_fn(say_hello)
    elif command == "debug_motor":
        run_threaded_fn(debug_motor)
