from pygame import mixer
from random import randint
from Ignition import IgnitionState


class Pedals:
    def __init__(self, scr, rpmeter, srvlabel):
        self.scr = scr
        self.brake = ServiceBrake(srvlabel, self.scr)
        self.gas = GasPedal(rpmeter, scr)

    
    def press_pedal(self, e, airtank, ign, cbrakes, ibrakes):
        if e.keysym.lower() == "g" and not self.gas.gas_pressed and ign.ign_status == IgnitionState.RUNNING:
            self.gas.gas_pressed = True
            if mixer.Sound.get_num_channels(self.gas.idling_hard) < 1 and mixer.Sound.get_num_channels(self.gas.gas_sound) < 1:
                mixer.Sound.play(self.gas.idling_hard, loops=-1)
                mixer.Sound.play(self.gas.gas_sound)
                mixer.Sound.stop(ign.idling_normal)
            self.gas.raise_rpms(ign.ign_status)
        elif e.keysym.lower() == "b":
            if self.brake.brake_pressed == True:
                pass
            else:
                self.brake.brake_pressed = True
                mixer.Sound.play(self.brake.srv_brake_sound)
                if ign.ign_status == IgnitionState.RUNNING or ign.ign_status == IgnitionState.AUXILIARY:
                    airtank.lower_psi(cbrakes, ibrakes)
                self.brake.label["text"] = "Service Brake: ON"
                self.brake.label["fg"] = "black"


    def depress_pedal(self, e, airtank, ign):
        if e.keysym.lower() == "g":
            self.gas.gas_depressed(ign, airtank)
        elif e.keysym.lower() == "b":
            self.brake.brake_pressed = False
            self.brake.label["text"] = "Service Brake: OFF"
            self.brake.label["fg"] = "red"


class ServiceBrake:
    def __init__(self, label, scr):
        self.srv_brake_sound = mixer.Sound("sounds/service_brake.mp3")
        self.brake_pressed = False
        self.scr = scr
        self.label = label


class GasPedal:
    def __init__(self, rpmeter, scr):
        self.rpms = randint(550, 600)
        self.gas_pressed = False
        self.MAX_RPMS = 1500
        self.MIN_RPMS = randint(550, 600)
        self.rpmeter = rpmeter
        self.scr = scr
        self.idling_hard = mixer.Sound("sounds/hard_idle.mp3")
        self.gas_sound = mixer.Sound("sounds/acc_burst.mp3")
        self.repeat_raise = self.scr.after(1000, lambda: None)
        self.repeat_lower = self.scr.after(1000, lambda: None)
    

    def raise_rpms(self, ign_status):
        self.rpmeter["text"] = f"{str(self.rpms).zfill(4)}"
        if self.rpms > self.MAX_RPMS:
            self.rpmeter["fg"] = "red"
        elif self.rpms > 1000:
            self.rpmeter["fg"] = "yellow"
        else:
            self.rpmeter["fg"] = "green"
        if self.gas_pressed and ign_status.value == 2:
            self.rpmeter["text"] = f"{str(self.rpms).zfill(4)}"
            self.rpms += randint(50, 65)
            self.repeat_raise = self.scr.after(100, lambda: self.raise_rpms(ign_status))

    
    def lower_rpms(self):
        if not self.gas_pressed and self.rpms > self.MIN_RPMS:
            rpms_decrease = randint(70, 90)
            if self.rpms - rpms_decrease >= 0:
                self.rpms -= rpms_decrease
            self.rpmeter["text"] = f"{str(self.rpms).zfill(4)}"
            self.repeat_lower = self.scr.after(100, self.lower_rpms)
            if self.rpms > self.MAX_RPMS:
              self.rpmeter["fg"] = "red"
            elif self.rpms > 1000:
              self.rpmeter["fg"] = "yellow"
            else:
              self.rpmeter["fg"] = "green"
    

    def gas_depressed(self, ign, airtank):
        self.gas_pressed = False
        airtank.psi_increase = 1
        mixer.Sound.stop(self.gas_sound)
        mixer.Sound.stop(self.idling_hard)
        if ign.ign_status.value == 2:
            mixer.Sound.play(ign.idling_normal, loops=-1)
        self.lower_rpms()
