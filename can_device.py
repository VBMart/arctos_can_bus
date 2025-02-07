from abc import abstractmethod, ABC
import can

from can_helper import calc_checksum, can_send_message_and_wait_response, can_send_message


class CanDevice(ABC):
    def __init__(self, bus: can.interface.Bus, can_id: int):
        self.can_id = can_id
        self.bus = bus
        self.is_active = True
        self.can_wait_for_response = True

    def make_message(self, data) -> can.Message:
        data.append(calc_checksum(self.can_id, data))
        return can.Message(arbitration_id=self.can_id, data=data, is_extended_id=False)

    def send_message(self, message: can.Message, timeout=0.5):
        if self.can_wait_for_response:
            can_send_message_and_wait_response(self.bus, message, timeout=timeout)
        else:
            can_send_message(self.bus, message)

    @abstractmethod
    def on_can_message(self, message: can.Message):
        ...