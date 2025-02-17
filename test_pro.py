import time

import can
import pygame

from arctos import Arctos
from swith_pro_controller import Button, Axis, DPad

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
                if button == Button.ZL:
                    arctos.x_motor().make_turn(1)
                elif button == Button.ZR:
                    arctos.x_motor().make_turn(-1)
                elif button == Button.L:
                    arctos.y_motor().make_turn(1)
                elif button == Button.R:
                    arctos.y_motor().make_turn(-1)
                elif button == Button.X:
                    arctos.z_motor().make_turn(1)
                elif button == Button.B:
                    arctos.z_motor().make_turn(-1)
                elif button == Button.A:
                    arctos.a_motor().make_turn(1)
                elif button == Button.Y:
                    arctos.a_motor().make_turn(-1)
            else:
                if button in pressed_buttons:
                    pressed_buttons.remove(button)

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.1)

    pygame.quit()
    bus.shutdown()

if __name__ == "__main__":
    play_with_arm()


