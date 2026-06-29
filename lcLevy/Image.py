import lcLevy.parse_cr3 as parse

class Img():
    
    def __init__(self, data, num = 0):
        self.data = data
        returned = parse.parse_image(data, num)
        self.cr3 = returned["cr3"]
        self.big_crx = returned["big_crx"]
        self.small_crx = returned["small_crx"]

    