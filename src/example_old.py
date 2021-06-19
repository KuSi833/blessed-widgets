from __future__ import annotations
from widgets import Label, Window, Button, Point, LabelStyle
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()

window = Window(term)

title = Label(window,
              Point((term.width // 2) - 8, term.height - 2),
              Point((term.width // 2) + 8, term.height - 2),
              text="This is a test program")

mainButton = Button(window, Point(82, 5), Point(90, 7), text="main", command=lambda: print("main"),
                    selected_style=LabelStyle(term.on_darkgreen, term.underline_yellow,
                                              border_color=term.white, border_style=BorderStyle.DOUBLE),
                    style=LabelStyle(term.on_darkgreen, term.white),
                    h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button1 = Button(window, Point(75, 5), Point(77, 7), text="1", command=lambda: print("1"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow,
                                           border_color=term.white, border_style=BorderStyle.SINGLE),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button2 = Button(window, Point(80, 0), Point(95, 2), text="2", command=lambda: print("2"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow,
                                           border_color=term.white, border_style=BorderStyle.SINGLE),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button3 = Button(window, Point(88, 10), Point(90, 13), text="3", command=lambda: print("3"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow,
                                           border_color=term.white, border_style=BorderStyle.SINGLE),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button4 = Button(window, Point(102, 5), Point(110, 7), text="4", command=lambda: print("4"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)
button5 = Button(window, Point(97, 12), Point(111, 14), text="5", command=lambda: print("5"),
                 style=LabelStyle(term.on_red4, term.white),
                 selected_style=LabelStyle(term.on_red4, term.underline_yellow,
                                           border_color=term.white),
                 h_align=HAlignment.MIDDLE, v_align=VAlignment.MIDDLE)


window.clear()
for element in window.elements:
    element.draw()
window.loop()

print(term.home)
