import matplotlib.pyplot as plt
import numpy as np

# Initialize parameters
d = 12.0e-2 #Hydrophone spacing (meters)
del_t = 67.889e-6  #time difference in signal arrival (seconds)
v = 1473 #Speed of sound in the medium (m/s)

def getFocii(spacing_of_elements):
	c = spacing_of_elements/2
	return c
	
def hyperbola(a,b):
	step = .1e-2 
	y = np.arange(-20e-2, 20e-2+step, step)
	x = a*np.sqrt(1+(y/a)**2)
	return (x,y)

def hyperbolaCOE(c,del_t,v_medium):
	# Compute a
	del_d = del_t*v
	a = del_d/2
	
	#check for error
	if a > c:
		print("hyperbolaCOE: ERROR. Your a, --%.1fcm--, is greater than c, --%.1fcm--. Please reduce time delay or increase element spacing."
				% (a*100, c*100))
		exit(1)
	
	# Compute b
	b = np.sqrt(c**2 - a**2)
	
	# Explain and return
	print("""hyperbolaCOE: I see you have a measured time delay of %.1f microseconds and the speed of sound in your medium is %d m/s. Given that your elements are %.1f cm appart, then a = %.1fcm, and b = %.1fcm."""
			% (del_t*1e6, v_medium, 2*c*100, a*100, b*100))
	return (a,b)

def main():
	#Compute first hyperbola
	c = getFocii(d)
	(a,b) = hyperbolaCOE(c,del_t,v)
	(x,y) = hyperbola(a,b)
	
	#Plot yo work!
	fig1,ax1 = plt.subplots()
	ax1.plot(d/2, 0, 'ro') #Plot focii
	ax1.plot(-d/2, 0, 'ro')
	ax1.plot(x,y) #hyperbola
	ax1.plot(-x,y)
	plt.show()

print("-"*50)
main()
