from __future__ import annotations
from widgets import Square, Window, Button, Point, ButtonStyle
from blessed import Terminal
from constants import HAlignment, VAlignment
from time import sleep, time

term = Terminal()

window = Window(term)
checkButton = Button(window, Point(0, 0), Point(15, 2), text="Check",
                     style=ButtonStyle(term.on_darkgreen, term.white),
                     h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
resetButton = Button(window, Point(27, 14), Point(41, 16), text="Reset",
                     style=ButtonStyle(term.on_red4, term.white),
                     h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)

window.clear()
checkButton.draw()
resetButton.draw()

print(term.home)
