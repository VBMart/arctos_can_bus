from typing import Optional

import can
from can_helper import make_message, can_send_message, calc_checksum, can_send_message_and_wait_response
from constants import CMD_READ_ENCODER, CMD_GO_HOME, CMD_SET_ZERO, CMD_SET_ENABLE, CMD_REMAP, CMD_MOTOR_STATUS, \
    CMD_RELATIVE_TURN


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


class BaseMotor:
    def __init__(self,
                 bus: can.interface.Bus,
                 id: int,
                 ratio: float,
                 zero_point: float = 0.0,
                 left_limit: Optional[float] = None,
                 right_limit: Optional[float] = None
                 ):
        self.bus = bus
        self.id = id
        self.ratio = ratio
        self.zero_point = zero_point
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.position = None
        self.is_active = True
        self.can_wait_for_response = True

    def set_active(self, active: bool):
        self.is_active = active

    def make_message(self, data) -> can.Message:
        data.append(calc_checksum(id, data))
        return can.Message(arbitration_id=self.id, data=data, is_extended_id=False)

    def send_message(self, message: can.Message, timeout=0.5):
        if self.can_wait_for_response:
            can_send_message_and_wait_response(self.bus, message, timeout=timeout)
        else:
            can_send_message(self.bus, message)

    def read_encoder(self):
        msg_read_encoder = make_message(self.id, [CMD_READ_ENCODER])
        self.send_message(msg_read_encoder)

    def motor_status(self):
        msg_motor_status = make_message(self.id, [CMD_MOTOR_STATUS])
        self.send_message(msg_motor_status)

    def remap(self, enable: bool):
        enable = 1 if enable else 0
        msg_read_encoder = make_message(self.id, [CMD_REMAP, enable])
        self.send_message(msg_read_encoder)

    def set_zero(self):
        msg_motor_set_zero = make_message(self.id, [CMD_SET_ZERO])
        self.send_message(msg_motor_set_zero)
        self.position = 0

    def set_enable(self, enable: bool):
        enable = 1 if enable else 0
        msg_motor_enable = make_message(self.id, [CMD_SET_ENABLE, enable])
        self.send_message(msg_motor_enable)

    def go_zero(self, timeout=30):
        self.position = -1 * self.zero_point
        if self.zero_point != 0:
            self.make_turn(self.zero_point, speed=1000, acc=200, timeout=timeout)

    def go_home(self, timeout=30):
        msg_go_home = make_message(self.id, [CMD_GO_HOME])
        self.send_message(msg_go_home, timeout=timeout)
        self.go_zero(timeout=timeout)

    def make_turn(self, degrees: float, speed: int=1000, acc: int=200, timeout: int = 10):
        assert self.position is not None, 'Position is not set. First call go_home'

        if speed > 3000:
            speed = 3000
        if acc > 1000:
            acc = 1000
        turn = make_relative_turn(speed=speed, acc=acc, degrees=degrees*self.ratio)
        turn_msg = make_message(self.id, turn)
        self.send_message(turn_msg, timeout=timeout)
        self.position += degrees