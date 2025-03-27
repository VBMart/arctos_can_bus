from enum import Enum

import can
from can_device import CanDevice

class Color(Enum):
    RED = 0
    ROSE = 1
    MAGENTA = 2
    VIOLET = 3
    BLUE = 4
    AZURE = 5
    CYAN = 6
    SPRING = 7
    GREEN = 8
    CHARTREUSE = 9
    YELLOW = 10
    ORANGE = 11
    WHITE = 12
    BLACK = 13

class LedDevice(CanDevice):
    def __init__(self,
                 bus: can.interface.Bus,
                 ):
        can_id = 0x08
        super().__init__(bus, can_id)
        self.leds = []
        self.num_leds = 11
        for i in range(0, self.num_leds):
            self.leds.append(Color.BLACK)

    def on_can_message(self, message: can.Message):
        pass

    def show(self):
        data = [0x02]
        for i in range(0, len(self.leds), 2):
            first = self.leds[i].value & 0x0F
            second = self.leds[i + 1].value & 0x0F if i + 1 < len(self.leds) else 0
            packed_byte = (first << 4) | second
            data.append(packed_byte)
        message = self.make_message(data)
        self.send_message(message, timeout=0)

    def set_all_leds(self, color: Color):
        for i in range(0, self.num_leds):
            self.set_led(i, color, send_to_device=False)
        self.show()

    def set_led(self, led_id: int, color: Color, send_to_device: bool = True):
        self.leds[led_id] = color

        if send_to_device:
            self.show()

    def set_motor_color(self, motor_id: int, color: Color) -> bool:
        led_mapping = {
            1: [9, 10],
            2: [7, 8],
            3: [5, 6],
            4: [4],
            5: [2, 3],
            6: [0, 1]
        }
        leds = led_mapping[motor_id]
        is_led_changed = False
        for led_id in leds:
            if self.leds[led_id] != color:
                is_led_changed = True
                self.set_led(led_id, color, send_to_device=False)
        return is_led_changed