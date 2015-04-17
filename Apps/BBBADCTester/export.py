import csv


def Submit(path, fieldnames, data):
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
