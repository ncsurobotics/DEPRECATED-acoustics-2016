import BBBIO
import time


class ADS7865:
    WAIT_TIME = 1

    def __init__(self, io):
        self.state = 'happy!'
        self.PortDB = io['PortDB']
        self.WR = io['/WR']
        self.BUSY = io['BUSY']
        self.CS = io['/CS']
        self.RD = io['/RD']
        self._CONVST = io['/CONVST']

    def PulseWR(self):
        callee_s = self.WR.value
        self.WR.write_to_port(1)
        time.sleep(self.WAIT_TIME)
        self.WR.write_to_port(0)
        time.sleep(self.WAIT_TIME)
        self.WR.write_to_port(callee_s)

    def Init_ADC(self):
        self.PortDB.set_port_dir('in')
        self.WR.set_port_dir('out')
        self.WR.write_to_port(1)
        self.BUSY.set_port_dir('in')
        self.RD.set_port_dir('out')
        self.RD.write_to_port(1)
        self._CONVST.set_port_dir('out')
        self._CONVST.write_to_port(1)
        self.CS.set_port_dir('out')
        self.CS.write_to_port(0)

        print('ADS7865: Initialization complete.')

    def Configure(self, cmd):
        callee_sPD = self.PortDB.portDirection

        self.WR.write_to_port(0)
        self.PortDB.set_port_dir("out")
        self.PortDB.write_to_port(cmd)
        print('ADS7865: Databus cmd %s has been sent.' % self.PortDB.read_str())

        time.sleep(self.WAIT_TIME)
        self.WR.write_to_port(1)
        self.PortDB.set_port_dir(callee_sPD)

    def StartConv(self):
        #a = time.time()
        self._CONVST.write_to_port(0)
        self._CONVST.write_to_port(1)
        #b = time.time()
        #print("_CONVST signal was low for %f seconds." % (b-a))

    def ReadConv(self):
        self.RD.write_to_port(0)
        result = self.PortDB.read_str()
        self.RD.write_to_port(1)
        return result

    def Close(self):
        self.CS.write_to_port(1)
        self.PortDB.close()
        self.WR.close()
        self.BUSY.close()
        self.CS.close()
        self.RD.close()
        self._CONVST.close()
