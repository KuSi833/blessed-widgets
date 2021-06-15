from __future__ import annotations
from blessed import Terminal
from exceptions import PaddingOverflow

from typing import Union, List, Optional, NewType
from abc import ABC, abstractclassmethod
from constants import Direction, HAlignment, VAlignment, ButtonState, Side, WindowState


def fill_rectangle(window: Window, rectangle: Rectangle, color):
    command = ''
    command += color

    for row in range(rectangle.get_edge(Side.BOTTOM), rectangle.get_edge(Side.TOP) + 1):
        command += window.move_xy(Point(rectangle.get_edge(Side.LEFT), row))
        command += " " * rectangle.get_width()

    command += window.term.normal
    print(command)


def align_text_in_rectangle(rectangle: Rectangle, text: str,
                            padding: List[int],
                            h_align: HAlignment, v_align: VAlignment
                            ) -> tuple[int, int, str]:

    max_text_len = rectangle.get_width() - (padding[1] + padding[3])
    text = text[:max_text_len]

    if h_align is HAlignment.LEFT:
        text_start_x = rectangle.get_edge(Side.LEFT) + padding[3]
    elif h_align is HAlignment.MIDDLE:
        text_start_x = rectangle.get_edge(Side.LEFT) + padding[3] + (rectangle.get_width() // 2) - (len(text) // 2)
    elif h_align is HAlignment.RIGHT:
        text_start_x = rectangle.get_edge(Side.RIGHT) - padding[1] - max_text_len

    if v_align is VAlignment.TOP:
        text_start_y = rectangle.get_edge(Side.TOP) + padding[0]
    elif v_align is VAlignment.MIDDLE:
        text_start_y = rectangle.get_edge(Side.TOP) - padding[0] - (rectangle.get_height() // 2)
    elif v_align is VAlignment.BOTTOM:
        text_start_y = rectangle.get_edge(Side.BOTTOM) + padding[2]

    return text_start_x, text_start_y, text


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Element(ABC):
    def __init__(self, window: Window, p1: Point, p2: Point) -> None:
        super().__init__()
        self.p1 = p1
        self.p2 = p2
        self.window = window


class InteractableElement(Element):
    def __init__(self, window: Window, p1: Point, p2: Point) -> None:
        super().__init__(window, p1, p2)

    @abstractclassmethod
    def toggle_select(self) -> None:
        pass

    @abstractclassmethod
    def get_border(self) -> Rectangle:
        pass


class Rectangle():
    def __init__(self, p1: Point, p2: Point) -> None:
        self.corners = {
            "tl": Point(min(p1.x, p2.x), max(p1.y, p2.y)),
            "tr": Point(max(p1.x, p2.x), max(p1.y, p2.y)),
            "bl": Point(min(p1.x, p2.x), min(p1.y, p2.y)),
            "br": Point(max(p1.x, p2.x), min(p1.y, p2.y))
        }

    def get_edge(self, side: Side) -> int:
        if side is Side.TOP:
            return self.corners["tl"].y
        elif side is Side.RIGHT:
            return self.corners["tr"].x
        elif side is Side.BOTTOM:
            return self.corners["bl"].y
        else:  # LEFT
            return self.corners["bl"].x

    def get_width(self) -> int:
        return self.get_edge(Side.RIGHT) - self.get_edge(Side.LEFT)

    def get_height(self) -> int:
        return self.get_edge(Side.TOP) - self.get_edge(Side.BOTTOM)

    def get_middle_x(self) -> int:
        return self.get_edge(Side.LEFT) + self.get_width() // 2

    def get_middle_y(self) -> int:
        return self.get_edge(Side.BOTTOM) + self.get_height() // 2

    def get_center(self) -> Point:
        return Point(self.get_middle_x(), self.get_middle_y())


class ButtonStyle():
    def __init__(self, bg_color, text_style) -> None:
        self.bg_color = bg_color
        self.text_style = text_style


class Button(InteractableElement):
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
        self.border = Rectangle(p1, p2)
        self.window = window
        self.window.add_element(self)
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
            if self.border.get_width() < self.padding[1] + self.padding[3]:
                raise PaddingOverflow("Ammount of padding on x axis exceeds button width")
            if self.border.get_height() < self.padding[0] + self.padding[2]:
                raise PaddingOverflow("Ammount of padding on y axis exceeds button height")

    def get_border(self) -> Rectangle:
        return self.border

    def toggle_select(self) -> None:
        if self.state is ButtonState.SELECTED:
            self.state = ButtonState.IDLE
        else:
            self.state = ButtonState.SELECTED
        self.draw()

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
        fill_rectangle(self.window, self.border, active_style.bg_color)

        # Alignment
        text_start_x, text_start_y, text = align_text_in_rectangle(
            self.border, self.text, self.padding, self.h_align, self.v_align)

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
        self.window_state = WindowState.VIEW
        self.active_element: Optional[InteractableElement] = None
        # Initialising element field
        self.elements: List[Element] = []

    def add_element(self, element: Element) -> None:
        self.elements.append(element)

    def add_elements(self, *elements: Element) -> None:
        self.elements.extend(elements)

    def get_interactable(self) -> List[InteractableElement]:
        return list(filter(lambda element: issubclass(type(element), InteractableElement), self.elements))

    def move_xy(self, p: Point, home: bool = True) -> str:
        """
        Goes to x, y

        IMPORTANT:
        x = 0 is left side of the screen
        y = 0 is bottom of the screen
        """
        return self.term.move_xy(p.x, self.term.height - p.y - 1)

    def clear(self) -> None:
        print(self.term.clear)

    def get_extreme_element(self, direction: Direction) -> Optional[InteractableElement]:
        extreme_element: Optional[InteractableElement] = None
        if direction is Direction.UP:
            highest_y = 0
            for element in self.get_interactable():
                if element.get_border().get_edge(Side.TOP) >= highest_y:
                    highest_y = element.get_border().get_edge(Side.TOP)
                    extreme_element = element
        elif direction is Direction.RIGHT:
            highest_x = 0
            for element in self.get_interactable():
                if element.get_border().get_edge(Side.RIGHT) >= highest_x:
                    highest_x = element.get_border().get_edge(Side.RIGHT)
                    extreme_element = element
        elif direction is Direction.DOWN:
            lowest_y = float('inf')
            for element in self.get_interactable():
                if element.get_border().get_edge(Side.BOTTOM) <= lowest_y:
                    highest_x = element.get_border().get_edge(Side.BOTTOM)
                    extreme_element = element
        elif direction is Direction.LEFT:
            lowest_x = float('inf')
            for element in self.get_interactable():
                if element.get_border().get_edge(Side.LEFT) <= lowest_x:
                    lowest_x = element.get_border().get_edge(Side.LEFT)
                    extreme_element = element

        return extreme_element

    def find_element(self, direction: Direction) -> Element:
        pass

    def key_event(self, val) -> None:
        if not val:
            pass
        else:
            if self.window_state is WindowState.VIEW:
                self.window_state = WindowState.SELECTION
                if val.is_sequence:
                    if val.name == "KEY_UP":
                        self.active_element = self.get_extreme_element(Direction.UP)
                    elif val.name == "KEY_RIGHT":
                        self.active_element = self.get_extreme_element(Direction.RIGHT)
                    elif val.name == "KEY_DOWN":
                        self.active_element = self.get_extreme_element(Direction.DOWN)
                    elif val.name == "KEY_LEFT":
                        self.active_element = self.get_extreme_element(Direction.LEFT)
                    elif val.name == "KEY_ESCAPE":
                        self.window_state = WindowState.VIEW

                    if self.active_element is not None:
                        self.active_element.toggle_select()
            else:
                if False:
                    if val.is_sequence:
                        if val.name == "KEY_UP":
                            self.active_element = self.get_extreme_element(Direction.UP)
                        elif val.name == "KEY_RIGHT":
                            self.active_element = self.get_extreme_element(Direction.RIGHT)
                        elif val.name == "KEY_DOWN":
                            self.active_element = self.get_extreme_element(Direction.DOWN)
                        elif val.name == "KEY_LEFT":
                            self.active_element = self.get_extreme_element(Direction.LEFT)
                        elif val.name == "KEY_ESCAPE":
                            self.window_state = WindowState.VIEW

                        self.active_element.toggle_select()
                    elif val:
                        pass

    def loop(self):
        with self.term.cbreak():
            val = ''
            while val.lower() != 'q':
                val = self.term.inkey(timeout=3)
                self.key_event(val)
