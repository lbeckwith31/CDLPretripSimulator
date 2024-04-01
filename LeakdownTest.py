from tkinter import *
from tkinter import messagebox
from random import random
from Ignition import IgnitionState

class LeakdownTest:
    def __init__(self, scr, pedals, cbrake, ibrake, airtank, ign, gearbox, button, final_func):
        self.scr = scr
        self.pedals = pedals
        self.cbrake = cbrake
        self.ibrake = ibrake
        self.airtank = airtank
        self.ign = ign
        self.gearbox = gearbox
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.one_minute_instructions = open("data/one_minute_test_instructions.txt").read()
        self.fanning_part_one_instructions = open("data/fanning_test_instructions_part1.txt").read()
        self.fanning_part_two_instructions = open("data/fanning_test_instructions_part2.txt").read()
        self.timer = Timer(self.scr)
        self.timer_func = None
        self.one_minute_label = None
        self.one_minute_test_started = False
        self.buzzer_psi = 0
        self.button = button
        self.final_func = final_func


    def display_timer(self):
        self.timer.bg.place(x=375, y=125)
        self.timer_countdown()


    def timer_countdown(self):
        if self.timer.start_time == 0:
            self.end_one_minute_test()
        else:
            if self.pedals.brake.brake_pressed:
                if self.timer.start_time % 15 == 0:
                    self.airtank.continuous_press_lower_psi(random())
                self.timer.bg.second_slice = self.timer.bg.create_arc(self.timer.time_pie_coords, start=self.timer.start_point, extent=6, fill="lawn green", outline="lawn green")
                self.timer.start_time -= 1
                self.timer.start_point -= 6
                self.timer.bg.itemconfig(self.timer.time_clock, text=str(self.timer.start_time).zfill(2))
                self.timer.bg.lift(self.timer.time_clock, self.timer.bg.second_slice)
            else:
                if self.timer_func:
                    self.scr.after_cancel(self.timer_func)
            self.timer_func = self.scr.after(1000, self.timer_countdown)


    def check_if_ready(self):
        if self.gearbox.gear != "Neutral" or self.cbrake.engaged or self.ibrake.engaged or self.ign.ign_status != IgnitionState.AUXILIARY or self.pedals.brake.brake_pressed or self.airtank.psi < self.airtank.GOVERNOR_CUT_OUT:
            messagebox.showerror(title="Not ready", message=open("data/leakdown_error.txt").read())
        else:
            self.display_instructions_one_minute_test()


    def display_instructions_one_minute_test(self):
        self.instructions_overlay.create_text(150, 130, text=self.one_minute_instructions, font=("Amazon Ember", 9, "normal"))
        self.airtank.one_minute_test_begun = True
        self.instructions_overlay.place(x=350, y=100)
        self.begin_button = Button(self.scr, text="Start test!")
        self.begin_button.place(x=465, y=360)
        self.begin_button.config(command=self.start_one_minute_test)
        self.button.config(text="Test in progress...", state=DISABLED)
        self.one_minute_test_started = True


    def display_instructions_fanning_test_part_one(self):
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.instructions_overlay.create_text(150, 120, text=self.fanning_part_one_instructions, font=("Amazon Ember", 9, "normal"))
        self.instructions_overlay.place(x=350, y=100)
        self.begin_button = Button(self.scr, text="Start test!")
        self.begin_button.place(x=465, y=330)
        self.begin_button.config(command=self.start_fanning_test_part_one)


    def display_instructions_fanning_test_part_two(self):
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.instructions_overlay.create_text(150, 120, text=self.fanning_part_two_instructions, font=("Amazon Ember", 9, "normal"))
        self.instructions_overlay.place(x=350, y=100)
        self.begin_button = Button(self.scr, text="Start test!")
        self.begin_button.place(x=465, y=330)
        self.begin_button.config(command=self.start_fanning_test_part_two)


    def start_one_minute_test(self):
        self.instructions_overlay.destroy()
        self.begin_button.destroy()
        if not self.one_minute_label:
            self.one_minute_label = Label(self.scr, text="Press and hold \"B\" for 60 seconds...", font=("Amazon Ember Display Heavy", 24, "bold"))
            self.one_minute_label.place(x=240, y=450)
        if self.pedals.brake.brake_pressed and self.one_minute_test_started:
            self.scr.after_cancel(self.timer_start)
            self.display_timer()
        else:
            self.timer_start = self.scr.after(1000, self.start_one_minute_test)


    def end_one_minute_test(self):
        self.one_minute_label.place_forget()
        self.scr.after_cancel(self.timer_func)
        self.scr.after_cancel(self.timer_start)
        self.scr.after(1000, self.timer.bg.destroy)
        self.scr.after(1000, self.display_instructions_fanning_test_part_one)
        self.one_minute_test_started = False
        self.airtank.one_minute_test_begun = False


    def start_fanning_test_part_one(self):
        self.fanning_test_part_one_started = True
        self.instructions_overlay.destroy()
        self.begin_button.destroy()
        self.check_for_buzzer()


    def end_fanning_test_part_one(self):
        self.instructions_overlay = Canvas(self.scr, width=300, height=300, bg="bisque")
        self.instructions_overlay.create_text(150, 120, text="Enter the PSI when your buzzer came on.", font=("Amazon Ember Display Light", 25, "bold"), width=250)
        self.instructions_overlay.place(x=350, y=100)
        self.psi_window = Entry(self.scr, width=5)
        self.begin_button = Button(self.scr, text="Enter")
        self.psi_window.place(x=485, y=330)
        self.begin_button.place(x=465, y=360)
        self.begin_button.config(command=self.get_buzzer_psi)
        self.fanning_test_part_one_started = False


    def get_buzzer_psi(self):
        try:
            self.buzzer_psi = int(self.psi_window.get())
            self.instructions_overlay.destroy()
            self.psi_window.destroy()
            self.begin_button.destroy()
            print(self.buzzer_psi)
            self.display_instructions_fanning_test_part_two()
        except:
            messagebox.showerror(title="Invalid input", text="Please enter the PSI level as a number only.")


    def check_for_buzzer(self):
        if self.airtank.get_psi() <= self.airtank.PSI_BUZZER:
            self.end_fanning_test_part_one()
        else:
            self.scr.after(100, self.check_for_buzzer)


    def start_fanning_test_part_two(self):
        self.fanning_test_part_two_started = True
        self.instructions_overlay.destroy()
        self.begin_button.destroy()
        self.check_for_brake_set()


    def check_for_brake_set(self):
        self.brake_set = min([self.cbrake.brake_set, self.ibrake.brake_set])
        if self.airtank.get_psi() <= self.brake_set:
            self.end_fanning_test_part_two()
        else:
            self.scr.after(100, self.check_for_brake_set)


    def end_fanning_test_part_two(self):
        self.fanning_test_part_two_started = False
        self.instructions_overlay = Canvas(self.scr, width=300, height=350, bg="bisque")
        self.instructions_overlay.create_text(150, 80, text="Enter the PSI when your trailer brake set.", font=("Amazon Ember Display Light", 14, "bold"), width=280)
        self.l_psi_window = Entry(self.scr, width=5)
        self.l_psi_window.place(x=485, y=225)
        self.instructions_overlay.create_text(150, 200, text="Enter the PSI when your tractor brake set.", font=("Amazon Ember Display Light", 14, "bold"), width=280)
        self.instructions_overlay.place(x=350, y=100)
        self.c_psi_window = Entry(self.scr, width=5)
        self.psi_button = Button(self.scr, text="Enter")
        self.c_psi_window.place(x=485, y=330)
        self.psi_button.place(x=465, y=380)
        self.psi_button.config(command=self.get_brake_set_psi)


    def get_brake_set_psi(self):
        try:
            self.tractor_set_psi = int(self.c_psi_window.get())
            self.trailer_set_psi = int(self.l_psi_window.get())
            self.instructions_overlay.destroy()
            self.c_psi_window.destroy()
            self.psi_button.destroy()
            self.l_psi_window.destroy()
            self.button.config(state=NORMAL, text="Get Your Final Score", command=self.final_func)
        except:
            messagebox.showerror(title="Invalid input", text="Please enter the PSI level as a number only.")


    def get_result(self):
        self.buzzer_diff = self.airtank.PSI_BUZZER - self.buzzer_psi
        self.cbrake_diff = self.cbrake.brake_set - self.tractor_set_psi
        self.ibrake_diff = self.ibrake.brake_set - self.trailer_set_psi
        return abs(self.buzzer_diff) < 5 and abs(self.cbrake_diff) < 5 and abs(self.ibrake_diff) < 5


class Timer:
    def __init__(self, scr):
        self.start_time = 60
        self.start_point = 84
        self.bg = Canvas(scr, width=300, height=300, bg="dark slate gray")
        self.time_pie_coords = 2, 2, 300, 300
        self.time_pie = self.bg.create_oval(self.time_pie_coords[0], self.time_pie_coords[1], self.time_pie_coords[2], self.time_pie_coords[3], fill="lime green")
        self.time_clock = self.bg.create_text(150, 150, text=str(self.start_time).zfill(2), font=("Amazon Ember Display Light", 80, "bold"), fill="dark slate gray")
