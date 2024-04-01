#from enum import Enum
#from collections import OrderedDict
from Ignition import IgnitionState
from tkinter import *

class TugTest:
    def __init__(self, scr, bgpic, backg, button, cbrake, ibrake, pedals, gearbox, ign):
        self.scr = scr
        self.bgpic = bgpic
        self.backg = backg
        self.button = button
        self.cbrake = cbrake
        self.ibrake = ibrake
        self.pedals = pedals
        self.gearbox = gearbox
        self.ign = ign
        self.cbrake.passed = False
        self.ibrake.passed = False
        self.test_begun = False
        self.test_ended = False
        self.instructions = open("data/tug_test_instructions.txt", "r").read()


    def display_instructions(self):
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.instructions_overlay.create_text(150, 120, text=self.instructions, font=("Amazon Ember", 9, "normal"))
        self.instructions_overlay.place(x=350, y=100)
        self.begin_button = Button(self.scr, text="Start test!")
        self.begin_button.place(x=465, y=330)
        self.begin_button.config(command=self.test)


    def test(self):
        self.test_begun = True
        self.button["text"] = "End Tug Test"
        self.instructions_overlay.destroy()
        self.begin_button.destroy()
        self.button.config(command=self.complete_test)
        self.check_tug(self.cbrake, self.ibrake)
        self.check_tug(self.ibrake, self.cbrake)


    #Credit to "Pythonista" on Stack Overflow for this function
    #https://stackoverflow.com/questions/36412636/text-animation-in-tkinter-python
    def tug(self, event=None):
        for distance in range(20, 100):
            self.bgpic.move(self.backg, -distance if distance % 2 == 0 else distance, 0)
            self.bgpic.update()
            self.bgpic.move(self.backg, distance if distance % 2 == 0 else -distance, 0)
            self.bgpic.update()

    
    def check_tug(self, brake1, brake2):
        if self.gearbox.gear == "Drive" and self.ign.ign_status == IgnitionState.RUNNING and not brake1.engaged and self.pedals.gas.gas_pressed and brake2.engaged:
            self.tug()
            brake1.passed = True
        if not brake1.passed:
            self.scr.after(100, lambda: self.check_tug(brake1, brake2))

    
    def complete_test(self):
        if self.cbrake.passed and self.ibrake.passed:
            self.button.config(text="Tug Test Passed!")
        else:
            self.button.config(text="Tug Test Failed!")
        self.test_ended = True
        self.button.config(state="disabled")

    
    def get_status(self):
        return self.test_ended
    

    def get_result(self):
        return self.cbrake.passed and self.ibrake.passed
