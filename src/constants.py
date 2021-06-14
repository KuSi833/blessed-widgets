from enum import Enum, auto


class HAlignment(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


class VAlignment(Enum):
    TOP = auto()
    MIDDLE = auto()
    BOTTOM = auto()


class ButtonState(Enum):
    IDLE = auto()
    DISABLED = auto()
    SELECTED = auto()
    CLICKED = auto()
