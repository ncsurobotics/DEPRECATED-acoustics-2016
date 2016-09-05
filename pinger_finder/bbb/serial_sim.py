class Serial(object):
    def __init__(self, *args, **kwargs):
        pass
        
    def open(self, *args, **kwargs):
        pass

    def write(self, msg):
        print("[serial out]: \"{}\"".format(msg))