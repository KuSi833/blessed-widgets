from __future__ import annotations
from blessed import Terminal
from exceptions import BorderOutOfBounds, InvalidElement, PaddingOverflow, RectangleTooSmall
import numpy as np

from typing import Callable, Union, List, Optional, NewType
from abc import ABC, abstractclassmethod
from helpers import gaussian
from constants import (
    BorderStyle, Direction, HAlignment, VAlignment, ButtonState,
    Side, WindowState, MAX_ANGLE)
from functools import partial


class Point():
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


class Element(ABC):
    def __init__(self, parent: Parent, p1: Point, p2: Point) -> None:
        self.border = Rectangle(p1, p2)
        self.parent = parent
        self.parent.add_element(self)
        self.window = parent.get_window()

    def get_window(self) -> Window:
        return self.parent.get_window()

    def get_border(self) -> Rectangle:
        return self.border

    def show(self) -> None:
        self.visible = True
        self.draw()

    def hide(self) -> None:
        self.visible = False
        self.clear()

    def toggle_visible(self) -> None:
        if self.visible:
            self.visible = False
            self.clear()
        else:
            self.visible = True
            self.draw()

    @abstractclassmethod
    def draw(self) -> None:
        pass

    def clear(self) -> None:
        command = self.window.term.normal
        for row in range(self.get_border().get_edge(Side.BOTTOM), self.get_border().get_edge(Side.TOP) + 1):
            command += self.window.move_xy(Point(self.get_border().get_edge(Side.LEFT), row))
            command += " " * self.get_border().get_width()
        print(command)


class Interactable(ABC):
    @abstractclassmethod
    def toggle_select(self) -> None:
        pass

    @abstractclassmethod
    def click(self) -> None:
        pass


class Frame(Element):
    def __init__(self, parent: Parent, p1: Point, p2: Point) -> None:
        super().__init__(parent, p1, p2)
        self.elements: List[Element] = []
        self.visible = True
        parent.add_element(self)

    def check_out_of_bounds(self, element: Element) -> bool:
        if element.get_border().get_edge(Side.LEFT) < self.get_border().get_edge(Side.LEFT):
            return True
        elif element.get_border().get_edge(Side.BOTTOM) < self.get_border().get_edge(Side.BOTTOM):
            return True
        elif element.get_border().get_edge(Side.TOP) > self.get_border().get_edge(Side.TOP):
            return True
        elif element.get_border().get_edge(Side.RIGHT) > self.get_border().get_edge(Side.RIGHT):
            return True
        return False

    def add_element(self, element: Element) -> None:
        if self.check_out_of_bounds(element):
            raise BorderOutOfBounds("Child coordinates are out of bounds of the parent")
        self.elements.append(element)

    def add_elements(self, *elements: Element) -> None:
        for element in elements:
            self.add_element(element)

    def get_all_elements(self, element_filter: Optional[Callable] = None) -> List[Element]:
        elements = []
        for element in self.elements:
            if isinstance(element, Frame):
                elements.extend(element.get_all_elements(element_filter))
            else:
                if element_filter:
                    if element_filter(element):
                        elements.append(element)
                else:
                    elements.append(element)
        return elements

    def draw(self) -> None:
        if self.visible:
            for element in self.elements:
                element.draw()


class Window():
    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.window_state = WindowState.VIEW
        self.active_element: Optional[Interactable] = None
        Frame(self, Point(0, 0), Point(self.term.width, self.term.height))

    def get_window(self) -> Window:
        return self

    def draw(self) -> None:
        self.clear()
        self.mainframe.draw()

    def move_xy(self, p: Point, invert_y: bool = True) -> str:  # TODO issue 17
        if invert_y:
            p.y = self.term.height - p.y - 1
        return self.term.move_xy(p.x, p.y)

    def clear(self) -> None:
        print(self.term.clear)

    def flush(self) -> None:
        "Resets pointer and color"
        print(self.term.home + self.term.normal)

    def get_all_elements(self, element_filter: Optional[Callable] = None) -> List[Element]:
        return self.mainframe.get_all_elements(element_filter)

    def get_all_interactive(self):
        return self.get_all_elements(lambda element: isinstance(element, Interactable))

    def get_extreme_element(self, direction: Direction) -> Optional[Interactable]:
        extreme_element: Optional[Interactable] = None
        if direction is Direction.UP:
            highest_y = 0
            for element in self.get_all_interactive():
                if element.get_border().get_edge(Side.TOP) >= highest_y:
                    highest_y = element.get_border().get_edge(Side.TOP)
                    extreme_element = element
        elif direction is Direction.RIGHT:
            highest_x = 0
            for element in self.get_all_interactive():
                if element.get_border().get_edge(Side.RIGHT) >= highest_x:
                    highest_x = element.get_border().get_edge(Side.RIGHT)
                    extreme_element = element
        elif direction is Direction.DOWN:
            lowest_y = float('inf')
            for element in self.get_all_interactive():
                if element.get_border().get_edge(Side.BOTTOM) <= lowest_y:
                    lowest_y = element.get_border().get_edge(Side.BOTTOM)
                    extreme_element = element
        elif direction is Direction.LEFT:
            lowest_x = float('inf')
            for element in self.get_all_interactive():
                if element.get_border().get_edge(Side.LEFT) <= lowest_x:
                    lowest_x = element.get_border().get_edge(Side.LEFT)
                    extreme_element = element

        return extreme_element

    def find_element(self, direction: Direction) -> Optional[Interactable]:
        if self.active_element is None:
            raise TypeError("Unable to find element if actie_element isn't set")
        else:
            assert(isinstance(self.active_element, Element))
            active_element_center = self.active_element.get_border().get_center()
            min_wighted_distance = float('inf')
            closest_element: Optional[Interactable] = None
            for element in self.get_all_interactive():
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

    def add_element(self, element: Element) -> None:
        "Allows for only one element to be added, which is a single Frame"
        if not isinstance(element, Frame):
            raise InvalidElement("Only a single element of type Frame can be added to a Window")
        self.mainframe = element

    def key_event(self, val) -> None:
        if not val:
            pass
        else:
            if self.window_state is WindowState.VIEW:
                # Active element can't be set if WindowState.VIEW
                assert(self.active_element is None)
                if val.is_sequence:
                    if val.name == "KEY_UP":
                        self.active_element = self.get_extreme_element(Direction.UP)
                    elif val.name == "KEY_RIGHT":
                        self.active_element = self.get_extreme_element(Direction.RIGHT)
                    elif val.name == "KEY_DOWN":
                        self.active_element = self.get_extreme_element(Direction.DOWN)
                    elif val.name == "KEY_LEFT":
                        self.active_element = self.get_extreme_element(Direction.LEFT)

                    if self.active_element is not None:
                        self.active_element.toggle_select()
                        self.window_state = WindowState.SELECTION
            else:
                # Active element must be set if WindowState.SELECTION
                assert(self.active_element is not None)
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
                    elif val.name == "KEY_ENTER":
                        self.active_element.click()
                    elif val.name == "KEY_ESCAPE" or val.name == "KEY_BACKSPACE":
                        self.window_state = WindowState.VIEW
                        self.active_element.toggle_select()
                        self.active_element = None
                    if direction:  # If a key is pressed which gives direction
                        # If a direction is given the active element couldn't have been set to None
                        assert(self.active_element is not None)
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


Parent = Union[Frame, Window]


class Rectangle():
    def __init__(self, p1: Point, p2: Point) -> None:
        self.corners = {
            "tl": Point(min(p1.x, p2.x), max(p1.y, p2.y)),
            "tr": Point(max(p1.x, p2.x), max(p1.y, p2.y)),
            "bl": Point(min(p1.x, p2.x), min(p1.y, p2.y)),
            "br": Point(max(p1.x, p2.x), min(p1.y, p2.y))
        }
        self.bg_color = None
        self.border_color: Optional[str] = None
        self.border_style: Optional[BorderStyle] = None
        self.text = None
        self.text_style: Optional[str] = None
        self.padding: Optional[List[int]] = None
        self.h_align: Optional[HAlignment] = None
        self.v_align: Optional[VAlignment] = None

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

    def insert_text(self, text, text_style: Optional[str] = None, padding: Optional[List[int]] = [0] * 4,
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


class RectangleStyle():
    def __init__(self, bg_color: Optional[str] = None, text_style: Optional[str] = None,
                 border_color: Optional[str] = None, border_style: Optional[BorderStyle] = None) -> None:
        "Leave all parameters empty for default style (no background, no border, white text)"
        self.bg_color = bg_color
        self.text_style = text_style
        self.border_color = border_color
        self.border_style = border_style


class Label(Element):
    def __init__(self, parent: Parent, p1: Point, p2: Point,
                 text: Optional[str] = None,
                 style: Optional[RectangleStyle] = None,
                 h_align: Optional[HAlignment] = HAlignment.MIDDLE,
                 v_align: Optional[VAlignment] = VAlignment.MIDDLE,
                 padding: Optional[List[int]] = None,
                 ) -> None:
        super().__init__(parent, p1, p2)
        self.text = text
        self.h_align = h_align
        self.v_align = v_align
        self.set_padding(padding)
        self.set_style(style)
        self.state = ButtonState.IDLE

    def set_padding(self, padding: Optional[List[int]]):
        "If no padding is given a default [0, 0, 0, 0] is set"
        if padding is None:
            self.padding = [0] * 4
        else:  # Padding overflow checking
            if self.border.get_width() < padding[1] + padding[3]:
                raise PaddingOverflow("Ammount of padding on x axis exceeds button width")
            if self.border.get_height() < padding[0] + padding[2]:
                raise PaddingOverflow("Ammount of padding on y axis exceeds button height")
            self.padding = padding

    def construct_default_style(self, style: Optional[RectangleStyle] = None) -> RectangleStyle:
        if style is None:
            # Default style
            return RectangleStyle(bg_color=self.window.term.normal, text_style=self.window.term.white,
                                  border_color=None, border_style=None)
        else:  # If style is given fill empty fields with default values
            if style.bg_color:
                bg_color = style.bg_color
            else:
                bg_color = self.window.term.normal  # Defualt bg_color
            if style.text_style:
                text_style = style.text_style
            else:
                text_style = self.window.term.white  # Default text_style
            return RectangleStyle(bg_color=bg_color, text_style=text_style,
                                  border_color=style.border_color, border_style=style.border_style)

    def set_style(self, style: Optional[RectangleStyle]) -> None:
        "If no style is given a default style is constructed"
        self.style = self.construct_default_style(style)

    def get_style(self) -> RectangleStyle:
        return self.style

    def draw(self):
        active_style = self.get_style()
        self.border.add_bg_color(color=active_style.bg_color)
        self.border.add_border(border_style=active_style.border_style, color=active_style.border_color)
        self.border.insert_text(text=self.text, text_style=active_style.text_style, padding=self.padding,
                                h_align=self.h_align, v_align=self.v_align)
        self.border.draw(self.window)


class Entry(Label, Interactable):
    def __init__(
            self, parent: Parent, p1: Point, p2: Point, default_text: Optional[str] = None,
            style: Optional[RectangleStyle] = None,
            h_align: Optional[HAlignment] = HAlignment.LEFT,
            v_align: Optional[VAlignment] = VAlignment.TOP,
            padding: Optional[List[int]] = None) -> None:
        super().__init__(parent, p1, p2, text=default_text, style=style,
                         h_align=h_align, v_align=v_align, padding=padding)
        self.text = ''

    def construct_default_style(self, style: Optional[RectangleStyle] = None) -> RectangleStyle:
        "Entry default style"
        if style is None:
            # Default style
            return RectangleStyle(bg_color=self.window.term.normal, text_style=self.window.term.white,
                                  border_color=self.window.term.white, border_style=BorderStyle.SINGLE)
        else:  # If style is given fill empty fields with default values
            if style.bg_color:
                bg_color = style.bg_color
            else:
                bg_color = self.window.term.normal  # Defualt bg_color
            if style.text_style:
                text_style = style.text_style
            else:
                text_style = self.window.term.white  # Default text_style
            if style.border_color:
                border_color = style.border_color
            else:
                border_color = self.window.term.white
            if style.border_style:
                border_style = style.border_style
            else:
                border_style = BorderStyle.SINGLE
            return RectangleStyle(bg_color=bg_color, text_style=text_style,
                                  border_color=border_color, border_style=border_style)


class Button(Label, Interactable):
    def __init__(
            self, parent: Parent, p1: Point, p2: Point, command: Callable,
            style: Optional[RectangleStyle] = None, text: Optional[str] = None,
            h_align: Optional[HAlignment] = HAlignment.MIDDLE, v_align: Optional[VAlignment] = VAlignment.MIDDLE,
            padding: Optional[List[int]] = None,
            disabled_style: Optional[RectangleStyle] = None, selected_style: Optional[RectangleStyle] = None,
            clicked_style: Optional[RectangleStyle] = None) -> None:
        super().__init__(parent, p1, p2, style=style, text=text, h_align=h_align, v_align=v_align, padding=padding)
        self.state = ButtonState.IDLE
        self.on_click(command)

        # Styles
        self.set_style(disabled_style, ButtonState.DISABLED)
        self.set_style(selected_style, ButtonState.SELECTED)
        self.set_style(clicked_style, ButtonState.CLICKED)

    def on_click(self, command: Callable) -> None:
        self.command = command

    def toggle_select(self) -> None:
        if self.state is ButtonState.SELECTED:
            self.state = ButtonState.IDLE
        else:
            self.state = ButtonState.SELECTED
        self.draw()

    def click(self) -> None:
        self.command()

    def set_style(self, style: Optional[RectangleStyle], state: Optional[ButtonState] = ButtonState.IDLE) -> None:
        "If no style is specified default values will be used"
        if state is ButtonState.IDLE:
            self.style = super().construct_default_style(style)
        elif state is ButtonState.DISABLED:
            self.disabled_style = super().construct_default_style(style)
        elif state is ButtonState.CLICKED:
            self.clicked_style = super().construct_default_style(style)
        elif state is ButtonState.SELECTED:
            self.selected_style = super().construct_default_style(style)

    def get_style(self) -> RectangleStyle:
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
