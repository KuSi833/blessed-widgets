from __future__ import annotations
from widgets import AbsoluteFrame, GridFrame, Label, DropdownMenu, OptionMenu, Window, Button, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    mainframe = AbsoluteFrame(window.mainframe, 60, 20,
                              style=RectangleStyle(bg_color=term.on_gray14, text_style=term.orange,
                                                   border_style=BorderStyle.SINGLE))
    mainframe.place(15, 3)
    # Title
    title = Label(mainframe, width=20, height=1, text=" Sound Recognition ",
                  style=RectangleStyle(text_style=term.orange))
    title.place(x=10, y=0)

    selectionFrame = AbsoluteFrame(mainframe, 34, 3, style=RectangleStyle(bg_color=term.on_gray20))
    selectionFrame.place(x=2, y=15)

    # Dropdowns
    levelLabel = Label(selectionFrame, width=6, height=1, text="Level: ",
                       style=RectangleStyle(text_style=term.white))
    levelLabel.place(x=0, y=2)
    levelOptions = OptionMenu(selectionFrame, 14, 1, "Beginner", options=["Beginner", "Intermediate", "Advanced"],
                              style=RectangleStyle(bg_color=term.on_deepskyblue3, text_style=term.white),
                              selected_style=RectangleStyle(bg_color=term.on_dodgerblue3, text_style=term.white),
                              focused_style=RectangleStyle(bg_color=term.on_skyblue2, text_style=term.white))
    levelOptions.place(x=6, y=2)
    # stageLabel = Label(selectionFrame, width=6, height=1, text="Stage: ",
    #                    style=RectangleStyle(text_style=term.white))
    # stageLabel.place(x=2, y=9)
    # stageOptions = OptionMenu(selectionFrame, 5, 1, "1", options=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
    #                           style=RectangleStyle(bg_color=term.on_mediumpurple2, text_style=term.white),
    #                           selected_style=RectangleStyle(bg_color=term.on_purple3, text_style=term.white),
    #                           focused_style=RectangleStyle(bg_color=term.on_purple3, text_style=term.white))
    # stageOptions.place(x=9, y=9)
    # disciplineLabel = Label(selectionFrame, width=12, height=1, text="Discipline: ",
    #                         style=RectangleStyle(text_style=term.white))
    # disciplineLabel.place(x=16, y=9)
    # disciplineOptions = OptionMenu(selectionFrame, 5, 1, "CQR", options=["CQR", "SSR", "CPR"],
    #                                style=RectangleStyle(bg_color=term.on_green4, text_style=term.white),
    #                                selected_style=RectangleStyle(bg_color=term.on_darkgreen, text_style=term.white),
    #                                focused_style=RectangleStyle(bg_color=term.on_darkgreen, text_style=term.white))
    # disciplineOptions.place(x=28, y=9)

    # enterButton = Button(mainframe, width=7, height=1, text="Enter", command=lambda: print(1),
    #                      style=RectangleStyle(bg_color=term.on_orange2, text_style=term.black),
    #                      selected_style=RectangleStyle(bg_color=term.on_orangered, text_style=term.black))
    # enterButton.place(x=26, y=11)

    frame1 = AbsoluteFrame(mainframe, 36, 6, style=RectangleStyle(bg_color=term.on_gray32))
    frame1.place(2, 2)
    table = GridFrame(mainframe, widths=[5, 5, 5, 5, 5], heights=[2, 2],
                      style=RectangleStyle(bg_color=term.on_gray14,
                                           border_style=BorderStyle.SINGLE,
                                           border_color=term.orange),
                      inner_border=True)
    table.place(5, 5)

    # Frame 1
    table.deactivate()
    window.clear()
    window.draw()
    window.loop()
    # window.clear()
    window.flush()
