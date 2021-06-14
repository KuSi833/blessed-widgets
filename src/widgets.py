from __future__ import annotations
from typing import Union, List, Optional
from blessed import Terminal
from abc import ABC
from helpers import Point, start_coordinates


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
        self.start_x, self.end_x, self.start_y, self.end_y = start_coordinates(self.p1, self.p2)
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
    def __init__(self, window: Window, p1: Point, text: Optional[str] = None,
                 p2: Optional[Point] = None, **kwargs) -> None:
        super().__init__(window, p1, p2)
        self.window = window
        self.p1 = p1
        if text:
            self.text = text
        if p2:
            self.p2 = p2

    def draw(self):
        command = ''.join((
            self.window.term.move_xy(self.p1.x, self.p1.y),
            self.text,
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
        print(self.term.home + self.term.clear)
