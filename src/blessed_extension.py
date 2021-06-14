from blessed import Terminal
from abc import ABC, abstractclassmethod
from typing import NewType
from enum import Enum, auto

Color = NewType('Color', int)


class GuiObject(ABC):
    def __init__(self, term: Terminal) -> None:
        super().__init__()
        self.term = term

    @abstractclassmethod
    def __str__(self) -> str:
        pass

class GuiVisualObject(GuiObject):
    def __init__(self, term: Terminal, x: int, y: int, h: int, w: int) -> None:
        super().__init__(term, x, y, h, w)
        self.x = x
        self.y = y
        self.h = h
        self.w = w


class VAlignment(Enum):
    TOP = auto


class ButtonStyle(GuiObject):
    def __init__(self, term: Terminal, text_color: Color, bg_color: Color) -> None:
        super().__init__(term)
        self.text_color = text_color
        self.bg_color = bg_color


class Window:
    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.elements = []

        


class Button(GuiObject):
    # TODO: add states for: highlighted, pressed
    def __init__(self, term: Terminal, x: int, y: int, h: int = None, w: int = None,
                 text: str = "", h_align
                 base: ButtonStyle, selected: ButtonStyle, clicked: ButtonStyle) -> None:
        super().__init__(term, x, y, h, w)
        self.text = text
        self.base = base,
        self.selected = selected
        self.clicked = clicked

    def __str__(self) -> str:
        command = ''.join((
            self.term.move_xy(self.x, self.y),
            self.text_color,
            self.bg,
            self.text,
            self.term.normal
        ))
        return command
