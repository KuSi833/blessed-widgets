from widgets import Window, Button, Point
from blessed import Terminal

term = Terminal()

window = Window(term)
enterButton = Button(window, Point(2, 2), "Check")

window.clear()
enterButton.draw()
