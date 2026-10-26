
class Cross:
    def __init__(self, xy):
        self.x = xy[0]
        self.y = xy[1]
    
        self.N = (self.x, self.y - 1)
        self.E = (self.x + 1, self.y)
        self.S = (self.x, self.y + 1)
        self.W = (self.x - 1, self.y)

        self.NE = (self.x + 1, self.y)
        self.NW = (self.x, self.y)
        self.SW = (self.x, self.y + 1)
        self.SE = (self.x + 1, self.y + 1)

        self.xy = (self.x, self.y)