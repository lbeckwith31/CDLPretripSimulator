from tkinter import *
from tkinter import ttk
from pygame import mixer
from idlelib.tooltip import Hovertip
from AirTank import AirTank
from Pedals import Pedals
from Brakes import Brakes
from Ignition import Ignition
from GearBox import GearBox
from TugTest import TugTest
from ServiceBrakeTest import ServiceBrakeTest
from Dashboard import Dashboard
from LeakdownTest import LeakdownTest
from sys import platform


image_dimensions = "1024x783"
SMALL_FONT = ("Amazon Ember Display Light", 8, "bold")
MAIN_FONT = ("Amazon Ember Display Medium", 12, "bold")
LARGE_FONT = ("Amazon Ember Display Heavy", 16, "bold")

window = Tk()
window.title("Ohio CDL Pretrip Simulator (Automatic)")
window.geometry(image_dimensions)

#I put the follwowing lines in here because I use Windows
#and Linux and was initially hoping to make this cross-
#platform. I'm now wondering if this is why the .exe
#file gets flagged by VirusTotal
if platform == "linux":
    icon = "@truck.xbm"
elif platform == "win32":
    icon = "truck.ico"
window.iconbitmap(icon)
bg_image = Canvas(window, width=1024, height=683)
bg_image.pack(side=LEFT, expand=1, fill=BOTH)
backg = PhotoImage(file="images/in_cab.png")
backgi = bg_image.create_image(0, 0, anchor=NW, image=backg)
key_img = PhotoImage(file="images/key.png").subsample(8, 10)


def activate_button(button, item, threshold):
    if item() >= threshold:
        button.config(bg="black", fg="red", state="normal")
    else:
        window.after(1000, lambda: activate_button(button, item, threshold))


ign_button = Button(window, text="Ignition", image=key_img)
# Command attribute is configured on this button later
# after other objects are initialized

ign_button.place(x=320, y=360)

ign_label = Label(window,
                  text=f"Ignition State: OFF",
                  font=LARGE_FONT,
                  fg="red")
ign_label.place(y=0, x=385)



dashboard_button = Button(window,
                        text="Display Dashboard",
                        font=LARGE_FONT,
                        bg="black",
                        fg="red",
                        state=DISABLED
                        )
dashboard_button.place(y=5, x=50)
dashboard_tooltip = Hovertip(dashboard_button, "Begin the In-Cab Pretrip Inspection here.")

tugtest_button = Button(window,
                        text="Begin Tug Test",
                        font=LARGE_FONT,
                        bg="grey",
                        fg="black",
                        state="disabled"
                        )
tugtest_button.place(y=5, x=800)
tugtest_tooltip = Hovertip(tugtest_button, "Do not start tug test\nunitl PSI is over 120.")

service_brake_button = Button(window,
                        text="Begin Service Brake Test",
                        font=LARGE_FONT,
                        bg="grey",
                        fg="black",
                        state="disabled"
                        )

service_brake_button.place(y=600, x=50)
service_brake_tooltip = Hovertip(service_brake_button, "Do not start the service brake\ntest until tug test is complete.")

leakdown_button = Button(window,
                        text="Begin Leakdown Test",
                        font=LARGE_FONT,
                        bg="grey",
                        fg="black",
                        state="disabled"
                        )
leakdown_button.place(y=600, x=735)
leakdown_tooltip = Hovertip(leakdown_button, "Do not start leakdown test until\nservice brake test is complete.")

gear_button = Button(window,
                     text="N",
                     bg="black",
                     font=LARGE_FONT,
                     fg="red",
                     )
gear_button.place(x=400, y=400)

traibutton = Button(text="Trailer Brake Set",
                       font=SMALL_FONT,
                       fg="black",
                       command=lambda: trailer_brake.brake_on("Trailer"))
traibutton.place(x=510, y=370)

tracbutton = Button(text="Tractor Brake Set",
                       font=SMALL_FONT,
                       fg="black",
                       command=lambda: tractor_brake.brake_on("Tractor"))
tracbutton.place(x=540, y=400)

rpm_label = Label(window, text="RPM:", font=LARGE_FONT)
rpms_meter = Label(window,
                   text=f"{str(0).zfill(4)}",
                   font=("Courier", 16, "bold"),
                   bg="black",
                   fg="green")
rpm_label.place(x=100, y=720)
rpms_meter.place(x=180, y=725)

psi_label = Label(window, text="PSI:", font=LARGE_FONT)
psi_meter = Label(window,
                  text=f"{str(0).zfill(3)}",
                  font=("Courier", 16, "bold"),
                  bg="black",
                  fg="red")
psi_label.place(x=800, y=720)
psi_meter.place(x=875, y=725)

low_psi_warning_label = Label(window,
                              text="Low PSI Warning:",
                              font=MAIN_FONT,
                              fg="black"
                              )
low_psi_warning_label.place(x=600, y=720)

low_psi_warning_light = Canvas(width=10, height=10)
blinker = low_psi_warning_light.create_oval(2, 2, 10, 10, fill="gray")
low_psi_warning_light.place(x=770, y=725)

instructions_label = Label(
    window,
    text="press (G) to step on the gas\npress (B) to step on the brake",
    font=MAIN_FONT)
instructions_label.place(x=250, y=710)

srv_brake_label = Label(window,
                  text=f"Service Brake: OFF",
                  font=LARGE_FONT,
                  fg="red")
srv_brake_label.place(y=650, x=400)

mixer.init()

ignition = Ignition(ign_label, window, psi_meter, rpms_meter)
airtank = AirTank(low_psi_warning_light, blinker, window, ignition)
pedals = Pedals(window, rpms_meter, srv_brake_label)
airtank.set_pedals(pedals)
ign_button.config(command=lambda: ignition.turn_key(airtank, pedals.gas))
tractor_brake = Brakes(tracbutton, "Tractor")
trailer_brake = Brakes(traibutton, "Trailer")
gearbox = GearBox(gear_button)
gear_button.config(command=gearbox.change_gear)


def final_result():
    final_message = """
You have completed the CDL In-Cab Pre-
Trip Simulator! Your overall grade is {}.

Here's how you did on the tests:
    Dashboard test - {}
    Tug test - {}
    Service Brake test - {}
    Leak Down test - {}

You will be ready for the In-Cab Pre-Trip test 
when you have scored 100% on the simulation.
{}!"""
    results = [i.get_result() for i in [dashboard, tugtest, sbtest, ldtest]]
    grade = results.count(True) / len(results)
    instructions_overlay = Canvas(window, width=300, height=300, bg="bisque")
    instructions_overlay.create_text(150, 120, text=final_message.format(
        "{:.2f}%".format(grade * 100), "Passed" if dashboard.get_result() else "Failed",
        "Passed" if tugtest.get_result() else "Failed",
        "Passed" if sbtest.get_result() else "Failed",
        "Passed" if ldtest.get_result() else "Failed",
        "Better luck next time" if grade < 1 else "Congratulations and good luck on your test"
    ))
    instructions_overlay.place(x=350, y=100)
    end_button = Button(window, text="End Test")
    end_button.place(x=465, y=330)
    end_button.config(command=window.destroy)



tugtest = TugTest(window, bg_image, backgi, tugtest_button, tractor_brake, trailer_brake, pedals, gearbox, ignition)
sbtest = ServiceBrakeTest(window, bg_image, backgi, service_brake_button, tractor_brake, trailer_brake, pedals, gearbox, ignition)
ldtest = LeakdownTest(window, pedals, tractor_brake, trailer_brake, airtank, ignition, gearbox, leakdown_button, final_result)
dashboard = Dashboard(window, icon, dashboard_button)
service_brake_button.config(command=sbtest.display_instructions)
tugtest_button.config(command=tugtest.display_instructions)
dashboard_button.config(command=dashboard.display_dashboard)
leakdown_button.config(command=ldtest.check_if_ready)
activate_button(tugtest_button, airtank.get_psi, 120)
activate_button(service_brake_button, tugtest.get_status, True)
activate_button(leakdown_button, sbtest.get_status, True)


scrollbar = ttk.Scrollbar(window, orient=VERTICAL)
scrollbar.pack(side=RIGHT, fill=Y)


def start_inspection():
    instructions_overlay.destroy()
    begin_button.destroy()
    dashboard_button.config(state=NORMAL)


instructions_overlay = Canvas(window, width=300, height=300, bg="bisque")
instructions_overlay.create_text(150, 130, text=open("data/main_instructions.txt").read(), font=("Amazon Ember", 9, "normal"))
instructions_overlay.place(x=350, y=100)
begin_button = Button(window, text="Start test!")
begin_button.place(x=465, y=370)
begin_button.config(command=start_inspection)

window.bind("<KeyPress>", lambda e: pedals.press_pedal(e, airtank, ignition, tractor_brake, trailer_brake))
window.bind("<KeyRelease>", lambda e: pedals.depress_pedal(e, airtank, ignition))


window.mainloop()
