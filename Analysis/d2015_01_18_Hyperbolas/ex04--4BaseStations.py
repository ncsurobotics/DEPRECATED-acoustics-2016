import matplotlib.pyplot as plt
import numpy as np
import itertools

def getFocii(spacing_of_elements):
	c = spacing_of_elements/2
	return c
	
def hyperbola(a,b):
	step = .1e-2 
	y = np.arange(-200, 200+step, step)
	x = a*np.sqrt(1+(y/b)**2)
	return (x,y)

def hyperbolaCOE(c,del_t,v_medium):
	# Compute a
	del_d = del_t*v_medium
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

def easyHyperbola(d,del_t,v):
	#Compute first hyperbola
	c = getFocii(d)
	(a,b) = hyperbolaCOE(c,del_t,v)
	(x,y) = hyperbola(a,b)
	hbla = np.vstack((x,y))
	return hbla
	
def xform_rotate(xy,theta):
	a11 = np.cos(theta)
	a12 = -np.sin(theta)
	a21 = np.sin(theta)
	a22 = np.cos(theta)
	A = np.array([[a11,a12],[a21,a22]])
	
	
	# transform
	xy = np.dot(A,xy)
		
	return xy
	
def xform_translate(xy,x_shift,y_shift):
	xy = xy + np.array([[x_shift],[y_shift]])
	return xy
	
def go(src_loc, n, bs):
	#Initialize parameters
	x = 0
	y = 1

	# Initialize plot
	fig1,ax1 = plt.subplots()
	ax1.set_title("Hydrophone Array")
	zoom = 200e-2
	ax1.axis(xmin = -zoom,
				xmax = zoom,
				ymin = -zoom,
				ymax = zoom)

	v = 1473 #Speed of sound in the medium (m/s)
	
	# Plot something we already know
	plt.plot(src_loc[x], src_loc[y], 'x')
	for i in range(n):
		plt.plot(bs[i][x], bs[i][y], 'ro')
		
	for ID in itertools.combinations(range(n), 2):
		# Set parameters and establish system for accessing elements
		print("go: Working on combo %s and %s" % (ID[0], ID[1]))
		el = [0,0]
		el[0] = bs[ID[0]]
		el[1] = bs[ID[1]]
		
		# Determine COMes and Rotations necessary to access individual elements
		COM_i = (el[0] + el[1])/2
		tangent_i = el[1]-el[0]
		rot_i = np.arctan2(tangent_i[y],tangent_i[x])[0]

		print("The rotation of this pair is %.1f radians." % rot_i)
		
		# Calculate del_t
		D1 = np.linalg.norm( el[0]-src_loc )
		D2 = np.linalg.norm( el[1]-src_loc )
		del_t = (D1-D2)/v
		
		# Generate boolean for left or right 
		if del_t > 0:
			r_bit = 1
		elif del_t < 0:
			r_bit = -1
			del_t = del_t*-1
		
		# Calculate the hyperbola
		d = np.linalg.norm( el[1]-el[0] )
		hbla_o = easyHyperbola(d,del_t,v)
		
		# select "side of hyperbola based on sign"
		hbla_o = hbla_o*np.array([[r_bit],[1]])
		
		# rotate hyperbola to the appropriate location
		hbla_o = xform_rotate(hbla_o,rot_i)
		hbla_i = xform_translate(hbla_o,COM_i[x][0],COM_i[y][0])
		
		# PLOT!!!
		plt.plot(hbla_i[x],hbla_i[y])
		
		
		#DEBUG plt.plot(center[x], center[y], 'x')
		print("")
		
	
	# Commit the final plot
	plt.show()
	
	
	

def main():
	rot = np.pi
	Hyd = [np.array([[0],[10e-2]])] #Hydrophone #1 location (meters)
	Hyd.append( xform_rotate(Hyd[0], rot) )
	#Hyd.append( xform_rotate(Hyd[1], rot) )
	#Hyd.append( xform_rotate(Hyd[2], rot) )

	src = np.array([[5e-2],[2e-2]])
	
	n_baseStations = len(Hyd)
	print(n_baseStations)
	go(src, n_baseStations, Hyd)

print("-"*50)
main()
