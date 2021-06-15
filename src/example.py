from __future__ import annotations
from widgets import Window, Button, Point, ButtonStyle
from blessed import Terminal
from constants import HAlignment, VAlignment
from time import sleep, time

term = Terminal()

window = Window(term)
mainButton = Button(window, Point(82, 5), Point(90, 7), text="main",
                    selected_style=ButtonStyle(term.on_darkgreen, term.underline_yellow),
                    style=ButtonStyle(term.on_darkgreen, term.white),
                    h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button1 = Button(window, Point(75, 5), Point(77, 7), text="1",
                 style=ButtonStyle(term.on_red4, term.white),
                 selected_style=ButtonStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button2 = Button(window, Point(80, 0), Point(95, 2), text="2",
                 style=ButtonStyle(term.on_red4, term.white),
                 selected_style=ButtonStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button3 = Button(window, Point(88, 10), Point(90, 13), text="3",
                 style=ButtonStyle(term.on_red4, term.white),
                 selected_style=ButtonStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button4 = Button(window, Point(102, 5), Point(110, 7), text="4",
                 style=ButtonStyle(term.on_red4, term.white),
                 selected_style=ButtonStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button5 = Button(window, Point(97, 12), Point(111, 14), text="5",
                 style=ButtonStyle(term.on_red4, term.white),
                 selected_style=ButtonStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)


window.clear()
for element in window.interactable:
    element.draw()
window.loop()

print(term.home)
