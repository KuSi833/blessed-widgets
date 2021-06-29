from __future__ import annotations
from widgets import Frame, Label, DropdownMenu, OptionMenu, Window, Button, Point, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    mainframe = Frame(window.mainframe, 40, 14,
                      style=RectangleStyle(bg_color=term.on_gray14, text_style=term.orange,
                                           border_style=BorderStyle.SINGLE))
    mainframe.place(15, 2)
    # Elements

    title = Label(mainframe, width=11, height=1, text="Example")
    title.place(x=14, y=12)

    # Placement
    # Init
    window.clear()
    window.draw()
    window.loop()
    print(term.home)
