from ssl import HAS_ALPN
from xml.dom import VALIDATION_ERR
from widgets import Square, Window, Button, Point
from blessed import Terminal
from constants import HAlignment, VAlignment

term = Terminal()

window = Window(term)
enterButton = Button(window, Point(12, 12), Point(26, 14), "Check",
                     text_color=term.black, bg_color=term.on_orange,
                     h_align=HAlignment.LEFT, v_align=VAlignment.BOTTOM,
                     padding=[2, 5, 2, 5])

window.clear()
enterButton.draw()
print(term.home)
