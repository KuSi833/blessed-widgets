from __future__ import annotations
from typing import Union, List, Optional
from blessed import Terminal
from abc import ABC
from helpers import Point, key_coordinates, align_text_in_square
from constants import HAlignment, VAlignment
from exceptions import PaddingOverflow


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


class Button(Element):
    def __init__(self, window: Window, p1: Point, p2: Point,
                 text: Optional[str] = None,
                 h_align: Optional[HAlignment] = HAlignment.MIDDLE,
                 v_align: Optional[VAlignment] = VAlignment.MIDDLE,
                 padding: Optional[tuple[int, int, int, int]] = None,
                 text_color=None, bg_color=None) -> None:
        super().__init__(window, p1, p2)
        self.window = window
        self.p1 = p1
        self.p2 = p2
        self.text = text
        self.h_align = h_align
        self.v_align = v_align
        self.padding = padding
        self.text_color = text_color
        self.bg_color = bg_color

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

        # Optional coloring
        if text_color is None:
            self.text_color = self.window.term.white
        if bg_color is None:
            self.bg_color = self.window.term.normal
        self.square = Square(self.window, self.p1, self.p2, self.bg_color)

    def draw(self):
        self.square.draw()
        text_start_x, text_start_y, text = align_text_in_square(
            self.p1, self.p2, self.text, self.padding, self.h_align, self.v_align)
        command = ''
        command = ''.join((
            self.window.term.move_xy(text_start_x, text_start_y),
            self.text_color,
            self.bg_color,
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
