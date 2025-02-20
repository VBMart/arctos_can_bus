import time

import can
import pygame
from pygame.joystick import JoystickType

from arctos import Arctos
from base_motor import MotorStatus
from swith_pro_controller import Button, Axis, DPad


button_motor_map = {
    Button.ZL: {'motor': 'x', 'direction':  1},
    Button.ZR: {'motor': 'x', 'direction': -1},
    Button.L:  {'motor': 'y', 'direction':  1},
    Button.R:  {'motor': 'y', 'direction': -1},
    Button.B:  {'motor': 'z', 'direction':  1},
    Button.X:  {'motor': 'z', 'direction': -1},
    Button.A:  {'motor': 'a', 'direction':  1},
    Button.Y:  {'motor': 'a', 'direction': -1},
}


def test_controller():
    # Initialize Pygame
    pygame.init()
    pygame.joystick.init()

    # Detect the first gamepad
    if pygame.joystick.get_count() == 0:
        print("No gamepad found!")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Connected to: {joystick.get_name()}")

    # Start reading input
    running = True
    while running:
        pygame.event.pump()  # Process system events

        # Read button presses
        for button in Button:
            if joystick.get_button(button.value):
                print(f"Button Pressed: {button.name}")

        # Read joystick axes (sticks & triggers)
        for axis in Axis:
            axis_value = joystick.get_axis(axis.value)
            if abs(axis_value) > 0.1:  # Ignore small movements
                print(f"{axis.name}: {axis_value:.2f}")

        # Read D-pad (Hat Switch)
        for i in range(joystick.get_numhats()):
            hat = joystick.get_hat(i)
            for direction in DPad:
                if hat == direction.value:
                    print(f"D-Pad Pressed: {direction.name}")

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.1)

    pygame.quit()


def play_with_turn_mode(joystick: JoystickType, arctos: Arctos):
    pressed_buttons = []

    # Start reading input
    running = True
    while running:
        pygame.event.pump()  # Process system events

        # Read button presses
        for button in Button:
            if joystick.get_button(button.value):
                if button not in pressed_buttons:
                    pressed_buttons.append(button)
                    print(f"Button Pressed: {button.name}")
                    if button == Button.HOME:
                        arctos.go_home()
                    elif button == Button.SCREENSHOT:
                        for motor in arctos.get_active_motors():
                            motor.set_zero()
                if button in button_motor_map:
                    motor_data = button_motor_map[button]
                    motor = arctos.get_motor_by_axis(motor_data['motor'])
                    angle = 1
                    motor.make_turn(motor_data['direction'] * angle, speed=1000, acc=100)
            else:
                if button in pressed_buttons:
                    pressed_buttons.remove(button)

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.1)

def play_with_speed_mode(joystick: JoystickType, arctos: Arctos):
    pressed_buttons = []

    # Start reading input
    running = True
    while running:
        pygame.event.pump()  # Process system events
        new_pressed_buttons = []
        unpresed_buttons = []

        # Read button presses
        for button in Button:
            if joystick.get_button(button.value):
                if button not in pressed_buttons:
                    new_pressed_buttons.append(button)
                    pressed_buttons.append(button)
            else:
                if button in pressed_buttons:
                    unpresed_buttons.append(button)
                    pressed_buttons.remove(button)

        for button in new_pressed_buttons:
            print(f"Button Pressed: {button.name}")
            if button == Button.HOME:
                arctos.go_home()
            elif button == Button.SCREENSHOT:
                for motor in arctos.get_active_motors():
                    motor.set_zero()
            if button in button_motor_map:
                motor_data = button_motor_map[button]
                motor = arctos.get_motor_by_axis(motor_data['motor'])
                if motor.status == MotorStatus.OK:
                    motor.run_in_speed_mode(motor_data['direction'], 300, 100)

        for button in unpresed_buttons:
            print(f"Button Released: {button.name}")
            if button in button_motor_map:
                motor_data = button_motor_map[button]
                motor = arctos.get_motor_by_axis(motor_data['motor'])
                if motor.status == MotorStatus.MOVING:
                    motor.stop_in_speed_mode(100)

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.1)

def play_with_arm():
    bus = can.ThreadSafeBus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
    arctos = Arctos(bus)
    arctos.b_motor().set_active(False)
    arctos.c_motor().set_active(False)

    # Initialize Pygame
    pygame.init()
    pygame.joystick.init()

    # Detect the first gamepad
    if pygame.joystick.get_count() == 0:
        print("No gamepad found!")
        exit()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    print(f"Connected to: {joystick.get_name()}")

    is_make_turn_mode = False

    if is_make_turn_mode:
        play_with_turn_mode(joystick, arctos)
    else:
        play_with_speed_mode(joystick, arctos)


    pygame.quit()
    bus.shutdown()

if __name__ == "__main__":
    play_with_arm()


