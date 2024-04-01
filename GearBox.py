class GearBox:
    def __init__(self, button):
        self.gear = "Neutral"
        self.button = button
        self.button["text"] = self.gear[:1]
    

    def change_gear(self):
        if self.gear == "Neutral":
            self.gear = "Drive"
        else:
            self.gear = "Neutral"
        self.button["text"] = self.gear[:1]
