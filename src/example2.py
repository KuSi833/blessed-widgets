from __future__ import annotations
from widgets import Frame, Label, DropdownMenu, OptionMenu, Window, Button, Point, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    title = Label(window.mainframe, Point(67, 14), Point(93, 14),
                  text="Button and frame example")

# Labels
    frame1 = Frame(window.mainframe, Point(63, 11), Point(100, 5))
    frame2 = Frame(window.mainframe, Point(60, 8), Point(100, 11))
    frame3 = Frame(window.mainframe, Point(63, 11), Point(98, 5))
    entry1 = Entry(frame1, Point(64, 9), Point(97, 7), default_text="default",
                   style=RectangleStyle(),
                   selected_style=RectangleStyle(border_color=term.yellow),
                   focused_style=RectangleStyle(border_color=term.orange))
    dropdownMenu = DropdownMenu(frame2, Point(64, 11), Point(77, 11), text="Menu",
                                style=RectangleStyle(text_style=term.white, bg_color=term.on_deepskyblue2),
                                selected_style=RectangleStyle(text_style=term.gray38, bg_color=term.on_goldenron1))
    dropdownMenu.addItem("Print 1", lambda: print("1"))
    dropdownMenu.addItem("Entry", lambda: print(entry1.getSavedText()))
    optionMenu = OptionMenu(frame2, Point(84, 11), Point(97, 11), default_text="Beginner",
                            options=["Beginner", "Intermediate", "Expert"],
                            style=RectangleStyle(text_style=term.white, bg_color=term.on_slateblue1),
                            selected_style=RectangleStyle(text_style=term.gray38, bg_color=term.on_goldenron1))
    dropdownMenu.addItem("OptionsMenu", lambda: print(optionMenu.getValue()))
    label3 = Label(frame3, Point(75, 9), Point(86, 7), "Frame 3",
                   style=RectangleStyle(text_style=term.red4, border_style=BorderStyle.SINGLE))

    # Functions

    def frame1toggle():
        frame2.deactivate()
        frame3.deactivate()
        frame1.activate()

    def frame2toggle():
        frame1.deactivate()
        frame3.deactivate()
        frame2.activate()

    def frame3toggle():
        frame1.deactivate()
        frame2.deactivate()
        frame3.activate()

    # Buttons
    buttonFrame = Frame(window.mainframe, Point(64, 2), Point(97, 4))
    button1 = Button(buttonFrame, Point(64, 2), Point(75, 4), text="Entry", command=frame1toggle,
                     style=RectangleStyle(term.on_darkorange2, term.white),
                     selected_style=RectangleStyle(term.on_darkorange2, term.underline_yellow,
                                                   border_style=BorderStyle.SINGLE))
    button2 = Button(buttonFrame, Point(75, 2), Point(86, 4), text="Dropdowns", command=frame2toggle,
                     style=RectangleStyle(term.on_darkgreen, term.white),
                     selected_style=RectangleStyle(term.on_darkgreen, term.underline_yellow,
                                                   border_style=BorderStyle.DOUBLE))
    button3 = Button(buttonFrame, Point(86, 2), Point(97, 4), text="Label", command=frame3toggle,
                     style=RectangleStyle(term.on_red4, term.white),
                     selected_style=RectangleStyle(term.on_red4, term.underline_yellow,
                                                   border_style=BorderStyle.SINGLE))

    # Init
    window.clear()
    frame2.deactivate()
    frame3.deactivate()
    frame1.activate()  # Unnecesary cause all elements are shown by default
    window.draw()
    window.loop()

    print(term.home)
