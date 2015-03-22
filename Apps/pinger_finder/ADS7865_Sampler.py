import boot
import numpy as np
SAMPLES_PER_CONV = 2


def main(ADC_obj):
	ADC_obj.Ready_PRUSS_For_Burst()
	
	
	print("ADC is armed and ready.")
	raw_input("Press enter when ready...")
	
	# grab data
	(y,temp) = ADC_obj.Burst()
	
	user_input = raw_input("Would you like to plot the data?")
	if "y" == user_input:
		plot_output(ADC_obj, y)
	
	boot.dearm()
	
		
		
def plot_output(ADC_obj, y):
	# Load the library
	plt = load_matplotlib()
	fig,ax = plt.subplots()
	
	# Compute parameters
	n 		= ADC_obj.n_channels
	M 		= y[0].size
	
	frequency_attenuation_factor = n/SAMPLES_PER_CONV
	fs 		= ADC_obj.sampleRate/float(frequency_attenuation_factor) #Hertz
	Ts		= 1/fs
	
	if (M*Ts/Ts <= M):
		t 		= np.arange(0, M*Ts, Ts) 
	elif (M*Ts/Ts > M):
		t 		= np.arange(0, (M-0.1)*Ts, Ts) # Chalk it up to precision error
	else:
		print("Something crazy happened.")
		
	
	# Plot the data
	legend_list = ['']*ADC_obj.n_channels
	for chan in range(ADC_obj.n_channels):
		ax.plot(t,y[chan])
		legend_list[chan] = ADC_obj.ch[chan]
	
	
	ax.axis(xmin=0,
			xmax=None,
			ymin=-2.5,
			ymax=2.5)
	ax.legend(legend_list)
	plt.show()
	
	
		
def load_matplotlib():
	print("Loading Matplotlib library...")
	import matplotlib
	matplotlib.use('GTK')
	import matplotlib.pyplot as plt
	print("...done.")
	
	return plt