class Data():
    def __init__(self, values):
        self.names = values[1::4]
        del values[1::4]

        self.img = values[::3]
        del values[::3]

        self.date = values[1::2]
        del values[1::2]

        self.price = values[::1]

    
