from typing import Optional

import can
from can_helper import make_message, can_send_message, calc_checksum
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
    print(data)
    data_bytes = ", ".join(
        [f"0x{byte:02X}" for byte in data]
    )
    print(data_bytes)
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

    def set_active(self, active: bool):
        self.is_active = active

    def make_message(self, data) -> can.Message:
        data.append(calc_checksum(id, data))
        return can.Message(arbitration_id=self.id, data=data, is_extended_id=False)

    def read_encoder(self):
        msg_read_encoder = make_message(self.id, [CMD_READ_ENCODER])
        can_send_message(self.bus, msg_read_encoder, timeout=1)

    def motor_status(self):
        msg_motor_status = make_message(self.id, [CMD_MOTOR_STATUS])
        can_send_message(self.bus, msg_motor_status, timeout=1)

    def remap(self, enable: bool):
        enable = 1 if enable else 0
        msg_read_encoder = make_message(self.id, [CMD_REMAP, enable])
        can_send_message(self.bus, msg_read_encoder, timeout=2)

    def set_zero(self):
        msg_motor_set_zero = make_message(self.id, [CMD_SET_ZERO])
        can_send_message(self.bus, msg_motor_set_zero, timeout=1)
        self.position = 0

    def set_enable(self, enable: bool):
        enable = 1 if enable else 0
        msg_motor_enable = make_message(self.id, [CMD_SET_ENABLE, enable])
        can_send_message(self.bus, msg_motor_enable, timeout=1)

    def go_zero(self, timeout=30):
        self.position = 0
        if self.zero_point != 0:
            self.make_turn(self.zero_point, speed=1000, acc=200, timeout=timeout)

    def go_home(self, timeout=30):
        msg_go_home = make_message(self.id, [CMD_GO_HOME])
        can_send_message(self.bus, msg_go_home, timeout=timeout)
        self.go_zero()

    def make_turn(self, degrees: float, speed: int=1000, acc: int=200, timeout: int = 10):
        assert self.position is not None, 'Position is not set. First call go_home'

        if speed > 3000:
            speed = 3000
        if acc > 1000:
            acc = 1000
        turn = make_relative_turn(speed=speed, acc=acc, degrees=degrees*self.ratio)
        turn_msg = make_message(self.id, turn)
        can_send_message(self.bus, turn_msg, timeout=timeout)
        self.position += degrees