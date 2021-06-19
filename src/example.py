from __future__ import annotations
from widgets import Label, Window, Button, Point, LabelStyle
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()
window = Window(term)
title = Label(window.mainframe,
              Point((term.width // 2) - 8, term.height - 2),
              Point((term.width // 2) + 8, term.height - 2),
              text="This is a test program")

button1 = Button(window.mainframe, Point(82, 5), Point(90, 7), text="main", command=lambda: print("main"),
                 selected_style=LabelStyle(term.on_darkgreen, term.underline_yellow,
                                           border_color=term.white, border_style=BorderStyle.DOUBLE),
                 style=LabelStyle(term.on_darkgreen, term.white),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button2 = Button(window.mainframe, Point(75, 5), Point(77, 7), text="1", command=lambda: print("1"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow,
                                           border_color=term.white, border_style=BorderStyle.SINGLE),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)


window.clear()
window.mainframe.draw()
window.loop()

print(term.home)
