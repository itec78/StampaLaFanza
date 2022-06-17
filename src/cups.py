import configparser

class CupsManager():
    def __init__(self,fname,DEFAULT_COPIES,DEFAULT_SIDES,DEFAULT_MEDIA):
        self.config = configparser.ConfigParser()
        self.name = "-".join(os.path.basename(fname).split("-")[1:])
        self.copies = DEFAULT_COPIES
        self.sides = DEFAULT_SIDES
        self.media = DEFAULT_MEDIA