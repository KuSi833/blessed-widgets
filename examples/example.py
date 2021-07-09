from __future__ import annotations
from blessed_widgets.widgets import (AbsoluteFrame, GridFrame, Label,
                                     DropdownMenu, OptionMenu, Window, Button,
                                     BoxStyle, Entry)
from blessed import Terminal
from blessed_widgets.constants import BorderStyle, HAlignment, VAlignment

term = Terminal()
with term.hidden_cursor():
    window = Window(term)
    mainframe = AbsoluteFrame(window.mainframe,
                              40,
                              14,
                              style=BoxStyle(bg_color=term.on_gray14,
                                             text_style=term.orange,
                                             border_style=BorderStyle.SINGLE))
    mainframe.place(x=15, y=2)

    title = Label(mainframe, width=11, height=1, text="Example")
    title.place(x=15, y=0)
    frame1 = AbsoluteFrame(mainframe,
                           36,
                           6,
                           style=BoxStyle(bg_color=term.on_gray32))
    frame1.place(x=2, y=2)
    frame2 = AbsoluteFrame(mainframe, 36, 6)
    frame2.place(x=2, y=2)
    frame3 = GridFrame(mainframe,
                       widths=[5, 5, 5, 5, 5],
                       heights=[2, 2],
                       style=BoxStyle(bg_color=term.on_gray14,
                                      border_style=BorderStyle.SINGLE,
                                      border_color=term.orange),
                       inner_border=True)
    frame3.place(x=5, y=2)

    # # Frame 1
    entry = Entry(frame1,
                  width=34,
                  height=3,
                  default_text="default",
                  style=BoxStyle(bg_color=term.on_gray12),
                  selected_style=BoxStyle(bg_color=term.on_gray12,
                                          border_color=term.yellow),
                  focused_style=BoxStyle(bg_color=term.on_gray12,
                                         border_color=term.orange))
    entry.place(1, 1)
    # # Frame 2
    dropdownMenu = DropdownMenu(frame2,
                                width=12,
                                height=1,
                                text="Menu",
                                style=BoxStyle(text_style=term.white,
                                               bg_color=term.on_deepskyblue2),
                                selected_style=BoxStyle(text_style=term.gray38,
                                                        bg_color=term.on_white))
    optionMenu = OptionMenu(frame2,
                            width=12,
                            height=1,
                            default_text="Beginner",
                            options=["Beginner", "Intermediate", "Expert"],
                            style=BoxStyle(text_style=term.white,
                                           bg_color=term.on_slateblue1),
                            selected_style=BoxStyle(text_style=term.gray38,
                                                    bg_color=term.on_white))
    optionMenu.place(23, 0)
    dropdownMenu.addItem("Entry", lambda: print(entry.getSavedText()))
    dropdownMenu.addItem("OptionsMenu", lambda: print(optionMenu.getValue()))
    label = Label(frame2,
                  width=24,
                  height=3,
                  text="Frame 3",
                  style=BoxStyle(text_style=term.darkturquoise,
                                 border_style=BorderStyle.SINGLE,
                                 bg_color=term.on_gray12))
    label.place(6, 4)
    dropdownMenu.addItem("Label", lambda: label.setText(entry.getSavedText()))
    dropdownMenu.place(1, 0)
    # # Frame 3
    gridbutton = Button(frame3,
                        9,
                        2,
                        text="0",
                        command=lambda: print("0"),
                        style=BoxStyle(bg_color=term.on_red,
                                       text_style=term.black),
                        selected_style=BoxStyle(bg_color=term.on_blue,
                                                text_style=term.black))
    gridbutton.grid(2, 1, columnspan=2, padx=1)
    gridbutton2 = Button(frame3,
                         3,
                         5,
                         text="1",
                         command=lambda: print("1"),
                         style=BoxStyle(bg_color=term.on_green,
                                        text_style=term.black),
                         selected_style=BoxStyle(bg_color=term.on_orange,
                                                 text_style=term.black))
    gridbutton2.grid(4, 0, rowspan=2, padx=1)
    gridentry = Entry(frame3,
                      15,
                      2,
                      style=BoxStyle(bg_color=term.on_gray24,
                                     text_style=term.black,
                                     border_style=BorderStyle.NONE),
                      selected_style=BoxStyle(bg_color=term.on_gray34,
                                              text_style=term.black,
                                              border_style=BorderStyle.NONE),
                      focused_style=BoxStyle(bg_color=term.on_gray34,
                                             text_style=term.black,
                                             border_style=BorderStyle.NONE))
    gridentry.grid(0, 0, columnspan=3, padx=1)

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

    buttonFrame = AbsoluteFrame(mainframe, 38, 3)
    buttonFrame.place(1, 10)
    button1 = Button(buttonFrame,
                     width=12,
                     height=3,
                     text="Entry",
                     command=frame1toggle,
                     style=BoxStyle(term.on_darkorange2, term.white),
                     selected_style=BoxStyle(term.on_darkorange2,
                                             term.underline_yellow,
                                             border_style=BorderStyle.SINGLE))
    button1.place(1, 0)
    button2 = Button(buttonFrame,
                     width=12,
                     height=3,
                     text="Dropdowns",
                     command=frame2toggle,
                     style=BoxStyle(term.on_darkgreen, term.white),
                     selected_style=BoxStyle(term.on_darkgreen,
                                             term.underline_yellow,
                                             border_style=BorderStyle.DOUBLE))
    button2.place(13, 0)
    button3 = Button(buttonFrame,
                     width=12,
                     height=3,
                     text="Label",
                     command=frame3toggle,
                     style=BoxStyle(term.on_red4, term.white),
                     selected_style=BoxStyle(term.on_red4,
                                             term.underline_yellow,
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
