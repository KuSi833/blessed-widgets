from __future__ import annotations
from widgets import Frame, Label, Window, Button, Point, RectangleStyle
from blessed import Terminal
from constants import BorderStyle, HAlignment, VAlignment
from time import sleep, time

term = Terminal()
window = Window(term)
title = Label(window.mainframe,
              Point((term.width // 2) - 28, term.height - 5),
              Point((term.width // 2) + 24, term.height - 5),
              text="Button and frame example")

# Labels
frame1 = Frame(window.mainframe, Point(63, 11), Point(98, 5))
frame2 = Frame(window.mainframe, Point(63, 11), Point(98, 5))
frame3 = Frame(window.mainframe, Point(63, 11), Point(98, 5))
label1 = Label(frame1, Point(75, 9), Point(86, 7), "Frame 1",
               style=RectangleStyle(text_style=term.darkorange2, border_style=BorderStyle.SINGLE))
label2 = Label(frame2, Point(75, 9), Point(86, 7), "Frame 2",
               style=RectangleStyle(text_style=term.darkgreen, border_style=BorderStyle.DOUBLE))
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

with term.hidden_cursor():
    window.clear()
    window.draw()
    window.loop()

print(term.home)
