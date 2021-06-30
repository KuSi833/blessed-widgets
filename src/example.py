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

    title = Label(mainframe, width=11, height=1, text="Example")
    title.place(x=15, y=13)
    frame1 = Frame(mainframe, 36, 6, style=RectangleStyle(bg_color=term.on_gray32))
    frame1.place(2, 6)
    frame2 = Frame(mainframe, 36, 6)
    frame2.place(2, 6)
    frame3 = Frame(mainframe, 36, 6)
    frame3.place(2, 6)

    # Frame 1
    entry = Entry(frame1, width=34, height=3, default_text="default",
                  style=RectangleStyle(bg_color=term.on_gray14),
                  selected_style=RectangleStyle(bg_color=term.on_gray14, border_color=term.yellow),
                  focused_style=RectangleStyle(bg_color=term.on_gray14, border_color=term.orange))
    entry.place(1, 2)
    # Frame 2
    dropdownMenu = DropdownMenu(frame2, width=12, height=1, text="Menu",
                                style=RectangleStyle(text_style=term.white, bg_color=term.on_deepskyblue2),
                                selected_style=RectangleStyle(text_style=term.gray38, bg_color=term.on_white))
    optionMenu = OptionMenu(frame2, width=12, height=1, default_text="Beginner",
                            options=["Beginner", "Intermediate", "Expert"],
                            style=RectangleStyle(text_style=term.white, bg_color=term.on_slateblue1),
                            selected_style=RectangleStyle(text_style=term.gray38, bg_color=term.on_white))
    optionMenu.place(21, 4)
    dropdownMenu.addItem("Entry", lambda: print(entry.getSavedText()))
    dropdownMenu.addItem("OptionsMenu", lambda: print(optionMenu.getValue()))
    # Frame 3
    label = Label(frame3, width=24, height=3, text="Frame 3",
                  style=RectangleStyle(text_style=term.red4, border_style=BorderStyle.SINGLE))
    label.place(6, 2)
    dropdownMenu.addItem("Label", lambda: label.setText(entry.getSavedText()))
    dropdownMenu.place(1, 4)

    # ButtonFrame

    def frame1toggle():
        frame2.deactivate()
        frame3.deactivate()
        frame1.activate()
        frame1.draw()

    def frame2toggle():
        frame1.deactivate()
        frame3.deactivate()
        frame2.activate()
        frame2.draw()

    def frame3toggle():
        frame1.deactivate()
        frame2.deactivate()
        frame3.activate()
        frame3.draw()

    buttonFrame = Frame(mainframe, 38, 5)
    buttonFrame.place(1, 1)
    button1 = Button(buttonFrame, width=12, height=3, text="Entry", command=frame1toggle,
                     style=RectangleStyle(term.on_darkorange2, term.white),
                     selected_style=RectangleStyle(term.on_darkorange2, term.underline_yellow,
                                                   border_style=BorderStyle.SINGLE))
    button1.place(1, 0)
    button2 = Button(buttonFrame, width=12, height=3, text="Dropdowns", command=frame2toggle,
                     style=RectangleStyle(term.on_darkgreen, term.white),
                     selected_style=RectangleStyle(term.on_darkgreen, term.underline_yellow,
                                                   border_style=BorderStyle.DOUBLE))
    button2.place(13, 0)
    button3 = Button(buttonFrame, width=12, height=3, text="Label", command=frame3toggle,
                     style=RectangleStyle(term.on_red4, term.white),
                     selected_style=RectangleStyle(term.on_red4, term.underline_yellow,
                                                   border_style=BorderStyle.SINGLE))
    button3.place(25, 0)

    # Init
    frame1.activate()
    frame2.deactivate()
    frame3.deactivate()
    window.clear()
    window.draw()
    window.loop()
    # window.clear()
    window.flush()
