import can
from base_motor import BaseMotor
from constants import X_MOTOR_ID, Y_MOTOR_ID, Z_MOTOR_ID, X_RATIO, Y_RATIO, Z_RATIO


class XMotor(BaseMotor):
    def __init__(self, bus: can.interface.Bus):
        super().__init__(
            bus,
            X_MOTOR_ID,
            X_RATIO
        )

class YMotor(BaseMotor):
    def __init__(self, bus: can.interface.Bus):
        super().__init__(
            bus,
            Y_MOTOR_ID,
            Y_RATIO,
            zero_point=53,
            left_limit=0,
            right_limit=170
        )

class ZMotor(BaseMotor):
    def __init__(self, bus: can.interface.Bus):
        super().__init__(
            bus,
            Z_MOTOR_ID,
            Z_RATIO,
            zero_point=103,
            left_limit=0,
            right_limit=140
        )