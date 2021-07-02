from __future__ import annotations
from widgets import AbsoluteFrame, GridFrame, Label, DropdownMenu, OptionMenu, Window, Button, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    gridframe = GridFrame(window.mainframe, widths=[2, 4, 6, 8], heights=[1, 2, 3],
                          style=RectangleStyle(bg_color=term.on_gray14,
                                               border_style=BorderStyle.SINGLE,
                                               border_color=term.orange),
                          inner_border=True)
    gridframe.place(35, 5)
    button1 = Button(gridframe, width=1, height=1, command=lambda: print("o"), text="o",
                     style=RectangleStyle(bg_color=term.on_red),
                     selected_style=RectangleStyle(bg_color=term.on_blue))
    button1.grid(1, 1, rowspan=1, columnspan=2)
    button2 = Button(gridframe, width=1, height=1, command=lambda: print("o"), text="o",
                     style=RectangleStyle(bg_color=term.on_red),
                     selected_style=RectangleStyle(bg_color=term.on_blue))
    button2.grid(1, 2, rowspan=1, columnspan=2)
    # button3 = Button(gridframe, width=1, height=1, command=lambda: print("o"), text="o",
    #                  style=RectangleStyle(bg_color=term.on_red),
    #                  selected_style=RectangleStyle(bg_color=term.on_blue))
    # button3.grid(0, 2)
    # button4 = Button(gridframe, width=1, height=1, command=lambda: print("o"), text="o",
    #                  style=RectangleStyle(bg_color=term.on_red),
    #                  selected_style=RectangleStyle(bg_color=term.on_blue))
    # button4.grid(2, 0)

    window.clear()
    window.draw()
    window.loop()
    # window.clear()
    window.flush()
