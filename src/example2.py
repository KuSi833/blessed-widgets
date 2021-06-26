from __future__ import annotations
from widgets import Frame, Label, OptionMenu, Window, Button, Point, RectangleStyle, Entry
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()
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
optionsMenu = OptionMenu(frame2, Point(75, 11), Point(86, 11), ["Beginner", "Intermediate"],
                         style=RectangleStyle(text_style=term.white, bg_color=term.on_deepskyblue2),
                         selected_style=RectangleStyle(text_style=term.gray38, bg_color=term.on_goldenron1))
label3 = Label(frame3, Point(75, 9), Point(86, 7), "Frame 3",
               style=RectangleStyle(text_style=term.red4, border_style=BorderStyle.SINGLE))

# Functions


def frame1toggle():
    frame2.hide()
    frame3.hide()
    frame1.show()


def frame2toggle():
    frame1.hide()
    frame3.hide()
    frame2.show()


def frame3toggle():
    frame1.hide()
    frame2.hide()
    frame3.show()


# Buttons
buttonFrame = Frame(window.mainframe, Point(64, 2), Point(97, 4))
button1 = Button(buttonFrame, Point(64, 2), Point(75, 4), text="Frame 1", command=frame1toggle,
                 style=RectangleStyle(term.on_darkorange2, term.white),
                 selected_style=RectangleStyle(term.on_darkorange2, term.underline_yellow,
                                               border_style=BorderStyle.SINGLE))
button2 = Button(buttonFrame, Point(75, 2), Point(86, 4), text="Frame 2", command=frame2toggle,
                 style=RectangleStyle(term.on_darkgreen, term.white),
                 selected_style=RectangleStyle(term.on_darkgreen, term.underline_yellow,
                                               border_style=BorderStyle.DOUBLE))
button3 = Button(buttonFrame, Point(86, 2), Point(97, 4), text="Frame 3", command=frame3toggle,
                 style=RectangleStyle(term.on_red4, term.white),
                 selected_style=RectangleStyle(term.on_red4, term.underline_yellow,
                                               border_style=BorderStyle.SINGLE))

# Init
with term.hidden_cursor():
    window.clear()
    frame2.hide()
    frame3.hide()
    frame1.show()  # Unnecesary cause all elements are shown by default
    window.draw()
    window.loop()

print(term.home)
