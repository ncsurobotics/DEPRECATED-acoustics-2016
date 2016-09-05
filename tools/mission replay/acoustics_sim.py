import csv
import numpy as np

N = 4 # the number of input channels recorded

class Data(object):
    def __init__(self):
        self.data = None
        self.fp = None

    def import_file(self, fp):
        self.fp = fp
        with open(fp, 'rb') as csvfile:
            self.read1(csvfile)
            

    def read1(self, csvfile):
        csv_data = csv.reader(csvfile, delimiter=',')

        # data place holders
        data = {}
        data['input'] = np.empty((0,N), float)
        data['start'] = []
        data['end'] = []
        data['mapping'] = ['']*N
        headers = []
        
        for i,row in enumerate(csv_data):

            if i == 0:
                # if on first row, just collect the header information
                headers = [head for head in row]
                print "headers: {}".format(headers)

                if 'DGainsample rate' in headers:
                    raise ValueError("You forgot to split 'DGainsample rate' in this file!! ({})".format(self.fp))

                data['mapping'][0] = headers[0][0:N]
                data['mapping'][1] = headers[1][0:N]
                data['mapping'][2] = headers[2][0:N]
                data['mapping'][3] = headers[3][0:N]

                # make a place holder for the rest of the data (dynamically)
                for head,item in zip(headers[N:],row[N:]):
                    data[head] = []

                continue

            m = i-1
            # record data head
            #TODO: sense how many inputs there are just from the csv file
            if len(row) > N:
                data['start'].append(m)
                data['end'].append(i)
            else:
                data['end'][-1] = i

            # stack data to array 
            input = [float(val) for val in row[0:N]]
            data['input'] = np.append(data['input'], np.array([input]), axis=0)

            if len(row) > N:
                for head,item in zip(headers[N:],row[N:]):
                    try:
                        data[head].append( eval(item) )
                    except SyntaxError:
                        data[head].append( item )

        self.data = data
        return data

    def get_data(self):
        return self.data

    def read2(self, csvfile):
        data = csv.DictReader(csvfile)
        for i,row in enumerate(data):
            if i ==1:
                print row
                break


class ADC_Tools():

    @staticmethod
    def meas_vpp(input, n=None):
        """Computes the vpp for each channel that the ADC is using.
        """
        if n is not None:
            # initialize variables
            vpp = []

            # Compute the vpp for each channel
            for ch in range(n):
                vpp.append(np.amax(input[ch]) - np.amin(input[ch]))
            
            # Return tuple containing the data
            return tuple(vpp)
        else:
            vpp = 0
            vpp = np.amax(input) - np.amin(input)
            return vpp