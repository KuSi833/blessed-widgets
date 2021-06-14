from __future__ import annotations
from typing import Union, List, Optional, NewType
from blessed import Terminal
from abc import ABC

from colorama import Style
from helpers import Point, key_coordinates, align_text_in_square
from constants import HAlignment, VAlignment, ButtonState, TextStyle
from exceptions import PaddingOverflow


Color = NewType('Color', str)


class Element(ABC):
    def __init__(self, window: Window, p1: Point, p2: Point) -> None:
        super().__init__()
        self.window = window
        self.p1 = p1
        self.p2 = p2


class Square(Element):
    def __init__(self, window: Window, p1: Point, p2: Point, color) -> None:
        super().__init__(window, p1, p2)
        self.color = color
        self.start_x, self.end_x, self.start_y, self.end_y = key_coordinates(self.p1, self.p2)
        self.height = self.end_y - self.start_y + 1
        self.width = self.end_x - self.start_x + 1

    def draw(self):
        command = ''
        command += self.color

        for row in range(self.start_y, self.end_y + 1):
            command += self.window.term.move_xy(self.start_x, row)
            command += " " * self.width

        command += self.window.term.normal
        print(command)


class ButtonStyle():
    def __init__(self, bg_color: Color, text_style) -> None:
        self.bg_color = bg_color
        self.text_style = text_style


class Button(Element):
    def __init__(self, window: Window, p1: Point, p2: Point, style: ButtonStyle,
                 text: Optional[str] = None,
                 h_align: Optional[HAlignment] = HAlignment.MIDDLE,
                 v_align: Optional[VAlignment] = VAlignment.MIDDLE,
                 padding: Optional[tuple[int, int, int, int]] = None,
                 disabled_style: Optional[ButtonState] = None,
                 selected_style: Optional[ButtonState] = None,
                 clicked_style: Optional[ButtonState] = None,
                 ) -> None:
        super().__init__(window, p1, p2)
        self.window = window
        self.p1 = p1
        self.p2 = p2
        self.text = text
        self.h_align = h_align
        self.v_align = v_align
        self.padding = padding
        self.state = ButtonState.IDLE

        # Styles
        self.style = style
        self.disabled_style = disabled_style
        self.selected_style = selected_style
        self.clicked_style = clicked_style

        # Additional fields
        self.start_x, self.end_x, self.start_y, self.end_y = key_coordinates(self.p1, self.p2)
        self.width = self.end_x - self.start_x
        self.height = self.end_y - self.start_y
        self.middle_x = self.width // 2
        self.middle_y = self.height // 2

        # Padding
        if self.padding is None:
            self.padding = [0] * 4
        else:  # Padding overflow checking
            if self.width < self.padding[1] + self.padding[3]:
                raise PaddingOverflow("Ammount of padding on x axis exceeds button width")
            if self.height < self.padding[0] + self.padding[2]:
                raise PaddingOverflow("Ammount of padding on y axis exceeds button height")

        self.square = Square(self.window, self.p1, self.p2, style.bg_color)

    def get_style(self) -> ButtonStyle:
        if self.state is ButtonState.IDLE:
            return self.style
        elif self.state is ButtonState.DISABLED:
            return self.disabled_style
        elif self.state is ButtonState.CLICKED:
            return self.clicked_style
        elif self.state is ButtonState.SELECTED:
            return self.selected_style

    def draw(self):
        active_style = self.get_style()

        # Update square
        self.square.color = active_style.bg_color
        self.square.draw()
        
        # Alignment
        text_start_x, text_start_y, text = align_text_in_square(
            self.p1, self.p2, self.text, self.padding, self.h_align, self.v_align)

        command = ''.join((
            self.window.term.move_xy(text_start_x, text_start_y),
            active_style.text_style,
            active_style.bg_color,
            text,
            self.window.term.normal
        ))
        print(command)


class Window():
    def __init__(self, term: Terminal) -> None:
        self.term = term

        # Initialising element field
        self.elements: List[Element] = []

    def add_element(self, element: Element) -> None:
        self.elements.append(element)

    def add_elements(self, *elements: Element) -> None:
        self.elements.extend(elements)

    def clear(self):
        print(self.term.clear)
