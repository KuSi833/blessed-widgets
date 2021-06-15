from __future__ import annotations
from blessed import Terminal
from exceptions import PaddingOverflow

from typing import Union, List, Optional, NewType
from abc import ABC
from constants import HAlignment, VAlignment, ButtonState, Sides


def align_text_in_square(square: Square, text: str,
                         padding: List[int],
                         h_align: HAlignment, v_align: VAlignment
                         ) -> tuple[int, int, str]:

    max_text_len = square.get_width() - (padding[1] + padding[3])
    text = text[:max_text_len]

    if h_align is HAlignment.LEFT:
        text_start_x = square.get_edge(Sides.LEFT) + padding[3]
    elif h_align is HAlignment.MIDDLE:
        text_start_x = square.get_edge(Sides.LEFT) + padding[3] + (square.get_width() // 2) - (len(text) // 2)
    elif h_align is HAlignment.RIGHT:
        text_start_x = square.get_edge(Sides.RIGHT) - padding[1] - max_text_len

    if v_align is VAlignment.TOP:
        text_start_y = square.get_edge(Sides.TOP) + padding[0]
    elif v_align is VAlignment.MIDDLE:
        text_start_y = square.get_edge(Sides.TOP) - padding[0] - (square.get_height() // 2)
    elif v_align is VAlignment.BOTTOM:
        text_start_y = square.get_edge(Sides.BOTTOM) + padding[2]

    return text_start_x, text_start_y, text


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Element(ABC):
    def __init__(self, window: Window, p1: Point, p2: Point) -> None:
        super().__init__()
        self.window = window
        self.p1 = p1
        self.p2 = p2


class Square(Element):
    def __init__(self, window: Window, p1: Point, p2: Point) -> None:
        super().__init__(window, p1, p2)
        self.corners = {
            "tl": Point(min(p1.x, p2.x), max(p1.y, p2.y)),
            "tr": Point(max(p1.x, p2.x), max(p1.y, p2.y)),
            "bl": Point(min(p1.x, p2.x), min(p1.y, p2.y)),
            "br": Point(max(p1.x, p2.x), min(p1.y, p2.y))
        }

    def get_edge(self, side: Sides) -> int:
        if side is Sides.TOP:
            return self.corners["tl"].y
        elif side is Sides.RIGHT:
            return self.corners["tr"].x
        elif side is Sides.BOTTOM:
            return self.corners["bl"].y
        else:  # LEFT
            return self.corners["bl"].x

    def get_width(self) -> int:
        return self.get_edge(Sides.RIGHT) - self.get_edge(Sides.LEFT)

    def get_height(self) -> int:
        return self.get_edge(Sides.TOP) - self.get_edge(Sides.BOTTOM)

    def get_middle_x(self) -> int:
        return self.get_width() // 2

    def get_middle_y(self) -> int:
        return self.get_height() // 2

    def align_text_in_square(square: Square, text: str,
                             padding: List[int],
                             h_align: HAlignment, v_align: VAlignment
                             ) -> tuple[int, int, str]:

        max_text_len = square.get_width() - (padding[1] + padding[3])
        text = text[:max_text_len]

        if h_align is HAlignment.LEFT:
            text_start_x = square.get_edge(Sides.LEFT) + padding[3]
        elif h_align is HAlignment.MIDDLE:
            text_start_x = square.get_edge(Sides.LEFT) + padding[3] + (square.get_width() // 2) - (len(text) // 2)
        elif h_align is HAlignment.RIGHT:
            text_start_x = square.get_edge(Sides.RIGHT) - padding[1] - max_text_len

        if v_align is VAlignment.TOP:
            text_start_y = square.get_edge(Sides.TOP) + padding[0]
        elif v_align is VAlignment.MIDDLE:
            text_start_y = square.get_edge(Sides.TOP) - padding[0] - (square.get_height() // 2)
        elif v_align is VAlignment.BOTTOM:
            text_start_y = square.get_edge(Sides.BOTTOM) + padding[2]

        return text_start_x, text_start_y, text

    def fill(self, color) -> None:
        command = ''
        command += color

        for row in range(self.get_edge(Sides.BOTTOM), self.get_edge(Sides.TOP) + 1):
            command += self.window.move_xy(Point(self.get_edge(Sides.LEFT), row))
            command += " " * self.get_width()

        command += self.window.term.normal
        print(command)


class ButtonStyle():
    def __init__(self, bg_color, text_style) -> None:
        self.bg_color = bg_color
        self.text_style = text_style


class Button(Element):
    def __init__(self, window: Window, p1: Point, p2: Point, style: ButtonStyle,
                 text: Optional[str] = None,
                 h_align: Optional[HAlignment] = HAlignment.MIDDLE,
                 v_align: Optional[VAlignment] = VAlignment.MIDDLE,
                 padding: Optional[List[int]] = None,
                 disabled_style: Optional[ButtonStyle] = None,
                 selected_style: Optional[ButtonStyle] = None,
                 clicked_style: Optional[ButtonStyle] = None,
                 ) -> None:
        super().__init__(window, p1, p2)
        self.square = Square(self.window, self.p1, self.p2)
        self.window = window
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

        # Padding
        if self.padding is None:
            self.padding = [0] * 4
        else:  # Padding overflow checking
            if self.square.get_width() < self.padding[1] + self.padding[3]:
                raise PaddingOverflow("Ammount of padding on x axis exceeds button width")
            if self.square.get_height() < self.padding[0] + self.padding[2]:
                raise PaddingOverflow("Ammount of padding on y axis exceeds button height")

    def get_style(self) -> ButtonStyle:
        if self.state is ButtonState.IDLE:
            return self.style
        elif self.state is ButtonState.DISABLED:
            if self.disabled_style is not None:
                return self.disabled_style
            else:
                return self.style
        elif self.state is ButtonState.CLICKED:
            if self.clicked_style is not None:
                return self.clicked_style
            else:
                return self.style
        elif self.state is ButtonState.SELECTED:
            if self.selected_style is not None:
                return self.selected_style
            else:
                return self.style

    def draw(self):
        active_style = self.get_style()

        # Update square
        self.square.fill(active_style.bg_color)

        # Alignment
        text_start_x, text_start_y, text = align_text_in_square(
            self.square, self.text, self.padding, self.h_align, self.v_align)

        command = ''.join((
            self.window.move_xy(Point(text_start_x, text_start_y)),
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

    def move_xy(self, p: Point):
        """
        Goes to x, y

        IMPORTANT:
        x = 0 is left side of the screen
        y = 0 is bottom of the screen
        """
        return self.term.move_xy(p.x, self.term.height - p.y - 1)

    def clear(self):
        print(self.term.clear)
