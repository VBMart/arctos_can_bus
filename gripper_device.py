import can
from can_device import CanDevice

class GripperDevice(CanDevice):
    def __init__(self,
                 bus: can.interface.Bus,
                 ):
        can_id = 0x07
        super().__init__(bus, can_id)
        self.gripper_position = 0
        self._max_position = 255

    def on_can_message(self, message: can.Message):
        pass

    def run(self):
        data = [self.gripper_position]
        message = self.make_message(data)
        self.send_message(message, timeout=0)

    def set_gripper_position(self, position: int):
        position = min(position, self._max_position)
        position = max(position, 0)
        self.gripper_position = position
        self.run()

    def open(self):
        self.set_gripper_position(self._max_position)

    def close(self):
        self.set_gripper_position(0)