from ssl import HAS_ALPN
from xml.dom import VALIDATION_ERR
from widgets import Square, Window, Button, Point, ButtonStyle
from blessed import Terminal
from constants import HAlignment, VAlignment
from time import sleep

term = Terminal()

window = Window(term)
enterButton = Button(window, Point(12, 12), Point(26, 14), text="Check",
                     style=ButtonStyle(term.on_orange, term.bold_black),
                     h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)

window.clear()
enterButton.draw()
print(term.home)
