def twos_comp(val, bits):
        """compute the 2's compliment of int value val"""
        if( (val&(1<<(bits-1))) != 0 ):
          val = val - (1<<bits)
        return val
