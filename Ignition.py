from enum import Enum
from itertools import cycle
from pygame import mixer

class IgnitionState(Enum):
    OFF = 0
    AUXILIARY = 1
    RUNNING = 2


class Ignition:
    def __init__(self, label, scr, pmeter, rmeter):
        self.ignition = cycle(IgnitionState)
        self.ign_status = next(self.ignition)
        self.label = label
        self.starting_sound = mixer.Sound("sounds/truck-diesel-10dodge-start-43785.mp3")
        self.idling_normal = mixer.Sound("sounds/idling_normal.mp3")
        self.aux_sound = mixer.Sound("sounds/aux_sound.mp3")
        self.scr = scr
        self.pmeter = pmeter
        self.rmeter = rmeter

    def turn_key(self, airtank, gas):
        self.ign_status = next(self.ignition)
        self.label.config(text=f"Ignition State: {self.ign_status.name}")
        if self.ign_status == IgnitionState.RUNNING:
            mixer.Sound.stop(self.aux_sound)
            mixer.Sound.play(self.starting_sound)
            mixer.Sound.play(self.idling_normal, loops=-1, fade_ms=3500)
            gas.raise_rpms(self.ign_status)
            if airtank.psi < airtank.GOVERNOR_CUT_OUT:
                airtank.raise_psi()
        elif airtank.psi < airtank.PSI_BUZZER and not self.ign_status == IgnitionState.OFF:
            if mixer.Sound.get_num_channels(airtank.buzzer) < 1:
                mixer.Sound.play(airtank.buzzer)
        elif self.ign_status == IgnitionState.OFF:
            for func in [airtank.repeat_function, gas.repeat_lower, gas.repeat_raise]:
                self.scr.after_cancel(func)
            self.reset_dash(gas.gas_sound, gas.idling_hard)
            mixer.Sound.stop(airtank.buzzer)
        if self.ign_status == IgnitionState.AUXILIARY:
            self.scr.after_cancel(airtank.repeat_function)
            mixer.Sound.play(self.aux_sound)
            self.pmeter["text"] = f"{str(airtank.get_psi()).zfill(3)}"


    def reset_dash(self, gsound, isound):
        self.pmeter["text"] = "000"
        self.rmeter["text"] = "0000"
        self.rmeter["fg"] = "green"
        mixer.Sound.stop(self.idling_normal)
        mixer.Sound.stop(isound)
        mixer.Sound.stop(gsound)
