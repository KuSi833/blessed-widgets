from blessed_extension import Button
from blessed import Terminal

term = Terminal()

print(term.clear)

button = Button(term, x=15, y=10, h=2, w=3, text="check", text_color=term.black, bg=term.on_orange)
print(button, end='')

any_key = input()

print(term.home + term.clear)
