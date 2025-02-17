from enum import Enum, auto

# Enums for Nintendo Switch Pro Controller
class Button(Enum):
    B = 0
    A = 1
    X = 2
    Y = 3
    SCREENSHOT = 4
    L = 5
    R = 6
    ZL = 7
    ZR = 8
    MINUS = 9
    PLUS = 10
    HOME = 11
    LEFT_STICK_PRESS = 12
    RIGHT_STICK_PRESS = 13

class Axis(Enum):
    LEFT_STICK_X = 0  # Left (-1) to Right (+1)
    LEFT_STICK_Y = 1  # Up (-1) to Down (+1)
    RIGHT_STICK_X = 2 # Left (-1) to Right (+1)
    RIGHT_STICK_Y = 3 # Up (-1) to Down (+1)

class DPad(Enum):
    UP = (0, 1)
    DOWN = (0, -1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


# Corrected Nintendo Switch Pro Controller Mapping
CONTROLLER_MAPPING = {
    "buttons": {
        0: "B",
        1: "A",
        2: "X",
        3: "Y",
        4: "Screenshot",
        5: "L",
        6: "R",
        7: "ZL",
        8: "ZR",
        9: "Minus (-)",
        10: "Plus (+)",
        11: "Home",
        12: "Left Stick Press",
        13: "Right Stick Press",
    },
    "axes": {
        0: "Left Stick X",  # Left (-1) to Right (+1)
        1: "Left Stick Y",  # Up (-1) to Down (+1)
        2: "Right Stick X", # Left (-1) to Right (+1)
        3: "Right Stick Y", # Up (-1) to Down (+1)
        4: "Left Trigger (ZL)", # -1 (not pressed) to +1 (fully pressed)
        5: "Right Trigger (ZR)" # -1 (not pressed) to +1 (fully pressed)
    },
    "hats": {
        (0, 1): "D-Pad Up",
        (0, -1): "D-Pad Down",
        (-1, 0): "D-Pad Left",
        (1, 0): "D-Pad Right"
    }
}