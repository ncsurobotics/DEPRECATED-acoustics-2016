import csv

def Submit(path,fieldnames,data):
	with open(path,'wt') as obj_csvfile:
		obj_wcsv = csv.DictWriter(obj_csvfile, delimiter=',', fieldnames=fieldnames)
		obj_wcsv.writeheader()
		
		for row in data:
			obj_wcsv.writerow(row)
	

def RunCSVExport(data):
	# Settings
	path = 'preview.csv'
	
	# Initialization
	sample = 0
	mylist = []
	fieldnames = ('sample', 'CH1')
	
	# Program
	for d in data:
		inner_dict = dict(zip(  fieldnames, (sample,d)  ))
		mylist.append(inner_dict)
		sample += 1
	
	Submit(path,fieldnames,mylist)
		
"""
	
"""