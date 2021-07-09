# std
from __future__ import annotations
from abc import ABC, abstractclassmethod
from typing import Callable, Text, Tuple, Union, List, Optional

# 3rd party
import numpy as np
from math import degrees, atan2
from blessed import Terminal

# local
from .exceptions import (BorderOutOfBounds, CellOutOfBounds, ElementNotPlaced,
                         InvalidAttributes, InvalidElement, InvalidLayout,
                         PaddingOverflow, RectangleTooSmall)
from .helpers import gaussian, getFirstAssigned
from .constants import (BorderStyle, Direction, HAlignment, Layout, Response,
                        VAlignment, State, Side, WindowState, MAX_ANGLE)


class Point():

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __add__(self, p: Point) -> Point:
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p: Point) -> Point:
        return Point(self.x - p.x, self.y - p.y)

    def __str__(self) -> str:
        return f"({self.x},{self.y})"


class Element(ABC):

    def __init__(self, parent: Parent, width: int, height: int) -> None:
        self.border: Optional[Box] = None
        self.parent = parent
        self.parent.addElement(self)
        self.width = width
        self.height = height
        self.active = False

    def getWidth(self) -> int:
        return self.width

    def getHeight(self) -> int:
        return self.height

    def place(self, x: int, y: int) -> None:
        "Works with Layout.ABSOLUTE"
        if not isinstance(self.parent, AbsoluteFrame):
            raise InvalidLayout("Frame is not of type AbsoluteFrame")
        assert (isinstance(self.parent, AbsoluteFrame))
        self.border = self.parent.placeElement(self, x, y)
        self.activate()

    def grid(self,
             column: int,
             row: int,
             rowspan: int = 1,
             columnspan: int = 1,
             padx: int = 0,
             pady: int = 0) -> None:
        if not isinstance(self.parent, GridFrame):
            raise InvalidLayout("Frame is not of type GridFrame")
        assert (isinstance(self.parent, GridFrame))
        self.border = self.parent.placeElement(element=self,
                                               padx=padx,
                                               pady=pady,
                                               row=row,
                                               column=column,
                                               rowspan=rowspan,
                                               columnspan=columnspan)
        self.activate()

    def getWindow(self) -> Window:
        return self.parent.getWindow()

    def getBorder(self) -> Box:
        if self.border is None:
            raise ElementNotPlaced("Element must be placed before drawing")
        else:
            # If it was None an error would've been raised
            # assert(self.border is not None)
            return self.border

    def isActive(self) -> bool:
        return self.active

    def activate(self, draw: bool = True) -> None:
        self.active = True
        if draw:
            self.draw()

    def deactivate(self) -> None:
        self.active = False
        self.clear()

    def toggle(self) -> None:
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def isPlaced(self) -> bool:
        if self.border:
            return True
        return False

    def raiseIfNotPlaced(self) -> None:
        if not self.isPlaced():
            raise ElementNotPlaced(
                "Element must first be placed on parent frame")

    @abstractclassmethod
    def draw(self) -> None:
        pass

    def clear(self) -> None:
        self.raiseIfNotPlaced()
        # Remove after MainFrame solution TODO
        command = ''
        if isinstance(self.parent, Frame):
            bg_color = self.parent.getStyle().bg_color
            if bg_color:
                command += bg_color
        else:
            command += self.getWindow().term.normal
        # Remove after MainFrame solution
        for row in range(self.getBorder().getEdge(Side.TOP),
                         self.getBorder().getEdge(Side.BOTTOM) + 1):
            command += self.getWindow().moveXY(
                Point(self.getBorder().getEdge(Side.LEFT), row))
            command += " " * self.getBorder().getWidth()
        print(command)

    def remove(self) -> None:
        self.deactivate()
        self.parent.removeElement(self)
        self = None


class HasText(ABC):

    def __init__(self, text: Optional[str], padding: List[int],
                 h_align: HAlignment, v_align: VAlignment, width: int,
                 height: int) -> None:
        self.setText(text)
        self.h_align = h_align
        self.v_align = v_align
        self.setPadding(padding, width, height)

    def setText(self, text: Optional[str]) -> None:
        self.text = text

    def setPadding(self, padding: List[int], width: int, height: int) -> None:
        if width < padding[1] + padding[3]:
            raise PaddingOverflow(
                "Ammount of padding on x axis exceeds button width")
        if height < padding[0] + padding[2]:
            raise PaddingOverflow(
                "Ammount of padding on y axis exceeds button height")
        self.padding = padding


class Visible(Element):  # Frame vs Label

    def __init__(
            self,
            parent: Parent,
            width: int,
            height: int,  # Element
            style: BoxStyle = None) -> None:  # Visible
        super().__init__(parent, width, height)
        self.setStyle(style)
        self.state = State.IDLE

    @abstractclassmethod
    def constructDefaultStyle(
            self, style: Optional[BoxStyle]) -> BoxStyle:
        pass

    def constructDefaultStyleTemplate(
        self,
        default_style: BoxStyle,
        style: Optional[BoxStyle] = None,
        inheritance_vector: Tuple[bool, bool, bool,
                                  bool] = (False, False, False, False)
    ) -> BoxStyle:
        """
        Constructs default style in the following order of priority in descending order:
        1. Given style
        2. Inherited style
        3. Default style
        Inheritence vector controls which features are inherited (1 for true, 0 for false)
        inheritence_vector is of form (bg_color, text_style, border_color, border_style)
        """
        if style is None:
            style = BoxStyle()
        inheritanceStyle = BoxStyle()
        if not isinstance(self.parent, Window):  # TODO: Make MainFrame class?
            parentStyle = self.parent.getStyle()
            # Controls which features are inherited
            if inheritance_vector[0]:
                inheritanceStyle.bg_color = parentStyle.bg_color
            if inheritance_vector[1]:
                inheritanceStyle.text_style = parentStyle.text_style
            if inheritance_vector[2]:
                inheritanceStyle.border_color = parentStyle.border_color
            if inheritance_vector[3]:
                inheritanceStyle.border_style = parentStyle.border_style

        bg_color: Optional[str] = getFirstAssigned(
            [style.bg_color, inheritanceStyle.bg_color],
            default=default_style.bg_color)
        text_style: Optional[str] = getFirstAssigned(
            [style.text_style, inheritanceStyle.text_style],
            default=default_style.text_style)
        border_color: Optional[str] = getFirstAssigned(
            [style.border_color, inheritanceStyle.border_color],
            default=default_style.border_color)
        border_style: Optional[BorderStyle] = getFirstAssigned(
            [style.border_style], default=default_style.border_style)
        return BoxStyle(bg_color=bg_color,
                              text_style=text_style,
                              border_color=border_color,
                              border_style=border_style)

    def setStyle(self, style: Optional[BoxStyle]) -> None:
        self.style = self.constructDefaultStyle(style)

    def getStyle(self) -> BoxStyle:
        return self.style


class Interactable(Visible):

    def __init__(
            self,
            parent: Parent,
            width: int,
            height: int,  # Element
            style: BoxStyle = None,  # Visible
            selected_style: BoxStyle = None,
            clicked_style: BoxStyle = None,
            disabled_style: BoxStyle = None) -> None:
        super().__init__(parent, width, height, style)  # Visible
        self.setSelectedStyle(selected_style)
        self.setClickedStyle(clicked_style)
        self.setDisabledStyle(disabled_style)
        self.navigation_override: dict[Direction, Optional[Interactable]] = {
            Direction.UP: None,
            Direction.DOWN: None,
            Direction.LEFT: None,
            Direction.RIGHT: None
        }

    def overrideNavigation(self, direction: Direction, element: Interactable):
        self.navigation_override[direction] = element

    def navigate(self, direction: Direction) -> Optional[Interactable]:
        return self.navigation_override[direction]

    def setSelectedStyle(self,
                         selected_style: Optional[BoxStyle]) -> None:
        self.selected_style = self.constructDefaultStyle(selected_style)

    def setDisabledStyle(self,
                         disabled_style: Optional[BoxStyle]) -> None:
        self.disabled_style = self.constructDefaultStyle(disabled_style)

    def setClickedStyle(self, clicked_style: Optional[BoxStyle]) -> None:
        self.clicked_style = self.constructDefaultStyle(clicked_style)

    def getSelectedStyle(self) -> BoxStyle:
        return self.selected_style

    def getDisabledStyle(self) -> BoxStyle:
        return self.disabled_style

    def getClickedStyle(self) -> BoxStyle:
        return self.clicked_style

    def getStyle(self) -> BoxStyle:
        if self.state is State.DISABLED:
            return self.getDisabledStyle()
        elif self.state is State.SELECTED:
            return self.getSelectedStyle()
        elif self.state is State.CLICKED:
            return self.getClickedStyle()
        return super().getStyle()

    @abstractclassmethod
    def click(self) -> Response:
        "returns response"
        pass

    def onClick(self, command):
        self.click = command

    def toggleSelected(self) -> None:
        if self.state is State.SELECTED:
            self.unselect()
        else:
            self.select()

    def select(self) -> None:
        self.state = State.SELECTED
        self.draw()

    def unselect(self) -> None:
        self.state = State.IDLE
        self.draw()


class Focusable(Interactable):

    def __init__(
        self,
        parent: Parent,
        width: int,
        height: int,  # Element
        style: Optional[BoxStyle] = None,  # Visible
        selected_style: Optional[BoxStyle] = None,
        clicked_style: Optional[BoxStyle] = None,
        disabled_style: Optional[BoxStyle] = None,
        focused_style: Optional[BoxStyle] = None,
        on_focused_command: Optional[Callable] = None,
        on_unfocused_command: Optional[Callable] = None,
    ) -> None:
        super().__init__(
            parent,
            width,
            height,  # Element
            style,  # Visible
            selected_style,
            clicked_style,
            disabled_style)  # Interactable
        self.setFocudesStyle(focused_style)
        self.setOnFocused(on_focused_command)
        self.setOnUnfocused(on_unfocused_command)

    def setOnFocused(self, command: Optional[Callable]) -> None:
        "Triggered when entry is focused"
        self.onFocused = command

    def setOnChange(self, command: Optional[Callable]) -> None:
        "Triggered when any character gets changed"
        self.onChange = command

    def setOnUnfocused(self, command: Optional[Callable]) -> None:
        "Triggered when entry is unfocused"
        self.onUnfocused = command

    @abstractclassmethod
    def handleKeyEvent(self, val) -> Response:
        pass

    def setFocudesStyle(self, focused_style: Optional[BoxStyle]) -> None:
        self.focused_style = self.constructDefaultStyle(focused_style)

    def getFocusedStyle(self) -> BoxStyle:
        return self.focused_style

    def getStyle(self) -> BoxStyle:
        if self.state is State.FOCUSED:
            return self.getFocusedStyle()
        return super().getStyle()

    def focus(self) -> Response:
        if self.onFocused:
            self.onFocused()
        self.state = State.FOCUSED
        self.draw()
        return Response.FOCUSED

    def unfocus(self) -> Response:
        if self.onUnfocused:
            self.onUnfocused()
        self.state = State.SELECTED
        self.draw()
        return Response.UNFOCUSED

    def toggleFocused(self) -> Response:
        if self.state is State.FOCUSED:
            return self.unfocus()
        else:
            return self.focus()


class Frame(Visible):

    def __init__(self,
                 parent: Parent,
                 width: int,
                 height: int,
                 style: BoxStyle = None) -> None:
        super().__init__(parent, width, height, style)
        self.elements: List[Element] = []

    def getAnchor(self) -> Point:
        self.raiseIfNotPlaced()
        return self.getBorder().corners["tl"]

    def constructDefaultStyle(self,
                              style: Optional[BoxStyle] = None
                             ) -> BoxStyle:
        return Interactable.constructDefaultStyleTemplate(
            self,
            style=style,
            default_style=BoxStyle(
                border_color=self.getWindow().term.white),
            inheritance_vector=(True, True, True, True))

    def checkOutOfBounds(self, border: Box, element: Element) -> None:
        if border.getEdge(Side.LEFT) < self.getBorder().getEdge(Side.LEFT):
            raise BorderOutOfBounds(
                f"{type(element).__name__} {str(border)} "
                f"LEFT border edge ({border.getEdge(Side.LEFT)}) "
                f"exceeds {type(element.parent).__name__} {str(self.border)} "
                f"LEFT border edge ({self.getBorder().getEdge(Side.LEFT)})")
        elif border.getEdge(Side.BOTTOM) < self.getBorder().getEdge(
                Side.BOTTOM):
            raise BorderOutOfBounds(
                f"{type(element).__name__} {str(border)} "
                f"BOTTOM border edge ({border.getEdge(Side.BOTTOM)}) "
                f"exceeds {type(element.parent).__name__} {str(self.border)} "
                f"BOTTOM border edge ({self.getBorder().getEdge(Side.BOTTOM)})")
        elif border.getEdge(Side.TOP) > self.getBorder().getEdge(Side.TOP):
            raise BorderOutOfBounds(
                f"{type(element).__name__} {str(border)} "
                f"top border edge ({border.getEdge(Side.TOP)}) "
                f"exceeds {type(element.parent).__name__} {str(self.border)} "
                f"top border edge ({self.getBorder().getEdge(Side.TOP)})")
        elif border.getEdge(Side.RIGHT) > self.getBorder().getEdge(Side.RIGHT):
            raise BorderOutOfBounds(
                f"{type(element).__name__} {str(border)} "
                f"RIGHT border edge ({border.getEdge(Side.RIGHT)}) "
                f"exceeds {type(element.parent).__name__} {str(self.border)} "
                f"RIGHT border edge ({self.getBorder().getEdge(Side.RIGHT)})")

    def addElement(self, element: Element) -> None:
        # if self.checkOutOfBounds(element):
        #     raise BorderOutOfBounds("Child coordinates are out of bounds of the parent")
        self.elements.append(element)

    def removeElement(self, element: Element) -> None:
        self.elements.remove(element)

    def addElements(self, *elements: Element) -> None:
        for element in elements:
            self.addElement(element)

    def getAllElements(self,
                       element_filter: Optional[Callable] = None
                      ) -> List[Element]:
        elements = []
        for element in self.elements:
            if element.isActive(
            ):  # TODO: Only searching active elements, might want to change
                if isinstance(element, Frame):
                    elements.extend(element.getAllElements(element_filter))
                else:
                    if element_filter:
                        if element_filter(element):
                            elements.append(element)
                    else:
                        elements.append(element)
        return elements


class AbsoluteFrame(Frame):

    def __init__(self,
                 parent: Parent,
                 width: int,
                 height: int,
                 style: BoxStyle = None) -> None:
        super().__init__(parent, width, height, style=style)

    def placeElement(self, element: Element, x: int, y: int) -> Box:
        border = Box(
            self.getAnchor() + Point(x, y),
            self.getAnchor() + Point(x, y) +
            Point(element.width, element.height - 1))
        # self.checkOutOfBounds(border, element)
        return border

    def draw(self) -> None:
        self.raiseIfNotPlaced()
        if self.isActive():
            self.getBorder().drawBackground(self.getWindow(), self.getStyle())
            for element in self.elements:
                if element.isPlaced() and element.isActive():
                    element.draw()


class GridFrame(Frame):

    def __init__(self,
                 parent: Parent,
                 style: BoxStyle,
                 widths: List[int],
                 heights: List[int],
                 inner_border: bool = False) -> None:
        self.width = sum(widths)
        self.height = sum(heights)
        self.widths = widths
        self.heights = heights
        self.setMatrix()
        if inner_border:
            self.width += len(widths) + 1
            self.height += len(heights) + 1
        elif style.border_style is not None:
            self.width += 2
            self.height += 2
        super().__init__(parent, self.width, self.height, style=style)
        self.inner_border = inner_border
        if self.inner_border and self.style.border_style is None:
            raise InvalidAttributes(
                "Must declare outter border style if inner border is used")
        self.setRows(len(heights))
        self.setColumns(len(widths))

    def setMatrix(self) -> None:
        self.matrix: List[List[Optional[Element]]] = []
        for r in range(len(self.heights)):
            temp: List[Optional[Element]] = []
            for c in range(len(self.widths)):
                temp.append(None)
            self.matrix.append(temp)

    def assignCells(self, element: Element, row: int, column: int, rowspan: int,
                    columnspan: int) -> None:
        for r in range(row, row + rowspan):
            for c in range(column, column + columnspan):
                if self.matrix[r][c] is not None:
                    raise CellOutOfBounds("Cell is out of bounds")
                else:
                    self.matrix[r][c] = element

    def raiseIfBorderOutOfBounds(self, element: Element, padx: int, pady: int,
                                 row: int, column: int, rowspan: int,
                                 columnspan: int) -> None:
        element_height = pady + element.getHeight()
        element_width = padx + element.getWidth()
        cell_height = sum(self.heights[row:row + rowspan])
        cell_width = sum(self.widths[column:column + columnspan])
        if self.inner_border:
            cell_height += rowspan - 1
            cell_width += columnspan - 1
        if element_height > cell_height:
            raise BorderOutOfBounds(f"Height of element: {element_height} "
                                    f"exceeds height of cell: {cell_height}")
        if element_width > cell_width:
            raise BorderOutOfBounds(f"Width of element: {element_width} "
                                    f"exceeds width of cell: {cell_width}")

    def placeElement(self,
                     element: Element,
                     padx: int,
                     pady: int,
                     row: int,
                     column: int,
                     rowspan: int = 1,
                     columnspan: int = 1) -> Box:
        self.assignCells(element, row, column, rowspan, columnspan)
        # self.raiseIfBorderOutOfBounds(element, padx, pady, row, column, rowspan, columnspan)
        border = Box(
            self.getAnchor() + Point(
                sum(self.widths[:column]) + padx,
                sum(self.heights[:row]) + pady),
            self.getAnchor() + Point(
                sum(self.widths[:column]) + element.getWidth() + padx,
                sum(self.heights[:row]) + element.getHeight() + pady - 1))
        if self.style.border_style is not None:
            border.p1 = border.p1 + Point(1, 1)
            border.p2 = border.p2 + Point(1, 1)
            border.updateCorners()
        if self.inner_border:
            border.p1 = border.p1 + Point(column, row)
            border.p2 = border.p2 + Point(column, row)
            border.updateCorners()
        # self.checkOutOfBounds(border, element)
        return border

    def setRows(self, rows: int) -> None:
        maxplaces = self.height
        if rows < 1:
            raise ValueError("Rows must be >= 1")
        if self.inner_border:
            maxplaces -= rows + 1
        if maxplaces < rows:
            raise ValueError("Not enough space for each row")
        self.rows = rows

    def setColumns(self, columns: int) -> None:
        maxplaces = self.width
        if columns < 1:
            raise ValueError("Columns must be >= 1")
        if self.inner_border:
            maxplaces -= columns + 1
        if maxplaces < columns:
            raise ValueError("Not enough space for each column")
        self.columns = columns

    def compareCells(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        return self.matrix[y1][x1] == self.matrix[y2][x2] and self.matrix[y1][
            x1] is not None

    def drawGrid(self) -> None:
        command = ''
        border = self.getBorder()
        style = self.getStyle()
        window = self.getWindow()
        if style.bg_color:
            command += style.bg_color
        if self.getWidth() < 2 or self.getHeight() < 2:
            raise RectangleTooSmall(
                "Unable to fit border on such small rectangle, must be at least 2x2"
            )
        else:
            if style.border_style is BorderStyle.SINGLE:
                br = "┌"
                lr = "─"
                blr = "┬"
                bl = "┐"
                tb = "│"
                tbr = "├"
                tblr = "┼"
                tbl = "┤"
                tr = "└"
                tlr = "┴"
                tl = "┘"
            elif style.border_style is BorderStyle.DOUBLE:
                br = "╔"
                lr = "═"
                blr = "╦"
                bl = "╗"
                tb = "║"
                tbr = "╠"
                tblr = "╬"
                tbl = "╣"
                tr = "╚"
                tlr = "╩"
                tl = "╝"
            else:
                br = " "
                lr = " "
                blr = " "
                bl = " "
                tb = " "
                tbr = " "
                tblr = " "
                tbl = " "
                tr = " "
                tlr = " "
                tl = " "

            if style.border_color:
                command += style.border_color
            for y, height in enumerate(self.heights):
                for slice in range(height + 1):
                    command += window.moveXY(
                        Point(
                            border.getEdge(Side.LEFT),
                            border.getEdge(Side.TOP) + sum(self.heights[:y]) +
                            y + slice))
                    if y == 0 and slice == 0:
                        command += br
                        for x, width in enumerate(self.widths):
                            command += lr * width
                            if x == len(self.widths) - 1:
                                command += bl
                            else:
                                if self.compareCells(x, y, x + 1, y):
                                    command += lr
                                else:
                                    command += blr
                    elif slice == 0 and y != 0:
                        x = 0
                        if self.compareCells(x, y, x, y - 1):
                            command += tb
                        else:
                            command += tbr
                        for x, width in enumerate(self.widths):
                            if self.compareCells(x, y, x, y - 1):
                                command += " " * width
                            else:
                                command += lr * width
                            if x == len(self.widths) - 1:
                                if self.compareCells(x, y - 1, x, y):
                                    command += tb
                                else:
                                    command += tbl
                            else:
                                bot = not self.compareCells(x, y, x + 1, y)
                                top = not self.compareCells(
                                    x, y - 1, x + 1, y - 1)
                                left = not self.compareCells(x, y - 1, x, y)
                                right = not self.compareCells(
                                    x + 1, y - 1, x + 1, y)
                                if not top and not bot and not left and not right:
                                    command += " "
                                elif not top and not bot and left and right:
                                    command += lr
                                elif not top and bot and not left and right:
                                    command += br
                                elif not top and bot and left and not right:
                                    command += bl
                                elif not top and bot and left and right:
                                    command += blr
                                elif top and not bot and not left and right:
                                    command += tr
                                elif top and not bot and left and not right:
                                    command += tl
                                elif top and not bot and left and right:
                                    command += tlr
                                elif top and bot and not left and not right:
                                    command += tb
                                elif top and bot and not left and right:
                                    command += tbr
                                elif top and bot and left and not right:
                                    command += tbl
                                elif top and bot and left and right:
                                    command += tblr

                    else:
                        command += tb
                        for x, width in enumerate(self.widths):
                            command += " " * width
                            if x != len(self.widths) - 1:
                                if self.compareCells(x, y, x + 1, y):
                                    command += " "
                                else:
                                    command += tb
                        command += tb
                command += window.moveXY(
                    Point(border.getEdge(Side.LEFT),
                          border.getEdge(Side.TOP) + sum(self.heights) + y + 1))
                command += tr
                for x, width in enumerate(self.widths):
                    if x == len(self.widths) - 1:
                        command += lr * width + tl
                    else:
                        command += lr * width
                        if self.compareCells(x, y, x + 1, y):
                            command += lr
                        else:
                            command += tlr

        print(command)
        window.flush()

    def draw(self) -> None:
        self.raiseIfNotPlaced()
        if self.isActive():
            if self.inner_border:
                self.drawGrid()
            else:
                self.getBorder().drawBackground(self.getWindow(),
                                                self.getStyle())
            for element in self.elements:
                if element.isPlaced() and element.isActive():
                    element.draw()


class Window():

    def __init__(self, term: Terminal) -> None:
        self.term = term
        self.window_state = WindowState.VIEW
        self.active_element: Optional[Interactable] = None
        AbsoluteFrame(self, self.term.width, self.term.height)
        self.mainframe.activate()
        self.hotkeys: dict[str, Callable] = {}

    def bind(self, val: str, command: Callable) -> None:
        self.hotkeys[val] = command

    def checkBindings(self, val) -> Response:
        if val.is_sequence:
            val = val.name
        else:
            val = val.lower()
        for hotkey in self.hotkeys:
            if hotkey == val:
                self.hotkeys[val]()
                return Response.COMPLETE
        return Response.CONTINUE

    def getWindow(self) -> Window:
        return self

    def draw(self) -> None:
        self.clear()
        self.mainframe.draw()

    def moveXY(self, p: Point) -> str:  # TODO issue 17
        return self.term.move_xy(p.x, p.y)

    def clear(self) -> None:
        print(self.term.normal + self.term.clear)

    def flush(self) -> None:
        "Resets pointer and color"
        print(self.term.home + self.term.normal)

    def getAllElements(self,
                       element_filter: Optional[Callable] = None
                      ) -> List[Element]:
        return self.mainframe.getAllElements(element_filter)

    def getAllInteractive(self):
        return self.getAllElements(lambda element: isinstance(
            element, Interactable) and element.isActive())

    def getExtremeElement(self, direction: Direction) -> Optional[Interactable]:
        extreme_element: Optional[Interactable] = None
        if direction is Direction.DOWN:
            highest_y = 0
            for element in self.getAllInteractive():
                if element.getBorder().getEdge(Side.TOP) >= highest_y:
                    highest_y = element.getBorder().getEdge(Side.TOP)
                    extreme_element = element
        elif direction is Direction.RIGHT:
            highest_x = 0
            for element in self.getAllInteractive():
                if element.getBorder().getEdge(Side.RIGHT) >= highest_x:
                    highest_x = element.getBorder().getEdge(Side.RIGHT)
                    extreme_element = element
        elif direction is Direction.UP:
            lowest_y = float('inf')
            for element in self.getAllInteractive():
                if element.getBorder().getEdge(Side.BOTTOM) <= lowest_y:
                    lowest_y = element.getBorder().getEdge(Side.BOTTOM)
                    extreme_element = element
        elif direction is Direction.LEFT:
            lowest_x = float('inf')
            for element in self.getAllInteractive():
                if element.getBorder().getEdge(Side.LEFT) <= lowest_x:
                    lowest_x = element.getBorder().getEdge(Side.LEFT)
                    extreme_element = element

        return extreme_element

    def calculateWeightedDistance(self, p1: Point, p2: Point,
                                  direction: Direction) -> float:
        delta_x = p1.x - p2.x
        delta_y = p1.y - p2.y

        argument = degrees(atan2(delta_y, delta_x))
        delta_angle = abs(direction.value - argument)

        if delta_angle > 180:
            delta_angle = 360 - delta_angle

        if delta_angle > MAX_ANGLE:
            return float('inf')

        distance = np.linalg.norm(np.array((delta_x, delta_y)))
        return distance / gaussian(x=delta_angle / 90, mean=0, std=0.45)

    def getActivePoint(self, element: Element, direction: Direction) -> Point:
        border = element.getBorder()
        if direction is Direction.UP:
            return Point(border.getCenter().x, border.getEdge(Side.TOP))
        elif direction is Direction.DOWN:
            return Point(border.getCenter().x, border.getEdge(Side.BOTTOM))
        elif direction is Direction.RIGHT:
            return Point(border.getEdge(Side.RIGHT), border.getCenter().y)
        elif direction is Direction.LEFT:
            return Point(border.getEdge(Side.LEFT), border.getCenter().y)

    def getCandidatePoint(self, element: Element,
                          direction: Direction) -> Point:
        border = element.getBorder()
        if direction is Direction.UP:
            return Point(border.getCenter().x, border.getEdge(Side.BOTTOM))
        elif direction is Direction.DOWN:
            return Point(border.getCenter().x, border.getEdge(Side.TOP))
        elif direction is Direction.RIGHT:
            return Point(border.getEdge(Side.LEFT), border.getCenter().y)
        elif direction is Direction.LEFT:
            return Point(border.getEdge(Side.RIGHT), border.getCenter().y)

    def findElement(self, direction: Direction) -> Optional[Interactable]:
        if self.active_element is None:
            raise TypeError(
                "Unable to find element if active_element isn't set")
        else:
            assert (isinstance(self.active_element, Element))
            active_point = self.getActivePoint(self.active_element, direction)
            min_wighted_distance = float('inf')
            closest_element: Optional[Interactable] = None
            for element in self.getAllInteractive():
                if element != self.active_element and element.isActive():
                    point = self.getCandidatePoint(element, direction)
                    weighted_distance = self.calculateWeightedDistance(
                        active_point, point, direction)
                    if weighted_distance < min_wighted_distance:
                        min_wighted_distance = weighted_distance
                        closest_element = element

            return closest_element

    def addElement(self, element: Element) -> None:
        "Allows for only one element to be added, which is a single Frame"
        if not isinstance(element, AbsoluteFrame):
            raise InvalidLayout(
                "Only a single element of type AbsoluteFrame can be added to a Window"
            )
        self.mainframe = element
        self.mainframe.border = Box(
            Point(0, 0), Point(self.term.width, self.term.height))

    def removeElement(self, element: Element) -> None:
        raise Exception("Not allowed to remove elements from Window")

    def handleKeyEvent(self, val) -> Response:
        if not val:
            pass
        else:
            if self.window_state is WindowState.VIEW:
                # Active element can't be set if WindowState.VIEW
                assert (self.active_element is None)
                res = self.checkBindings(val)
                if res is Response.COMPLETE:
                    return Response.COMPLETE
                if val.is_sequence:
                    if val.name == "KEY_UP":
                        self.active_element = self.getExtremeElement(
                            Direction.UP)
                    elif val.name == "KEY_RIGHT":
                        self.active_element = self.getExtremeElement(
                            Direction.RIGHT)
                    elif val.name == "KEY_DOWN":
                        self.active_element = self.getExtremeElement(
                            Direction.DOWN)
                    elif val.name == "KEY_LEFT":
                        self.active_element = self.getExtremeElement(
                            Direction.LEFT)

                    if self.active_element is not None:
                        self.active_element.toggleSelected()
                        self.window_state = WindowState.SELECTION
                elif val:
                    if val.lower() == 'q':
                        return Response.QUIT
            elif self.window_state is WindowState.SELECTION:
                # Active element must be set if WindowState.SELECTION
                assert (isinstance(self.active_element, Interactable))
                res = self.checkBindings(val)
                if res is Response.COMPLETE:
                    return Response.COMPLETE
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
                        res = self.active_element.click()
                        if res is Response.FOCUSED:
                            self.window_state = WindowState.FOCUSED
                    elif val.name == "KEY_ESCAPE" or val.name == "KEY_BACKSPACE":
                        self.window_state = WindowState.VIEW
                        self.active_element.toggleSelected()
                        self.active_element = None
                    if direction:  # If a key is pressed which gives direction
                        # If a direction is given the active element couldn't have been set to None
                        assert (self.active_element is not None)
                        next_element = self.active_element.navigate(direction)
                        if not next_element:
                            next_element = self.findElement(direction)
                        if next_element:  # If a good next element is found
                            self.active_element.toggleSelected()
                            self.active_element = next_element
                            self.active_element.toggleSelected()
                elif val:
                    if val.lower() == 'q':
                        return Response.QUIT
            elif self.window_state is WindowState.FOCUSED:
                assert (isinstance(self.active_element, Focusable))
                res = self.active_element.handleKeyEvent(val)
                if res is Response.UNFOCUSED:
                    self.window_state = WindowState.SELECTION
                elif res is Response.CONTINUE:
                    if val:
                        if val.lower() == 'q':
                            return Response.QUIT
                elif res is Response.QUIT:
                    return Response.QUIT
        return Response.CONTINUE

    def loop(self):
        with self.term.cbreak():
            self.clear()
            self.draw()
            res = Response.CONTINUE
            while res != Response.QUIT:
                val = self.term.inkey(timeout=3)
                res = self.handleKeyEvent(val)
            self.clear()
            self.flush()


Parent = Union[Frame, Window]


class Box():

    def __init__(self, p1: Point, p2: Point) -> None:
        self.setP1(p1)
        self.setP2(p2)
        self.updateCorners()

    def __str__(self) -> str:
        return f"[{self.p1}, {self.p2}]"

    def setP1(self, p1: Point) -> None:
        self.p1 = p1

    def setP2(self, p2: Point) -> None:
        self.p2 = p2

    def updateCorners(self) -> None:
        self.corners = {
            "tl": Point(min(self.p1.x, self.p2.x), min(self.p1.y, self.p2.y)),
            "tr": Point(max(self.p1.x, self.p2.x), min(self.p1.y, self.p2.y)),
            "bl": Point(min(self.p1.x, self.p2.x), max(self.p1.y, self.p2.y)),
            "br": Point(max(self.p1.x, self.p2.x), max(self.p1.y, self.p2.y))
        }

    def getEdge(self, side: Side) -> int:
        if side is Side.TOP:
            return self.corners["tl"].y
        elif side is Side.RIGHT:
            return self.corners["tr"].x
        elif side is Side.BOTTOM:
            return self.corners["bl"].y
        else:  # LEFT
            return self.corners["bl"].x

    def getWidth(self) -> int:
        return self.getEdge(Side.RIGHT) - self.getEdge(Side.LEFT)

    def getHeight(self) -> int:
        return self.getEdge(Side.BOTTOM) - self.getEdge(Side.TOP)

    def getMiddleX(self) -> int:
        return self.getEdge(Side.LEFT) + self.getWidth() // 2

    def getMiddleY(self) -> int:
        return self.getEdge(Side.BOTTOM) + self.getHeight() // 2

    def getCenter(self) -> Point:
        return Point(self.getMiddleX(), self.getMiddleY())

    def drawBackground(self, window: Window, style: BoxStyle) -> None:
        command = ''
        if style.bg_color:
            command += style.bg_color
        if style.border_style is not BorderStyle.NONE and style.border_style is not None:
            if self.getWidth() < 2 or self.getHeight() < 2:
                raise RectangleTooSmall(
                    "Unable to fit border on such small rectangle, must be at least 2x2"
                )
            else:
                if style.border_color:
                    command += style.border_color
                for row in range(self.getEdge(Side.TOP),
                                 self.getEdge(Side.BOTTOM) + 1):
                    command += window.moveXY(Point(self.getEdge(Side.LEFT),
                                                   row))
                    if row == self.getEdge(Side.BOTTOM):
                        if style.border_style is BorderStyle.SINGLE:
                            command += "└" + "─" * (self.getWidth() - 2) + "┘"
                        elif style.border_style is BorderStyle.DOUBLE:
                            command += "╚" + "═" * (self.getWidth() - 2) + "╝"
                    elif row == self.getEdge(Side.TOP):
                        if style.border_style is BorderStyle.SINGLE:
                            command += "┌" + "─" * (self.getWidth() - 2) + "┐"
                        elif style.border_style is BorderStyle.DOUBLE:
                            command += "╔" + "═" * (self.getWidth() - 2) + "╗"
                    else:
                        if style.border_style is BorderStyle.SINGLE:
                            command += "│" + " " * (self.getWidth() - 2) + "│"
                        elif style.border_style is BorderStyle.DOUBLE:
                            command += "║" + " " * (self.getWidth() - 2) + "║"

        else:
            if style.bg_color:
                for row in range(self.getEdge(Side.TOP),
                                 self.getEdge(Side.BOTTOM) + 1):
                    command += window.moveXY(Point(self.getEdge(Side.LEFT),
                                                   row))
                    command += " " * self.getWidth()

        print(command)
        window.flush()

    def writeText(self, window: Window, style: BoxStyle,
                  text: Optional[str], padding: List[int], h_align: HAlignment,
                  v_align: VAlignment) -> None:
        command = ''
        if text:
            # Text style
            if style.bg_color:
                command += style.bg_color
            if style.text_style:
                command += style.text_style

            # Cut of text if it wont fit
            max_text_len = self.getWidth() - (padding[1] + padding[3])
            text = text[:max_text_len]

            # Text alignment
            # Horizontal
            if h_align is HAlignment.LEFT:
                text_start_x = self.getEdge(Side.LEFT) + padding[3]
            elif h_align is HAlignment.MIDDLE:
                text_start_x = self.getEdge(Side.LEFT) + padding[3] + (
                    self.getWidth() // 2) - (len(text) // 2)
            elif h_align is HAlignment.RIGHT:
                text_start_x = self.getEdge(Side.RIGHT) - padding[1] - len(text)
            # Vertical
            if v_align is VAlignment.TOP:
                text_start_y = self.getEdge(Side.BOTTOM) - padding[0]
            elif v_align is VAlignment.MIDDLE:
                text_start_y = self.getEdge(
                    Side.BOTTOM) - padding[0] - (self.getHeight() // 2)
            elif v_align is VAlignment.BOTTOM:
                text_start_y = self.getEdge(Side.TOP) + padding[2]

            command += window.moveXY(Point(text_start_x, text_start_y))
            command += text
            print(command)
            window.flush()

    def draw(self, window: Window, style: BoxStyle, text: Optional[str],
             padding: List[int], h_align: HAlignment,
             v_align: VAlignment) -> None:
        self.drawBackground(window, style)
        self.writeText(window, style, text, padding, h_align, v_align)


class BoxStyle():

    def __init__(self,
                 bg_color: Optional[str] = None,
                 text_style: Optional[str] = None,
                 border_color: Optional[str] = None,
                 border_style: Optional[BorderStyle] = None) -> None:
        "Leave all parameters empty for default style"
        self.bg_color = bg_color
        self.text_style = text_style
        self.border_color = border_color
        self.border_style = border_style


class Label(Visible, HasText):

    def __init__(
        self,
        parent: Parent,
        width: int,
        height: int,
        text: Optional[str] = None,
        style: BoxStyle = None,
        padding: List[int] = [0] * 4,
        h_align: HAlignment = HAlignment.MIDDLE,
        v_align: VAlignment = VAlignment.MIDDLE,
    ) -> None:
        Visible.__init__(
            self,
            parent,
            width,
            height,  # Element
            style)  # Visible
        HasText.__init__(self, text, padding, h_align, v_align, width, height)

    def constructDefaultStyle(self, style: Optional[BoxStyle] = None):
        return Interactable.constructDefaultStyleTemplate(
            self,
            default_style=BoxStyle(
                bg_color=self.getWindow().term.normal,
                text_style=self.getWindow().term.white),
            style=style,
            inheritance_vector=(True, True, True, True))

    def draw(self) -> None:
        self.getBorder().draw(self.getWindow(), self.getStyle(), self.text,
                              self.padding, self.h_align, self.v_align)


class Button(Interactable, HasText):

    def __init__(self,
                 parent: Parent,
                 width: int,
                 height: int,
                 command: Optional[Callable] = None,
                 style: BoxStyle = None,
                 text: Optional[str] = None,
                 h_align: HAlignment = HAlignment.MIDDLE,
                 v_align: VAlignment = VAlignment.MIDDLE,
                 padding: List[int] = [0] * 4,
                 disabled_style: BoxStyle = None,
                 selected_style: BoxStyle = None,
                 clicked_style: BoxStyle = None) -> None:
        Interactable.__init__(
            self,
            parent,
            width,
            height,  # Element
            style,  # Visible
            selected_style,
            clicked_style,
            disabled_style)  # Interactable
        HasText.__init__(self, text, padding, h_align, v_align, width, height)
        self.onClick(command)

    def constructDefaultStyle(self,
                              style: Optional[BoxStyle] = None
                             ) -> BoxStyle:
        return Interactable.constructDefaultStyleTemplate(
            self,
            style=style,
            default_style=BoxStyle(
                bg_color=self.getWindow().term.on_white,
                text_style=self.getWindow().term.black),
            inheritance_vector=(False, True, False,
                                False))  # Only inherits text style

    def draw(self) -> None:
        self.getBorder().draw(self.getWindow(), self.getStyle(), self.text,
                              self.padding, self.h_align, self.v_align)

    def onClick(self, command: Optional[Callable]) -> None:
        self.command = command

    def click(self) -> Response:
        if self.command:
            return self.command()
        return Response.CONTINUE


class Entry(Focusable, HasText):

    def __init__(
        self,
        parent: Parent,
        width: int,
        height: int,
        default_text: Optional[str] = None,
        style: BoxStyle = None,
        padding: List[int] = [0] * 4,
        h_align: HAlignment = HAlignment.LEFT,
        v_align: VAlignment = VAlignment.TOP,
        selected_style: BoxStyle = None,
        clicked_style: BoxStyle = None,
        disabled_style: BoxStyle = None,
        focused_style: BoxStyle = None,
        cursor_style: str = None,
        cursor_bg_color: str = None,
        highlight_color: str = None,
        on_focused_command: Optional[Callable] = None,
        on_unfocused_command: Optional[Callable] = None,
        on_change_command: Optional[Callable] = None,
    ) -> None:
        # Assigning text
        Focusable.__init__(
            self,
            parent,
            width,
            height,  # Element
            style,  # Visible
            selected_style,
            clicked_style,
            disabled_style,  # Interactable
            focused_style,  # Focusable
            on_focused_command=on_focused_command,
            on_unfocused_command=on_unfocused_command)
        HasText.__init__(self, default_text, padding, h_align, v_align, width,
                         height)
        self.saved_text = ''
        self.state = State.IDLE
        self.cursor_pos = 0
        self.text: str = getFirstAssigned([self.text], '')
        self.cursor_style: str = getFirstAssigned(
            [cursor_style],
            self.getWindow().term.on_goldenrod1)
        self.cursor_bg_color: str = getFirstAssigned(
            [cursor_bg_color],
            self.getWindow().term.gray33)
        self.highlight_color: str = getFirstAssigned(
            [highlight_color],
            self.getWindow().term.on_gray38)
        self.setOnChange(on_change_command)

    def constructDefaultStyle(self, style: Optional[BoxStyle] = None):
        return Interactable.constructDefaultStyleTemplate(
            self,
            style=style,
            default_style=BoxStyle(
                bg_color=self.getWindow().term.normal,
                text_style=self.getWindow().term.white,
                border_color=self.getWindow().term.white,
                border_style=BorderStyle.SINGLE),
            inheritance_vector=(False, True, True,
                                True))  # Doesn't inherit bg_color

    def setText(self, text: Optional[str] = None) -> None:
        HasText.setText(self, text)
        self.updateCursor()

    def updateCursor(self) -> None:
        if self.text is None or self.text == '':
            self.cursor_pos = 0
        else:
            self.cursor_pos = len(self.text)

    def clear(self) -> None:
        self.text = ''
        self.saved_text = ''
        self.updateCursor()

    def click(self) -> Response:
        self.text = self.saved_text
        self.focus()
        return Response.FOCUSED

    def getSavedText(self) -> str:
        return self.saved_text

    def handleKeyEvent(self, val) -> Response:
        "Returns True if key event was handled"
        if val.is_sequence:
            if val.name == "KEY_UP":
                return Response.COMPLETE
            elif val.name == "KEY_RIGHT":
                self.cursor_pos = min(self.cursor_pos + 1, len(self.text))
                self.draw()
                return Response.COMPLETE
            elif val.name == "KEY_DOWN":
                return Response.COMPLETE
            elif val.name == "KEY_LEFT":
                self.cursor_pos = max(self.cursor_pos - 1, 0)
                self.draw()
                return Response.COMPLETE
            elif val.name == "KEY_BACKSPACE":
                if self.cursor_pos > 0:
                    self.setText(self.text[:self.cursor_pos - 1] +
                                 self.text[self.cursor_pos:])
                    self.draw()
                return Response.COMPLETE
            elif val.name == "KEY_ENTER":
                self.saved_text = self.text
                self.unfocus()
                return Response.UNFOCUSED
            elif val.name == "KEY_ESCAPE":
                self.text = self.saved_text
                self.unfocus()
                return Response.UNFOCUSED
        elif val:
            if self.onChange:
                self.onChange()
            if len(self.text) < self.getWidth(
            ):  # TODO: Support text larger than width
                self.setText(self.text + val)
                self.draw()
            return Response.COMPLETE
        else:
            pass
        return Response.CONTINUE

    def drawCursor(self, border: Box, window: Window) -> None:
        command = ''
        # Cursor style
        command += self.cursor_style
        command += self.cursor_bg_color

        # Cut of text if it wont fit
        max_text_len = border.getWidth() - (self.padding[1] + self.padding[3])
        text = self.text[:max_text_len]

        # Get cursor character
        if self.cursor_pos >= len(text):
            cursor_character = ' '
        else:
            cursor_character = text[self.cursor_pos]

        # Text alignment
        # Horizontal
        if self.h_align is HAlignment.LEFT:
            text_start_x = border.getEdge(Side.LEFT) + self.padding[3]
        elif self.h_align is HAlignment.MIDDLE:
            text_start_x = border.getEdge(Side.LEFT) + self.padding[3] + (
                border.getWidth() // 2) - (len(text) // 2)
        elif self.h_align is HAlignment.RIGHT:
            text_start_x = border.getEdge(
                Side.RIGHT) - self.padding[1] - max_text_len
        # Vertical
        if self.v_align is VAlignment.TOP:
            text_start_y = border.getEdge(Side.TOP) - self.padding[0]
        elif self.v_align is VAlignment.MIDDLE:
            text_start_y = border.getEdge(
                Side.TOP) - self.padding[0] - (border.getHeight() // 2)
        elif self.v_align is VAlignment.BOTTOM:
            text_start_y = border.getEdge(Side.BOTTOM) + self.padding[2]

        command += window.moveXY(
            Point(text_start_x + self.cursor_pos, text_start_y))
        command += cursor_character
        print(command)
        window.flush()

    def draw(self) -> None:
        self.getBorder().draw(self.getWindow(), self.getStyle(), self.text,
                              self.padding, self.h_align, self.v_align)
        if self.state is State.FOCUSED:
            self.drawCursor(self.getBorder(), self.getWindow())


class DropdownMenu(Focusable, HasText):

    def __init__(self,
                 parent: Parent,
                 width: int,
                 height: int,
                 text: Optional[str],
                 auto_redraw: bool = True,
                 style: Optional[BoxStyle] = None,
                 padding: List[int] = [0] * 4,
                 h_align: HAlignment = HAlignment.LEFT,
                 v_align: VAlignment = VAlignment.MIDDLE,
                 selected_style: Optional[BoxStyle] = None,
                 clicked_style: Optional[BoxStyle] = None,
                 disabled_style: Optional[BoxStyle] = None,
                 focused_style: Optional[BoxStyle] = None) -> None:
        Focusable.__init__(
            self,
            parent,
            width,
            height,  # Element
            style,  # Visible
            selected_style,
            clicked_style,
            disabled_style,  # Interactable
            focused_style)  # Focusable
        HasText.__init__(self, None, padding, h_align, v_align, width, height)
        self.itemFrame = AbsoluteFrame(parent, width, height)
        # TODO: add ▼ to main button
        self.mainButton = Button(self.itemFrame,
                                 width,
                                 height,
                                 command=self.toggleFocused,
                                 style=self.style,
                                 text=text,
                                 selected_style=self.selected_style,
                                 clicked_style=self.clicked_style,
                                 disabled_style=self.disabled_style)
        self.itemButtons: List[Button] = [self.mainButton]
        self.active_index = 0
        self.active_item = self.mainButton
        self.auto_redraw = auto_redraw

    def place(self, x: int, y: int) -> None:
        self.itemFrame.height = self.getItemHeight() * len(self.itemButtons)
        self.itemFrame.place(x, y)
        self.mainButton.place(0, 0)
        self.border = self.mainButton.getBorder()
        for i, itemButton in enumerate(self.itemButtons):
            itemButton.place(0, i * self.getItemHeight())
        self.activate()
        self.itemFrame.deactivate()

    def focus(self) -> Response:
        self.itemFrame.activate()
        return super().focus()

    def unfocus(self) -> Response:
        self.active_item.toggleSelected()
        self.active_index = 0
        self.active_item = self.itemButtons[self.active_index]
        self.active_item.toggleSelected()
        self.itemFrame.deactivate()
        if self.auto_redraw:
            self.getWindow().draw()
        return super().unfocus()

    def click(self) -> Response:
        assert (self.mainButton.command is not None)  # Always declared in init
        return self.mainButton.command()

    def selectNext(self) -> None:
        if self.active_index < len(self.itemButtons) - 1:
            self.active_item.toggleSelected()
            self.active_index += 1
            self.active_item = self.itemButtons[self.active_index]
            self.active_item.toggleSelected()

    def selectPrev(self) -> None:
        if self.active_index > 0:
            self.active_item.toggleSelected()
            self.active_index -= 1
            self.active_item = self.itemButtons[self.active_index]
            self.active_item.toggleSelected()

    def handleKeyEvent(self, val) -> Response:
        if val.is_sequence:
            if val.name == "KEY_UP":
                self.selectPrev()
                return Response.COMPLETE
            elif val.name == "KEY_RIGHT":
                pass
            elif val.name == "KEY_DOWN":
                self.selectNext()
                return Response.COMPLETE
            elif val.name == "KEY_LEFT":
                pass
            elif val.name == "KEY_ENTER":
                res = self.active_item.click()
                if res:
                    return res
                return Response.COMPLETE
            elif val.name == "KEY_BACKSPACE":
                return self.toggleFocused()
            elif val.name == "KEY_ESCAPE":
                return self.toggleFocused()
        return Response.CONTINUE

    def toggleSelected(self) -> None:
        self.mainButton.toggleSelected()
        if self.state is State.SELECTED:
            self.unselect()
        else:
            self.select()

    def constructDefaultStyle(self, style: Optional[BoxStyle] = None):
        return Interactable.constructDefaultStyleTemplate(
            self,
            default_style=BoxStyle(
                bg_color=self.getWindow().term.on_white,
                text_style=self.getWindow().term.black),
            style=style,
            inheritance_vector=(True, False, False, False))  # Doesn't inherit

    def getItemHeight(self) -> int:
        return self.height

    def addItem(self,
                text: str,
                command: Callable,
                style: Optional[BoxStyle] = None,
                padding: Optional[List[int]] = None,
                h_align: Optional[HAlignment] = None,
                v_align: Optional[VAlignment] = None,
                selected_style: Optional[BoxStyle] = None,
                clicked_style: Optional[BoxStyle] = None,
                disabled_style: Optional[BoxStyle] = None) -> None:
        # Extend frame to fit option
        # Match mainButton params if none are given
        padding = getFirstAssigned([padding], self.mainButton.padding)
        h_align = getFirstAssigned([h_align], self.mainButton.h_align)
        v_align = getFirstAssigned([v_align], self.mainButton.v_align)
        style = getFirstAssigned([style], self.mainButton.style)
        selected_style = getFirstAssigned([selected_style],
                                          self.mainButton.selected_style)
        clicked_style = getFirstAssigned([clicked_style],
                                         self.mainButton.clicked_style)
        disabled_style = getFirstAssigned([disabled_style],
                                          self.mainButton.disabled_style)

        optionButton = Button(parent=self.itemFrame,
                              width=self.width,
                              height=self.height,
                              command=command,
                              text=text,
                              style=style,
                              selected_style=selected_style,
                              clicked_style=clicked_style,
                              disabled_style=disabled_style)
        self.itemButtons.append(optionButton)

    def draw(self) -> None:
        self.raiseIfNotPlaced()
        self.mainButton.draw()
        self.itemFrame.draw()


class OptionMenu(DropdownMenu):

    def __init__(self,
                 parent: Parent,
                 width: int,
                 height: int,
                 default_text=Optional[str],
                 options=List[str],
                 style: Optional[BoxStyle] = None,
                 padding: List[int] = [0] * 4,
                 h_align: HAlignment = HAlignment.LEFT,
                 v_align: VAlignment = VAlignment.MIDDLE,
                 selected_style: Optional[BoxStyle] = None,
                 clicked_style: Optional[BoxStyle] = None,
                 disabled_style: Optional[BoxStyle] = None,
                 focused_style: Optional[BoxStyle] = None) -> None:
        super().__init__(parent=parent,
                         width=width,
                         height=height,
                         text=default_text,
                         style=style,
                         padding=padding,
                         h_align=h_align,
                         v_align=v_align,
                         selected_style=selected_style,
                         clicked_style=clicked_style,
                         disabled_style=disabled_style,
                         focused_style=focused_style)
        self.options = options
        for option in self.options:
            self.addOption(text=option,
                           style=style,
                           padding=padding,
                           h_align=h_align,
                           v_align=v_align,
                           selected_style=selected_style,
                           clicked_style=clicked_style,
                           disabled_style=disabled_style)

    def getValue(self) -> Optional[str]:
        return self.mainButton.text

    def switchOptions(self, optionIndex: int) -> Response:
        optionButton = self.itemButtons[optionIndex]

        self.mainButton.text = optionButton.text
        self.mainButton.style = optionButton.style
        self.mainButton.selected_style = optionButton.selected_style
        self.mainButton.clicked_style = optionButton.clicked_style
        self.mainButton.disabled_style = optionButton.disabled_style
        return self.unfocus()

    def addOption(self,
                  text: str,
                  style: Optional[BoxStyle] = None,
                  padding: Optional[List[int]] = None,
                  h_align: Optional[HAlignment] = None,
                  v_align: Optional[VAlignment] = None,
                  selected_style: Optional[BoxStyle] = None,
                  clicked_style: Optional[BoxStyle] = None,
                  disabled_style: Optional[BoxStyle] = None) -> None:
        if self.mainButton.text is None:
            self.mainButton.text = text
        else:
            optionIndex = len(self.itemButtons)
            super().addItem(text=text,
                            command=lambda: self.switchOptions(optionIndex),
                            style=style,
                            padding=padding,
                            h_align=h_align,
                            v_align=v_align,
                            selected_style=selected_style,
                            clicked_style=clicked_style,
                            disabled_style=disabled_style)
