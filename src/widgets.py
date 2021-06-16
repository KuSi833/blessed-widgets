from __future__ import annotations
from blessed import Terminal
from exceptions import PaddingOverflow, RectangleTooSmall
import numpy as np

from typing import Union, List, Optional, NewType
from abc import ABC, abstractclassmethod
from helpers import gaussian
from constants import (
    BorderStyle, Direction, HAlignment, VAlignment, ButtonState,
    Side, WindowState, MAX_ANGLE)


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
        self.window.add_element(self)

    @abstractclassmethod
    def draw(self) -> None:
        pass


class Interactable(ABC):
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
        self.bg_color = None
        self.border_color = None
        self.border_style = None
        self.text = None
        self.text_style = None
        self.padding = [0] * 4
        self.h_align = None
        self.v_align = None

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

    def add_bg_color(self, color) -> None:
        self.bg_color = color

    def add_border(self, border_style: BorderStyle, color: Optional[str] = None) -> None:
        self.border_style = border_style
        self.border_color = color

    def insert_text(self, text, text_style: Optional[str] = None, padding: Optional[List[int]] = None,
                    h_align: Optional[HAlignment] = HAlignment.MIDDLE,
                    v_align: Optional[VAlignment] = VAlignment.MIDDLE) -> None:
        self.text = text
        self.text_style = text_style
        self.padding = padding
        self.h_align = h_align
        self.v_align = v_align

    def draw(self, window: Window):
        command = ''
        if self.bg_color:
            command += self.bg_color

        # Color and border
        if self.border_style:
            if self.get_width() < 2 or self.get_height() < 2:
                raise RectangleTooSmall("Unable to fit border on such small rectangle, must be at least 2x2")
            else:
                if self.border_color:
                    command += self.border_color
                for row in range(self.get_edge(Side.BOTTOM), self.get_edge(Side.TOP) + 1):
                    command += window.move_xy(Point(self.get_edge(Side.LEFT), row))
                    if row == self.get_edge(Side.BOTTOM):
                        if self.border_style is BorderStyle.SINGLE:
                            command += "└" + "─" * (self.get_width() - 2) + "┘"
                        elif self.border_style is BorderStyle.DOUBLE:
                            command += "╚" + "═" * (self.get_width() - 2) + "╝"
                    elif row == self.get_edge(Side.TOP):
                        if self.border_style is BorderStyle.SINGLE:
                            command += "┌" + "─" * (self.get_width() - 2) + "┐"
                        elif self.border_style is BorderStyle.DOUBLE:
                            command += "╔" + "═" * (self.get_width() - 2) + "╗"
                    else:
                        if self.border_style is BorderStyle.SINGLE:
                            command += "│" + " " * (self.get_width() - 2) + "│"
                        elif self.border_style is BorderStyle.DOUBLE:
                            command += "║" + " " * (self.get_width() - 2) + "║"

        else:
            for row in range(self.get_edge(Side.BOTTOM), self.get_edge(Side.TOP) + 1):
                command += window.move_xy(Point(self.get_edge(Side.LEFT), row))
                command += " " * self.get_width()
        print(command)
        window.flush()

        command = ''

        # Text
        if self.text:
            # Text style
            if self.bg_color:
                command += self.bg_color
            if self.text_style:
                command += self.text_style

            # Cut of text if it wont fit
            max_text_len = self.get_width() - (self.padding[1] + self.padding[3])
            text = self.text[:max_text_len]

            # Text alignment
            # Horizontal
            if self.h_align is HAlignment.LEFT:
                text_start_x = self.get_edge(Side.LEFT) + self.padding[3]
            elif self.h_align is HAlignment.MIDDLE:
                text_start_x = self.get_edge(Side.LEFT) + self.padding[3] + (self.get_width() // 2) - (len(text) // 2)
            elif self.h_align is HAlignment.RIGHT:
                text_start_x = self.get_edge(Side.RIGHT) - self.padding[1] - max_text_len
            # Vertical
            if self.v_align is VAlignment.TOP:
                text_start_y = self.get_edge(Side.TOP) + self.padding[0]
            elif self.v_align is VAlignment.MIDDLE:
                text_start_y = self.get_edge(Side.TOP) - self.padding[0] - (self.get_height() // 2)
            elif self.v_align is VAlignment.BOTTOM:
                text_start_y = self.get_edge(Side.BOTTOM) + self.padding[2]

            command += window.move_xy(Point(text_start_x, text_start_y))
            command += text
            print(command)

        window.flush()


class ButtonStyle():
    def __init__(self, bg_color, text_style, border_color=None, border_style: Optional[BorderStyle] = None) -> None:
        self.bg_color = bg_color
        self.text_style = text_style
        self.border_color = border_color
        self.border_style = border_style


class Button(Element, Interactable):
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
        self.border.add_bg_color(color=active_style.bg_color)
        self.border.add_border(border_style=active_style.border_style, color=active_style.border_color)
        self.border.insert_text(text=self.text, text_style=active_style.text_style, padding=self.padding,
                                h_align=self.h_align, v_align=self.v_align)
        self.border.draw(self.window)


class Window():
    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.window_state = WindowState.VIEW
        self.active_element: Optional[Interactable] = None
        # Initialising element field
        self.elements: List[Element] = []
        self.interactable: List[Interactable] = []

    def add_element(self, element: Element) -> None:
        self.elements.append(element)
        if issubclass(type(element), Interactable):
            self.interactable.append(element)

    def add_elements(self, *elements: Element) -> None:
        for element in elements:
            self.add_element(element)

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

    def flush(self) -> None:
        "Resets pointer and color"
        print(self.term.home + self.term.normal)

    def get_extreme_element(self, direction: Direction) -> Optional[Interactable]:
        extreme_element: Optional[Interactable] = None
        if direction is Direction.UP:
            highest_y = 0
            for element in self.interactable:
                if element.get_border().get_edge(Side.TOP) >= highest_y:
                    highest_y = element.get_border().get_edge(Side.TOP)
                    extreme_element = element
        elif direction is Direction.RIGHT:
            highest_x = 0
            for element in self.interactable:
                if element.get_border().get_edge(Side.RIGHT) >= highest_x:
                    highest_x = element.get_border().get_edge(Side.RIGHT)
                    extreme_element = element
        elif direction is Direction.DOWN:
            lowest_y = float('inf')
            for element in self.interactable:
                if element.get_border().get_edge(Side.BOTTOM) <= lowest_y:
                    lowest_y = element.get_border().get_edge(Side.BOTTOM)
                    extreme_element = element
        elif direction is Direction.LEFT:
            lowest_x = float('inf')
            for element in self.interactable:
                if element.get_border().get_edge(Side.LEFT) <= lowest_x:
                    lowest_x = element.get_border().get_edge(Side.LEFT)
                    extreme_element = element

        return extreme_element

    def find_element(self, direction: Direction) -> Interactable:
        active_element_center = self.active_element.get_border().get_center()
        min_wighted_distance = float('inf')
        closest_element: Optional[Interactable] = None
        for element in self.interactable:
            if element != self.active_element:
                element_center = element.get_border().get_center()

                delta_x = element_center.x - active_element_center.x
                delta_y = element_center.y - active_element_center.y
                c = complex(delta_x, delta_y)

                argument = np.angle(c, deg=True)
                if argument < 0:
                    argument += 360

                delta_angle = abs(direction.value - argument)

                if delta_angle > MAX_ANGLE:
                    continue

                distance = np.linalg.norm(np.array((delta_x, delta_y)))

                # Calculating weighted distance
                weighted_distance = distance / gaussian(x=delta_angle / 90, mean=0, std=0.35)

                if weighted_distance < min_wighted_distance:
                    min_wighted_distance = weighted_distance
                    closest_element = element

        return closest_element

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
                direction = None
                next_element = None
                if val.is_sequence:
                    if val.name == "KEY_UP":
                        direction = Direction.UP
                    elif val.name == "KEY_RIGHT":
                        direction = Direction.RIGHT
                    elif val.name == "KEY_DOWN":
                        direction = Direction.DOWN
                    elif val.name == "KEY_LEFT":
                        direction = Direction.LEFT
                    elif val.name == "KEY_ESCAPE" or val.name == "KEY_BACKSPACE":
                        self.window_state = WindowState.VIEW
                        self.active_element.toggle_select()
                    if direction:  # If a key is pressed which gives direction
                        next_element = self.find_element(direction)
                    if next_element:  # If a good next element is found
                        self.active_element.toggle_select()
                        self.active_element = next_element
                        self.active_element.toggle_select()
                elif val:
                    pass

    def loop(self):
        with self.term.cbreak():
            val = ''
            while val.lower() != 'q':
                val = self.term.inkey(timeout=3)
                self.key_event(val)
