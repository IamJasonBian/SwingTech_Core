import os, sys

sys.path.append(os.path.join("usr/local/lib/python2.7/dist-packages (1.3.2)"))

from bluedot import*
from signal import pause

def start():
    print("Running Capture")
    os.system("Capture.py")
    

def stop():
    print("You stopped the blue dot!")
    
def swiped(swipe):
    if swipe.up:
        start()
    elif swipe.down:
        stop()
     
bd = BlueDot()
bd.when_swiped = swiped

pause()


