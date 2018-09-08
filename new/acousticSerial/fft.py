import numpy as np

def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return (idx, array[idx])

MINSTD = 9.8 * 10**-5
MINDIFF = 10

# This replaces sigToa.m in the matlab
def calcTDOA(sig1, sig2, ch1, ch2, Fs, pf, tit = "none", db=False):
    Ts = 1.0 / Fs
    size = sig1.size
    
    # Generate the fourier transforms. n = size * 8 to add resolution to the plot
    sig1_fourier = np.fft.fft(sig1, n = size * 8)
    sig2_fourier = np.fft.fft(sig2, n = size * 8)
    
    # Get the frequency values associated with each index in the fourier transforms
    freq = np.fft.fftfreq(size * 8, d=Ts)

    # Get a reasonable range around the pinger frequency to plot and use for maximum
    index, value = find_nearest(freq, pf)
    step = int((pf / 2) / (freq[1] - freq[0]))

    # Limit the signals to that range
    freq_range = freq[index - step:index + step]
    sig1_fourier_range = sig1_fourier[index - step:index + step]
    sig2_fourier_range = sig2_fourier[index - step:index + step]
    
    
    mags1 = np.abs(sig1_fourier_range)
    mags2 = np.abs(sig2_fourier_range)
    phases1 = np.angle(sig1_fourier_range)
    phases2 = np.angle(sig2_fourier_range)

    
    
    index_max_1 = np.argmax(mags1)
    index_max_2 = np.argmax(mags2)
    
    std1 = np.std(mags1)
    std2 = np.std(mags2)
    m1 = np.mean(mags1)
    m2 = np.mean(mags2)
    
    print "STD: %10d %10d\nMEAN: %9d %10d\nMAG: %10d %10d\n\n" % (std1 * 10**-5, std2* 10**-5, m1* 10**-5, m2* 10**-5, mags1[index_max_1]* 10**-5, mags2[index_max_2]* 10**-5)
    good = (min(std1, std2) > MINSTD and (min(mags1[index_max_1], mags2[index_max_2]) > (max(std1, std2) * MINDIFF)))
    
    aaa = "IS GOOD " if good else "BAD"
    print aaa
   
    index_max = int((index_max_1 + index_max_2) / 2)
   
    phase_diff = (phases2[index_max_2] - phases1[index_max_1])
    tdoa = phase_diff/(2 * np.pi * pf)
    

    if db and good:
        print(tit + " TDOA: " + str(tdoa * 10 ** 6) + "us")
       
       
        
    return tdoa, good



hydrophones = np.array([[0,       -0.1,   0],
                        [0,       -0.119, 0],
                        [0.0095,   0,     0],
                        [-0.0095,  0,     0]])




def calcOrientation(data, Fs, pf, db=False):


    tdoa1, good1 = calcTDOA(data[:, 1], data[:, 0], "Sig1", "Sig0", Fs, pf, "PIT",  db)
    tdoa2, good2 = calcTDOA(data[:, 2], data[:, 3], "Sig2", "Sig3", Fs, pf, "YAW", db)

    tdoa = (tdoa1, tdoa2)

    SPEED_OF_SOUND = 1484

    sideToSideDistance = np.linalg.norm(hydrophones[3] - hydrophones[2]) / 2
    inlineDistance = np.linalg.norm(hydrophones[1] - hydrophones[0]) / 2 

    sideToSideA = tdoa[1] * SPEED_OF_SOUND / 2
    sideToSideB = np.sqrt(sideToSideDistance ** 2 - sideToSideA ** 2)

    inlineA = tdoa[0] * SPEED_OF_SOUND / 2
    inlineB = np.sqrt(inlineDistance ** 2 - inlineA ** 2)

    front = -1 * np.sign(inlineA)

    yaw = np.arctan2(-sideToSideA, front * sideToSideB)
    pitch = np.arctan2(inlineA, inlineB)

    return (np.rad2deg(yaw), np.rad2deg(pitch), good1 or good2)
    



