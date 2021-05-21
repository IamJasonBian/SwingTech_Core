port = "22"
server = '192.168.7.2'
username = 'pi'
password = 'raspberry'
localpath = 'C:/Users/Jason/Desktop/Test_2'
remoteCalibration = '/home/pi/Processing/Spatial_Clustering/Handoff/Calibration.csv'

#During copy, timestamp gets changed as data is pushed to archive
remoteData = '/home/pi/Processing/Spatial_Clustering/Handoff/Data.csv'

import os
import paramiko
from scp import SCPClient

#SSH Client
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

#Data Transfer, the same path is used for raspberry pi
def transfer(localpath):
    
    print("Creating ssh client")
    
    try:
        ssh = createSSHClient(server, port, username, password)
        print("Ssh Established!")
        scp = SCPClient(ssh.get_transport())
        
    except:
        return("Not Connected")
    
    scp.get(remoteCalibration, localpath)
    scp.get(remoteData, localpath)
    print("Calibration and Data Downloaded!")
    scp.close
    return ("Connected")


if __name__ == "__main__":  
    transfer(localpath)




