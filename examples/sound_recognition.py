# typing
from __future__ import annotations
from typing import List, Optional

# 3rd party
from blessed import Terminal
import json

# local
from blessed_widgets.widgets import (AbsoluteFrame, GridFrame, Label,
                                     DropdownMenu, OptionMenu, Window, Button,
                                     BoxStyle, Entry)
from blessed_widgets.constants import (BorderStyle, Direction, HAlignment,
                                       VAlignment)


class Application(Window):

    def __init__(self, term: Terminal) -> None:
        super().__init__(term)
        self.baseframe = AbsoluteFrame(self.mainframe,
                                       width=39,
                                       height=23,
                                       style=BoxStyle(
                                           bg_color=term.on_gray14,
                                           text_style=term.orange,
                                           border_style=BorderStyle.SINGLE))
        self.baseframe.place(x=15, y=3)
        # Title
        self.title = Label(self.baseframe,
                           width=19,
                           height=1,
                           text=" Sound Recognition ",
                           style=BoxStyle(text_style=term.orange))
        self.title.place(x=10, y=0)

        # Dropdowns
        self.selectionFrame = AbsoluteFrame(self.baseframe, 34, 3)
        self.selectionFrame.place(x=2, y=2)
        self.selected_style = BoxStyle(bg_color=term.on_white,
                                       text_style=term.black)

        self.levelLabel = Label(self.selectionFrame,
                                width=6,
                                height=1,
                                text="Level: ",
                                style=BoxStyle(text_style=term.white))
        self.levelLabel.place(x=1, y=0)

        self.levelOptions = OptionMenu(
            self.selectionFrame,
            width=14,
            height=1,
            default_text="Beginner",
            options=["Beginner", "Intermediate", "Advanced"],
            style=BoxStyle(bg_color=term.on_deepskyblue2,
                           text_style=term.white),
            selected_style=self.selected_style,
            focused_style=BoxStyle(bg_color=term.on_skyblue2,
                                   text_style=term.white))
        self.levelOptions.place(x=8, y=0)

        self.stageLabel = Label(self.selectionFrame,
                                width=6,
                                height=1,
                                text="Stage: ",
                                style=BoxStyle(text_style=term.white))
        self.stageLabel.place(x=1, y=2)

        self.stageOptions = OptionMenu(
            self.selectionFrame,
            width=5,
            height=1,
            default_text="1",
            options=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
            style=BoxStyle(bg_color=term.on_mediumpurple2,
                           text_style=term.white),
            selected_style=self.selected_style,
            focused_style=BoxStyle(bg_color=term.on_purple3,
                                   text_style=term.white))
        self.stageOptions.place(x=8, y=2)

        self.disciplineLabel = Label(self.selectionFrame,
                                     width=12,
                                     height=1,
                                     text="Discipline: ",
                                     style=BoxStyle(text_style=term.white))
        self.disciplineLabel.place(x=17, y=2)

        self.disciplineOptions = OptionMenu(
            self.selectionFrame,
            width=5,
            height=1,
            default_text="CQR",
            options=["CQR", "SSR", "CPR"],
            style=BoxStyle(bg_color=term.on_darkorange3, text_style=term.white),
            selected_style=self.selected_style,
            focused_style=BoxStyle(bg_color=term.on_darkgreen,
                                   text_style=term.white))
        self.disciplineOptions.place(x=29, y=2)

        self.enterButton = Button(self.selectionFrame,
                                  width=7,
                                  height=1,
                                  text="Enter",
                                  command=lambda: print(1),
                                  style=BoxStyle(bg_color=term.on_darkgreen,
                                                 text_style=term.white),
                                  selected_style=self.selected_style)
        self.enterButton.place(x=27, y=0)

        # Navigation Override
        self.stageOptions.overrideNavigation(Direction.RIGHT,
                                             self.disciplineOptions)
        self.disciplineOptions.overrideNavigation(Direction.LEFT,
                                                  self.stageOptions)
        self.levelOptions.overrideNavigation(Direction.DOWN, self.stageOptions)

        # Buttonframe
        self.buttonFrame = AbsoluteFrame(self.baseframe, 34, 1)
        self.buttonFrame.place(1, 20)

        self.checkButton = Button(self.buttonFrame,
                                  width=12,
                                  height=1,
                                  text="Check",
                                  style=BoxStyle(term.on_darkgreen, term.white),
                                  selected_style=BoxStyle(
                                      bg_color=term.on_white,
                                      text_style=term.black))
        self.checkButton.place(4, 0)

        self.clearButton = Button(self.buttonFrame,
                                  width=12,
                                  height=1,
                                  text="Clear",
                                  command=self.clearEntries,
                                  style=BoxStyle(term.on_red4, term.white),
                                  selected_style=BoxStyle(
                                      bg_color=term.on_white,
                                      text_style=term.black))
        self.clearButton.place(21, 0)

        self.enterButton.onClick(self.getAnswers)

        self.logLabel = Label(self.buttonFrame,
                              width=18,
                              height=1,
                              h_align=HAlignment.MIDDLE,
                              style=BoxStyle(bg_color=term.on_gray10))
        self.logLabel.place(10, 0)

        # Data
        self.getData()

        # Key bindings
        self.bind("c", self.clearButton.click)

        # Holders
        self.frameType1: Optional[AbsoluteFrame] = None
        self.labels: List[Label] = []
        self.entries: List[Entry] = []

        # Init activations
        self.checkButton.deactivate()
        self.clearButton.deactivate()
        self.logLabel.deactivate()

    def getData(self) -> None:
        with open('resources/sound_recognition_data.json') as file:
            self.data = json.load(file)

    def getAnswers(self) -> None:
        level = self.levelOptions.getValue()
        stage = self.stageOptions.getValue()
        discipline = self.disciplineOptions.getValue()
        if self.frameType1:
            self.frameType1.remove()
            self.frameType1 = None
        try:
            self.answers = self.data[level][stage][discipline]
            self.logLabel.setText("")
            self.logLabel.deactivate()
            if discipline == "SSR" or discipline == "CQR":
                self.initType1(self.answers)
            elif discipline == "CPR":
                self.initType2(self.answers)
        except KeyError:
            if self.logLabel.text == "No data found":
                self.logLabel.setText(".No data found.")
            else:
                self.logLabel.setText("No data found")
            self.checkButton.deactivate()
            self.clearButton.deactivate()
            self.logLabel.activate()
            self.logLabel.draw()

    def checkAnswers(self) -> None:
        for i, entry in enumerate(self.entries):
            entry_text = entry.text.replace(" ", "").lower()
            answer_text = self.answers[i].replace(" ", "").lower()
            if entry_text == answer_text:
                entry.setStyle(
                    BoxStyle(border_style=BorderStyle.NONE,
                             bg_color=term.on_gray10,
                             text_style=term.green))
            else:
                entry.setStyle(
                    BoxStyle(border_style=BorderStyle.NONE,
                             bg_color=term.on_gray10,
                             text_style=term.red))
            entry.draw()

    def clearEntries(self) -> None:
        for entry in self.entries:
            entry.clear()
            entry.draw()

    def initType1(self, answers: List[str]) -> None:
        self.frameType1 = AbsoluteFrame(self.baseframe,
                                        width=33,
                                        height=13,
                                        style=BoxStyle(bg_color=term.on_gray22))
        self.frameType1.place(3, 6)

        self.table = GridFrame(self.frameType1,
                               widths=[3, 6],
                               heights=[1, 1, 1, 1, 1],
                               style=BoxStyle(bg_color=term.on_gray14,
                                              border_style=BorderStyle.SINGLE,
                                              border_color=term.orange),
                               inner_border=True)

        self.labels = []
        self.entries = []

        if len(answers) == 5:
            self.table.place(11, 1)
        elif len(answers) == 10:
            self.table2 = GridFrame(self.frameType1,
                                    widths=[3, 6],
                                    heights=[1, 1, 1, 1, 1],
                                    style=BoxStyle(
                                        bg_color=term.on_gray14,
                                        border_style=BorderStyle.SINGLE,
                                        border_color=term.orange),
                                    inner_border=True)
            self.table2.place(19, 1)
            self.table.place(2, 1)

        for i in range(5):
            label = Label(self.table,
                          width=3,
                          height=1,
                          text=str(i + 1) + ".",
                          h_align=HAlignment.RIGHT,
                          style=BoxStyle(text_style=term.white))
            label.grid(0, i)
            self.labels.append(label)

            entry = Entry(self.table,
                          width=6,
                          height=1,
                          style=BoxStyle(border_style=BorderStyle.NONE,
                                         bg_color=term.on_gray10,
                                         text_style=term.white),
                          selected_style=BoxStyle(border_style=BorderStyle.NONE,
                                                  bg_color=term.on_gray8),
                          focused_style=BoxStyle(border_style=BorderStyle.NONE,
                                                 bg_color=term.on_gray8))
            entry.setOnChange(lambda entry=entry: entry.setStyle(
                BoxStyle(border_style=BorderStyle.NONE,
                         bg_color=term.on_gray10,
                         text_style=term.white)))
            entry.grid(1, i)
            self.entries.append(entry)

        if len(answers) == 10:
            for i in range(5):
                label = Label(self.table2,
                              width=3,
                              height=1,
                              text=str(i + 6) + ".",
                              h_align=HAlignment.RIGHT,
                              style=BoxStyle(text_style=term.white))
                label.grid(0, i)
                self.labels.append(label)

                entry = Entry(
                    self.table2,
                    width=6,
                    height=1,
                    default_text="",
                    style=BoxStyle(border_style=BorderStyle.NONE,
                                   bg_color=term.on_gray10,
                                   text_style=term.white),
                    selected_style=BoxStyle(border_style=BorderStyle.NONE,
                                            bg_color=term.on_gray8),
                    focused_style=BoxStyle(border_style=BorderStyle.NONE,
                                           bg_color=term.on_gray8))
                entry.setOnChange(lambda entry=entry: entry.setStyle(
                    BoxStyle(border_style=BorderStyle.NONE,
                             bg_color=term.on_gray10,
                             text_style=term.white)))
                entry.grid(1, i)
                self.entries.append(entry)

        self.frameType1.draw()
        self.logLabel.deactivate()
        self.checkButton.activate()
        self.clearButton.activate()
        self.checkButton.onClick(self.checkAnswers)
        self.buttonFrame.draw()

        # Navigation
        self.stageOptions.overrideNavigation(Direction.DOWN, self.entries[0])
        self.disciplineOptions.overrideNavigation(Direction.DOWN,
                                                  self.entries[0])
        self.checkButton.overrideNavigation(Direction.UP, self.entries[-1])
        self.clearButton.overrideNavigation(Direction.UP, self.entries[-1])

    def initType2(self, answers: List[str]) -> None:
        self.frameType2 = AbsoluteFrame(self.baseframe,
                                        35,
                                        13,
                                        style=BoxStyle(bg_color=term.on_gray22))
        self.frameType2.place(2, 6)
        self.table = GridFrame(self.frameType2,
                               widths=[7, 7, 7, 7],
                               heights=[1, 1, 1],
                               style=BoxStyle(bg_color=term.on_gray14,
                                              border_style=BorderStyle.SINGLE,
                                              border_color=term.orange),
                               inner_border=True)
        self.table.place(1, 3)
        self.labels = []
        self.entries = []
        for r in range(3):
            for c in range(4):
                entry = Entry(
                    self.table,
                    width=7,
                    height=1,
                    style=BoxStyle(border_style=BorderStyle.NONE,
                                   bg_color=term.on_gray10,
                                   text_style=term.white),
                    selected_style=BoxStyle(border_style=BorderStyle.NONE,
                                            bg_color=term.on_gray8),
                    focused_style=BoxStyle(border_style=BorderStyle.NONE,
                                           bg_color=term.on_gray8))
                entry.setOnChange(lambda entry=entry: entry.setStyle(
                    BoxStyle(border_style=BorderStyle.NONE,
                             bg_color=term.on_gray10,
                             text_style=term.white)))
                entry.grid(c, r)
                self.entries.append(entry)
        self.frameType2.draw()
        self.logLabel.deactivate()
        self.checkButton.activate()
        self.clearButton.activate()
        self.checkButton.onClick(self.checkAnswers)
        self.buttonFrame.draw()


if __name__ == "__main__":
    term = Terminal()
    with term.hidden_cursor():
        app = Application(term)
        app.loop()
