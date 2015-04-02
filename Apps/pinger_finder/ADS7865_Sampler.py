import boot
import numpy as np
SAMPLES_PER_CONV = 2


def main(ADC_obj, plt):
	ADC_obj.Ready_PRUSS_For_Burst()
	
	
	print("ADC is armed and ready.")
	raw_input("Press enter when ready...")
	
	# grab data
	(y,temp) = ADC_obj.Burst()
	
	if plt:
		user_input = raw_input("Would you like to plot the data?")
		if "y" == user_input:
			plot_output(ADC_obj, y, plt)
	
	boot.dearm()
	return y
		
		
def plot_output(ADC_obj, y, plt):
	# get plotting objects
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
		plt.xlabel('time (seconds)')
		plt.ylabel('Voltage')
		plt.title('Voltage vs Time, Fs=%dKHz' % (fs/1000))
	
	
	ax.axis(xmin=0,
			xmax=None,
			ymin=-2.5,
			ymax=2.5)
	ax.legend(legend_list)
	plt.show()