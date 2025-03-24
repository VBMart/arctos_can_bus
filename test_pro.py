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

button_axis_map = {
    DPad.DOWN:  {'axis': 'b', 'direction': -1},
    DPad.UP:    {'axis': 'b', 'direction':  1},
    DPad.RIGHT: {'axis': 'c', 'direction':  1},
    DPad.LEFT:  {'axis': 'c', 'direction': -1},
}

class MyJoystick:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.joystick.init()

        # Detect the first gamepad
        if pygame.joystick.get_count() == 0:
            print("No gamepad found!")
            exit()

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Connected to: {self.joystick.get_name()}")

        self.held_buttons = []
        self.pressed_buttons = []
        self.released_buttons = []

    def __delete__(self, instance):
        pygame.quit()

    def process_buttons(self):
        pygame.event.pump()
        self.pressed_buttons = []
        self.released_buttons = []
        for button in Button:
            if self.joystick.get_button(button.value):
                if button not in self.held_buttons:
                    self.pressed_buttons.append(button)
                    self.held_buttons.append(button)
            else:
                if button in self.held_buttons:
                    self.released_buttons.append(button)
                    self.held_buttons.remove(button)

        dpad_position = self.joystick.get_hat(0)
        for direction in DPad:
            if dpad_position == direction.value:
                if direction not in self.held_buttons:
                    self.pressed_buttons.append(direction)
                    self.held_buttons.append(direction)
            if dpad_position == (0, 0):
                if direction in self.held_buttons:
                    self.released_buttons.append(direction)
                    self.held_buttons.remove(direction)

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

def play_with_turn_mode(arctos: Arctos):
    gp = MyJoystick()

    # Start reading input
    running = True
    while running:
        pygame.event.pump()  # Process system events

        for button in gp.released_buttons:
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

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.1)

def play_with_speed_mode(arctos: Arctos):
    gp = MyJoystick()

    # Start reading input
    running = True
    while running:
        gp.process_buttons()

        for button in gp.pressed_buttons:
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
                else:
                    print(f"Motor {motor.can_id} is not ready. Status: {motor.status}")

            if button in button_axis_map:
                axis_data = button_axis_map[button]
                speed = 100
                acc = 200
                b_motor = arctos.get_motor_by_axis('b')
                c_motor = arctos.get_motor_by_axis('c')
                if b_motor.status == MotorStatus.OK and c_motor.status == MotorStatus.OK:
                    axis = axis_data['axis']
                    direction = axis_data['direction']
                    d_b = 1
                    d_c = 1
                    if axis == 'c':
                        if direction > 0:
                            d_b = -1
                            d_c = -1
                        else:
                            d_b = 1
                            d_c = 1
                    elif axis == 'b':
                        if direction > 0:
                            d_b = -1
                            d_c = 1
                        else:
                            d_b = 1
                            d_c = -1
                    if b_motor.status == MotorStatus.OK and c_motor.status == MotorStatus.OK:
                        b_motor.run_in_speed_mode(d_b, speed, acc)
                        c_motor.run_in_speed_mode(d_c, speed, acc)
                        time.sleep(0.3)
                else:
                    print(f"Motor {b_motor.can_id} is not ready. Status: {b_motor.status}")
                    print(f"Motor {c_motor.can_id} is not ready. Status: {c_motor.status}")

        for button in gp.released_buttons:
            print(f"Button Released: {button.name}")
            if button in button_motor_map:
                motor_data = button_motor_map[button]
                motor = arctos.get_motor_by_axis(motor_data['motor'])
                if motor.status == MotorStatus.MOVING:
                    motor.stop_in_speed_mode(100)
            if button in button_axis_map:
                b_motor = arctos.get_motor_by_axis('b')
                c_motor = arctos.get_motor_by_axis('c')
                if b_motor.status == MotorStatus.MOVING:
                    b_motor.stop_in_speed_mode(100)
                if c_motor.status == MotorStatus.MOVING:
                    c_motor.stop_in_speed_mode(100)

        # Quit on ESC key
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        time.sleep(0.3)

def debug_buttons():
    gp = MyJoystick()
    running = True
    while running:
        gp.process_buttons()
        for button in gp.pressed_buttons:
            print(f"Button Pressed: {button.name}")
        for button in gp.released_buttons:
            print(f"Button Released: {button.name}")
        time.sleep(0.1)


def play_with_arm():
    bus = can.ThreadSafeBus(interface="slcan", channel="/dev/ttyACM0", bitrate=500000)
    arctos = Arctos(bus)

    is_make_turn_mode = False

    if is_make_turn_mode:
        play_with_turn_mode(arctos)
    else:
        play_with_speed_mode(arctos)

    pygame.quit()
    bus.shutdown()

if __name__ == "__main__":
    # debug_buttons()
    play_with_arm()


