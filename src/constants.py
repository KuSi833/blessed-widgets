from enum import Enum, auto, unique


@unique
class HAlignment(Enum):
    LEFT = auto()
    MIDDLE = auto()
    RIGHT = auto()


@unique
class VAlignment(Enum):
    TOP = auto()
    MIDDLE = auto()
    BOTTOM = auto()


@unique
class ButtonState(Enum):
    IDLE = auto()
    DISABLED = auto()
    SELECTED = auto()
    CLICKED = auto()


@unique
class Sides(Enum):
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    LEFT = auto()
