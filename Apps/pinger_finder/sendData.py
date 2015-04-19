import os

for i in range(20):
    print(os.system("echo you_%d > /dev/ttyO4" % i))

print("done")
