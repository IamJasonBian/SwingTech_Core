import os, sys, time

sys.path.append(os.path.join("usr/local/lib/python2.7/dist-packages (1.3.2)"))

from bluedot import*
from signal import pause
from Capture import*

def start():
    print("Running Capture")
    x = Sensor()
    x.erase()
    x.run()
    
def stop():
    print("Extracting Data")
    x = Sensor()
    x.stop()
    x.extract()
    print("Extraction Complete")

def calibrate():
    print("Initial Calibration")
    x = Sensor()
    x.calibrate()
    #light_signal("off")

def senddata():
    print("Sending ")
    #light_signal("on")
          
def swiped(swipe):
    if swipe.up:
        start()
    elif swipe.down:
        stop()
    elif swipe.left:
        calibrate()
    elif swipe.right:
        senddata()

print("Awaiting Bluetooth")
bd = BlueDot()
bd.when_swiped = swiped

pause()


