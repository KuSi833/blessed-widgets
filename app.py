from blessed import Terminal
from blessed_extension import Button

term = Terminal()

print(term.home + term.clear + term.move_x(term.height // 2))

some_text = input()

print(term.move_down(5) + term.orange(some_text))


class Mainframe():
    def __init__(self) -> None:
        self.term = Terminal()


    def main_menu(self) -> None:
