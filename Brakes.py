from pygame import mixer
from random import randint
       

class Brakes:
    def __init__(self, button, name):
        self.engaged = True
        self.button = button
        self.brake_set = randint(20, 45)
        self.brake_set_sound = mixer.Sound("sounds/click-button-140881.mp3")
        self.name = name


    def brake_on(self, name):
      if not self.engaged:
          self.button["text"] = f"{name} Brake Set"
          mixer.Sound.play(self.brake_set_sound)
          self.engaged = True
          self.button["fg"] = "black"
      else:
          self.button["text"] = f"{name} Brake Released"
          self.button["fg"] = "red"
          self.engaged = False
