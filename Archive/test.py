import os, sys
sys.path.append(os.path.join("/home/pi/.local/lib/python2.7/site-packages"))
from bluedot import*
import datetime
from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_relay import *

from yoctopuce.yocto_tilt import *
from yoctopuce.yocto_compass import *
from yoctopuce.yocto_gyro import *
from yoctopuce.yocto_accelerometer import *
from yoctopuce.yocto_realtimeclock import *

def usage():
    scriptname = os.path.basename(sys.argv[0])
    print("Usage:")
    print(scriptname + ' <serial_number>')
    print(scriptname + ' <logical_name>')
    print(scriptname + ' any  ')
    sys.exit()

def die(msg):
    sys.exit(msg + ' (check USB cable)')
errmsg = YRefParam()

if len(sys.argv) < 2:
    usage()
target = sys.argv[1]

bd = BlueDot()
#bd.when_pressed = execfile("Capture.py")

# Setup the API to use local USB devices
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("init error" + errmsg.value)

if target == 'any':
    # retreive any tilt sensor
    anytilt = YTilt.FirstTilt()

    if anytilt is None:
        die('No module connected (check USB cable)')

    m = anytilt.get_module()
    target = m.get_serialNumber()

else:
    anytilt = YTilt.FindTilt(target + ".tilt1")
    if not (anytilt.isOnline()):
        die('Module not connected (check identification and USB cable)')

serial = anytilt.get_module().get_serialNumber()
tilt1 = YTilt.FindTilt(serial + ".tilt1")
tilt2 = YTilt.FindTilt(serial + ".tilt2")
compass = YCompass.FindCompass(serial + ".compass")
accelerometer = YAccelerometer.FindAccelerometer(serial + ".accelerometer")
gyro = YGyro.FindGyro(serial + ".gyro")
start = datetime.datetime.now()
count = 0
sensors = [tilt1,tilt2,compass, accelerometer, gyro]
names = ['tilt1','tilt2','compass', 'accelerometer', 'gyro']

#Erase data logger contents from previous run
datalogger = YDataLogger.FirstDataLogger()
datalogger.forgetAllDataStreams()

for i in sensors: 
    i.set_logFrequency("5/s")
    i.startDataLogger()
if not (accelerometer.isOnline()):
    die("Module not connected (check identification and USB cable)")

def start(accelerometer):
    count = 0
    while accelerometer.isOnline():
        if count % 5 == 0:
            print("Recording Data....")
        count += 1
        YAPI.Sleep(250, errmsg)

def pause(accelerometer, sensors, names):
    accelerometer.stopDataLogger()
    
    #Extracting using datalogger
    print("Begin Datalogger extraction")
    cnt = 0
    
    #set path
    os.chdir('../Recorded_Data')
            
    for i in sensors:
        name = names[cnt]
        dataset = i.get_recordedData(0,0)
        dataset.loadMore()
        #summary = dataset.get_summary()
        progress = 0
        while progress < 100:
            progress = dataset.loadMore()
        details = dataset.get_measures()
        
        fmt = 'hh:mm:ss,fff'
        lst = []
        for m in details:
            lst.append([str(m.get_startTimeUTC_asDatetime()),
                str(m.get_endTimeUTC_asDatetime()),
                #m.get_minValue(), accelerometer.get_unit(),
                m.get_averageValue(), accelerometer.get_unit()])
                #m.get_maxValue(), accelerometer.get_unit()])
        with open(name+str(start)+'.csv', mode='w') as file:
            writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['start','end','avg'])
            for row in lst:
                writer.writerow(row)  
        cnt += 1
        
bd.wait_for_press()
start(accelerometer)
bd.wait_for_press()
pause(accelerometer, sensors, names)
