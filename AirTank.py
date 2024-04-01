from pygame import mixer
from random import randint
from Ignition import IgnitionState


class AirTank:
  def __init__(self, wlight, wlightw, scr, ign):
    self.gov_sneeze = mixer.Sound("sounds/governor_cut_out.mp3")
    self.gov_sneeze.set_volume(1)
    self.buzzer = mixer.Sound("sounds/blinking-bell-loop-39522.mp3")
    self.psi = 0
    self.psi_increase = 1
    self.GOVERNOR_CUT_OUT = randint(120, 140)
    self.MIN_PSI = 0
    self.PSI_BUZZER = randint(55, 60)
    self.wlight = wlight
    self.scr = scr
    self.ign = ign
    self.wlightw = wlightw
    self.one_minute_test_begun = False
    
    self.repeat_function = self.scr.after(1000, lambda: None)

  
  def set_pedals(self, pedals):
    self.pedals = pedals


  def raise_psi(self):
    self.scr.after_cancel(self.repeat_function)
    if self.pedals.brake.brake_pressed:
      self.repeat_function = self.scr.after(1000, self.raise_psi)
    else:
      if self.pedals.gas.gas_pressed:
        self.psi_increase *= randint(2, 3)
      if self.psi < self.GOVERNOR_CUT_OUT:
        self.psi += self.psi_increase
        self.ign.pmeter["text"] = f"{str(self.psi).zfill(3)}"
      if self.psi < self.GOVERNOR_CUT_OUT and self.psi > 90:
        self.ign.pmeter["fg"] = "green"
      elif self.psi < 90 and self.psi >= self.PSI_BUZZER:
        self.ign.pmeter["fg"] = "yellow"
        self.wlight.itemconfig(self.wlightw, fill="gray")
        mixer.Sound.stop(self.buzzer)
      elif self.psi < self.PSI_BUZZER and mixer.Sound.get_num_channels(self.buzzer) < 1:
        mixer.Sound.play(self.buzzer)
        self.wlight.itemconfig(self.wlightw, fill="red")
      if self.psi < self.GOVERNOR_CUT_OUT and self.ign.ign_status.value == 2:
        self.psi_increase = 1
        self.repeat_function = self.scr.after(1000, self.raise_psi)
      elif self.psi >= self.GOVERNOR_CUT_OUT and mixer.Sound.get_num_channels(self.gov_sneeze) < 1:
        mixer.Sound.play(self.gov_sneeze)


  def lower_psi(self, tracbrake, traibrake):
    psi_decrease = randint(1, 4)
    if self.psi - psi_decrease >= 0 and not self.one_minute_test_begun:
      self.psi -= psi_decrease
    if self.ign.ign_status == IgnitionState.RUNNING or self.ign.ign_status == IgnitionState.AUXILIARY:
      self.ign.pmeter["text"] = f"{str(self.psi).zfill(3)}"
      if self.psi <= self.GOVERNOR_CUT_OUT and self.psi >= 90:
        self.ign.pmeter["fg"] = "green"
      elif self.psi < 90 and self.psi > self.PSI_BUZZER:
        self.ign.pmeter["fg"] = "yellow"
      elif self.psi <= self.PSI_BUZZER:
        self.ign.pmeter["fg"] = "red"
        self.wlight.itemconfig(self.wlightw, fill="red")
        if mixer.Sound.get_num_channels(self.buzzer) < 1:
          mixer.Sound.play(self.buzzer, loops=-1)
      if self.psi <= tracbrake.brake_set:
        if tracbrake.button["text"].endswith("Brake Released"):
          tracbrake.brake_on("Tractor")
      if self.psi <= traibrake.brake_set:
        if traibrake.button["text"].endswith("Brake Released"):
          traibrake.brake_on("Trailer")
    if self.ign.ign_status == IgnitionState.RUNNING and self.psi < self.GOVERNOR_CUT_OUT:
      self.raise_psi()


  def continuous_press_lower_psi(self, rand):
    self.psi = int(round(self.psi - rand))
    self.ign.pmeter["text"] = f"{str(self.psi).zfill(3)}"

    
  def get_psi(self):
    return self.psi
