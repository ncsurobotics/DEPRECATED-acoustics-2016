import csv

class Datafile:
    """Class meant to define datasets objects that you can pack and export
    in a somewhat intuitive manner
    """
    def __init__(self):
        self.filename = None
        self.filepath = None
        
    def package(self):
        if self.fileName == None
            print("filename: ")
            
        
        
    
    
class Simple_Data_Plot(Datafile):
    """
    """
    
    def convert_data(self, data):
        

def submit_file(path, fieldnames, data):
    """
    """
    #
    with open(path, 'wt') as obj_csvfile:
        obj_wcsv = csv.DictWriter(obj_csvfile, delimiter=',', fieldnames=fieldnames)
        obj_wcsv.writeheader()

        for row in data:
            obj_wcsv.writerow(row)


def RunCSVExport(data):
    '''Data is a tuple of the following format: (time, CH1)'''

    # Settings
    path = 'DataCaptureFiles/preview.csv'

    # Initialization
    mylist = []
    fieldnames = ('time', 'CH1')

    # Program
    for d in data:
        inner_dict = dict(zip(fieldnames, d))
        mylist.append(inner_dict)

    Submit(path, fieldnames, mylist)

"""
"""