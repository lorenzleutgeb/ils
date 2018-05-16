class Percept:
    def __init__(self, stench, breeze, glitter, bump, scream):
        self.stench = stench
        self.breeze = breeze
        self.glitter = glitter
        self.bump = bump
        self.scream = scream

    def __str__(self):
        return "Percept{" + "stench=" + str(self.stench) + ", breeze=" + str(self.breeze) + ", glitter=" + str(self.glitter) + ", bump=" + str(self.bump) + ", scream=" + str(self.scream) + "}"
