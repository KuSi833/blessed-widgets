from blessed import Terminal
from abc import ABC, abstractclassmethod
from typing import NewType

Color = NewType('Color', int)


class GuiObject(ABC):
    def __init__(self, term: Terminal, x: int, y: int, h: int, w: int) -> None:
        super().__init__()
        self.term = term
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    @abstractclassmethod
    def __str__(self) -> str:
        pass


class Button(GuiObject):
    # TODO: add states for: highlighted, pressed
    def __init__(self, term: Terminal, x: int, y: int, h: int = 1, w: int = 1,
                 text: str = "", text_color: Color = None, bg: Color = None,
                 border_style=None, border_color: Color = None) -> None:
        super().__init__(term, x, y, h, w)
        self.text = text
        self.text_color = text_color
        self.bg = bg
        self.border_style = border_color
        self.border_color = border_color

    def __str__(self) -> str:
        command = ''.join((
            self.term.move_xy(self.x, self.y),
            self.text_color,
            self.bg,
            self.text,
            self.term.normal
        ))
        return command

