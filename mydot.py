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

def light_signal(state):
    #!/usr/bin/python

    import RPi.GPIO as GPIO
    from time import sleep

    # Needs to be BCM. GPIO.BOARD lets you address GPIO ports by periperal
    # connector pin number, and the LED GPIO isn't on the connector
    GPIO.setmode(GPIO.BCM)

    # set up GPIO output channel
    GPIO.setup(16, GPIO.OUT)

    if(state == "on"):
        # On
        GPIO.output(16, GPIO.LOW)
    else:
        # Off
        GPIO.output(16, GPIO.HIGH)

print("Awaiting Bluetooth")
bd = BlueDot()
bd.when_swiped = swiped

pause()


