import numpy as np

class Environment():
    def __init__(self):
        self.c = 1473 # m/s. The speed of sound in water. 

class Phys_Obj(object):
    all_objects = []
    
    def __init__(self):
        self.position = np.array([[0,0,0]])
        self.orientation = None
        Phys_Obj.all_objects.append(self)
        
        self.X = 0
        self.Y = 0
        self.Z = 0
        
        # matplotlib data
        self.pdata = None
        
    def move(self, coordinates):
        if coordinates.size != 3:
            print("acoustics: 3 dimensional coordinates please!")
            return None
          
        # Create necessary vectors  
        new_position = coordinates
        old_position = self.position
        translation_vect = new_position - old_position
        
        # Update position
        self.position = new_position
        #self.position = coordinates

        self.X = self.X + translation_vect[0,0]
        self.Y = self.Y + translation_vect[0,1]
        self.Z = self.Z + translation_vect[0,2]
        
    def set_XYZ(self, X=None, Y=None, Z=None, XYZ=None):
        """defines all X, Y, and Z values. User can pass in single 1xN numpy
        array for X, Y, Z, or user can just pass an Nx3 array for XYZ, where each
        row is an X, Y, Z coordinate.
        """
        if (X != None) and (Y != None) and (Z != None):
            self.X = X
            self.Y = Y
            self.Z = Z
        
        elif (XYZ != None):
            self.X = XYZ[:,0].T
            self.Y = XYZ[:,1].T
            self.Z = XYZ[:,2].T
        
        else:
            raise SyntaxError("XYZ matrix or X, Y, Z values.")
        
    def xform_translate(self, shift_vals):
        if shift_vals.size != 3:
            print("acoustics: 3 dimensional coordinates please!")
            return None
            
        new_position = shift_vals + self.position
        self.move(new_position)

    def rotate(self, new_normal_vector):
        self.orientation = new_normal_vector
        self.position = coordinates
        
    def xform_translate(self, shift_values):
        new_location = self.position + shift_values
        self.move(new_location)
        
    def xform_rotate(self, rot_values):
        rot_x = rot_values[0,0]
        rot_y = rot_values[0,1]
        rot_z = rot_values[0,2]
        
        mat_xrot = np.array([[1,0,0],
            [0,np.cos(rot_x),-np.sin(rot_x)],
            [0,np.sin(rot_x),np.cos(rot_x)]])
            
        mat_yrot = np.array([[np.cos(rot_y),0,np.sin(rot_y)],
            [0,1,0],
            [-np.sin(rot_y),0,np.cos(rot_y)]])
            
        mat_zrot = np.array([[np.cos(rot_z),-np.sin(rot_z),0],
            [np.sin(rot_z),np.cos(rot_z),0],
            [0,0,1]])
            
            
        # Do X axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_xrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
        # Do Y axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_yrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
        # Do Z axis rotation
        old_xyz = np.array([self.X, self.Y, self.Z])
        new_xyz = [0]*3
        for r in range(3):
            for c in range(3):
                new_xyz[r] = new_xyz[r] + mat_zrot[r][c]*old_xyz[c]
        
        self.X = new_xyz[0]
        self.Y = new_xyz[1]
        self.Z = new_xyz[2]
        
def get_xaxis_rotation(vect_a, align_vect):
    """Computes the rotation necessesary to align vect_a with 
    align_vect. vect_a and align_vect must lie in the xz-plane for the function.
    """
    # Use dot products to compute rotation vector
    dot_prod = np.dot(vect_a, align_vect)
    mag_prog = np.linalg.norm(vect_a)*np.linalg.norm(align_vect)
    y_rot = np.arccos(dot_prod/mag_prog)
    
    # Return y_rot
    return y_rot