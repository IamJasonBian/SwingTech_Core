import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation as R
import math
import collections


def double_int_class(vect, delta_t, x0, v0):
    x = []
    v = []

    for i in range(len(vect) - 1):
        if i==0 :
            v.append(delta_t[i] * vect[i] + v0)
        else:
            v.append(delta_t[i] * vect[i] + v[i-1])
    for i in range(len(vect) - 1):
        if i==0:
            x.append(delta_t[i] * v[i] + x0)
        else:
            x.append(delta_t[i] * v[i] + x[i-1])
    
    return np.array(x), np.array(v)

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from procrustes import procrustes

def plot_3d_dist(vect_x, vect_y, vect_z):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(vect_x, vect_y, vect_z, s=1)
    plt.show()
    
def unit_vect_transform(unit_vec, angle_vec):

    x = unit_vec[0]
    y = unit_vec[1]
    z = unit_vec[2]
    
    yaw = angle_vec[0]
    roll = angle_vec[1]
    pitch = angle_vec[2]
    
    #apply yaw (around y)
    x = x * math.cos(yaw) - z * math.sin(yaw)
    z = z * math.cos(yaw) + x * math.sin(yaw)

    #apply pitch (around x)
    y = y * math.cos(roll) - z * math.sin(roll)
    z = z * math.cos(roll) + y * math.sin(roll)

    #apply roll (around z)
    x = x * math.cos(pitch) - y * math.sin(pitch)
    y = y * math.cos(pitch) + x * math.sin(pitch)
    
    trans_vec = np.array([x,y,z])
    return trans_vec

def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return math.sqrt(dotproduct(v, v))

def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))
  
def Calculate(data, GPA=False, delta_t=0.1, plot=False): 
#    data = pd.read_csv(file)
    delta_t = np.repeat(0.1, data.shape[0]) # time interval is 0.1 seconds
    unit_vec = np.array([1,0,0])
    
#    position = []
#    position.extend([0, 0, 0])
#    velocity = []
#    velocity.extend([0, 0, 0])
        
    for i in range(int(len(data)/9)):
        
        df = data.iloc[i:i+9]
        Axc = df['ax'].tolist()
        Ayc = df['ay'].tolist()
        Azc = df['az'].tolist()

        position_x, velocity_x = double_int_class(Axc, delta_t, 0, 0)
        position_y, velocity_y = double_int_class(Ayc, delta_t, 0, 0)
        position_z, velocity_z = double_int_class(Azc, delta_t, 0, 0)
        position = np.array([position_x, position_y, position_z])
        velocity = np.array([velocity_x, velocity_y, velocity_z])

        if GPA == True:
            if i == 0:
                X = np.array([position_x, position_y, position_z])
            else:
                position = procrustes(X, position, scaling=False)
                    
        t1 = df['tilt1'].tolist()
        t2 = df['tilt2'].tolist()
        compass = df['compass'].tolist()
        trans_vec = []
        for j in range(8):
            angle_vec = np.array([t1[j]*math.pi/180, t2[j]*math.pi/180, compass[j]*math.pi/180])
            trans_vec.append(unit_vect_transform(unit_vec, angle_vec))
        max_angle = angle(trans_vec[0], trans_vec[-1])
        trans_vec = np.array(trans_vec)
        
        if plot == True:
            fig = plt.figure(figsize=(20, 10))
            ax = fig.add_subplot(211, projection='3d')
            ax.scatter(position[0, :],  position[1, :], position[2, :])
            ax.plot(position[0, :],  position[1, :], position[2, :], color='blue')
            for j in range(8):
                ax.quiver(position[0, j],  position[1, j], position[2, j], 
                          trans_vec[j, 0], trans_vec[j, 1], trans_vec[j, 2], 
                          length = 20, normalize = True, color='red', linestyle = '--')
            ax.view_init(azim=0, elev=90) #xy plane
            plt.xticks(fontsize=10)
            plt.xticks(fontsize=10)
#            ax.set_axis_off()
            
            ax2 = fig.add_subplot(212, projection='3d')
            ax2.scatter(position[0, :],  position[1, :], position[2, :])
            ax2.plot(position[0, :],  position[1, :], position[2, :], color='blue')
            for j in range(8):
                ax2.quiver(position[0, j],  position[1, j], position[2, j], 
                          trans_vec[j, 0], trans_vec[j, 1], trans_vec[j, 2], 
                          length = 20, normalize = True, color='red', linestyle = '--')
            ax2.view_init(azim=0, elev=45)
            
#            ax3 = fig.add_subplot(223, projection='3d')
#            ax3.scatter(position[0, :],  position[1, :], position[2, :])
#            ax3.plot(position[0, :],  position[1, :], position[2, :])
#            for j in range(8):
#                ax3.quiver(position[0, j],  position[1, j], position[2, j], 
#                          trans_vec[j, 0], trans_vec[j, 1], trans_vec[j, 2], 
#                          length = 20, normalize = True, color='red', linestyle = '--')
#            ax3.set_axis_off()
            
    ReturnType = collections.namedtuple('ReturnType', 'Position_Vector Max_Speed Max_Angle')
    
    return ReturnType(Position_Vector=position, Max_Speed=round(max(np.linalg.norm(velocity,axis=1))/1000, 3),
                      Max_Angle = round(max_angle/math.pi*180, 3))
#    position, max(np.linalg.norm(velocity,axis=1))
