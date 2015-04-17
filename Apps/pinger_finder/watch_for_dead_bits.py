import boot
import pypruss  # Python PRUSS wrapper
import time


class mask:

    def __init__(self):
        self.burn_bit = 1
        self.capture = [0] * 12
        self.word_size = 12

    def burn(self, samples, delay):
        format_code = '0' + str(self.word_size) + 'b'
        T = delay / float(len(samples))

        # Grab a sample
        for samp in samples:

            # Convert it to binary
            b_samp = format(samp, format_code)

            # Burn in those values
            for i in range(self.word_size):
                # Count down w/ index
                index = self.word_size - 1 - i

                # Inspect each bit for burn-in
                #import pdb; pdb.set_trace()
                if (b_samp[index] == str(self.burn_bit)):
                    self.capture[index] = self.burn_bit

            # Wait certain amount of time for next loop
            print(''.join(map(str, self.capture)))
            time.sleep(T)

    def normal(self, samples, delay):
        format_code = '0' + str(self.word_size) + 'b'
        T = delay / float(len(samples))

        # Grab a sample
        for samp in samples:

            # Convert it to binary
            b_samp = format(samp, format_code)

            # Wait certain amount of time for next loop
            print(b_samp)
            time.sleep(T)


def main(ADC_Obj):
    # Config the ADC for success
    ADC_Obj.Config([0x100])
    ADC_Obj.Ready_PRUSS_For_Burst()

    # Config burning maching
    msk = mask()

    #
    print("normal or burn?")
    user_input = raw_input(" >> ")

    # Some error handling
    if user_input == 'burn':
        print("What value should burn (1 or 0)?")
        msk.burn_bit = raw_input(" >> ")

    elif user_input != 'normal':
        print("I don't recognize that. Quitting program.")
        user_input = 'q'

    while (user_input != 'q'):
        try:
            # Capture Data
            y, t = ADC_Obj.Burst(raw=1)

            # Parse The Data
            if user_input == 'burn':
                msk.burn(y[0], .1)
            if user_input == 'normal':
                msk.normal(y[0], .1)

            # Uncomment to allow for user loop control
            #user_input = raw_input('Press enter to continue...')
        except KeyboardInterrupt:
            print("Quitting program")
            user_input = 'q'

    boot.dearm()
