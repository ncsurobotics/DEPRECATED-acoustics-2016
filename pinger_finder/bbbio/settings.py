from os import path

# Get variables for navigating the file system.
root_directory = path.dirname(path.dirname(path.realpath(__file__)))
pf_directory = path.join(root_directory, "pinger_finder")
bin_directory = path.join(pf_directory, "bbbio/pru/bin/")
