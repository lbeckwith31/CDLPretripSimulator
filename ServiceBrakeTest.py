from Ignition import IgnitionState
from tkinter import *


class ServiceBrakeTest:
    def __init__(self, scr, bgpic, backg, button, cbrake, ibrake, pedals, gearbox, ign):
        self.scr = scr
        self.bgpic = bgpic
        self.backg = backg
        self.button = button
        self.pedals = pedals
        self.gearbox = gearbox
        self.ign = ign
        self.test_begun = False
        self.test_ended = False
        self.test_passed = False
        self.instructions = open("data/service_brake_instructions.txt", "r").read()
        self.cbrake = cbrake
        self.ibrake = ibrake
   #     self.gas_pressed_recently = False
        self.since_gas_pressed = 0


 #   def detect_gas_press(self, pedals):
 #       if pedals.gas.gas_pressed:
 #           pass
 #       pass

    
    def display_instructions(self):
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.instructions_overlay.create_text(150, 120, text=self.instructions, font=("Amazon Ember", 9, "normal"))
        self.instructions_overlay.place(x=350, y=100)
        self.begin_button = Button(self.scr, text="Start test!")
        self.begin_button.place(x=465, y=330)
        self.begin_button.config(command=self.test)


    def engage_brake(self, event=None):
        for distance in range(20, 100):
            self.bgpic.move(self.backg, 0, -distance if distance % 2 == 0 else distance)
            self.bgpic.update()
            self.bgpic.move(self.backg, 0, distance if distance % 2 == 0 else -distance)
            self.bgpic.update()


    def check_brake(self, brake1, brake2):
        if self.gearbox.gear == "Drive" and self.ign.ign_status == IgnitionState.RUNNING and not brake1.engaged and self.pedals.brake.brake_pressed and not brake2.engaged:
            self.engage_brake()
            self.scr.after(1000, self.complete_test)
        else:
            self.scr.after(10, lambda: self.check_brake(brake1, brake2))

    
    def test(self):
        self.test_begun = True
        self.button["text"] = "End Service Brake Test"
        self.instructions_overlay.destroy()
        self.begin_button.destroy()
        self.button.config(command=self.complete_test)
        self.check_brake(self.cbrake, self.ibrake)


    def complete_test(self):
        self.service_brake_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.service_brake_overlay.create_text(150, 120, text="Did your steering wheel pull to the left or right?")
        self.service_brake_overlay.place(x=350, y=100)
        self.yes_button = Button(self.scr, text="Yes", command=self.yes)
        self.no_button = Button(self.scr, text="No", command=self.no)
        self.yes_button.place(x=375, y=330)
        self.no_button.place(x=565, y=330)
        self.test_ended = True


    def yes(self):
        self.service_brake_overlay.destroy()
        self.yes_button.destroy()
        self.no_button.destroy()
        self.button.config(text="Service Brake Test Failed!")
        self.button.config(state="disabled")


    def no(self):
        self.service_brake_overlay.destroy()
        self.yes_button.destroy()
        self.no_button.destroy()
        self.test_passed = True
        self.button.config(text="Service Brake Test Passed!")
        self.button.config(state="disabled")


    def get_status(self):
        return self.test_ended
    

    def get_result(self):
        return self.test_passed
