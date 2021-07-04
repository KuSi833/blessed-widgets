from __future__ import annotations
from typing import List
from widgets import AbsoluteFrame, GridFrame, Label, DropdownMenu, OptionMenu, Window, Button, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, Direction, HAlignment, VAlignment

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    mainframe = AbsoluteFrame(window.mainframe, 38, 23,
                              style=RectangleStyle(bg_color=term.on_gray14, text_style=term.orange,
                                                   border_style=BorderStyle.SINGLE))
    mainframe.place(x=15, y=3)
    # Title
    title = Label(mainframe, width=19, height=1, text=" Sound Recognition ",
                  style=RectangleStyle(text_style=term.orange))
    title.place(x=10, y=0)

    selectionFrame = AbsoluteFrame(mainframe, 34, 3)
    selectionFrame.place(x=2, y=2)

    # Dropdowns
    selected_style = RectangleStyle(bg_color=term.on_white, text_style=term.black)
    levelLabel = Label(selectionFrame, width=6, height=1, text="Level: ",
                       style=RectangleStyle(text_style=term.white))
    levelLabel.place(x=1, y=0)
    levelOptions = OptionMenu(selectionFrame, 14, 1, "Beginner", options=["Beginner", "Intermediate", "Advanced"],
                              style=RectangleStyle(bg_color=term.on_deepskyblue2, text_style=term.white),
                              selected_style=selected_style,
                              focused_style=RectangleStyle(bg_color=term.on_skyblue2, text_style=term.white))
    levelOptions.place(x=8, y=0)
    stageLabel = Label(selectionFrame, width=6, height=1, text="Stage: ",
                       style=RectangleStyle(text_style=term.white))
    stageLabel.place(x=1, y=2)
    stageOptions = OptionMenu(selectionFrame, 5, 1, "1", options=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
                              style=RectangleStyle(bg_color=term.on_mediumpurple2, text_style=term.white),
                              selected_style=selected_style,
                              focused_style=RectangleStyle(bg_color=term.on_purple3, text_style=term.white))
    stageOptions.place(x=8, y=2)
    disciplineLabel = Label(selectionFrame, width=12, height=1, text="Discipline: ",
                            style=RectangleStyle(text_style=term.white))
    disciplineLabel.place(x=16, y=2)
    disciplineOptions = OptionMenu(selectionFrame, 5, 1, "CQR", options=["CQR", "SSR", "CPR"],
                                   style=RectangleStyle(bg_color=term.on_darkorange3, text_style=term.white),
                                   selected_style=selected_style,
                                   focused_style=RectangleStyle(bg_color=term.on_darkgreen, text_style=term.white))
    disciplineOptions.place(x=28, y=2)

    enterButton = Button(selectionFrame, width=7, height=1, text="Enter", command=lambda: print(1),
                         style=RectangleStyle(bg_color=term.on_darkgreen, text_style=term.white),
                         selected_style=selected_style)
    enterButton.place(x=26, y=0)
    # Navigation Override
    stageOptions.overrideNavigation(Direction.RIGHT, disciplineOptions)
    disciplineOptions.overrideNavigation(Direction.LEFT, stageOptions)
    levelOptions.overrideNavigation(Direction.DOWN, stageOptions)

    # Main Content
    frame1 = AbsoluteFrame(mainframe, 33, 13, style=RectangleStyle(bg_color=term.on_gray22))
    frame1.place(3, 6)
    table = GridFrame(frame1, widths=[3, 6], heights=[1, 1, 1, 1, 1],
                      style=RectangleStyle(bg_color=term.on_gray14,
                                           border_style=BorderStyle.SINGLE,
                                           border_color=term.orange),
                      inner_border=True)
    table.place(2, 1)
    table2 = GridFrame(frame1, widths=[3, 6], heights=[1, 1, 1, 1, 1],
                       style=RectangleStyle(bg_color=term.on_gray14,
                                            border_style=BorderStyle.SINGLE,
                                            border_color=term.orange),
                       inner_border=True)
    table2.place(19, 1)

    labels: List[Label] = []
    entries: List[Entry] = []
    for i in range(5):
        label = Label(table, width=3, height=1, text=str(i + 1) + ".", h_align=HAlignment.RIGHT,
                      style=RectangleStyle(text_style=term.white))
        label.grid(0, i)
        labels.append(label)
        entry = Entry(
            table, width=6, height=1, default_text="______",
            style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray10, text_style=term.white),
            selected_style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray8),
            focused_style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray8),)
        entry.grid(1, i)
        entries.append(entry)
    for i in range(5):
        label = Label(table2, width=3, height=1, text=str(i + 6) + ".", h_align=HAlignment.RIGHT,
                      style=RectangleStyle(text_style=term.white))
        label.grid(0, i)
        labels.append(label)
        entry = Entry(
            table2, width=6, height=1, default_text="______",
            style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray10, text_style=term.white),
            selected_style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray8),
            focused_style=RectangleStyle(border_style=BorderStyle.NONE, bg_color=term.on_gray8),)
        entry.grid(1, i)
        entries.append(entry)

    buttonFrame = AbsoluteFrame(mainframe, 34, 1)
    buttonFrame.place(1, 20)
    checkButton = Button(buttonFrame, width=12, height=1, text="Check", command=lambda: print("lol"),
                         style=RectangleStyle(term.on_darkgreen, term.white),
                         selected_style=RectangleStyle(bg_color=term.on_white, text_style=term.black))
    checkButton.place(4, 0)
    clearButton = Button(buttonFrame, width=12, height=1, text="Clear", command=lambda: print("lol"),
                         style=RectangleStyle(term.on_red4, term.white),
                         selected_style=RectangleStyle(bg_color=term.on_white, text_style=term.black))
    clearButton.place(21, 0)
    # table.deactivate()
    window.clear()
    window.draw()
    window.loop()
    # window.clear()
    window.flush()
