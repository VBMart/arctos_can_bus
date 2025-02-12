from enum import Enum
from typing import Optional
import can

from can_device import CanDevice
from can_helper import print_motor_message
from constants import CMD_READ_ENCODER, CMD_GO_HOME, CMD_SET_ZERO, CMD_SET_ENABLE, CMD_REMAP, CMD_MOTOR_STATUS, \
    CMD_RELATIVE_TURN, CMD_GET_CURRENT_SPEED


def make_relative_turn(speed: int, acc: int, degrees: float):
    # speed in range 0-3000
    # acc in range 0-255
    # degrees in range -8388607，+8388607
    command = CMD_RELATIVE_TURN
    degrees_value = round(degrees * 0x3FFF) // 360
    data = [command]
    data.extend(list(speed.to_bytes(2, byteorder='big', signed=False)))
    data.extend(list(acc.to_bytes(1, byteorder='big', signed=False)))
    data.extend(list(degrees_value.to_bytes(3, byteorder='big', signed=True)))
    return data


class MotorStatus(str, Enum):
    OK = 'OK'
    ERROR = 'ERROR'
    HOMING = 'HOMING'
    MOVING = 'MOVING'
    UNKNOWN = 'UNKNOWN'


class BaseMotor(CanDevice):
    def __init__(self,
                 bus: can.interface.Bus,
                 can_id: int,
                 ratio: float,
                 zero_point: float = 0.0,
                 left_limit: Optional[float] = None,
                 right_limit: Optional[float] = None
                 ):
        super().__init__(bus, can_id)
        self.ratio = ratio
        self.zero_point = zero_point
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.position = None
        self.status = MotorStatus.UNKNOWN
        self.pending_degrees = None
        self.current_speed = None

    def __str__(self):
        return f"Motor {self.can_id} (active={self.is_active}) with position {self.position}, status {self.status} speed {self.current_speed}"

    def set_active(self, active: bool):
        self.is_active = active

    def is_ready(self):
        return self.status == MotorStatus.OK

    def on_can_message(self, message: can.Message):
        print(f"\tMotor {self.can_id} received message: {message}")
        command = message.data[0]

        print_motor_message(message)

        if command == CMD_GO_HOME:
            status = message.data[1]
            if status == 0x01:
                # Motor started homing
                self.status = MotorStatus.HOMING
            elif status == 0x02:
                # Motor finished homing
                self.status = MotorStatus.OK
                self.position = -1 * self.zero_point
                self.go_zero()
            elif status == 0x00:
                # Motor failed homing
                self.status = MotorStatus.ERROR
        elif command == CMD_RELATIVE_TURN:
            status = message.data[1]
            if status == 0x01:
                # Motor started moving
                self.status = MotorStatus.MOVING
            elif status == 0x02:
                # Motor finished moving
                self.position += self.pending_degrees
                self.pending_degrees = None
                self.status = MotorStatus.OK
            elif status == 0x03:
                # Motor found limit
                if self.pending_degrees > 0:
                    self.position = self.right_limit
                else:
                    self.position = self.left_limit
                self.pending_degrees = None
                self.status = MotorStatus.OK
            elif status == 0x00:
                # Motor failed moving
                self.status = MotorStatus.ERROR
        elif command == CMD_GET_CURRENT_SPEED:
            speed_bytes = message.data[1:3]
            self.current_speed = int.from_bytes(speed_bytes, byteorder='big', signed=True)

    def read_encoder(self):
        msg_read_encoder = self.make_message([CMD_READ_ENCODER])
        self.send_message(msg_read_encoder)

    def get_current_speed(self):
        self.current_speed = None
        msg_get_current_speed = self.make_message([CMD_GET_CURRENT_SPEED])
        self.send_message(msg_get_current_speed)

    def motor_status(self):
        msg_motor_status = self.make_message([CMD_MOTOR_STATUS])
        self.send_message(msg_motor_status)

    def remap(self, enable: bool):
        enable = 1 if enable else 0
        msg_read_encoder = self.make_message([CMD_REMAP, enable])
        self.send_message(msg_read_encoder)

    def set_zero(self):
        msg_motor_set_zero = self.make_message([CMD_SET_ZERO])
        self.send_message(msg_motor_set_zero)
        self.position = 0

    def set_enable(self, enable: bool):
        enable = 1 if enable else 0
        msg_motor_enable = self.make_message([CMD_SET_ENABLE, enable])
        self.send_message(msg_motor_enable)

    def go_zero(self, timeout=30):
        if self.zero_point != 0:
            self.make_turn(self.zero_point, speed=1000, acc=200, timeout=timeout)

    def go_home(self, timeout=30):
        self.status = MotorStatus.UNKNOWN
        self.position = None
        msg_go_home = self.make_message([CMD_GO_HOME])
        self.send_message(msg_go_home, timeout=timeout)

    def make_turn(self, degrees: float, speed: int=1000, acc: int=200, timeout: int = 10):
        assert self.position is not None, 'Position is not set. First call go_home'

        if speed > 3000:
            speed = 3000
        if acc > 1000:
            acc = 1000
        turn = make_relative_turn(speed=speed, acc=acc, degrees=degrees*self.ratio)
        turn_msg = self.make_message(turn)
        self.send_message(turn_msg, timeout=timeout)
        self.pending_degrees = degrees