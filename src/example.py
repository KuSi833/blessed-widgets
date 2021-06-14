from widgets import Square, Window, Button, Point
from blessed import Terminal

term = Terminal()

window = Window(term)
enterButton = Button(window, Point(2, 2), "Check")
square = Square(window, Point(2, 2), Point(6, 6), term.on_orange)

window.clear()
square.draw()
# enterButton.draw()
