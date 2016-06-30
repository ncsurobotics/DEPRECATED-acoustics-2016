import threading
import curses
import time
import random

LOG_FILE = open('./log.txt', 'w')
TIME0 = time.time()

class Entity(object):
    """Base class for objects in the curses gui"""
    
    def __init__(self):
        self.origin = [None, None]
        self.symbols = []

    def place(self, x, y):
        self.origin = [x,y]

    def add_char(self, ch, offset):
        """Adds a char to the entity's visual construction. This
        information can be later attained from self.symbols data attribute,
        which is just a list of characters and their offsets.
        
        Args:
          * ch: a character
          * offset: list of format [x,y], which are integers indicating how
          how many space from the origin the symbol/character is located.
        """

        # place symbol
        symbol = [ch, offset]
        self.symbols.append(symbol)

    def write_char(self, ch, offset):
        x,y = offset

        # find desired location of the symbol
        for (i, (character, loc)) in enumerate(self.symbols):
            if [x,y] == loc:
                # write char into correct location
                self.symbols[i][0] = ch

class Blip(Entity):
    """main object used to visually represent a hydrophone"""
    def __init__(self, loc=None):
        super(Blip,self).__init__()

        # build the symbol
        self.add_char('[', [-1,0])
        self.add_char(']', [1,0])
        self.add_char(' ', [0,0])

        # optionally place the Blip in a specific location
        if loc is not None:
            self.place(loc[0], loc[1])

    def set(self, value):
        """A non-false value will turn on the blip"""

        #LOG_FILE.write( "[{:.3f}]".format(time.time() - TIME0) + str(value) + '\n')

        if value is True:
            self.write_char('x', [0,0])
        else:
            self.write_char(' ', [0,0])

#TODO: make a label entity

class SubFrame(Entity):
    """Frame object for curses gui"""

    def __init__(self, loc):
        """
        args:
          * loc: list of format [x,y]. specifies the location of a subframe."""
        super(SubFrame,self).__init__()

        # size parameters
        self.place(loc[0], loc[1])
        self.size = [None, None]

        # content parameters
        self.sprite = {}
        self.label = []

    def add_sprite(self, new_sprite, name):
        """Adds a sprite to the drawing frame
        Args:
          * new_sprite: an instance of the entity base-class that
          can be used as a sprite. I.E, one that contains symbols
          * name: name to designate the new sprite.
        """

        if name in self.sprite.keys():
            print "WARNING: sprite overwritten."
        self.sprite[name] = new_sprite

    def draw(self, stdscr):
        # draw each sprite
        for sprite in self.sprite.values():
            x0 = sprite.origin[0] + self.origin[0]
            y0 = sprite.origin[1] + self.origin[1]

            # draw each symbol in the sprite
            for symbol in sprite.symbols:
                sym_loc = 1
                sym = 0

                x1 = symbol[sym_loc][0] + x0
                y1 = symbol[sym_loc][1] + y0
                ch = symbol[sym]

                # print the character
                stdscr.addch(y1,x1, ord(ch))

    #TODO: add an add_label method





class Curses_GUI(object):
    """Wrapper for making a curses GUI"""
    default_subframe_name = "subframe1"
    
    def __init__(self):
        self.subframe = {}

        # hydrophones
        self.blips = {}

        # drawing loop/thread tools
        self.drawlock = threading.RLock()
        self.datalock = threading.RLock()

        # debug
        self.fps_loc = [20,20]

        # ncurses objects
        #self.stdscr = None

    def add_subframe(self, name, loc=[0,0]):
        """Adds a subframe to the scene.
        
        args:
          * name: desired name of subframe.
          * loc: list of format [x,y]. specifies the location of a subframe."""
        self.subframe[name] = SubFrame(loc)
        
    
    def add_blip(self, subframe, loc, name):
        """Adds a blip to the scene.
        Args:
          * subframe: string representing the name of the subframe
          which the blip is going to be appended to.
          * loc: location of the sprit. given as  list in [x,y] format.
        """
        # add a blip object
        blip_sprite = Blip(loc)
        if name is None:
            id = str(len(self.blips))
            blip_name = 'blip'+id
        else:
            blip_name = name
                
        self.subframe[subframe].add_sprite(blip_sprite, blip_name)

        # save blip
        self.blips[blip_name] = blip_sprite


    def get_blips(self):
        return self.blips

    def pulse_blip(self, name, pulse_time):
        """temporarily pulses a blip"""

        # define pulse function
        def pulse(blip, pulse_time, data_lock):
            # pulse on
            with data_lock:
                blip.set(True)

            # wait
            time.sleep(pulse_time)

            # pulse off
            with data_lock:
                blip.set(False)

        # create a thread for pulsing the blip
        blip = self.blips[name]
        pulse_thread = threading.Thread(target=pulse, args=(blip, pulse_time, self.drawlock))

        # start the thread and exit
        pulse_thread.start()
    
    def get_key(self, stdscr):
        key = stdscr.getch()
        A = 65
        z = 122
        Z = 90


        # if ascii
        if (A <= key) and (key <= z):

            # detect if shift is held
            if key <= Z:
                shift = True
                key += 32 #lower(key)
            else:
                shift = False

            key = chr(key) #convert decimal to ascii
        else:
            key = None
            shift = None
            
        return (key,shift)


    def print_random(self, x,y, stdscr):
        """Prints a random chr to the screen for debugging purposes"""

        rand = chr(int(random.random() * 10 + 77))
        stdscr.addstr(x,y, rand)

    def get_datalock(self):
        """returns the data lock of the gui"""

        return self.datalock
    
    def _run(self, stdscr):
        stdscr.nodelay(1)
        timea = time.time()
        while 1:
            
            
            # get new data
            lock_aquired = self.datalock.acquire()
            if lock_aquired:
                pass
            else:
                continue

            lock_aquired = self.drawlock.acquire()
            if lock_aquired:
                # clear the screen
                stdscr.clear()

                # draw the new contents
                #import pdb; pdb.set_trace()
                for subframe in self.subframe.values():
                    subframe.draw(stdscr)

                # draw in the fps counter
                timeb = time.time()
                fps = 1.0 / (timeb - timea)
                fps = "{:.0f}".format(fps)
                stdscr.addstr(20,20, fps)
                timea = time.time()

                # refresh the screen
                stdscr.refresh()
                
                # release the lock
                self.drawlock.release()

            # process inputs
            key,shift = self.get_key(stdscr)

            if (key == 'q'):
                print "exiting loop."
                break
            #TODO: come up with more inputs

    def mainloop(self):
        curses.wrapper(self._run)
