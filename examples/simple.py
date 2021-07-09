from __future__ import annotations
from blessed_widgets.widgets import AbsoluteFrame, GridFrame, Label, DropdownMenu, OptionMenu, Window, Button, BoxStyle, Entry
from blessed import Terminal
from blessed_widgets.constants import BorderStyle, HAlignment, VAlignment

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    gridframe = GridFrame(window.mainframe,
                          widths=[2, 4, 6, 8],
                          heights=[1, 2, 3],
                          style=BoxStyle(bg_color=term.on_gray14,
                                               border_style=BorderStyle.SINGLE,
                                               border_color=term.orange),
                          inner_border=True)
    gridframe.place(35, 5)
    button1 = Button(gridframe,
                     width=4,
                     height=1,
                     command=lambda: print("o"),
                     text="o",
                     style=BoxStyle(bg_color=term.on_red),
                     selected_style=BoxStyle(bg_color=term.on_blue))
    button1.grid(1, 0, rowspan=2, columnspan=1)
    button2 = Button(gridframe,
                     width=6,
                     height=2,
                     command=lambda: print("o"),
                     text="o",
                     style=BoxStyle(bg_color=term.on_red),
                     selected_style=BoxStyle(bg_color=term.on_blue))
    button2.grid(2, 1, rowspan=1, columnspan=2)
    button3 = Button(gridframe,
                     width=8,
                     height=3,
                     command=lambda: print("o"),
                     text="o",
                     style=BoxStyle(bg_color=term.on_red),
                     selected_style=BoxStyle(bg_color=term.on_blue))
    button3.grid(3, 2, rowspan=1, columnspan=1)

    window.clear()
    window.draw()
    window.loop()
    window.flush()
    window.clear()
